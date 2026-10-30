# FDE Kit — FastAPI 범용 키트

> 이 저장소는 SK하이닉스 AI 해커톤 2차 예선 전에 만든 범용 FastAPI 키트입니다. 특정 과제의 정답이나 도메인 결과물은 포함하지 않으며, 엔티티 정의·테스트 하네스·작업 지침(AGENTS.md)·문서 템플릿만 제공합니다. 과제별 구현은 응시 중 작업 이력으로 남깁니다.

`app/entities.py`의 정의로 SQLite 테이블과 범용 REST API, 목록·등록·수정 화면을 구성합니다. 현재 예제 엔티티는 `item`입니다. 프론트엔드는 빌드 없는 HTML/CSS/JS이며, 의존성은 `fastapi`, `uvicorn`, 테스트용 `httpx`입니다.

## 시험장 시작 순서

Linux에서 다음 명령을 한 줄씩 실행합니다.

```bash
git clone https://github.com/shinsoyoung1085-netizen/fde-kit.git
```

```bash
cd fde-kit
```

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

서버는 그대로 두고 다른 터미널에서 `fde-kit` 디렉터리로 이동해 `source .venv/bin/activate`로 같은 가상환경을 활성화한 뒤 실행합니다.

```bash
python scripts/smoke.py
```

Browser 도구에 **PORT 8000**, **경로 /**를 입력합니다. 로컬 브라우저에서는 `http://localhost:8000/`을 엽니다.

## 기존 코드가 주어진 과제일 때

기존 과제 저장소의 코드를 사용하고, 이 키트에서는 작업 지침과 문서 템플릿만 복사합니다. 아래는 `fde-kit`과 `task-repo`가 같은 상위 디렉터리에 있는 Linux 예시입니다. 경로를 실제 과제 저장소에 맞추고, 대상에 같은 이름의 파일이 있으면 내용을 먼저 확인해 필요한 부분을 병합합니다. `cp -i`는 덮어쓰기 전에 확인합니다.

```bash
cp -i fde-kit/AGENTS.md task-repo/AGENTS.md
```

```bash
mkdir -p task-repo/docs
```

```bash
cp -i fde-kit/docs/PLAN.md fde-kit/docs/DECISIONS.md task-repo/docs/
```

복사한 `AGENTS.md`의 경로·실행 명령은 과제 저장소의 실제 구조에 맞게 조정하고, 문서의 빈칸은 과제 요구사항과 담당자 답변으로 채웁니다.

## Windows 실행 방법

PowerShell에서 저장소를 복제하고 이동합니다.

```powershell
git clone https://github.com/shinsoyoung1085-netizen/fde-kit.git
cd fde-kit
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

다른 PowerShell 터미널에서 같은 저장소 디렉터리로 이동해 실행합니다. 가상환경 활성화 없이 해당 Python을 직접 사용합니다.

```powershell
.\.venv\Scripts\python.exe scripts/smoke.py
```

브라우저에서 `http://localhost:8000/`을 엽니다.

## 구조와 현재 기능

| 파일 | 역할 |
| --- | --- |
| `app/main.py` | FastAPI 시작 시 DB 초기화, `/`와 `/static` 서빙, 메타데이터·CRUD API 및 오류 응답 |
| `app/entities.py` | `item`의 이름·수량·최소 수량·단위 필드 정의 |
| `app/engine.py` | sqlite3 테이블 생성, CRUD, 필수값·타입·미정의 필드 검증 |
| `static/index.html` | 엔티티 목록·테이블·폼의 공통 화면 골격 |
| `static/app.js` | `/api/meta` 기반 화면 생성, 등록·수정·삭제, 모든 문자열 필드의 브라우저 내 검색 |
| `static/style.css` | 상단 `:root` 디자인 토큰과 화면 스타일 |
| `scripts/smoke.py` | 실행 중인 서버의 서빙·item CRUD·입력 검증 스모크 테스트 |
| `requirements.txt` | Python 의존성 목록 |
| `AGENTS.md` | 작업 순서·제약·변경 보고·커밋 지침 |
| `docs/PLAN.md` | 과제 목표·요구사항·설계·검증 계획 템플릿 |
| `docs/DECISIONS.md` | 결정 근거·대안·검증·한계 기록 템플릿 |
| `.gitignore` | DB 데이터·가상환경·Python 캐시 제외 |

DB는 서버 시작 시 `data/app.db`에 생성됩니다. 각 레코드에는 `id`, `created_at`, `updated_at`이 자동으로 붙습니다. 지원 필드 타입은 `str`, `int`, `float`, `bool`, `date`, `datetime`입니다. `min_qty`는 현재 저장하는 숫자 필드입니다.

| 메서드와 경로 | 동작 |
| --- | --- |
| `GET /api/meta` | 엔티티 정의 조회 |
| `GET /api/{entity}` | 전체 목록 조회 |
| `POST /api/{entity}` | 등록 |
| `GET /api/{entity}/{id}` | 단건 조회 |
| `PUT /api/{entity}/{id}` | 전달된 필드만 수정 |
| `DELETE /api/{entity}/{id}` | 삭제 |

화면에서는 첫 엔티티를 자동 선택합니다. 행을 클릭하면 수정 폼이 열리고, 삭제는 확인 후 처리합니다. 검색은 모든 `str` 필드에 대해 대소문자 구분 없는 부분 일치로 수행합니다.

## 엔티티 추가 예시

`app/entities.py`의 기존 `ENTITIES` 사전 안에 아래 항목을 추가합니다. 예시는 문서용이며 현재 코드에는 추가되어 있지 않습니다.

```python
"location": {
    "label": "보관 위치",
    "fields": [
        {"name": "name", "type": "str", "label": "이름", "required": True},
        {"name": "capacity", "type": "int", "label": "수용량", "default": 0}
    ]
}
```

기존 항목과 쉼표로 구분하고 서버를 재시작하면 새 테이블, `/api/location` CRUD, 공통 화면의 보관 위치 목록·폼을 사용할 수 있습니다. 등록 시 `name`은 필수이고, API에서 `capacity`를 생략하면 0이 저장됩니다.

새 엔티티 검증은 `scripts/smoke.py`에 추가합니다. 기존 테스트는 `item`을 전제로 하므로 이를 교체하면 테스트 데이터와 기대값도 바꿔야 합니다. 현재 엔진은 없는 테이블을 생성하며, 이미 생성된 테이블의 필드 변경을 자동 반영하지 않습니다.

## 검증 방법

서버 실행 후 `python scripts/smoke.py`의 마지막 출력이 `PASS`인지 확인합니다. 이 테스트는 루트·정적 파일 서빙, 메타데이터, item 등록·조회·수정·삭제, 기본값·시각 필드, 필수값·타입·미정의 필드 오류, 없는 엔티티·항목 처리를 확인합니다. 테스트 중 등록한 품목은 삭제합니다.

화면 검색과 삭제 확인 창은 스모크 테스트에 포함되지 않습니다. 브라우저에서 이름과 단위를 입력해 등록하고, 각각의 문자열로 검색한 뒤 행 클릭 수정과 삭제 취소·확인을 직접 확인합니다.
