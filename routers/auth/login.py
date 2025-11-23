from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas.auth.login import LoginRequest, TokenPair, RefreshRequest
from services.auth.login import LoginService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair, summary="로그인 후 Access/Refresh 토큰 발급")
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await LoginService.login(db, data)


@router.post("/refresh", response_model=TokenPair, summary="Refresh 토큰으로 토큰 재발급")
async def refresh_tokens(
    data: RefreshRequest,
):
    return await LoginService.refresh_token(data)