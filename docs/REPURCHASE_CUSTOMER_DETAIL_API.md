# 👤 재구매 고객 상세 분석 API

**Base URL:** `/api/v1/repurchase-analysis`

**용도:** 특정 고객의 재구매 패턴 상세 분석 (상품 + 배송지)

---

## 📌 API 엔드포인트

### `GET /api/v1/repurchase-analysis/customer/{customer_id}/detail`

특정 고객의 재구매 상세 정보 (통합 API)

---

## 📋 사용 시나리오

```
1. 재구매 분석 페이지에서 상품 선택 (예: 히알루론산 세럼)
   ↓
2. 해당 상품을 재구매한 고객 목록 표시
   ↓
3. 고객 1명 클릭 (예: 조인서)
   ↓
4. 해당 고객의 상세 재구매 데이터 표시
   - 고객 기본 정보 (이름, 등급, 포인트, 구매 횟수, 평균 재구매 기간)
   - 재구매 상품 목록 (막대그래프)
   - 재구매 배송지 분포 (도넛차트)
```

---

## 🔧 파라미터

### **Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `customer_id` | string | ✅ | 고객 ID (회원/비회원 구분) |

#### **customer_id 형식:**

**1. 회원 고객**
```
customer_id = member_id
예: "C017"
```

**2. 비회원 고객**
```
customer_id = "billing_name|order_address_1"
예: "김철수|서울시 강남구"
⚠️ URL 인코딩 필수!
```

---

## 📨 요청 예시

### **1. 회원 고객**
```http
GET /api/v1/repurchase-analysis/customer/C017/detail
```

### **2. 비회원 고객** (URL 인코딩)
```http
GET /api/v1/repurchase-analysis/customer/%EA%B9%80%EC%B2%A0%EC%88%98%7C%EC%84%9C%EC%9A%B8%EC%8B%9C%20%EA%B0%95%EB%82%A8%EA%B5%AC/detail
```
**디코딩:** `"김철수|서울시 강남구"`

---

## 📤 응답 형식

### **성공 (200 OK)**

```json
{
  "customer": {
    "customer_id": "C017",
    "name": "조인서",
    "grade": "VIP",
    "point": 12950,
    "total_order_count": 22,
    "avg_repurchase_days": 66,
    "first_order_date": "2024-01-15",
    "last_order_date": "2025-11-20"
  },
  "products": [
    {
      "product_id": 15,
      "product_name": "히알루론산 세럼",
      "repurchase_count": 8,
      "percentage": 36.4,
      "first_purchase_date": "2024-01-15",
      "last_purchase_date": "2025-11-20"
    },
    {
      "product_id": 40,
      "product_name": "비타민C 앰플",
      "repurchase_count": 6,
      "percentage": 27.3,
      "first_purchase_date": "2024-03-10",
      "last_purchase_date": "2025-10-05"
    },
    {
      "product_id": 10,
      "product_name": "수분 크림",
      "repurchase_count": 5,
      "percentage": 22.7,
      "first_purchase_date": "2024-02-20",
      "last_purchase_date": "2025-09-15"
    }
  ],
  "addresses": [
    {
      "address": "서울특별시 서초구 반포동",
      "order_count": 20,
      "percentage": 90.9,
      "first_order_date": "2024-01-15",
      "last_order_date": "2025-11-20"
    },
    {
      "address": "경기도 성남시 분당구",
      "order_count": 2,
      "percentage": 9.1,
      "first_order_date": "2024-07-10",
      "last_order_date": "2024-12-15"
    }
  ]
}
```

### **에러 응답**

**404 Not Found** - 고객을 찾을 수 없음
```json
{
  "detail": "고객을 찾을 수 없습니다"
}
```

---

## 📊 응답 필드 설명

### **customer (고객 기본 정보)**

| 필드 | 타입 | 설명 |
|------|------|------|
| `customer_id` | string | 고객 ID (회원: member_id, 비회원: "이름\|주소") |
| `name` | string | 고객 이름 |
| `grade` | string | 고객 등급 (VIP, GOLD, 전체 등) |
| `point` | integer | 보유 포인트 (비회원은 0) |
| `total_order_count` | integer | 총 구매 횟수 |
| `avg_repurchase_days` | integer | 평균 재구매 기간 (일) |
| `first_order_date` | string | 첫 구매일 (YYYY-MM-DD) |
| `last_order_date` | string | 최근 구매일 (YYYY-MM-DD) |

**평균 재구매 기간 계산:**
```
avg_repurchase_days = (마지막 구매일 - 첫 구매일) / (구매 횟수 - 1)
```

---

### **products (재구매 상품 Top 10)**

| 필드 | 타입 | 설명 |
|------|------|------|
| `product_id` | integer | 상품 ID |
| `product_name` | string | 상품명 |
| `repurchase_count` | integer | 해당 상품 구매 횟수 |
| `percentage` | float | 전체 구매 중 해당 상품 비율 (%) |
| `first_purchase_date` | string | 해당 상품 첫 구매일 |
| `last_purchase_date` | string | 해당 상품 최근 구매일 |

**정렬:** 구매 횟수 많은 순 (상위 10개)

**percentage 계산:**
```
percentage = (해당 상품 구매 횟수 / 전체 구매 횟수) × 100
```

---

### **addresses (재구매 배송지 Top 5)**

| 필드 | 타입 | 설명 |
|------|------|------|
| `address` | string | 배송지 주소 (order_address_1) |
| `order_count` | integer | 해당 배송지 주문 횟수 |
| `percentage` | float | 전체 주문 중 해당 배송지 비율 (%) |
| `first_order_date` | string | 해당 배송지 첫 주문일 |
| `last_order_date` | string | 해당 배송지 최근 주문일 |

**정렬:** 주문 횟수 많은 순 (상위 5개)

**percentage 계산:**
```
percentage = (해당 배송지 주문 횟수 / 전체 주문 횟수) × 100
```

---

## 🎨 프론트엔드 연동

### **1. 서비스 함수**

```typescript
// src/services/repurchase.ts

/**
 * 특정 고객의 재구매 상세 정보 조회
 * @param customerId - 회원: member_id, 비회원: "이름|주소"
 */
export async function getCustomerRepurchaseDetail(customerId: string) {
  const encodedId = encodeURIComponent(customerId);
  const response = await apiClient.get(
    `/api/v1/repurchase-analysis/customer/${encodedId}/detail`
  );
  return response.data;
}
```

### **2. React Query 훅**

```typescript
// src/hooks/useRepurchase.ts

export const useCustomerRepurchaseDetail = (customerId: string | null) => {
  return useQuery({
    queryKey: ['customerRepurchaseDetail', customerId],
    queryFn: () => getCustomerRepurchaseDetail(customerId!),
    enabled: !!customerId,  // customerId가 있을 때만 실행
  });
};
```

### **3. 페이지 컴포넌트**

```tsx
// src/pages/RepurchaseAnalysisPage.tsx

const RepurchaseAnalysisPage = () => {
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);

  // 고객 클릭 이벤트
  const handleCustomerClick = (customerId: string) => {
    setSelectedCustomerId(customerId);
  };

  // 고객 상세 정보 조회
  const { data: detail, isLoading } = useCustomerRepurchaseDetail(selectedCustomerId);

  return (
    <>
      {/* 고객 목록 */}
      <CustomerList onCustomerClick={handleCustomerClick} />

      {/* 고객 상세 정보 */}
      {detail && (
        <CustomerDetailPanel>
          {/* 고객 정보 카드 */}
          <CustomerInfoCard 
            name={detail.customer.name}
            grade={detail.customer.grade}
            totalOrders={detail.customer.total_order_count}
            avgDays={detail.customer.avg_repurchase_days}
            points={detail.customer.point}
          />

          {/* 재구매 상품 막대그래프 */}
          <Card title="재구매 상품들">
            <BarChart 
              data={detail.products}
              xKey="product_name"
              yKey="repurchase_count"
              label={(item) => `${item.percentage}%`}
            />
          </Card>

          {/* 재구매 배송지 도넛차트 */}
          <Card title="재구매 배송지">
            <PieChart 
              data={detail.addresses}
              nameKey="address"
              valueKey="order_count"
              label={(item) => `${item.percentage}%`}
            />
          </Card>
        </CustomerDetailPanel>
      )}
    </>
  );
};
```

---

## 📊 차트 데이터 매핑

### **막대그래프 (재구매 상품)**

```javascript
const productChartData = detail.products.map(p => ({
  name: p.product_name,
  value: p.repurchase_count,
  label: `${p.percentage}%`
}));

// Recharts 예시
<BarChart data={productChartData}>
  <XAxis dataKey="name" />
  <YAxis />
  <Bar dataKey="value" fill="#4F46E5" />
  <Tooltip />
</BarChart>
```

### **도넛차트 (재구매 배송지)**

```javascript
const addressChartData = detail.addresses.map(a => ({
  name: a.address.length > 20 ? a.address.substring(0, 20) + '...' : a.address,
  value: a.order_count,
  percentage: a.percentage
}));

// Recharts 예시
<PieChart>
  <Pie 
    data={addressChartData} 
    dataKey="value" 
    nameKey="name"
    innerRadius={60}
    outerRadius={100}
    label={(entry) => `${entry.percentage}%`}
  />
  <Tooltip />
</PieChart>
```

---

## ⚠️ 주의사항

### **1. 비회원 customer_id 처리**

```javascript
// ❌ 잘못된 예
const customerId = "김철수|서울시 강남구";
fetch(`/api/v1/repurchase-analysis/customer/${customerId}/detail`);
// → URL: ...customer/김철수|서울시 강남구/detail (에러!)

// ✅ 올바른 예
const encodedId = encodeURIComponent("김철수|서울시 강남구");
fetch(`/api/v1/repurchase-analysis/customer/${encodedId}/detail`);
// → URL: ...customer/%EA%B9%80%EC%B2%A0%EC%88%98%7C.../detail
```

### **2. 회원 vs 비회원 구분**

```javascript
// customer_id에 "|"가 포함되어 있으면 비회원
const isGuest = customerId.includes("|");

if (isGuest) {
  // 비회원: 이름만 표시, 포인트는 0
  console.log(detail.customer.name);  // "김철수"
  console.log(detail.customer.point); // 0
} else {
  // 회원: 모든 정보 표시
  console.log(detail.customer.name);  // "조인서"
  console.log(detail.customer.point); // 12950
}
```

### **3. 날짜 형식**

- 모든 날짜는 `YYYY-MM-DD` 형식
- 프론트에서 변환 필요 시:

```javascript
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('ko-KR');
};

formatDate("2024-01-15"); // "2024. 1. 15."
```

### **4. 빈 데이터 처리**

```javascript
if (!detail.products.length) {
  return <EmptyState message="재구매 상품이 없습니다" />;
}

if (!detail.addresses.length) {
  return <EmptyState message="배송지 정보가 없습니다" />;
}
```

---

## 🔍 SQL 로직 (참고)

### **고객 식별**

```sql
-- 회원
WHERE member_id = 'C017'

-- 비회원
WHERE member_id LIKE '__guest__%'
  AND billing_name = '김철수'
  AND order_address_1 = '서울시 강남구'
```

### **재구매 상품 통계**

```sql
SELECT 
    p.product_id,
    p.product_name,
    COUNT(DISTINCT o.order_id) AS repurchase_count,
    MIN(o.order_date) AS first_purchase_date,
    MAX(o.order_date) AS last_purchase_date
FROM orders o
JOIN order_products op ON o.order_id = op.order_id
JOIN products p ON op.product_id = p.product_id
WHERE member_id = 'C017'
GROUP BY p.product_id, p.product_name
ORDER BY repurchase_count DESC
LIMIT 10;
```

### **재구매 배송지 통계**

```sql
SELECT 
    o.order_address_1 AS address,
    COUNT(DISTINCT o.order_id) AS order_count,
    MIN(o.order_date) AS first_order_date,
    MAX(o.order_date) AS last_order_date
FROM orders o
WHERE member_id = 'C017'
GROUP BY o.order_address_1
ORDER BY order_count DESC
LIMIT 5;
```

---

## 🎯 사용 예시

### **시나리오: "조인서" 고객 상세 보기**

**1단계: 고객 목록에서 선택**
```
고객 목록:
- 조인서 (C017, VIP, 31회 구매)  ← 클릭!
- 김서연 (C001, GOLD, 35회 구매)
- ...
```

**2단계: API 호출**
```javascript
const detail = await getCustomerRepurchaseDetail("C017");
```

**3단계: 화면 표시**
```
┌─────────────────────────────────────┐
│ 최희윤 고객 재구매 분석              │
├─────────────────────────────────────┤
│ 구매 횟수: 22회                      │
│ 평균 재구매 기간: 66일               │
│ 고객 등급: VIP                       │
│ 보유 포인트: 12,950P                 │
└─────────────────────────────────────┘

재구매 상품들 (막대그래프):
히알루론산 세럼 ████████ 8회 (36.4%)
비타민C 앰플    ██████   6회 (27.3%)
수분 크림        █████    5회 (22.7%)

재구매 배송지 (도넛차트):
서울특별시 서초구 반포동  90.9%
경기도 성남시 분당구       9.1%
```

---

## 🔗 관련 API

- [재구매 고객 목록](./REPURCHASE_ANALYSIS_API.md#고객-리스트-api)
- [재구매 KPI](./REPURCHASE_ANALYSIS_API.md#재구매-kpi)
- [상품 목록](./REPURCHASE_ANALYSIS_API.md#상품-목록)



