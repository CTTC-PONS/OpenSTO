from uuid import uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from src.resources.models.nsf import NSF, NSFGet


class NFInterfaceBase(SQLModel):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    name: str
    ip: str
    mac: str
    vnf_info_id: str = Field(foreign_key='vnfinfo.id')


class NFInterface(NFInterfaceBase, table=True): ...


class NFInterfaceGet(NFInterfaceBase):
    @classmethod
    def from_table(cls, table_data: NFInterface) -> 'NFInterfaceGet':
        return cls.model_validate(table_data)


class VNFInfoBase(SQLModel):
    id: str = Field(primary_key=True)
    type: str
    floating_ip: str
    ns_info_id: str = Field(foreign_key='nsinfo.id')


class VNFInfo(VNFInfoBase, table=True):
    interfaces: list[NFInterface] = Relationship()


class VNFInfoGet(VNFInfoBase):
    interfaces: list[NFInterfaceBase]

    @classmethod
    def from_table(cls, table_data: VNFInfo) -> 'VNFInfoGet':
        return cls(
            **{
                **table_data.model_dump(),
                **{'interfaces': [NFInterfaceGet.from_table(i) for i in table_data.interfaces]},
            }
        )


class NSInfoBase(SQLModel):
    id: str = Field(primary_key=True)
    type: str
    status: str
    nsf_id: str | None = Field(foreign_key='nsf.id', default=None)
    nsi_id: str | None = Field(foreign_key='nsi.id', default=None)
    estsla_dict: dict = Field(sa_column=Column(JSON), default_factory=dict)


class NSInfo(NSInfoBase, table=True):
    vnfs: list[VNFInfo] = Relationship()
    nsf: NSF = Relationship()


class NSInfoGet(NSInfoBase):
    vnfs: list[VNFInfoGet]
    nsf: NSFGet | None

    @classmethod
    def from_table(cls, table_data: NSInfo) -> 'NSInfoGet':
        nsf = NSFGet.model_validate(table_data.nsf) if table_data.nsf else None
        return cls(
            **{
                **table_data.model_dump(),
                **{
                    'vnfs': [VNFInfoGet.from_table(v) for v in table_data.vnfs],
                    'nsf': nsf,
                },
            }
        )
