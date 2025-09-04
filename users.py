from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

# 요청 body 정의
class User(BaseModel):
    name: str

users = []  # 간단히 메모리에 저장

# POST: 유저 이름 등록
@router.post("")
def create_user(user: User):
    users.append(user.name)
    return {"message": f"User '{user.name}' created successfully."}

# GET: 유저 목록 반환
@router.get("")
def list_users():
    return {"users": users}