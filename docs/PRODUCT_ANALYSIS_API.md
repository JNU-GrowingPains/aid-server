# 📊 상품분석 API 규격서

## 개요
상품 판매 데이터를 분석하고 시각화하기 위한 API입니다.

**Base URL:** `/api/v1/product-analysis`

---

## 1️⃣ 상품 목록 조회

### `GET /api/v1/product-analysis/products`

그룹화된 대표 상품 목록을 반환합니다.

#### Query Parameters
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `limit` | integer | ❌ | 10 | 반환할 상품 개수 |
| `from_date` | date | ❌ | null | 조회 시작일 (YYYY-MM-DD) |
| `to_date` | date | ❌ | null | 조회 종료일 (YYYY-MM-DD) |

#### 요청 예시
```http
GET /api/v1/product-analysis/products?limit=10
```

#### 응답 예시
```json
{
  "items": [
    {
      "product_id": 15,
      "product_code": 345,
      "product_name": "히알루론산 세럼",
      "price": "45000"
    },
    {
      "product_id": 40,
      "product_code": 350,
      "product_name": "비타민C 앰플",
      "price": "52000"
    }
  ],
  "count": 10
}
```

#### 필드 설명
- `product_id`: 상품 내부 ID (대표 상품)
- `product_code`: 상품 코드 (product_no)
- `product_name`: 상품명
- `price`: 가격 (문자열)

---

## 2️⃣ 상품 KPI 통계 조회

### `GET /api/v1/product-analysis/stats`

전체 또는 특정 상품(그룹)의 KPI를 조회합니다.

#### Query Parameters
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `days` | integer | ❌ | 30 | 조회 기간 (일) |
| `product_id` | integer | ❌ | null | 상품 ID (미입력 시 전체) |

#### 요청 예시
```http
# 전체 상품 최근 30일
GET /api/v1/product-analysis/stats?days=30

# 특정 상품(그룹) 최근 7일
GET /api/v1/product-analysis/stats?days=7&product_id=15
```

#### 응답 예시
```json
{
  "days": 30,
  "sales": 15420000,
  "items": 342,
  "buyers": 156
}
```

#### 필드 설명
- `days`: 조회 기간 (일)
- `sales`: 총 매출액 (원)
- `items`: 총 판매 수량 (개)
- `buyers`: 총 구매자 수 (명)

#### 그룹화 적용
- `product_id=15` 선택 시 → 그룹 [6, 7, 12, 13, 14, 15]의 모든 상품 통계 합산
- `product_id` 미입력 시 → 전체 상품 통계

---

## 3️⃣ 특정 상품 KPI 통계 조회 (RESTful)

### `GET /api/v1/product-analysis/products/{product_id}/stats`

특정 상품(그룹)의 KPI를 조회합니다. (RESTful 방식)

#### Path Parameters
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `product_id` | integer | ✅ | 상품 ID |

#### Query Parameters
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `startDate` | string | ❌ | null | 시작일 (YYYY-MM-DD) |
| `endDate` | string | ❌ | null | 종료일 (YYYY-MM-DD) |

#### 요청 예시
```http
GET /api/v1/product-analysis/products/15/stats
GET /api/v1/product-analysis/products/15/stats?startDate=2025-01-01&endDate=2025-01-31
```

#### 응답 예시
```json
{
  "days": 30,
  "sales": 3250000,
  "items": 72,
  "buyers": 45
}
```

**참고:** 현재는 `startDate`, `endDate`를 무시하고 최근 30일 기본값 사용

---

## 4️⃣ 일별 트렌드 차트 데이터 조회

### `GET /api/v1/product-analysis/chart/trend`

일별 매출/판매량/구매자 수 트렌드 데이터를 반환합니다.

#### Query Parameters
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `days` | integer | ❌ | 30 | 조회 기간 (최소 7일) |
| `metric` | string | ❌ | "amount" | 지표 종류 |
| `product_id` | integer | ❌ | null | 상품 ID (미입력 시 전체) |

#### metric 종류
- `amount`: 매출액
- `quantity`: 판매 수량
- `buyers`: 구매자 수

#### 요청 예시
```http
# 전체 상품 최근 30일 매출 트렌드
GET /api/v1/product-analysis/chart/trend?days=30&metric=amount

# 특정 상품 최근 7일 판매량 트렌드
GET /api/v1/product-analysis/chart/trend?days=7&metric=quantity&product_id=15
```

#### 응답 예시
```json
[
  {
    "date": "2025-01-01",
    "value": 450000
  },
  {
    "date": "2025-01-02",
    "value": 520000
  },
  {
    "date": "2025-01-03",
    "value": 380000
  }
]
```

#### 필드 설명
- `date`: 날짜 (YYYY-MM-DD)
- `value`: 지표 값 (매출액/수량/구매자 수)

---

## 📋 그룹화 적용 규칙

### 상품 그룹 예시
```
대표 상품 15 (히알루론산 세럼)
  ├─ product_id: 6
  ├─ product_id: 7
  ├─ product_id: 12
  ├─ product_id: 13
  ├─ product_id: 14
  └─ product_id: 15
```

### 적용 방식
1. **목록 API**: 대표 상품 10개만 표시
2. **통계 API**: 대표 상품 선택 시 그룹 내 모든 상품 통계 합산
3. **트렌드 API**: 대표 상품 선택 시 그룹 내 모든 상품 트렌드 합산

---

## 🔄 날짜 범위 계산

### days 파라미터
- `days=7`: 오늘 포함 최근 7일
- `days=30`: 오늘 포함 최근 30일
- `days=90`: 오늘 포함 최근 90일

### 예시
```
오늘: 2025-01-05
days=7 → 2024-12-30 ~ 2025-01-05
days=30 → 2024-12-07 ~ 2025-01-05
```

---

## ❌ 에러 응답

### 404 Not Found
```json
{
  "detail": "상품을 찾을 수 없습니다"
}
```

### 400 Bad Request
```json
{
  "detail": "잘못된 파라미터입니다"
}
```

---

## 📌 주요 특징

✅ **그룹화 지원**: 대표 상품 선택 시 그룹 내 모든 상품 통계 합산  
✅ **날짜 필터**: `days`, `startDate`, `endDate`로 기간 조회  
✅ **다양한 지표**: 매출액, 판매량, 구매자 수  
✅ **RESTful API**: 일관된 엔드포인트 구조  

---

## 🚀 프론트엔드 연동 예시

### 1. 상품 목록 불러오기
```javascript
const response = await apiClient.get('/api/v1/product-analysis/products', {
  params: { limit: 10 }
});
const products = response.data.items;
```

### 2. 특정 상품 KPI 조회
```javascript
const productId = 15;
const response = await apiClient.get('/api/v1/product-analysis/stats', {
  params: { days: 30, product_id: productId }
});
console.log(response.data); // { days: 30, sales: 3250000, items: 72, buyers: 45 }
```

### 3. 트렌드 차트 데이터 조회
```javascript
const response = await apiClient.get('/api/v1/product-analysis/chart/trend', {
  params: { 
    days: 7, 
    metric: 'amount', 
    product_id: 15 
  }
});
const chartData = response.data; // [{ date: '2025-01-01', value: 450000 }, ...]
```

---

## 📝 참고사항

1. **product_id vs product_code**:
   - `product_id`: 내부 데이터베이스 ID (사용 권장)
   - `product_code`: 쇼핑몰 상품 번호 (product_no)

2. **그룹화 설정**: `config/product_groups.py`에서 관리

3. **날짜 형식**: ISO 8601 형식 (`YYYY-MM-DD`)

4. **응답 시간**: 평균 < 200ms

---

## 🔗 관련 API
- [재구매 분석 API](./REPURCHASE_ANALYSIS_API.md)
- [리뷰 분석 API](./REVIEW_API_SPEC.md)
- [회원 분석 API](./MEMBER_API_FULL_DATA.md)


