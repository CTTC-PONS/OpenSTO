from sqlmodel import Session
from src.exceptions import OpenSTOServiceNotFoundError
from src.resources.models.opensto_service import OpenSTOService, OpenSTOServiceCreate, OpenSTOServiceGet


def create_opensto_service(open_sto_service_create: OpenSTOServiceCreate, session: Session) -> OpenSTOServiceGet:
    open_sto_service = OpenSTOService.model_validate(open_sto_service_create.model_dump())
    session.add(open_sto_service)
    session.commit()
    session.refresh(open_sto_service)
    return OpenSTOServiceGet.from_OpenSTOService(open_sto_service)


def get_opensto(open_sto_id: str, session: Session) -> OpenSTOService:
    opensto_service = session.get(OpenSTOService, open_sto_id)
    if not opensto_service:
        raise OpenSTOServiceNotFoundError
    return opensto_service


def get_opensto_api(service_id: str, session: Session) -> OpenSTOServiceGet:
    service = session.get(OpenSTOService, service_id)
    if not service:
        raise OpenSTOServiceNotFoundError
    return OpenSTOServiceGet.from_OpenSTOService(service)


def remove_opensto_service(opensto_service_id: str, session: Session) -> None:
    opensto = get_opensto(opensto_service_id, session)
    session.delete(opensto)
    session.commit()
