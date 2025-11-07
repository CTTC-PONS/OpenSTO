from dataclasses import dataclass
from enum import Enum

from src.control.control_sbi import SBIRequest
from src.control.controller import MirroringRequest


class SSLAType(str, Enum):
    DOS_PREVENTION = 'ddos_protection'
    ACL = 'ssh-block-service'
    HTTP_DEFAULT = 'http-default'
    HTTP_ALLOW_CLIENT = 'http-allow-client'


class SLS_UUIDS(str, Enum):
    DOS_PREVENTION = '0ddaa555-0de1-2567-0953-4eb432b7ab27'
    MIRROR_INVOKE_SIGNAL = 'abe4a771-d7ad-4758-96ee-ce72c707cdb6'


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
class E2ETranslation:
    domain: str
    ssla: str
    policy: str


@dataclass
class DomainTranslation:
    sbi_request: SBIRequest
