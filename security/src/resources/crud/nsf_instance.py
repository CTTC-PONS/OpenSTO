from sqlmodel import Session, select

from src.exceptions import NetSecurityFunctionInstaceNotFoundError
from src.resources.models.nsf_instance import (
    NSFInstance,
    NSFInstanceCreate,
    NSFInstanceGet,
)


def create_nsf_instance(nsf_instance_create: NSFInstanceCreate, session: Session) -> NSFInstanceGet:
    nsf_instance = NSFInstance.model_validate(nsf_instance_create)
    session.add(nsf_instance)
    session.commit()
    session.refresh(nsf_instance)
    return NSFInstanceGet.model_validate(nsf_instance)


def delete_nsf_instance(nsf_instance_id: str, session: Session) -> NSFInstanceGet:
    statement = select(NSFInstance).where(NSFInstance.id == nsf_instance_id)
    nsf_instances = session.exec(statement)
    nsf_instace = nsf_instances.first()
    if not nsf_instace:
        raise NetSecurityFunctionInstaceNotFoundError
    session.delete(nsf_instace)
    session.commit()
    return NSFInstanceGet.model_validate(nsf_instace)


def get_nsf_instance(session: Session, nsf_instance_id: str) -> NSFInstanceGet:
    nsf_instance = session.get(NSFInstance, nsf_instance_id)
    if not nsf_instance:
        raise NetSecurityFunctionInstaceNotFoundError
    return NSFInstanceGet.model_validate(nsf_instance)
