import pydantic
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class NSTBase(SQLModel):
    id: str = Field(primary_key=True)
    name: str
    description: str
    e2essla_ref: str = Field(alias='e2essla-ref')
    e2etsla_ref: str = Field(alias='e2etsla-ref')
    ns_list: list = Field(alias='ns-list', sa_column=Column(JSON))
    cs_list: list = Field(alias='cs-list', sa_column=Column(JSON))


class NST(NSTBase, table=True): ...


class NSTCreate(pydantic.BaseModel):

    model_config = pydantic.ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: str
    e2essla_ref: str = pydantic.Field(alias='e2essla-ref')
    e2etsla_ref: str = pydantic.Field(alias='e2etsla-ref')
    ns_list: list[dict] = pydantic.Field(alias='ns-list')
    cs_list: list[dict] = pydantic.Field(alias='cs-list')


class NSTGet(NSTCreate):
    @classmethod
    def from_NST(cls, nst: NST) -> 'NSTGet':
        return NSTGet(**nst.model_dump())
