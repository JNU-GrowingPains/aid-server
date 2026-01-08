from fastapi import FastAPI, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db, engine, Base
from sqlalchemy import select, func
from models import models
import time

# from routers.auth.register_router import router as register_router  # 🔒 일시 비활성화
from routers.auth.login_router import router as login_router
from routers.auth.logout_router import router as logout_router
from routers.auth.refresh_router import router as refresh_router

from config.settings import setup_cors

# 대시보드 라우터들
from routers.dashboard import (
    review_router,
    repurchase_router,
    management_router
)
from routers.dashboard.member_router import router as member_router
from routers.dashboard.product_router import router as product_router


app = FastAPI()

# ✅ API 요청 로깅 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import sys
    start_time = time.time()
    
    # 요청 로그
    msg = f"\n{'='*80}\n🔵 요청: {request.method} {request.url}\n{'='*80}"
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 응답 로그
        msg = f"🟢 응답: {request.method} {request.url} - {response.status_code} ({process_time:.3f}s)\n{'='*80}\n"
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()
        
        return response
    except Exception as e:
        # 에러 로그
        msg = f"🔴 에러: {request.method} {request.url} - {str(e)}\n{'='*80}\n"
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()
        raise

# ✅ CORS 설정
setup_cors(app)

# DB 테이블은 coredata.sql로 이미 생성되어 있음


# 헬스체크
@app.get("/")
async def test_connection(db: AsyncSession = Depends(get_db)):
    now = (await db.execute(select(func.now()))).scalar_one()
    return {"message": "Connected to AWS RDS!", "time": now}

# 1. 인증 관련
# app.include_router(register_router)  # 🔒 일시 비활성화 (회원가입 중단)
app.include_router(login_router)
app.include_router(logout_router)
app.include_router(refresh_router)

# 2. 상세 분석 대시보드
app.include_router(product_router)              # 상품 분석
app.include_router(review_router.router)        # 리뷰 분석
app.include_router(member_router)               # 고객 분석
app.include_router(repurchase_router.router)    # 재구매 분석

# 3. 개인정보 관리
app.include_router(management_router.router)     # 개인정보 관리