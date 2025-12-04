# config/settings.py

from pydantic_settings import BaseSettings
from fastapi.middleware.cors import CORSMiddleware


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

# 프론트 도메인들
# 개발 중이면 일단 * 로 다 열어도 됨
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*",  # 개발용 - 전부 허용
]


def setup_cors(app):
    """FastAPI app에 CORS 미들웨어를 붙이는 함수"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )