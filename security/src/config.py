from typing import Literal

from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=True, env_ignore_empty=True, extra='ignore')

    LOGGING_LEVEL: Literal['WARNING', 'ERROR', 'DEBUG', 'INFO']
    PROVIDER_NAME: str = 'DOMAIN01'

    # NBI
    PROJECT_NAME: str
    ACROSS_API_V1_STR: str = '/opensto/api/v1'

    # Backend
    DOCKER_IMAGE_SECURITY: str
    TAG: str
    DEBUG_MODE: bool

    # TFS
    TFS_USERNAME: str = 'admin'
    TFS_PASSWORD: str = 'admin'
    TFS_HOSTNAME: str = '0.0.0.0'
    TFS_NBI_SERVICE_PORT: int = 80

    # OpenSTO Transport Domains
    TRANSPORT_DOMAINS: str

    # Postgres
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    SECURITY_POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme='postgresql+psycopg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.SECURITY_POSTGRES_DB,
        )

    def TFS_NBI_BASE_URL(self, host: str, port: int) -> str:
        return str(
            MultiHostUrl.build(
                scheme='http',
                username=self.TFS_USERNAME,
                password=self.TFS_PASSWORD,
                host=host,
                port=port,
                path='',
            )
        )


settings = Settings()  # type: ignore
