# app/core/exceptions.py
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse

async def value_error_handler(request: Request, exc: ValueError):
    raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )ㅗ토