from sqlmodel import Session, select

from src.exceptions import (
    NetworkSecurityFunctionNotFoundError,
    NetworkServiceDescriptionNotFound,
)
from src.resources.models.nsf import NSD, NSF, NSDCreate, NSDGet, NSFCreate, NSFGet
from src.resources.models.nsi import KEY


def create_nsd(nsd_create: NSDCreate, session: Session) -> KEY:
    nsd = NSD.model_validate(nsd_create)
    session.add(nsd)
    session.commit()
    session.refresh(nsd)
    return KEY(key=nsd.id)


def get_nsd(nsd_id: str, session: Session) -> NSD:
    statement = select(NSD).where(NSD.id == nsd_id)
    nsds = session.exec(statement)
    nsd = nsds.first()
    if not nsd:
        raise NetworkServiceDescriptionNotFound
    return nsd


def get_nsd_api(nsd_id: str, session: Session) -> NSDGet:
    nsd = get_nsd(nsd_id, session)
    if nsd is None:
        raise NetworkServiceDescriptionNotFound
    return NSDGet.model_validate(nsd)


def get_nsds_api(session: Session) -> list[NSDGet]:
    statement = select(NSD)
    nsds = session.exec(statement)
    return [NSDGet.model_validate(nsd) for nsd in nsds]


def create_nsf(nsf_create: NSFCreate, session: Session) -> NSFGet:
    ns = NSF.model_validate(nsf_create)
    session.add(ns)
    session.commit()
    session.add(ns)
    return NSFGet.model_validate(ns)


def update_nsf(nsf_update: NSF, session: Session) -> NSFGet:
    nsf = get_nsf(nsf_update.id, session)
    nsf.ssla_id = nsf_update.ssla_id
    nsf.tsla_id = nsf_update.tsla_id
    nsf.vertical_service_nsr_id = nsf_update.vertical_service_nsr_id
    nsf.vertical_service_floating_ip = nsf_update.vertical_service_floating_ip
    nsf.status = nsf_update.status
    nsf.trust_controller_id = nsf_update.trust_controller_id
    nsf.closed_loop_id = nsf_update.closed_loop_id
    session.add(nsf)
    session.commit()
    session.refresh(nsf)
    return NSFGet.model_validate(nsf)


def delete_nsf(nsf_id: str, session: Session) -> None:
    nsf = get_nsf(nsf_id, session)
    session.delete(nsf)
    session.commit()


def get_nsf(nsf_id: str, session: Session) -> NSF:
    ns = session.get(NSF, nsf_id)
    if not ns:
        raise NetworkSecurityFunctionNotFoundError
    return ns


def get_nsf_by_closed_loop_id(cl_id: str, session: Session) -> NSF:
    statement = select(NSF).where(NSF.closed_loop_id == cl_id)
    nsfs = session.exec(statement)
    nsf = nsfs.first()
    if not nsf:
        raise NetworkSecurityFunctionNotFoundError
    return nsf


def get_nsf_by_vertical_service_id(vertical_service_id: str, session: Session) -> NSF:
    statement = select(NSF).where(NSF.vertical_service_nsr_id == vertical_service_id)
    nsfs = session.exec(statement)
    nsf = nsfs.first()
    if not nsf:
        raise NetworkSecurityFunctionNotFoundError
    return nsf


def get_nsf_api(nsf_id: str, session: Session) -> NSFGet:
    ns = get_nsf(nsf_id, session)
    if not ns:
        raise NetworkSecurityFunctionNotFoundError
    return NSFGet.model_validate(ns)


# TODO: add provider id filtering capability
def get_nsfs_api(session: Session) -> list[NSFGet]:
    statement = select(NSF)
    nss = session.exec(statement)
    return [NSFGet.model_validate(ns) for ns in nss]
