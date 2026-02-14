from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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
    # MONGO
    # ======================
    MONGO_URI: str
    MONGO_DB_NAME: str

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
    # CORS
    # ======================
    CORS_ORIGINS: list[str] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
