from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from src.resources.models.ssla.ssla import ESSLAAIO


class ServiceInfoBase(SQLModel):
    id: str = Field(primary_key=True)
    domain_name: str


class OpenSTOServiceBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    ssla_id: str = Field(foreign_key='esslaaio.id')


class OpenSTOServiceCreate(OpenSTOServiceBase):
    mano_services_info: list[ServiceInfoBase]
    wim_services_info: list[ServiceInfoBase]


class OpenSTOService(OpenSTOServiceBase, table=True):
    ssla: ESSLAAIO = Relationship()
    mano_services_info: list = Field(sa_column=Column(JSON))
    wim_services_info: list = Field(sa_column=Column(JSON))


class OpenSTOServiceGet(OpenSTOServiceBase):
    mano_services_info: list[ServiceInfoBase]
    wim_services_info: list[ServiceInfoBase]

    @classmethod
    def from_OpenSTOService(cls, open_sto_service: OpenSTOService) -> 'OpenSTOServiceGet':
        mano_services_info = [ServiceInfoBase.model_validate(s) for s in open_sto_service.mano_services_info]
        wim_services_info = [ServiceInfoBase.model_validate(s) for s in open_sto_service.wim_services_info]
        return cls(
            id=open_sto_service.id,
            ssla_id=open_sto_service.ssla_id,
            mano_services_info=mano_services_info,
            wim_services_info=wim_services_info,
        )
