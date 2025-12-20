# routers/register_repository.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas.auth.register_shema import SignupRequest, CustomerResponse
from services.auth.register_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.signup(db, data)
