from fastapi import APIRouter

from .controller import controller_router
from .firewall import firewall_router
from .probe import probe_router
from .provider import provider_router
from .topology import topology_router

common_api_router = APIRouter()

common_api_router.include_router(controller_router, prefix='/controller')
common_api_router.include_router(probe_router, prefix='/probe')
common_api_router.include_router(firewall_router, prefix='/firewall')
common_api_router.include_router(provider_router, prefix='/provider')
common_api_router.include_router(topology_router, prefix='/topology')
