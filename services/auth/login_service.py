#services/auth/login_repository.py

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from repositories.auth.login_repository import LoginRepository
from repositories.auth.refresh_token_repository import RefreshTokenRepository
from schemas.auth.login_schema import LoginRequest, TokenPair, RefreshRequest


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

        # 기존에 발급된 RefreshToken들 제거 (선택 사항, 한 계정당 1개만 유지하려는 경우)
        await RefreshTokenRepository.delete_all_by_customer(db, customer.customer_id)

        # 새 RefreshToken DB에 저장
        await RefreshTokenRepository.create(
            db=db,
            customer_id=customer.customer_id,
            token=refresh_token,
        )

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    async def refresh_token(db: AsyncSession, data: RefreshRequest) -> TokenPair:
        # 1) JWT 검증 (서명/유효기간/타입 확인)
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

        customer_id = int(subject)

        # 2) DB에서 해당 토큰이 실제로 존재하는지 확인
        stored_token = await RefreshTokenRepository.get_by_token(db, data.refresh_token)
        if stored_token is None or stored_token.customer_id != customer_id:
            # DB에 없으면 → 이미 삭제된/탈취된/조작된 토큰
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or revoked",
            )

        # 3) 토큰 회전(Token rotation): 사용된 기존 토큰 삭제
        await RefreshTokenRepository.delete_by_id(db, stored_token.refresh_token_id)

        # 4) 새 access + 새 refresh 발급
        new_access = create_access_token(subject)
        new_refresh = create_refresh_token(subject)

        # 5) 새 refresh를 DB에 저장
        await RefreshTokenRepository.create(
            db=db,
            customer_id=customer_id,
            token=new_refresh,
        )

        return TokenPair(access_token=new_access, refresh_token=new_refresh)
