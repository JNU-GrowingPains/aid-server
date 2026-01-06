# routers/auth/logout_repository.py

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from schemas.auth.logout_schema import LogoutResponse
from services.auth.logout_service import LogoutService
from services.auth.token_service import TokenService


router = APIRouter(prefix="/auth", tags=["auth"])

security = HTTPBearer()


def get_current_customer_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """
    Authorization 헤더의 Bearer 토큰에서 customer_id 추출.
    """
    token = credentials.credentials
    return TokenService.get_current_customer_id(token)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="로그아웃 (모든 세션 종료)",
)
async def logout(
    db: AsyncSession = Depends(get_db),
    customer_id: int = Depends(get_current_customer_id),
):
    """
    Authorization 헤더의 Access Token으로 인증 후,
    해당 사용자의 모든 refresh_token 삭제 (모든 디바이스에서 로그아웃).
    """
    return await LogoutService.logout(db, customer_id)
