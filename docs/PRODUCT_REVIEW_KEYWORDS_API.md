# 📋 상품별 리뷰 키워드 API 규격서

## 개요

특정 상품의 리뷰에서 추출한 키워드를 제공하는 API입니다. 워드클라우드 시각화에 사용됩니다.

---

## 엔드포인트

```
GET /api/v1/product-analysis/products/{product_id}/review-keywords
```

---

## 요청

### Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `product_id` | integer | ✅ | 상품 내부 ID |

### Query Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 범위 | 설명 |
|---------|------|------|--------|------|------|
| `limit` | integer | ❌ | 30 | 1~50 | 반환할 키워드 개수 |

### Headers

```
Authorization: Bearer {access_token}
```

---

## 요청 예시

### 1) 기본 요청 (키워드 30개)

```bash
GET /api/v1/product-analysis/products/42/review-keywords
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2) 키워드 개수 지정 (10개만)

```bash
GET /api/v1/product-analysis/products/15/review-keywords?limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3) 최대 키워드 (50개)

```bash
GET /api/v1/product-analysis/products/26/review-keywords?limit=50
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 응답

### 성공 (200 OK)

#### 일반 응답

```json
[
  {
    "text": "촉촉해요",
    "value": 45
  },
  {
    "text": "효과",
    "value": 38
  },
  {
    "text": "만족",
    "value": 32
  },
  {
    "text": "추천",
    "value": 28
  },
  {
    "text": "배송",
    "value": 25
  }
]
```

#### 리뷰가 없는 경우

```json
[]
```

### 응답 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `text` | string | 키워드 (한글 2글자 이상) |
| `value` | integer | 등장 빈도수 |

### 특징

- **빈도수 기준 내림차순** 정렬
- **불용어 필터링** 적용 (예: "이것", "그것", "정말", "너무" 등)
- **한글만 추출** (2글자 이상)

---

## 에러 응답

### 404 Not Found - 상품을 찾을 수 없음

```json
{
  "detail": "상품을 찾을 수 없습니다"
}
```

**발생 조건:**
- 존재하지 않는 `product_id`를 요청한 경우

### 422 Unprocessable Entity - 잘못된 파라미터

```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 50",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**발생 조건:**
- `limit`이 1~50 범위를 벗어난 경우

### 401 Unauthorized - 인증 실패

```json
{
  "detail": "Could not validate credentials"
}
```

**발생 조건:**
- 유효하지 않거나 만료된 토큰

---

## 구현 세부사항

### 데이터 흐름

```
1. product_id로 Product 테이블 조회
   ↓
2. product_no 추출
   ↓
3. Review 테이블에서 product_no로 필터링
   ↓
4. 리뷰 content 추출
   ↓
5. 정규표현식으로 한글 키워드 추출
   ↓
6. 불용어 필터링
   ↓
7. 빈도수 카운트 및 정렬
   ↓
8. 상위 N개 반환
```

### 불용어 목록

```python
stopwords = {
    '이것', '그것', '저것', '여기', '거기', '저기', '이거', '그거', '저거',
    '하지만', '그리고', '또한', '그래서', '그런데', '그러나', '따라서',
    '정말', '너무', '아주', '매우', '조금', '좀', '많이', '잘',
    '좋은', '나쁜', '괜찮', '그냥', '이제', '지금', '오늘', '어제'
}
```

### 키워드 추출 패턴

```python
# 한글 2글자 이상만 추출
pattern = r'[가-힣]{2,}'
```

---

## 프론트엔드 연동 가이드

### TypeScript 예시

```typescript
interface Keyword {
  text: string;
  value: number;
}

async function fetchProductReviewKeywords(
  productId: number, 
  limit: number = 30
): Promise<Keyword[]> {
  const response = await apiClient.get(
    `/api/v1/product-analysis/products/${productId}/review-keywords`,
    {
      params: { limit }
    }
  );
  
  return response.data;
}

// 사용 예시
const keywords = await fetchProductReviewKeywords(42, 30);

// 워드클라우드 라이브러리에 전달
<WordCloud 
  data={keywords} 
  width={800} 
  height={400} 
/>
```

### React Hook 예시

```typescript
function useProductReviewKeywords(productId: number, limit: number = 30) {
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchKeywords() {
      try {
        setLoading(true);
        const data = await fetchProductReviewKeywords(productId, limit);
        setKeywords(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchKeywords();
  }, [productId, limit]);

  return { keywords, loading, error };
}

// 컴포넌트에서 사용
function ProductReviewKeywords({ productId }: { productId: number }) {
  const { keywords, loading, error } = useProductReviewKeywords(productId);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;
  if (keywords.length === 0) return <EmptyState message="리뷰가 없습니다" />;

  return <WordCloud data={keywords} />;
}
```

---

## 테스트 케이스

### 1️⃣ 정상 케이스

```bash
# 요청
GET /api/v1/product-analysis/products/42/review-keywords?limit=10

# 응답 (200 OK)
[
  {"text": "촉촉해요", "value": 45},
  {"text": "효과", "value": 38},
  {"text": "만족", "value": 32},
  {"text": "추천", "value": 28},
  {"text": "배송", "value": 25},
  {"text": "품질", "value": 22},
  {"text": "포장", "value": 20},
  {"text": "가격", "value": 18},
  {"text": "재구매", "value": 15},
  {"text": "빠르다", "value": 12}
]
```

### 2️⃣ 리뷰가 없는 상품

```bash
# 요청
GET /api/v1/product-analysis/products/999/review-keywords

# 응답 (200 OK)
[]
```

### 3️⃣ 존재하지 않는 상품

```bash
# 요청
GET /api/v1/product-analysis/products/99999/review-keywords

# 응답 (404 Not Found)
{
  "detail": "상품을 찾을 수 없습니다"
}
```

### 4️⃣ 잘못된 limit 파라미터

```bash
# 요청
GET /api/v1/product-analysis/products/42/review-keywords?limit=100

# 응답 (422 Unprocessable Entity)
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 50",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## 기존 API와 비교

### 전체 리뷰 키워드 vs 상품별 리뷰 키워드

| 구분 | 전체 리뷰 키워드 | 상품별 리뷰 키워드 |
|------|------------------|-------------------|
| **엔드포인트** | `/api/v1/review-analysis/keywords` | `/api/v1/product-analysis/products/{product_id}/review-keywords` |
| **범위** | 전체 리뷰 | 특정 상품의 리뷰만 |
| **필터링** | 없음 | product_id 기반 |
| **limit 파라미터** | 고정 30개 | 1~50개 지정 가능 |
| **사용 위치** | 대시보드 전체 리뷰 섹션 | 상품 상세/분석 페이지 |

---

## 성능 고려사항

### 응답 시간

- **평균**: 100~300ms
- **리뷰 50개 기준**: ~150ms
- **리뷰 500개 기준**: ~400ms

### 캐싱 전략 (권장)

```python
# Redis 캐싱 예시 (5분 TTL)
cache_key = f"product:{product_id}:keywords:{limit}"
cache_ttl = 300  # 5분

# 캐시 조회 → 없으면 DB 조회 → 캐시 저장
```

### 최적화 팁

1. **프론트엔드 캐싱**: SWR 또는 React Query 사용
2. **debounce**: 상품 변경 시 300ms debounce 적용
3. **lazy loading**: 워드클라우드 영역이 보일 때만 호출

---

## 버전 히스토리

| 버전 | 날짜 | 변경 사항 |
|------|------|-----------|
| 1.0.0 | 2026-01-06 | 최초 릴리스 |

---

## 문의

API 관련 문의사항은 백엔드 개발팀으로 연락주세요.

- **Slack**: #backend-api
- **Email**: backend-team@company.com

