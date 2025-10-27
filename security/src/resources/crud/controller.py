from sqlmodel import Session, select
from src.control import ControllerCredentials
from src.exceptions import ControllerNotFoundError
from src.resources.models.controller import Controller, ControllerCreate, ControllerGet, ControllerType


def create_controller(ctrl: ControllerCreate, session: Session) -> ControllerGet:
    controller = Controller.model_validate(ctrl)
    session.add(controller)
    session.commit()
    session.refresh(controller)
    return ControllerGet.model_validate(controller)


def delete_controller(ctrl_id: str, session: Session) -> ControllerGet:
    statement = select(Controller).where(Controller.id == ctrl_id)
    controllers = session.exec(statement)
    controller = controllers.first()
    if not controller:
        raise ControllerNotFoundError
    session.delete(controller)
    session.commit()
    return ControllerGet.model_validate(controller)


def get_controller(ctrl_id: str, session: Session) -> ControllerGet:
    controller = session.get(Controller, ctrl_id)
    if not controller:
        raise ControllerNotFoundError
    return ControllerGet.model_validate(controller)


def get_controller_credentials(controller_type: ControllerType, session: Session) -> ControllerCredentials:
    statement = select(Controller).where(Controller.controller_type == controller_type)
    controllers = session.exec(statement)
    controller = controllers.first()
    if not controller:
        raise ControllerNotFoundError
    return ControllerCredentials(
        ip=controller.ip, port=controller.port, username=controller.username, password=controller.password
    )
