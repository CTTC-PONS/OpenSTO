from uuid import uuid4

import sqlmodel
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import JSON, Column


class NSF(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nsf_name: str = Field(alias='nsf-name', default='')
    version: str = ''
    condition_capabilities: dict = Field(alias='condition-capabilities', default_factory=dict)
    action_capabilities: dict = Field(alias='action-capabilities', default_factory=dict)
    nsf_specification: dict = Field(alias='nsf-specification', default_factory=dict)
    nsf_access_info: dict = Field(alias='nsf-access-info', default_factory=dict)


class CapabilityCreate(BaseModel):  # same as capability registration interface
    nsf: NSF


class Capability(sqlmodel.SQLModel, table=True):
    id: str = sqlmodel.Field(primary_key=True, default_factory=lambda: str(uuid4()))
    nsf_name: str = sqlmodel.Field(default='')
    version: str = ''
    condition_capabilities: dict = sqlmodel.Field(sa_column=Column(JSON), default_factory=dict)
    action_capabilities: dict = sqlmodel.Field(sa_column=Column(JSON), default_factory=dict)
    nsf_specification: dict = sqlmodel.Field(sa_column=Column(JSON), default_factory=dict)
    nsf_access_info: dict = sqlmodel.Field(sa_column=Column(JSON), default_factory=dict)


class CapabilityGet(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    nsf: NSF

    @classmethod
    def from_table(cls, capability: Capability) -> 'CapabilityGet':
        return cls(
            id=capability.id,
            nsf=NSF(
                nsf_name=capability.nsf_name,
                version=capability.version,
                condition_capabilities=capability.condition_capabilities,
                action_capabilities=capability.action_capabilities,
                nsf_specification=capability.nsf_specification,
                nsf_access_info=capability.nsf_access_info,
            ),
        )
