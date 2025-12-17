import logging, numpy, os, pickle, time, uuid
from typing import Any, Dict
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(name)s:%(message)s')
LOGGER = logging.getLogger(__name__)

KAFKA_SERVER      = os.getenv('KAFKA_SERVER',   'localhost:9092' )
CONSUMER_TOPICS   = str(os.getenv('CONSUMER_TOPICS', 'demo-topic')).split(',')
CONSUMER_GROUP_ID = os.getenv('KAFKA_GROUP_ID', str(uuid.uuid4()))

#KAFKA_SERVER      = '192.168.159.157:30995'
#CONSUMER_TOPICS   = ['inference_probs', 'attacks_detected']
#CONSUMER_GROUP_ID = str(uuid.uuid4())

ADDRESSES_OF_INTEREST = {
    #'13.0.1.1', '13.0.2.1', 
}

def init_kafka_consumer(retries: int = 30, delay: float = 3) -> KafkaConsumer:
    for attempt in range(1, retries + 1):
        MSG = '[init_kafka_consumer] Try #{:d}/{:d}: Connecting to Kafka...'
        LOGGER.info(MSG.format(attempt, retries))
        try:
            return KafkaConsumer(
                *CONSUMER_TOPICS, bootstrap_servers=KAFKA_SERVER, group_id=CONSUMER_GROUP_ID,
                value_deserializer = pickle.loads,
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
        if message.topic != 'inference_probs': continue

        candidate_data : numpy.array    = message.value['data']
        candidate_meta : Dict[str, Any] = message.value['metadata']

        for i,data in enumerate(candidate_data):
            metadata = candidate_meta[i]
            if (
                len(ADDRESSES_OF_INTEREST) > 0 and
                metadata['src_ip'] not in ADDRESSES_OF_INTEREST
            ): continue

            MSG = 'Inference Probs: data={:s} metadata={:s}'
            LOGGER.info(MSG.format(str(data), str(metadata)))

if __name__ == '__main__':
    main()
