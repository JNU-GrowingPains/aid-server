from sqlalchemy.ext.asyncio import AsyncSession
from repositories.analysis import analysis_repository as repo
from datetime import date


# ---------- 고객 분석 서비스 ----------

async def get_customer_analysis(db: AsyncSession, site_id: int):
    # 1. 등급 분포
    grade_rows = await repo.fetch_customer_grade_dist(db, site_id)
    total_users = sum([r.count for r in grade_rows])

    grade_dist = []
    for r in grade_rows:
        percent = round((r.count / total_users * 100), 1) if total_users > 0 else 0
        grade_dist.append({"grade": r.grade, "count": r.count, "percent": percent})

    # 2. 포인트 상위 유저
    top_users = await repo.fetch_top_point_users(db, site_id)

    # 3. 고객 리스트
    list_rows = await repo.fetch_customer_list(db, site_id)

    return {
        "grade_distribution": grade_dist,
        "top_point_users": [dict(r._mapping) for r in top_users],
        "customer_list": [dict(r._mapping) for r in list_rows]
    }


# ---------- 재구매 분석 서비스 ----------

async def get_repurchase_analysis(db: AsyncSession, site_id: int):
    # 1. KPI 계산
    total_users, re_users_cnt = await repo.fetch_repurchase_kpi(db, site_id)

    repurchase_rate = round((re_users_cnt / total_users * 100), 1) if total_users > 0 else 0

    # 더미 데이터 또는 간단한 계산 (평균 재구매 기간 등은 복잡해서 일단 고정값/단순화)
    # 실제로는 datediff 평균을 내야 함

    kpi = {
        "total_repurchase_count": re_users_cnt,  # 총 재구매 유저 수
        "avg_repurchase_rate": repurchase_rate,  # 재구매율
        "avg_repurchase_days": 30,  # (예시) 평균 30일
        "same_product_rate": 49.1,  # (예시) 동일 상품 재구매 비율
        "sales_contribution": 75.0  # (예시) 매출 기여도
    }

    # 2. 재구매 고객 리스트
    user_rows = await repo.fetch_repurchase_user_list(db, site_id)

    user_list = []
    for u in user_rows:
        # 재구매 주기 단순 계산 (마지막구매 - 첫구매) / (구매횟수-1)
        period = 0
        if u.purchase_count > 1 and u.last_purchase_date and u.first_purchase_date:
            delta = u.last_purchase_date - u.first_purchase_date
            period = delta.days // (u.purchase_count - 1)

        user_list.append({
            "user_id": u.user_id,
            "name": u.name,
            "grade": u.grade,
            "purchase_count": u.purchase_count,
            "address": u.address,
            "phone": u.phone,
            "email": u.email,
            "last_purchase": u.last_purchase_date,
            "point": u.point,
            "avg_period": f"{period}일"
        })

    return {"kpi": kpi, "repurchase_list": user_list}


# ---------- 개인별 상세 분석 (Modal) ----------
async def get_user_detail_analysis(db: AsyncSession, user_id: int):
    # 유저 정보
    user = await repo.fetch_user_detail(db, user_id)
    if not user:
        return None

    # 재구매 상품 목록
    products = await repo.fetch_user_top_products(db, user_id)

    # 배송지 분석 (화면의 도넛 차트용 - 여기선 단순하게 유저 주소로 100% 처리)
    # 실제로는 Order 테이블의 배송지 주소를 그룹핑해야 함
    location_stat = [{"name": user.address, "value": 100}]

    return {
        "user_info": {
            "name": user.name,
            "grade": user.grade,
            "point": user.point,
            "purchase_count": len(user.orders) if user.orders else 0  # (Lazy loading 주의)
        },
        "top_products": [{"name": p.product_name, "count": p.cnt} for p in products],
        "location_stat": location_stat
    }