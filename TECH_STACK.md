# 기술 스택 정의서 (TECH_STACK)

본 문서는 본 프로젝트에서 사용한 기술 스택과,  
각 기술을 선택한 이유 및 역할을 명확히 정의한다.

---

## 1. 전체 기술 스택 개요

| 구분 | 기술 | 버전 | 사용 목적 |
|------|------|------|-----------|
| Frontend | Vue.js | 3.x | 사용자 인터페이스 구현 |
| Frontend | JavaScript | ES6+ | 클라이언트 로직 처리 |
| Frontend | Axios | 최신 | 백엔드 API 통신 |
| Backend | Django | 4.x | REST API 서버 |
| Backend | Django REST Framework | 최신 | API 개발 |
| Database | SQLite | 3 | 개발용 DB |
| External API | DART Open API | - | 기업 데이터 수집 |
| Version Control | Git / GitHub | - | 형상 관리 |
| Environment | django-environ | - | 환경 변수 관리 |

---

## 2. Frontend 기술 스택

### 2-1. Vue.js 3
- **선정 이유**
  - 컴포넌트 기반 구조로 UI 재사용 용이
  - SPA에 최적화된 반응성 시스템
  - Composition API를 통해 로직 분리 가능
- **프로젝트 내 역할**
  - 기업 목록, 기업 상세 페이지 UI 구현
  - 사용자 로그인 후 대시보드 화면 처리
  - 즐겨찾기, 최근 본 기업 Floating UI 구현

---

### 2-2. JavaScript (ES6+)
- **선정 이유**
  - 브라우저 기본 언어
  - 비동기 처리(Promise, async/await)에 유리
- **프로젝트 내 역할**
  - 사용자 이벤트 처리
  - API 통신 로직 처리
  - 데이터 가공 및 상태 관리

---

### 2-3. Axios
- **선정 이유**
  - HTTP 통신을 간단하게 처리 가능
  - 요청 / 응답 인터셉터 제공
- **프로젝트 내 역할**
  - Django REST API와 데이터 통신
  - 인증 토큰(JWT) 자동 첨부 처리

---

## 3. Backend 기술 스택

### 3-1. Django
- **선정 이유**
  - Python 기반의 빠른 개발 생산성
  - ORM 제공으로 DB 접근 용이
  - 보안 기능(CSRF, 인증) 기본 제공
- **프로젝트 내 역할**
  - 사용자 인증 처리
  - 기업 정보 관리
  - 게시글, 댓글 CRUD 처리

---

### 3-2. Django REST Framework
- **선정 이유**
  - REST API 표준 구조 제공
  - Serializer 기반 데이터 검증
- **프로젝트 내 역할**
  - 로그인 API, 기업 API, 게시판 API 제공

---

## 4. Database

### 4-1. SQLite
- **선정 이유**
  - 별도 설치 없이 빠른 테스트 가능
- **프로젝트 내 역할**
  - DB

---

## 5. External API

### 5-1. DART Open API
- **선정 이유**
  - 금융감독원에서 제공하는 공식 기업 공시 API
  - 신뢰도 높은 기업 데이터 제공
- **프로젝트 내 역할**
  - 기업 기본 정보 수집
  - 재무 데이터 수집 및 저장

---

## 6. 개발 및 배포 환경

### 6-1. Git / GitHub
- **선정 이유**
  - 분산 버전 관리
  - Pull Request 기반 협업 가능
- **프로젝트 내 역할**
  - 소스코드 형상 관리
  - 코드 리뷰 및 협업

---

## 7. 환경 변수 관리

### 7-1. django-environ
- **선정 이유**
  - 민감한 정보(API Key, Secret Key) 보호
  - 로컬/운영 환경 설정 분리
- **프로젝트 내 역할**
  - DART API Key 관리
  - DB 계정 정보 관리

---

## 8. 기술 스택 선정 요약

| 항목 | 핵심 이유 |
|------|-----------|
Vue | 빠른 SPA UI 구성 |
Django | 안정적인 백엔드 API 구축 |
DART API | 신뢰도 높은 기업 데이터 |

---

## 9. 향후 기술 확장 계획 (선택)

- Redis : 캐싱 및 인증 세션 관리
- Celery : 비동기 크롤링 및 데이터 수집
- ElasticSearch : 기업 검색 고속화
- AWS S3 : 이미지 파일 저장소
