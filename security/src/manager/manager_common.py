from sqlmodel import Session

from src.control.control_sbi import SBIProtocol, sbi
from src.resources.crud.closed_loop import (
    delete_closed_loop_request,
    get_closed_loop_request,
)
from src.resources.crud.controller import (
    create_controller,
    delete_controller,
    get_controller,
    get_controller_credentials,
)
from src.resources.crud.firewall import (
    create_firewall,
    delete_firewall,
    get_firewall_by_id,
)
from src.resources.crud.nsf_instance import (
    create_nsf_instance,
    delete_nsf_instance,
    get_nsf_instance,
)
from src.resources.crud.probe import create_probe, delete_probe, get_probe
from src.resources.crud.provider import (
    create_provider,
    delete_provider,
    get_provider_by_id,
)
from src.resources.crud.topology import create_topology, get_topology_api
from src.resources.crud.vertical_ns import create_mano_service_info
from src.resources.models.closed_loop import (
    ClosedLoopInitializationRequestBase,
    ClosedLoopType,
)
from src.resources.models.controller import (
    ControllerCreate,
    ControllerGet,
    ControllerType,
)
from src.resources.models.firewall import FirewallCreate, FirewallGet
from src.resources.models.nsf_instance import NSFInstanceCreate, NSFInstanceGet
from src.resources.models.probe import ProbeCreate, ProbeGet
from src.resources.models.provider import ProviderCreate, ProviderGet
from src.resources.models.topology import TopologyCreate, TopologyGet
from src.resources.models.vertical_ns import NSInfoGet

from . import logger


class CommonManager:
    def __init__(self, sbi_instance: SBIProtocol) -> None:
        self.sbi = sbi_instance

    def create_provider(self, provider_create: ProviderCreate, session: Session) -> str:
        provider_get = create_provider(provider_create, session)
        logger.info('provider stored in db')
        return provider_get.id

    def delete_provider(self, provider_name: str, session: Session) -> None:
        provider_get = delete_provider(provider_name, session)
        logger.info('provider removed from db')

    def get_provider(self, provider_id: str, session: Session) -> ProviderGet:
        provider_get = get_provider_by_id(provider_id, session)
        logger.info('provider found in db')
        return provider_get

    def collect_wim_service_info(self, mano_service_id: str, session: Session) -> NSInfoGet:
        ctrl_creds = get_controller_credentials(ControllerType.OSM, session)
        mano_service_info = self.sbi.get_mano_service_info(mano_service_id, ctrl_creds)
        return create_mano_service_info(mano_service_info, session)

    def upload_topology(self, topology: TopologyCreate, session: Session) -> str:
        topology_get = create_topology(topology, session)
        logger.info('topology stored in db')
        return topology_get.id

    def retrieve_topology(self, session: Session) -> TopologyGet:
        return get_topology_api(session=session)

    def create_controller(self, controller_create: ControllerCreate, session: Session) -> str:
        controller_get = create_controller(controller_create, session)
        logger.info('controller stored in db')
        return controller_get.id

    def delete_controller(self, ctrl_id: str, session: Session) -> None:
        controller_get = delete_controller(ctrl_id, session)
        logger.info('controller removed from db')

    def get_controller(self, ctrl_id: str, session) -> ControllerGet:
        controller_get = get_controller(ctrl_id, session)
        logger.info('controller found in db')
        return controller_get

    def create_probe(self, probe_create: ProbeCreate, session: Session) -> str:
        probe_get = create_probe(probe_create, session)
        logger.info('probe stored in db')
        return probe_get.id

    def get_probe(self, session: Session) -> ProbeGet:
        probe_get = get_probe(session)
        logger.info('probe found')
        return probe_get

    def delete_probe(self, probe_id: str, session: Session) -> None:
        probe_get = delete_probe(probe_id, session)
        logger.info('probe removed from db')

    def create_firewall(self, firewall_create: FirewallCreate, session: Session) -> str:
        firewall_get = create_firewall(firewall_create, session)
        logger.info('firewall stored in db')
        return firewall_get.id

    def get_firewall(self, firewall_id: str, session: Session) -> FirewallGet:
        firewall_get = get_firewall_by_id(firewall_id, session)
        logger.info('firewall found')
        return firewall_get

    def delete_firewall(self, firewall_id: str, session: Session) -> None:
        firewall_get = delete_firewall(firewall_id, session)
        logger.info('firewall removed from db')

    def create_nsf_instance(self, nsf_instance_create: NSFInstanceCreate, session: Session) -> str:
        nsf_instance_get = create_nsf_instance(nsf_instance_create, session)
        logger.info('network security function instance stored in db')
        return nsf_instance_get.id

    def get_nsf_instance(self, nsf_instance_id: str, session: Session) -> NSFInstanceGet:
        nsf_instance_get = get_nsf_instance(session, nsf_instance_id)
        logger.info('network security function found')
        return nsf_instance_get

    def delete_nsf_instance(self, nsf_instance_id: str, session: Session) -> None:
        _ = delete_nsf_instance(nsf_instance_id, session)
        logger.info('firewall removed from db')

    def remove_closed_loop(
        self, closed_loop_id: str, closed_loop_type: ClosedLoopType, session: Session
    ) -> ClosedLoopInitializationRequestBase:
        closed_loop_request = ClosedLoopInitializationRequestBase.model_validate(
            get_closed_loop_request(closed_loop_id, session, False)
        )
        self.sbi.delete_domain_closed_loop(closed_loop_id)
        delete_closed_loop_request(closed_loop_id, closed_loop_type, session)
        return closed_loop_request


common_manager = CommonManager(sbi)
