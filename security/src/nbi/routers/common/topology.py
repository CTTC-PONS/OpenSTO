from fastapi import APIRouter, status

from src.manager.manager_common import common_manager
from src.nbi.routers.dependencies import SessionDep
from src.resources.models.topology import TopologyCreate, TopologyGet

topology_router = APIRouter()


@topology_router.post('/', response_model=str, status_code=status.HTTP_201_CREATED)
def topology_create(session: SessionDep, topology: TopologyCreate):
    return common_manager.upload_topology(topology, session)


@topology_router.get('/', response_model=TopologyGet, status_code=status.HTTP_200_OK)
def topology_get(session: SessionDep):
    return common_manager.retrieve_topology(session)
