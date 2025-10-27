from dataclasses import dataclass

from sqlmodel import Session

from src.control import ControllerCredentials
from src.exceptions import NSFNotSupportedError
from src.resources.models.ssla.capability import CapabilityGet
from src.resources.models.ssla.ssla import ESSLAAIOGet


@dataclass
class MapRequest:
    essla_aio: ESSLAAIOGet
    session: Session | None = None
    capabilities: list[CapabilityGet] | None = None
    topology: dict | None = None
    controller_credentials: ControllerCredentials | None = None
    service_id: str | None = None


def check_capability(required_capabilities: list[str], capabilities: list[CapabilityGet]) -> None:
    paths = []

    def hierarchi(item: dict | list, prefix: str = ''):
        if isinstance(item, dict):
            for k, v in item.items():
                if isinstance(v, str):
                    paths.append(prefix + f'.{k}.{v}')
                    continue
                hierarchi(v, prefix + f'.{k}')
        if isinstance(item, list):
            paths.extend([prefix + f'.{i}' for i in item])

    for c in capabilities:
        hierarchi(c.model_dump(by_alias=True))

    if not all(r in paths for r in required_capabilities):
        raise NSFNotSupportedError
