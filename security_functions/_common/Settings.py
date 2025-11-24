import enum, logging, os

class ServiceNameEnum(enum.Enum):
    TRAFFIC_SNIFFER = 'traffic-sniffer'

def get_service_host(service_name : ServiceNameEnum):
    return service_name.value

def get_setting(name, **kwargs):
    value = os.environ.get(name)
    if 'settings' in kwargs:
        value = kwargs['settings'].pop(name, value)
    if value is not None: return value
    if 'default' in kwargs: return kwargs['default']
    MSG = 'Setting({:s}) not specified in environment or configuration'
    raise Exception(MSG.format(str(name)))

def get_log_level(default : int = logging.WARNING):
    return get_setting('LOG_LEVEL', default=default)

def get_grpc_bind_address(default : str = '0.0.0.0'):
    return get_setting('GRPC_BIND_ADDRESS', default=default)

def get_grpc_bind_port(default : int = 50051):
    return get_setting('GRPC_BIND_PORT', default=default)

def get_grpc_max_workers(default : int = 200):
    return int(get_setting('GRPC_MAX_WORKERS', default=default))

def get_grpc_grace_period(default : int = 10):
    return int(get_setting('GRPC_GRACE_PERIOD', default=default))
