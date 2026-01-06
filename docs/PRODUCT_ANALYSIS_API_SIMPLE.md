# 📊 상품분석 API 규격서

**Base URL:** `/api/v1/product-analysis`

---

## 1️⃣ 상품 목록

### `GET /api/v1/product-analysis/products`

그룹화된 대표 상품 10개 반환

#### 요청
```http
GET /api/v1/product-analysis/products?limit=10
```

#### 응답
```json
{
  "items": [
    {
      "product_id": 15,
      "product_code": 345,
      "product_name": "히알루론산 세럼",
      "price": "45000"
    }
  ],
  "count": 10
}
```

**참고:** 18, 19번 상품은 제외됨

---

## 2️⃣ 상품 KPI 통계

### `GET /api/v1/product-analysis/stats`

전체 또는 특정 상품(그룹)의 판매 통계

#### 파라미터
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `days` | int | 30 | 조회 기간 (일) |
| `product_id` | int | null | 상품 ID (미입력 시 전체) |

#### 요청 예시
```http
# 전체 상품 최근 30일
GET /api/v1/product-analysis/stats?days=30

# 특정 상품(그룹) 최근 7일
GET /api/v1/product-analysis/stats?days=7&product_id=15
```

#### 응답
```json
{
  "days": 30,
  "sales": 15420000,   // 총 매출액 (원)
  "items": 342,        // 총 판매 수량 (개)
  "buyers": 156        // 총 구매자 수 (명, 회원만)
}
```

**중요:**
- `sales`, `items`: 전체 주문 (회원 + 비회원)
- `buyers`: **회원만** 카운트 (비회원 제외)

---

## 3️⃣ 일별 트렌드 차트

### `GET /api/v1/product-analysis/chart/trend`

일별 매출/판매량/구매자 수 트렌드

#### 파라미터
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `days` | int | 30 | 조회 기간 (최소 7일) |
| `metric` | string | "amount" | `amount` (매출액), `quantity` (판매량), `buyers` (구매자수) |
| `product_id` | int | null | 상품 ID |

#### 요청 예시
```http
# 최근 30일 매출 트렌드
GET /api/v1/product-analysis/chart/trend?days=30&metric=amount

# 특정 상품 최근 7일 판매량
GET /api/v1/product-analysis/chart/trend?days=7&metric=quantity&product_id=15
```

#### 응답
```json
[
  { "date": "2025-01-01", "value": 450000 },
  { "date": "2025-01-02", "value": 520000 },
  { "date": "2025-01-03", "value": 380000 }
]
```

---

## 📋 그룹화 규칙

### 예시: product_id = 15 선택
```
대표 상품 15 (히알루론산 세럼)
  ├─ product_id: 6
  ├─ product_id: 7
  ├─ product_id: 12
  ├─ product_id: 13
  ├─ product_id: 14
  └─ product_id: 15
```

**통계 계산:**
- `sales` = 6번 매출 + 7번 매출 + ... + 15번 매출
- `items` = 6번 판매량 + 7번 판매량 + ... + 15번 판매량
- `buyers` = (6번 + ... + 15번) 구매한 고유 회원 수

---

## 🔄 날짜 계산

```
오늘: 2025-01-05
days=7  → 2024-12-30 ~ 2025-01-05 (7일)
days=30 → 2024-12-07 ~ 2025-01-05 (30일)
days=90 → 2024-10-08 ~ 2025-01-05 (90일)
```

---

## 🚀 프론트 연동 예시

### 1. 상품 목록
```javascript
const response = await api.get('/api/v1/product-analysis/products');
const products = response.data.items;
```

### 2. KPI 조회
```javascript
const response = await api.get('/api/v1/product-analysis/stats', {
  params: { days: 30, product_id: 15 }
});
// { days: 30, sales: 3250000, items: 72, buyers: 45 }
```

### 3. 트렌드 차트
```javascript
const response = await api.get('/api/v1/product-analysis/chart/trend', {
  params: { days: 7, metric: 'amount', product_id: 15 }
});
const chartData = response.data; // [{ date, value }, ...]
```

---

## ⚠️ 주의사항

1. **비회원 처리**
   - 매출, 판매량: 회원 + 비회원 모두 포함
   - 구매자 수: **회원만** 포함

2. **그룹화**
   - 대표 상품 선택 시 그룹 내 모든 상품 통계 합산
   - 목록에는 대표 10개만 표시

3. **제외 상품**
   - product_id 1, 18, 19는 모든 API에서 제외

4. **날짜 범위**
   - `days` 파라미터: 오늘 포함 최근 N일
   - `OrderProduct.order_date` 기준

---

## 📝 SQL 예시

### KPI 구매자 수 (회원만)
```sql
SELECT COUNT(DISTINCT orders.user_id)
FROM order_products
JOIN orders ON order_products.order_id = orders.order_id
WHERE order_products.order_date >= '2024-12-07'
  AND order_products.order_date <= '2025-01-05'
  AND orders.user_id IS NOT NULL  -- 회원만
  AND order_products.product_id IN (9, 10);  -- 그룹화
```

### 일별 트렌드 (매출)
```sql
SELECT order_products.order_date AS date,
       SUM(order_products.order_product_amount) AS value
FROM order_products
WHERE order_products.product_id IN (9, 10)
GROUP BY order_products.order_date
ORDER BY order_products.order_date
LIMIT 90;
```

---

## 🔗 관련 API
- 재구매 분석: `/api/v1/repurchase-analysis` (비회원 포함)
- 리뷰 분석: `/api/v1/review-analysis`
- 회원 분석: `/api/v1/member-analysis`

