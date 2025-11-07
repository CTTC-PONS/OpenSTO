import httpx
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from . import logger
from src.config import settings
from src.resources.models.wim import IETFNetworkGet, WIMServiceInfoGet

TIMEOUT = 3600

ACL_POST_URL     = 'restconf/data/device={}/ietf-access-control-list:acls'
ACL_DELETE_URL   = 'restconf/data/device={}/ietf-access-control-list:acl={}'
IETF_NETWORK_URL = 'restconf/data/ietf-network:networks'
TFS_TOPOLOGY     = 'tfs-api/context/{}/topology_details/{}'


@dataclass
class ConnectivityServiceCreateRequest:
    wim_ip: str
    wim_port: int
    source_port: str
    source_ip: str
    destination_port: str
    destination_ip: str


@dataclass
class ConnectivityServiceDeleteRequest:
    wim_ip: str
    wim_port: int
    connectivity_service_id: str


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
class ACLCreate:
    device_id : str
    name      : str
    acl_type  : ACLListType = ACLListType.IPV4
    entries   : List[ACLEntry] = field(default_factory=list)

    def compose(self) -> Dict[str, Any]:
        data = {'name': self.name, 'type': self.acl_type.value}
        aces : List[Dict] = data.setdefault('aces', dict()).setdefault('ace', list())
        for entry in self.entries:
            aces.append(entry.compose())
        return data

    def to_db_record(self) -> Dict[str, Any]:
        data = self.compose()
        data['device_id'] = self.device_id
        return data


@dataclass
class ACLInstallationLocation:
    device_id     : str
    interface_ids : Set[str] = field(default_factory=set)


@dataclass
class ACLGet:
    device_id: str
    name: str


@dataclass
class ACLDetele:
    device_id: str
    name: str


@dataclass
class ACLCreateRequest:
    acl_create: ACLCreate
    wim_ip: str
    wim_port: int


@dataclass
class ACLDeleteRequest:
    device_id: str
    acl_name: str
    wim_ip: str
    wim_port: int


@dataclass
class ACLGetRequest:
    device_id: str
    acl_name: str
    wim_ip: str
    wim_port: int


@dataclass
class WIMServiceInfoGetRequest:
    service_id: str
    wim_ip: str
    wim_port: int


@dataclass
class IETFNetworkGetRequest:
    wim_ip: str
    wim_port: int
    context: str = 'admin'
    topology: str = 'admin'


def get_ietf_acl(acl: ACLCreate) -> dict:
    # attachment_points : interface => {'ingress' : Set[ACL-Name], 'egress' : Set[ACL-Name]}
    if_acl_map : Dict[str, Dict[str, Set[str]]] = dict()
    for acl_entry in acl.entries:
        egress_if = acl_entry.egress_interface
        if egress_if is not None:
            direction : Dict[str, Set[str]] = if_acl_map.setdefault(egress_if, dict())
            acl_names : Set[str] = direction.setdefault('egress', set())
            acl_names.add(acl.name)

        ingress_if = acl_entry.ingress_interface
        if ingress_if is not None:
            direction : Dict[str, Set[str]] = if_acl_map.setdefault(ingress_if, dict())
            acl_names : Set[str] = direction.setdefault('ingress', set())
            acl_names.add(acl.name)

    logger.info('[get_ietf_acl] if_acl_map={:s}'.format(str(if_acl_map)))

    attachment_points : List[Dict] = list()
    for iface_id, direction_map in if_acl_map.items():
        attachment_point = {'interface-id' : iface_id}
        for direction, acl_names in direction_map.items():
            acl_set = [{'name': acl_name} for acl_name in acl_names]
            attachment_point[direction] = {'acl-sets': {'acl-set': acl_set}}
        attachment_points.append(attachment_point)

    logger.info('[get_ietf_acl] attachment_points={:s}'.format(str(attachment_points)))

    return {
        'ietf-access-control-list:acls': {
            'acl': [acl.compose()],
            'attachment-points': {'interface': attachment_points},
        }
    }


class TFS:
    def add_acl(self, request: ACLCreateRequest) -> dict:  # Returns device uuid value
        request_url = settings.TFS_NBI_BASE_URL(
            request.wim_ip, request.wim_port
        ) + ACL_POST_URL.format(request.acl_create.device_id)
        logger.info('[add_acl] request_url={:s}'.format(str(request_url)))
        ietf_acl_data = get_ietf_acl(request.acl_create)
        logger.info('[add_acl] ietf_acl_data={:s}'.format(str(ietf_acl_data)))
        r = httpx.post(request_url, json=ietf_acl_data, timeout=TIMEOUT).raise_for_status()
        return r.json()

    def delete_acl(self, request: ACLDeleteRequest) -> str:  # Returns device uuid value
        request_url = settings.TFS_NBI_BASE_URL(
            request.wim_ip, request.wim_port
        ) + ACL_DELETE_URL.format(request.device_id, request.acl_name)
        r = httpx.delete(request_url, timeout=TIMEOUT).raise_for_status()
        return r.json()

    def get_acl(self, request: ACLGetRequest) -> dict:  # Returns in IETF_ACL format
        request_url = (
            settings.TFS_NBI_BASE_URL(request.wim_ip, request.wim_port)
            + ACL_DELETE_URL.format(request.device_id, request.acl_name).raise_for_status()
        )
        r = httpx.get(request_url, timeout=TIMEOUT).raise_for_status()
        return r.json()

    def get_ietf_topology(self, request: IETFNetworkGetRequest) -> IETFNetworkGet:
        request_url = settings.TFS_NBI_BASE_URL(request.wim_ip, request.wim_port) + IETF_NETWORK_URL
        r = httpx.get(request_url, timeout=TIMEOUT).raise_for_status()
        return IETFNetworkGet.model_validate(r.json())

    def get_tfs_topology(self, request: IETFNetworkGetRequest) -> dict:
        request_url = settings.TFS_NBI_BASE_URL(
            request.wim_ip, request.wim_port
        ) + TFS_TOPOLOGY.format(request.context, request.topology)
        logger.info('[get_tfs_topology] request_url={:s}'.format(str(request_url)))
        r = httpx.get(request_url, timeout=TIMEOUT).raise_for_status()
        return r.json()

    def get_service_info(self, request: WIMServiceInfoGetRequest) -> WIMServiceInfoGet:
        raise NotImplementedError

    def create_network_service(self, request: ConnectivityServiceCreateRequest) -> str:
        request_url = settings.TFS_NBI_BASE_URL(request.wim_ip, request.wim_port)
        r = httpx.post(request_url, timeout=TIMEOUT).raise_for_status()
        return r.json()

    def delete_network_service(self, request: ConnectivityServiceDeleteRequest) -> None:
        request_url = settings.TFS_NBI_BASE_URL(request.wim_ip, request.wim_port)
        r = httpx.delete(request_url, timeout=TIMEOUT).raise_for_status()
        return r.json()
