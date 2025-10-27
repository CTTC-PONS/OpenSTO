from fastapi import APIRouter, status

from src.manager.manager_across import across_manager
from src.nbi.routers.dependencies import SessionDep
from src.resources.models.ssla.capability import CapabilityCreate, CapabilityGet
from src.resources.models.ssla.ssla import DXSLAAIO, ESSLAAIOCreate, ESSLAAIOGet

opensto_ssla_and_policy_router = APIRouter()


@opensto_ssla_and_policy_router.post(
    '/nsfr', response_model=str, status_code=status.HTTP_201_CREATED
)
def nsfr_create(session: SessionDep, nsfr: CapabilityCreate):
    return across_manager.upload_capability(nsfr, session)


@opensto_ssla_and_policy_router.get(
    '/nsfr/{nsfr_id}', response_model=CapabilityGet, status_code=status.HTTP_200_OK
)
def nsfr_get(session: SessionDep, nsfr_id: str):
    return across_manager.retrieve_capability(nsfr_id, session)


@opensto_ssla_and_policy_router.get(
    '/dssla/{essla_id}', response_model=DXSLAAIO, status_code=status.HTTP_200_OK
)
def dssla_aio_get(session: SessionDep, essla_id: str):
    return across_manager.translate_essla_to_dssla(essla_id, session)


@opensto_ssla_and_policy_router.post(
    '/essla', response_model=str, status_code=status.HTTP_201_CREATED
)
def essla_aio_create(session: SessionDep, essla_create: ESSLAAIOCreate):
    return across_manager.create_essla_aio(essla_create, session)


@opensto_ssla_and_policy_router.get(
    '/essla/{id}', response_model=ESSLAAIOGet, status_code=status.HTTP_200_OK
)
def essla_aio_get(session: SessionDep, id: str):
    return across_manager.get_essla_aio(id, session)
