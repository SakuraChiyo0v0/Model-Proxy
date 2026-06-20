from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./model_proxy.db"
    encryption_key: str = "your-32-byte-encryption-key-here!"
    jwt_secret: str = "your-jwt-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    admin_username: str = "admin"
    admin_password: str = "admin123"

    class Config:
        env_file = ".env"


settings = Settings()
