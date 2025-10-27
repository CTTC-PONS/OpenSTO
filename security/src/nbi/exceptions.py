import json

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from src.config import settings
from src.exceptions import CustomException, CustomNotFoundException
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import logger


def add_nbi_exception_handlers(app: FastAPI):
    if not settings.DEBUG_MODE:

        @app.exception_handler(StarletteHTTPException)
        def non_debug_custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
            logger.error('http exception %s', str(exc.detail))
            return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

        @app.exception_handler(RequestValidationError)
        def non_debug_custom_request_validation_error_handler(request: Request, exc: RequestValidationError):
            json_message = {'detail': exc.errors(), 'body': exc.body}
            logger.error('request validation error :%s', json.dumps(json_message))
            return PlainTextResponse(str(exc), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @app.exception_handler(CustomNotFoundException)
    def custom_not_found_error_handler(request: Request, exc: CustomNotFoundException):
        raise HTTPException(detail=exc.detail, status_code=status.HTTP_404_NOT_FOUND) from None

    @app.exception_handler(CustomException)
    def custom_error_handler(request: Request, exc: CustomException):
        raise HTTPException(detail=exc.detail, status_code=status.HTTP_400_BAD_REQUEST) from None
