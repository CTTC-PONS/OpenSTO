import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


LOGGER = logging.getLogger(__name__)


@dataclass
class ACLEntryMatchEth:
    ethertype            : Optional[int] = None
    src_mac_address      : Optional[str] = None
    dst_mac_address_mask : Optional[str] = None
    src_mac_address      : Optional[str] = None
    dst_mac_address_mask : Optional[str] = None

    def compose(self) -> Dict[str, Any]:
        data = dict()
        if self.ethertype            is not None: data['ethertype'                   ] = self.ethertype
        if self.src_mac_address      is not None: data['source-mac-address'          ] = self.src_mac_address
        if self.dst_mac_address_mask is not None: data['source-mac-address-mask'     ] = self.dst_mac_address_mask
        if self.src_mac_address      is not None: data['destination-mac-address'     ] = self.src_mac_address
        if self.dst_mac_address_mask is not None: data['destination-mac-address-mask'] = self.dst_mac_address_mask
        return {} if len(data) == 0 else {'eth' : data}


@dataclass
class ACLEntryMatchIPv4:
    dscp           : Optional[int] = None
    ecn            : Optional[int] = None
    length         : Optional[int] = None
    ttl            : Optional[int] = None
    protocol       : Optional[int] = None
    ihl            : Optional[int] = None
    flags          : Optional[str] = None
    offset         : Optional[int] = None
    identification : Optional[int] = None
    src_ip_prefix  : Optional[str] = None
    dst_ip_prefix  : Optional[str] = None

    def compose(self) -> Dict[str, Any]:
        data = dict()
        if self.dscp           is not None: data['dscp'                    ] = self.dscp
        if self.ecn            is not None: data['ecn'                     ] = self.ecn
        if self.length         is not None: data['length'                  ] = self.length
        if self.ttl            is not None: data['ttl'                     ] = self.ttl
        if self.protocol       is not None: data['protocol'                ] = self.protocol
        if self.ihl            is not None: data['ihl'                     ] = self.ihl
        if self.flags          is not None: data['flags'                   ] = self.flags
        if self.offset         is not None: data['offset'                  ] = self.offset
        if self.identification is not None: data['identification'          ] = self.identification
        if self.src_ip_prefix  is not None: data['source-ipv4-network'     ] = self.src_ip_prefix
        if self.dst_ip_prefix  is not None: data['destination-ipv4-network'] = self.dst_ip_prefix
        return {} if len(data) == 0 else {'ipv4' : data}


@dataclass
class ACLEntryMatchIPv6:
    dscp           : Optional[int] = None
    ecn            : Optional[int] = None
    length         : Optional[int] = None
    ttl            : Optional[int] = None
    protocol       : Optional[int] = None
    src_ip_prefix  : Optional[str] = None
    dst_ip_prefix  : Optional[str] = None
    flow_label     : Optional[str] = None

    def compose(self) -> Dict[str, Any]:
        data = dict()
        if self.dscp          is not None: data['dscp'                    ] = self.dscp
        if self.ecn           is not None: data['ecn'                     ] = self.ecn
        if self.length        is not None: data['length'                  ] = self.length
        if self.ttl           is not None: data['ttl'                     ] = self.ttl
        if self.protocol      is not None: data['protocol'                ] = self.protocol
        if self.src_ip_prefix is not None: data['source-ipv6-network'     ] = self.src_ip_prefix
        if self.dst_ip_prefix is not None: data['destination-ipv6-network'] = self.dst_ip_prefix
        if self.flow_label    is not None: data['flow-label'              ] = self.flow_label
        return {} if len(data) == 0 else {'ipv6' : data}


@dataclass
class ACLEntryMatchTCP:
    seq_number     : Optional[int] = None
    ack_number     : Optional[int] = None
    data_offset    : Optional[int] = None
    reserved       : Optional[int] = None
    flags          : Optional[str] = None
    window_size    : Optional[int] = None
    urgent_pointer : Optional[int] = None
    options        : Optional[int] = None
    src_port       : Optional[int] = None   # port ranges and operators still not supported
    dst_port       : Optional[int] = None   # port ranges and operators still not supported

    def compose(self) -> Dict[str, Any]:
        def compose_port(number : int) -> Dict:
            return {'port': number, 'operator': 'eq'}

        data = dict()
        if self.seq_number     is not None: data['sequence-number'       ] = self.seq_number
        if self.ack_number     is not None: data['acknowledgement-number'] = self.ack_number
        if self.data_offset    is not None: data['data-offset'           ] = self.data_offset
        if self.reserved       is not None: data['reserved'              ] = self.reserved
        if self.flags          is not None: data['flags'                 ] = self.flags
        if self.window_size    is not None: data['window-size'           ] = self.window_size
        if self.urgent_pointer is not None: data['urgent-pointer'        ] = self.urgent_pointer
        if self.options        is not None: data['options'               ] = self.options
        if self.src_port       is not None: data['source-port'           ] = compose_port(self.src_port)
        if self.dst_port       is not None: data['destination-port'      ] = compose_port(self.dst_port)
        return {} if len(data) == 0 else {'tcp' : data}


@dataclass
class ACLEntryMatchUDP:
    length   : Optional[int] = None
    src_port : Optional[int] = None   # port ranges and operators still not supported
    dst_port : Optional[int] = None   # port ranges and operators still not supported

    def compose(self) -> Dict[str, Any]:
        def compose_port(number : int) -> Dict:
            return {'port': number, 'operator': 'eq'}

        data = dict()
        if self.length   is not None: data['length'          ] = self.length
        if self.src_port is not None: data['source-port'     ] = compose_port(self.src_port)
        if self.dst_port is not None: data['destination-port'] = compose_port(self.dst_port)
        return {} if len(data) == 0 else {'udp' : data}


@dataclass
class ACLEntryMatchICMP:
    type           : Optional[int] = None
    code           : Optional[int] = None
    rest_of_header : Optional[str] = None

    def compose(self) -> Dict[str, Any]:
        data = dict()
        if self.type           is not None: data['type'          ] = self.type
        if self.code           is not None: data['code'          ] = self.code
        if self.rest_of_header is not None: data['rest-of-header'] = self.rest_of_header
        return {} if len(data) == 0 else {'icmp' : data}


class ACLActionForward(Enum):
    ACCEPT = 'accept'
    DROP   = 'drop'
    REJECT = 'reject'

class ACLActionLog(Enum):
    NONE   = 'log-none'
    SYSLOG = 'log-syslog'

@dataclass
class ACLActions:
    forwarding : ACLActionForward       = ACLActionForward.DROP
    logging    : Optional[ACLActionLog] = None

    def compose(self) -> Dict[str, Any]:
        data = {'forwarding': self.forwarding.value}
        if self.logging is not None: data['logging'] = self.logging.value
        return data


@dataclass
class ACLEntry:
    name              : str
    egress_interface  : Optional[str] = None
    ingress_interface : Optional[str] = None
    match_eth         : ACLEntryMatchEth  = field(default_factory=ACLEntryMatchEth )
    match_ipv4        : ACLEntryMatchIPv4 = field(default_factory=ACLEntryMatchIPv4)
    match_ipv6        : ACLEntryMatchIPv6 = field(default_factory=ACLEntryMatchIPv6)
    match_tcp         : ACLEntryMatchTCP  = field(default_factory=ACLEntryMatchTCP )
    match_udp         : ACLEntryMatchUDP  = field(default_factory=ACLEntryMatchUDP )
    match_icmp        : ACLEntryMatchICMP = field(default_factory=ACLEntryMatchICMP)
    actions           : ACLActions        = field(default_factory=ACLActions       )

    def compose(self) -> Dict[str, Any]:
        data = {'name': self.name}

        matches : Dict = data.setdefault('matches', dict())
        if self.egress_interface  is not None: matches['egress-interface' ] = self.egress_interface
        if self.ingress_interface is not None: matches['ingress-interface'] = self.ingress_interface

        matches.update(self.match_eth .compose())
        matches.update(self.match_ipv4.compose())
        matches.update(self.match_ipv6.compose())
        matches.update(self.match_tcp .compose())
        matches.update(self.match_udp .compose())
        matches.update(self.match_icmp.compose())

        actions : Dict = data.setdefault('actions', dict())
        actions.update(self.actions.compose())

        return data


class ACLListType(Enum):
    IPV4                = 'ipv4-acl-type'
    IPV6                = 'ipv6-acl-type'
    ETH                 = 'eth-acl-type'
    MIXED_ETH_IPV4      = 'mixed-eth-ipv4-acl-type'
    MIXED_ETH_IPV6      = 'mixed-eth-ipv6-acl-type'
    MIXED_ETH_IPV4_IPV6 = 'mixed-eth-ipv4-ipv6-acl-type'

@dataclass
class ACLRuleSet:
    name      : str
    acl_type  : ACLListType = ACLListType.IPV4
    entries   : List[ACLEntry] = field(default_factory=list)

    def compose(self) -> Dict[str, Any]:
        data = {'name': self.name, 'type': self.acl_type.value}
        aces : List[Dict] = data.setdefault('aces', dict()).setdefault('ace', list())
        for entry in self.entries:
            aces.append(entry.compose())
        return data

def get_ietf_acl(acl_rule_set : ACLRuleSet) -> Dict:
    # attachment_points : interface => {'ingress' : Set[ACL-Name], 'egress' : Set[ACL-Name]}
    if_acl_map : Dict[str, Dict[str, Set[str]]] = dict()
    for acl_entry in acl_rule_set.entries:
        egress_if = acl_entry.egress_interface
        if egress_if is not None:
            direction : Dict[str, Set[str]] = if_acl_map.setdefault(egress_if, dict())
            acl_names : Set[str] = direction.setdefault('egress', set())
            acl_names.add(acl_rule_set.name)

        ingress_if = acl_entry.ingress_interface
        if ingress_if is not None:
            direction : Dict[str, Set[str]] = if_acl_map.setdefault(ingress_if, dict())
            acl_names : Set[str] = direction.setdefault('ingress', set())
            acl_names.add(acl_rule_set.name)

    LOGGER.info('[get_ietf_acl] if_acl_map={:s}'.format(str(if_acl_map)))

    attachment_points : List[Dict] = list()
    for iface_id, direction_map in if_acl_map.items():
        attachment_point = {'interface-id' : iface_id}
        for direction, acl_names in direction_map.items():
            acl_set = [{'name': acl_name} for acl_name in acl_names]
            attachment_point[direction] = {'acl-sets': {'acl-set': acl_set}}
        attachment_points.append(attachment_point)

    LOGGER.info('[get_ietf_acl] attachment_points={:s}'.format(str(attachment_points)))

    return {
        'ietf-access-control-list:acls': {
            'acl': [acl_rule_set.compose()],
            'attachment-points': {'interface': attachment_points},
        }
    }

def compose_acl_rule_set() -> ACLRuleSet:
    acl_rule_set = ACLRuleSet()

    return acl_rule_set
