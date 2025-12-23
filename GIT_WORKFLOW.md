
# GIT
## 1. Branch 생성 원칙

- 기능 구현은 반드시 **기능 단위 브랜치**에서 작업한다.
- 브랜치 네이밍 규칙은 다음 형식을 따른다.
    ```text
    feature/기능명
    ```
  - 기능명의 경우 공백이 필요한 경우 " _ "로 표현한다.

## 2. Commit Message 원칙

  - [Git Commit Style Guide](https://gist.github.com/ericavonb/3c79e5035567c8ef3267)를 따른다.
  - 참고: https://gist.github.com/ericavonb/3c79e5035567c8ef3267
  - 커밋 메시지 형식은 아래 규칙을 따른다.

    ### ✅ 기본 형식
    {타입}({파일 또는 기능}): {변경 요약}

    ---

    ### ✅ 타입(Type) 종류

    | 타입 | 의미 |
    |------|------|
    | feat | 새로운 기능 추가 |
    | fix | 버그 수정 |
    | docs | 문서 수정 |
    | style | 코드 포맷팅, 세미콜론 수정 등 로직 변경 없음 |
    | refactor | 코드 리팩토링 |
    | test | 테스트 코드 추가 |
    | chore | 빌드, 설정 파일, 패키지 매니저 수정 |
    | init | 초기 커밋 |
    | rearrange | 파일 이동, 추가, 삭제 등 |
    | update | 코드 업데이트 (버전, 라이브러리 호환성)

    ---

    ### ✅ docs 타입 예시

    - docs(./GIT_WORKFLOW.md): git 브랜치 전략 내용 추가
    - docs(./TECH_STACK.md): 기술 스택 선정 이유 보완
    - docs(./REQUIREMENTS.md): 기능 요구사항 입력-처리-출력 구조 반영
    - docs(README): 프로젝트 실행 방법 수정

    ---

    ### ✅ feat 타입 예시

    - feat(auth): 회원가입 API 구현
    - feat(company): 기업 검색 기능 추가
    - feat(recommend): 사용자 맞춤 기업 추천 로직 추가
    - feat(board): 게시글 작성 기능 구현
    - feat(bookmark): 기업 즐겨찾기 기능 추가

    ---

    ### ✅ fix 타입 예시

    - fix(login): 로그인 시 토큰 저장 오류 수정
    - fix(company): 기업 검색 결과 중복 출력 버그 수정
    - fix(comment): 댓글 삭제 권한 오류 수정
    - fix(cors): CORS 정책으로 인한 통신 오류 해결

    ---

    ### ✅ refactor 타입 예시

    - refactor(user): 사용자 모델 구조 개선
    - refactor(api): 기업 API 로직 함수 분리
    - refactor(auth): 인증 로직 모듈화
    - refactor(board): 게시판 서비스 레이어 분리

    ---

    ### ✅ style 타입 예시

    - style(frontend): eslint 규칙에 따른 코드 포맷 수정
    - style(css): 불필요한 공백 및 정렬 수정
    - style(template): Django template 들여쓰기 정리

    ---

    ### ✅ test 타입 예시

    - test(user): 회원가입 API 테스트 코드 추가
    - test(auth): 로그인 인증 테스트 추가
    - test(company): 기업 조회 기능 테스트 추가

    ---

    ### ✅ chore 타입 예시

    - chore(env): django-environ 패키지 추가
    - chore(docker): docker-compose 설정 파일 수정
    - chore(requirements): requirements.txt 라이브러리 버전 업데이트
    - chore(gitignore): .env 파일 gitignore에 추가

    ---

    ### ✅ 커밋 메시지 작성 규칙

    1. 한 커밋에는 **하나의 목적만 담는다.**
    2. 커밋 메시지는 **한글 또는 영어 중 하나로 통일한다.**
    3. 마침표(.)는 사용하지 않는다.
    4. “수정”, “변경” 같은 **포괄적인 단어 사용 금지**  
    → 무엇을 수정했는지 반드시 명확히 작성한다.
    5. PR Merge 전에는 **팀원 코드 리뷰 필수**로 진행한다.

    ---

    ### 예시
    원칙: 첫 줄만 사용, but, 큰 작업, 버그 원인 설명이 필요할 때만 body 작성
    ```text
    feat(auth): 회원가입 API 구현

    // 아래는 큰 기능, 버그 원인 설명이 필요하거나 이슈 트래킹 연동 시에만 작성
    비밀번호를 bcrypt로 암호화하여 저장하도록 수정하고,
    이메일 중복 검증 로직을 추가함.

    Closes #15 // 이슈 번호
    BREAKING CHANGE: 로그인 API 응답 구조 변경
    ```

## Push 원칙
  - 기능 구현 이후 main(master) branch에 merge하기 전엔 함께 코드 리뷰 및 기능 검증 이후 merge를 진행할 것