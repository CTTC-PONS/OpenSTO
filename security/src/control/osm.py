from typing import Callable

from src.control import ControllerCredentials
from src.resources.models.vertical_ns import NFInterface, NSInfo, VNFInfo

from .controller import InvokeSignalingRequest


class OSM:
    def __init__(self, client_class: Callable) -> None:
        self.client_class = client_class

    def monitor_invoke_signaling(self, request: InvokeSignalingRequest) -> None: ...

    def get_service_info(self, ns_id: str, ctrl_creds: ControllerCredentials) -> NSInfo:
        my_client = self.client_class(host=ctrl_creds.ip, sol005=True)
        ns = my_client.ns.get(ns_id)
        nsd_id = ns['nsd-name-ref']
        vnf_ids = ns['constituent-vnfr-ref']
        ns_info = NSInfo(id=ns['id'], type=nsd_id, status=ns['operational-status'])

        vnfs = []
        for v_id in vnf_ids:
            vnfr = my_client.vnf.get(v_id)
            vnf = VNFInfo(
                id=vnfr['id'],
                type=vnfr['vnfd-ref'],
                floating_ip=vnfr['ip-address'],
                ns_info_id=ns_id,
            )
            vnf.interfaces = [
                NFInterface(
                    name=i['external-connection-point-ref'],
                    ip=i['ip-address'],
                    mac=i['mac-address'],
                    vnf_info_id=vnfr['id'],
                )
                for c in vnfr['vdur']
                for i in c['interfaces']
            ]
            vnfs.append(vnf)
        ns_info.vnfs = vnfs
        return ns_info

    def create_network_service(
        self, nsd_name: str, vim_account: str, nsr_name: str, ctrl_creds: ControllerCredentials
    ) -> str:
        my_client = self.client_class(host=ctrl_creds.ip, sol005=True)
        return my_client.ns.create(nsd_name=nsd_name, nsr_name=nsr_name, account=vim_account)

    def delete_network_service(self, nsr_id: str, ctrl_creds: ControllerCredentials) -> None:
        my_client = self.client_class(host=ctrl_creds.ip, sol005=True)
        return my_client.ns.delete(nsr_name=nsr_id)
