import logging, os, time, uuid
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(name)s:%(message)s')
LOGGER = logging.getLogger(__name__)

KAFKA_SERVER      = os.getenv('KAFKA_SERVER',   'localhost:9092' )
CONSUMER_TOPICS   = str(os.getenv('CONSUMER_TOPICS', 'demo-topic')).split(',')
CONSUMER_GROUP_ID = os.getenv('KAFKA_GROUP_ID', str(uuid.uuid4()))

def init_kafka_consumer(retries: int = 30, delay: float = 3) -> KafkaConsumer:
    for attempt in range(1, retries + 1):
        MSG = '[init_kafka_consumer] Try #{:d}/{:d}: Connecting to Kafka...'
        LOGGER.info(MSG.format(attempt, retries))
        try:
            return KafkaConsumer(
                *CONSUMER_TOPICS, bootstrap_servers=KAFKA_SERVER, group_id=CONSUMER_GROUP_ID,
                value_deserializer = lambda x: x.decode('utf-8'),
                auto_offset_reset='earliest', enable_auto_commit=True,
            )
        except Exception:
            LOGGER.info('[init_kafka_consumer] Failed to connect to Kafka')
            time.sleep(delay)
    raise Exception('[init_kafka_consumer] Could not connect to Kafka. Exiting.')

def main() -> None:
    consumer = init_kafka_consumer()
    
    MSG = 'Listening to topics "{:s}" on "{:s}"...'
    LOGGER.info(MSG.format(str(CONSUMER_TOPICS), str(KAFKA_SERVER)))
    for message in consumer:
        MSG = 'Received: topic={:s} message={:s}'
        LOGGER.info(MSG.format(str(message.topic), str(message.value)))

if __name__ == '__main__':
    main()
