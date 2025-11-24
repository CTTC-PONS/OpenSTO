from typing import TYPE_CHECKING
from _common.GenericGrpcService import GenericGrpcService
from _common.proto import traffic_sniffer_pb2 as pb2
from _common.proto import traffic_sniffer_pb2_grpc as pb2_grpc
from .TrafficSnifferServicerImpl import TrafficSnifferServicerImpl

if TYPE_CHECKING:
    from .Manager import Manager

class GrpcService(GenericGrpcService):
    def __init__(self, manager : 'Manager', cls_name : str = __name__) -> None:
        super().__init__(cls_name=cls_name)
        self.servicer = TrafficSnifferServicerImpl(manager)

    def install_servicers(self):
        pb2_grpc.add_TrafficSnifferServicer_to_server(self.servicer, self.server)
        self.add_reflection_service_name(pb2.DESCRIPTOR, 'TrafficSniffer')
