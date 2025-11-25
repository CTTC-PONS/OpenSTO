import queue
from .AttackStore import AttackSpecs, AttackStore
from .Consumer import Consumer
from .GrpcService import GrpcService
from .Processor import Processor

class Manager:
    def __init__(self):
        self.grpc_service  = GrpcService(self)
        self.attack_store  = AttackStore()
        self.message_queue = queue.Queue()
        self.consumer      = Consumer(self.message_queue)
        self.processor     = Processor(self.message_queue, self.attack_store)

        # Manual settings for debugging
        self.attack_store.set(AttackSpecs('normal_traffic',      0.8, 0.3).to_proto())
        self.attack_store.set(AttackSpecs('benign_heavy_hitter', 0.8, 0.3).to_proto())
        self.attack_store.set(AttackSpecs('malign_heavy_hitter', 0.8, 0.3).to_proto())

    def start(self) -> None:
        self.grpc_service.start()
        self.consumer.start()
        self.processor.start()

    def stop(self) -> None:
        self.grpc_service.stop()
        self.consumer.stop()
        self.processor.stop()
