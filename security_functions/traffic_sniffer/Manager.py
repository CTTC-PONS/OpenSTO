import queue
from .Sniffer import Sniffer
from .GrpcService import GrpcService
from .Processor import Processor

class Manager:
    def __init__(self):
        self.grpc_service  = GrpcService(self)
        self.message_queue = queue.Queue()
        self.sniffer       = Sniffer(self.message_queue)
        self.processor     = Processor(self.message_queue)

    def start(self) -> None:
        self.grpc_service.start()
        self.sniffer.start()
        self.processor.start()

    def stop(self) -> None:
        self.grpc_service.stop()
        self.sniffer.stop()
        self.processor.stop()
