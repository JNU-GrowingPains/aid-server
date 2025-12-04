# schemas/register_repository.py

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class SignupRequest(BaseModel):
    site_type: str
    site_name: str
    site_url: str
    site_tz: str
    site_category: Optional[str] = None

    first_name: str
    last_name: str
    email: EmailStr
    password: str

    agree_privacy: bool


class CustomerResponse(BaseModel):
    customer_id: int
    name: str | None
    email: EmailStr

    class Config:
        from_attributes = True
