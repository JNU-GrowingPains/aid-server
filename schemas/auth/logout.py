# schemas/auth/logout.py

from pydantic import BaseModel


class LogoutRequest(BaseModel):
    refresh_token: str


class LogoutResponse(BaseModel):
    detail: str = "Successfully logged out"