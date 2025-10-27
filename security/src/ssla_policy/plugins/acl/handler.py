import copy
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple
from src.control.tfs import ACLActionForward, ACLCreate, ACLEntry, ACLInstallationLocation, ACLListType
from src.ssla_policy import logger
from src.ssla_policy.plugins import MapRequest


@dataclass
class ACLConfig:
    acls: list[ACLCreate]


def is_any(device_name : str) -> bool:
    return device_name.lower() in {'any', 'all', '*'}

def is_external(device_type : str) -> bool:
    return device_type in {
        'client', 'datacenter', 'network', 'emu-client',
        'emu-computer', 'emu-datacenter', 'emu-virtual-machine',
    }

def decide_acl_installation_location(
    topology : dict, target_device : str
) -> Dict[str, ACLInstallationLocation]:
    # Parse the topology to retrieve all devices and their type
    for device in topology['devices']:
        device_name = device['name']
        if target_device == device_name:
            target_device_id = device['device_id']['device_uuid']['uuid']
            break
    else:
        raise ValueError(f'target device {target_device} not found in topology.')

    # Identify the links connected to target_device
    connected_links = []
    for link in topology['links']:
        for endpoint in link['link_endpoint_ids']:
            if endpoint['device_id']['device_uuid']['uuid'] == target_device_id:
                connected_links.append(link)
                break

    # Find the router connected to target_device through these links
    acl_installation_locations : Dict[str, ACLInstallationLocation] = dict()
    for link in connected_links:
        for endpoint in link['link_endpoint_ids']:
            device_id = endpoint['device_id']['device_uuid']['uuid']
            if device_id == target_device_id: continue
            for device in topology['devices']:
                if device['device_id']['device_uuid']['uuid'] != device_id: continue
                if device['device_type'] != 'packet-router': continue

                device_name = device['name']
                acl_il = acl_installation_locations.get(device_name)
                if acl_il is None:
                    acl_il = ACLInstallationLocation(device_name)
                    acl_installation_locations[device_name] = acl_il

                # Select the ports of the router
                for endpoint in device['device_endpoints']:
                    acl_il.interface_ids.add(endpoint['name'])

    return acl_installation_locations


# Maps ICMPv4 message to ICMPv4 (type,code)
ICMPv4_MESSAGE_TO_TYPE_CODE = {
    'echo-reply'                        : ( 0, None),
    'destination-unreachable'           : ( 3, None),
    'redirect'                          : ( 5, None),
    'echo'                              : ( 8, None),
    'router-advertisement'              : ( 9, None),
    'router-solicitation'               : (10, None),
    'time-exceeded'                     : (11, None),
    'parameter-problem'                 : (12, None),
    'experimental-mobility-protocols'   : (41, None),
    'extended-echo-request'             : (42, None),
    'extended-echo-reply'               : (43, None),
    'port-unreachable'                  : ( 3, 3),
    'request-no-error'                  : (42, 0),
    'reply-no-error'                    : (43, 0),
    'malformed-query'                   : (43, 1),
    'no-such-interface'                 : (43, 2),
    'no-such-table-entry'               : (43, 3),
    'multiple-interfaces-satisfy-query' : (43, 4),
}


class ACLHandler:
    required_capabilities: list[str] = []

    def translate_rule(
        self, rule : Dict, device_ipv4_prefixes : Dict
    ) -> Tuple[ACLEntry, str, str]:
        if 'name' not in rule:
            MSG = 'Missing attribute "name" in rule: {:s}'
            raise Exception(MSG.format(str(rule)))

        acl_entry = ACLEntry(name=rule['name'])

        if 'condition' not in rule:
            MSG = 'Missing attribute "condition" in rule: {:s}'
            raise Exception(MSG.format(str(rule)))
        condition = rule['condition']

        if 'firewall' not in condition:
            MSG = 'Missing attribute "firewall" in condition: {:s}'
            raise Exception(MSG.format(str(rule)))
        firewall = condition['firewall']

        src_device = firewall.get('source')
        if src_device is not None and not isinstance(src_device, str):
            MSG = 'Unsupported "source": {:s}'
            raise Exception(MSG.format(str(rule)))

        dst_device = firewall.get('destination')
        if dst_device is not None and not isinstance(dst_device, str):
            MSG = 'Unsupported "destination": {:s}'
            raise Exception(MSG.format(str(rule)))

        acl_entry.match_ipv4.dscp = 18

        if src_device is None:
            src_device_ip_prefix = '0.0.0.0/0'
        else:
            src_device_ip_prefix = device_ipv4_prefixes.get(src_device)
            if src_device_ip_prefix is None:
                MSG = 'DeviceGroup({:s}) not found: {:s}'
                raise Exception(MSG.format(str(src_device), str(device_ipv4_prefixes)))
        acl_entry.match_ipv4.src_ip_prefix = src_device_ip_prefix

        if dst_device is None:
            dst_device_ip_prefix = '0.0.0.0/0'
        else:
            dst_device_ip_prefix = device_ipv4_prefixes.get(dst_device)
            if dst_device_ip_prefix is None:
                MSG = 'DeviceGroup({:s}) not found: {:s}'
                raise Exception(MSG.format(str(dst_device), str(device_ipv4_prefixes)))
        acl_entry.match_ipv4.dst_ip_prefix = dst_device_ip_prefix

        if 'icmp' in firewall:
            acl_entry.match_ipv4.protocol = 1 # ICMP

            icmp_data = firewall['icmp']
            if 'message' in icmp_data:
                MSG = 'Explicit ICMP messages is unsupported: {:s}'
                raise Exception(MSG.format(str(rule)))
        else:
            src_port = None
            dst_port = None

            if 'source-range-port-number' in firewall:
                # Custom extension over draft-ietf-i2nsf-consumer-facing-interface-dm-31
                range_port_number = firewall['source-range-port-number']
                # assumed port numbers are destination ports
                start_port_number = range_port_number.get('start-port-number')
                end_port_number   = range_port_number.get('end-port-number')
                if start_port_number != end_port_number:
                    MSG = 'Unsupported "source-range-port-number": {:s}'
                    raise Exception(MSG.format(str(rule)))
                src_port = start_port_number

            if 'destination-range-port-number' in firewall:
                # Custom extension over draft-ietf-i2nsf-consumer-facing-interface-dm-31
                range_port_number = firewall['destination-range-port-number']
                # assumed port numbers are destination ports
                start_port_number = range_port_number.get('start-port-number')
                end_port_number   = range_port_number.get('end-port-number')
                if start_port_number != end_port_number:
                    MSG = 'Unsupported "range-port-number": {:s}'
                    raise Exception(MSG.format(str(rule)))
                dst_port = start_port_number

            if dst_port is None and 'range-port-number' in firewall:
                # Fallback to pure draft-ietf-i2nsf-consumer-facing-interface-dm-31
                range_port_number = firewall['range-port-number']
                # assumed port numbers are destination ports
                start_port_number = range_port_number.get('start-port-number')
                end_port_number   = range_port_number.get('end-port-number')
                if start_port_number != end_port_number:
                    MSG = 'Unsupported "range-port-number": {:s}'
                    raise Exception(MSG.format(str(rule)))
                dst_port = start_port_number

            transport_layer_protocol = firewall.get('transport-layer-protocol')
            if transport_layer_protocol == 'tcp':
                acl_entry.match_ipv4.protocol = 6 # TCP
                acl_entry.match_tcp.flags = 'syn'
                if src_port is not None: acl_entry.match_tcp.src_port = src_port
                if dst_port is not None: acl_entry.match_tcp.dst_port = dst_port
            elif transport_layer_protocol == 'udp':
                acl_entry.match_ipv4.protocol = 17 # UDP
                if src_port is not None: acl_entry.match_udp.src_port = src_port
                if dst_port is not None: acl_entry.match_udp.dst_port = dst_port
            else:
                MSG = 'Unsupported "transport-layer-protocol": {:s}'
                raise Exception(MSG.format(str(rule)))

        if 'action' not in rule:
            MSG = 'Missing attribute "action" in rule: {:s}'
            raise Exception(MSG.format(str(rule)))
        action = rule['action']

        if 'primary-action' not in action:
            MSG = 'Missing attribute "primary-action" in action: {:s}'
            raise Exception(MSG.format(str(rule)))
        primary_action = action['primary-action']

        if 'action' not in primary_action:
            MSG = 'Missing attribute "action" in primary-action: {:s}'
            raise Exception(MSG.format(str(rule)))
        action = primary_action['action']

        acl_entry.actions.forwarding = {
            'pass'   : ACLActionForward.ACCEPT,
            'drop'   : ACLActionForward.DROP,
            'reject' : ACLActionForward.REJECT,
        }[action]

        return acl_entry, src_device, dst_device

    def translate(self, request: MapRequest) -> ACLConfig:
        essla_aio = request.essla_aio
        topology = request.topology
        if not topology:
            raise ValueError('Topology is required for translation')
        service_id = request.service_id
        if not service_id:
            raise ValueError('Service ID is required for translation')
        if len(essla_aio.policies) != 1:
            raise ValueError('Only one policy is supported')
        policy = essla_aio.policies[0]['i2nsf-cfi-policy']

        device_ipv4_prefixes = {
            d['name'] : d['ipv4']
            for d in policy['endpoint-groups']['device-group']
        }

        target_device_acl_entries : Dict[str, List[ACLEntry]] = dict()
        for rule in policy['rules']:
            acl_entry, src_device, dst_device = self.translate_rule(rule, device_ipv4_prefixes)

            src_device_acl_entries : List[ACLEntry] = target_device_acl_entries.setdefault(src_device, list())
            src_device_acl_entries.append(acl_entry)

            dst_device_acl_entries : List[ACLEntry] = target_device_acl_entries.setdefault(dst_device, list())
            dst_device_acl_entries.append(acl_entry)

        acls : List[ACLCreate] = list()
        for target_device, acl_entries in target_device_acl_entries.items():
            logger.debug('protected device found: %s', target_device)
            acl_installation_locations = decide_acl_installation_location(topology, target_device)
            for acl_il in acl_installation_locations.values():
                for endpoint_name in sorted(acl_il.interface_ids):
                    acl_name = '{:s}--{:s}'.format(service_id, endpoint_name)
                    acl = ACLCreate(device_id=acl_il.device_id, name=acl_name)
                    acl.acl_type = ACLListType.IPV4
                    for acl_entry in acl_entries:
                        _acl_entry = copy.deepcopy(acl_entry)
                        # TODO: set ingress and egress interfaces for the flow
                        # instead of same interface
                        _acl_entry.egress_interface = endpoint_name
                        _acl_entry.ingress_interface = endpoint_name
                        acl.entries.append(_acl_entry)
                    acls.append(acl)

        return ACLConfig(acls=acls)
