from src.exceptions import DomainSSLANotSupportedError
from src.resources.models.ssla.ssla import DSSLAAIO

from .plugins import DomainTranslation, ServiceContext, SSLAType, ssla_handlers


def make_decision(domain_ssla_aio: DSSLAAIO, service_context: ServiceContext) -> DomainTranslation:
    policy_rule_names = {p['name'] for p in domain_ssla_aio.policies}
    if policy_rule_names == {'traffic_mirroring', 'ddos_detection'}:
        ssla_handlers[SSLAType.DDOS_PROTECTION].translate(domain_ssla_aio, service_context)
    raise DomainSSLANotSupportedError
