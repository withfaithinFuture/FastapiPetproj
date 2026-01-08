import os
from pathlib import Path

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
                #валидация connect str
    postgres_url: PostgresDsn = Field(env='POSTGRES_URL')

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        extra = "ignore"