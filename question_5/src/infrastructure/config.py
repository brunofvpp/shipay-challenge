from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_ASYNC_DRIVER: str = "postgresql+asyncpg"
    DATABASE_SYNC_DRIVER: str = "postgresql+psycopg2"
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASS: str
    DATABASE_SCHEMA: str

    @computed_field(return_type=str)
    def async_database_url(self) -> str:
        return (
            f"{self.DATABASE_ASYNC_DRIVER}://{self.DATABASE_USER}:{self.DATABASE_PASS}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_SCHEMA}"
        )

    @computed_field(return_type=str)
    def sync_database_url(self) -> str:
        return (
            f"{self.DATABASE_SYNC_DRIVER}://{self.DATABASE_USER}:{self.DATABASE_PASS}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_SCHEMA}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
