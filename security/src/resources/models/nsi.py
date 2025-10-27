from uuid import uuid4

import pydantic
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from src.resources.models.nst import NSTGet
from src.resources.models.vertical_ns import NSInfo


class NSIBase(SQLModel):
    id: str = Field(primary_key=True)
    name: str
    nst_ref: str = Field(alias='nst-ref', foreign_key='nst.id')
    e2essla_ref: str = Field(alias='e2essla-ref')
    e2etsla_ref: str = Field(alias='e2etsla-ref')
    ns_list: list = Field(alias='ns-list', sa_column=Column(JSON))
    cs_list: list = Field(alias='cs-list', sa_column=Column(JSON))


class NSI(NSIBase, table=True):
    active: bool = True
    nss: list[NSInfo] = Relationship()


class NSICreate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    id: str
    name: str
    nst_ref: str = pydantic.Field(alias='nst-ref')
    e2essla_ref: str = pydantic.Field(alias='e2essla-ref')
    e2etsla_ref: str = pydantic.Field(alias='e2etsla-ref')
    ns_list: list = pydantic.Field(alias='ns-list')
    cs_list: list = pydantic.Field(alias='cs-list')
    active: bool = True

    @classmethod
    def from_nst_get(cls, nst: NSTGet) -> 'NSICreate':
        ns_list = [
            {
                'nsd-ref': ns['nsd-ref'],
                'nsr-id': '',
                'nfvo-ref': ns['nfvo-ref'],
                'status': '',
                'ssla': {'id': '', 'provider-id': ''},
                'tla-ref': {'id': '', 'provider-id': ''},
            }
            for ns in nst.ns_list
        ]
        cs_list = [
            {
                'source': cs['source'],
                'destination': cs['destination'],
                'domain': cs['domain'],
                'ssla': {'id': '', 'provider-id': ''},
                'tla-ref': {'id': '', 'provider-id': ''},
            }
            for cs in nst.cs_list
        ]
        return cls(
            id=str(uuid4()),
            name=f'{nst.name}_instance',
            nst_ref=nst.id,
            e2essla_ref=nst.e2essla_ref,
            e2etsla_ref=nst.e2etsla_ref,
            ns_list=ns_list,
            cs_list=cs_list,
        )


class NSIGet(NSICreate):
    @classmethod
    def from_NSI(cls, nsi: NSI) -> 'NSIGet':
        return NSIGet(**nsi.model_dump())


class NSIUpdate(SQLModel):
    nsi_id: str
    ns_list: list[str]
    policy_id: str


class KEY(SQLModel):
    key: str
