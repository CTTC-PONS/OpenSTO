import logging, json, requests
from typing import Any, Dict, Optional
from .AclComposer import ACLRuleSet, get_ietf_acl


TFS_API_ADDRESS  = None #'127.0.0.1'
TFS_API_PORT     = 80
TFS_API_BASE_URL = f'http://{TFS_API_ADDRESS}:{TFS_API_PORT}'

TFS_API_TOPO_URL     = TFS_API_BASE_URL + '/tfs-api/context/admin/topology_details/admin'
TFS_API_ACL_ROOT_URL = TFS_API_BASE_URL + '/restconf/data/device={}/ietf-access-control-list:acls'
TFS_API_ACL_ITEM_URL = TFS_API_BASE_URL + '/restconf/data/device={}/ietf-access-control-list:acl={}'

TFS_API_TIMEOUT  = 30


LOGGER = logging.getLogger(__name__)


class TfsApiClient:
    def __init__(self):
        pass

    def get_topology(self) -> Optional[Dict]:
        if TFS_API_ADDRESS is None:
            with open('/app/attack_mitigator/topology.json', 'r', encoding='UTF-8') as fp:
                return json.load(fp)

        try:
            response = requests.get(TFS_API_TOPO_URL, timeout=TFS_API_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            LOGGER.exception('Unhandled Exception')
            return None

    def configure_acl_rules(self, target_device_uuid : str, acl_rule_set : ACLRuleSet) -> Any:
        request_url = TFS_API_ACL_ROOT_URL.format(target_device_uuid)
        LOGGER.info('[configure_acl_rules] request_url={:s}'.format(str(request_url)))
        ietf_acl_data = get_ietf_acl(acl_rule_set)
        LOGGER.info('[configure_acl_rules] ietf_acl_data={:s}'.format(str(ietf_acl_data)))
        if TFS_API_ADDRESS is None: return None
        response = requests.post(request_url, json=ietf_acl_data, timeout=TFS_API_TIMEOUT)
        LOGGER.info('[configure_acl_rules] response.status_code={:s}'.format(str(response.status_code)))
        LOGGER.info('[configure_acl_rules] response.content={:s}'.format(str(response.content.decode('UTF-8'))))
        response.raise_for_status()
        return response.json()

    def deconfigure_acl_rules(self, target_device_uuid : str, acl_name : str) -> Any:
        request_url = TFS_API_ACL_ITEM_URL.format(target_device_uuid, acl_name)
        LOGGER.info('[deconfigure_acl_rules] request_url={:s}'.format(str(request_url)))
        if TFS_API_ADDRESS is None: return None
        response = requests.delete(request_url, timeout=TFS_API_TIMEOUT)
        LOGGER.info('[deconfigure_acl_rules] response.status_code={:s}'.format(str(response.status_code)))
        LOGGER.info('[deconfigure_acl_rules] response.content={:s}'.format(str(response.content.decode('UTF-8'))))
        response.raise_for_status()
        return response.json()

    def retrieve_acl_rules(self, target_device_uuid : str, acl_name : str) -> Any:
        request_url = TFS_API_ACL_ITEM_URL.format(target_device_uuid, acl_name)
        LOGGER.info('[retrieve_acl_rules] request_url={:s}'.format(str(request_url)))
        if TFS_API_ADDRESS is None: return None
        response = requests.get(request_url, timeout=TFS_API_TIMEOUT)
        LOGGER.info('[retrieve_acl_rules] response.status_code={:s}'.format(str(response.status_code)))
        LOGGER.info('[retrieve_acl_rules] response.content={:s}'.format(str(response.content.decode('UTF-8'))))
        response.raise_for_status()
        return response.json()
