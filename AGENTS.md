# AGENTS.md — FDE 범용 키트

## 이 저장소의 목적
어떤 업무 도메인 과제든 80%는 설정으로 해결하고, 나머지 20%만 도메인 코드로 채우는 FastAPI 키트다.
엔티티를 정의하면 DB 테이블, REST API, 목록/등록/수정 화면이 자동으로 생긴다.

## 구조
- app/main.py        : FastAPI 앱, 정적 파일 서빙, 라우터 등록
- app/entities.py    : 엔티티 정의 (도메인 과제는 여기부터 수정한다)
- app/engine.py      : 엔티티 정의를 읽어 테이블 생성, 범용 CRUD, 검증 수행
- app/patterns.py    : 공통 패턴 (임계값 경고, 상태 흐름, 변경 이력, 시간 겹침 검사, 중복 검사)
- app/domain/        : 설정으로 안 되는 도메인 전용 로직 (20%)
- app/llm.py         : LLM 호출 어댑터 (키가 없으면 mock 응답)
- static/            : index.html, app.js, style.css — /api/meta를 읽어 화면을 자동 구성
- scripts/smoke.py   : 핵심 API 스모크 테스트
- docs/PLAN.md, docs/DECISIONS.md : 과제 제출 문서 템플릿

## 새 도메인 과제를 받았을 때 순서
1. README와 업무 담당자 답변으로 docs/PLAN.md를 먼저 채운다.
2. app/entities.py에 엔티티를 정의한다. 패턴은 설정 키로 켠다.
3. 설정으로 표현이 안 되는 규칙만 app/domain/에 함수로 추가하고 engine 훅에 연결한다.
4. scripts/smoke.py에 해당 규칙 테스트를 추가하고 실행한다.
5. 결정 사항을 docs/DECISIONS.md에 기록한다.

## 규칙
- 요구사항에 없는 기능(로그인, 통계, 알림, 배포 설정 등)을 추가하지 않는다.
- 새 의존성을 추가하지 않는다. fastapi, uvicorn, httpx(테스트용)만 쓴다.
- DB는 sqlite3 표준 라이브러리만 쓴다. ORM을 도입하지 않는다.
- 프론트엔드는 빌드 없는 순수 HTML/CSS/JS다. 프레임워크를 도입하지 않는다.
- 엔티티별 전용 API나 화면을 새로 만들기 전에, 설정으로 해결할 수 있는지 먼저 확인한다.
- 변경 후에는 python scripts/smoke.py를 실행하고 결과를 보고한다.
- 작업이 끝나면 바꾼 파일, 이유, 확인 방법을 3~5줄로 요약한다.

## 실행
- 서버: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
- 테스트: python scripts/smoke.py
