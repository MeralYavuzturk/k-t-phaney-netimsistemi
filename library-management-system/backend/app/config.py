from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Online Kütüphane Yönetim Sistemi"
    database_url: str = "sqlite:///./library.db"
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_minutes: int = 60 * 24
    loan_days_default: int = 14
    cors_origins: list[str] = ["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8080", "http://localhost:8080", "http://127.0.0.1:3000", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
