from sqlmodel import Session, select
from src.exceptions import NetworkServiceInstanceNotFoundError
from src.resources.models.nsi import KEY, NSI, NSICreate, NSIGet


def create_nsi(nsi_create: NSICreate, session: Session) -> KEY:
    nsi = NSI.model_validate(nsi_create)
    session.add(nsi)
    session.commit()
    session.refresh(nsi)
    return KEY(key=nsi.id)


def update_nsi(new_nsi: NSICreate, session: Session) -> None:
    nsi = NSI.model_validate(new_nsi)
    session.add(nsi)
    session.commit()


def delete_nsi(nsi: NSI, session: Session) -> None:
    session.delete(nsi)
    session.commit()


def get_nsi(nsi_id: str, session: Session) -> NSI:
    statement = select(NSI).where(NSI.id == nsi_id)
    nsis = session.exec(statement)
    nsi = nsis.first()
    if not nsi:
        raise NetworkServiceInstanceNotFoundError
    return nsi


def get_nsi_api(nsi_id: str, session: Session) -> NSIGet:
    nsi = get_nsi(nsi_id, session)
    if not nsi:
        raise NetworkServiceInstanceNotFoundError
    return NSIGet.from_NSI(nsi)


# todo: Define what is summarized info of NSI and return in the summarized format
def get_nsis(session: Session) -> list[NSIGet]:
    statement = select(NSI)
    nsis = session.exec(statement)
    return [NSIGet.model_validate(nsi) for nsi in nsis]
