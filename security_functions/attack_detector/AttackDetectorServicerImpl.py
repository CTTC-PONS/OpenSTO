import grpc, logging
from typing import TYPE_CHECKING, Iterator
from _common.proto import attack_detector_pb2 as pb2
from _common.proto import attack_detector_pb2_grpc as pb2_grpc

if TYPE_CHECKING:
    from .Manager import Manager

LOGGER = logging.getLogger(__name__)


class AttackDetectorServicerImpl(pb2_grpc.AttackDetectorServicer):
    def __init__(self, manager : 'Manager') -> None:
        self._manager = manager

    def ConfigureAttack(
        self, request : pb2.AttackSpecs, context : grpc.ServicerContext
    ) -> pb2.Empty:
        self._manager.attack_store.set(request)

    def ListConfiguredAttacks(
        self, request : pb2.Empty, context : grpc.ServicerContext
    ) -> Iterator[pb2.AttackSpecs]:
        for attack in self._manager.attack_store.list():
            yield attack.to_proto()

    def GetConfiguredAttack(
        self, request : pb2.AttackId, context : grpc.ServicerContext
    ) -> pb2.AttackSpecs:
        attack_uuid = request.attack_uuid
        attack_specs = self._manager.attack_store.get(attack_uuid)
        if attack_specs is None: return pb2.AttackSpecs()
        return attack_specs.to_proto()

    def DeconfigureAttack(
        self, request : pb2.AttackId, context : grpc.ServicerContext
    ) -> pb2.Empty:
        attack_uuid = request.attack_uuid
        self._manager.attack_store.delete(attack_uuid)
