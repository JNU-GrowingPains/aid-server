# repositories/dashboard/review_repository.py

from typing import Optional
from sqlalchemy import select, func, desc, case
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Review
from config.product_groups import PRODUCT_GROUPS


async def get_review_stats(db: AsyncSession, product_id: Optional[int] = None):
    """
    리뷰 통계 조회 (그룹화 적용)
    - product_id가 주어지면 해당 그룹의 모든 상품 리뷰를 합산
    - 총 리뷰 수
    - 평균 평점
    - 긍정 리뷰 개수 (rating >= 4)
    - 부정 리뷰 개수 (rating <= 2)
    - 부정 리뷰 Top 3 (최신 날짜순)
    """
    # product_id가 주어진 경우, 그룹 내 모든 product_id 가져오기
    if product_id:
        group_ids = PRODUCT_GROUPS.get(product_id, [product_id])
    else:
        group_ids = None
    
    # 리뷰 통계 쿼리
    q_stats = select(
        func.count(Review.review_id).label("total_reviews"),
        func.avg(Review.rating).label("avg_rating"),
        func.sum(case((Review.rating >= 4, 1), else_=0)).label("positive_cnt"),
        func.sum(case((Review.rating <= 2, 1), else_=0)).label("negative_cnt")
    )
    
    # 그룹 내 모든 상품 필터 (그룹화 적용)
    if group_ids:
        q_stats = q_stats.where(Review.product_id.in_(group_ids))
    
    # 부정 리뷰 Top 3 쿼리
    q_bad = select(Review).where(Review.rating <= 2).order_by(desc(Review.created_date))
    
    # 그룹 내 모든 상품 필터 (그룹화 적용)
    if group_ids:
        q_bad = q_bad.where(Review.product_id.in_(group_ids))
    
    q_bad = q_bad.limit(3)
    
    return (await db.execute(q_stats)).one(), (await db.execute(q_bad)).scalars().all()


async def fetch_all_review_texts(db: AsyncSession):
    return (await db.execute(select(Review.content))).scalars().all()


async def fetch_review_texts_by_product(db: AsyncSession, product_no: int):
    """특정 상품의 리뷰 내용만 조회"""
    query = select(Review.content).where(Review.product_no == product_no)
    return (await db.execute(query)).scalars().all()


async def fetch_reviews(db: AsyncSession, page: int, limit: int, rating: Optional[int]):
    # 전체 개수 조회
    q_cnt = select(func.count(Review.review_id))
    if rating: 
        q_cnt = q_cnt.where(Review.rating == rating)
    total = (await db.execute(q_cnt)).scalar() or 0

    # 쿼리 생성
    q = select(Review).order_by(desc(Review.created_date))
    if rating: 
        q = q.where(Review.rating == rating)
    
    # limit=0이면 전체 데이터 조회 (최대 10,000개 제한)
    if limit == 0:
        actual_limit = min(total, 10000)
        q = q.limit(actual_limit)
    else:
        # 일반 페이징
        q = q.offset((page - 1) * limit).limit(limit)

    reviews = (await db.execute(q)).scalars().all()
    return reviews, total