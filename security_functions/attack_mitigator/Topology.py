import copy, json, logging, networkx, threading
from ipaddress import IPv4Address, IPv4Interface
from networkx.algorithms.approximation import steiner_tree
from typing import Dict, List, Optional, Set, Tuple, Union
from .TfsApiClient import TfsApiClient

LOGGER = logging.getLogger(__name__)

class Topology:
    def __init__(self, tfs_api_client : TfsApiClient):
        self._tfs_api_client = tfs_api_client
        self._lock = threading.Lock()
        self._network = networkx.Graph()
        self._device_id_to_uuid : Dict[str, str] = dict()
        self._device_id_to_name : Dict[str, str] = dict()
        self._endpoint_id_to_uuid : Dict[Tuple[str, str], str] = dict()
        self._endpoint_id_to_name : Dict[Tuple[str, str], str] = dict()
        self._ipif_to_device_endpoint : Dict[IPv4Interface, Tuple[str, str]] = dict()
        self._device_endpoint_to_ipif : Dict[Tuple[str, str], IPv4Interface] = dict()

    def get_device_uuid(self, device_id : str, raise_if_not_exists : bool = True) -> Optional[str]:
        if raise_if_not_exists:
            return self._device_id_to_uuid[device_id]
        else:
            return self._device_id_to_uuid.get(device_id)

    def get_device_name(self, device_id : str, raise_if_not_exists : bool = True) -> Optional[str]:
        if raise_if_not_exists:
            return self._device_id_to_name[device_id]
        else:
            return self._device_id_to_name.get(device_id)

    def get_endpoint_uuid(
        self, device_id : str, endpoint_id : str, raise_if_not_exists : bool = True
    ) -> Optional[str]:
        if raise_if_not_exists:
            return self._endpoint_id_to_uuid[(device_id, endpoint_id)]
        else:
            return self._endpoint_id_to_uuid.get((device_id, endpoint_id))

    def get_endpoint_name(
        self, device_id : str, endpoint_id : str, raise_if_not_exists : bool = True
    ) -> Optional[str]:
        if raise_if_not_exists:
            return self._endpoint_id_to_name[(device_id, endpoint_id)]
        else:
            return self._endpoint_id_to_name.get((device_id, endpoint_id))

    def get_device_endpoint_from_ip_addr(self, ip_address : IPv4Address) -> Optional[Tuple[str, str]]:
        with self._lock:
            for ipif,device_endpoint_uuid in self._ipif_to_device_endpoint.items():
                if ipif.ip == ip_address:
                    return device_endpoint_uuid
            return self._ipif_to_device_endpoint.get(IPv4Interface('0.0.0.0/0'))

    def get_target_firewalls(
        self, src_device_ids : Set[str], dst_device_ids : Set[str], involved_device_ids : Set[str] = set()
    ) -> Dict:
        src_device_uuids = {
            self._device_id_to_uuid[d_id]
            for d_id in src_device_ids
        }

        dst_device_uuids = {
            self._device_id_to_uuid[d_id]
            for d_id in dst_device_ids
        }

        involved_device_uuids = {
            self._device_id_to_uuid[d_id]
            for d_id in involved_device_ids
        }

        WEIGHT = 'weight'

        if len(dst_device_uuids) != 1:
            MSG = 'Unsupported number of destinations: {:s}'
            raise Exception(MSG.format(str(dst_device_uuids)))
        dst_device_uuid = copy.deepcopy(dst_device_uuids).pop()
        
        # Compose set of devices required (sources U {destination} U involved)
        required_device_uuids : Set[str] = set()
        required_device_uuids.update(src_device_uuids)
        required_device_uuids.add(dst_device_uuid)
        required_device_uuids.update(involved_device_uuids)

        MSG = '[get_target_firewalls] required_device_uuids={:s}'
        LOGGER.info(MSG.format(str(required_device_uuids)))

        # Build a Steiner tree over required devices
        stree = steiner_tree(self._network, required_device_uuids, weight=WEIGHT)
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
                endpoints : Dict = edge_data.get('endpoints', dict())
                firewall_endpoint_uuid = endpoints.get(device_uuid, None)
                break

            target_firewalls[src_device_uuid] = {
                'firewall_device_uuid': firewall_device_uuid,
                'firewall_endpoint_uuid': firewall_endpoint_uuid,
                'path_src_to_dst': path_src_to_dst,
            }

        return target_firewalls

    def refresh(self) -> bool:
        with self._lock:
            succeeded = self._load_unsafe()
            return succeeded

    def _load_unsafe(self) -> bool:
        self._network.clear()
        self._ipif_to_device_endpoint.clear()
        self._device_endpoint_to_ipif.clear()
        self._device_id_to_uuid.clear()
        self._device_id_to_name.clear()
        self._endpoint_id_to_uuid.clear()
        self._endpoint_id_to_name.clear()

        json_devices = self._tfs_api_client.get_devices()
        json_links   = self._tfs_api_client.get_links()

        if json_devices is None:
            LOGGER.warning('Devices is None')
            return False

        if not isinstance(json_devices, dict):
            LOGGER.warning('devices is not a Dict')
            return False

        if json_links is None:
            LOGGER.warning('Links is None')
            return False

        if not isinstance(json_links, dict):
            LOGGER.warning('Links is not a Dict')
            return False

        devices : List[Dict] = json_devices.get('devices', [])
        if len(devices) == 0:
            LOGGER.warning('Devices are empty')
            return False

        links : List[Dict] = json_links.get('links', [])
        if len(links) == 0:
            LOGGER.warning('Links are empty')
            return False

        # Build nodes with their endpoints and record IP/interface mappings.
        for device in devices:
            device_uuid = device['device_id']['device_uuid']['uuid']
            device_name = device.get('name', device_uuid)
            if len(device_name) == 0: device_name = device_uuid

            for device_key in {device_uuid, device_name}:
                self._device_id_to_uuid[device_key] = device_uuid
                self._device_id_to_name[device_key] = device_name

            endpoints : Set[str] = set()

            device_endpoints = device.get('device_endpoints', [])
            for device_endpoint in device_endpoints:
                endpoint_uuid = device_endpoint['endpoint_id']['endpoint_uuid']['uuid']
                endpoint_name = device_endpoint['name']
                if len(endpoint_name) == 0: endpoint_name = endpoint_uuid

                for device_key in [device_uuid, device_name]:
                    for endpoint_key in [endpoint_uuid, endpoint_name]:
                        self._endpoint_id_to_uuid[(device_key, endpoint_key)] = endpoint_uuid
                        self._endpoint_id_to_name[(device_key, endpoint_key)] = endpoint_name

                endpoints.add(endpoint_uuid)

            config_rules = device.get('device_config', {}).get('config_rules', [])
            for rule in config_rules:
                custom = rule.get('custom')
                if custom is None: continue

                resource_key : str = custom['resource_key']
                if resource_key in {'_connect/address', '_connect/port'}: continue

                resource_value : Union[str, Dict] = custom['resource_value']
                if isinstance(resource_value, str):
                    try:
                        resource_value = json.loads(resource_value)
                    except Exception:
                        pass

                if resource_key == '_connect/settings':
                    connect_settings_endpoints : List[Dict] = resource_value.get('endpoints', [])
                    for endpoint in connect_settings_endpoints:
                        endpoint_uuid = endpoint.get('uuid')
                        if endpoint_uuid is None: continue

                        endpoint_name = endpoint.get('name', endpoint_uuid)
                        if len(endpoint_name) == 0: endpoint_name = endpoint_uuid

                        for device_key in [device_uuid, device_name]:
                            for endpoint_key in [endpoint_uuid, endpoint_name]:
                                self._endpoint_id_to_uuid[(device_key, endpoint_key)] = endpoint_uuid
                                self._endpoint_id_to_name[(device_key, endpoint_key)] = endpoint_name

                        endpoints.add(endpoint_uuid)

                elif resource_key.startswith('/interface[') and resource_key.endswith(']/subinterface[0]'):
                    endpoint_id = resource_key[len('/interface['):-len(']/subinterface[0]')]
                    if len(endpoint_id) == 0: continue
                    endpoint_uuid = self._endpoint_id_to_uuid.get((device_uuid, endpoint_id))
                    if endpoint_uuid is None: continue
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
            firewall_drivers = {
                #'DEVICEDRIVER_UNDEFINED',
                'DEVICEDRIVER_GNMI_OPENCONFIG'
            }

            is_firewall = (
                ('firewall' in device_type or 'packet-router' in device_type)
                and
                (len(set(device_drivers).intersection(firewall_drivers)) > 0)
                and
                str(device_name).endswith('_ACL')
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
                device_id = endpoint_id['device_id']['device_uuid']['uuid']
                device_uuid = self._device_id_to_uuid[device_id]

                endpoint_id = endpoint_id['endpoint_uuid']['uuid']
                endpoint_uuid = self._endpoint_id_to_uuid[(device_uuid, endpoint_id)]

                if device_uuid not in self._network: continue
                device_uuids.append(device_uuid)
                link_endpoints[device_uuid] = endpoint_uuid

            if len(device_uuids) != 2: raise Exception('Malformed Link: {:s}'.format(str(link)))
            if len(link_endpoints) != 2: raise Exception('Malformed Link: {:s}'.format(str(link)))

            device_a, device_b = device_uuids[0], device_uuids[-1]
            if self._network.has_edge(device_a, device_b): continue # skip bidirectional links

            self._network.add_edge(device_a, device_b, endpoints=link_endpoints)

        return True
