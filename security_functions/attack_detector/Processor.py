import json, logging, os, queue, threading, time
from kafka import KafkaProducer
from numpy import array
from typing import Any, Dict, List
from .AttackStore import AttackStore

LOGGER = logging.getLogger(__name__)

KAFKA_SERVER   = os.getenv('KAFKA_SERVER',   'localhost:9092'  )
PUBISHER_TOPIC = os.getenv('PUBISHER_TOPIC', 'attacks_detected')

META_FIELD_NAMES = {
    'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol', 'monitored_device', 'interface'
}

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
                    str_candidate = self.message_queue.get(block=True, timeout=1.0)
                except queue.Empty:
                    continue

                LOGGER.info('Processing: {:s}'.format(str(str_candidate)))
                attacks = self.identify_attacks(str_candidate)
                LOGGER.info('  attacks={:s}'.format(str(attacks)))
                for attack in attacks:
                    producer.send(PUBISHER_TOPIC, value=attack)
                producer.flush()

        except Exception:
            LOGGER.exception('Unhandled Exception')

    def identify_attacks(self, str_candidate : str) -> List[Dict]:
        attacks = list()

        try:
            candidate : Dict = eval(str_candidate.encode('UTF-8')) # pylint: disable=eval-used
        except Exception:
            LOGGER.exception('Unable to parse: {:s}'.format(str(str_candidate)))
            return attacks

        candidate_data   : array          = candidate['data']
        candidate_meta   : Dict[str, Any] = candidate['metadata'][0]
        candidate_labels : Dict[int, str] = candidate['label_correspondence']
        ml_confidence    : float          = candidate.get('ml_confidence', 1.0)

        for pos,label_name in candidate_labels.items():
            attack_specs = self.attack_store.get(label_name)

            if attack_specs is None:
                continue

            if attack_specs.attack_uuid in {'normal_traffic', 'benign_heavy_hitter'}:
                continue

            if ml_confidence < attack_specs.min_ml_confidence_level:
                continue

            probability = float(candidate_data[0][pos])
            if probability < attack_specs.probability_threshold:
                continue

            attack = {'attack_uuid': attack_specs.attack_uuid}
            for meta_field_name in META_FIELD_NAMES:
                if meta_field_name not in candidate_meta: continue
                attack[meta_field_name] = candidate_meta[meta_field_name]

            attacks.append(attack)

        return attacks
