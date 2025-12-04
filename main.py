from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database.session import get_db
from routers.dashboard.dashboard_router import router as dashboard_router

app = FastAPI(title="Dashboard API (ORM)")

# 헬스체크
@app.get("/")
async def test_connection(db: AsyncSession = Depends(get_db)):
    now = (await db.execute(select(func.now()))).scalar_one()
    return {"message": "Connected to AWS RDS!", "time": now}


app.include_router(dashboard_router)
