# 🎓 고객 분석 API 개발 - 주요 시행착오 및 해결 방법

## 📋 목차
1. [site_id 파라미터 이슈](#1-site_id-파라미터-이슈)
2. [고객 이름 표시 문제](#2-고객-이름-표시-문제)
3. [전체 데이터 조회 구현](#3-전체-데이터-조회-구현)
4. [성능 및 안전성 고려사항](#4-성능-및-안전성-고려사항)

---

## 1. site_id 파라미터 이슈

### ❌ 문제 상황

초기 설계에서 모든 API에 `site_id` 파라미터를 포함시켰습니다.

```python
# 문제가 있는 코드
@router.get("/grade-stats")
async def get_member_grade_statistics(
    site_id: int = Query(1, description="사이트 ID"),
    db: AsyncSession = Depends(get_db)
):
    return await MemberService.get_member_grade_statistics(db, site_id)

# Repository에서
query = select(...).where(Member.site_id == site_id)
```

### 🔍 발견된 문제점

1. **불필요한 파라미터**: 대부분의 경우 단일 사이트 운영
2. **복잡도 증가**: 모든 함수에 site_id 전달 필요
3. **사용자 혼란**: API 호출 시 불필요한 파라미터 입력
4. **데이터베이스 필터링**: WHERE 절에 불필요한 조건 추가

### ✅ 해결 방법

**site_id 파라미터 완전 제거**

```python
# 개선된 코드
@router.get("/grade-stats")
async def get_member_grade_statistics(
    db: AsyncSession = Depends(get_db)
):
    return await MemberService.get_member_grade_statistics(db)

# Repository에서
query = select(...)  # WHERE site_id 조건 제거
```

### 📝 교훈

**핵심 교훈:**
- ✅ **YAGNI 원칙**: You Aren't Gonna Need It - 필요할 때 추가하기
- ✅ **단순성 우선**: 복잡한 멀티 테넌시는 실제 필요할 때만 구현
- ✅ **API 설계**: 사용자 관점에서 최소한의 파라미터만 요구

**멀티 사이트가 정말 필요한 경우:**
```python
# 옵션 1: JWT 토큰에서 site_id 추출
def get_current_site_id(token: str) -> int:
    payload = decode_token(token)
    return payload.get("site_id")

# 옵션 2: 인증된 사용자의 site_id 자동 조회
async def get_user_site_id(customer_id: int, db: AsyncSession) -> int:
    result = await db.execute(
        select(Customer.site_id).where(Customer.customer_id == customer_id)
    )
    return result.scalar()
```

---

## 2. 고객 이름 표시 문제

### ❌ 문제 상황

초기에는 `member_id`를 그대로 이름으로 사용했습니다.

```python
# 문제가 있는 코드
for row in result.all():
    members.append({
        "user_id": row.user_id,
        "member_id": row.member_id,
        "name": row.member_id,  # member_id를 이름으로 사용 (문제!)
        "grade": row.grade,
        ...
    })
```

### 🔍 발견된 문제점

1. **가독성 저하**: "user123" 같은 ID가 이름으로 표시됨
2. **UX 문제**: 관리자가 고객을 식별하기 어려움
3. **실제 이름 누락**: Order 테이블에 `billing_name`이 있는데 활용 안 함

### ✅ 해결 방법

**서브쿼리로 실제 이름 가져오기**

```python
# 개선된 코드
# 최근 주문의 billing_name을 가져오는 서브쿼리
subq_name = select(Order.billing_name).where(
    Order.user_id == Member.user_id
).order_by(desc(Order.order_date)).limit(1).correlate(Member).scalar_subquery()

query = (
    select(
        Member.user_id,
        Member.member_id,
        subq_name.label("name"),  # 실제 이름 추가
        MemberGroup.group_name.label("grade"),
        ...
    )
    .join(MemberGroup, Member.group_id == MemberGroup.group_id)
    .outerjoin(Order, Member.user_id == Order.user_id)
    .group_by(Member.user_id, Member.member_id, MemberGroup.group_name, ...)
)

# 결과 처리
for row in result.all():
    members.append({
        "user_id": row.user_id,
        "member_id": row.member_id,
        "name": row.name or row.member_id,  # 이름 없으면 member_id 사용
        ...
    })
```

### 📝 교훈

**핵심 교훈:**
- ✅ **데이터 모델 이해**: 관련 테이블의 컬럼 제대로 파악하기
- ✅ **서브쿼리 활용**: 복잡한 데이터 조회에 서브쿼리 적극 활용
- ✅ **Fallback 전략**: 데이터 없을 때 대체값 제공

**서브쿼리 작성 팁:**

```python
# 패턴 1: 최신 데이터 가져오기
subq_latest = select(Table.column).where(
    Table.fk_id == MainTable.id
).order_by(desc(Table.date)).limit(1).correlate(MainTable).scalar_subquery()

# 패턴 2: 집계 함수 사용
subq_count = select(func.count(Table.id)).where(
    Table.fk_id == MainTable.id
).correlate(MainTable).scalar_subquery()

# 패턴 3: COALESCE로 기본값 설정
subq_with_default = func.coalesce(subq_name, 'Unknown')
```

**주의사항:**
```python
# ❌ 잘못된 방법: correlate() 없으면 카테시안 곱 발생
subq = select(Order.billing_name).where(
    Order.user_id == Member.user_id
).scalar_subquery()  # correlate() 누락!

# ✅ 올바른 방법
subq = select(Order.billing_name).where(
    Order.user_id == Member.user_id
).correlate(Member).scalar_subquery()  # correlate() 필수!
```

---

## 3. 전체 데이터 조회 구현

### ❌ 초기 설계 문제

페이지네이션만 지원하여 전체 데이터 조회가 불편했습니다.

```python
# 초기 코드: 페이지네이션만 지원
limit: int = Query(20, ge=1, le=100)  # 최소값 1

# 전체 데이터를 조회하려면 반복 호출 필요
async function getAllMembers() {
  let allMembers = [];
  let page = 1;
  while (true) {
    const data = await fetch(`...?page=${page}&limit=100`);
    allMembers.push(...data.members);
    if (page >= data.total_pages) break;
    page++;
  }
  return allMembers;
}
```

### 🔍 문제점

1. **비효율**: 여러 번 API 호출 필요
2. **네트워크 오버헤드**: 각 요청마다 TCP 연결, 인증 등
3. **클라이언트 복잡도**: 반복 로직 작성 필요
4. **성능**: 총 응답 시간 증가

### ✅ 해결 방법

**`limit=0` 옵션 추가 + 10,000개 안전 제한**

```python
# 개선된 코드
limit: int = Query(20, ge=0, le=100, description="0 = 전체 조회")

# Repository에서
fetch_all = (limit == 0)

if fetch_all:
    # 전체 데이터 조회 (안전장치: 최대 10,000개)
    actual_limit = min(total_count, 10000)
    query = query.limit(actual_limit)
    page = 1
    limit = actual_limit
else:
    # 페이징 적용
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
```

### 📝 교훈

**핵심 교훈:**
- ✅ **유연성**: 다양한 사용 사례 지원
- ✅ **안전장치**: 무제한 조회는 위험, 합리적 제한 설정
- ✅ **하위 호환**: 기존 API 동작 유지

**10,000개 제한 선택 이유:**

| 고려사항 | 설명 |
|---------|------|
| **메모리** | 10,000개 × 평균 500 bytes ≈ 5MB (안전) |
| **응답시간** | 일반적으로 1~2초 이내 |
| **데이터베이스** | MySQL에서 충분히 빠른 범위 |
| **사용자 경험** | 웹 브라우저에서 렌더링 가능한 수준 |

**다른 제한값 고려:**

```python
# 작은 서비스: 1,000개
MAX_ITEMS = 1000

# 중간 서비스: 5,000개
MAX_ITEMS = 5000

# 대형 서비스: 10,000개 (채택)
MAX_ITEMS = 10000

# 엔터프라이즈: 별도의 배치 처리 API 제공
# GET /api/v1/member-analysis/export
# → 백그라운드 작업으로 CSV 생성 후 다운로드 링크 제공
```

---

## 4. 성능 및 안전성 고려사항

### 🔍 주요 고려사항

#### 4.1 N+1 쿼리 문제

**❌ 잘못된 접근:**
```python
# 각 멤버마다 개별 쿼리 실행
members = await db.execute(select(Member))
for member in members:
    # N+1 문제 발생!
    orders = await db.execute(
        select(Order).where(Order.user_id == member.user_id)
    )
```

**✅ 올바른 접근:**
```python
# JOIN으로 한 번에 조회
query = (
    select(Member, func.count(Order.order_id))
    .outerjoin(Order, Member.user_id == Order.user_id)
    .group_by(Member.user_id)
)
```

#### 4.2 인덱스 활용

**확인해야 할 인덱스:**
```sql
-- 필수 인덱스
CREATE INDEX idx_member_group_id ON member(group_id);
CREATE INDEX idx_order_user_id ON order(user_id);
CREATE INDEX idx_order_date ON order(order_date);

-- 복합 인덱스 (자주 함께 쿼리되는 컬럼)
CREATE INDEX idx_order_user_date ON order(user_id, order_date DESC);
```

**인덱스 확인 방법:**
```sql
-- MySQL
EXPLAIN SELECT ...;
SHOW INDEX FROM member;

-- 쿼리 실행 계획 확인
EXPLAIN ANALYZE SELECT ...;
```

#### 4.3 데이터베이스 커넥션 풀

```python
# config/settings.py
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,          # 기본 커넥션 수
    max_overflow=20,       # 초과 허용 커넥션
    pool_timeout=30,       # 타임아웃
    pool_recycle=3600,     # 1시간마다 재활용
    pool_pre_ping=True     # 연결 확인
)
```

#### 4.4 쿼리 타임아웃

```python
# Repository에서
from sqlalchemy import text

# 타임아웃 설정
await db.execute(text("SET SESSION MAX_EXECUTION_TIME=5000"))  # 5초

# 또는 쿼리 힌트 사용
query = query.execution_options(timeout=5.0)
```

#### 4.5 캐싱 전략

**Redis 캐싱 예시:**
```python
import json
from redis import asyncio as aioredis

class MemberService:
    @staticmethod
    async def get_member_grade_statistics(db: AsyncSession) -> MemberGradeStatsResponse:
        # 캐시 키
        cache_key = "member:grade_stats"
        
        # Redis에서 확인
        redis = await aioredis.from_url("redis://localhost")
        cached = await redis.get(cache_key)
        
        if cached:
            data = json.loads(cached)
            return MemberGradeStatsResponse(**data)
        
        # DB 조회
        stats_data = await MemberRepository.get_member_grade_distribution(db)
        
        # 캐시 저장 (5분)
        await redis.setex(
            cache_key,
            300,  # 5분
            json.dumps(stats_data)
        )
        
        return MemberGradeStatsResponse(**stats_data)
```

#### 4.6 Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.get("/members")
@limiter.limit("10/minute")  # 분당 10회 제한
async def get_member_list(...):
    ...
```

### 📝 교훈

**성능 체크리스트:**

- [ ] **인덱스**: 자주 조회/정렬되는 컬럼에 인덱스 설정
- [ ] **N+1 방지**: JOIN으로 한 번에 조회
- [ ] **커넥션 풀**: 적절한 크기 설정
- [ ] **쿼리 최적화**: EXPLAIN으로 실행 계획 확인
- [ ] **캐싱**: 자주 조회되고 변경 적은 데이터 캐싱
- [ ] **Rate Limiting**: API 남용 방지
- [ ] **모니터링**: 느린 쿼리 로깅 및 추적

---

## 5. API 설계 원칙

### 💡 배운 설계 원칙

#### 5.1 RESTful 설계

```python
# ✅ 좋은 예
GET  /api/v1/member-analysis/members           # 리스트 조회
GET  /api/v1/member-analysis/members/{id}      # 단일 조회
GET  /api/v1/member-analysis/grade-stats       # 통계 조회

# ❌ 나쁜 예
GET  /api/v1/getMemberList
POST /api/v1/member-analysis/get-members
GET  /api/v1/members/all/data/query
```

#### 5.2 파라미터 검증

```python
# ✅ 좋은 예: Pydantic으로 명확한 검증
limit: int = Query(20, ge=0, le=100, description="페이지당 항목 수")
sort_by: str = Query(
    "latest_purchase",
    regex="^(latest_purchase|purchase_count|points|name)$"
)

# ❌ 나쁜 예: 검증 없음
limit: int = Query(20)
sort_by: str = Query("latest_purchase")
```

#### 5.3 에러 처리

```python
# ✅ 좋은 예: 명확한 에러 메시지
try:
    result = await MemberService.get_member_list(...)
    return result
except ValueError as e:
    raise HTTPException(
        status_code=400,
        detail=f"잘못된 요청: {str(e)}"
    )
except Exception as e:
    logger.error(f"고객 리스트 조회 실패: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail=f"고객 리스트 조회 실패: {str(e)}"
    )

# ❌ 나쁜 예: 불명확한 에러
except Exception:
    raise HTTPException(status_code=500, detail="Error")
```

#### 5.4 문서화

```python
# ✅ 좋은 예: 상세한 문서
@router.get(
    "/members",
    response_model=MemberListResponse,
    summary="고객 리스트",
    description="""
    전체 고객 목록을 페이지네이션으로 조회합니다.
    
    **전체 데이터 조회:**
    - limit=0으로 설정 시 모든 데이터 반환 (최대 10,000개 제한)
    
    **정렬 옵션:**
    - latest_purchase: 최근 구매일순 (기본값)
    - purchase_count: 구매횟수순
    ...
    """
)

# ❌ 나쁜 예: 문서 없음
@router.get("/members")
```

---

## 6. 코드 리뷰 체크리스트

개발 완료 후 확인해야 할 사항:

### 기능 테스트
- [ ] 정상 케이스 동작 확인
- [ ] 경계값 테스트 (0, 1, 최대값)
- [ ] 에러 케이스 처리
- [ ] 필터링/정렬 옵션 확인

### 성능 테스트
- [ ] 대용량 데이터 조회 테스트
- [ ] 응답 시간 측정
- [ ] EXPLAIN으로 쿼리 최적화 확인
- [ ] 부하 테스트 (동시 요청)

### 보안 체크
- [ ] SQL Injection 방지 (ORM 사용)
- [ ] 인증/인가 확인
- [ ] Rate Limiting 설정
- [ ] 민감 정보 노출 방지

### 문서화
- [ ] API 문서 작성
- [ ] 예제 코드 제공
- [ ] README 업데이트
- [ ] 변경 이력 기록

---

## 7. 추천 개발 프로세스

### 단계별 접근

1. **요구사항 분석**
   - 실제 사용 시나리오 파악
   - 불필요한 기능 제거 (YAGNI)

2. **데이터 모델 이해**
   - ERD 확인
   - 관계 파악
   - 인덱스 확인

3. **프로토타입**
   - 최소 기능으로 시작
   - 빠른 검증

4. **반복 개선**
   - 사용자 피드백
   - 성능 최적화
   - 기능 추가

5. **문서화**
   - 코드 주석
   - API 문서
   - 사용 예제

---

## 8. 유용한 도구 및 라이브러리

### 개발 도구
```bash
# API 테스트
httpie
curl
Postman

# 성능 모니터링
py-spy          # Python 프로파일러
locust          # 부하 테스트
New Relic / DataDog  # APM

# 데이터베이스
mycli           # MySQL CLI
DBeaver         # DB GUI
```

### Python 라이브러리
```python
# 비동기 처리
asyncio
aiohttp
httpx

# 캐싱
redis
aiocache

# 모니터링
prometheus-client
opentelemetry
```

---

## 📚 참고 자료

### SQLAlchemy
- [서브쿼리 가이드](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#scalar-subqueries)
- [성능 팁](https://docs.sqlalchemy.org/en/20/faq/performance.html)

### FastAPI
- [의존성 주입](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [쿼리 파라미터 검증](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)

### 데이터베이스 최적화
- [MySQL 인덱스 가이드](https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html)
- [쿼리 최적화](https://use-the-index-luke.com/)

---

## 💡 마지막 조언

1. **단순함이 최고**: 복잡한 설계는 나중에
2. **측정하고 개선**: 추측 말고 실제 데이터로
3. **문서화**: 미래의 나를 위해
4. **테스트**: 자동화된 테스트 작성
5. **배우기**: 실수는 성장의 기회

---

**작성일**: 2026-01-07  
**작성자**: AID-SERVER Development Team


