import json, logging, os, queue, threading, time, uuid
from kafka import KafkaConsumer

LOGGER = logging.getLogger(__name__)

KAFKA_SERVER      = os.getenv('KAFKA_SERVER',   'localhost:9092' )
CONSUMER_TOPIC    = os.getenv('CONSUMER_TOPIC', 'traffic_flows')
CONSUMER_GROUP_ID = os.getenv('KAFKA_GROUP_ID', str(uuid.uuid4()))

def init_kafka_consumer(retries: int = 30, delay: float = 3) -> KafkaConsumer:
    for attempt in range(1, retries + 1):
        MSG = '[init_kafka_consumer] Try #{:d}/{:d}: Connecting to Kafka...'
        LOGGER.info(MSG.format(attempt, retries))
        try:
            return KafkaConsumer(
                CONSUMER_TOPIC, bootstrap_servers=KAFKA_SERVER, group_id=CONSUMER_GROUP_ID,
                value_deserializer = lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='earliest', enable_auto_commit=True,
            )
        except Exception:
            LOGGER.info('[init_kafka_consumer] Failed to connect to Kafka')
            time.sleep(delay)
    raise Exception('[init_kafka_consumer] Could not connect to Kafka. Exiting.')

class Consumer(threading.Thread):
    def __init__(self, message_queue : queue.Queue) -> None:
        super().__init__(daemon=True)
        self.message_queue = message_queue
        self.terminate = threading.Event()

    def stop(self) -> None:
        self.terminate.set()

    def run(self) -> None:
        try:
            consumer = init_kafka_consumer()
            for msg in consumer:
                #LOGGER.debug('Received: {:s}'.format(str(msg.value)))
                self.message_queue.put(msg.value)
        except Exception:
            LOGGER.exception('Unhandled Exception')
