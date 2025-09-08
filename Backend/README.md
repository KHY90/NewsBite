# NewsBite Backend API

뉴스한입 백엔드 API 서버

## 기술 스택

- **Framework**: FastAPI
- **Database**: PostgreSQL + pgvector
- **Authentication**: Supabase
- **ORM**: SQLAlchemy + Alembic
- **Cache**: Redis
- **AI/ML**: OpenAI, Google Gemini
- **Web Scraping**: Playwright, Selenium

## 개발 환경 설정

### 1. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값들을 설정
```

### 2. Docker로 개발 환경 실행

```bash
# 프로젝트 루트에서
docker-compose up -d
```

### 3. 로컬 개발 환경 설정

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head

# 개발 서버 실행
uvicorn app.main:app --reload
```

## API 문서

개발 서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
app/
├── api/           # API 엔드포인트
├── core/          # 핵심 설정 (DB, config 등)
├── models/        # SQLAlchemy 모델
├── schemas/       # Pydantic 스키마
├── services/      # 비즈니스 로직
├── utils/         # 유틸리티 함수
└── main.py        # FastAPI 앱 엔트리포인트
```

## 데이터베이스

PostgreSQL + pgvector 확장을 사용하여 뉴스 임베딩 기반 유사도 검색을 지원합니다.

### 마이그레이션

```bash
# 새 마이그레이션 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

## 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=app

# 특정 테스트 파일 실행
pytest tests/test_auth.py
```

## 코드 품질

```bash
# 코드 포매팅
black app/
isort app/

# 린팅
flake8 app/

# 타입 체킹
mypy app/
```