from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from src.resources.models.ssla.policy import DomainPolicyBase

from .sls import SLS


class XSLABase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    href: str = ''
    name: str = ''


class DXSLAAIO(XSLABase):
    sls: SLS
    policies: list[dict] | list[DomainPolicyBase]


class ESSLAAIOBase(XSLABase):
    sls: dict = Field(sa_column=Column(JSON))
    policies: list = Field(sa_column=Column(JSON))


class ESSLAAIOCreate(ESSLAAIOBase): ...


class ESSLAAIOGet(ESSLAAIOBase): ...


class ESSLAAIO(ESSLAAIOBase, table=True): ...


class EXSLAAIOBase(XSLABase):
    sls: SLS
    policies: list[dict]
    capabilities: list[dict]


class ESTSLA(SQLModel):
    ssla: EXSLAAIOBase
    tsla: EXSLAAIOBase


class DSTSLA(SQLModel):
    ssla: DXSLAAIO
    tsla: DXSLAAIO
