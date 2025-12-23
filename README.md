# 관통 PJT - TEAM_오피셜키무단디즘

## 주제
- 사용자의 관심분야, 스펙 및 성향에 맞춘 기업 **추천** 시스템


## Web
- 기본적으로 Bootstrap을 활용하여 css 구현할 것
- BASE_DIR를 'templates'로 설정하고 기본 템플릿들을 만들어 이를 활용해 재사용성이 높도록 구현할 것
- 한국 취준생, 이직자들을 대상으로 서비스하는 웹사이트로 한국어를 기본 언어로 구성할 것


## dataset
- 전자공시시스템 api
https://wikidocs.net/230304
https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019002


## ERD
- erdcloud
https://www.erdcloud.com/


## 구현할 것(Todos)
- AI chatbot
  - 토크나이저 - 대화기억
  - RAG
- 게시판


## env, gitignore
- 환경변수 .env파일에 저장 후 사용할 것
- gitignore에 push하면 안될 파일들 등록해둘것. **특히 .env**

- env활용 요령
  - django-environ 패키지 설치
  - settings.py 에서 환경변수 불러오기 예시
    ```python
    import environ
    env = environ.Env()
    environ.Env.read_env()
    API_KEY = env('API_KEY')
    ```

## 시연 이전 개발자 도구에 안나오도록 console.log 잘 정리해둘것