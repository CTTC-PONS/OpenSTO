from uuid import uuid4

from sqlmodel import Field, SQLModel


class ProviderBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    name: str
    domain_opensto_ip: str
    domain_opensto_port: int


class ProviderCreate(ProviderBase): ...


class ProviderGet(ProviderBase):
    domain: str


class Provider(ProviderBase, table=True):
    domain: str


class NewProviderSelection(SQLModel):
    cl_id: str
    nsd_id: str
    domain: str
    failed_provider: str
    ssla_id: str
    tsla_id: str


class NewProviderSelectionRequestFromXSLAP(SQLModel):
    nsd_id: str
    domain: str
    failed_provider: str
    ssla_id: str
    tsla_id: str
