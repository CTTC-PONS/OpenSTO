import logging, os, pickle, queue, threading, time, uuid
from datetime import datetime, timezone
from enum import Enum
from ipaddress import IPv4Address
from kafka import KafkaProducer
from typing import List, Optional, Tuple
from .AttackModels import AttackModels, AttackSample, FlowRef
from .TfsApiClient import TfsApiClient
from .Topology import Topology

LOGGER = logging.getLogger(__name__)

KAFKA_SERVER   = os.getenv('KAFKA_SERVER',   'localhost:9092'  )
PUBISHER_TOPIC = os.getenv('PUBISHER_TOPIC', 'attacks_detected')
ACLS_TOPIC     = os.getenv('ACLS_TOPIC',     'acls'            )

ADDRESSES_OF_INTEREST = {
    IPv4Address('13.0.1.1'), IPv4Address('13.0.2.1'), 
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

class AclActionEnum(Enum):
    ACL_ADD    = 'add'
    ACL_REMOVE = 'remove'

def publish_acl_action(
    producer : KafkaProducer, flow_ref : FlowRef, acl_action : AclActionEnum,
    timestamp : Optional[datetime] = None, acl_rule_uuid : Optional[str] = None,
    flush : bool = True
) -> None:
    if timestamp is None: timestamp = datetime.now(timezone.utc)
    if acl_rule_uuid is None: acl_rule_uuid = str(uuid.uuid4())
    acl_rule = {
        'timestamp' : float(timestamp.timestamp()),
        'uuid'      : acl_rule_uuid,
        'src-ip'    : str(flow_ref.src_ip_addr),
        'dst-ip'    : str(flow_ref.dst_ip_addr),
        'proto'     : flow_ref.protocol,
        'src-port'  : flow_ref.src_port,
        'dst-port'  : flow_ref.dst_port,
        'action'    : acl_action.value,
    }
    producer.send(ACLS_TOPIC, value=acl_rule)
    if flush: producer.flush()

class Processor(threading.Thread):
    def __init__(
        self, message_queue : queue.Queue, attack_models : AttackModels, topology : Topology,
        tfs_api_client : TfsApiClient
    ) -> None:
        super().__init__(daemon=True)
        self.message_queue = message_queue
        self.attack_models = attack_models
        self.topology = topology
        self.topology_timestamp = None
        self.tfs_api_client = tfs_api_client
        self.terminate = threading.Event()

    def stop(self) -> None:
        self.terminate.set()

    def run(self) -> None:
        try:
            producer = init_kafka_producer()

            while not self.terminate.is_set():
                try:
                    attack_sample = self.message_queue.get(block=True, timeout=1.0)
                except queue.Empty:
                    continue

                attack_sample = AttackSample.from_dict(attack_sample)
                if attack_sample.attack_uuid in {'normal_traffic', 'benign_heavy_hitter'}: continue
                if attack_sample.src_ip_addr not in ADDRESSES_OF_INTEREST: continue

                LOGGER.info('Processing: {:s}'.format(str(attack_sample)))
                self.dispatch_attack(attack_sample, producer)

        except Exception:
            LOGGER.exception('Unhandled Exception')

    def dispatch_attack(self, attack_sample : AttackSample, producer : KafkaProducer) -> None:
        attack_ref = attack_sample.get_attack_ref()
        self.attack_models.add_attack_sample(attack_sample)

        now_timestamp = datetime.now(timezone.utc) 
        if (
            self.topology_timestamp is None or \
            (now_timestamp-self.topology_timestamp).total_seconds() > 30
        ):
            succeeded = self.topology.refresh()
            if succeeded:
                self.topology_timestamp = datetime.now(timezone.utc)

        self.attack_models.update_attack_end_devices(attack_ref, self.topology)
        firewall_acl_rule_set, mitigated_sources = self.attack_models.get_mitigation_acls(
            attack_ref, self.topology
        )

        acls_to_publish : List[Tuple[datetime, str, AclActionEnum]] = list()
        for firewall_uuid, acl_rule_set in firewall_acl_rule_set.items():
            self.tfs_api_client.configure_acl_rules(firewall_uuid, acl_rule_set)

            timestamp = datetime.now(timezone.utc)
            acl_rule_uuid = acl_rule_set.name
            acl_action = AclActionEnum.ACL_ADD
            acls_to_publish.append((timestamp, acl_rule_uuid, acl_action))

        self.attack_models.mark_mitigated_device_uuids(attack_ref, mitigated_sources)

        flow_ref = attack_sample.get_flow_ref()
        for timestamp, acl_rule_uuid, acl_action in acls_to_publish:
            publish_acl_action(
                producer, flow_ref, acl_action, timestamp=timestamp,
                acl_rule_uuid=acl_rule_uuid, flush=False
            )
        producer.flush()
