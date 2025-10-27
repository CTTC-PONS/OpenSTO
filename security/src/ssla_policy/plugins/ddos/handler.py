from src.resources.models.ssla.policy import DomainPolicyBase, DomainRuleBase
from src.resources.models.ssla.sls import SLS
from src.resources.models.ssla.ssla import DXSLAAIO
from src.ssla_policy.plugins import MapRequest, check_capability


class DoSHandler:
    required_capabilities = [
        '.nsf.condition-capabilities.generic-nsf-capabilities.ipv4-capability.source-address',
        '.nsf.condition-capabilities.generic-nsf-capabilities.ipv4-capability.destination-address',
        '.nsf.condition-capabilities.generic-nsf-capabilities.tcp-capability.source-port-number',
        '.nsf.condition-capabilities.generic-nsf-capabilities.tcp-capability.destination-port-number',
        '.nsf.action-capabilities.ingress-action-capability.invoke-signaling',
        '.nsf.action-capabilities.egress-action-capability.invoke-signaling',
    ]

    def translate(self, request: MapRequest) -> DXSLAAIO:
        capabilities = request.capabilities
        essla_aio = request.essla_aio
        if not capabilities:
            raise ValueError('Capabilities are required for translation')
        check_capability(self.required_capabilities, capabilities)

        traffic_mirroring_rules = [
            DomainRuleBase(
                name='traffic_mirroring_rule',
                description='mirror traffic from port of destination ip to monitoring entity',
                condition={'ipv4': {'destination-ipv4-network': 'x.x.x.x/x'}},
                action={'packet-action': {'ingress-action': 'mirror'}},
            )
        ]
        traffic_mirroring_policy = DomainPolicyBase(
            name='traffic_mirroring', rules=traffic_mirroring_rules
        )
        ddos_detection_rules = [
            DomainRuleBase(
                name='ddos_detection_rule',
                description='detect ddos attack to destination-ipv4-network and invoke-signaling',
                condition={
                    'ipv4': {'destination-ipv4-network': 'x.x.x.x/x'},
                    'tcp': {'destination-port-number': {'operator': 'eq', 'port': 'x'}},
                },
                action={'packet-action': {'ingress-action': 'invoke-signaling'}},
            )
        ]
        ddos_detection_policy = DomainPolicyBase(name='ddos_detection', rules=ddos_detection_rules)

        return DXSLAAIO(
            id=essla_aio.id,
            href=essla_aio.href,
            name=essla_aio.name,
            sls=SLS.model_validate(essla_aio.sls),
            policies=[traffic_mirroring_policy, ddos_detection_policy],
        )
