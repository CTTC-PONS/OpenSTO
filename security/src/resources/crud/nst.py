from sqlmodel import Session, select
from src.exceptions import NetworkServiceTemplateNotFound
from src.resources.models.nst import NST, NSTCreate, NSTGet


def create_nst(nst_create: NSTCreate, session: Session) -> str:
    nst = NST.model_validate(nst_create)
    session.add(nst)
    session.commit()
    session.refresh(nst)
    return nst.id


def delete_nst(nst_id: str, session: Session) -> None:
    statement = select(NST).where(NST.id == nst_id)
    nsts = session.exec(statement)
    nst = nsts.first()
    if not nst:
        raise NetworkServiceTemplateNotFound
    session.delete(nst)
    session.commit()


def get_nst(nst_id: str, session: Session) -> NST:
    statement = select(NST).where(NST.id == nst_id)
    nsts = session.exec(statement)
    nst = nsts.first()
    if not nst:
        raise NetworkServiceTemplateNotFound
    return nst


def get_nst_api(nst_id: str, session: Session) -> NSTGet:
    nst = get_nst(nst_id, session)
    if not nst:
        raise NetworkServiceTemplateNotFound
    return NSTGet.from_NST(nst)


# todo: Define what is summarized info of NST and return in the summarized format
def get_nsts_api(session: Session) -> list[NSTGet]:
    statement = select(NST)
    nsts = session.exec(statement)
    return [NSTGet.model_validate(nst) for nst in nsts]
