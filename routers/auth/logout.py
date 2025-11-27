# routers/auth/logout.py

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas.auth.logout import LogoutRequest, LogoutResponse
from services.auth.logout import LogoutService
from services.auth.token import TokenService


router = APIRouter(prefix="/auth", tags=["auth"])

security = HTTPBearer()


def get_current_customer_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """
    Authorization 헤더의 Bearer 토큰에서 customer_id 추출.
    """
    token = credentials.credentials  # "Bearer xxx" 중 xxx 부분
    return TokenService.get_current_customer_id(token)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="로그아웃 (RefreshToken 삭제)",
)
async def logout(
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db),
    customer_id: int = Depends(get_current_customer_id),
):
    return await LogoutService.logout(db, customer_id, data)
