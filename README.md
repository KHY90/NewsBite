# 🗞️ NewsBite (뉴스한입)

**매일 저녁 7시, 당신만을 위한 개인 맞춤 뉴스 요약 서비스**

## 📋 프로젝트 개요

NewsBite는 사용자의 관심 분야에 따라 매일 주요 뉴스를 AI로 요약하여 이메일로 제공하는 개인화된 뉴스 서비스입니다.

### 🎯 핵심 기능
- 🔐 **구글 소셜 로그인** (Supabase 인증)
- 📊 **개인 맞춤 카테고리** 선택 (정치, 경제, 과학, 사회 등)
- 🏢 **관심 기업** 뉴스 추적 및 감정 분석
- 🤖 **AI 자동 요약** 및 찬반 정리 (중립적 관점)
- 📧 **개인화 이메일** 발송 (매일 19:00)
- 🧩 **뉴스 퀴즈** 기능

## 🏗️ 프로젝트 구조

```
NewsBite/
├── Frontend/          # React + TypeScript 클라이언트
├── Backend/           # FastAPI 서버
├── docker-compose.yml # 개발 환경 설정
├── .gitignore
└── README.md
```

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy + Alembic
- **Authentication**: Supabase
- **AI/ML**: OpenAI API, Gemini API, HuggingFace
- **Crawling**: Playwright, Selenium
- **Container**: Docker

### Frontend
- **Framework**: React.js + TypeScript
- **Styling**: Tailwind CSS
- **Build**: Vite
- **Deployment**: Vercel

### DevOps
- **Container**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Cloud**: AWS (Lambda, EC2, Secret Manager)

## 🚀 빠른 시작

### 전제 조건
- Node.js 18+ 
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/NewsBite.git
cd NewsBite
```

### 2. 환경 설정
```bash
# Backend 환경 설정
cd Backend
cp .env.example .env
# .env 파일 편집 - API 키와 데이터베이스 설정 추가

# Frontend 환경 설정  
cd ../Frontend
cp .env.example .env.local
# .env.local 파일 편집 - Supabase 설정 추가
```

⚠️ **보안 주의사항**: 
- `.env` 파일에는 실제 API 키를 입력하세요
- 이 파일들은 .gitignore에 포함되어 커밋되지 않습니다
- 프로덕션 환경에서는 환경변수나 보안 관리 서비스를 사용하세요

### 3. Docker로 실행
```bash
# 루트 디렉토리에서
docker-compose up -d
```

### 4. 개발 모드 실행
```bash
# Backend (Terminal 1)
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (Terminal 2)
cd Frontend  
npm install
npm run dev
```

## 📖 API 문서

개발 서버 실행 후 다음 URL에서 확인 가능:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔄 워크플로우

1. **뉴스 수집**: 매일 18:00-18:30 자동 크롤링
2. **AI 처리**: 요약, 감정분석, 찬반정리
3. **개인화**: 사용자별 관심사 필터링  
4. **발송**: 19:00 개인화된 이메일 전송

## 📋 개발 로드맵

- [x] 프로젝트 구조 설계
- [ ] Backend API 개발
- [ ] Frontend UI 구현
- [ ] 뉴스 크롤링 시스템
- [ ] AI 요약 파이프라인
- [ ] 이메일 발송 시스템
- [ ] 관리자 대시보드
- [ ] 배포 및 운영

## 🤝 기여하기

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 연락처

- **개발자**: 김화연
- **이메일**: power4206@gmail.com
- **프로젝트 링크**: [https://github.com/your-username/NewsBite](https://github.com/your-username/NewsBite)

## 🙏 감사의 말

- [FastAPI](https://fastapi.tiangolo.com/) - 웹 프레임워크
- [React](https://reactjs.org/) - UI 라이브러리
- [Supabase](https://supabase.com/) - 인증 서비스
- [OpenAI](https://openai.com/) - AI 모델 API
- [Playwright](https://playwright.dev/) - 웹 크롤링

---

**⭐ 이 프로젝트가 도움이 되었다면 별표를 눌러주세요!**