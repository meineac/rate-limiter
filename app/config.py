from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379"
    database_url: str = "postgresql+asyncpg://rl_user:password@postgres:5432/ratelimiter"
    admin_token: str = "changeme-to-a-secure-token"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
