import logging, os, queue, threading, time
from kafka import KafkaProducer
from numpy import array
from typing import Dict

LOGGER = logging.getLogger(__name__)

KAFKA_SERVER   = os.getenv('KAFKA_SERVER',   'localhost:9092' )
PUBISHER_TOPIC = os.getenv('PUBISHER_TOPIC', 'inference_probs')

def init_kafka_producer(retries: int = 30, delay: float = 3) -> KafkaProducer:
    for attempt in range(1, retries + 1):
        MSG = '[init_kafka_producer] Try #{:d}/{:d}: Connecting to Kafka...'
        print(MSG.format(attempt, retries), flush=True)
        try:
            return KafkaProducer(
                bootstrap_servers = KAFKA_SERVER, 
                value_serializer = lambda o: str(o).encode('utf-8'),
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
                    traffic_flow = self.message_queue.get(block=True, timeout=1.0)
                except queue.Empty:
                    continue

                LOGGER.info('Processing: {:s}'.format(str(traffic_flow)))
                inference_probs = self.do_inference(traffic_flow)
                LOGGER.info('  inference_probs={:s}'.format(str(inference_probs)))
                producer.send(PUBISHER_TOPIC, value=str(inference_probs))
                producer.flush()
        except Exception:
            LOGGER.exception('Unhandled Exception')

    def do_inference(self, traffic_flow : Dict) -> Dict:
        data : Dict = traffic_flow.get('data', dict())
        features : Dict = data.get('features', dict())
        ip_version = features.get('ip_version')
        src_ip     = features.get('src_ip'    )
        dst_ip     = features.get('dst_ip'    )
        src_port   = features.get('src_port'  )
        dst_port   = features.get('dst_port'  )
        protocol   = features.get('protocol'  )

        metadata : Dict = traffic_flow.get('metadata', dict())
        mon_device = metadata.get('monitored_device')
        interface  = metadata.get('interface'       )
        flow_pkts  = metadata.get('flow_pkts'       )
        flow_bytes = metadata.get('flow_bytes'      )

        if ip_version == 6 or protocol not in {1, 6, 17}:
            prob_normal_traffic      = float(1.0)
            prob_benign_heavy_hitter = float(0.0)
            prob_malign_heavy_hitter = float(0.0)
        elif src_ip == '13.0.1.1':
            prob_normal_traffic      = float(0.2)
            prob_benign_heavy_hitter = float(0.2)
            prob_malign_heavy_hitter = float(0.6)
        elif src_ip == '13.0.2.1':
            prob_normal_traffic      = float(0.1)
            prob_benign_heavy_hitter = float(0.8)
            prob_malign_heavy_hitter = float(0.1)
        else:
            prob_normal_traffic      = float(0.0)
            prob_benign_heavy_hitter = float(0.0)
            prob_malign_heavy_hitter = float(1.0)

        metadata = {
            'monitored_device' : mon_device,
            'interface'        : interface,
            'src_ip'           : src_ip,
            'dst_ip'           : dst_ip,
            'src_port'         : src_port,
            'dst_port'         : dst_port,
            'protocol'         : protocol,
            'flow_bytes'       : flow_pkts,
            'flow_pkts'        : flow_bytes,
        }
        inference_probs = {
            'data': array([[
                float(prob_normal_traffic),
                float(prob_benign_heavy_hitter),
                float(prob_malign_heavy_hitter),
            ]]),
            'metadata': [metadata],
            'label_correspondence': {
                0: 'normal_traffic',
                1: 'benign_heavy_hitter',
                2: 'malign_heavy_hitter'
            }
        }
        return inference_probs
