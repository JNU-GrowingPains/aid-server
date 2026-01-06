# 🚀 AID-SERVER

이커머스 분석 플랫폼을 위한 FastAPI 백엔드 서버

## 📋 주요 기능

### 🔐 인증 시스템
- 회원가입 / 로그인 / 로그아웃
- JWT 토큰 기반 인증
- Refresh 토큰 지원

### 📊 대시보드 분석
- **상품 분석**: 인기 상품, 판매 트렌드
- **고객 분석**: 고객 등급별 분포, 고객 목록
- **리뷰 분석**: 리뷰 통계, 키워드 분석
- **재구매 분석**: 재구매율, 재구매 고객 분석
- **개인정보 관리**: 프로필 조회/수정, 통계 정보

### 🏗️ 아키텍처

```
[Client Request]
       ↓
[Router] ← JWT 인증
   └─ db = Depends(get_db)
       ↓
[Service] ← 비즈니스 로직
       ↓
[Repository] ← 데이터베이스 쿼리
       ↓
[Models] ← SQLAlchemy ORM
       ↓
[AWS RDS MySQL]
```

## 🚀 빠른 시작

### 1. 자동 설치 및 실행 (권장)

**Windows:**
```bash
install_and_run.bat
```

**Linux/Mac:**
```bash
python install_and_run.py
```

### 2. 수동 설치

```bash
# 패키지 설치
pip install -r requirements.txt

# 서버 실행
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 환경 설정

`.env` 파일 생성:
```env
DATABASE_URL=mysql+aiomysql://username:password@host:port/database
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=14
```

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서 확인:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗂️ 프로젝트 구조

```
aid-server/
├── config/           # 설정 파일
├── database/         # 데이터베이스 연결
├── models/           # SQLAlchemy 모델
├── schemas/          # Pydantic 스키마
├── repositories/     # 데이터베이스 쿼리
├── services/         # 비즈니스 로직
├── routers/          # API 엔드포인트
├── main.py           # FastAPI 앱
└── requirements.txt  # 의존성 패키지
```

## 🌐 API 엔드포인트

### 인증 API
- `POST /auth/register` - 회원가입
- `POST /auth/login` - 로그인
- `POST /auth/refresh` - 토큰 재발급
- `POST /auth/logout` - 로그아웃

### 대시보드 API
- `GET /api/v1/product-analysis/*` - 상품 분석
- `GET /api/v1/member-analysis/*` - 고객 분석 (**전체 데이터 조회 지원**: `limit=0`)
- `GET /api/v1/review-analysis/*` - 리뷰 분석
- `GET /api/v1/repurchase-analysis/*` - 재구매 분석
- `GET /api/v1/management/*` - 개인정보 관리

#### 고객 분석 주요 기능
- **등급별 통계**: 고객 등급(VIP, PLATINUM, GOLD 등) 분포 분석
- **상위 고객**: 포인트 기준 상위 고객 조회
- **고객 리스트**: 페이지네이션 & 전체 데이터 조회 (최대 10,000개)
  - `limit=0` 설정 시 전체 데이터 반환
  - 등급 필터링, 정렬 지원

📖 **상세 문서**: [고객 분석 API 전체 조회 가이드](docs/MEMBER_API_FULL_DATA.md)

## 🛠️ 기술 스택

- **Framework**: FastAPI 0.104.1
- **Database**: MySQL (AWS RDS)
- **ORM**: SQLAlchemy 2.0.23
- **Authentication**: JWT (python-jose)
- **Data Analysis**: pandas, numpy
- **Korean NLP**: konlpy

