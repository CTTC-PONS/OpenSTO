from enum import Enum
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel


class NodeType(str, Enum):
    DOMAIN = 'domain'
    PROVIDER = 'provider'
    ROUTER = 'router'
    DATACENTER = 'datacenter'


class DomainType(str, Enum):
    EDGE = 'edge'
    TRANSPORT = 'transport'
    CLOUD = 'cloud'
    EDGE_IP = 'edgeip'
    CLOUD_IP = 'cloudip'
    OPTICAL = 'optical'


class EndpointBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    ip: str = ''
    type: str = ''
    name: str = ''
    inter_domain_cross_connect: str = ''


class Endpoint(EndpointBase, table=True):
    topology_id: str = Field(foreign_key='topology.id')
    node_id: str | None = Field(foreign_key='node.id', default=None)
    link_id: str | None = Field(foreign_key='link.id', default=None)
    link: 'Link' = Relationship(back_populates='endpoints')
    node: 'Node' = Relationship(back_populates='endpoints')


class EndpointGet(EndpointBase):

    @classmethod
    def from_table(cls, table_data: Endpoint) -> 'EndpointGet':
        return cls(**table_data.model_dump())


class NodeBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    name: str = ''
    domain: str
    type: NodeType
    ip: str
    port: int
    username: str
    password: str


class Node(NodeBase, table=True):
    endpoints: list[Endpoint] = Relationship(back_populates='node')
    topology_id: str = Field(foreign_key='topology.id')


class NodeGet(NodeBase):
    endpoint_ids: list[str]

    @classmethod
    def from_table(cls, table_data: Node) -> 'NodeGet':
        endpoint_ids = [v.id for v in table_data.endpoints]
        return cls(**{**table_data.model_dump(), **{'endpoint_ids': endpoint_ids}})


class LinkBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    domain: str = ''
    inter_domain_cross_connect: str = ''


class Link(LinkBase, table=True):
    endpoints: list[Endpoint] = Relationship(back_populates='link')
    topology_id: str = Field(foreign_key='topology.id')


class LinkGet(LinkBase):
    endpoint_ids: list[str]

    @classmethod
    def from_table(cls, table_data: Link) -> 'LinkGet':
        endpoint_ids = [v.id for v in table_data.endpoints]
        return cls(**{**table_data.model_dump(), **{'endpoint_ids': endpoint_ids}})


class TopologyBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))


class Topology(TopologyBase, table=True):
    endpoints: list[Endpoint] = Relationship()
    nodes: list[Node] = Relationship()
    links: list[Link] = Relationship()


class TopologyGet(TopologyBase):
    endpoints: list[EndpointGet]
    nodes: list[NodeGet]
    links: list[LinkGet]

    @classmethod
    def from_table(cls, table_data: Topology) -> 'TopologyGet':
        endpoints = [EndpointGet.from_table(v) for v in table_data.endpoints]
        nodes = [NodeGet.from_table(v) for v in table_data.nodes]
        links = [LinkGet.from_table(v) for v in table_data.links]
        return cls(**{**table_data.model_dump(), **{'nodes': nodes, 'links': links, 'endpoints': endpoints}})

    def model_dump(self, *args, **kwargs):
        model_dumped = super().model_dump(*args, **kwargs)
        for k, v in model_dumped.items():
            if SQLModel in v.__class__.__mro__:
                model_dumped[k] = v.model_dump()
        return model_dumped


class TopologyCreate(SQLModel):
    topologies: list
    devices: list
    links: list

class TopologyE2ECreate(SQLModel):
    nodes: list
    endpoints: list
    links: list