from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# AWS RDS MySQL 연결 URL
DATABASE_URL = (
    "mysql+aiomysql://admin:wemeet2025@coredata-0.cbmakace0h32.ap-northeast-2.rds.amazonaws.com:3306/coredata"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL 로그 출력
    pool_pre_ping=True  # 연결 유지
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

# 세션 의존성
async def get_db():
    async with async_session() as session:
        yield session
