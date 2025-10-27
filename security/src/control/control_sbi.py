from dataclasses import dataclass
from typing import Callable, Protocol
from osmclient import client
from src.config import settings
from src.exceptions import InvalidRunningModeError
from src.resources.models.ssla.ssla import ESSLAAIOGet
from src.resources.models.vertical_ns import NSInfo
from src.resources.models.wim import IETFNetworkGet, WIMServiceInfoGet

from . import ControllerCredentials, controller, logger
from . import tfs as TFS
from .osm import OSM


@dataclass
class MirrorInvokeSignalRequest(controller.MirroringRequest, controller.InvokeSignalingRequest): ...


@dataclass
class SBIRequest:
    request: MirrorInvokeSignalRequest


class SBIProtocol(Protocol):
    @classmethod
    def get_mano_service_info(cls, ns_id, ctrl_creds: ControllerCredentials) -> NSInfo: ...

    @classmethod
    def create_mano_service(
        cls, nsd_name: str, vim_account: str, nsr_name: str, ctrl_creds: ControllerCredentials
    ) -> NSInfo: ...

    @classmethod
    def get_tfs_topology(cls, request: TFS.IETFNetworkGetRequest) -> dict: ...

    @classmethod
    def get_wim_service_info(cls, request: TFS.WIMServiceInfoGetRequest) -> WIMServiceInfoGet: ...

    @classmethod
    def create_wim_service(
        cls,
        source_gateway_port: str,
        destination_gateway_port: str,
        source_ip: str,
        destination_ip: str,
        ctrl_creds: ControllerCredentials,
    ) -> WIMServiceInfoGet: ...

    @classmethod
    def delete_wim_service(
        cls,
        service_id: str,
        ctrl_creds: ControllerCredentials,
    ) -> None: ...

    @classmethod
    def get_essla_aio(cls, request: str) -> ESSLAAIOGet: ...

    @classmethod
    def add_acl(cls, request: TFS.ACLCreateRequest) -> dict:  # Returns device uuid value
        ...

    @classmethod
    def get_acl(cls, request: TFS.ACLGetRequest) -> dict:  # Returns in IETF_ACL format
        ...

    @classmethod
    def delete_acl(cls, request: TFS.ACLDeleteRequest) -> str:  # Returns device uuid value
        ...

    @classmethod
    def delete_mano_service(cls, ns_id: str, ctrl_creds: ControllerCredentials) -> None: ...


class SBIModule:
    def __init__(
        self,
        mano_client: controller.MANO,
        wim_client: controller.WIM,
    ) -> None:
        self.mano = mano_client
        self.wim = wim_client

    def get_mano_service_info(self, ns_id: str, ctrl_creds: ControllerCredentials) -> NSInfo:
        ns_info = self.mano.get_service_info(ns_id, ctrl_creds)
        logger.debug('mano network service information retrieved')
        return ns_info

    def create_mano_service(
        self, nsd_name: str, vim_account: str, nsr_name: str, ctrl_creds: ControllerCredentials
    ) -> NSInfo:
        ns_id = self.mano.create_network_service(nsd_name, vim_account, nsr_name, ctrl_creds)
        logger.debug('mano network service created')
        ns_info = self.get_mano_service_info(ns_id, ctrl_creds)
        logger.debug('mano network service information retrieved')
        return ns_info

    def get_wim_service_info(self, request: TFS.WIMServiceInfoGetRequest) -> WIMServiceInfoGet:
        wim_service_info = self.wim.get_service_info(request)
        logger.debug('wim service information retrieved')
        return wim_service_info

    def create_wim_service(
        self,
        source_gateway_port: str,
        destination_gateway_port: str,
        source_ip: str,
        destination_ip: str,
        ctrl_creds: ControllerCredentials,
    ) -> WIMServiceInfoGet:
        cs_id = self.wim.create_network_service(
            TFS.ConnectivityServiceCreateRequest(
                wim_ip=ctrl_creds.ip,
                wim_port=ctrl_creds.port,
                source_ip=source_ip,
                source_port=source_gateway_port,
                destination_ip=destination_ip,
                destination_port=destination_gateway_port,
            )
        )
        logger.debug('connectivity service %s created', cs_id)
        cs_info = self.get_wim_service_info(
            TFS.WIMServiceInfoGetRequest(
                wim_ip=ctrl_creds.ip, wim_port=ctrl_creds.port, service_id=cs_id
            )
        )
        logger.debug('connectivity service information retrieved')
        return cs_info

    def delete_wim_service(
        self,
        service_id: str,
        ctrl_creds: ControllerCredentials,
    ) -> None:
        self.wim.delete_network_service(
            TFS.ConnectivityServiceDeleteRequest(
                wim_ip=ctrl_creds.ip, wim_port=ctrl_creds.port, connectivity_service_id=service_id
            )
        )
        logger.debug('connectivity service %s deleted', service_id)

    def add_acl(self, request: TFS.ACLCreateRequest) -> dict:
        return self.wim.add_acl(request)

    def get_acl(self, request: TFS.ACLGetRequest) -> dict:
        return self.wim.get_acl(request)

    def delete_acl(self, request: TFS.ACLDeleteRequest) -> str:
        return self.wim.delete_acl(request)

    def delete_mano_service(self, ns_id: str, ctrl_creds: ControllerCredentials) -> None:
        return self.mano.delete_network_service(ns_id, ctrl_creds)

    def get_ietf_topology(self, request: TFS.IETFNetworkGetRequest) -> IETFNetworkGet:
        return self.wim.get_ietf_topology(request)

    def get_tfs_topology(self, request: TFS.IETFNetworkGetRequest) -> dict:
        return self.wim.get_tfs_topology(request)


class SBI:
    @classmethod
    def create_sbi_module(
        cls,
        mano_client_class: Callable,
        wim_client: controller.WIM,
    ) -> type['SBI']:
        cls.sbi_module = SBIModule(
            mano_client=OSM(client_class=mano_client_class),
            wim_client=wim_client,
        )
        return cls

    @classmethod
    def get_mano_service_info(cls, ns_id, ctrl_creds: ControllerCredentials) -> NSInfo:
        return cls.sbi_module.get_mano_service_info(ns_id, ctrl_creds)

    @classmethod
    def create_mano_service(
        cls, nsd_name: str, vim_account: str, nsr_name: str, ctrl_creds: ControllerCredentials
    ) -> NSInfo:
        return cls.sbi_module.create_mano_service(nsd_name, vim_account, nsr_name, ctrl_creds)

    @classmethod
    def get_wim_service_info(cls, request: TFS.WIMServiceInfoGetRequest) -> WIMServiceInfoGet:
        return cls.sbi_module.get_wim_service_info(request)

    @classmethod
    def get_tfs_topology(cls, request: TFS.IETFNetworkGetRequest) -> dict:
        return cls.sbi_module.wim.get_tfs_topology(request)

    @classmethod
    def create_wim_service(
        cls,
        source_gateway_port: str,
        destination_gateway_port: str,
        source_ip: str,
        destination_ip: str,
        ctrl_creds: ControllerCredentials,
    ) -> WIMServiceInfoGet:
        return cls.sbi_module.create_wim_service(
            source_gateway_port=source_gateway_port,
            destination_gateway_port=destination_gateway_port,
            source_ip=source_ip,
            destination_ip=destination_ip,
            ctrl_creds=ctrl_creds,
        )

    @classmethod
    def delete_wim_service(
        cls,
        service_id: str,
        ctrl_creds: ControllerCredentials,
    ) -> None:
        return cls.sbi_module.delete_wim_service(service_id=service_id, ctrl_creds=ctrl_creds)

    @classmethod
    def add_acl(cls, request: TFS.ACLCreateRequest) -> dict:
        return cls.sbi_module.wim.add_acl(request)

    @classmethod
    def get_acl(cls, request: TFS.ACLGetRequest) -> dict:
        return cls.sbi_module.wim.get_acl(request)

    @classmethod
    def delete_acl(cls, request: TFS.ACLDeleteRequest) -> str:
        return cls.sbi_module.wim.delete_acl(request)

    @classmethod
    def delete_mano_service(cls, ns_id: str, ctrl_creds: ControllerCredentials) -> None:
        return cls.sbi_module.mano.delete_network_service(ns_id, ctrl_creds)


mano_client = client.Client
wim_client = TFS.TFS()

sbi = SBI.create_sbi_module(
    mano_client_class=mano_client,
    wim_client=wim_client,
)
