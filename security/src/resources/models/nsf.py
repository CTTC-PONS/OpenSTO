from uuid import uuid4

import pydantic
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel
from typing_extensions import TypedDict

from src.resources.models.closed_loop import ClosedLoopInitializationRequest
from src.resources.models.ssla.ssla import DSTSLA, ESTSLA


class DeviceEndpoint(TypedDict):
    device_id: str
    endpoint_uuid: str
    ip: str


class NSDBase(pydantic.BaseModel):
    nsd: dict


class NSDCreate(NSDBase): ...


class NSDGet(NSDBase):
    @classmethod
    def model_validate(cls, obj) -> 'NSDGet':
        return cls(nsd=obj.nsd)


class NSD(SQLModel, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    nsd: dict = Field(sa_column=Column(JSON))


class NSFBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    ssla_id: str = ''
    tsla_id: str = ''
    vertical_service_nsr_id: str = ''
    vertical_service_floating_ip: str = ''
    status: str = ''
    trust_controller_id: str
    closed_loop_id: str | None = Field(foreign_key='closedloopinitializationrequest.id')


class NSFCreate(NSFBase): ...


class NSFGet(NSFBase): ...


class NSF(NSFBase, table=True):
    closed_loop: ClosedLoopInitializationRequest = Relationship()


class ServiceCreateAPI(SQLModel):
    nsd_id: str
    nsi_id: str | None = None
    ssla_id: str
    tsla_id: str
    provider: str
    domain: str
    source: DeviceEndpoint | None = None
    destination: DeviceEndpoint | None = None
    xsla_aio: ESTSLA | DSTSLA


class NSFReplaceRequest(ServiceCreateAPI):
    nsso_ip: str
    nsso_port: int
    nsf_id: str


class NSFTerminationRequest(SQLModel):
    nsf_id: str
    nsso_ip: str
    nsso_port: int


class NSUpdate(SQLModel):
    ns_id: str
    ssla_id: str = ''
    tsla_id: str = ''
    policy_id: str = ''
