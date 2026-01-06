# routers/auth/refresh_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from schemas.auth.login_schema import RefreshRequest, TokenPair
from services.auth.login_service import LoginService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Access Token 재발급",
    description="""
    Refresh Token을 사용하여 새로운 Access Token과 Refresh Token을 발급받습니다.
    
    **Token Rotation 방식:**
    - 기존 Refresh Token은 사용 후 삭제됩니다
    - 새로운 Access Token과 Refresh Token이 발급됩니다
    - 보안을 위해 Refresh Token은 한 번만 사용 가능합니다
    
    **요청 예시:**
    ```json
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    
    **응답 예시:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    ```
    
    **에러 케이스:**
    - 401: Refresh Token이 만료되었거나 유효하지 않음
    - 401: Refresh Token이 DB에 없음 (이미 사용됨 또는 로그아웃됨)
    """
)
async def refresh_token(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh Token으로 새로운 Access Token 발급
    
    - **refresh_token**: 로그인 시 발급받은 Refresh Token
    """
    return await LoginService.refresh_token(db, request)



