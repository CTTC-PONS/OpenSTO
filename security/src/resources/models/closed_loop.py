from enum import Enum
from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from src.resources.models.firewall import FirewallType


class ClosedLoopType(str, Enum):
    E2E = 'e2e'
    DOMAIN = 'domain'


class ClosedLoopInitializationRequestBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    nsi_id: str | None = None
    nsr_id: str = ''
    ns_ip: str = ''
    ns_port: int = -1
    cs_id: str = ''
    cs_source_port: str = ''
    cs_destination_port: str = ''
    cs_source_ip: str = ''
    cs_destination_ip: str = ''
    nsf_id: str = ''
    domain: str = ''
    provider: str = ''
    probe_ip: str = ''
    probe_port: int = -1
    probe_username: str = ''
    probe_password: str = ''
    ssla_id: str = ''
    tsla_id: str = ''
    firewall_type: FirewallType = FirewallType.TFS
    firewall_ip: str = ''
    firewall_port: int = -1
    firewall_username: str = ''
    firewall_password: str = ''
    closed_loop_type: ClosedLoopType  = ClosedLoopType.DOMAIN
    security_sls: dict = Field(sa_column=Column(JSON), default_factory=dict)
    trust_sls: dict = Field(sa_column=Column(JSON), default_factory=dict)
    xslap: dict = Field(sa_column=Column(JSON), default_factory=dict)
    e2e_cl_id: str = ''
    nsd_id: str = ''
    configurations: dict = Field(sa_column=Column(JSON), default_factory=dict)


class ClosedLoopInitializationRequest(ClosedLoopInitializationRequestBase, table=True):
    active: bool = False


class ClosedLoopInitializationRequestCreate(ClosedLoopInitializationRequestBase): ...


class ClosedLoopInitializationRequestGet(ClosedLoopInitializationRequestBase): ...


class E2EClosedLoopInitializationRequest(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    closed_loop_requests: list[ClosedLoopInitializationRequestCreate]


class Metrics(SQLModel):
    provider: str
    closed_loop_id: str
    cl_status: bool


class DomainClosedLoopAction(SQLModel):
    nsd_id: str
    ssla_id: str
    tsla_id: str
