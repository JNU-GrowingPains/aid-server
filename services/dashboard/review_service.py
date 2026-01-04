# services/dashboard/review_service.py

import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from konlpy.tag import Okt
from collections import Counter
from repositories.dashboard import review_repository as repo

async def get_review_analysis(db: AsyncSession):
    stats, bad = await repo.fetch_review_stats(db)
    return {
        "total_count": stats.total_reviews or 0, "avg_rating": round(stats.avg_rating, 1) if stats.avg_rating else 0.0,
        "positive_count": int(stats.positive_cnt or 0), "negative_count": int(stats.negative_cnt or 0),
        "negative_top3": [{"name": r.writer, "rating": r.rating, "date": r.created_date, "content": r.content} for r in bad]
    }

async def get_review_keywords(db: AsyncSession):
    texts = await repo.fetch_all_review_texts(db)
    if not texts: return []
    okt = Okt()
    count = Counter([n for n in okt.nouns(" ".join(texts)) if len(n) > 1])
    return [{"text": w, "value": f} for w, f in count.most_common(30)]

async def get_review_list(db: AsyncSession, page: int, limit: int, rating: Optional[int]):
    reviews, total = await repo.fetch_reviews(db, page, limit, rating)
    def get_sentiment(score): return "긍정" if score >= 4 else "중립" if score == 3 else "부정"
    return {
        "total_count": total, "page": page, "limit": limit,
        "items": [{
            "review_id": r.review_id, "writer": r.writer, "rating": r.rating,
            "sentiment": get_sentiment(r.rating), "content": r.content,
            "created_date": r.created_date, "product_no": r.product_no
        } for r in reviews]
    }