from enum import Enum
from uuid import uuid4

from sqlmodel import Field, SQLModel


class FirewallType(str, Enum):
    TFS = 'tfs'
    NONE = 'none'


class FirewallBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    ip: str = ''
    port: int = 0
    type: FirewallType = FirewallType.TFS
    username: str = ''
    password: str = ''


class FirewallCreate(FirewallBase): ...


class Firewall(FirewallBase, table=True): ...


class FirewallGet(FirewallBase): ...
