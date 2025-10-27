from typing import Literal, Sequence, overload

from sqlmodel import Session, select

from src.exceptions import ClosedLoopRequestNotFoundError
from src.manager import DomainType
from src.resources.models.closed_loop import (
    ClosedLoopInitializationRequest,
    ClosedLoopInitializationRequestCreate,
    ClosedLoopInitializationRequestGet,
    ClosedLoopType,
)


def create_closed_loop_request(
    closed_loop_request_create: ClosedLoopInitializationRequestCreate, session: Session
) -> ClosedLoopInitializationRequest:
    closed_loop_request = ClosedLoopInitializationRequest.model_validate(closed_loop_request_create)
    session.add(closed_loop_request)
    session.commit()
    session.refresh(closed_loop_request)
    return closed_loop_request


@overload
def get_closed_loop_request(
    closed_loop_request_id: str, session: Session, as_table: Literal[True]
) -> ClosedLoopInitializationRequest: ...


@overload
def get_closed_loop_request(
    closed_loop_request_id: str, session: Session, as_table: Literal[False]
) -> ClosedLoopInitializationRequestGet: ...


def get_closed_loop_request(
    closed_loop_request_id: str, session: Session, as_table: bool = False
) -> ClosedLoopInitializationRequestGet | ClosedLoopInitializationRequest:
    closed_loop = session.get(ClosedLoopInitializationRequest, closed_loop_request_id)
    if not closed_loop:
        raise ClosedLoopRequestNotFoundError
    if as_table:
        return closed_loop
    return ClosedLoopInitializationRequestGet.model_validate(closed_loop)


def update_closed_loop_request(
    closed_loop_request_update: ClosedLoopInitializationRequest, session: Session
) -> None:
    closed_loop = session.get(ClosedLoopInitializationRequest, closed_loop_request_update.id)
    if not closed_loop:
        raise ClosedLoopRequestNotFoundError
    closed_loop.nsi_id = closed_loop_request_update.nsi_id
    closed_loop.nsr_id = closed_loop_request_update.nsr_id
    closed_loop.ns_ip = closed_loop_request_update.ns_ip
    closed_loop.ns_port = closed_loop_request_update.ns_port
    closed_loop.nsf_id = closed_loop_request_update.nsf_id
    closed_loop.domain = closed_loop_request_update.domain
    closed_loop.provider = closed_loop_request_update.provider
    closed_loop.probe_ip = closed_loop_request_update.probe_ip
    closed_loop.probe_port = closed_loop_request_update.probe_port
    closed_loop.probe_username = closed_loop_request_update.probe_username
    closed_loop.probe_password = closed_loop_request_update.probe_password
    closed_loop.ssla_id = closed_loop_request_update.ssla_id
    closed_loop.tsla_id = closed_loop_request_update.tsla_id
    closed_loop.firewall_type = closed_loop_request_update.firewall_type
    closed_loop.firewall_ip = closed_loop_request_update.firewall_ip
    closed_loop.firewall_port = closed_loop_request_update.firewall_port
    closed_loop.firewall_username = closed_loop_request_update.firewall_username
    closed_loop.firewall_password = closed_loop_request_update.firewall_password
    closed_loop.closed_loop_type = closed_loop_request_update.closed_loop_type
    closed_loop.security_sls = closed_loop_request_update.security_sls
    closed_loop.trust_sls = closed_loop_request_update.trust_sls
    closed_loop.active = closed_loop_request_update.active
    closed_loop.e2e_cl_id = closed_loop_request_update.e2e_cl_id
    closed_loop.nsd_id = closed_loop_request_update.nsd_id
    closed_loop.xslap = closed_loop_request_update.xslap
    session.add(closed_loop)
    session.commit()


def delete_closed_loop_request(
    closed_loop_request_id: str, closed_loop_type: ClosedLoopType, session: Session
) -> None:
    statement = (
        select(ClosedLoopInitializationRequest)
        .where(ClosedLoopInitializationRequest.id == closed_loop_request_id)
        .where(ClosedLoopInitializationRequest.closed_loop_type == closed_loop_type)
    )
    closed_loop = session.exec(statement).first()
    if not closed_loop:
        raise ClosedLoopRequestNotFoundError
    session.delete(closed_loop)
    session.commit()


def get_closed_loop_request_by_nsr_id(
    nsr_id: str, closed_loop_type: ClosedLoopType, session: Session
) -> ClosedLoopInitializationRequest:
    statement = (
        select(ClosedLoopInitializationRequest)
        .where(ClosedLoopInitializationRequest.nsr_id == nsr_id)
        .where(ClosedLoopInitializationRequest.closed_loop_type == closed_loop_type)
    )
    closed_loop_request = session.exec(statement).first()
    if not closed_loop_request:
        raise ClosedLoopRequestNotFoundError
    return closed_loop_request


def get_closed_loop_request_by_domain_nsi_id(
    domain: DomainType, nsi_id: str, closed_loop_type: ClosedLoopType, session: Session
) -> ClosedLoopInitializationRequest:
    statement = (
        select(ClosedLoopInitializationRequest)
        .where(ClosedLoopInitializationRequest.domain == domain)
        .where(ClosedLoopInitializationRequest.nsi_id == nsi_id)
        .where(ClosedLoopInitializationRequest.closed_loop_type == closed_loop_type)
    )
    closed_loop_request = session.exec(statement).first()
    if not closed_loop_request:
        raise ClosedLoopRequestNotFoundError
    return closed_loop_request


def get_closed_loop_requests_by_nsi_id(
    nsi_id: str, session: Session
) -> Sequence[ClosedLoopInitializationRequest]:
    statement = select(ClosedLoopInitializationRequest).where(
        ClosedLoopInitializationRequest.nsi_id == nsi_id
    )
    closed_loop_requests = session.exec(statement).all()
    return closed_loop_requests


def get_closed_loop_request_by_domain_and_e2e_cl_id(
    domain: DomainType, e2e_cl_id: str, closed_loop_type: ClosedLoopType, session: Session
) -> ClosedLoopInitializationRequest:
    statement = (
        select(ClosedLoopInitializationRequest)
        .where(ClosedLoopInitializationRequest.domain == domain)
        .where(ClosedLoopInitializationRequest.e2e_cl_id == e2e_cl_id)
        .where(ClosedLoopInitializationRequest.closed_loop_type == closed_loop_type)
    )
    closed_loop_request = session.exec(statement).first()
    if not closed_loop_request:
        raise ClosedLoopRequestNotFoundError
    return closed_loop_request
