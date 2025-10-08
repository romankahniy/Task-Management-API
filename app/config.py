from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/task_manager"

    DB_USER: Optional[str] = "postgres"
    DB_PASSWORD: Optional[str] = "postgres"
    DB_NAME: Optional[str] = "task_manager"
    DB_HOST: Optional[str] = "localhost"
    DB_PORT: Optional[int] = 5432

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PROJECT_NAME: str = "Task Management API"

    VERSION: str = "1.0.0"
    DEBUG: bool = True

    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEFAULT_PAGE_SIZE: int = 50

    MAX_PAGE_SIZE: int = 100

    TESTING: bool = False

    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"

    RATE_LIMIT_ENABLED: bool = False

    RATE_LIMIT_PER_MINUTE: int = 60

    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_testing(self) -> bool:
        return self.TESTING or self.ENVIRONMENT == "testing"

    @property
    def database_url_for_env(self) -> str:
        if self.is_testing:
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL

    def get_db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()


def validate_settings() -> None:
    errors = []

    if settings.is_production:
        default_key = "your-secret-key-change-in-production"
        if default_key in settings.SECRET_KEY:
            errors.append("SECRET_KEY must be changed in production!")

        if len(settings.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters!")

        if settings.DEBUG:
            errors.append("DEBUG must be False in production!")

    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is required!")

    if errors:
        error_msg = "\n".join(f"  - {error}" for error in errors)
        raise ValueError(f"Configuration errors:\n{error_msg}")

    print("✅ Configuration validated successfully")


class DevelopmentSettings(Settings):
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "WARNING"
    DOCS_URL: Optional[str] = None
    REDOC_URL: Optional[str] = None


class TestingSettings(Settings):
    TESTING: bool = True
    ENVIRONMENT: str = "testing"
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"


def get_settings_for_environment(env: str = "development") -> Settings:
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestingSettings,
    }

    settings_class = settings_map.get(env, Settings)
    return settings_class()
