from sqlmodel import Session, select

from src.exceptions import InvalidTopologyError, NodeNotFoundError, TopologyNotFoundError
from src.resources.crud.provider import get_domain_name_from_nfvo_ref
from src.resources.models.topology import (
    DomainType,
    Endpoint,
    Link,
    Node,
    NodeType,
    Topology,
    TopologyCreate,
    TopologyE2ECreate,
    TopologyGet,
)


def create_topology_e2e(topology_create: TopologyE2ECreate, session: Session):
    topology = Topology()
    session.add(topology)
    nodes = {}
    for node in topology_create.nodes:
        node = Node(
            domain=node['domain'],
            name=node['name'],
            ip='',
            port=0,
            username='',
            password='',
            topology_id=topology.id,
            type=NodeType.PROVIDER,
        )
        session.add(node)
        nodes[node.name] = node.id

    endpoints = {}
    for ep in topology_create.endpoints:
        ep_obj = Endpoint(
            name=ep['name'],
            ip=ep['ip'],
            inter_domain_cross_connect=ep['interdomain_cross_connect'],
            node_id=nodes[ep['node']],
            topology_id=topology.id,
        )
        session.add(ep_obj)
        endpoints[(ep['node'], ep['name'])] = ep_obj
    for link in topology_create.links:
        link_obj = Link(
            inter_domain_cross_connect=endpoints[
                (link['endpoints'][0]['node'], link['endpoints'][0]['endpoint'])
            ].inter_domain_cross_connect,
            topology_id=topology.id,
        )
        session.add(link_obj)
        ep_1 = endpoints[(link['endpoints'][0]['node'], link['endpoints'][0]['endpoint'])]
        ep_2 = endpoints[(link['endpoints'][1]['node'], link['endpoints'][1]['endpoint'])]
        ep_1.link_id = link_obj.id
        ep_2.link_id = link_obj.id
        session.add(ep_1)
        session.add(ep_2)

    session.commit()
    session.refresh(topology)
    return TopologyGet.from_table(topology)


def create_topology(topology_create: TopologyCreate, session: Session):
    topology = Topology(id=topology_create.topologies[0]['topology_id']['topology_uuid']['uuid'])
    for node in topology_create.devices:
        device_id = node['device_id']['device_uuid']['uuid']
        device_type = node['device_type']
        device_config_rules = node['device_config']['config_rules']
        username = ''
        password = ''
        for cr in device_config_rules:
            if 'custom' not in cr:
                continue
            custom_cr_k = cr['custom']['resource_key']
            custom_cr_v = cr['custom']['resource_value']
            if custom_cr_k == '_connect/address':
                ip = custom_cr_v
            elif custom_cr_k == '_connect/port':
                port = int(custom_cr_v)
            elif custom_cr_k == '_connect/settings' and device_type == 'packet-router':
                username = custom_cr_v['username']
                password = custom_cr_v['password']
        if not any([ip, port, username, password]):
            raise InvalidTopologyError
        if device_type == 'packet-router':
            node = Node(
                id=device_id,
                domain=DomainType.TRANSPORT,
                ip=ip,
                port=port,
                username=username,
                password=password,
                topology_id=topology.id,
                type=NodeType.ROUTER,
            )
            session.add(node)
        elif device_type in ['datacenter', 'emu-datacenter']:
            node = Node(
                id=device_id,
                domain=get_domain_name_from_nfvo_ref(device_id),
                ip=ip,
                port=port,
                username=username,
                password=password,
                topology_id=topology.id,
                type=NodeType.DATACENTER,
            )
            session.add(node)

    included_links = set()
    for link in topology_create.links:
        link_id = link['link_id']['link_uuid']['uuid']
        device_id_1 = link['link_endpoint_ids'][0]['device_id']['device_uuid']['uuid']
        device_id_2 = link['link_endpoint_ids'][1]['device_id']['device_uuid']['uuid']
        if (device_id_1, device_id_2) in included_links:
            continue

        ep_id_1 = link['link_endpoint_ids'][0]['endpoint_uuid']['uuid']
        ep_id_2 = link['link_endpoint_ids'][1]['endpoint_uuid']['uuid']
        session.add(Link(id=link_id, topology_id=topology.id))
        session.add(
            Endpoint(name=ep_id_1, node_id=device_id_1, link_id=link_id, topology_id=topology.id)
        )
        session.add(
            Endpoint(name=ep_id_2, node_id=device_id_2, link_id=link_id, topology_id=topology.id)
        )

        included_links.update({(device_id_1, device_id_2), (device_id_2, device_id_1)})

    session.add(topology)
    session.commit()
    session.refresh(topology)
    return TopologyGet.from_table(topology)


def get_node_by_name(name: str, session: Session) -> Node:
    statement = select(Node).where(Node.name == name)
    node = session.exec(statement).first()
    if not node:
        raise NodeNotFoundError
    return node


def get_topology(session: Session) -> Topology:
    statement = select(Topology)
    topology = session.exec(statement).first()
    if not topology:
        raise TopologyNotFoundError
    return topology


def get_topology_api(session: Session) -> TopologyGet:
    return TopologyGet.from_table(get_topology(session))
