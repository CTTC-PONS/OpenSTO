from enum import Enum
from uuid import uuid4

from sqlmodel import Field, SQLModel


class ControllerType(str, Enum):
    OSM = 'osm'
    TFS = 'tfs'
    OPENSLICE = 'openslice'


class ControllerBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    controller_type: ControllerType
    ip: str
    port: int
    username: str
    password: str


class ControllerCreate(ControllerBase): ...


class ControllerGet(ControllerBase): ...


class Controller(ControllerBase, table=True): ...
