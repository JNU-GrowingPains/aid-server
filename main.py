from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from sqlalchemy import text
from routers.auth.register_router import router as register_router
from routers.auth.login_router import router as login_router
from routers.auth.logout_router import router as logout_router
from config.settings import setup_cors

app = FastAPI()

# ✅ CORS 설정
setup_cors(app)

@app.get("/")
async def test_connection(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT NOW()"))
        current_time = result.scalar()
        return {"message": "Connected to AWS RDS!", "time": current_time}
    except Exception as e:
        # 브라우저/터미널에서 에러 원문을 그대로 보기 위해
        return {"error": str(e)}

app.include_router(register_router)
app.include_router(login_router)
app.include_router(logout_router)