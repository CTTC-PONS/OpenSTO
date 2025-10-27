import logging

from pydantic import BaseModel

logger = logging.getLogger('control')


class ControllerCredentials(BaseModel):
    ip: str = ''
    port: int = 0
    username: str = ''
    password: str = ''
