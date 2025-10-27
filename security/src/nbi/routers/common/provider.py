from fastapi import APIRouter, status

from src.manager.manager_common import common_manager
from src.nbi.routers.dependencies import SessionDep
from src.resources.models.provider import ProviderCreate, ProviderGet

provider_router = APIRouter()


@provider_router.post('/', response_model=str, status_code=status.HTTP_201_CREATED)
def post_provider(session: SessionDep, provider_create: ProviderCreate):
    return common_manager.create_provider(provider_create, session)


@provider_router.get('/{provider_id}', response_model=ProviderGet)
def get_provider(session: SessionDep, provider_id: str):
    return common_manager.get_provider(provider_id, session)


@provider_router.delete('/{provider_name}', status_code=status.HTTP_200_OK)
def delete_provider(session: SessionDep, provider_name: str):
    common_manager.delete_provider(provider_name, session)
