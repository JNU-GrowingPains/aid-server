from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

    # JWT 설정
    JWT_SECRET_KEY: str = "change_me_secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30     # Access 30분
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14       # Refresh 14일

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
