## SSAFY 14th ESG Project

TEAM 오피셜키무단디즘

사용자의 관심 분야/성향/스펙(입력 데이터)과 기업 데이터를 기반으로 기업을 추천하고, 기업별 커뮤니티(게시글/댓글)를 제공하는 취업 지원 서비스입니다.

---

## 핵심 기능

- 인증/계정
  - 회원가입/로그인 (dj-rest-auth)
  - 소셜 로그인(Google)
  - 프로필(아바타 업로드), 비밀번호 변경
- 기업
  - 기업 검색(서버사이드 검색 지원)
  - 기업 상세(기업 프로필 요약/지역/규모/산업 등)
  - 즐겨찾기(내 즐겨찾기 목록)
  - 기업 댓글/좋아요
  - 추천(조건 기반 추천 + GPT 기반 추천 엔드포인트)
- 게시판
  - 게시글/댓글 CRUD
  - 좋아요 토글
  - 내가 작성한 글/댓글 목록
- 데이터 수집/정규화
  - DART Open API 기반 기업/프로필 데이터 수집
  - 대용량 배치/백필(backfill) 커맨드 제공

---

## 아키텍처

```text
[ 사용자 브라우저 ]
        ↓
[ Vue 3 (Vite) Frontend ]
        ↓ (Axios / REST API)
[ Django + DRF Backend ]
        ↓ (ORM)
[ SQLite (dev) ]
        ↓
[ DART Open API ]
```

---

## 기술 스택

- Frontend: Vue 3, Vite, Pinia, Vue Router, TailwindCSS, Axios
- Backend: Django, Django REST Framework, dj-rest-auth, django-allauth
- DB: SQLite (개발용)
- External: DART Open API

---

## 로컬 실행 방법

### 0) 사전 준비

- Node.js: `package.json`의 `engines.node` 범위(예: Node 20+ 권장)
- Python: 가상환경(venv) 사용 권장

### 1) Backend (Django)

1. 가상환경 생성/활성화

- Windows (PowerShell)
  - `cd back`
  - `python -m venv venv`
  - `venv\Scripts\Activate.ps1`

- macOS/Linux
  - `cd back`
  - `python3 -m venv venv`
  - `source venv/bin/activate`

2. 의존성 설치

- `pip install -r requirements.txt`

3. 환경변수 설정

- `back/.env` 또는 프로젝트 루트 `.env`에 설정합니다. (둘 다 로드됨)
- ⚠️ `.env` 파일에는 API Key 등 민감정보가 포함되므로 Git에 커밋하지 않습니다.

필수/선택 키:

- `DART_API_KEY` (기업 데이터 수집 시 필요)
- `OPENAI_API_KEY` (GPT 추천/분석 기능 사용 시 필요)

예시(`back/.env`):

```env
DART_API_KEY=YOUR_DART_KEY
OPENAI_API_KEY=YOUR_OPENAI_KEY
```

참고:

- 현재 개발 설정은 `DEBUG=True`로 동작합니다.
- 운영/배포 환경에서는 `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` 등을 환경변수로 분리하는 것을 권장합니다.

4. 마이그레이션

- `python manage.py migrate`

5. 초기 데이터 로드 (필수)

이 프로젝트는 아래 fixture 로딩이 **필수**입니다.

- `department.json`
- `company.json`
- `companyprofile.json`

권장 로딩 순서:

```bash
python manage.py loaddata department.json
python manage.py loaddata company.json
python manage.py loaddata companyprofile.json
```

한 번에 로딩하려면:

```bash
python manage.py loaddata department.json company.json companyprofile.json
```

참고:

- `companyprofile.json`은 용량이 매우 클 수 있습니다. (로딩에 시간이 걸릴 수 있음)
- 인코딩 문제(UTF-8 아님)로 로딩이 실패한다면, UTF-8로 변환 후 다시 시도하세요.

6. 서버 실행

- `python manage.py runserver`

기본 주소: http://127.0.0.1:8000

### 2) Frontend (Vue)

1. 설치/실행

- `cd front`
- `npm install`
- `npm run dev`

기본 주소: http://127.0.0.1:5173

---

## 주요 API 엔드포인트

Backend base URL: `http://127.0.0.1:8000`

### Accounts

- `POST /accounts/login/`
- `POST /accounts/logout/`
- `POST /accounts/registration/` (회원가입)
- `POST /accounts/google/` (소셜 로그인)
- `POST /accounts/password/change/custom/`
- `POST /accounts/user/avatar/`
- `POST /accounts/withdraw/`

### Articles

prefix: `/api/v1/articles/`

- `GET /api/v1/articles/` (목록)
- `POST /api/v1/articles/` (작성)
- `GET /api/v1/articles/<article_pk>/` (상세)
- `PUT /api/v1/articles/<article_pk>/` (수정)
- `DELETE /api/v1/articles/<article_pk>/` (삭제)
- `POST /api/v1/articles/<article_pk>/like/` (좋아요 토글)
- `GET /api/v1/articles/me/` (내가 작성한 글)
- `GET /api/v1/articles/me/comments/` (내가 작성한 댓글)

### Companies

prefix: `/companies/`

- `GET /companies/api/list/?q=<query>&limit=<n>` (기업 리스트/검색)
- `GET /companies/api/companyprofile/summary/?company_id=<id>` (기업 프로필 요약)
- `POST /companies/api/<company_pk>/favorite/` (즐겨찾기 토글)
- `GET /companies/api/myfavorites/` (내 즐겨찾기)

추천:

- `POST /companies/api/recommend/` (조건 기반 추천)
- `POST /companies/api/gpt_recommend/` (GPT 기반 추천)

---

## 데이터 수집/배치 커맨드

대량 데이터 수집/정규화는 [commands.txt](commands.txt) 기준으로 운영합니다.

예시:

- CompanyProfile 대량 업데이트
  - `python manage.py update_profiles_bulk --confirm --start 0 --limit 30000 --sleep 0.1`

- 특정 키워드 기업 프로필 수집(DART)
  - `python manage.py fetch_dart_profiles_by_keyword --keyword 삼성 --limit 270 --refresh --sleep 0.15 --log-every 5`

---

## Troubleshooting

- `DEFAULT_AUTO_FIELD` 관련 에러는 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 참고
- Pinia 토큰 영속화가 안 되면 `pinia-plugin-persistedstate` 설정 확인
- `companyprofile.json` 등 대용량 JSON은 인코딩/용량 이슈가 있을 수 있음

---

## 소셜 로그인 (Google)

현재 구현된 소셜 로그인은 Google만 지원합니다.

백엔드 `dj-rest-auth + django-allauth` 기반으로 소셜 로그인 엔드포인트를 제공합니다.

개발용 최소 흐름:

- 프론트 `/login`에서 Google OAuth로 `access_token`을 획득
- `POST /accounts/google/`에 `{ "access_token": "..." }`로 전달
- 백엔드가 DRF Token(`key`)를 반환 → 이후 일반 로그인과 동일하게 동작

필수 설정

1) Django admin에서 SocialApp 등록

- `http://127.0.0.1:8000/admin/` 접속
- Social applications 에서 Provider = Google 선택
- Client id / Secret 입력
- Sites에 현재 Site(보통 id=1) 연결

2) 프론트 env 설정

- `front/.env.example`를 참고해서 `front/.env.local`을 생성하세요. (Vite는 재시작 필요)

```env
VITE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
```

3) Google Console Redirect URI

- Redirect URI에 `http://127.0.0.1:5173/login` 등록

참고

- 현재 프론트 구현은 개발 편의상 `access_token`을 해시(`#`)로 받는 흐름(implicit flow)입니다.
- 운영 환경에서는 authorization code + PKCE(또는 서버 사이드 code 교환)로 전환을 권장합니다.

---

## 협업 규칙

- 브랜치/커밋 규칙은 [GIT_WORKFLOW.md](GIT_WORKFLOW.md) 참고

