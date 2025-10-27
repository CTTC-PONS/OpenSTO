from enum import Enum
from uuid import uuid4

from sqlmodel import Field, SQLModel


class NSFInstanceType(str, Enum):
    TFS_FIREWALL = 'tfs_firewall'
    NONE = 'none'


class NSFInstanceBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    ip: str = ''
    port: int = 0
    type: NSFInstanceType = NSFInstanceType.TFS_FIREWALL
    username: str = ''
    password: str = ''


class NSFInstanceCreate(NSFInstanceBase): ...


class NSFInstance(NSFInstanceBase, table=True): ...


class NSFInstanceGet(NSFInstanceBase): ...
