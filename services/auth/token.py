# services/auth/token.py

from fastapi import HTTPException, status
from services.auth.login import decode_token


class TokenService:

    @staticmethod
    def get_current_customer_id(token: str) -> int:
        """
        Access Token의 서명/유효성 체크 후
        customer_id(sub)를 integer로 변환해서 반환.
        """

        payload = decode_token(token)

        if payload.get("type") != "access":
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

        try:
            customer_id = int(subject)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid subject in token",
            )

        return customer_id
