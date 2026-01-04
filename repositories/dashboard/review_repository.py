# repositories/dashboard/review_repository.py

from typing import Optional
from sqlalchemy import select, func, desc, case
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Review


async def fetch_review_stats(db: AsyncSession):
    q_stats = select(
        func.count(Review.review_id).label("total_reviews"),
        func.avg(Review.rating).label("avg_rating"),
        func.sum(case((Review.rating >= 4, 1), else_=0)).label("positive_cnt"),
        func.sum(case((Review.rating <= 2, 1), else_=0)).label("negative_cnt")
    )
    q_bad = select(Review).where(Review.rating <= 2).order_by(desc(Review.created_date)).limit(3)
    return (await db.execute(q_stats)).one(), (await db.execute(q_bad)).scalars().all()


async def fetch_all_review_texts(db: AsyncSession):
    return (await db.execute(select(Review.content))).scalars().all()


async def fetch_reviews(db: AsyncSession, page: int, limit: int, rating: Optional[int]):
    q_cnt = select(func.count(Review.review_id))
    if rating: q_cnt = q_cnt.where(Review.rating == rating)
    total = (await db.execute(q_cnt)).scalar()

    q = select(Review).order_by(desc(Review.created_date))
    if rating: q = q.where(Review.rating == rating)
    q = q.offset((page - 1) * limit).limit(limit)

    return (await db.execute(q)).scalars().all(), total