from typing import Literal, overload

from sqlmodel import Session
from src.exceptions import NetworkServiceInfoNotFoundError
from src.resources.models.nsf import NSF
from src.resources.models.vertical_ns import NSInfo, NSInfoGet


def create_mano_service_info(ns_info: NSInfo, session: Session) -> NSInfoGet:
    session.add(ns_info)
    session.commit()
    session.refresh(ns_info)
    return NSInfoGet.from_table(ns_info)


@overload
def get_mano_service_info(ns_id: str, session: Session, as_table: Literal[True]) -> NSInfo: ...
@overload
def get_mano_service_info(ns_id: str, session: Session, as_table: Literal[False]) -> NSInfoGet: ...


def get_mano_service_info(ns_id: str, session: Session, as_table: bool) -> NSInfoGet | NSInfo:
    ns_info = session.get(NSInfo, ns_id)
    if not ns_info:
        raise NetworkServiceInfoNotFoundError
    if as_table:
        return ns_info
    return NSInfoGet.from_table(ns_info)


def update_mano_service_info(ns_info: NSInfo, session: Session) -> None:
    updated_ns_info = session.get(NSInfo, ns_info.id)
    if not updated_ns_info:
        raise NetworkServiceInfoNotFoundError
    updated_ns_info.type = ns_info.type
    updated_ns_info.status = ns_info.status
    updated_ns_info.nsf_id = ns_info.nsf_id
    updated_ns_info.nsi_id = ns_info.nsi_id
    updated_ns_info.estsla_dict = ns_info.estsla_dict
    session.add(updated_ns_info)
    session.commit()


def delete_mano_service_info(ns_id: str, session: Session) -> None:
    ns_info = session.get(NSInfo, ns_id)
    if not ns_info:
        raise NetworkServiceInfoNotFoundError
    for vnf in ns_info.vnfs:
        for interface in vnf.interfaces:
            session.delete(interface)
        session.delete(vnf)
    session.delete(ns_info)
    session.commit()


def get_nsf_of_vertical_ns(ns_id: str, session: Session) -> NSF:
    ns_info = session.get(NSInfo, ns_id)
    if not ns_info:
        raise NetworkServiceInfoNotFoundError
    return ns_info.nsf
