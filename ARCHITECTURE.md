# 시스템 아키텍처 정의서 (ARCHITECTURE)

SSAFY 관통 프로젝트  
TEAM 오피셜키무단디즘

---

## 1. 문서 목적

본 문서는 프로젝트의 전체 시스템 구조와  
클라이언트–서버–데이터베이스–외부 API 간의 관계를 정의한다.  
개발자 간 공통된 설계 이해를 목적으로 한다.

---

## 2. 전체 시스템 구성도

```text
[ 사용자 브라우저 ]
        ↓
[ Vue 3 Frontend ]
        ↓ (Axios / REST API)
[ Django REST Server ]
        ↓ (ORM)
[ Database (SQLite) ]
        ↓
[ DART Open API ]

```

## 3. 세부 페이지 구성도
Vue frontend component
src/
  components/
    CompanyList.vue
    CompanyDetail.vue
    SearchBox.vue
    ArticleList.vue
    ArticleDetail.vue
    CommentList.vue
    LoginForm.vue

  pages/
    HomePage.vue
    RecommendPage.vue
    CompanyPage.vue
    ArticlePage.vue

  store/
    user.js
    company.js
    article.js

  api/
    axios.js
    companyApi.js
    articleApi.js
    authApi.js
```
