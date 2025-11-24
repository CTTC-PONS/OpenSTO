import queue
from .AttackModels import AttackModels
from .Consumer import Consumer
from .GrpcService import GrpcService
from .Processor import Processor
from .TfsApiClient import TfsApiClient
from .Topology import Topology

class Manager:
    def __init__(self):
        self.grpc_service   = GrpcService(self)
        self.attack_models  = AttackModels()
        self.tfs_api_client = TfsApiClient()
        self.topology       = Topology(self.tfs_api_client)
        self.message_queue  = queue.Queue()
        self.consumer       = Consumer(self.message_queue)
        self.processor      = Processor(
            self.message_queue, self.attack_models, self.topology,
            self.tfs_api_client
        )

    def start(self) -> None:
        self.grpc_service.start()
        self.consumer.start()
        self.processor.start()

    def stop(self) -> None:
        self.grpc_service.stop()
        self.consumer.stop()
        self.processor.stop()
