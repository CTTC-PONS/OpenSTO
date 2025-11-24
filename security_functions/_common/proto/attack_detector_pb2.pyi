from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AttackId(_message.Message):
    __slots__ = ("attack_uuid",)
    ATTACK_UUID_FIELD_NUMBER: _ClassVar[int]
    attack_uuid: str
    def __init__(self, attack_uuid: _Optional[str] = ...) -> None: ...

class AttackSpecs(_message.Message):
    __slots__ = ("attack_id", "probability_threshold", "min_ml_confidence_level")
    ATTACK_ID_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    MIN_ML_CONFIDENCE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    attack_id: AttackId
    probability_threshold: float
    min_ml_confidence_level: float
    def __init__(self, attack_id: _Optional[_Union[AttackId, _Mapping]] = ..., probability_threshold: _Optional[float] = ..., min_ml_confidence_level: _Optional[float] = ...) -> None: ...
