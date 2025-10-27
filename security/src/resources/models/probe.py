from uuid import uuid4

from sqlmodel import Field, SQLModel


class ProbeBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    ip: str = ''
    port: int = 0
    username: str = ''
    password: str = ''


class ProbeCreate(ProbeBase): ...


class Probe(ProbeBase, table=True): ...


class ProbeGet(ProbeBase): ...
