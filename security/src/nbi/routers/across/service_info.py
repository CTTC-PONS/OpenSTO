from fastapi import APIRouter, status

from src.manager.manager_across import across_manager
from src.nbi.routers.dependencies import SessionDep
from src.resources.models.vertical_ns import NSInfoGet

opensto_service_info_router = APIRouter()


@opensto_service_info_router.get('/', response_model=NSInfoGet, status_code=status.HTTP_200_OK)
def get_service_info(
    session: SessionDep, mano_service_id: str, wim_service_id: str = '', domain_name: str = ''
):
    service_info = across_manager.collect_service_info(
        mano_service_id=mano_service_id, wim_service_id=wim_service_id, session=session
    )
    return service_info.mano_service_info
