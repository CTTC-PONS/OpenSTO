from typing import Protocol

from src.resources.models.ssla.ssla import DXSLAAIO
from src.ssla_policy.plugins import MapRequest
from src.ssla_policy.plugins.acl.handler import ACLConfig

from .acl.handler import ACLHandler
from .ddos.handler import DoSHandler
from .types import SSLAType


class SSLAHandlerProtocol(Protocol):
    required_capabilities: list[str]

    def translate(self, request: MapRequest) -> DXSLAAIO | ACLConfig: ...


def get_ssla_handlers() -> dict[SSLAType, SSLAHandlerProtocol]:
    def register_handler(ssla_type: SSLAType, handler_class: type[SSLAHandlerProtocol]):
        ssla_handlers[ssla_type] = handler_class()

    ssla_handlers: dict[SSLAType, SSLAHandlerProtocol] = {}
    register_handler(SSLAType.DOS_PREVENTION, DoSHandler)
    register_handler(SSLAType.ACL, ACLHandler)
    register_handler(SSLAType.HTTP_DEFAULT, ACLHandler)
    register_handler(SSLAType.HTTP_ALLOW_CLIENT, ACLHandler)
    return ssla_handlers
