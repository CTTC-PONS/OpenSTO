import grpc, logging
from typing import TYPE_CHECKING
from _common.proto import traffic_sniffer_pb2 as pb2
from _common.proto import traffic_sniffer_pb2_grpc as pb2_grpc

if TYPE_CHECKING:
    from .Manager import Manager


LOGGER = logging.getLogger(__name__)


class TrafficSnifferServicerImpl(pb2_grpc.TrafficSnifferServicer):
    def __init__(self, manager : 'Manager') -> None:
        self._manager = manager

    def Configure(self, request, context : grpc.ServicerContext):
        overrides = {
            'source_interface'   : request.source_interface,
            'capture_filter'     : request.capture_filter,
            'kafka_server'       : request.kafka_bootstrap_servers,
            'kafka_export_topic' : request.kafka_topic,
            'elasticsearch_url'  : request.elasticsearch_url,
            'elasticsearch_index': request.elasticsearch_index,
        }
        new_config = self._manager.config.update(**overrides)
        LOGGER.info('Received configuration via gRPC: %s', new_config)
        return self._manager.update_config(new_config)

    def GetConfig(self, request, context : grpc.ServicerContext):
        return self._manager.get_config()

    def Start(self, request, context : grpc.ServicerContext):
        LOGGER.info('Starting collector via NBI request.')
        return self._manager.start_sniffer()

    def Stop(self, request, context : grpc.ServicerContext):
        LOGGER.info('Stopping collector via NBI request.')
        return self._manager.stop_sniffer()

    def GetStatus(self, request, context : grpc.ServicerContext):
        return self._manager.get_status()
