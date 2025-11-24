import json, logging, os, queue, threading, time
from datetime import datetime
from kafka import KafkaProducer
from nfstream.flow import NFlow
from typing import Tuple
from .FlowToJson import serialize_flow

LOGGER = logging.getLogger(__name__)

KAFKA_SERVER   = os.getenv('KAFKA_SERVER',   'localhost:9092')
PUBISHER_TOPIC = os.getenv('PUBISHER_TOPIC', 'traffic_flows' )

def init_kafka_producer(retries: int = 30, delay: float = 3) -> KafkaProducer:
    for attempt in range(1, retries + 1):
        MSG = '[init_kafka_producer] Try #{:d}/{:d}: Connecting to Kafka...'
        print(MSG.format(attempt, retries), flush=True)
        try:
            return KafkaProducer(
                bootstrap_servers = KAFKA_SERVER, 
                value_serializer = lambda o: json.dumps(o).encode('utf-8'),
            )
        except Exception as exc:
            MSG = '[init_kafka_producer] Failed to connect to Kafka: {:s}'
            print(MSG.format(str(exc)), flush=True)
            time.sleep(delay)
    raise Exception('[init_kafka_producer] Could not connect to Kafka. Exiting.')

class Processor(threading.Thread):
    def __init__(self, message_queue : queue.Queue) -> None:
        super().__init__(daemon=True)
        self.message_queue = message_queue
        self.terminate = threading.Event()

    def stop(self) -> None:
        self.terminate.set()

    def run(self) -> None:
        try:
            producer = init_kafka_producer()

            while not self.terminate.is_set():
                try:
                    flow_timestamp : Tuple[NFlow, datetime] = \
                        self.message_queue.get(block=True, timeout=1.0)
                except queue.Empty:
                    continue

                LOGGER.info('Processing: {:s}'.format(str(flow_timestamp)))
                flow, timestamp = flow_timestamp
                json_flow = serialize_flow(flow, timestamp)
                LOGGER.info('  json_flow={:s}'.format(str(json_flow)))
                producer.send(PUBISHER_TOPIC, value=json_flow)
                producer.flush()
        except Exception:
            LOGGER.exception('Unhandled Exception')
