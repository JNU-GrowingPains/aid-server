# 📋 리뷰 분석 API 규격서

## 목차
- [1. 리뷰 통계 & 부정 리뷰 Top 3](#1-리뷰-통계--부정-리뷰-top-3)
- [2. 리뷰 키워드 (워드클라우드)](#2-리뷰-키워드-워드클라우드)
- [3. 전체 리뷰 목록](#3-전체-리뷰-목록)

---

## 1. 리뷰 통계 & 부정 리뷰 Top 3

### **Endpoint**
```
GET /api/v1/review-analysis/stats
```

### **설명**
- 전체 리뷰 통계 (총 개수, 평균 평점, 긍정/부정 개수)
- 부정 리뷰 최신 3건 제공

### **요청 파라미터**
없음

### **응답 예시**
```json
{
  "total_count": 150,
  "avg_rating": 4.3,
  "positive_count": 120,
  "negative_count": 15,
  "negative_top3": [
    {
      "name": "김**",
      "rating": 1,
      "date": "2025-12-03",
      "content": "제품이 설명과 다릅니다. 실망했어요."
    },
    {
      "name": "이**",
      "rating": 2,
      "date": "2025-12-02",
      "content": "배송이 너무 늦었습니다."
    },
    {
      "name": "박**",
      "rating": 2,
      "date": "2025-12-01",
      "content": "포장 상태가 불량했습니다."
    }
  ]
}
```

### **응답 필드**

| 필드 | 타입 | 설명 |
|------|------|------|
| `total_count` | integer | 전체 리뷰 개수 |
| `avg_rating` | float | 평균 평점 (소수점 1자리) |
| `positive_count` | integer | 긍정 리뷰 개수 (별점 4~5점) |
| `negative_count` | integer | 부정 리뷰 개수 (별점 1~2점) |
| `negative_top3` | array | 부정 리뷰 최신 3건 |
| `negative_top3[].name` | string | 작성자명 |
| `negative_top3[].rating` | integer | 별점 (1~5) |
| `negative_top3[].date` | string | 작성일 (YYYY-MM-DD) |
| `negative_top3[].content` | string | 리뷰 내용 |

---

## 2. 리뷰 키워드 (워드클라우드)

### **Endpoint**
```
GET /api/v1/review-analysis/keywords
```

### **설명**
- 전체 리뷰에서 추출한 주요 키워드 30개
- 워드클라우드 시각화에 사용

### **요청 파라미터**
없음

### **응답 예시**
```json
[
  {
    "text": "효과",
    "value": 45
  },
  {
    "text": "만족",
    "value": 38
  },
  {
    "text": "배송",
    "value": 32
  },
  {
    "text": "품질",
    "value": 28
  },
  {
    "text": "추천",
    "value": 25
  }
]
```

### **응답 필드**

| 필드 | 타입 | 설명 |
|------|------|------|
| `text` | string | 키워드 |
| `value` | integer | 등장 빈도수 |

### **특징**
- 한글 2글자 이상 키워드만 추출
- 불용어 필터링 적용
- 빈도수 기준 상위 30개 반환

---

## 3. 전체 리뷰 목록

### **Endpoint**
```
GET /api/v1/review-analysis/list
```

### **설명**
- 전체 리뷰 목록을 페이지네이션으로 조회
- 별점 필터링 지원
- **`limit=0`으로 전체 데이터 조회 가능** (최대 10,000개)

### **요청 파라미터**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `page` | integer | No | 1 | 페이지 번호 (1부터 시작) |
| `limit` | integer | No | 10 | 페이지당 개수 (0~100)<br>**0 = 전체 조회** |
| `rating` | integer | No | null | 별점 필터 (1~5)<br>null = 전체 |

### **요청 예시**

#### 1) 일반 페이징 (10개씩)
```
GET /api/v1/review-analysis/list?page=1&limit=10
```

#### 2) 전체 데이터 조회
```
GET /api/v1/review-analysis/list?limit=0
```

#### 3) 별점 필터링 (별점 5점만)
```
GET /api/v1/review-analysis/list?page=1&limit=10&rating=5
```

### **응답 예시**

#### 일반 페이징 (limit=10)
```json
{
  "total_count": 150,
  "page": 1,
  "limit": 10,
  "items": [
    {
      "review_id": 1,
      "writer": "김철수",
      "rating": 5,
      "sentiment": "긍정",
      "content": "정말 좋은 제품입니다. 효과가 확실해요!",
      "created_date": "2025-12-03",
      "product_no": 350
    },
    {
      "review_id": 2,
      "writer": "이영희",
      "rating": 4,
      "sentiment": "긍정",
      "content": "만족합니다. 재구매 의사 있어요.",
      "created_date": "2025-12-02",
      "product_no": 322
    }
  ]
}
```

#### 전체 데이터 조회 (limit=0)
```json
{
  "total_count": 150,
  "page": 1,
  "limit": 150,
  "items": [
    // ... 전체 150개의 리뷰 데이터
  ]
}
```

### **응답 필드**

| 필드 | 타입 | 설명 |
|------|------|------|
| `total_count` | integer | 전체 리뷰 개수 (필터 적용 후) |
| `page` | integer | 현재 페이지 번호<br>(limit=0일 때는 1로 고정) |
| `limit` | integer | 페이지당 개수<br>(limit=0일 때는 실제 반환된 개수) |
| `items` | array | 리뷰 목록 |
| `items[].review_id` | integer | 리뷰 ID |
| `items[].writer` | string | 작성자명 |
| `items[].rating` | integer | 별점 (1~5) |
| `items[].sentiment` | string | 감성 분석 결과<br>- "긍정": 4~5점<br>- "중립": 3점<br>- "부정": 1~2점 |
| `items[].content` | string | 리뷰 내용 |
| `items[].created_date` | string | 작성일 |
| `items[].product_no` | integer | 상품 번호 |

---

## 📌 주요 변경 사항 (2025-01-05)

### ✅ `limit=0` 전체 조회 기능 추가

**변경 전:**
- `limit` 최소값: 1
- 전체 데이터 조회 불가능

**변경 후:**
- `limit` 최소값: **0**
- `limit=0`일 때 전체 데이터 반환 (최대 10,000개 제한)
- `page`는 자동으로 1로 설정됨

### 사용 예시 (프론트엔드)

```typescript
// TypeScript - 전체 리뷰 데이터 조회
async function fetchAllReviews(rating?: number) {
  const params = new URLSearchParams({
    limit: '0',  // 전체 조회
    ...(rating && { rating: String(rating) })
  });
  
  const response = await fetch(
    `/api/v1/review-analysis/list?${params.toString()}`
  );
  
  const data = await response.json();
  
  console.log(`총 ${data.total_count}개 중 ${data.items.length}개 로드됨`);
  return data.items;
}

// 사용법
const allReviews = await fetchAllReviews();  // 전체 리뷰
const fiveStarReviews = await fetchAllReviews(5);  // 별점 5점 리뷰만
```

---

## 🔍 참고 사항

### 정렬 기준
- 모든 리뷰는 **작성일 기준 최신순**으로 정렬됩니다.

### 별점 기준
- **긍정**: 별점 4~5점
- **중립**: 별점 3점
- **부정**: 별점 1~2점

### 성능 고려사항
- `limit=0` 사용 시 데이터가 많으면 응답 시간이 길어질 수 있습니다.
- 최대 10,000개 제한이 적용됩니다.
- 프론트엔드에서 적절한 로딩 UI를 제공하는 것을 권장합니다.

---

## 📞 문의

API 관련 문의사항이 있으시면 백엔드 개발팀에 연락주세요.



