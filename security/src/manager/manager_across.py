from dataclasses import asdict

from sqlmodel import Session

from src.control import ControllerCredentials
from src.control.control_sbi import SBIProtocol, sbi
from src.control.opensto import SSLAApplyRequest
from src.control.tfs import (
    ACLCreateRequest,
    ACLDeleteRequest,
    IETFNetworkGetRequest,
    WIMServiceInfoGetRequest,
)
from src.manager.manager_common import CommonManager
from src.resources.crud.closed_loop import (
    create_closed_loop_request,
    delete_closed_loop_request,
    get_closed_loop_request,
)
from src.resources.crud.controller import get_controller_credentials
from src.resources.crud.ssla import (
    create_capability,
    create_essla_aio,
    get_capabilities,
    get_capability,
    get_essla_aio,
)
from src.resources.crud.vertical_ns import create_mano_service_info
from src.resources.crud.wim import create_wim_service_info
from src.resources.models.closed_loop import (
    ClosedLoopInitializationRequestCreate,
    ClosedLoopType,
)
from src.resources.models.controller import ControllerType
from src.resources.models.service_info import ManoWimServiceInfo
from src.resources.models.ssla.capability import CapabilityCreate, CapabilityGet
from src.resources.models.ssla.ssla import DXSLAAIO, ESSLAAIOCreate, ESSLAAIOGet
from src.resources.models.wim import WIMServiceInfoCreate
from src.ssla_policy.plugins import MapRequest
from src.ssla_policy.plugins.acl.handler import ACLConfig
from src.ssla_policy.ssla_policy import SSLAPolicyProtocol, sslap

from . import logger


class AcrossManager(CommonManager):
    def __init__(self, sbi_instance: SBIProtocol, ssla_policy: SSLAPolicyProtocol) -> None:
        super().__init__(sbi_instance)
        self.sslap = ssla_policy

    def get_wim_topology(self, controller: ControllerCredentials) -> dict:
        return self.sbi.get_tfs_topology(
            IETFNetworkGetRequest(wim_ip=controller.ip, wim_port=controller.port)
        )

    def apply_ssla_to_deployed_service(self, request: SSLAApplyRequest, session: Session) -> str:
        service_id = request.service_id
        ssla = get_essla_aio(request.ssla_id, session)

        controller = get_controller_credentials(ControllerType.TFS, session)
        logger.debug('controller credentials found')
        topology = self.get_wim_topology(controller)
        logger.debug('topology found')
        mapping_request = MapRequest(
            essla_aio=ESSLAAIOGet.model_validate(ssla),
            topology=topology,
            controller_credentials=controller,
            service_id=service_id,
        )
        cfg = self.sslap.map(mapping_request).config
        match cfg:
            case ACLConfig() as acl_cfg:
                for acl in acl_cfg.acls:
                    self.sbi.add_acl(
                        ACLCreateRequest(
                            acl_create=acl,
                            wim_ip=controller.ip,
                            wim_port=controller.port,
                        )
                    )
                    logger.debug('ACL %s created', acl)
                #configurations = asdict(acl_cfg)
                configurations = {"acls": [
                    acl.to_db_record()
                    for acl in acl_cfg.acls
                ]}
            case DXSLAAIO():
                configurations = {}
            case _:
                raise ValueError('Invalid configuration type')

        closed_loop_request = ClosedLoopInitializationRequestCreate(
            id=service_id, configurations=configurations
        )
        create_closed_loop_request(closed_loop_request, session)
        return request.service_id

    def remove_ssla_from_deployed_service(self, service_id: str, session: Session) -> None:
        controller = get_controller_credentials(ControllerType.TFS, session)
        logger.debug('controller credentials found')
        closed_loop = get_closed_loop_request(service_id, session, as_table=False)
        config = closed_loop.configurations
        delete_requests = {(acl['device_id'], acl['name']) for acl in config['acls']}
        for dr in delete_requests:
            device_id = dr[0]
            acl_name = dr[1]
            self.sbi.delete_acl(
                ACLDeleteRequest(
                    device_id=device_id,
                    acl_name=acl_name,
                    wim_ip=controller.ip,
                    wim_port=controller.port,
                )
            )
            logger.debug('ACL %s deleted on device %s', acl_name, device_id)
        delete_closed_loop_request(service_id, ClosedLoopType.DOMAIN, session)

    def upload_capability(self, capability: CapabilityCreate, session: Session) -> str:
        created_capability = create_capability(capability, session)
        logger.info('capability stored in db')
        return created_capability.id

    def retrieve_capability(self, nsfr_id: str, session: Session) -> CapabilityGet:
        capability_get = get_capability(nsfr_id, session)
        logger.info('capability found in db')
        return capability_get

    def create_essla_aio(self, essla_create: ESSLAAIOCreate, session: Session) -> str:
        essla_aio = create_essla_aio(essla_create, session)
        logger.info('essla stored in db')
        return essla_aio.id

    def get_essla_aio(self, id: str, session: Session) -> ESSLAAIOGet:
        logger.info('querying db for the essla')
        return get_essla_aio(id, session)


across_manager = AcrossManager(sbi_instance=sbi, ssla_policy=sslap)
