import copy, operator, threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from _common.proto import attack_detector_pb2 as pb2

@dataclass
class AttackSpecs:
    attack_uuid             : str
    min_ml_confidence_level : float
    probability_threshold   : float

    @classmethod
    def from_proto(cls, attack_specs : pb2.AttackSpecs) -> 'AttackSpecs':
        return cls (
            attack_specs.attack_id.attack_uuid,
            attack_specs.min_ml_confidence_level,
            attack_specs.probability_threshold,
        )

    def update(self, attack_specs : pb2.AttackSpecs) -> None:
        self.min_ml_confidence_level = attack_specs.min_ml_confidence_level
        self.probability_threshold   = attack_specs.probability_threshold

    def to_proto(self) -> pb2.AttackSpecs:
        attack_specs = pb2.AttackSpecs()
        attack_specs.attack_id.attack_uuid   = self.attack_uuid
        attack_specs.min_ml_confidence_level = self.min_ml_confidence_level
        attack_specs.probability_threshold   = self.probability_threshold
        return attack_specs

@dataclass
class AttackStore:
    _lock : threading.Lock = threading.Lock()
    attacks : Dict[str, AttackSpecs] = field(default_factory=dict)

    def list(self) -> List[AttackSpecs]:
        with self._lock:
            attacks : List[AttackSpecs] = [
                copy.deepcopy(attack)
                for attack in self.attacks.values()
            ]
        return sorted(attacks, key=operator.attrgetter('attack_uuid'))

    def get(self, attack_uuid : str) -> Optional[AttackSpecs]:
        with self._lock:
            return self.attacks.get(attack_uuid)

    def set(self, attack_specs : pb2.AttackSpecs) -> None:
        attack_uuid = attack_specs.attack_id.attack_uuid
        with self._lock:
            if attack_uuid in self.attacks:
                self.attacks[attack_uuid].update(attack_specs)
            else:
                self.attacks[attack_uuid] = AttackSpecs.from_proto(attack_specs)

    def delete(self, attack_uuid : str) -> None:
        with self._lock:
            self.attacks.pop(attack_uuid, None)
