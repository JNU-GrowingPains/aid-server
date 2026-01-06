# 고객 분석 API - 전체 데이터 조회 가이드

## 개요

고객 분석 API에 전체 데이터 조회 기능이 추가되었습니다.

### 주요 변경사항
- `limit=0` 설정 시 **전체 데이터 반환**
- 안전장치: 최대 **10,000개 제한**
- 기존 페이지네이션 방식과 호환

---

## 사용 방법

### 1. 전체 데이터 조회

**엔드포인트:** `GET /api/v1/member-analysis/members`

**요청 예시:**
```http
GET /api/v1/member-analysis/members?limit=0
Authorization: Bearer {access_token}
```

**응답:**
```json
{
  "members": [
    {
      "user_id": 123,
      "member_id": "user123",
      "name": "홍길동",
      "grade": "VIP",
      "purchase_count": 25,
      "first_purchase": "2025-01-15",
      "last_purchase": "2026-01-03",
      "available_points": 50000
    }
    // ... 최대 10,000개
  ],
  "total_count": 500,
  "page": 1,
  "limit": 500,  // 실제 반환된 개수
  "total_pages": 1
}
```

---

### 2. 전체 데이터 + 필터링

**VIP 등급 전체 조회:**
```http
GET /api/v1/member-analysis/members?limit=0&grade=VIP
Authorization: Bearer {access_token}
```

**포인트 높은 순 전체 조회:**
```http
GET /api/v1/member-analysis/members?limit=0&sort_by=points&order=desc
Authorization: Bearer {access_token}
```

---

### 3. 기존 페이지네이션 (변경 없음)

```http
GET /api/v1/member-analysis/members?page=1&limit=20
Authorization: Bearer {access_token}
```

---

## JavaScript 사용 예시

### 전체 데이터 조회

```javascript
async function getAllMembers(accessToken) {
  const response = await fetch(
    'https://api.example.com/api/v1/member-analysis/members?limit=0',
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  
  console.log(`전체 고객 수: ${data.total_count}`);
  console.log(`실제 반환된 수: ${data.members.length}`);
  
  if (data.total_count > 10000) {
    console.warn('⚠️ 전체 데이터가 10,000개를 초과하여 일부만 반환됩니다.');
  }
  
  return data;
}

// 사용
try {
  const allMembers = await getAllMembers('your_access_token');
  allMembers.members.forEach(member => {
    console.log(`${member.name} (${member.grade}) - ${member.available_points}P`);
  });
} catch (error) {
  console.error('에러:', error);
}
```

### VIP 고객 전체 조회

```javascript
async function getAllVIPMembers(accessToken) {
  const url = new URL('https://api.example.com/api/v1/member-analysis/members');
  url.searchParams.append('limit', '0');
  url.searchParams.append('grade', 'VIP');
  url.searchParams.append('sort_by', 'points');
  url.searchParams.append('order', 'desc');
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  
  return {
    vipMembers: data.members,
    totalVIP: data.total_count
  };
}
```

---

## Python 사용 예시

```python
import requests

def get_all_members(access_token, grade=None):
    """전체 고객 데이터 조회"""
    url = 'https://api.example.com/api/v1/member-analysis/members'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    params = {
        'limit': 0,
        'sort_by': 'points',
        'order': 'desc'
    }
    
    if grade:
        params['grade'] = grade
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    # 10,000개 제한 경고
    if data['total_count'] > 10000:
        print(f"⚠️ 경고: 전체 {data['total_count']}명 중 10,000명만 반환됩니다.")
    
    return data

# 사용 예시
try:
    # 전체 고객 조회
    all_members = get_all_members('your_access_token')
    print(f"전체 고객 수: {all_members['total_count']}")
    
    # VIP 고객만 조회
    vip_members = get_all_members('your_access_token', grade='VIP')
    print(f"VIP 고객 수: {vip_members['total_count']}")
    
    # 데이터 처리
    for member in all_members['members']:
        print(f"{member['name']} ({member['grade']}) - {member['available_points']}P")
        
except requests.exceptions.HTTPError as e:
    print(f"에러 발생: {e}")
```

---

## React 컴포넌트 예시

```typescript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Member {
  user_id: number;
  member_id: string;
  name: string;
  grade: string;
  purchase_count: number;
  first_purchase: string | null;
  last_purchase: string | null;
  available_points: number;
}

const AllMembersComponent: React.FC = () => {
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [warning, setWarning] = useState<string | null>(null);

  useEffect(() => {
    const fetchAllMembers = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get(
          'https://api.example.com/api/v1/member-analysis/members',
          {
            headers: {
              'Authorization': `Bearer ${token}`
            },
            params: {
              limit: 0,
              sort_by: 'points',
              order: 'desc'
            }
          }
        );
        
        const data = response.data;
        setMembers(data.members);
        setTotalCount(data.total_count);
        
        // 10,000개 제한 경고
        if (data.total_count > 10000) {
          setWarning(`전체 ${data.total_count}명 중 10,000명만 표시됩니다.`);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('데이터 로드 실패:', error);
        setLoading(false);
      }
    };

    fetchAllMembers();
  }, []);

  if (loading) return <div>로딩 중...</div>;

  return (
    <div className="all-members-container">
      <h2>전체 고객 목록 ({totalCount}명)</h2>
      
      {warning && (
        <div className="warning-banner">
          ⚠️ {warning}
        </div>
      )}
      
      <table className="members-table">
        <thead>
          <tr>
            <th>고객명</th>
            <th>등급</th>
            <th>구매횟수</th>
            <th>포인트</th>
            <th>최근 구매일</th>
          </tr>
        </thead>
        <tbody>
          {members.map((member) => (
            <tr key={member.user_id}>
              <td>{member.name}</td>
              <td>{member.grade}</td>
              <td>{member.purchase_count}회</td>
              <td>{member.available_points.toLocaleString()}P</td>
              <td>{member.last_purchase || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AllMembersComponent;
```

---

## 주의사항

### 1. 성능 고려사항

- **응답 시간**: 데이터가 많을수록 응답 시간이 길어집니다
- **메모리 사용**: 클라이언트에서 많은 메모리를 사용할 수 있습니다
- **네트워크**: 페이로드 크기가 커집니다

### 2. 10,000개 제한

```javascript
// 10,000개 초과 시 처리 예시
async function fetchAllMembersWithPagination(accessToken) {
  // 먼저 전체 조회 시도
  const response = await fetch(
    'https://api.example.com/api/v1/member-analysis/members?limit=0',
    {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    }
  );
  
  const data = await response.json();
  
  // 10,000개 초과 시 페이지네이션으로 전환
  if (data.total_count > 10000) {
    console.warn('데이터가 10,000개를 초과합니다. 페이지네이션을 사용하세요.');
    return await fetchAllWithPagination(accessToken, data.total_count);
  }
  
  return data.members;
}

async function fetchAllWithPagination(accessToken, totalCount) {
  const limit = 100;
  const totalPages = Math.ceil(totalCount / limit);
  const allMembers = [];
  
  for (let page = 1; page <= totalPages; page++) {
    const response = await fetch(
      `https://api.example.com/api/v1/member-analysis/members?page=${page}&limit=${limit}`,
      {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      }
    );
    const data = await response.json();
    allMembers.push(...data.members);
  }
  
  return allMembers;
}
```

### 3. 권장 사용 시나리오

**✅ 적합한 경우:**
- 고객 수가 10,000명 이하인 경우
- CSV/Excel 내보내기 기능
- 일회성 데이터 분석
- 등급별 필터링으로 범위를 좁힌 경우

**❌ 부적합한 경우:**
- 실시간 대시보드 (페이지네이션 권장)
- 고객 수가 10,000명을 초과하는 경우
- 빈번한 조회가 필요한 경우

---

## 에러 처리

### 타임아웃 처리

```javascript
async function getAllMembersWithTimeout(accessToken, timeoutMs = 30000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    const response = await fetch(
      'https://api.example.com/api/v1/member-analysis/members?limit=0',
      {
        headers: { 'Authorization': `Bearer ${accessToken}` },
        signal: controller.signal
      }
    );
    
    clearTimeout(timeoutId);
    return await response.json();
    
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('요청 타임아웃: 페이지네이션을 사용하세요.');
      // 페이지네이션으로 폴백
      return await getMembersWithPagination(accessToken);
    }
    throw error;
  }
}
```

### 재시도 로직

```javascript
async function getAllMembersWithRetry(accessToken, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(
        'https://api.example.com/api/v1/member-analysis/members?limit=0',
        {
          headers: { 'Authorization': `Bearer ${accessToken}` }
        }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
      
    } catch (error) {
      console.warn(`시도 ${i + 1}/${maxRetries} 실패:`, error);
      
      if (i === maxRetries - 1) {
        throw error;
      }
      
      // 지수 백오프
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
}
```

---

## 파라미터 참조

| 파라미터 | 타입 | 기본값 | 범위 | 설명 |
|---------|------|--------|------|------|
| `limit` | integer | 20 | **0~100** | **0 = 전체 조회** (최대 10,000개) |
| `page` | integer | 1 | ≥1 | 페이지 번호 (limit=0 시 무시됨) |
| `grade` | string | null | - | 등급 필터 |
| `sort_by` | string | latest_purchase | - | 정렬 기준 |
| `order` | string | desc | desc, asc | 정렬 순서 |
| `site_id` | integer | 1 | - | 사이트 ID |

---

## FAQ

### Q1. 10,000개 이상의 데이터를 조회하려면?

**A:** 페이지네이션을 사용하거나, 필터링으로 범위를 좁히세요.

```javascript
// 방법 1: 페이지네이션
const page1 = await fetch('...?page=1&limit=100');
const page2 = await fetch('...?page=2&limit=100');

// 방법 2: 등급별 필터링
const vipMembers = await fetch('...?limit=0&grade=VIP');
const goldMembers = await fetch('...?limit=0&grade=GOLD');
```

### Q2. limit=0과 limit=10000의 차이는?

**A:**
- `limit=0`: 전체 데이터 (최대 10,000개 제한)
- `limit=10000`: 범위 초과 에러 (최대 100)

### Q3. 응답이 너무 느린데요?

**A:** 다음을 시도해보세요:
1. 등급 필터링으로 범위 축소
2. 페이지네이션 사용
3. 서버 성능 확인
4. 네트워크 상태 확인

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|-----|------|----------|
| 1.0 | 2026-01-05 | 전체 데이터 조회 기능 추가 (limit=0) |

---

**© 2026 AID-SERVER. All rights reserved.**


