from src.control.control_sbi import MirrorInvokeSignalRequest, SBIRequest
from src.control.controller import InvokeSignalingRequest, MirroringRequest
from src.resources.models.ssla.ssla import DSSLAAIO

from . import (
    NSF,
    DomainTranslation,
    FieldValueRequiredError,
    Firewall,
    FirewallWithProbe,
    OpenSTODomainServiceInfo,
    Probe,
    RuleType,
    ServiceContext,
    UnsupportedOpenSTOServiceInfoDataTypeError,
)


class SignalingDestinationAddressNotFound(Exception): ...


class MirroringRequestNotFoundError(Exception): ...


class DDoSProtectionHandler:
    def translate(self, domain_ssla_aio: DSSLAAIO, service_context: ServiceContext) -> DomainTranslation:

        nsfs = [NSF(Firewall())]
        probes = [Probe()]
        return DomainTranslation(probes=probes, nsfs=nsfs)
