from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # ======================
    # APP
    # ======================
    APP_NAME: str = "GraphQL API"
    DEBUG: bool = False

    # ======================
    # JWT
    # ======================
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    # ======================
    # COOKIES / SESSION
    # ======================
    ACCESS_COOKIE_NAME: str = "access_token"
    REFRESH_COOKIE_NAME: str = "refresh_token"
    SESSION_SECRET_KEY: str
    SESSION_MAX_AGE: int = 86400

    # ======================
    # POSTGRES
    # ======================
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "graphqlapp"

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ======================
    # REDIS
    # ======================
    REDIS_URL: str = "redis://redis:6379/0"

    # ======================
    # MAIL
    # ======================
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USE_TLS: bool = True
    MAIL_USE_SSL: bool = False
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_DEFAULT_SENDER: str

    # ======================
    # FRONTEND
    # ======================
    FRONTEND_URL: str

    # ======================
    # RUN CONTROL
    # ======================
    RUN_SEEDERS: bool = False

    # ======================
    # CORS
    # ======================
    CORS_ORIGINS: list[str] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


settings = Settings()
