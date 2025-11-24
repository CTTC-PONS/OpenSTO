import logging, threading, uuid
from dataclasses import dataclass, field
from ipaddress import IPv4Address
from typing import Dict, Set, Tuple
from .AclComposer import ACLActionForward, ACLEntry, ACLListType, ACLRuleSet
from .Topology import Topology

LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True)
class FlowRef:
    src_ip_addr : IPv4Address
    src_port    : int
    dst_ip_addr : IPv4Address
    dst_port    : int
    protocol    : int

@dataclass(frozen=True)
class AttackRef:
    attack_uuid : str
    src_ip_addr : IPv4Address
    src_port    : int
    dst_ip_addr : IPv4Address
    dst_port    : int
    protocol    : int

@dataclass
class AttackSample:
    attack_uuid : str
    src_ip_addr : IPv4Address
    src_port    : int
    dst_ip_addr : IPv4Address
    dst_port    : int
    protocol    : int
    device      : str

    @classmethod
    def from_dict(cls, json_attack_sample : Dict) -> 'AttackSample':
        return cls(
            attack_uuid = str        (json_attack_sample['attack_uuid'     ]),
            src_ip_addr = IPv4Address(json_attack_sample['src_ip'          ]),
            src_port    = int        (json_attack_sample['src_port'        ]),
            dst_ip_addr = IPv4Address(json_attack_sample['dst_ip'          ]),
            dst_port    = int        (json_attack_sample['dst_port'        ]),
            protocol    = int        (json_attack_sample['protocol'        ]),
            device      = str        (json_attack_sample['monitored_device']),
        )

    def get_attack_ref(self) -> AttackRef:
        return AttackRef(
            attack_uuid = self.attack_uuid,
            src_ip_addr = self.src_ip_addr,
            src_port    = self.src_port,
            dst_ip_addr = self.dst_ip_addr,
            dst_port    = self.dst_port,
            protocol    = self.protocol,
        )

    def get_flow_ref(self) -> FlowRef:
        return FlowRef(
            src_ip_addr = self.src_ip_addr,
            src_port    = self.src_port,
            dst_ip_addr = self.dst_ip_addr,
            dst_port    = self.dst_port,
            protocol    = self.protocol,
        )

@dataclass
class AttackModel:
    attack_ref               : AttackRef
    source_device_uuids      : Set[str] = field(default_factory=set)
    involved_device_uuids    : Set[str] = field(default_factory=set)
    destination_device_uuids : Set[str] = field(default_factory=set)
    mitigated_device_uuids   : Set[str] = field(default_factory=set)

    def add_attack_sample(self, attack_sample : AttackSample) -> None:
        self.involved_device_uuids.add(attack_sample.device)

    def update_attack_end_devices(self, topology : Topology) -> None:
        src_ip_addr = self.attack_ref.src_ip_addr
        src_device_endpoint_uuid = topology.get_device_endpoint_from_ip_addr(src_ip_addr)
        if src_device_endpoint_uuid is None:
            MSG = '[update_attack_end_devices] Unable to map AttackRef({:s})/src_ip_addr({:s}) to device/endpoint'
            LOGGER.warning(MSG.format(str(self.attack_ref), str(src_ip_addr)))
            return
        self.source_device_uuids.add((src_device_endpoint_uuid[0]))
        
        dst_ip_addr = self.attack_ref.dst_ip_addr
        dst_device_endpoint_uuid = topology.get_device_endpoint_from_ip_addr(dst_ip_addr)
        if dst_device_endpoint_uuid is None:
            MSG = '[update_attack_end_devices] Unable to map AttackRef({:s})/dst_ip_addr({:s}) to device/endpoint'
            LOGGER.warning(MSG.format(str(self.attack_ref), str(dst_ip_addr)))
            return
        self.destination_device_uuids.add((dst_device_endpoint_uuid[0]))

    def get_target_firewalls(self, topology : Topology) -> Dict[str, Dict]:
        LOGGER.info('[get_target_firewalls] source_device_uuids={:s}'.format(str(self.source_device_uuids)))
        LOGGER.info('[get_target_firewalls] destination_device_uuids={:s}'.format(str(self.destination_device_uuids)))
        LOGGER.info('[get_target_firewalls] involved_device_uuids={:s}'.format(str(self.involved_device_uuids)))
        target_firewalls = topology.get_target_firewalls(
            self.source_device_uuids, self.destination_device_uuids, self.involved_device_uuids
        )
        LOGGER.info('[get_target_firewalls] target_firewalls={:s}'.format(str(target_firewalls)))
        return target_firewalls

    def get_mitigation_acls(self, topology : Topology) -> Tuple[Dict[str, ACLRuleSet], Set[str]]:
        target_firewalls = self.get_target_firewalls(topology)

        acl_ruleset_uuid = str(uuid.uuid4())
        acl_ruleset_name = 'opensto-{:s}-{:s}'.format(self.attack_ref.attack_uuid, acl_ruleset_uuid)

        firewall_acl_rule_set : Dict[str, ACLRuleSet] = dict()
        mitigated_sources : Set[str] = set()
        for src_device_uuid in self.source_device_uuids:
            if src_device_uuid in self.mitigated_device_uuids: continue

            target_firewall = target_firewalls[src_device_uuid]

            firewall_device_uuid = target_firewall['firewall_device_uuid']
            if firewall_device_uuid is None:
                MSG = 'Attack({:s}): Unable to identify Firewall for Source({:s})'
                LOGGER.warning(MSG.format(str(self.attack_ref), str(src_device_uuid)))
                continue

            firewall_endpoint_uuid = target_firewall['firewall_endpoint_uuid']
            if firewall_endpoint_uuid is None:
                MSG = 'Attack({:s}): Unable to identify interface in Firewall({:s}) for Source({:s})'
                LOGGER.warning(MSG.format(
                    str(self.attack_ref), str(firewall_device_uuid), str(src_device_uuid)
                ))
                continue

            if self.attack_ref.protocol not in {1, 6, 17}: # ICMP, TCP, UDP
                MSG = 'Attack({:s}): Unsupported Protocol({:s})'
                LOGGER.warning(MSG.format(
                    str(self.attack_ref), str(self.attack_ref.protocol)
                ))
                continue

            if firewall_device_uuid not in firewall_acl_rule_set:
                firewall_acl_rule_set[firewall_device_uuid] = ACLRuleSet(
                    name=acl_ruleset_name, acl_type=ACLListType.IPV4
                )
            acl_rule_set = firewall_acl_rule_set[firewall_device_uuid]

            acl_entry_name = 'opensto-{:s}-{:s}-{:s}'.format(
                src_device_uuid, firewall_endpoint_uuid, acl_ruleset_uuid
            )
            acl_entry = ACLEntry(name=acl_entry_name)
            acl_entry.ingress_interface        = firewall_endpoint_uuid
            acl_entry.match_ipv4.src_ip_prefix = '{:s}/32'.format(str(self.attack_ref.src_ip_addr))
            acl_entry.match_ipv4.dst_ip_prefix = '{:s}/32'.format(str(self.attack_ref.dst_ip_addr))

            acl_entry.match_ipv4.protocol      = self.attack_ref.protocol
            if self.attack_ref.protocol == 1: # ICMP
                pass
            elif self.attack_ref.protocol == 6: # TCP
                acl_entry.match_tcp.src_port = self.attack_ref.src_port
                acl_entry.match_tcp.dst_port = self.attack_ref.dst_port
            elif self.attack_ref.protocol == 17: # UDP
                acl_entry.match_udp.src_port = self.attack_ref.src_port
                acl_entry.match_udp.dst_port = self.attack_ref.dst_port
            else:
                pass # controlled before

            acl_entry.actions.forwarding = ACLActionForward.DROP

            acl_rule_set.entries.append(acl_entry)
            mitigated_sources.add(src_device_uuid)

        LOGGER.info('[get_mitigation_acls] firewall_acl_rule_set={:s}'.format(str(firewall_acl_rule_set)))
        LOGGER.info('[get_mitigation_acls] mitigated_sources={:s}'.format(str(mitigated_sources)))
        return firewall_acl_rule_set, mitigated_sources

    def mark_mitigated_device_uuids(self, mitigated_device_uuids : Set[str]) -> None:
        self.mitigated_device_uuids.update(mitigated_device_uuids)

@dataclass
class AttackModels:
    _lock : threading.Lock = threading.Lock()
    attacks : Dict[AttackRef, AttackModel] = field(default_factory=dict)

    def _get_or_create_unsafe(self, attack_ref : AttackRef) -> AttackModel:
        if attack_ref not in self.attacks:
            attack_model = self.attacks.setdefault(attack_ref, AttackModel(attack_ref=attack_ref))
        else:
            attack_model = self.attacks.get(attack_ref)
        return attack_model

    def add_attack_sample(self, attack_sample : AttackSample) -> None:
        with self._lock:
            attack_ref = attack_sample.get_attack_ref()
            attack_model = self._get_or_create_unsafe(attack_ref)
            attack_model.add_attack_sample(attack_sample)

    def update_attack_end_devices(self, attack_ref : AttackRef, topology : Topology) -> None:
        with self._lock:
            attack_model = self._get_or_create_unsafe(attack_ref)
            attack_model.update_attack_end_devices(topology)

    def get_target_firewalls(self, attack_ref : AttackRef, topology : Topology) -> Dict[str, Dict]:
        with self._lock:
            attack_model = self._get_or_create_unsafe(attack_ref)
            target_firewalls = attack_model.get_target_firewalls(topology)
            return target_firewalls

    def get_mitigation_acls(
        self, attack_ref : AttackRef, topology : Topology
    ) -> Tuple[Dict[str, ACLRuleSet], Set[str]]:
        with self._lock:
            attack_model = self._get_or_create_unsafe(attack_ref)
            firewall_acl_rule_set, mitigated_sources = attack_model.get_mitigation_acls(topology)
            return firewall_acl_rule_set, mitigated_sources

    def mark_mitigated_device_uuids(self, attack_ref : AttackRef, mitigated_device_uuids : Set[str]) -> None:
        with self._lock:
            attack_model = self._get_or_create_unsafe(attack_ref)
            attack_model.mark_mitigated_device_uuids(mitigated_device_uuids)
