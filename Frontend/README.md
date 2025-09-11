# NewsBite Frontend

NewsBite 프로젝트의 React 기반 프론트엔드 애플리케이션입니다.

## 🚀 주요 역할
- 사용자 로그인 및 회원가입 UI
- 뉴스 카테고리 및 관심사 설정 페이지
- 개인화된 뉴스 대시보드
- 백엔드 API와의 통신

## 🛠️ 기술 스택
- **Framework**: React.js (with TypeScript)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context
- **Authentication**: Supabase Client
- **HTTP Client**: Axios

## ⚙️ 개발 환경 설정

### 1. 환경 변수

`.env.example` 파일을 복사하여 `.env.local` 파일을 생성하고, Supabase 연동에 필요한 환경 변수를 설정합니다.

```bash
cp .env.example .env.local
```

### 2. 의존성 설치

`npm`을 사용하여 필요한 라이브러리를 설치합니다.

```bash
npm install
```

### 3. 개발 서버 실행

Vite 개발 서버를 실행합니다.

```bash
npm run dev
```

서버가 시작되면 [http://localhost:3000](http://localhost:3000)에서 애플리케이션을 확인할 수 있습니다.

## 🏗️ 프로젝트 구조

```
src/
├── components/    # 재사용 가능한 UI 컴포넌트
├── config/        # 설정 파일 (e.g., Supabase 클라이언트)
├── contexts/      # React Context (e.g., AuthContext)
├── pages/         # 라우팅 단위의 페이지 컴포넌트
├── types/         # TypeScript 타입 정의
├── App.tsx        # 메인 애플리케이션 컴포넌트
└── index.tsx      # 애플리케이션 진입점
```

## 📦 빌드

프로덕션용으로 애플리케이션을 빌드하려면 다음 명령어를 실행합니다. 빌드 결과물은 `dist/` 디렉토리에 생성됩니다.

```bash
npm run build
```
