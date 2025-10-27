from uuid import uuid4

import pydantic
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class WIMServiceInfoBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    type: str = ''
    status: str = ''
    nsf_id: str | None = Field(foreign_key='nsf.id', default=None)
    nsi_id: str | None = Field(foreign_key='nsi.id', default=None)
    estsla_dict: dict = Field(sa_column=Column(JSON), default_factory=dict)
    path: list[str] = Field(sa_column=Column(JSON), default_factory=list)


class WIMServiceInfo(WIMServiceInfoBase, table=True): ...


class WIMServiceInfoGet(WIMServiceInfoBase): ...


class WIMServiceInfoCreate(WIMServiceInfoBase): ...


class IETFNetworkCreate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    ietf_network: dict = pydantic.Field(alias='ietf-network:networks')


class IETFNetwork(SQLModel, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    ietf_network: dict = Field(sa_column=Column(JSON))

    @classmethod
    def model_validate(cls, obj) -> 'IETFNetwork':
        return cls(ietf_network=obj.ietf_network)


class IETFNetworkGet(IETFNetworkCreate):
    @classmethod
    def from_IETFNetwork(cls, ietf_network: IETFNetwork) -> 'IETFNetworkGet':
        return cls(ietf_network=ietf_network.ietf_network)
