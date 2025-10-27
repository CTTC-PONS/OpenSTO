from copy import deepcopy
from enum import Enum
from itertools import pairwise
from typing import TypedDict

import networkx as nx
from sqlmodel import Session

from src.control.controller import MirroringRequest
from src.exceptions import (
    DatacenterNotFound,
    DC2RouterMultiplePathsError,
    GatewayNotFoundError,
    MonitoringPortsNotFound,
)
from src.manager import get_transport_domains_list
from src.resources.crud.topology import get_node_by_name, get_topology
from src.resources.models.topology import NodeType


class DomainCSDict(TypedDict):
    domain: str
    source: str
    destination: str
    ssla_provider: dict
    tsla_provider: dict


class GraphNodeType(str, Enum):
    NODE = 'node'
    ENDPOINT = 'endpoint'


class GraphEdgeType(str, Enum):
    INTRA_NODE = 'intra_node'
    INTER_NODE = 'inter_node'


class EndpointType(str, Enum):
    GATEWAY = 'gateway'
    MONITORING = 'monitoring'


class TopologyManager:
    @staticmethod
    def __topology(session: Session) -> nx.Graph:
        graph = nx.Graph()
        topology = get_topology(session)
        for ep in topology.endpoints:
            node = ep.node
            ep_info = {'ip': ep.ip, 'type': ep.type, 'name': ep.name, 'node_id': node.id}
            graph.add_node(
                ep.id,
                name=ep.name,
                node_domain=node.domain,
                node_type=GraphNodeType.ENDPOINT,
                interdomain_cross_connect=ep.inter_domain_cross_connect,
                node_info=ep_info,
            )
            ep_node_info = {'type': node.type}
            if node.id not in graph:
                graph.add_node(
                    node.id,
                    name=node.name,
                    node_domain=node.domain,
                    node_type=GraphNodeType.NODE,
                    node_info=ep_node_info,
                )
            graph.add_edge(ep.id, node.id, edge_type=GraphEdgeType.INTRA_NODE, edge_info={})
        for link in topology.links:
            link_endpoints = link.endpoints
            graph.add_edge(
                link_endpoints[0].id,
                link_endpoints[1].id,
                edge_type=GraphEdgeType.INTER_NODE,
                edge_info={},
            )
        return graph

    @staticmethod
    def calculate_path(
        provider: str,
        domain: str,
        source_provider: str,
        destination_provider: str,
        session: Session,
    ) -> list[str]:
        graph = TopologyManager.__topology(session)
        nodes = list(graph.nodes)
        for n in nodes:
            node = graph.nodes[n]
            if (
                node['name'] != provider
                and node['node_domain'] == domain
                and node['node_type'] == GraphNodeType.NODE
            ):
                graph.remove_node(n)
        source_node = get_node_by_name(source_provider, session)
        destination_node = get_node_by_name(destination_provider, session)
        path_nodes = list(nx.all_shortest_paths(graph, source_node.id, destination_node.id))[0]
        return [graph.nodes[n]['name'] for n in path_nodes]

    @staticmethod
    def break_e2e_cs_into_domain_cs_list(e2e_cs: dict, session: Session) -> list[DomainCSDict]:
        domains = get_transport_domains_list()
        graph = TopologyManager.__topology(session)
        source = e2e_cs['service_endpoint_ids'][0]['device_id']
        destination = e2e_cs['service_endpoint_ids'][1]['device_id']
        source_node = get_node_by_name(source, session)
        destination_node = get_node_by_name(destination, session)
        path_nodes = list(nx.all_shortest_paths(graph, source_node.id, destination_node.id))[0]
        cross_connects = list(
            pairwise(
                (
                    graph.nodes[n]['interdomain_cross_connect']
                    for n in path_nodes
                    if graph.nodes[n]['node_type'] == GraphNodeType.ENDPOINT
                )
            )
        )
        domains = [
            graph.nodes[n]['node_domain']
            for n in path_nodes
            if graph.nodes[n]['node_type'] == GraphNodeType.NODE
        ]
        return [
            DomainCSDict(
                domain=d,
                source=sd[0],
                destination=sd[1],
                ssla_provider={'ssla': {'provider-id': ''}},
                tsla_provider={'tla-ref': {'provider-id': ''}},
            )
            for d, sd in zip(domains[1:-1], cross_connects[1:-1])
        ]

    @staticmethod
    def get_dc2gateway_path_nodes(dc_id: str, router_id: str, session: Session) -> list[str]:
        topology = TopologyManager.__topology(session)

        #! We assume there is only one path between dc_id and router_id
        def _get_gateway_endpoint_id(node_id):
            for i in topology.adj[node_id]:
                node = topology.nodes[i]
                if node['node_info']['type'] == EndpointType.GATEWAY:
                    return i
            raise GatewayNotFoundError

        dc_if_id = _get_gateway_endpoint_id(dc_id)
        router_if_id = _get_gateway_endpoint_id(router_id)
        topology_copy = deepcopy(topology)
        for node_id in topology.nodes:
            node = topology.nodes[node_id]
            if (
                node['node_type'] == GraphNodeType.ENDPOINT
                and node['node_info']['type'] == EndpointType.MONITORING
            ):
                topology_copy.remove_node(node_id)
        path_nodes = list(nx.all_shortest_paths(topology_copy, dc_if_id, router_if_id))
        if len(path_nodes) != 1:
            raise DC2RouterMultiplePathsError
        return path_nodes[0]

    @staticmethod
    def get_mirroring_device_endpoints(session: Session) -> MirroringRequest:
        topology = TopologyManager.__topology(session)
        monitoring_eps = []
        dc_id = ''
        for node_id in topology.nodes:
            node = topology.nodes[node_id]
            if (
                node['node_type'] == GraphNodeType.ENDPOINT
                and node['node_info']['type'] == EndpointType.MONITORING
            ):
                monitoring_eps.append(node)
            if (
                node['node_type'] == GraphNodeType.NODE
                and node['node_info']['type'] == NodeType.DATACENTER
            ):
                dc_id = node_id
        if not dc_id:
            raise DatacenterNotFound
        first_monitoring_ep = monitoring_eps[0]
        second_monitoring_ep = monitoring_eps[1]
        first_device_id = first_monitoring_ep['node_info']['node_id']
        second_device_id = second_monitoring_ep['node_info']['node_id']
        if topology.nodes[first_device_id]['node_info']['type'] == NodeType.ROUTER:
            mirroring_device_id = first_device_id
            mirroring_destination_port = first_monitoring_ep['id']
        elif topology.nodes[second_device_id]['node_info']['type'] == NodeType.ROUTER:
            mirroring_device_id = second_device_id
            mirroring_destination_port = second_monitoring_ep['id']
        else:
            raise MonitoringPortsNotFound

        path = TopologyManager.get_dc2gateway_path_nodes(
            dc_id=dc_id, router_id=mirroring_device_id, session=session
        )
        mirroring_source_port = [
            node_id for node_id in topology.adj[mirroring_device_id] if node_id in path
        ][0]

        return MirroringRequest(
            mirroring_device_id=mirroring_device_id,
            mirroring_source_port=mirroring_source_port,
            mirroring_destination_port=mirroring_destination_port,
        )
