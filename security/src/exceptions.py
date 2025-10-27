class CustomException(Exception):
    detail = ''


class CustomNotFoundException(CustomException): ...


class RequestNotSupported(CustomException):
    detail = 'request not supported'


class InvalidRunningModeError(CustomException):
    detail = 'invalid running mode'


class DomainSSLANotSupportedError(CustomException):
    detail = 'domain ssla not supported'


class GatewayNotFoundError(CustomNotFoundException):
    detail = 'gateway not found'


class DC2RouterMultiplePathsError(CustomException):
    detail = 'multiple paths found between datacenter and router'


class MonitoringPortsNotFound(CustomNotFoundException):
    detail = 'monitoring port not found'


class DatacenterNotFound(CustomNotFoundException):
    detail = 'datacenter not found'


class SSLANotFoundError(CustomNotFoundException):
    detail = 'ssla not found'


class SLSNotFoundError(CustomNotFoundException):
    detail = 'sls not found'


class OpenSTOServiceNotFoundError(CustomNotFoundException):
    detail = 'opensto service not found'


class ControllerNotFoundError(CustomNotFoundException):
    detail = 'controller not found'


class NetworkServiceNotFoundError(CustomNotFoundException):
    detail = 'network service not found'


class NetworkServiceInstanceNotFoundError(CustomNotFoundException):
    detail = 'network service instance not found'


class NetworkServiceInfoNotFoundError(CustomNotFoundException):
    detail = 'network service information not found'


class ClosedLoopRequestNotFoundError(CustomNotFoundException):
    detail = 'closed loop request not found'


class ClosedLoopDeactivatedError(CustomException):
    detail = 'closed loop is deactivated'


class NetworkServiceDescriptionNotFound(CustomNotFoundException):
    detail = 'network service description not found'


class NetworkSecurityFunctionNotFoundError(CustomNotFoundException):
    detail = 'network security function description not found'


class NetworkServiceTemplateNotFound(CustomNotFoundException):
    detail = 'network service template not found'


class ProviderNotFoundError(CustomNotFoundException):
    detail = 'provider not found'


class ProbeNotFoundError(CustomNotFoundException):
    detail = 'probe not found'


class FirewallNotFoundError(CustomNotFoundException):
    detail = 'firewall not found'


class NetSecurityFunctionInstaceNotFoundError(CustomNotFoundException):
    detail = 'network security function instance not found'


class TopologyNotFoundError(CustomNotFoundException):
    detail = 'topology not found'


class NodeNotFoundError(CustomNotFoundException):
    detail = 'node not found'


class EndpointNotFound(CustomNotFoundException):
    detail = 'endpoint not found'


class InvalidTopologyError(CustomException):
    detail = 'invalid topology'


class InvalidNFVONameError(CustomException):
    detail = 'invalid NFVO name'


class SSLANotSupportedError(CustomException):
    detail = 'ssla not supported'


class FieldValueRequiredError(CustomException):
    detail = 'field value required'


class NSFNotSupportedError(CustomException):
    detail = 'NSF not supported'


class WIMServiceInfoNotFoundError(CustomNotFoundException):
    detail = 'wim service information not found'


class InvalidDomainTypeError(CustomException):
    detail = 'invalid domain type'


class CapabilityNotFoundError(CustomNotFoundException):
    detail = 'capability not found'
