from fastapi import APIRouter, status

from src.manager.manager_common import common_manager
from src.nbi.routers.dependencies import SessionDep
from src.resources.models.controller import ControllerCreate, ControllerGet

controller_router = APIRouter()


@controller_router.post('/', response_model=str, status_code=status.HTTP_201_CREATED)
def post_controller(session: SessionDep, ctrl_create: ControllerCreate):
    return common_manager.create_controller(ctrl_create, session)


@controller_router.get('/{controller_id}', response_model=ControllerGet)
def get_controller(session: SessionDep, controller_id: str):
    return common_manager.get_controller(controller_id, session)


@controller_router.delete('/{controller_id}', status_code=status.HTTP_200_OK)
def delete_controller(session: SessionDep, controller_id: str):
    common_manager.delete_controller(controller_id, session)
