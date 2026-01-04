from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db, engine, Base
from sqlalchemy import select, func
from models import models

from routers.auth.register_router import router as register_router
from routers.auth.login_router import router as login_router
from routers.auth.logout_router import router as logout_router

from config.settings import setup_cors

from routers.dashboard import (
    product_router,
    review_router,
    customer_router,
    repurchase_router
)


app = FastAPI()

# ✅ CORS 설정
setup_cors(app)

# 서버 켜질 때 테이블 자동 생성
@app.on_event("startup")
async def startup():
    # DB 엔진을 연결해서
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 헬스체크
@app.get("/")
async def test_connection(db: AsyncSession = Depends(get_db)):
    now = (await db.execute(select(func.now()))).scalar_one()
    return {"message": "Connected to AWS RDS!", "time": now}

# 1. 인증 관련
app.include_router(register_router)
app.include_router(login_router)
app.include_router(logout_router)

# 2. 상세 분석 대시보드
app.include_router(product_router.router)     # 상품 분석
app.include_router(review_router.router)      # 리뷰 분석
app.include_router(customer_router.router)    # 고객 분석 (새로 등록!)
app.include_router(repurchase_router.router)  # 재구매 분석