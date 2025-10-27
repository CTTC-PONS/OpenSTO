from fastapi import APIRouter, status

from src.manager.manager_common import common_manager
from src.nbi.routers.dependencies import SessionDep
from src.resources.models.probe import ProbeCreate, ProbeGet

probe_router = APIRouter()


@probe_router.post('/', response_model=str, status_code=status.HTTP_201_CREATED)
def post_probe(session: SessionDep, probe_create: ProbeCreate):
    return common_manager.create_probe(probe_create, session)


@probe_router.delete('/{probe_id}', status_code=status.HTTP_200_OK)
def delete_probe(session: SessionDep, probe_id: str):
    common_manager.delete_probe(probe_id, session)


@probe_router.get('/{probe_id}', response_model=ProbeGet, status_code=status.HTTP_200_OK)
def get_probe(session: SessionDep, probe_id: str):
    return common_manager.get_probe(session)
