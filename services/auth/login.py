#services/auth/login.py

from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from repositories.auth.login import LoginRepository
from schemas.auth.login import LoginRequest, TokenPair, RefreshRequest


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": subject,         # 보통 user_id 또는 email
        "type": "access",
        "exp": expire,
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": subject,
        "type": "refresh",
        "exp": expire,
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


class LoginService:
    @staticmethod
    async def login(db: AsyncSession, data: LoginRequest) -> TokenPair:
        # 1) 이메일로 유저 조회
        customer = await LoginRepository.get_customer_by_email(db, data.email)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # 2) 비밀번호 검증
        if not verify_password(data.password, customer.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # 3) JWT 발급 (sub로 customer_id 사용)
        subject = str(customer.customer_id)
        access_token = create_access_token(subject)
        refresh_token = create_refresh_token(subject)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    async def refresh_token(data: RefreshRequest) -> TokenPair:
        payload = decode_token(data.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # refresh로 새 access + 새 refresh 둘 다 발급하는 패턴
        new_access = create_access_token(subject)
        new_refresh = create_refresh_token(subject)

        return TokenPair(access_token=new_access, refresh_token=new_refresh)