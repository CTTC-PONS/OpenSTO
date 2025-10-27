import logging
import os
from enum import Enum

logger = logging.getLogger('manager')


class DomainType(str, Enum):
    EDGE = 'edge'
    TRANSPORT = 'transport'
    CLOUD = 'cloud'
    EDGE_IP = 'edgeip'
    CLOUD_IP = 'cloudip'
    OPTICAL = 'optical'


def get_transport_domains_list() -> list[str]:
    domains = os.getenv('TRANSPORT_DOMAINS')
    return [d.lower() for d in domains.split(' ')]
