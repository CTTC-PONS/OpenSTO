import logging, numpy, os, pickle, queue, threading, time
from kafka import KafkaProducer
from typing import Any, Dict, List
from .AttackStore import AttackStore

LOGGER = logging.getLogger(__name__)

KAFKA_SERVER   = os.getenv('KAFKA_SERVER',   'localhost:9092'  )
PUBISHER_TOPIC = os.getenv('PUBISHER_TOPIC', 'attacks_detected')

ADDRESSES_OF_INTEREST = {
    '13.0.1.1', '13.0.2.1', 
}

META_FIELD_NAMES = {
    'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol', 'monitored_device', 'interface'
}

def init_kafka_producer(retries: int = 30, delay: float = 3) -> KafkaProducer:
    for attempt in range(1, retries + 1):
        MSG = '[init_kafka_producer] Try #{:d}/{:d}: Connecting to Kafka...'
        print(MSG.format(attempt, retries), flush=True)
        try:
            return KafkaProducer(
                bootstrap_servers=KAFKA_SERVER, 
                value_serializer=pickle.dumps,
            )
        except Exception as exc:
            MSG = '[init_kafka_producer] Failed to connect to Kafka: {:s}'
            print(MSG.format(str(exc)), flush=True)
            time.sleep(delay)
    raise Exception('[init_kafka_producer] Could not connect to Kafka. Exiting.')

class Processor(threading.Thread):
    def __init__(self, message_queue : queue.Queue, attack_store : AttackStore) -> None:
        super().__init__(daemon=True)
        self.message_queue = message_queue
        self.attack_store = attack_store
        self.terminate = threading.Event()

    def stop(self) -> None:
        self.terminate.set()

    def run(self) -> None:
        try:
            producer = init_kafka_producer()

            while not self.terminate.is_set():
                try:
                    candidate = self.message_queue.get(block=True, timeout=1.0)
                except queue.Empty:
                    continue

                LOGGER.debug('Processing: {:s}'.format(str(candidate)))
                attacks = self.identify_attacks(candidate)
                LOGGER.debug('  attacks={:s}'.format(str(attacks)))

                if len(attacks) > 0:
                    LOGGER.info('Processing: {:s}'.format(str(candidate)))
                    LOGGER.info('  attacks={:s}'.format(str(attacks)))

                for attack in attacks:
                    producer.send(PUBISHER_TOPIC, value=attack)
                producer.flush()

        except Exception:
            LOGGER.exception('Unhandled Exception')

    def identify_attacks(self, candidate : Dict) -> List[Dict]:
        candidate_data   : numpy.array    = candidate['data']
        candidate_meta   : Dict[str, Any] = candidate['metadata']
        candidate_labels : Dict[int, str] = candidate['label_correspondence']
        ml_confidence    : float          = candidate.get('ml_confidence', 1.0)

        label_to_pos = {label:position for position,label in candidate_labels.items()}

        attacks = list()
        for i,row in enumerate(candidate_data):
            prob_normal_traffic      = row[label_to_pos['normal_traffic'     ]]
            prob_benign_heavy_hitter = row[label_to_pos['benign_heavy_hitter']]
            prob_malign_heavy_hitter = row[label_to_pos['malign_heavy_hitter']]

            if (prob_malign_heavy_hitter < prob_normal_traffic): continue
            if (prob_malign_heavy_hitter < prob_benign_heavy_hitter): continue

            attack_specs = self.attack_store.get('malign_heavy_hitter')

            if ml_confidence < attack_specs.min_ml_confidence_level:
                continue

            if prob_malign_heavy_hitter < attack_specs.probability_threshold:
                continue

            metadata = candidate_meta[i]
            if metadata['src_ip'] not in ADDRESSES_OF_INTEREST: continue

            attack = {'attack_uuid': attack_specs.attack_uuid}
            for meta_field_name in META_FIELD_NAMES:
                if meta_field_name not in metadata: continue
                attack[meta_field_name] = metadata[meta_field_name]

            attacks.append(attack)

        return attacks
