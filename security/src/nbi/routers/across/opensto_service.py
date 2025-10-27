from fastapi import APIRouter, status

from src.control.opensto import SSLAApplyRequest
from src.manager.manager_across import across_manager
from src.nbi.routers.dependencies import SessionDep

opensto_service_router = APIRouter()


@opensto_service_router.post('/apply', response_model=str, status_code=status.HTTP_201_CREATED)
def apply_ssla(session: SessionDep, service: SSLAApplyRequest):
    return across_manager.apply_ssla_to_deployed_service(service, session)


@opensto_service_router.delete('/apply/{service_id}', status_code=status.HTTP_200_OK)
def remove_ssla(session: SessionDep, service_id: str):
    return across_manager.remove_ssla_from_deployed_service(service_id, session)
