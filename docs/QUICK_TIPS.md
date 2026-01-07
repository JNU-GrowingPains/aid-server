# ⚡ 빠른 참고 - 핵심 시행착오 정리

## 🎯 Top 5 중요 교훈

### 1️⃣ site_id는 필요할 때만 추가하라
```python
# ❌ 처음부터 복잡하게
async def get_data(db, site_id: int):
    query.where(Table.site_id == site_id)

# ✅ 단순하게 시작
async def get_data(db):
    query  # 필터 없음, 나중에 필요하면 추가
```
**이유**: YAGNI (You Aren't Gonna Need It)

---

### 2️⃣ 서브쿼리로 실제 이름 가져오기
```python
# ❌ member_id를 이름으로 사용
"name": row.member_id  # "user123" 표시됨

# ✅ 서브쿼리로 실제 이름
subq_name = select(Order.billing_name).where(
    Order.user_id == Member.user_id
).order_by(desc(Order.order_date)).limit(1).correlate(Member).scalar_subquery()

"name": row.name or row.member_id  # "홍길동" 표시됨
```
**포인트**: `.correlate()` 꼭 사용!

---

### 3️⃣ limit=0으로 전체 조회, 단 10,000개 제한
```python
# ✅ 안전한 전체 조회
fetch_all = (limit == 0)
if fetch_all:
    actual_limit = min(total_count, 10000)  # 안전장치
    query = query.limit(actual_limit)
```
**이유**: 
- 무제한 조회는 위험
- 10,000개면 충분히 유용
- 메모리 약 5MB (안전)

---

### 4️⃣ N+1 쿼리 절대 금지
```python
# ❌ N+1 문제
for member in members:
    orders = await db.execute(
        select(Order).where(Order.user_id == member.user_id)
    )

# ✅ JOIN으로 한 방에
query = select(Member, func.count(Order.id)).join(Order).group_by(Member.id)
```

---

### 5️⃣ 인덱스 꼭 확인
```sql
-- 필수 인덱스
CREATE INDEX idx_member_group_id ON member(group_id);
CREATE INDEX idx_order_user_id ON order(user_id);
CREATE INDEX idx_order_date ON order(order_date);

-- 복합 인덱스
CREATE INDEX idx_order_user_date ON order(user_id, order_date DESC);
```
**확인**: `EXPLAIN SELECT ...`

---

## 🔧 실전 코드 패턴

### 서브쿼리 템플릿
```python
# 패턴: 최신 데이터 가져오기
subq = select(ChildTable.column).where(
    ChildTable.fk_id == ParentTable.id
).order_by(desc(ChildTable.date)).limit(1).correlate(ParentTable).scalar_subquery()
```

### 전체 조회 패턴
```python
# 라우터
limit: int = Query(20, ge=0, le=100)  # 0 허용

# Repository
fetch_all = (limit == 0)
if fetch_all:
    actual_limit = min(total_count, MAX_ITEMS)
    query = query.limit(actual_limit)
else:
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
```

### 에러 처리 패턴
```python
try:
    result = await Service.method(...)
    return result
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"실패: {e}")
    raise HTTPException(status_code=500, detail=f"실패: {str(e)}")
```

---

## 📋 코드 리뷰 체크리스트

작업 완료 후 확인:

```
기능
□ limit=0 테스트 (전체 조회)
□ 필터링/정렬 동작 확인
□ 빈 데이터 처리

성능
□ EXPLAIN 실행 계획 확인
□ 인덱스 사용 확인
□ N+1 쿼리 없는지 확인

문서
□ API 문서 업데이트
□ 예제 코드 작성
□ README 수정
```

---

## 🚨 절대 하지 말 것

1. ❌ **correlate() 없이 서브쿼리** → 카테시안 곱
2. ❌ **무제한 데이터 조회** → 서버 다운
3. ❌ **N+1 쿼리** → 성능 저하
4. ❌ **인덱스 없는 WHERE/ORDER BY** → 느린 쿼리
5. ❌ **에러 메시지 "Error"** → 디버깅 불가

---

## 💡 빠른 디버깅

### 느린 쿼리
```python
# 1. 실행 계획 확인
EXPLAIN SELECT ...

# 2. 인덱스 확인
SHOW INDEX FROM table_name

# 3. 쿼리 로그
echo=True  # SQLAlchemy engine
```

### 이름이 안 나올 때
```python
# subq_name에 .correlate() 있나?
# Order 테이블에 billing_name 있나?
# JOIN이 제대로 되었나?
```

### 10,000개 제한 걸렸을 때
```python
# 방법 1: 필터링으로 범위 축소
?limit=0&grade=VIP

# 방법 2: 페이지네이션으로 전환
?page=1&limit=100
```

---

## 📚 더 알아보기

자세한 내용: [LESSONS_LEARNED.md](LESSONS_LEARNED.md)

---

**작성**: 2026-01-07

