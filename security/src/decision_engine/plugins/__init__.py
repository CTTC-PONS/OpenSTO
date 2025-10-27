from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field
from src.control.controller import MirroringRequest


class FieldValueRequiredError(Exception): ...


class UnsupportedOpenSTOServiceInfoDataTypeError(Exception): ...


class ActionType(str, Enum):
    MIRROR = 'mirror'
    DROP = 'drop'
    INVOKE_SIGNALING = 'invoke-signaling'


class RuleType(str, Enum):
    MIRROR = 'mirror'
    DROP = 'drop'
    INVOKE_SIGNALING = 'invoke-signaling'


class FirewallCondition(BaseModel):
    source: str | None = None
    destination: str | None = None


class DOS(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rate_limit: int = Field(alias='rate-limit')


class Condition(BaseModel):
    firewall: FirewallCondition | None = None
    ddos: DOS | None = None


class PrimaryAction(BaseModel):
    action: ActionType


class Action(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    primary_action: PrimaryAction = Field(alias='primary-action')


class Rule(BaseModel):
    name: str
    condition: Condition
    action: Action


class I2NSF_CFI_Policy(BaseModel):
    name: str
    rules: list[Rule]


class DeviceGroup(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    ipv4_prefix: str = Field(alias='ipv4-prefix')


class ENDPOINT_GROUPS(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    device_group: list[DeviceGroup] = Field(alias='device-group')


class PolicySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    i2nsf_cfi_policy: list[I2NSF_CFI_Policy] = Field(alias='i2nsf-cfi-policy')
    endpoint_groups: ENDPOINT_GROUPS = Field(alias='endpoint-groups')


class SSLAType(str, Enum):
    DDOS_PROTECTION = 'ddos_protection'


@dataclass
class ServiceInfo:
    ip_prefix: str
    domain: str


@dataclass
class OpenSTODomainServiceInfo:
    domain_info: MirroringRequest
    security_service: ServiceInfo


@dataclass
class OpenSTOE2EServiceInfo:
    security_service: ServiceInfo
    main_mano_service: ServiceInfo | None = None
    main_wim_service: ServiceInfo | None = None
    signaling_listener_ip_prefix: str | None = None


@dataclass
class OpenSTOServiceInfo:
    service_info: OpenSTOE2EServiceInfo | OpenSTODomainServiceInfo


@dataclass
class ServiceContext:
    provider: str


@dataclass
class E2ETranslation:
    domain: str
    ssla: str
    policy: str


@dataclass
class ProbeTranslation: ...


@dataclass
class Firewall: ...


@dataclass
class FirewallWithProbe: ...


@dataclass
class NSFTranslation:
    nsf: Firewall | FirewallWithProbe


@dataclass
class DomainTranslation:
    probes: list[ProbeTranslation] = field(default_factory=list)
    nsfs: list[NSFTranslation] = field(default_factory=list)
