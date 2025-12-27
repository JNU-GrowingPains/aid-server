# services/dashboard_service.py : 날짜계산,리스트/딕셔너리 가공,레포지토리 호출


from datetime import date, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from konlpy.tag import Okt
from collections import Counter

from repositories.dashboard import dashboard_repository as repo


def range_from_days(days: int) -> tuple[date, date]:
    to_d = date.today()
    from_d = to_d - timedelta(days=days - 1)
    return from_d, to_d


# KPI Summary
async def get_kpi_summary(db: AsyncSession, days: int):
    from_d, to_d = range_from_days(days)
    sales, items, buyers = await repo.fetch_kpi_summary(db, from_d, to_d)

    return {
        "days": days,
        "sales": int(sales or 0),
        "items": int(items or 0),
        "buyers": int(buyers or 0),
    }


# Daily Trend
async def get_daily_trend(db: AsyncSession, days: int, metric: str):
    rows = await repo.fetch_daily_trend(db, days, metric)

    return [
        {
            "date": r.date,
            "value": int(r.value) if r.value else 0
        }
        for r in rows
    ]


# Top Products
async def get_top_products(
    db: AsyncSession,
    limit: int,
    from_date: Optional[date],
    to_date: Optional[date],
    category_id: Optional[int],
):
    rows = await repo.fetch_top_products(
        db, limit, from_date, to_date, category_id
    )
    return {"items": [dict(r) for r in rows], "count": len(rows)}


# Review Stats
async def get_review_analysis(db: AsyncSession):
    stats, bad_reviews = await repo.fetch_review_stats(db)

    return {
        "total_count": stats.total_reviews or 0,
        "avg_rating": round(stats.avg_rating, 1) if stats.avg_rating else 0.0,
        "positive_count": int(stats.positive_cnt or 0),
        "negative_count": int(stats.negative_cnt or 0),
        "negative_top3": [
            {
                "name": r.writer_name,
                "rating": r.rating,
                "date": r.created_at,
                "content": r.content
            } for r in bad_reviews
        ]
    }


# All Review Texts (워드클라우드)
async def get_review_keywords(db: AsyncSession):
    texts = await repo.fetch_all_review_texts(db)
    full_text = " ".join(texts)

    okt = Okt()
    nouns = okt.nouns(full_text)
    count = Counter([n for n in nouns if len(n) > 1])

    return [
        {"text": word, "value": freq}
        for word, freq in count.most_common(30)
    ]


# Device Share
async def get_device_share(db: AsyncSession, metric: str):
    rows = await repo.fetch_device_share(db, metric)
    return [dict(r) for r in rows]


# Orders By Category
async def get_orders_by_category(db: AsyncSession, metric: str):
    rows = await repo.fetch_orders_by_category(db, metric)
    return [dict(r) for r in rows]


# Funnel
async def get_funnel(
    db: AsyncSession,
    from_date: Optional[date],
    to_date: Optional[date],
):
    rows = await repo.fetch_funnel(db, from_date, to_date)
    data = [{"step": r["step"], "count": int(r["count"])} for r in rows]

    if not from_date and not to_date:
        visits = await repo.fetch_visits(db)
        data.insert(0, {"step": "visit", "count": int(visits)})

    return data
