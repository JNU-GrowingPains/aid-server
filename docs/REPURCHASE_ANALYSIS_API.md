# 🔄 재구매 분석 API 규격서

**Base URL:** `/api/v1/repurchase-analysis`

**특징:** 비회원 포함 (이름+주소로 동일인 판단)

---

## 1️⃣ 상품 목록

### `GET /api/v1/repurchase-analysis/products`

그룹화된 대표 상품 10개 반환

#### 요청
```http
GET /api/v1/repurchase-analysis/products
```

#### 응답
```json
[
  {
    "product_id": 15,
    "product_name": "히알루론산 세럼",
    "price": "45000"
  },
  {
    "product_id": 40,
    "product_name": "비타민C 앰플",
    "price": "52000"
  }
]
```

**참고:** 18, 19번 상품 제외됨

---

## 2️⃣ 재구매 KPI

### `GET /api/v1/repurchase-analysis/kpis`

전체 또는 특정 상품(그룹)의 재구매 통계

#### 파라미터
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `product_ids` | int[] | null | 상품 ID 목록 (복수 선택 가능) |

#### 요청 예시
```http
# 전체 상품
GET /api/v1/repurchase-analysis/kpis

# 단일 상품(그룹)
GET /api/v1/repurchase-analysis/kpis?product_ids=15

# 복수 상품 (교차 재구매 포함)
GET /api/v1/repurchase-analysis/kpis?product_ids=15&product_ids=40
```

#### 응답
```json
{
  "total_repurchase_count": 879,     // 총 재구매 고객 수
  "avg_repurchase_rate": 64.7,       // 평균 재구매율 (%)
  "avg_repurchase_days": 29,         // 재구매 소요 기간 (일)
  "same_product_rate": 48.5,         // 동일 상품 재구매 비율 (%)
  "sales_contribution": 74.4         // 재구매 고객 매출 기여도 (%)
}
```

---

## 3️⃣ 재구매 고객 리스트

### `GET /api/v1/repurchase-analysis/customers`

재구매 고객 목록 (회원 + 비회원)

#### 파라미터
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `page` | int | 1 | 페이지 번호 |
| `limit` | int | 10 | 페이지당 개수 (최대 100) |
| `grade` | string | null | 등급 필터 (VIP, GOLD 등) |
| `sort_by` | string | "latest_repurchase" | 정렬 기준 |
| `product_ids` | int[] | null | 상품 ID 목록 |

#### sort_by 옵션
- `latest_repurchase`: 최근 구매일순 (기본)
- `purchase_count`: 구매 횟수순
- `points`: 포인트순
- `name`: 이름순

#### 요청 예시
```http
# 전체 고객 (최근 구매일순)
GET /api/v1/repurchase-analysis/customers?page=1&limit=20

# VIP 등급만 (구매 횟수순)
GET /api/v1/repurchase-analysis/customers?grade=VIP&sort_by=purchase_count

# 특정 상품 구매 고객
GET /api/v1/repurchase-analysis/customers?product_ids=15&product_ids=40
```

#### 응답
```json
{
  "total_count": 879,
  "page": 1,
  "limit": 20,
  "items": [
    {
      "user_id": 123,
      "customer_id": "C017",        // 회원: member_id 반환
      "name": "조인서",
      "grade": "VIP",
      "purchase_count": "31회",
      "address": "서울특별시 서초구 반포동",
      "phone": "010-0017-0119",
      "email": "minseo.jo@email.com",
      "point": "16,240P",
      "avg_period": "48일"
    },
    {
      "user_id": null,
      "customer_id": "김철수|서울시 강남구",  // 비회원: "이름|주소" 형식
      "name": "김철수",              // billing_name
      "grade": "전체",
      "purchase_count": "3회",
      "address": "서울시 강남구",
      "phone": "010-1234-5678",
      "email": "guest@temp.com",
      "point": "0P",
      "avg_period": "45일"
    }
  ]
}
```

---

## 📋 핵심 로직

### **1. 비회원 식별**

```sql
-- 동일인 판단
CASE 
    WHEN member_id LIKE '__guest__%' 
    THEN CONCAT(billing_name, '|', order_address_1)  -- "김철수|서울시 강남구"
    ELSE CAST(user_id AS CHAR)                       -- "123"
END AS customer_key
```

**예시:**
```
주문1: member_id="__guest__:1", billing_name="김철수", order_address_1="서울시 강남구"
주문2: member_id="__guest__:2", billing_name="김철수", order_address_1="서울시 강남구"
→ 같은 customer_key ("김철수|서울시 강남구") → 동일인 ✅
```

---

### **2. 그룹화 적용**

```
product_id=15 선택
→ PRODUCT_GROUPS[15] = [6, 7, 12, 13, 14, 15]
→ 6번~15번 모든 상품의 주문 포함
```

**재구매 쌍 생성:**
```
고객 A의 주문:
2025-01-01: 상품 6 구매
2025-02-01: 상품 7 구매
2025-03-01: 상품 12 구매

생성되는 재구매 쌍:
A: (6→7, 31일)   group_id 15 = 15 → 동일 상품 재구매 ✅
A: (6→12, 59일)  group_id 15 = 15 → 동일 상품 재구매 ✅
A: (7→12, 28일)  group_id 15 = 15 → 동일 상품 재구매 ✅
```

---

### **3. 재구매 KPI 계산**

#### **A. 총 재구매 고객 수**
```sql
COUNT(DISTINCT customer_key) WHERE 주문 2회 이상
```

#### **B. 평균 재구매율**
```
(재구매 고객 수 / 전체 고객 수) × 100
```

#### **C. 평균 재구매 소요 기간**
```sql
AVG(DATEDIFF(재구매 날짜, 첫 구매 날짜))
```

#### **D. 동일 상품 재구매 비율**
```sql
-- 그룹 내 상품끼리도 동일 상품으로 계산
SUM(CASE WHEN first_group_id = repurchase_group_id THEN 1 ELSE 0 END) / 전체 재구매 쌍 × 100
```

#### **E. 재구매 고객 매출 기여도**
```sql
(재구매 고객의 총 매출 / 전체 매출) × 100
```

---

## 🎯 재구매 시나리오

### **전체 상품**
```
product_ids 없음
→ 모든 상품의 재구매 패턴 분석
```

### **단일 상품 (A)**
```
product_ids=[15]
→ 그룹 [6,7,12,13,14,15] 내에서만 분석
→ 6→7, 7→12 등 모두 동일 상품 재구매
```

### **복수 상품 (A, B)**
```
product_ids=[15, 40]
→ 그룹15 [6,7,12,13,14,15] + 그룹40 [28,40,45]
→ 6→7: 동일 상품 (같은 그룹)
→ 6→28: 교차 재구매 (다른 그룹)
→ 28→40: 동일 상품 (같은 그룹)
```

---

## 🚀 프론트 연동 예시

### 1. 상품 목록
```javascript
const response = await api.get('/api/v1/repurchase-analysis/products');
const products = response.data;  // [{ product_id, product_name, price }, ...]
```

### 2. KPI 조회
```javascript
// 전체
const response = await api.get('/api/v1/repurchase-analysis/kpis');

// 특정 상품
const response = await api.get('/api/v1/repurchase-analysis/kpis', {
  params: { product_ids: [15, 40] }
});
// { total_repurchase_count: 879, avg_repurchase_rate: 64.7, ... }
```

### 3. 고객 리스트
```javascript
const response = await api.get('/api/v1/repurchase-analysis/customers', {
  params: {
    page: 1,
    limit: 20,
    grade: 'VIP',
    sort_by: 'purchase_count',
    product_ids: [15]
  }
});
// { total_count, page, limit, items: [...] }
```

---

## ⚠️ 주의사항

### **1. 비회원 처리**
- 회원: `user_id`로 식별
- 비회원: `billing_name + order_address_1`로 식별
- 같은 이름 + 같은 주소 = 동일인

### **2. 고객 리스트**
- 회원: `customer_id`에 member_id 표시 (예: "C017")
- 비회원: `customer_id`에 "이름|주소" 형식으로 표시 (예: "김철수|서울시 강남구")
- 비회원: `name`에 billing_name 표시
- 비회원의 customer_id는 고객 상세 API 호출 시 그대로 사용 가능 (URL 인코딩 필요)

### **3. 그룹화**
- 대표 상품 선택 시 그룹 내 모든 상품 포함
- 그룹 내 상품끼리 재구매 = 동일 상품 재구매

### **4. 등급 필터**
- 비회원은 grade="전체"로 고정
- 등급 필터 적용 시 비회원 제외됨

---

## 📊 SQL 예시

### 재구매 쌍 생성 (비회원 포함)
```sql
WITH customer_purchases AS (
    SELECT 
        CASE 
            WHEN o.member_id LIKE '__guest__%' 
            THEN CONCAT(o.billing_name, '|', o.order_address_1)
            ELSE CAST(o.user_id AS CHAR)
        END AS customer_key,
        o.order_date,
        op.product_id
    FROM orders o
    JOIN order_products op ON o.order_id = op.order_id
    WHERE op.product_id IN (6, 7, 12, 13, 14, 15)  -- 그룹 15
),
repurchase_pairs AS (
    SELECT 
        cp1.customer_key,
        DATEDIFF(cp2.order_date, cp1.order_date) AS days_between
    FROM customer_purchases cp1
    JOIN customer_purchases cp2 
        ON cp1.customer_key = cp2.customer_key
        AND cp1.order_date < cp2.order_date
)
SELECT 
    COUNT(DISTINCT customer_key) AS total_repurchase_count,
    AVG(days_between) AS avg_repurchase_days
FROM repurchase_pairs;
```

---

## 🔗 관련 API
- 상품 분석: `/api/v1/product-analysis` (회원만)
- 회원 분석: `/api/v1/member-analysis`
- 리뷰 분석: `/api/v1/review-analysis`

