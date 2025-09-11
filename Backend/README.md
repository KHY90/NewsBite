# NewsBite Backend API

NewsBite 프로젝트의 FastAPI 기반 백엔드 API 서버입니다.

## 🚀 주요 역할
- 사용자 인증 및 관리
- 뉴스 기사 크롤링, AI 요약 및 분석
- 개인화된 뉴스 콘텐츠 제공
- 데이터베이스 관리 및 API 엔드포인트 제공

## 🛠️ 기술 스택
- **Framework**: FastAPI
- **Database**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy
- **DB Migration**: Alembic
- **Authentication**: Supabase
- **AI/ML**: OpenAI API, Gemini API
- **Web Scraping**: Playwright, Selenium
- **Container**: Docker

## ⚙️ 개발 환경 설정

### 1. 환경 변수

프로젝트 루트의 `.env.example` 파일을 복사하여 `.env` 파일을 생성하고, API 키 및 데이터베이스 접속 정보 등 필요한 값들을 설정합니다.

```bash
cp .env.example .env
```

### 2. 의존성 설치

가상환경을 설정한 후, `requirements.txt` 파일을 이용해 필요한 라이브러리를 설치합니다.

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 데이터베이스 마이그레이션

Alembic을 사용하여 데이터베이스 스키마를 최신 상태로 업데이트합니다.

```bash
alembic upgrade head
```

### 4. 개발 서버 실행

Uvicorn을 사용하여 FastAPI 개발 서버를 실행합니다.

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 API 문서

개발 서버 실행 후, 아래 URL에서 API 문서를 확인할 수 있습니다.

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🏗️ 프로젝트 구조

```
app/
├── api/           # API 라우터 및 엔드포인트
├── core/          # 핵심 설정 (DB, CORS, Pydantic Settings 등)
├── models/        # SQLAlchemy DB 모델
├── schemas/       # Pydantic 데이터 검증 스키마
├── services/      # 크롤링, AI 처리 등 비즈니스 로직
├── utils/         # 인증 헬퍼 등 유틸리티 함수
└── main.py        # FastAPI 애플리케이션 생성 및 메인 진입점
```

## ✅ 테스트

`pytest`를 사용하여 테스트를 실행합니다.

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_crawler.py
```
