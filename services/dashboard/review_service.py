# services/dashboard/review_service.py

import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
# konlpy 대신 정규표현식 사용
from collections import Counter
from repositories.dashboard import review_repository as repo

async def get_review_analysis(db: AsyncSession, product_id: Optional[int] = None):
    """
    리뷰 분석 통계 (그룹화 적용)
    - product_id가 주어지면 해당 그룹의 모든 상품 리뷰를 합산
    """
    stats, bad = await repo.get_review_stats(db, product_id)
    return {
        "total_count": stats.total_reviews or 0, 
        "avg_rating": round(stats.avg_rating, 1) if stats.avg_rating else 0.0,
        "positive_count": int(stats.positive_cnt or 0), 
        "negative_count": int(stats.negative_cnt or 0),
        "negative_top3": [
            {
                "name": r.writer, 
                "rating": r.rating, 
                "date": r.created_date, 
                "content": r.content
            } for r in bad
        ]
    }


async def get_product_review_keywords(db: AsyncSession, product_no: int, limit: int = 30):
    """특정 상품의 리뷰 키워드 추출 (기존 로직 재사용)"""
    texts = await repo.fetch_review_texts_by_product(db, product_no)
    if not texts: 
        return []
    
    # 기존 키워드 추출 로직 재사용
    all_keywords = []
    
    # 불용어 리스트
    stopwords = {
        '이것', '그것', '저것', '여기', '거기', '저기', '이거', '그거', '저거',
        '하지만', '그리고', '또한', '그래서', '그런데', '그러나', '따라서',
        '정말', '너무', '아주', '매우', '조금', '좀', '많이', '잘',
        '좋은', '나쁜', '괜찮', '그냥', '이제', '지금', '오늘', '어제'
    }
    
    for text in texts:
        korean_words = re.findall(r'[가-힣]{2,}', text)
        filtered_words = [word for word in korean_words if word not in stopwords]
        all_keywords.extend(filtered_words)
    
    count = Counter(all_keywords)
    return [{"text": w, "value": f} for w, f in count.most_common(limit)]

async def get_review_list(db: AsyncSession, page: int, limit: int, rating: Optional[int]):
    reviews, total = await repo.fetch_reviews(db, page, limit, rating)
    
    def get_sentiment(score): 
        return "긍정" if score >= 4 else "중립" if score == 3 else "부정"
    
    # limit=0일 때는 실제 반환된 개수를 limit으로 설정
    actual_limit = len(reviews) if limit == 0 else limit
    actual_page = 1 if limit == 0 else page
    
    return {
        "total_count": total, 
        "page": actual_page, 
        "limit": actual_limit,
        "items": [{
            "review_id": r.review_id, 
            "writer": r.writer, 
            "rating": r.rating,
            "sentiment": get_sentiment(r.rating), 
            "content": r.content,
            "created_date": r.created_date, 
            "product_no": r.product_no
        } for r in reviews]
    }