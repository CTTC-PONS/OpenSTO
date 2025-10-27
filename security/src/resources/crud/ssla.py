from sqlmodel import Session, select
from src.exceptions import CapabilityNotFoundError, SLSNotFoundError, SSLANotFoundError
from src.resources.models.ssla.capability import Capability, CapabilityCreate, CapabilityGet
from src.resources.models.ssla.sls import SLS, SLSCreate, SLSGet
from src.resources.models.ssla.ssla import ESSLAAIO, ESSLAAIOCreate, ESSLAAIOGet


def create_capability(capability_create: CapabilityCreate, session: Session) -> CapabilityGet:
    capability = Capability.model_validate(capability_create.nsf.model_dump(by_alias=False))
    session.add(capability)
    session.commit()
    return CapabilityGet.from_table(capability)


def get_capability(nsfr_id: str, session: Session) -> CapabilityGet:
    capability = session.get(Capability, nsfr_id)
    if not capability:
        raise CapabilityNotFoundError
    return CapabilityGet.from_table(capability)


def get_capabilities(session: Session) -> list[CapabilityGet]:
    statement = select(Capability)
    capabilities = session.exec(statement)
    return [CapabilityGet.from_table(c) for c in capabilities]


def create_sls(sls_create: SLSCreate, session: Session) -> SLSGet:
    sls = SLS.model_validate(sls_create)
    session.add(sls)
    session.commit()
    return SLSGet.model_validate(sls)


def get_sls(sls_id: str, session: Session) -> SLS:
    sls = session.get(SLS, sls_id)
    if not sls:
        raise SLSNotFoundError
    return sls


def get_sls_api(sls_id: str, session: Session) -> SLSGet:
    sls = session.get(SLS, sls_id)
    if not sls:
        raise SLSNotFoundError
    return SLSGet.model_validate(sls)


def create_essla_aio(essla_create: ESSLAAIOCreate, session: Session) -> ESSLAAIOGet:
    essla_aio = ESSLAAIO.model_validate(essla_create)
    session.add(essla_aio)
    session.commit()
    session.refresh(essla_aio)
    return ESSLAAIOGet.model_validate(essla_aio)


def get_essla_aio(essla_id: str, session: Session) -> ESSLAAIOGet:
    essla_aio = session.get(ESSLAAIO, essla_id)
    if not essla_aio:
        raise SSLANotFoundError
    return ESSLAAIOGet.model_validate(essla_aio)
