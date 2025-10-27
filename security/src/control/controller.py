from dataclasses import dataclass
from typing import Protocol, Type

from src.control import ControllerCredentials, tfs
from src.resources.models.vertical_ns import NSInfo
from src.resources.models.wim import IETFNetworkGet, WIMServiceInfoGet


@dataclass
class MirroringRequest:
    mirroring_device_id: str
    mirroring_source_port: str
    mirroring_destination_port: str


@dataclass
class InvokeSignalingRequest:
    signaling_destination: str
    monitoring_management_address: str


class MANO(Protocol):
    def __init__(self, client_class: Type) -> None: ...
    def get_service_info(self, ns_id: str, ctrl_creds: ControllerCredentials) -> NSInfo: ...
    def monitor_invoke_signaling(self, request: InvokeSignalingRequest) -> None: ...
    def create_network_service(
        self, nsd_name: str, vim_account: str, nsr_name: str, ctrl_creds: ControllerCredentials
    ) -> str: ...
    def delete_network_service(self, nsr_id: str, ctrl_creds: ControllerCredentials) -> None: ...


class WIM(Protocol):
    def add_acl(self, request: tfs.ACLCreateRequest) -> dict:  # Returns device uuid value
        ...

    def delete_acl(self, request: tfs.ACLDeleteRequest) -> str:  # Returns device uuid value
        ...

    def get_acl(self, request: tfs.ACLGetRequest) -> dict:  # Returns in IETF_ACL format
        ...

    def get_ietf_topology(self, request: tfs.IETFNetworkGetRequest) -> IETFNetworkGet: ...
    def get_tfs_topology(self, request: tfs.IETFNetworkGetRequest) -> dict: ...

    def get_service_info(self, request: tfs.WIMServiceInfoGetRequest) -> WIMServiceInfoGet: ...
    def create_network_service(self, request: tfs.ConnectivityServiceCreateRequest) -> str: ...
    def delete_network_service(self, request: tfs.ConnectivityServiceDeleteRequest) -> None: ...

