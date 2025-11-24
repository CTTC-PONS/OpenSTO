import logging, os
from datetime import datetime
from nfstream.flow import NFlow
from typing import Any, Dict

LOGGER = logging.getLogger(__name__)

# Set new name for field, or None to skip it
FEATURE_RENAMINGS = {
    'src_oui': 'source_oui',
    'dst_oui': 'destination_oui',
}

MONITORED_DEVICE  = str(os.getenv('MONITORED_DEVICE',  'router'))
SNIFFER_INTERFACE = str(os.getenv('SNIFFER_INTERFACE', 'eth1'  ))

def serialize_flow(flow : NFlow, timestamp : datetime) -> Dict:
    LOGGER.debug('Flow: {:s}'.format(str(flow)))

    feature_dict : Dict[str, Any] = dict()
    for attr_name in flow.__slots__:
        if attr_name == 'udps': continue
        try:
            attr_value = getattr(flow, attr_name)
            attr_name = FEATURE_RENAMINGS.get(attr_name, attr_name)
            if attr_name is None: continue
            feature_dict[attr_name] = attr_value
        except AttributeError:
            pass

    return {
        'data': {'features': feature_dict},
        'metadata': {
            'timestamp': timestamp,
            'monitored_device': MONITORED_DEVICE,
            'interface': SNIFFER_INTERFACE,
            'connection_id': {
                'src_ip'  : flow.src_ip,
                'dst_ip'  : flow.dst_ip,
                'src_port': flow.src_port,
                'dst_port': flow.dst_port,
                'protocol': flow.protocol,
            },
            'flow_pkts' : flow.bidirectional_packets,
            'flow_bytes': flow.bidirectional_bytes,
        },
    }
