# app/core/exceptions.py
from fastapi import Request, status
from fastapi.responses import JSONResponse

async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )