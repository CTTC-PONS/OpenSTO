from sqlmodel import Session, select

from src.exceptions import FirewallNotFoundError
from src.resources.models.firewall import Firewall, FirewallCreate, FirewallGet


def create_firewall(firewall_create: FirewallCreate, session: Session) -> FirewallGet:
    firewall = Firewall.model_validate(firewall_create)
    session.add(firewall)
    session.commit()
    session.refresh(firewall)
    return FirewallGet.model_validate(firewall)


def delete_firewall(firewall_id: str, session: Session) -> FirewallGet:
    statement = select(Firewall).where(Firewall.id == firewall_id)
    firewalls = session.exec(statement)
    firewall = firewalls.first()
    if not firewall:
        raise FirewallNotFoundError
    session.delete(firewall)
    session.commit()
    return FirewallGet.model_validate(firewall)


def get_firewall(session: Session) -> FirewallGet:
    statement = select(Firewall)
    firewalls = session.exec(statement)
    firewall = firewalls.first()
    if not firewall:
        raise FirewallNotFoundError
    return FirewallGet.model_validate(firewall)


def get_firewall_by_id(firewall_id: str, session: Session) -> FirewallGet:
    firewall = session.get(Firewall, firewall_id)
    if not firewall:
        raise FirewallNotFoundError
    return FirewallGet.model_validate(firewall)