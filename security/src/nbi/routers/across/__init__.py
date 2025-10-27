from fastapi import APIRouter

from .opensto_service import opensto_service_router
from .service_info import opensto_service_info_router
from .sslap import opensto_ssla_and_policy_router

across_api_router = APIRouter()

across_api_router.include_router(opensto_service_info_router, prefix='/service_info')
across_api_router.include_router(opensto_ssla_and_policy_router, prefix='/ssla')
across_api_router.include_router(opensto_service_router, prefix='/service')
