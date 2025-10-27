from fastapi import FastAPI

from src.config import settings
from src.nbi.exceptions import add_nbi_exception_handlers

from . import logger
from .routers.across import across_api_router
from .routers.common import common_api_router


def get_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)
    app.include_router(common_api_router, prefix='/common', tags=['common'])
    app.include_router(across_api_router, prefix=settings.ACROSS_API_V1_STR, tags=['across'])
    logger.info('Routes added')

    add_nbi_exception_handlers(app)
    logger.info('nbi exception handlers added in %s mode', 'debug' if settings.DEBUG_MODE else 'non-debug')
    return app
