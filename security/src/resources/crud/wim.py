from sqlmodel import Session, select

from src.exceptions import TopologyNotFoundError, WIMServiceInfoNotFoundError
from src.resources.models.wim import (
    IETFNetwork,
    IETFNetworkCreate,
    IETFNetworkGet,
    WIMServiceInfo,
    WIMServiceInfoCreate,
    WIMServiceInfoGet,
)


def create_ietf_topology(topology_create: IETFNetworkCreate, session: Session) -> IETFNetworkGet:
    topology = IETFNetwork.model_validate(topology_create)
    session.add(topology)
    session.commit()
    session.refresh(topology)
    return IETFNetworkGet.from_IETFNetwork(topology)


def get_ietf_topology(session: Session) -> IETFNetworkGet:
    statement = select(IETFNetwork)
    topology = session.exec(statement).first()
    if not topology:
        raise TopologyNotFoundError
    return IETFNetworkGet.from_IETFNetwork(topology)


def create_wim_service_info(wim_service_info_create: WIMServiceInfoCreate, session: Session) -> WIMServiceInfoGet:
    wim_service_info = WIMServiceInfo.model_validate(wim_service_info_create)
    session.add(wim_service_info)
    session.commit()
    session.refresh(wim_service_info)
    return WIMServiceInfoGet.model_validate(wim_service_info)


def get_wim_service_info(wim_service_id: str, session: Session) -> WIMServiceInfoGet:
    wim_service_info = session.get(WIMServiceInfo, wim_service_id)
    if not wim_service_info:
        raise WIMServiceInfoNotFoundError
    return WIMServiceInfoGet.model_validate(wim_service_info)


def delete_wim_service_info(wim_service_id: str, session: Session) -> None:
    wim_service_info = session.get(WIMServiceInfo, wim_service_id)
    if not wim_service_info:
        raise WIMServiceInfoNotFoundError
    session.delete(wim_service_info)
    session.commit()


def update_wim_service_info(cs_info: WIMServiceInfo, session: Session) -> None:
    updated_cs_info = session.get(WIMServiceInfo, cs_info.id)
    if not updated_cs_info:
        raise WIMServiceInfoNotFoundError
    updated_cs_info.type = cs_info.type
    updated_cs_info.status = cs_info.status
    updated_cs_info.nsf_id = cs_info.nsf_id
    updated_cs_info.nsi_id = cs_info.nsi_id
    updated_cs_info.estsla_dict = cs_info.estsla_dict
    updated_cs_info.path = cs_info.path
    session.add(updated_cs_info)
    session.commit()