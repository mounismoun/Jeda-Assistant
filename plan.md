# Discord 대화형 범용 비서 계획

## 요약

- Python 기반 Discord 대화형 범용 비서 v1을 만든다.
- 슬래시 명령어가 아니라 멘션, 답글, DM을 통해 자연스럽게 대화한다.
- 첫 전문 기능은 사용자가 명시적으로 저장한 메모와 파일을 기억하고 회상하는 것이다.
- 이후 전문 에이전트를 쉽게 추가할 수 있도록 처음부터 얇은 멀티 에이전트 구조로 시작한다.
- 에이전트 목록의 목적, 설명, 예시는 `agent_catalog.json` 설정 파일로 관리한다.
- 라우팅 모델은 `gpt-5.4-mini`로 고정한다.
- 각 전문 에이전트는 작업 난이도를 판단한 뒤 답변 모델을 선택한다.

## 핵심 UX

봇은 다음 조건 중 하나를 만족할 때만 응답한다.

- 사용자가 봇을 멘션한다.
- 사용자가 봇 메시지에 답글을 단다.
- 사용자가 봇에게 DM을 보낸다.

장기 기억은 사용자가 명시적으로 기억을 요청한 경우에만 저장한다.

예시:

- "이거 기억해줘: 나는 오전에 집중이 잘 돼."
- "이 파일 저장해줘."
- "이 문서 내용을 기억해줘."

사용자가 명시적인 저장 요청 없이 첨부 파일만 보내면 봇은 저장하지 않는다. 대신 기억할지 짧게 확인한다.

## v1 지원 입력

- 일반 텍스트 메모
- `.txt` 첨부 파일
- `.md` 첨부 파일
- `.pdf` 첨부 파일

PDF는 텍스트 추출만 지원한다. 스캔 이미지 OCR은 v1 범위에서 제외한다.
텍스트 파일은 UTF-8로 읽을 수 있어야 하며, 의미 있는 문자 없이 기호만 있는 파일은 저장하지 않는다.

## 에이전트 구조

에이전트 실행 코드는 `assistant_bot/agents/` 패키지로 분리한다.
라우터가 참고하는 에이전트 목적, 설명, 예시는 `agent_catalog.json`에서 관리하고, 실제 실행 핸들러는 `assistant_bot/agent_registry.py`에서 연결한다.

### Router Agent

- `gpt-5.4-mini`를 사용한다.
- 현재 메시지와 최근 대화 맥락을 라우팅 모델에 먼저 전달한다.
- `assistant_bot/capabilities.py`의 지원/미지원 기능 목록을 함께 전달해 코드로 제공하지 않는 실행 요청은 `unsupported`로 분류한다.
- 휴리스틱 라우팅은 모델 호출 실패 또는 라우터 JSON 파싱 실패 시 fallback으로만 사용한다.
- 사용자 메시지를 다음 intent 중 하나로 분류한다.
  - `chat`
  - `help`
  - `status`
  - `cancel_pending`
  - `remember`
  - `recall`
  - `list_memory`
  - `update_memory`
  - `delete_memory`
  - `restore_memory`
  - `daily_briefing`
  - `reset_context`
  - `manage_task`
  - `unsupported`
- 대상 전문 에이전트를 선택한다.
- 짧은 구조화 라우팅 결과만 반환한다.
- 최종 사용자 답변은 생성하지 않는다.

### Conversation Agent

- 일반 대화를 처리한다.
- Discord 채널, 스레드, DM, 사용자 기준으로 최근 대화 컨텍스트를 유지한다.
- 필요할 때 관련 장기 기억을 함께 사용한다.
- 대화 컨텍스트가 설정한 기준보다 커지면 압축 요약을 생성한다.
- 압축된 대화 요약은 명시적 장기 기억과 별도로 저장한다.

### Memory Agent

- 사용자가 명시적으로 저장한 메모와 파일을 저장한다.
- 이미 같은 사용자가 같은 텍스트 메모를 저장했다면 중복 저장하지 않고 기존 메모 ID를 안내한다.
- 이미 같은 사용자가 같은 문서 내용을 저장했다면 중복 저장하지 않고 기존 문서 ID를 안내한다.
- 지원하는 첨부 파일에서 텍스트를 추출한다.
- 내용을 chunk 단위로 나눈다.
- 각 chunk의 embedding을 생성한다.
- 저장된 기억과 문서를 의미 유사도로 검색한다.
- 저장된 텍스트 메모를 ID 또는 관련 키워드 기반으로 수정한다.
- 사용자가 명확히 전체 삭제를 요청하면 확인을 받은 뒤 사용자 기준 장기 기억과 문서를 모두 삭제한다.
- "내 운동 관련 기억 삭제해줘" 같은 자연어 삭제 요청을 처리한다.

## 모델 선택

### 고정 라우터 모델

라우터는 항상 다음 모델을 사용한다.

- `gpt-5.4-mini`

### 전문 에이전트 난이도

각 전문 에이전트는 답변 생성 전에 작업 난이도를 지정한다.

- `easy`: 단순 대화, 저장 확인, 짧은 요약, 직접적인 기억 조회
- `medium`: 여러 기억 조합, 파일 요약, 가벼운 추론
- `hard`: 긴 문서 종합, 상충 정보 비교, 계획 수립, 복잡한 추론

### 기본 모델 매핑

- `easy`: `gpt-5.4-mini`
- `medium`: `gpt-5.4`
- `hard`: `gpt-5.5`

사용자가 빠르게, 저렴하게, 정확하게, 깊게 생각해서 같은 선호를 말하면 전문 에이전트는 모델 선택에 그 선호를 반영한다.

각 에이전트는 다음 내용을 로그로 남긴다.

- 선택한 모델
- 난이도
- 모델 선택 이유 요약

## Tool Calling 설계 원칙

앞으로 추가되는 모든 전문 에이전트는 개발 단계부터 OpenAI tool/function calling 적용 여부를 검토한다.

기본 원칙은 다음과 같다.

- 에이전트가 외부 데이터 조회, 저장소 검색, 여러 단계의 정보 수집, 구조화된 작업 실행을 해야 한다면 tool calling 후보로 본다.
- 모델 판단이 실제 효율을 높이는 복잡한 조회, 다중 검색, 애매한 자연어 해석에는 tool calling을 우선 검토한다.
- 단순 도움말, 상태 확인, 명확한 CRUD, 삭제 확인, 리마인더 발송처럼 deterministic 제어가 더 안전한 흐름은 Python 직접 실행을 우선한다.
- destructive 작업은 tool calling으로 바로 실행하지 않고 기존 확인 절차와 권한 제한을 유지한다.
- 각 에이전트 설계 문서에는 사용 가능한 tool 목록, read-only/mutation 구분, tool 호출 실패 시 fallback 정책을 함께 기록한다.
- tool calling은 에이전트 카탈로그 기반 라우팅 및 모듈화 계획과 연결하며, `agent_catalog.json`과 `AgentDefinition`에 사용 가능한 tool 목록을 포함한다.
- 사용자에게 보이는 최종 답변은 가능한 한 AI 응답 구성 계층이 작성하고, 에이전트 내부의 하드코딩 문구는 상태 변경 결과와 안전상 필요한 최소 안내로 제한한다.

현재 1차 적용 상태는 다음과 같다.

- `OpenAIService.tool_response`와 `ToolSpec` 기반 tool executor를 구현했다.
- `ConversationAgent`는 `search_memories`, `list_recent_memories`, `get_memory_detail`, `get_document_detail`, `search_tasks`, `list_tasks`, `list_due_tasks` read-only tool을 사용할 수 있다.
- `MemoryAgent.recall`의 일반 자연어 회상 경로는 `search_memories`, `list_recent_memories`, `get_memory_detail`, `get_document_detail` read-only tool을 사용한다.
- 명확한 CRUD, 삭제, 복구, 리마인더 발송은 기존 Python 직접 실행 흐름을 유지한다.

## 저장소

v1은 Python 표준 `sqlite3` 기반 SQLite를 사용한다.

권장 환경 변수:

- `DISCORD_TOKEN`
- `DISCORD_CLIENT_ID`
- `OPENAI_API_KEY`
- `OPENAI_ROUTER_MODEL=gpt-5.4-mini`
- `OPENAI_EASY_MODEL=gpt-5.4-mini`
- `OPENAI_MEDIUM_MODEL=gpt-5.4`
- `OPENAI_HARD_MODEL=gpt-5.5`
- `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`
- `OPENAI_TIMEOUT_SECONDS=30`
- `OPENAI_MAX_RETRIES=2`
- `DATABASE_PATH=./data/assistant.sqlite`
- `ASSISTANT_TIMEZONE=Asia/Seoul`
- `MAX_ATTACHMENT_BYTES=10485760`
- `CONTEXT_COMPRESSION_CHARS=20000`
- `RETRIEVAL_LIMIT=8`
- `PENDING_CONFIRMATION_TTL_MINUTES=10`
- `TASK_REMINDER_INTERVAL_MINUTES=1`
- `TASK_REMINDER_BATCH_SIZE=20`
- `LOG_LEVEL=INFO`
- `LOG_FILE=./data/assistant.log`

장기 기억은 두 범주로 분리한다.

- `user_memories`: 사용자가 명시적으로 저장한 사실, 선호, 메모
- `documents`: 사용자가 명시적으로 저장한 첨부 파일과 추출 텍스트

대화 요약은 장기 기억과 별도로 저장한다.

## 동작 정책

- 사용자가 텍스트 기억을 요청하면 저장하고 짧게 확인한다.
- 사용자가 지원하는 첨부 파일의 기억을 요청하면 텍스트를 추출하고 색인한다.
- 사용자가 저장된 정보에 대해 질문하면 관련 기억과 문서를 검색한 뒤 답한다.
- 근거가 충분하지 않으면 저장된 기억에 답이 없다고 말한다.
- 필요할 경우 근거 기반 답변과 추측을 구분한다.
- 긴 답변은 Discord 메시지 제한에 맞게 분할한다.

## 구현 상태

- Python 패키지 구조로 구현했다.
- Discord 메시지 이벤트 기반으로 멘션, 답글, DM 응답을 처리한다.
- 같은 사용자의 장기 기억은 DM, 서버, 스레드 어디서든 이어지도록 사용자 단위 전역 기억으로 조회한다.
- 현재 대화 위치를 에이전트 컨텍스트와 상태 응답에 포함한다.
- SQLite 테이블 생성과 저장소 로직을 구현했다.
- 텍스트 메모 저장, 파일 텍스트 추출, chunking, embedding 저장, 유사도 검색을 구현했다.
- UTF-8로 읽을 수 없거나 의미 있는 텍스트가 없는 첨부는 저장하지 않도록 구현했다.
- 동일한 텍스트 메모는 중복 저장하지 않고 기존 메모 ID와 저장 위치를 안내하도록 구현했다.
- 동일한 문서 내용은 `content_hash`로 중복 저장을 방지하고 기존 문서 ID와 저장 위치를 안내하도록 구현했다.
- 자연어 기반 기억 목록 조회와 기억 상태 확인을 구현했다.
- `방금 말한 거 기억해줘`, `그거 기억해줘`처럼 직전 사용자 발화를 장기 기억으로 저장하도록 구현했다.
- 자연어 기반 도움말과 봇 상태 확인을 구현했다.
- `오늘 브리핑 해줘`로 오늘까지 할 일, 열린/완료 작업 수, 최근 기억, 최근 대화 위치를 한 번에 보여주도록 구현했다.
- 현재 DM, 채널, 스레드의 최근 대화 기록과 요약만 지우고 장기 기억은 유지하는 대화 맥락 초기화를 구현했다.
- 사용자별 할 일 추가, 중복 방지, 상세 조회, 전체/오늘 목록 조회, 최근 대화 기반 추출, 제목/우선순위 수정, 완료, 완료 취소, 미루기, 삭제를 자연어 대화와 운영 CLI에서 처리하도록 구현했다.
- 사용자가 요청한 특정 시각 알림을 할 일과 분리된 알림 전용 저장소에 등록하고, 생성 위치와 관계없이 사용자 DM으로 한 번 발송하도록 구현했다.
- 사용자가 `할 일 3 내일 오전 9시 다시 알려줘`처럼 말하면 새 기한으로 리마인더를 다시 예약하도록 구현했다.
- ID 없는 `30분 뒤 다시 알려줘`는 최근 할 일 스누즈가 아니라 새 알림 요청으로 분리하고, 할 일 미루기는 `할 일 3 30분 뒤 다시 알려줘`처럼 대상을 명시하도록 구현했다.
- 할 일 기한은 `오늘`, `내일`, `모레`, `30분 뒤`, `2시간 후`, `3일 뒤`, `2주 후`, `이번 주 금요일`, `다음 주 금요일`, `YYYY-MM-DD`, `n월 n일`, `오전 9시`, `18:30`, `오후 3시` 표현을 인식하도록 구현했다.
- `내일 오전 9시에 물 마시라고 알려줘`, `30분 뒤 물 마시라고 알려줘` 같은 자연어 알림 문장을 열린 할 일이 아니라 알림 요청으로 저장하도록 구현했다.
- `오늘 할 일 뭐야?`, `내일 할 일 뭐야?`, `이번 주 할 일 보여줘`, `기한 없는 할 일 보여줘`처럼 목록 범위를 바꿔 조회하도록 구현했다.
- `완료한 할 일 보여줘`, `전체 할 일 목록 보여줘`처럼 상태별 할 일 목록을 조회하도록 구현했다.
- `최근 대화에서 할 일 뽑아줘`는 후보를 보여주고, `최근 대화에서 할 일 뽑아서 추가해줘`는 후보를 열린 할 일로 저장하도록 구현했다.
- `그거 할 일로 추가해줘`처럼 직전 사용자 발화를 열린 할 일로 저장하도록 구현했다.
- `할 일 3을 고객 미팅 준비로 바꿔줘`처럼 열린 할 일 제목을 수정하도록 구현했다.
- `할 일 3 중요하게 표시해줘`처럼 열린 할 일 우선순위를 높음, 보통, 낮음으로 수정하도록 구현했다.
- 완료, 삭제, 미루기, 우선순위 변경은 ID가 없어도 키워드가 단일 열린 할 일로 명확히 좁혀지면 처리하도록 구현했다.
- 할 일 목록, 오늘까지 목록, 리마인더, 브리핑은 높은 우선순위 항목을 먼저 보여주도록 구현했다.
- `할 일 3 다시 열어줘`처럼 실수로 완료한 할 일을 열린 상태로 되돌리도록 구현했다.
- `메모 3 보여줘`, `문서 2 보여줘` 같은 ID 기반 상세 조회를 구현했다.
- `메모 3을 ...로 수정해줘` 같은 ID 기반 텍스트 메모 수정과 관련 키워드 기반 수정 후보 선택을 구현했다.
- ID, 키워드, 의미 검색 후보 기반 삭제를 구현했다.
- `방금 저장한 거 지워줘`처럼 최근 저장 항목 1개를 삭제하는 실수 복구 흐름을 구현했다.
- `삭제한 기억 목록 보여줘`, `메모 3 복구해줘`, `방금 지운 거 복구해줘`처럼 삭제 항목 조회와 복구 흐름을 구현했다.
- `내 기억 전부 삭제해줘` 같은 요청은 확인 대기 상태를 만든 뒤, 정해진 시간 안에 사용자가 `응, 전부 삭제해`처럼 전체 범위와 삭제 의사를 함께 답장해야 사용자 기준 장기 기억 전체 삭제를 실행하도록 구현했다.
- 첨부만 보낸 뒤 사용자가 봇 확인 메시지에 제한 시간 안에 답장하면 원본 첨부를 찾아 저장하는 흐름을 구현했다.
- 첨부 저장 확인 대기 상태를 자연어로 취소하는 흐름을 구현했다.
- 지원하지 않는 첨부 파일을 보냈을 때 현재 지원 형식을 안내하도록 구현했다.
- OpenAI Responses API 기반 라우터와 답변 생성을 구현했다.
- OpenAI 텍스트 응답과 embedding 호출에 timeout과 재시도 설정을 적용했다.
- 라우터는 `gpt-5.4-mini`를 사용하고, 전문 에이전트는 난이도와 사용자 선호에 따라 모델을 선택한다.
- `LOG_LEVEL`, `LOG_FILE` 설정으로 콘솔 로그 레벨과 선택적 파일 로그를 조정하도록 구현했다.
- `.env.example`만 제공하고 실제 비밀값은 저장하지 않는다.
- `assistant-admin doctor`로 필수 환경 변수, 예시 비밀값, 숫자 설정, 타임존, SQLite 저장 경로를 점검하도록 구현했다.
- `assistant-admin init-db`로 SQLite 저장소를 생성하고 핵심 테이블, journal mode, foreign key 설정을 확인하도록 구현했다.
- `assistant-admin openai-check`로 OpenAI 텍스트 응답 모델과 embedding 모델 연결을 점검하도록 구현했다.
- `assistant-admin users`로 사용자별 활성 메모, 문서, 삭제 항목 수와 최근 저장 시각을 조회하도록 구현했다.
- `assistant-admin memories`로 최근 저장된 메모와 문서를 user_id와 종류 기준으로 조회하도록 구현했다.
- `assistant-admin deleted`로 삭제된 메모와 문서를 user_id와 종류 기준으로 조회하도록 구현했다.
- `assistant-admin undelete`로 삭제된 메모와 문서를 user_id와 ID 기준으로 복구하도록 구현했다.
- `assistant-admin export`로 저장된 메모, 문서, 할 일을 전체 또는 user_id 기준으로 JSON 내보내도록 구현했다.
- `assistant-admin search`로 저장된 메모, 문서, 할 일을 전체 또는 user_id 기준으로 로컬 SQLite에서 키워드 검색하도록 구현했다.
- `assistant-admin ingest`로 로컬 `.txt`, `.md`, `.pdf` 파일을 Discord 없이 사용자 장기 기억 문서로 저장하도록 구현했다.
- `assistant-admin route`로 OpenAI 호출 없이 휴리스틱 fallback intent를 미리 확인하도록 구현했다.
- `assistant-admin ask`로 Discord를 켜기 전 로컬에서 실제 에이전트, OpenAI, SQLite 흐름을 실행하도록 구현했다.
- `assistant-admin briefing`으로 사용자별 오늘 브리핑을 SQLite 기준으로 출력하도록 구현했다.
- `assistant-admin snapshot`으로 사용자별 기억, 할 일, 대기 작업, 최근 대화 위치를 한 번에 점검하도록 구현했다.
- `assistant-admin conversations`로 대화 컨텍스트별 메시지 수, 요약 수, 최근 메시지 시각과 미리보기를 조회하도록 구현했다.
- `assistant-admin clear-conversation`으로 특정 대화 컨텍스트의 메시지와 요약만 초기화하고 장기 기억은 유지하도록 구현했다.
- `assistant-admin tasks`로 사용자별 할 일을 조회, 추가, 완료, 삭제하고 삭제한 할 일을 다시 복구하도록 구현했다.
- `assistant-admin reminders`로 예약 시각이 지난 사용자 알림 발송 대상을 미리 확인하도록 구현했다.
- `assistant-admin logs`로 최근 에이전트 라우팅, intent, 난이도, 모델 선택 로그를 조회하도록 구현했다.
- `assistant-admin cleanup`으로 오래된 대화 기록, 에이전트 로그, 해결된 첨부 대기 요청, 삭제된 기억/문서/할 일을 보존 기간 기준으로 정리하도록 구현했다.
- `assistant-admin backup`으로 embedding과 로그를 포함한 SQLite 저장소 전체를 백업하도록 구현했다.
- `assistant-admin restore`로 SQLite 백업 파일을 복구하되, 현재 저장소를 먼저 안전 백업하도록 구현했다.
- setuptools 패키지 발견 설정을 추가해 콘솔 스크립트가 설치 후 정상 동작하도록 보정했다.

## 테스트 계획

### 단위 테스트

- `chat`, `help`, `status`, `cancel_pending`, `remember`, `recall`, `list_memory`, `update_memory`, `delete_memory`, `manage_task`, `manage_reminder` 휴리스틱 라우팅
- 첨부 저장 지시문과 실제 저장할 텍스트 구분
- 깨진 UTF-8 텍스트와 의미 있는 텍스트가 없는 첨부 저장 방지
- SQLite 저장소의 목록, 통계, 검색, 삭제 동작
- SQLite 저장소의 삭제 항목 목록, ID 기반 복구, 최근 삭제 항목 복구 동작
- SQLite 저장소의 사용자 기준 전체 장기 기억 삭제 동작
- SQLite 저장소의 동일 텍스트 메모 중복 탐지 동작
- SQLite 저장소의 동일 문서 내용 중복 탐지 동작
- SQLite 저장소의 사용자별 할 일 추가, 중복 방지, 상세 조회, 전체/기한 목록 조회, 대화 기반 후보 저장, 제목/우선순위 수정, 완료, 완료 취소, 미루기, 삭제 동작
- SQLite 저장소의 알림 예약, 발송 대상 조회, 발송 표시 동작
- SQLite 저장소의 텍스트 메모 수정과 embedding 재생성 동작
- SQLite 저장소의 메모/문서 상세 조회 동작
- 같은 사용자 기억이 DM/서버 위치를 넘어 유지되고, 저장 위치 힌트가 표시되는지 확인
- 첨부 저장 확인 대기 상태 저장과 해소 동작
- 현재 대화 맥락 초기화 시 메시지와 요약만 삭제하고 다른 대화와 장기 기억은 유지하는지 확인
- 전체 기억 삭제 확인 대기 상태 저장, 확정, 취소, 만료 동작
- 지원 첨부 확장자 판별
- 운영 CLI의 환경 점검, 초대 URL 생성, 저장소 통계 출력
- 운영 CLI의 OpenAI 텍스트 응답 및 embedding 연결 점검 출력 형식
- 운영 CLI의 사용자별 데이터 현황 조회 포맷
- 운영 CLI의 최근 기억 목록 조회와 user_id, 종류 필터링 포맷
- 운영 CLI의 삭제 기억 목록 조회와 user_id, 종류 필터링 포맷
- 운영 CLI의 삭제 기억 ID 기반 복구 동작과 결과 포맷
- 운영 CLI의 전체 및 user_id 기준 기억, 문서, 할 일 export 출력 형식
- 운영 CLI의 전체 및 user_id 기준 메모, 문서, 할 일 키워드 검색 결과 포맷
- 운영 CLI의 로컬 파일 기억 저장과 중복 방지
- 운영 CLI의 라우팅 미리보기 출력 형식
- 운영 CLI의 로컬 대화 실행 설정 로딩
- 운영 CLI의 사용자별 오늘 브리핑 출력
- 운영 CLI의 대화 컨텍스트 현황 조회 포맷
- 운영 CLI의 사용자별 할 일 추가, 전체/기한 목록 조회, 제목/우선순위 수정, 미루기, 완료, 다시 열기 결과 포맷
- 운영 CLI의 에이전트 로그 조회와 필터링 포맷
- 운영 CLI의 보존 기간 기반 대화/로그 정리 미리보기와 실제 삭제 동작
- 운영 CLI의 SQLite 백업 동작과 덮어쓰기 방지
- 운영 CLI의 SQLite 복구 동작과 pre-restore 안전 백업 생성
- 난이도 기반 모델 선택
- 빠름, 저렴함, 정확함, 깊은 추론에 대한 사용자 선호 반영
- OpenAI 텍스트 응답과 embedding 호출의 재시도 동작
- 텍스트 chunking
- embedding 유사도 정렬
- Discord 메시지 분할

### 통합 테스트

- 현재 자동화된 통합 테스트는 아직 없다.
- 실제 Discord 토큰과 OpenAI API 키를 추가한 뒤 수동 검증을 우선 수행한다.
- 텍스트 기억을 저장하고 자연어로 회상한다.
- `.md` 파일을 저장하고 내용 기반 질문에 답한다.
- `.pdf` 파일을 저장하고 추출 텍스트 기반 질문에 답한다.
- 명시적 저장 의도 없는 첨부 파일이 저장되지 않는지 확인한다.
- 삭제된 기억이 이후 검색 결과에 나오지 않는지 확인한다.
- 긴 대화가 유용한 맥락을 유지한 채 압축되는지 확인한다.
- 어려운 종합 요청에서 더 높은 성능의 모델이 선택되는지 확인한다.

### Discord 수동 테스트

- 멘션 기반 대화
- 답글 기반 대화
- DM 대화
- 텍스트 기억 저장과 회상
- 파일 저장과 회상
- 자연어 기억 수정
- 자연어 기억 삭제
- 자연어 할 일 추가, 전체/오늘 목록 조회, 최근 대화 추출, 제목/우선순위 수정, 미루기, 완료, 완료 취소, 삭제
- 자연어 오늘 브리핑 조회
- 기한 도래 할 일 리마인드 전송
- 최근 저장 항목 삭제
- 내부 라우팅과 모델 선택 로그

### 자동 검증 결과

- `python3 -m pytest`: 통과, 163개 테스트
- `python3 -m ruff check .`: 통과
- `python3 -m compileall assistant_bot tests`: 통과
- `assistant-admin doctor`, `assistant-admin invite`, `assistant-admin stats`, `assistant-admin export`, `assistant-admin search`, `assistant-admin backup`: 실행 확인
- `assistant-admin export --help`: 실행 확인
- `assistant-admin users --help`: 실행 확인
- `assistant-admin memories --help`: 실행 확인
- `assistant-admin deleted --help`: 실행 확인
- `assistant-admin undelete --help`: 실행 확인
- `assistant-admin ingest --help`: 실행 확인
- `assistant-admin route`: 실행 확인
- `assistant-admin ask --help`: 실행 확인
- `assistant-admin snapshot --help`: 실행 확인
- `assistant-admin conversations --help`: 실행 확인
- `assistant-admin clear-conversation --help`: 실행 확인
- `assistant-admin tasks --help`: 실행 확인
- `assistant-admin reminders --help`: 실행 확인
- `assistant-admin tasks`: 추가, 조회, 오늘까지 필터, 제목/우선순위 수정, 미루기, 완료, 다시 열기, 삭제 항목 조회, 복구 실행 확인
- `assistant-admin route "최근 대화에서 할 일 뽑아서 추가해줘"`: 실행 확인
- `assistant-admin route "그거 할 일로 추가해줘"`: 실행 확인
- `assistant-admin route "30분 뒤 다시 알려줘"`: `manage_reminder` 실행 확인
- `assistant-admin briefing --help`: 실행 확인
- `assistant-admin briefing`: 실행 확인
- 발송 대기 알림 전송 함수: fake destination으로 실행 확인
- `assistant-admin cleanup --help`: 실행 확인
- `assistant-admin openai-check --help`: 실행 확인
- `assistant-admin logs --help`: 실행 확인
- `assistant-admin restore --help`: 실행 확인

## 가정

- 첫 버전은 로컬에서 실행한다.
- 봇은 모든 채널 메시지를 듣지 않는다.
- 장기 기억은 명시적 사용자 의도가 있을 때만 저장한다.
- 컨텍스트 압축은 내부 대화 연속성을 위한 것이며 명시적 사용자 기억과 분리한다.
- v1은 기억, 파일 회상, 개인 할 일 관리에 집중한다.
- 일정, 코딩, 리서치 같은 향후 전문 에이전트도 같은 라우팅 및 모델 선택 인터페이스를 구현한다.

## 대화형 비서 말투 통일 원칙

- 모든 에이전트는 개별 성격을 갖지 않고, 하나의 공통 비서 persona 뒤에서 기능만 수행한다.
- 기본 말투는 친근한 존댓말이며, 반말과 딱딱한 시스템 안내문 말투는 사용하지 않는다.
- 에이전트는 가능한 한 사용자-facing 완성 문장보다 실행 결과, 상태, ID, 시간, 목록 같은 구조화 데이터를 반환한다.
- 최종 사용자 답변은 공통 `ResponseComposer`가 공통 persona와 최근 대화 맥락을 기준으로 작성한다.
- 새 에이전트를 추가할 때도 `OperationResult` 기반 반환을 우선 사용하고, 레거시 문자열 반환은 임시 호환용으로만 둔다.
- 정확성이 필요한 ID, 숫자, 파일명, 상태, 예약 시각은 구조화 필드에 보존하고, 표현만 자연스럽게 바꾼다.
- 현재 `ReminderAgent`, `UtilityAgent`, `TaskAgent`의 주요 사용자-facing 경로는 `OperationResult` 기반으로 전환했다.
- 남은 핵심 전환 대상은 `MemoryAgent`와 일부 예외/오류 fallback 경로다.
