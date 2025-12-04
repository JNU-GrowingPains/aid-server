from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from sqlalchemy import text, select, func
from routers.auth.register_router import router as register_router
from routers.auth.login_router import router as login_router
from routers.auth.logout_router import router as logout_router
from config.settings import setup_cors
from routers.dashboard.dashboard_router import router as dashboard_router

app = FastAPI()

# ✅ CORS 설정
setup_cors(app)

# 헬스체크
@app.get("/")
async def test_connection(db: AsyncSession = Depends(get_db)):
    now = (await db.execute(select(func.now()))).scalar_one()
    return {"message": "Connected to AWS RDS!", "time": now}


app.include_router(register_router)
app.include_router(login_router)
app.include_router(logout_router)
app.include_router(dashboard_router)

