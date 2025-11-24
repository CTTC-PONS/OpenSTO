import copy, json, logging, networkx, threading
from ipaddress import IPv4Address, IPv4Interface
from networkx.algorithms.approximation import steiner_tree
from typing import Dict, List, Set, Tuple, Union
from .TfsApiClient import TfsApiClient

LOGGER = logging.getLogger(__name__)

class Topology:
    def __init__(self, tfs_api_client : TfsApiClient):
        self._tfs_api_client = tfs_api_client
        self._lock = threading.Lock()
        self._network = networkx.Graph()
        self._ipif_to_device_endpoint : Dict[IPv4Interface, Tuple[str, str]] = dict()
        self._device_endpoint_to_ipif : Dict[Tuple[str, str], IPv4Interface] = dict()

    def get_device_endpoint_from_ip_addr(self, ip_address : IPv4Address) -> Tuple[str, str]:
        with self._lock:
            for ipif,device_endpoint_uuid in self._ipif_to_device_endpoint.items():
                if ipif.ip == ip_address:
                    return device_endpoint_uuid
            return self._ipif_to_device_endpoint[IPv4Interface('0.0.0.0/0')]

    def get_target_firewalls(
        self, src_device_uuids : Set[str], dst_device_uuids : Set[str], involved_device_uuids : Set[str] = set()
    ) -> Dict:
        WEIGHT = 'weight'

        if len(dst_device_uuids) != 1:
            MSG = 'Unsupported number of destinations: {:s}'
            raise Exception(MSG.format(str(dst_device_uuids)))
        dst_device_uuid = copy.deepcopy(dst_device_uuids).pop()
        
        # Compose set of devices required (sources U {destination} U involved)
        required : Set[str] = set()
        required.update(src_device_uuids)
        required.add(dst_device_uuid)
        required.update(involved_device_uuids)

        MSG = '[get_target_firewalls] required={:s}'
        LOGGER.info(MSG.format(str(required)))

        # Build a Steiner tree over required devices
        stree = steiner_tree(self._network, required, weight=WEIGHT)
        MSG = '[get_target_firewalls] Steiner tree edges: {:s}'
        LOGGER.info(MSG.format(str(list(stree.edges(data=True)))))

        # Dict[src_device_uuid] => {path_src_to_dst, firewall_device_uuid, firewall_endpoint_uuid}
        target_firewalls : Dict[str, Dict] = dict()

        # For each source find the first firewall actually traversed on the
        # path source -> destination in that Steiner tree.
        for src_device_uuid in src_device_uuids:
            # Compute path source -> destination in the Steiner tree
            path_src_to_dst = networkx.shortest_path(
                stree, src_device_uuid, dst_device_uuid, weight=WEIGHT
            )

            firewall_device_uuid = None
            firewall_endpoint_uuid = None

            # Scan path to find first firewall (closest to source along the path)
            for idx, device_uuid in enumerate(path_src_to_dst):
                if idx == 0: continue  # skip the source itself
                candidate_device = self._network.nodes[device_uuid]
                is_firewall = candidate_device.get('is_firewall', False)
                if not is_firewall : continue

                firewall_device_uuid = device_uuid
                prev_device_uuid = path_src_to_dst[idx - 1]

                # Edge data from network
                edge_data = self._network[prev_device_uuid][device_uuid]
                endpoints = edge_data.get('endpoints', dict())
                firewall_endpoint_uuid = endpoints.get(device_uuid, None)

                break

            target_firewalls[src_device_uuid] = {
                'firewall_device_uuid': firewall_device_uuid,
                'firewall_endpoint_uuid': firewall_endpoint_uuid,
                'path_src_to_dst': path_src_to_dst,
            }

        return target_firewalls

    def load(self) -> None:
        with self._lock:
            self._load_unsafe()

    def _load_unsafe(self) -> None:
        json_topology = self._tfs_api_client.get_topology()
        if not isinstance(json_topology, dict):
            raise Exception('Topology is not a dict')

        self._network.clear()
        self._ipif_to_device_endpoint.clear()
        self._device_endpoint_to_ipif.clear()

        devices : List[Dict] = json_topology.get('devices', [])
        links   : List[Dict] = json_topology.get('links',   [])

        # Build nodes with their endpoints and record IP/interface mappings.
        for device in devices:
            device_uuid  = device['device_id']['device_uuid']['uuid']
            config_rules = device.get('device_config', {}).get('config_rules', [])

            endpoints : Set[str] = set()

            for rule in config_rules:
                custom = rule.get('custom')
                if custom is None: continue

                resource_key : str = custom['resource_key']
                if resource_key in {'_connect/address', '_connect/port'}: continue

                resource_value : Union[str, Dict] = custom['resource_value']
                if isinstance(resource_value, str):
                    try:
                        resource_value = json.loads(resource_value)
                    except:
                        pass

                if resource_key == '_connect/settings':
                    connect_settings_endpoints = resource_value.get('endpoints', [])
                    for endpoint in connect_settings_endpoints:
                        endpoint_uuid = endpoint.get('uuid')
                        if endpoint_uuid is None: continue
                        endpoints.add(endpoint_uuid)

                elif resource_key.startswith('/endpoint[') and resource_key.endswith(']/settings'):
                    endpoint_uuid = resource_key[len('/endpoint['):-len(']/settings')]
                    if len(endpoint_uuid) == 0: continue
                    endpoints.add(endpoint_uuid)

                    address_ip     = resource_value.get('address_ip')
                    address_prefix = resource_value.get('address_prefix')
                    if address_ip is None: continue
                    if address_prefix is None: continue

                    try:
                        ip_interface = IPv4Interface(f'{address_ip}/{address_prefix}')
                    except ValueError:
                        continue

                    self._ipif_to_device_endpoint[ip_interface] = (device_uuid, endpoint_uuid)
                    self._device_endpoint_to_ipif[(device_uuid, endpoint_uuid)] = ip_interface

            device_type = device.get('device_type')
            device_drivers = device.get('device_drivers', [])
            firewall_drivers = {'DEVICEDRIVER_UNDEFINED', 'DEVICEDRIVER_GNMI_OPENCONFIG'}

            is_firewall = (
                ('firewall' in device_type or 'packet-router' in device_type)
                and
                (len(set(device_drivers).intersection(firewall_drivers)) > 0)
            )

            self._network.add_node(
                device_uuid,
                is_firewall=is_firewall,
                device_type=device_type,
                device_drivers=device_drivers,
                endpoints=endpoints
            )

        # Add edges using link information, keeping track of multiple links between nodes.
        for link in links:
            link_endpoint_ids = link['link_endpoint_ids']
            if len(link_endpoint_ids) != 2: continue

            device_uuids : List[str] = list()
            link_endpoints : Dict[str, Set[str]] = dict()
            for endpoint_id in link_endpoint_ids:
                device_uuid = endpoint_id['device_id']['device_uuid']['uuid']
                endpoint_uuid = endpoint_id['endpoint_uuid']['uuid']
                if device_uuid not in self._network: continue
                device_uuids.append(device_uuid)
                link_endpoints[device_uuid] = endpoint_uuid

            if len(device_uuids) != 2: raise Exception('Malformed Link: {:s}'.format(str(link)))
            if len(link_endpoints) != 2: raise Exception('Malformed Link: {:s}'.format(str(link)))

            device_a, device_b = device_uuids[0], device_uuids[-1]
            if self._network.has_edge(device_a, device_b): continue # skip bidirectional links

            self._network.add_edge(device_a, device_b, endpoints=link_endpoints)
