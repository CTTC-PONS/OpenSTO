from dataclasses import dataclass

from sqlmodel import SQLModel

from src.resources.models.ssla.ssla import ESSLAAIOGet


class SSLAApplicationRequest(SQLModel):
    nsr_id: str
    wim_service_id: str
    ssla_aio: ESSLAAIOGet


class SSLAApplyRequest(SQLModel):
    ssla_id: str
    service_id: str


class SSLAApplicationClientRequest(SSLAApplicationRequest):
    domain_opensto_ip: str
    domain_opensto_port: int


class SSLADeletionClientRequest(SQLModel):
    service_id: str
    domain_opensto_ip: str
    domain_opensto_port: int
