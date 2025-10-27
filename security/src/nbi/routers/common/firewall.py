from fastapi import APIRouter, status

from src.manager.manager_common import common_manager
from src.nbi.routers.dependencies import SessionDep
from src.resources.models.firewall import FirewallCreate, FirewallGet

firewall_router = APIRouter()


@firewall_router.post('/', response_model=str, status_code=status.HTTP_201_CREATED)
def post_firewall(session: SessionDep, firewall_create: FirewallCreate):
    return common_manager.create_firewall(firewall_create, session)


@firewall_router.delete('/{firewall_id}', status_code=status.HTTP_200_OK)
def delete_firewall(session: SessionDep, firewall_id: str):
    common_manager.delete_firewall(firewall_id, session)


@firewall_router.get('/{firewall_id}', response_model=FirewallGet)
def get_firewall(session: SessionDep, firewall_id: str):
    return common_manager.get_firewall(firewall_id, session)
