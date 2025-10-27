from dataclasses import dataclass
from typing import Protocol

from src.exceptions import SSLANotSupportedError
from src.resources.models.ssla.ssla import DXSLAAIO
from src.ssla_policy.plugins import MapRequest
from src.ssla_policy.plugins.acl.handler import ACLConfig

from . import logger
from .plugins.ssla_handlers import get_ssla_handlers


@dataclass
class Configuration:
    config: ACLConfig | DXSLAAIO


class SSLAPolicyProtocol(Protocol):
    def map(self, request: MapRequest) -> Configuration: ...


class SSLAPolicy:
    ssla_handlers = get_ssla_handlers()

    def map(self, request: MapRequest) -> Configuration:
        ssla_type = request.essla_aio.name
        logger.debug('%s selected as the ssla_type', ssla_type)
        if ssla_type not in self.ssla_handlers:
            raise SSLANotSupportedError
        return Configuration(self.ssla_handlers[ssla_type].translate(request))


sslap = SSLAPolicy()
