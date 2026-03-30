from pathlib import Path
from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
                #валидация connect str
    postgres_url: PostgresDsn = Field(env='POSTGRES_URL')
    base_market_data_service_url: str = Field(env='BASE_MARKET_DATA_SERVICE_URL')
    base_market_data_service_timeout: float = Field(env='BASE_MARKET_DATA_SERVICE_TIMEOUT')
    redis_url: str = Field(env='REDIS_URL')
    SERVICE_NAME: str = "market_data_service"

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        extra = "ignore"


settings = Settings()