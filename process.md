# 작업 기록

이 파일은 프로젝트에서 수행한 작업을 기록한다. 앞으로 모든 작업은 작업 이름, 진행상황, 진행내용을 포함해 새 항목으로 추가한다.

## 2026-06-04 - 초기 계획 문서화

- 작업 이름: 초기 비서 계획 문서화
- 진행상황: 완료
- 진행내용:
  - Discord 대화형 범용 비서 v1 방향을 `plan.md`에 작성했다.
  - 대화형 UX, 명시적 기억 정책, 에이전트 구조, 모델 라우팅 전략, 저장소 가정, 동작 정책, 테스트 계획을 정리했다.
  - 이후 구현과 계획 작업을 기록할 `process.md`를 만들었다.

## 2026-06-04 - 개발 브랜치 설정

- 작업 이름: `develop` 브랜치 생성 및 전환
- 진행상황: 완료
- 진행내용:
  - 현재 작업 상태를 기준으로 `develop` 브랜치를 생성했다.
  - 구현을 `develop` 브랜치에서 시작할 수 있도록 작업공간을 전환했다.
  - 기존 계획 문서는 이후 staging 및 commit 대상으로 작업 트리에 유지했다.

## 2026-06-04 - 문서 언어 기준 정리

- 작업 이름: 문서 한글화
- 진행상황: 완료
- 진행내용:
  - 모든 문서를 한글로 작성한다는 기준을 반영했다.
  - `plan.md`의 설명, 제목, 정책, 테스트 계획을 한글로 변경했다.
  - `process.md`의 작업 기록 형식과 기존 기록을 한글로 변경했다.
  - 구현 식별자로 쓰이는 모델명, 환경 변수, intent 값은 그대로 유지했다.

## 2026-06-04 - Python MVP 구현

- 작업 이름: Discord 대화형 범용 비서 MVP 구현
- 진행상황: 완료
- 진행내용:
  - 기술 스택을 Python으로 확정하고 Node/TypeScript 초안 파일을 제거했다.
  - `discord.py`, OpenAI SDK, Python 표준 `sqlite3`, `pypdf` 기반 프로젝트를 구성했다.
  - 멘션, 답글, DM에만 응답하는 Discord 봇 진입점을 구현했다.
  - `Router Agent`, `Conversation Agent`, `Memory Agent`를 구현했다.
  - 라우터는 `gpt-5.4-mini`를 사용하고, 전문 에이전트는 난이도와 사용자 선호에 따라 모델을 선택하도록 구현했다.
  - 명시적 기억 요청이 있을 때만 텍스트 메모와 지원 첨부 파일을 저장하도록 구현했다.
  - `.txt`, `.md`, `.pdf` 첨부 텍스트 추출, chunking, embedding 저장, 의미 유사도 검색을 구현했다.
  - 대화 컨텍스트 저장과 설정 기준 초과 시 압축 요약 생성을 구현했다.
  - Discord 메시지 길이 제한에 맞춘 답변 분할을 구현했다.
  - 실제 비밀값 없이 `.env.example`만 제공했다.
  - `python3 -m pytest`와 `python3 -m ruff check .` 검증을 통과했다.

## 2026-06-04 - 실사용 편의성 보강

- 작업 이름: 기억 관리 기능 보강
- 진행상황: 완료
- 진행내용:
  - 자연어로 저장된 기억 목록과 상태를 확인하는 `list_memory` 라우팅을 추가했다.
  - 텍스트 기억 수, 문서 수, chunk 수와 최근 기억 목록을 조회하는 저장소 기능을 추가했다.
  - 기억 삭제를 ID, 키워드, 의미 검색 후보 기반으로 처리하도록 개선했다.
  - 문서 검색 결과의 ID를 문서 삭제에 바로 사용할 수 있도록 문서 ID 기준으로 보정했다.
  - 첨부 파일 저장 중 일부 파일 오류가 전체 처리를 막지 않도록 파일별 오류 안내를 추가했다.
  - 저장소 목록, 통계, 검색, 삭제 동작 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, import 검증을 통과했다.

## 2026-06-04 - 첨부 저장 확인 흐름 개선

- 작업 이름: 첨부 저장 확인 대기 흐름 구현
- 진행상황: 완료
- 진행내용:
  - 사용자가 지원 첨부 파일만 보낸 경우, 봇이 바로 저장하지 않고 확인 메시지를 보내도록 유지했다.
  - 확인 대기 중인 첨부 메시지 ID와 파일명을 SQLite에 저장하는 `pending_attachment_requests` 테이블을 추가했다.
  - 사용자가 이후 “응, 기억해줘”라고 답하면 원본 첨부 메시지를 다시 가져와 파일을 저장하도록 구현했다.
  - 첨부 저장이 성공한 경우에만 대기 상태를 해소하도록 처리했다.
  - 테스트용 `:memory:` SQLite가 실제 파일로 생성되지 않도록 DB 초기화 처리를 보정했다.
  - pending attachment 저장소 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 도움말과 상태 확인 기능 추가

- 작업 이름: 자연어 도움말 및 상태 확인 구현
- 진행상황: 완료
- 진행내용:
  - `help`와 `status` 라우팅 intent를 추가했다.
  - 사용자가 “도움말 보여줘”, “뭘 할 수 있어?”처럼 물으면 모델 호출 없이 즉시 사용 예시를 안내하도록 구현했다.
  - 사용자가 “상태 확인해줘”처럼 물으면 현재 기억 수, 문서 수, chunk 수, 저장 확인 대기 첨부 수, 모델 설정을 보여주도록 구현했다.
  - pending attachment 저장소에 미해결 대기 요청 개수 조회 기능을 추가했다.
  - 도움말/상태 라우팅과 대기 요청 개수 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 첨부 저장 취소 및 미지원 파일 안내

- 작업 이름: 첨부 저장 취소 흐름과 미지원 첨부 안내 구현
- 진행상황: 완료
- 진행내용:
  - `cancel_pending` 라우팅 intent를 추가했다.
  - 사용자가 “취소해”, “저장하지 마”처럼 말하면 대기 중인 첨부 저장 확인을 해소하도록 구현했다.
  - 첨부 저장 확인 메시지에 저장 취소 방법을 함께 안내하도록 변경했다.
  - 지원하지 않는 첨부 파일만 들어온 경우 `.txt`, `.md`, `.pdf`만 지원한다고 안내하도록 구현했다.
  - pending attachment 해소와 지원 확장자 판별 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 운영 CLI 추가

- 작업 이름: 운영 점검용 CLI 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin doctor`로 환경 변수와 기본 설정을 점검하도록 구현했다.
  - `assistant-admin invite`로 `DISCORD_CLIENT_ID` 기반 Discord 봇 초대 URL을 생성하도록 구현했다.
  - `assistant-admin stats`로 SQLite 저장소의 기억, 문서, 대화, 대기 첨부, 로그 개수를 확인하도록 구현했다.
  - 실제 비밀값은 출력하지 않고 설정 여부만 표시하도록 처리했다.
  - setuptools 패키지 발견 설정을 추가해 콘솔 스크립트가 설치 후 패키지를 찾지 못하는 문제를 해결했다.
  - CLI helper 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin doctor`, `assistant-admin invite`, `assistant-admin stats` 실행을 확인했다.

## 2026-06-04 - 기억 상세 조회 기능 추가

- 작업 이름: 메모/문서 ID 기반 상세 조회 구현
- 진행상황: 완료
- 진행내용:
  - `메모 3 보여줘`, `문서 2 보여줘` 같은 자연어 요청에서 ID를 추출하도록 구현했다.
  - ID 기반 조회는 embedding 검색이나 모델 호출보다 먼저 처리해 비용과 오탐을 줄였다.
  - SQLite 저장소에 텍스트 메모 상세 조회와 문서 상세 조회 기능을 추가했다.
  - 긴 문서 상세 조회는 Discord에서 읽기 좋게 앞부분만 보여주고, 추가 질문으로 이어가도록 안내한다.
  - 상세 조회와 ID 추출 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 사용자 단위 전역 기억과 위치 인지 반영

- 작업 이름: 위치가 바뀌어도 이어지는 사용자 기억 구현
- 진행상황: 완료
- 진행내용:
  - 같은 사용자의 장기 기억은 DM, 서버, 스레드 어디서든 이어지도록 저장소 조회 범위를 사용자 단위로 정리했다.
  - 목록과 상세 조회에는 해당 기억이 DM에서 저장됐는지 서버에서 저장됐는지 위치 힌트를 표시하도록 구현했다.
  - 일반 대화 에이전트 입력에 현재 대화 위치를 포함해, 위치가 바뀐 상황을 답변에서 고려할 수 있도록 했다.
  - 상태 확인 응답에 현재 대화 위치를 표시하도록 구현했다.
  - 같은 사용자의 DM/서버 기억이 함께 유지되는지 검증하는 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 기억 export CLI 추가

- 작업 이름: 저장된 기억 JSON 내보내기 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin export` 명령으로 저장된 텍스트 기억과 문서를 JSON으로 내보내도록 구현했다.
  - `--output` 옵션을 제공해 파일 저장과 stdout 출력을 모두 지원하도록 했다.
  - export 결과에는 메모/문서 텍스트, 생성 시각, 저장 위치, source message ID를 포함했다.
  - embedding 벡터는 export에서 제외해 결과를 사람이 읽고 백업하기 쉽게 유지했다.
  - export 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin export` 실행을 확인했다.

## 2026-06-04 - 기억 검색 CLI 추가

- 작업 이름: 로컬 기억 키워드 검색 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin search <keyword>` 명령으로 저장된 메모와 문서를 키워드 검색하도록 구현했다.
  - 검색은 OpenAI API 호출 없이 로컬 SQLite의 제목, 본문, 파일명, 문서 chunk 텍스트를 대상으로 수행한다.
  - 결과에는 항목 종류, ID, 제목, 저장 위치, 짧은 미리보기를 표시한다.
  - 검색 결과 포맷과 미리보기 생성 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin search` 실행을 확인했다.

## 2026-06-04 - SQLite 백업 CLI 추가

- 작업 이름: SQLite 전체 백업 CLI 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin backup --output <path>` 명령으로 SQLite 저장소 전체를 백업하도록 구현했다.
  - SQLite `backup` API를 사용해 WAL 상태에서도 일관된 사본을 만들도록 했다.
  - 기본값으로 기존 백업 파일을 덮어쓰지 않고, `--overwrite` 옵션이 있을 때만 덮어쓰도록 했다.
  - JSON export와 달리 embedding, 대화, 로그, 대기 첨부 테이블까지 전체 DB를 보존한다.
  - 백업 파일 생성과 덮어쓰기 방지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin backup` 실행을 확인했다.

## 2026-06-04 - SQLite 복구 CLI 추가

- 작업 이름: SQLite 백업 복구 CLI 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin restore --input <path> --force` 명령으로 SQLite 백업 파일을 현재 저장소로 복구하도록 구현했다.
  - `--force` 없이는 복구하지 않도록 해 실수로 현재 저장소를 교체하는 일을 막았다.
  - 복구 전에 현재 저장소를 `pre-restore` 안전 백업 파일로 자동 저장하도록 구현했다.
  - 복구 대상 백업 파일 존재 여부를 확인하도록 했다.
  - 복구 후 대상 DB가 백업 내용으로 바뀌고 안전 백업이 기존 내용을 보존하는지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin restore --help` 실행을 확인했다.

## 2026-06-04 - 텍스트 메모 수정 기능 추가

- 작업 이름: 자연어 기반 기억 수정 구현
- 진행상황: 완료
- 진행내용:
  - 라우터에 `update_memory` intent를 추가해 “수정해”, “바꿔”, “고쳐” 같은 표현을 기억 수정 요청으로 분류하도록 했다.
  - `메모 3을 ...로 수정해줘`처럼 ID를 지정한 텍스트 메모 수정 기능을 구현했다.
  - ID가 없을 때는 관련 키워드로 저장된 텍스트 메모를 검색하고, 충분히 확실한 후보가 하나일 때만 수정하도록 했다.
  - 수정된 메모는 제목, 본문, embedding을 함께 갱신해 이후 의미 검색이 새 내용 기준으로 동작하도록 했다.
  - 문서 내용 직접 수정은 아직 지원하지 않고, 새 문서 저장 후 기존 문서 삭제 흐름을 안내하도록 했다.
  - 도움말과 README 사용 예시에 기억 수정 문장을 추가했다.
  - 라우팅, 수정 문장 추출, 저장소 수정 동작 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 에이전트 로그 조회 CLI 추가

- 작업 이름: 최근 라우팅 및 모델 선택 로그 조회 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin logs` 명령으로 최근 `agent_logs`를 조회하도록 구현했다.
  - `--limit`, `--agent`, `--conversation-id` 옵션을 추가해 특정 에이전트나 대화 단위로 로그를 좁혀 볼 수 있게 했다.
  - 출력에는 로그 ID, 생성 시각, 에이전트, intent, 난이도, 선택 모델, conversation_id, 선택 이유를 포함했다.
  - 운영 중 라우터가 어떤 intent를 골랐는지, 전문 에이전트가 어떤 모델을 골랐는지 확인할 수 있게 했다.
  - 로그 조회와 빈 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin logs --help` 실행을 확인했다.

## 2026-06-04 - 텍스트 메모 중복 저장 방지 추가

- 작업 이름: 동일 텍스트 기억 중복 저장 방지 구현
- 진행상황: 완료
- 진행내용:
  - 텍스트 메모 저장 전에 같은 사용자의 기존 기억을 정규화된 본문 기준으로 비교하도록 구현했다.
  - 공백과 대소문자 차이만 있는 동일 메모는 새로 저장하지 않고 기존 메모 ID와 저장 위치를 안내하도록 했다.
  - 중복 판정은 같은 사용자 기준으로만 수행해 다른 사용자의 기억과 섞이지 않도록 했다.
  - 중복 저장 방지 시에도 에이전트 로그에 이유를 남기도록 했다.
  - 저장소 중복 탐지 테스트와 Memory Agent 중복 저장 방지 응답 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 문서 중복 저장 방지 추가

- 작업 이름: 동일 문서 내용 중복 저장 방지 구현
- 진행상황: 완료
- 진행내용:
  - `documents` 테이블에 `content_hash` 컬럼을 추가하는 마이그레이션을 구현했다.
  - 문서 본문을 줄 단위로 정규화한 뒤 SHA-256 해시를 저장하도록 했다.
  - 같은 사용자가 같은 문서 내용을 다시 저장하려고 하면 새 문서를 만들지 않고 기존 문서 ID와 저장 위치를 안내하도록 했다.
  - 기존 DB에서 `content_hash`가 없는 문서도 chunk 텍스트를 재구성해 동일 내용 여부를 확인할 수 있도록 했다.
  - 중복 문서 저장 방지 시에도 에이전트 로그에 이유를 남기도록 했다.
  - 문서 해시 저장과 동일 문서 탐지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - OpenAI 연결 점검 CLI 추가

- 작업 이름: OpenAI 모델 연결 점검 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin openai-check` 명령으로 OpenAI 텍스트 응답 모델과 embedding 모델 연결을 점검하도록 구현했다.
  - `OPENAI_API_KEY`가 없으면 실제 호출을 하지 않고 설정 안내와 함께 실패하도록 했다.
  - 점검 출력에는 텍스트 응답 모델, embedding 모델, embedding 차원, 전체 통과 여부를 표시한다.
  - 실제 비밀값은 출력하지 않도록 했다.
  - 네트워크 호출 없이 검증할 수 있도록 fake OpenAI client 기반 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin openai-check --help` 실행을 확인했다.

## 2026-06-04 - 최근 기억 목록 CLI 추가

- 작업 이름: 최근 저장 기억 목록 조회 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin memories` 명령으로 최근 저장된 텍스트 메모와 문서를 한 줄 요약 목록으로 조회하도록 구현했다.
  - `--limit`, `--user-id`, `--kind memory|document|all` 옵션을 추가해 운영 중 특정 사용자나 항목 종류만 빠르게 확인할 수 있게 했다.
  - 출력에는 항목 종류, ID, 제목, user_id, 저장 위치, 생성 시각, 짧은 미리보기를 포함했다.
  - 문서 항목은 chunk 개수도 함께 표시하도록 했다.
  - 최근 기억 목록 조회, user_id 필터링, 종류 필터링, 빈 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin memories --help` 실행을 확인했다.

## 2026-06-04 - 오래된 운영 기록 정리 CLI 추가

- 작업 이름: 보존 기간 기반 대화 및 로그 정리 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin cleanup` 명령으로 오래된 대화 메시지, 대화 요약, 에이전트 로그, 해결된 첨부 대기 요청을 정리하도록 구현했다.
  - `--days`로 최근 보존 일수를 지정하고, `--target all|conversations|logs|pending`으로 정리 대상을 좁힐 수 있게 했다.
  - 기본 동작은 삭제하지 않는 미리보기이며, `--force`가 있을 때만 실제 삭제하도록 했다.
  - 장기 기억과 문서는 정리 대상에서 제외해 사용자의 명시적 기억을 보존하도록 했다.
  - 해결되지 않은 첨부 대기 요청은 오래되어도 삭제하지 않도록 했다.
  - 미리보기와 실제 삭제 동작 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin cleanup --help` 실행을 확인했다.

## 2026-06-04 - OpenAI 호출 안정성 보강

- 작업 이름: OpenAI timeout 및 재시도 설정 구현
- 진행상황: 완료
- 진행내용:
  - `OPENAI_TIMEOUT_SECONDS`, `OPENAI_MAX_RETRIES` 환경 변수 예시를 `.env.example`에 추가했다.
  - OpenAI SDK 자체 재시도는 끄고, 앱 레벨에서 텍스트 응답과 embedding 호출을 동일한 정책으로 재시도하도록 구현했다.
  - 기본 timeout은 30초, 기본 재시도 횟수는 2회로 설정했다.
  - `assistant-admin doctor`가 OpenAI timeout과 재시도 설정 값이 올바른지 검사하도록 보강했다.
  - fake OpenAI client 기반으로 텍스트 응답 재시도, embedding 재시도, 재시도 한도 초과 시 예외 전파 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 사용자 전체 기억 삭제 기능 추가

- 작업 이름: 사용자 기준 장기 기억 전체 삭제 구현
- 진행상황: 완료
- 진행내용:
  - `내 기억 전부 삭제해줘`, `모든 문서와 메모를 지워줘` 같은 명확한 전체 삭제 요청을 감지하도록 구현했다.
  - 전체 삭제는 현재 사용자 기준의 텍스트 메모와 문서를 soft-delete 처리하며, 다른 사용자의 기억은 보존하도록 했다.
  - 운영 로그와 대화 기록은 장기 기억이 아니므로 전체 기억 삭제 대상에서 제외했다.
  - 도움말과 README 사용 예시에 전체 삭제 문장을 추가했다.
  - 전체 삭제 감지, 저장소 전체 삭제, Memory Agent 응답 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 전체 기억 삭제 확인 단계 추가

- 작업 이름: 전체 기억 삭제 확인 대기 흐름 구현
- 진행상황: 완료
- 진행내용:
  - `pending_memory_deletions` 테이블과 저장소를 추가해 전체 기억 삭제 요청을 즉시 실행하지 않고 확인 대기 상태로 저장하도록 했다.
  - 사용자가 `내 기억 전부 삭제해줘`라고 말하면 대상 메모/문서 수를 안내하고, `응, 전부 삭제해` 같은 답장으로 확정해야 삭제하도록 구현했다.
  - `취소해`, `아니` 같은 답장을 받으면 전체 삭제 대기 상태를 해소하고 삭제하지 않도록 했다.
  - `assistant-admin stats`와 상태 응답에 삭제 확인 대기 기억 개수를 표시하도록 했다.
  - Memory Agent가 직접 호출되어도 전체 삭제를 즉시 실행하지 않고 확인 필요 응답을 반환하도록 보강했다.
  - 삭제 확인 대기 저장소, CLI 통계, 확인 문장 판별, 안전한 Memory Agent 응답 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 삭제 확인 만료 시간 추가

- 작업 이름: 전체 기억 삭제 확인 TTL 구현
- 진행상황: 완료
- 진행내용:
  - `PENDING_CONFIRMATION_TTL_MINUTES` 환경 변수 예시를 `.env.example`에 추가했다.
  - 전체 기억 삭제 확인 대기 요청은 기본 10분 안에 확정해야 하도록 구현했다.
  - 만료된 삭제 확인 요청은 자동으로 해소하고, 이후 `응, 전부 삭제해` 같은 답장이 와도 삭제하지 않도록 했다.
  - 상태 응답과 `assistant-admin stats`의 삭제 확인 대기 개수는 만료된 요청을 제외하도록 했다.
  - `assistant-admin doctor`가 TTL 값이 양의 정수인지 검사하도록 보강했다.
  - 삭제 확인 대기 만료 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 첨부 텍스트 품질 검증 강화

- 작업 이름: 깨진 텍스트 및 무의미한 첨부 저장 방지 구현
- 진행상황: 완료
- 진행내용:
  - `.txt`, `.md` 첨부는 UTF-8로 엄격하게 디코딩하도록 변경했다.
  - UTF-8로 읽을 수 없는 텍스트 파일은 저장하지 않고 사용자에게 파일별 오류로 안내하도록 했다.
  - 추출 텍스트에 한글, 영문, 숫자 중 하나도 없는 경우 의미 있는 텍스트가 없다고 판단해 저장하지 않도록 했다.
  - PDF도 추출된 텍스트 기준으로 의미 있는 문자 검사를 적용한다.
  - 깨진 UTF-8, 기호뿐인 텍스트, 정상 텍스트 추출 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 사용자별 기억 export 필터 추가

- 작업 이름: user_id 기준 기억 JSON 내보내기 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin export --user-id <id>` 옵션을 추가해 특정 Discord 사용자 기억만 JSON으로 내보낼 수 있게 했다.
  - 기존 전체 export 구조는 유지하면서, 결과 payload에 적용된 `user_id` 필터 값을 포함하도록 했다.
  - user_id 필터가 적용된 경우 다른 사용자의 메모와 문서가 export 결과에 포함되지 않도록 했다.
  - embedding 벡터는 기존처럼 export에서 제외한다.
  - 사용자별 export 필터 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin export --help` 실행을 확인했다.

## 2026-06-04 - 전체 기억 삭제 확인 문구 강화

- 작업 이름: 파괴적 삭제 확인 문구 안전성 보강
- 진행상황: 완료
- 진행내용:
  - 전체 기억 삭제 대기 상태에서 `응`, `ok` 같은 짧은 긍정만으로 삭제가 실행되지 않도록 전용 확인 판별 함수를 추가했다.
  - 전체 삭제 확정은 삭제 의사와 전체 범위 표현이 함께 들어간 답장일 때만 통과하도록 제한했다.
  - `응, 전부 삭제해`, `네, 모두 지워줘`, `yes delete all`은 허용하고, `응`, `ok`, `삭제해`, `메모 삭제해`는 거부하는 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 최근 저장 항목 삭제 기능 추가

- 작업 이름: 실수 복구용 최근 기억 삭제 구현
- 진행상황: 완료
- 진행내용:
  - `방금 저장한 거 지워줘`, `최근 기억 삭제해줘`, `delete last memory` 같은 표현을 최근 저장 항목 삭제 요청으로 판별하도록 했다.
  - 같은 사용자 기준으로 가장 최근 저장된 텍스트 메모 또는 문서 1개만 soft-delete 처리하는 저장소 기능을 추가했다.
  - 다른 사용자의 기억은 삭제하지 않고, 삭제된 항목의 종류와 ID를 사용자에게 안내하도록 했다.
  - 봇 도움말과 README 사용 예시에 최근 저장 항목 삭제 문장을 추가했다.
  - 최근 항목 삭제 저장소 동작, 에이전트 응답, 자연어 판별 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 로컬 대화 점검 CLI 추가

- 작업 이름: Discord 없이 에이전트 흐름 점검 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin route <message>` 명령으로 OpenAI 호출 없이 휴리스틱 라우팅 intent, confidence, reason을 확인하도록 했다.
  - `assistant-admin ask <message>` 명령으로 Discord를 켜기 전에 실제 Router Agent, Memory Agent, Conversation Agent, OpenAI, SQLite 저장소 흐름을 로컬에서 실행하도록 했다.
  - 로컬 실행은 `--user-id`, `--conversation-id`, `--channel-id`, `--guild-id`, `--author-name` 옵션으로 사용자와 위치를 흉내낼 수 있게 했다.
  - 로컬 실행에서도 사용자 기준 기억, 현재 위치 라벨, 전체 삭제 확인 대기/취소/확정 흐름을 유지하도록 했다.
  - `OPENAI_API_KEY`가 없으면 traceback 대신 설정 안내를 출력하도록 했다.
  - 라우팅 미리보기 출력과 로컬 실행 설정 로딩 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route`, `assistant-admin ask --help`, `assistant-admin ask "도움말"` 실행을 확인했다.

## 2026-06-04 - 로컬 파일 기억 CLI 추가

- 작업 이름: Discord 없이 로컬 파일 문서 저장 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin ingest <path...>` 명령으로 로컬 `.txt`, `.md`, `.pdf` 파일을 사용자 장기 기억 문서로 저장하도록 했다.
  - 로컬 파일 저장도 Discord 첨부와 같은 UTF-8, 파일 크기, 의미 있는 텍스트, 지원 확장자 검사를 사용하도록 했다.
  - `--user-id`, `--guild-id` 옵션으로 저장 대상 사용자와 위치를 지정할 수 있게 했다.
  - 같은 사용자 기준으로 동일 문서 내용은 중복 저장하지 않고 기존 문서 ID를 안내하도록 했다.
  - 로컬 파일 추출, 저장 결과 포맷, 로컬 파일 저장 및 중복 방지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin ingest --help` 실행을 확인했다.

## 2026-06-04 - 최근 삭제 항목 복구 기능 추가

- 작업 이름: 삭제 기억 복구 흐름 구현
- 진행상황: 완료
- 진행내용:
  - `restore_memory` intent를 추가해 `방금 지운 거 복구해줘`, `restore` 같은 표현을 삭제 기억 복구 요청으로 분류하도록 했다.
  - 같은 사용자 기준으로 가장 최근 삭제된 텍스트 메모 또는 문서 1개를 복구하는 저장소 기능을 추가했다.
  - Discord 대화 처리와 로컬 `assistant-admin ask` 모두 같은 복구 경로를 사용하도록 연결했다.
  - 봇 도움말과 README 사용 예시에 최근 삭제 항목 복구 문장을 추가했다.
  - 최근 삭제 항목 복구 저장소 동작, 에이전트 응답, 자연어 라우팅 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 지운 거 복구해줘"` 실행을 확인했다.

## 2026-06-04 - 삭제 기억 목록 및 ID 복구 기능 추가

- 작업 이름: 삭제 항목 목록 조회와 선택 복구 구현
- 진행상황: 완료
- 진행내용:
  - `삭제한 기억 목록 보여줘`처럼 말하면 최근 삭제된 메모와 문서를 ID, 제목, 저장 위치, 삭제 시각과 함께 보여주도록 했다.
  - `메모 3 복구해줘`, `문서 2 복구해줘`처럼 삭제된 항목 ID를 지정해 복구할 수 있도록 했다.
  - 최근 삭제 항목 복구는 유지하되, 목록 확인 후 원하는 항목만 복구할 수 있는 흐름을 추가했다.
  - 삭제 항목 목록 조회, ID 기반 복구 저장소 동작, 에이전트 응답, 자연어 판별과 라우팅 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "삭제한 기억 목록 보여줘"` 실행을 확인했다.

## 2026-06-04 - 사용자별 기억 현황 CLI 추가

- 작업 이름: 사용자별 저장소 현황 조회 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin users` 명령으로 user_id별 활성 텍스트 메모 수, 문서 수, 삭제된 기억 수, 최근 저장 시각을 조회하도록 했다.
  - 운영자가 특정 사용자 기억을 export, memories, search로 확인하기 전에 어떤 user_id가 저장소에 있는지 빠르게 파악할 수 있게 했다.
  - 사용자별 현황 조회와 빈 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin users --help` 실행을 확인했다.

## 2026-06-04 - 현재 대화 맥락 초기화 기능 추가

- 작업 이름: 대화 컨텍스트 리셋 구현
- 진행상황: 완료
- 진행내용:
  - `reset_context` intent를 추가해 `대화 맥락 초기화해줘`, `clear context` 같은 표현을 현재 대화 맥락 초기화 요청으로 분류하도록 했다.
  - 현재 conversation_id의 `conversation_messages`와 `conversation_summaries`만 삭제하고, 다른 대화와 장기 기억은 유지하도록 했다.
  - Discord 대화 처리와 로컬 `assistant-admin ask` 모두 같은 초기화 경로를 사용하도록 연결했다.
  - 봇 도움말과 README 사용 예시에 대화 맥락 초기화 문장을 추가했다.
  - 대화 저장소 초기화 범위와 자연어 라우팅 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "대화 맥락 초기화해줘"` 실행을 확인했다.

## 2026-06-04 - 사용자별 기억 검색 필터 추가

- 작업 이름: search CLI user_id 필터 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin search <keyword> --user-id <id>` 옵션을 추가해 특정 사용자의 저장 기억과 문서만 키워드 검색할 수 있게 했다.
  - 검색 결과에 user_id를 함께 표시해 전체 검색과 사용자 필터 검색을 운영자가 구분하기 쉽게 했다.
  - 사용자별 검색 필터 테스트와 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin search 운동 --user-id user-1 --limit 5` 실행을 확인했다.

## 2026-06-04 - 삭제 기억 목록 CLI 추가

- 작업 이름: deleted CLI 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin deleted` 명령으로 삭제된 텍스트 메모와 문서를 목록으로 조회하도록 했다.
  - `--user-id`, `--kind memory|document|all`, `--limit` 옵션으로 특정 사용자와 항목 종류만 확인할 수 있게 했다.
  - 출력에는 항목 종류, ID, 제목, user_id, 저장 위치, 삭제 시각, 미리보기를 포함하고, 대화에서 ID로 복구하는 방법을 안내하도록 했다.
  - 삭제 기억 목록 조회, user_id 필터링, 종류 필터링, 빈 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin deleted --help` 실행을 확인했다.

## 2026-06-04 - 삭제 기억 CLI 복구 명령 추가

- 작업 이름: undelete CLI 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin undelete --user-id <id> --memory-id <id>`와 `--document-id <id>` 옵션으로 삭제된 메모와 문서를 운영 CLI에서 복구하도록 했다.
  - 복구 대상 ID를 하나도 지정하지 않으면 traceback 대신 안내 메시지와 실패 코드로 종료하도록 했다.
  - 복구 결과에는 요청 ID와 실제 복구된 메모/문서 개수를 표시하도록 했다.
  - 삭제 기억 CLI 복구 동작, 결과 포맷, ID 누락 검증 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin undelete --help` 실행을 확인했다.

## 2026-06-04 - 대화 컨텍스트 현황 CLI 추가

- 작업 이름: conversations CLI 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin conversations` 명령으로 conversation_id별 메시지 수, 요약 수, 최근 메시지 시각, 최근 요약 시각, 마지막 메시지 미리보기를 조회하도록 했다.
  - `logs --conversation-id`나 대화 맥락 초기화 전 어떤 conversation_id가 활성화되어 있는지 운영자가 확인할 수 있게 했다.
  - 대화 컨텍스트 조회와 빈 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin conversations --help` 실행을 확인했다.

## 2026-06-04 - 대화 컨텍스트 CLI 초기화 추가

- 작업 이름: clear-conversation CLI 구현
- 진행상황: 완료
- 진행내용:
  - `assistant-admin clear-conversation --conversation-id <id>` 명령으로 특정 대화 컨텍스트의 메시지와 요약만 삭제하도록 했다.
  - 장기 기억과 문서는 삭제하지 않고, 다른 conversation_id의 대화 기록도 유지하도록 했다.
  - `assistant-admin conversations`로 conversation_id를 확인한 뒤 CLI에서 바로 초기화할 수 있게 안내 문구를 보강했다.
  - 대화 컨텍스트 CLI 초기화 동작, 장기 기억 보존, 빈 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin clear-conversation --help` 실행을 확인했다.

## 2026-06-04 - 사용자별 할 일 관리 기능 추가

- 작업 이름: Task Agent와 tasks CLI 구현
- 진행상황: 완료
- 진행내용:
  - `tasks` SQLite 테이블과 `TaskStore`를 추가해 사용자별 할 일을 저장, 조회, 완료, 삭제하도록 했다.
  - `manage_task` 라우팅 intent와 `TaskAgent`를 추가해 `할 일 추가`, `할 일 목록`, `할 일 3 완료`, `할 일 4 삭제` 같은 자연어 요청을 처리하도록 했다.
  - 할 일은 사용자 기준으로 유지하되 저장 위치 힌트를 제공해 DM, 서버, 스레드 이동을 인지할 수 있게 했다.
  - `assistant-admin tasks` 명령으로 Discord 없이 사용자별 할 일을 조회, 추가, 완료, 삭제할 수 있게 했다.
  - 상태 응답과 도움말에 열린 할 일 수와 사용 예시를 추가했다.
  - 할 일 라우팅, 날짜/ID 파싱, 저장소 동작, 운영 CLI 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin tasks --help`와 임시 SQLite에서 할 일 추가, 조회, 완료 실행을 확인했다.

## 2026-06-04 - 할 일 자동 리마인더 추가

- 작업 이름: 기한 도래 작업 리마인더 구현
- 진행상황: 완료
- 진행내용:
  - `tasks` 테이블에 `channel_id`와 `reminder_sent_at` 컬럼을 추가해 할 일이 저장된 위치와 리마인드 발송 여부를 추적하도록 했다.
  - 봇이 준비되면 `TASK_REMINDER_INTERVAL_MINUTES` 주기로 기한이 오늘이거나 지난 열린 할 일을 조회하도록 했다.
  - 리마인더는 저장된 채널로 우선 전송하고, 채널을 찾지 못하면 사용자 DM으로 전송을 시도하도록 했다.
  - 전송에 성공한 할 일만 `reminder_sent_at`을 기록해 같은 항목이 반복 발송되지 않도록 했다.
  - `.env.example`에 `TASK_REMINDER_INTERVAL_MINUTES`, `TASK_REMINDER_BATCH_SIZE` 기본 예시를 추가했다.
  - 기한 도래 할 일 조회, 발송 표시, fake destination 기반 전송 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-04 - 할 일 미루기 기능 추가

- 작업 이름: 작업 snooze 및 리마인더 재예약 구현
- 진행상황: 완료
- 진행내용:
  - `할 일 3 내일 다시 알려줘`, `3번 내일 다시 알려줘` 같은 자연어를 할 일 미루기 요청으로 처리하도록 했다.
  - `TaskStore.postpone`을 추가해 열린 할 일의 `due_at`을 변경하고 `reminder_sent_at`을 비워 리마인더를 다시 예약하도록 했다.
  - `assistant-admin tasks --postpone <id> --due <date>` 명령으로 운영 CLI에서도 할 일을 미룰 수 있게 했다.
  - 미루기 대상 ID나 새 기한이 없을 때 사용자에게 구체적인 예시를 안내하도록 했다.
  - 자연어 ID 추출, 리마인더 재예약, CLI 미루기 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `assistant-admin tasks` 할 일 추가와 미루기 실행을 확인했다.

## 2026-06-04 - 오늘까지 할 일 조회 기능 추가

- 작업 이름: 기한 기준 할 일 조회 구현
- 진행상황: 완료
- 진행내용:
  - `TaskStore.list_due`를 추가해 사용자별 열린 할 일 중 특정 날짜까지인 항목만 조회하도록 했다.
  - `오늘 할 일 뭐야?`, `기한 지난 할 일 보여줘` 같은 자연어를 오늘까지 처리할 할 일 조회로 처리하도록 했다.
  - `assistant-admin tasks --due-before <date>` 옵션으로 운영 CLI에서도 기한 기준 목록을 확인할 수 있게 했다.
  - 전체 할 일 목록과 오늘까지 할 일 목록의 응답 문구를 분리해 사용자가 바로 다음 행동을 고를 수 있게 했다.
  - 라우팅, 저장소 기한 필터, CLI 기한 필터 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `assistant-admin tasks --due-before` 필터 실행을 확인했다.

## 2026-06-04 - 최근 대화 할 일 추출 기능 추가

- 작업 이름: 대화 기반 작업 후보 추출 구현
- 진행상황: 완료
- 진행내용:
  - 최근 대화 메시지에서 `해야`, `필요`, `작성`, `검토`, `공유`, `todo`, `follow up` 같은 후속 작업 후보 표현을 규칙 기반으로 추출하도록 했다.
  - `최근 대화에서 할 일 뽑아줘`는 후보만 보여주고, `최근 대화에서 할 일 뽑아서 추가해줘`는 후보를 열린 할 일로 저장하도록 했다.
  - 열린 할 일에 같은 제목이 이미 있으면 중복 저장하지 않고 기존 항목을 건너뛰도록 했다.
  - 대화 후보 추출은 assistant 응답보다 사용자 메시지를 기준으로 처리해 봇의 안내 문구가 할 일로 저장되지 않게 했다.
  - 후보 추출, 중복 제거, 로컬 대화 기반 할 일 저장 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "최근 대화에서 할 일 뽑아서 추가해줘"` 실행을 확인했다.

## 2026-06-04 - 오늘 브리핑 기능 추가

- 작업 이름: 일일 브리핑 구현
- 진행상황: 완료
- 진행내용:
  - `daily_briefing` 라우팅 intent를 추가해 `오늘 브리핑 해줘` 같은 요청을 별도 유틸리티 흐름으로 처리하도록 했다.
  - 브리핑 응답에는 현재 위치, 열린/완료 할 일 수, 오늘까지 처리할 할 일, 저장 기억 수, 최근 기억을 포함하도록 했다.
  - `assistant-admin briefing --user-id <id>` 명령으로 Discord 없이도 사용자별 브리핑을 SQLite 기준으로 확인할 수 있게 했다.
  - 브리핑 CLI는 OpenAI API 키 없이도 동작하도록 운영용 Config와 NullOpenAIService를 사용한다.
  - 브리핑 라우팅, CLI 브리핑 출력, 기한 도래 작업과 최근 기억 포함 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `assistant-admin briefing` 실행을 확인했다.

## 2026-06-04 - 할 일 제목 수정 기능 추가

- 작업 이름: 작업 제목 rename 구현
- 진행상황: 완료
- 진행내용:
  - `TaskStore.rename`을 추가해 사용자별 열린 할 일 제목을 ID 기준으로 수정하도록 했다.
  - `할 일 3을 고객 미팅 준비로 바꿔줘` 같은 자연어를 할 일 제목 수정 요청으로 처리하도록 했다.
  - `assistant-admin tasks --rename <id> --title <title>` 명령으로 운영 CLI에서도 제목을 수정할 수 있게 했다.
  - 제목 수정 대상 ID나 새 제목이 없을 때 구체적인 예시를 안내하도록 했다.
  - 자연어 제목 추출, 저장소 제목 수정, CLI 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `assistant-admin tasks` 할 일 추가와 제목 수정 실행을 확인했다.

## 2026-06-04 - 할 일 우선순위 기능 추가

- 작업 이름: 작업 priority 구현
- 진행상황: 완료
- 진행내용:
  - `tasks` 테이블에 `priority` 컬럼을 추가하고 기존 데이터는 기본 `normal`로 유지하도록 했다.
  - 할 일 추가 시 `중요`, `긴급`, `높음`, `낮음` 같은 자연어 우선순위 표현을 감지하도록 했다.
  - `할 일 3 중요하게 표시해줘` 같은 요청으로 열린 할 일 우선순위를 수정하도록 했다.
  - `assistant-admin tasks --priority high`와 `--set-priority <id> --priority low` 옵션으로 운영 CLI에서도 우선순위를 지정하고 수정할 수 있게 했다.
  - 목록, 오늘까지 목록, 리마인더, 브리핑에서 우선순위 라벨을 표시하고 높은 우선순위가 먼저 보이도록 정렬했다.
  - 우선순위 저장, 정렬, 자연어 파싱, CLI 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `assistant-admin tasks` 할 일 추가와 우선순위 수정 실행을 확인했다.

## 2026-06-05 - 완료한 할 일 다시 열기 기능 추가

- 작업 이름: 작업 reopen 구현
- 진행상황: 완료
- 진행내용:
  - `TaskStore.reopen`을 추가해 완료된 할 일을 다시 열린 상태로 되돌리고 `completed_at`과 `reminder_sent_at`을 초기화하도록 했다.
  - `할 일 3 다시 열어줘`, `완료 취소` 같은 자연어를 완료 취소 요청으로 처리하도록 했다.
  - `assistant-admin tasks --reopen <id>` 명령으로 운영 CLI에서도 완료한 할 일을 다시 열 수 있게 했다.
  - 다시 열린 할 일은 기존 기한과 우선순위를 유지하면서 리마인더 대상이 될 수 있게 했다.
  - 자연어 ID 추출, 저장소 reopen 동작, CLI 다시 열기 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `assistant-admin tasks` 할 일 추가, 완료, 다시 열기 실행을 확인했다.

## 2026-06-05 - 삭제한 할 일 조회와 복구 기능 추가

- 작업 이름: 작업 soft-delete 복구 구현
- 진행상황: 완료
- 진행내용:
  - `TaskStore.list_deleted`, `TaskStore.restore`, `TaskStore.restore_latest_deleted`를 추가해 삭제한 할 일을 조회하고 다시 복구하도록 했다.
  - `삭제한 할 일 목록 보여줘`, `할 일 3 복구해줘`, `방금 삭제한 할 일 복구해줘` 같은 자연어를 할 일 복구 흐름으로 처리하도록 했다.
  - 복구된 할 일은 삭제 전 상태, 기한, 우선순위를 유지하도록 했다.
  - `assistant-admin tasks --deleted`와 `assistant-admin tasks --restore <id>` 명령으로 운영 CLI에서도 삭제 항목 확인과 복구를 할 수 있게 했다.
  - 저장소 복구 동작, 자연어 파싱, CLI 삭제 목록/복구 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `assistant-admin tasks` 할 일 추가, 삭제, 삭제 항목 조회, 복구 실행을 확인했다.

## 2026-06-05 - 데이터 export에 할 일 포함

- 작업 이름: 운영 export 범위 확장
- 진행상황: 완료
- 진행내용:
  - `assistant-admin export` 결과에 `tasks` 배열을 추가해 열린 할 일, 완료한 할 일, 삭제한 할 일을 함께 내보내도록 했다.
  - 할 일 export 항목에 user_id, conversation_id, channel_id, 저장 위치, 제목, 상태, 우선순위, 기한, source message ID, 생성/완료/리마인드/삭제 시각을 포함했다.
  - `--user-id` 필터가 메모, 문서뿐 아니라 할 일에도 동일하게 적용되도록 했다.
  - embedding 벡터는 기존처럼 export에서 제외한다.
  - 전체 export와 user_id 기준 export 테스트를 할 일 데이터까지 확장했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `assistant-admin tasks` 할 일 추가 후 `assistant-admin export --user-id <id>` 결과에 `tasks`가 포함되는지 확인했다.

## 2026-06-05 - 사용자별 데이터 현황에 할 일 포함

- 작업 이름: users CLI 통계 범위 확장
- 진행상황: 완료
- 진행내용:
  - `assistant-admin users`가 메모와 문서뿐 아니라 할 일만 있는 사용자도 표시하도록 `tasks` 테이블을 사용자 목록 기준에 포함했다.
  - 사용자별 현황에 활성 할 일 수를 추가하고, 삭제된 메모/문서/할 일을 삭제 항목 수로 합산하도록 했다.
  - 최근 저장 시각 계산에 활성 할 일 생성 시각도 포함했다.
  - 출력 제목을 `사용자별 데이터 현황`으로 바꿔 기억 외 데이터까지 포함한다는 점을 명확히 했다.
  - 할 일만 있는 사용자가 누락되지 않는지 확인하는 CLI 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 할 일만 있는 사용자를 만든 뒤 `assistant-admin users` 출력에 표시되는지 확인했다.

## 2026-06-05 - 직접 할 일 추가 중복 방지

- 작업 이름: 열린 할 일 중복 생성 방지
- 진행상황: 완료
- 진행내용:
  - 자연어 대화로 할 일을 직접 추가할 때 같은 사용자에게 같은 제목의 열린 할 일이 이미 있으면 새로 저장하지 않고 기존 할 일 ID를 안내하도록 했다.
  - `assistant-admin tasks --add`도 같은 기준으로 중복 열린 할 일을 만들지 않고 기존 ID를 안내하도록 했다.
  - 중복 판정은 같은 사용자, 열린 상태, 제목의 앞뒤 공백과 대소문자를 정규화한 동일 제목 기준으로 수행한다.
  - 완료됐거나 삭제된 할 일은 다시 추가할 수 있게 유지했다.
  - 대화형 Task Agent 중복 응답 테스트와 CLI 중복 추가 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 같은 제목의 할 일을 두 번 추가했을 때 두 번째 요청이 기존 ID를 안내하고 새 항목을 만들지 않는지 확인했다.

## 2026-06-05 - 할 일 검색 기능 추가

- 작업 이름: Task Agent와 search CLI 검색 범위 확장
- 진행상황: 완료
- 진행내용:
  - `TaskStore.search`를 추가해 사용자별 삭제되지 않은 할 일을 제목 키워드로 검색하도록 했다.
  - `제안서 할 일 찾아줘`, `제안서 관련 할 일 찾아줘` 같은 자연어를 할 일 검색으로 처리하도록 했다.
  - 최근 대화 추출은 `최근 대화`, `대화에서`, `뽑아`, `추출`, `정리`처럼 명확한 추출 표현이 있을 때만 실행되도록 조정했다.
  - `assistant-admin search <keyword>` 결과에 메모, 문서뿐 아니라 할 일도 포함하도록 했다.
  - 할 일 검색 결과에는 상태, 우선순위, 기한, 완료 시각과 저장 위치를 표시하도록 했다.
  - CLI 검색 테스트, 자연어 할 일 검색 파서 테스트, Task Agent 검색 응답 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 할 일을 추가한 뒤 `assistant-admin search <keyword> --user-id <id>` 결과에 할 일이 표시되는지 확인했다.

## 2026-06-05 - 할 일 상세 조회 기능 추가

- 작업 이름: Task detail 조회 구현
- 진행상황: 완료
- 진행내용:
  - `TaskItem`에 conversation_id와 source_message_id를 포함해 할 일의 저장 대화와 원본 메시지를 추적할 수 있게 했다.
  - `TaskStore.get`을 추가해 사용자별 할 일을 ID로 상세 조회하도록 했다.
  - `할 일 3 자세히 보여줘`, `할 일 3 확인해줘` 같은 자연어를 할 일 상세 조회로 처리하도록 했다.
  - 상세 조회 응답에는 상태, 우선순위, 기한, 저장 위치, 대화 ID, 채널 ID, 원본 메시지 ID, 생성/완료/리마인드/삭제 시각을 표시하도록 했다.
  - `assistant-admin tasks --show <id>` 명령으로 운영 CLI에서도 같은 상세 정보를 확인할 수 있게 했다.
  - 자연어 상세 조회 파서 테스트, Task Agent 상세 응답 테스트, CLI 상세 결과 포맷 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 할 일을 추가한 뒤 `assistant-admin tasks --show <id>`로 상세 정보가 표시되는지 확인했다.

## 2026-06-05 - 할 일 상대 기한 표현 보강

- 작업 이름: 자연어 due date 파서 개선
- 진행상황: 완료
- 진행내용:
  - 할 일 기한 파서가 `3일 뒤`, `2주 후`, `이번 주 금요일`, `다음 주 금요일`, `다음주` 표현을 인식하도록 보강했다.
  - 할 일 제목 추출 시 `3일 뒤`, `2주 후` 같은 상대 기한 표현이 제목에 남지 않도록 정리했다.
  - `다음 주 금요일`은 현재 주의 금요일이 아니라 다음 주 금요일로 계산하도록 했다.
  - 상대 날짜 표현 테스트와 제목 추출 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `assistant-admin ask "할 일 추가: 3일 뒤까지 제안서 초안 작성"` 실행 후 제목과 기한이 올바르게 저장되는지 확인했다.

## 2026-06-05 - 할 일 날짜 계산 타임존 설정 추가

- 작업 이름: ASSISTANT_TIMEZONE 기반 날짜 계산
- 진행상황: 완료
- 진행내용:
  - `ASSISTANT_TIMEZONE` 환경 변수를 추가하고 기본값을 `Asia/Seoul`로 설정했다.
  - 할 일 기한 파서, 오늘까지 할 일 목록, 오늘 브리핑, 자동 리마인더가 설정 타임존 기준 날짜를 사용하도록 했다.
  - 잘못된 타임존 값이 들어와도 UTC로 안전하게 동작하도록 타임존 해석 헬퍼를 추가했다.
  - `assistant-admin doctor`의 선택 환경 변수 점검 목록에 `ASSISTANT_TIMEZONE`을 포함했다.
  - UTC 날짜와 로컬 날짜가 달라지는 고정 시각 테스트를 추가해 `오늘` 계산이 설정 타임존 기준으로 동작하는지 확인했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin doctor` 실행에서 `ASSISTANT_TIMEZONE`이 점검 목록에 표시되는지 확인했다.
  - 임시 SQLite에서 `assistant-admin ask "할 일 추가: 3일 뒤까지 타임존 확인"` 실행 후 기본 `Asia/Seoul` 기준 기한과 제목이 올바르게 저장되는지 확인했다.

## 2026-06-05 - ID 없는 할 일 작업 키워드 처리

- 작업 이름: Task Agent 키워드 기반 작업 대상 해석
- 진행상황: 완료
- 진행내용:
  - 완료, 삭제, 미루기, 우선순위 변경, 완료 취소 요청에서 ID가 없어도 키워드가 단일 할 일로 명확히 좁혀지면 해당 할 일을 처리하도록 했다.
  - 키워드 검색 결과가 없거나 여러 개이면 안전하게 처리하지 않고 ID 확인을 요청하도록 했다.
  - `3일 뒤` 같은 기한 표현의 숫자가 할 일 ID로 오인되지 않도록 ID 추출 규칙을 보정했다.
  - 작업 키워드 추출 테스트, 단일 후보 자동 완료 테스트, 다중 후보 ID 확인 요청 테스트, 키워드 기반 미루기/삭제 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `제안서 할 일 완료했어`가 ID 없이 단일 후보를 찾아 완료 처리하는지 확인했다.

## 2026-06-05 - 대화형 상태별 할 일 목록 추가

- 작업 이름: 완료/전체 할 일 목록 자연어 조회
- 진행상황: 완료
- 진행내용:
  - `완료한 할 일 보여줘` 요청은 완료 상태의 할 일만 보여주도록 했다.
  - `전체 할 일 목록 보여줘` 요청은 열린 할 일과 완료한 할 일을 함께 보여주도록 했다.
  - 완료 목록에는 완료 시각을 표시하고, 다시 열기 예시를 안내하도록 했다.
  - `회의록 정리` 같은 일반 할 일 제목이 최근 대화 추출 요청으로 오인되지 않도록 추출 의도 판별을 보정했다.
  - 상태별 목록 파서 테스트와 Task Agent 완료/전체 목록 응답 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - 임시 SQLite에서 `완료한 할 일 보여줘`, `전체 할 일 목록 보여줘`가 각각 완료 목록과 전체 목록을 보여주는지 확인했다.

## 2026-06-05 - 오래된 삭제 항목 cleanup 추가

- 작업 이름: 삭제된 기억/문서/할 일 보존 기간 정리
- 진행상황: 완료
- 진행내용:
  - `assistant-admin cleanup --target deleted` 옵션으로 오래전에 삭제된 메모, 문서, 문서 chunk, 할 일을 영구 정리하도록 했다.
  - `--target all`에도 오래된 삭제 항목 정리를 포함해 운영 데이터 정리 시 복구 보존 기간이 지난 항목까지 함께 정리되도록 했다.
  - 문서 chunk는 삭제된 문서보다 먼저 정리되도록 처리해 연결된 chunk가 남지 않게 했다.
  - cleanup 미리보기와 실행 결과에 삭제된 메모, 삭제된 문서, 삭제된 할 일 개수를 표시하도록 했다.
  - 오래된 삭제 항목만 정리하고 최근 삭제 항목은 보존하는 CLI 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin cleanup --help`에서 `deleted` 대상이 표시되는지 확인했다.

## 2026-06-05 - 사용자 스냅샷과 최근 대화 위치 브리핑 추가

- 작업 이름: 사용자별 상태 스냅샷 구현
- 진행상황: 완료
- 진행내용:
  - `ConversationStore`에 사용자별 최근 대화 컨텍스트 조회 기능을 추가했다.
  - `오늘 브리핑 해줘` 응답에 최근 대화 위치, 사용자 메시지 수, 최근 미리보기를 함께 표시하도록 했다.
  - `assistant-admin snapshot --user-id <id>` 명령으로 사용자별 기억 수, 할 일 수, 대기 작업, 오늘까지 할 일, 최근 열린 할 일, 최근 기억, 최근 대화 위치를 한 번에 점검하도록 했다.
  - 같은 사용자가 DM, 채널, 스레드를 오가도 최근 대화 위치가 사용자 기준으로 합쳐져 보이도록 했다.
  - 브리핑과 snapshot 출력 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin snapshot --help` 실행을 확인했다.

## 2026-06-05 - 할 일 시각 기한 지원 추가

- 작업 이름: Task Agent 날짜+시각 기한 처리
- 진행상황: 완료
- 진행내용:
  - 할 일 기한 파서가 `내일 오전 9시`, `오후 3시`, `18:30`, `9시 30분` 같은 시각 표현을 인식하도록 했다.
  - 새 할 일 추가, 키워드 기반 미루기, 최근 대화 기반 할 일 추출에서 시각이 포함된 기한을 `YYYY-MM-DD HH:MM` 형식으로 저장하도록 했다.
  - 날짜만 있는 기한은 기존처럼 해당 날짜 끝까지 처리하고, 시각이 있는 기한은 해당 시각이 지난 뒤 리마인더 대상으로 잡히도록 보정했다.
  - `오전 9시`의 숫자를 할 일 ID로 오인하지 않도록 ID 추출 규칙을 보정했다.
  - 시각 포함 기한 파서 테스트, Task Agent 미루기 테스트, 저장소 리마인더 cutoff 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 할 일 목록 범위 필터 추가

- 작업 이름: 내일/이번 주/기한 없음 할 일 조회
- 진행상황: 완료
- 진행내용:
  - `내일 할 일 뭐야?`, `이번 주 할 일 보여줘`, `기한 없는 할 일 보여줘` 같은 자연어 목록 범위를 추가했다.
  - `할 일 추가: 내일 ...`, `내일 다시 알려줘` 같은 추가/미루기 요청이 목록 조회로 오인되지 않도록 라우팅 휴리스틱을 보정했다.
  - `TaskStore.list_recent`에 `due_after`, `due_before`, `undated` 필터를 추가해 날짜+시각 기한 범위를 안정적으로 조회하도록 했다.
  - `assistant-admin tasks`에 `--due-after`, `--undated` 옵션을 추가하고 목록 헤더에 적용된 필터를 표시하도록 했다.
  - CLI 범위 필터 테스트, 대화형 목록 범위 테스트, 라우팅 오인 방지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin tasks --help`에서 새 옵션이 표시되는지 확인했다.

## 2026-06-05 - 운영 doctor 점검 보강

- 작업 이름: 실행 전 환경 점검 강화
- 진행상황: 완료
- 진행내용:
  - `assistant-admin doctor`가 `your_...` 형태의 예시 비밀값을 실제 설정으로 오인하지 않도록 했다.
  - `ASSISTANT_TIMEZONE`이 유효한 IANA 타임존 이름인지 검사하도록 했다.
  - `DATABASE_PATH`가 디렉터리로 설정된 경우와 부모 디렉터리 쓰기 권한 문제를 안내하도록 했다.
  - 실제 비밀값은 계속 출력하지 않고 설정 여부와 점검 결과만 표시하도록 유지했다.
  - 예시 비밀값과 잘못된 타임존을 감지하는 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin doctor` 실행을 확인했다.

## 2026-06-05 - 리마인더 발송 대상 미리보기 CLI 추가

- 작업 이름: 운영용 리마인더 대기열 확인
- 진행상황: 완료
- 진행내용:
  - `assistant-admin reminders` 명령으로 기한이 도래했고 아직 발송되지 않은 할 일 리마인더 대상을 조회하도록 했다.
  - `--user-id`로 특정 사용자만 필터링하고, `--as-of`로 기준 날짜/시각을 지정할 수 있게 했다.
  - `TaskStore.due_for_reminder`에 user_id 필터를 추가해 봇 발송 경로와 운영 미리보기 경로가 같은 조회 기준을 쓰도록 했다.
  - 출력에는 할 일 ID, 제목, user_id, 우선순위, 기한, 채널, 저장 위치를 포함했다.
  - 이미 발송된 리마인더와 다른 사용자 항목이 미리보기에서 제외되는지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin reminders --help` 실행을 확인했다.

## 2026-06-05 - SQLite 초기화 CLI 추가

- 작업 이름: 저장소 초기화 및 스키마 확인
- 진행상황: 완료
- 진행내용:
  - `assistant-admin init-db` 명령으로 `DATABASE_PATH` 기준 SQLite 저장소를 명시적으로 생성하고 마이그레이션하도록 했다.
  - 초기화 결과에 핵심 테이블 누락 여부, `journal_mode`, foreign key 설정, 전체 테이블 수를 표시하도록 했다.
  - 첫 실행자가 `stats` 같은 조회 명령에 의존하지 않고 DB 준비 상태를 바로 확인할 수 있게 했다.
  - 중첩된 디렉터리 경로에서도 DB 파일이 생성되고 핵심 테이블이 준비되는지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin init-db` 실행을 확인했다.

## 2026-06-05 - 첨부 저장 확인 TTL 적용

- 작업 이름: 오래된 첨부 저장 확인 만료 처리
- 진행상황: 완료
- 진행내용:
  - `pending_attachment_requests`도 `PENDING_CONFIRMATION_TTL_MINUTES` 기준으로 만료되도록 했다.
  - 오래된 첨부 저장 확인은 `응, 기억해줘`나 취소 요청에 뒤늦게 반응하지 않도록 자동 해소한다.
  - 봇 상태 표시, 취소 처리, 원본 첨부 저장 처리, 로컬 ask 상태/취소 경로가 같은 TTL 기준을 쓰도록 보정했다.
  - 오래된 첨부 저장 확인 요청이 만료되어 조회와 카운트에서 빠지는지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 운영 로그 설정 추가

- 작업 이름: LOG_LEVEL/LOG_FILE 기반 로깅 설정
- 진행상황: 완료
- 진행내용:
  - `LOG_LEVEL` 환경 변수로 봇 실행 로그 레벨을 조정하도록 했다.
  - `LOG_FILE` 환경 변수가 있으면 지정한 파일에도 로그를 기록하도록 했다.
  - `assistant-admin doctor`가 `LOG_LEVEL` 유효성을 검사하고 로그 관련 선택 환경 변수를 표시하도록 했다.
  - CLI용 설정 생성 경로와 테스트용 `Config` 생성 경로에 로그 설정 기본값을 반영했다.
  - 파일 로그가 실제로 생성되고 기록되는지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin doctor` 실행으로 로그 설정 점검 출력과 전체 환경 점검 통과를 확인했다.

## 2026-06-05 - 대화형 기억 검색 목록 추가

- 작업 이름: 저장 기억 검색 결과 목록화
- 진행상황: 완료
- 진행내용:
  - 사용자가 `운동 관련 기억 찾아줘`, `계약 문서 검색해줘`처럼 말하면 저장된 메모와 문서를 관련도 순 목록으로 보여주도록 했다.
  - 검색 결과에 메모/문서 ID, 제목, 관련도, 저장 위치, 짧은 미리보기를 포함해 바로 상세 조회나 삭제/수정으로 이어갈 수 있게 했다.
  - 로컬 `assistant-admin ask` 경로도 같은 검색형 기억 목록 흐름을 사용하도록 맞췄다.
  - 라우팅 휴리스틱과 검색어 추출 테스트, 메모리 에이전트 검색 목록 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 할 일 묶음 완료 처리 추가

- 작업 이름: 오늘/전체 열린 할 일 자연어 일괄 완료
- 진행상황: 완료
- 진행내용:
  - `오늘 할 일 다 했어`처럼 말하면 오늘까지 처리할 열린 할 일을 한 번에 완료 처리하도록 했다.
  - `모든 할 일 완료했어`처럼 말하면 사용자 기준 열린 할 일을 한 번에 완료 처리하도록 했다.
  - 묶음 완료 결과에는 처리한 개수와 일부 항목 목록을 보여주고, 실수 시 `할 일 3 다시 열어줘`로 되돌릴 수 있음을 안내하도록 했다.
  - 묶음 완료 자연어 판별 테스트와 오늘/전체 열린 할 일 완료 처리 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "오늘 할 일 다 했어"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 최근 완료 할 일 되돌리기 추가

- 작업 이름: 방금 완료한 할 일 자연어 재오픈
- 진행상황: 완료
- 진행내용:
  - `방금 완료한 할 일 되돌려줘`처럼 말하면 사용자 기준 가장 최근 완료한 할 일을 다시 열린 상태로 바꾸도록 했다.
  - 최근 완료 항목은 `completed_at DESC, id DESC` 기준으로 찾아 같은 시각에 완료된 항목도 안정적으로 처리하도록 했다.
  - 기존 `할 일 3 다시 열어줘` ID 기반 재오픈 흐름은 그대로 유지했다.
  - 최근 완료 할 일 재오픈 테스트와 자연어 판별 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 완료한 할 일 되돌려줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 직전 발화 기억 저장 추가

- 작업 이름: `방금 말한 거 기억해줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `방금 말한 거 기억해줘`처럼 말하면 해당 문장 자체가 아니라 직전 사용자 메시지를 장기 기억으로 저장하도록 했다.
  - Discord 봇과 로컬 `assistant-admin ask` 경로 모두 같은 `MemoryAgent` 로직을 사용하도록 대화 저장소를 연결했다.
  - 직전 사용자 메시지가 없거나 직전 메시지도 참조형 저장 요청이면 내용을 직접 적어 달라고 안내하도록 했다.
  - 직전 발화 저장 테스트, 직전 메시지 없음 안내 테스트, 자연어 판별 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 말한 거 기억해줘"` 실행으로 `remember` 라우팅을 확인했다.

## 2026-06-05 - 최신 저장 기억 상세 조회 추가

- 작업 이름: `방금 저장한 거 보여줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `방금 저장한 거 보여줘`, `마지막 저장한 문서 보여줘`처럼 말하면 최근 저장한 메모나 문서의 상세 내용을 바로 보여주도록 했다.
  - 최신 저장 항목 상세 조회는 기존 ID 기반 상세 조회 포맷을 재사용해 제목, 저장 위치, 저장 시각, 본문을 보여준다.
  - 새로 저장하는 메모와 문서는 마이크로초 단위 `created_at`을 기록해 같은 초 안에서 저장한 항목도 최신순으로 더 안정적으로 정렬되도록 했다.
  - 최신 저장 기억 라우팅 테스트, 최신 메모/문서 상세 조회 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 저장한 거 보여줘"` 실행으로 `recall` 라우팅을 확인했다.

## 2026-06-05 - 최신 추가 할 일 상세 조회 추가

- 작업 이름: `방금 추가한 할 일 보여줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `방금 추가한 할 일 보여줘`처럼 말하면 최근 추가한 할 일의 상세 정보를 바로 보여주도록 했다.
  - 할 일 생성 시에도 마이크로초 단위 `created_at`을 기록해 같은 초 안에 추가한 항목도 최신순으로 더 안정적으로 조회되도록 했다.
  - 최신 할 일 상세 조회는 기존 상세 포맷을 재사용해 상태, 우선순위, 기한, 저장 위치, 원본 메시지 ID를 보여준다.
  - 최신 할 일 상세 조회 자연어 판별 테스트와 에이전트 상세 조회 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 추가한 할 일 보여줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 최신 추가 할 일 삭제 추가

- 작업 이름: `방금 추가한 할 일 삭제해줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `방금 추가한 할 일 삭제해줘`처럼 말하면 최근 추가한 할 일을 soft-delete 처리하도록 했다.
  - 삭제 응답에는 실수 시 `할 일 n 복구해줘`로 되돌릴 수 있음을 안내하도록 했다.
  - 기존 ID 기반 삭제와 키워드 기반 삭제 흐름은 그대로 유지했다.
  - 최신 할 일 삭제 자연어 판별 테스트와 에이전트 삭제 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 추가한 할 일 삭제해줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 최신 추가 할 일 리마인더 재예약 추가

- 작업 이름: `방금 추가한 할 일 내일 다시 알려줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `방금 추가한 할 일 내일 오전 9시 다시 알려줘`처럼 말하면 최근 추가한 열린 할 일의 기한을 바로 변경하도록 했다.
  - `다시 알려줘` 표현이 최신 할 일 상세 조회로 오인되지 않도록 상세 조회 판별 조건을 보정했다.
  - 기존 ID 기반 미루기와 키워드 기반 미루기 흐름은 그대로 유지했다.
  - 최신 추가 할 일 참조 자연어 판별 테스트와 에이전트 미루기 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 추가한 할 일 내일 오전 9시 다시 알려줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 최신 추가 할 일 우선순위 변경 추가

- 작업 이름: `방금 추가한 할 일 중요하게 표시해줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `방금 추가한 할 일 중요하게 표시해줘`처럼 말하면 최근 추가한 열린 할 일의 우선순위를 바로 변경하도록 했다.
  - 기존 ID 기반 우선순위 변경과 키워드 기반 우선순위 변경 흐름은 그대로 유지했다.
  - 최신 추가 할 일 참조 자연어 판별 테스트와 에이전트 우선순위 변경 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 추가한 할 일 중요하게 표시해줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 최신 추가 할 일 제목 변경 추가

- 작업 이름: `방금 추가한 할 일을 ...로 바꿔줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `방금 추가한 할 일을 고객 미팅 준비로 바꿔줘`처럼 말하면 최근 추가한 열린 할 일의 제목을 바로 변경하도록 했다.
  - 최신 추가 할 일 표현에서도 새 제목을 추출할 수 있도록 제목 변경 자연어 패턴을 보강했다.
  - 기존 ID 기반 제목 변경 흐름은 그대로 유지했다.
  - 최신 추가 할 일 참조 자연어 판별 테스트와 에이전트 제목 변경 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 추가한 할 일을 고객 미팅 준비로 바꿔줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 최신 저장 메모 수정 추가

- 작업 이름: `방금 저장한 메모를 ...로 바꿔줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `방금 저장한 메모를 나는 저녁 운동을 선호한다로 바꿔줘`처럼 말하면 최근 저장한 메모를 바로 수정하도록 했다.
  - 최신 저장 항목이 문서인 경우 기존 정책대로 직접 수정할 수 없다고 안내하도록 했다.
  - 최신 메모 수정 표현에서도 새 내용을 정확히 추출하도록 자연어 패턴을 보강했다.
  - 최신 메모 수정 자연어 판별 테스트, 최신 메모 수정 테스트, 최신 문서 수정 방지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 저장한 메모를 나는 저녁 운동을 선호한다로 바꿔줘"` 실행으로 `update_memory` 라우팅을 확인했다.

## 2026-06-05 - 할 일 기한 제거 추가

- 작업 이름: 할 일 기한 및 리마인더 예약 제거
- 진행상황: 완료
- 진행내용:
  - 사용자가 `할 일 3 기한 없애줘`처럼 말하면 열린 할 일의 기한과 리마인더 발송 예약을 제거하도록 했다.
  - `방금 추가한 할 일 리마인더 제거해줘`처럼 최근 추가한 열린 할 일을 대상으로도 기한 제거가 가능하도록 했다.
  - `기한 없는 할 일 보여줘` 같은 목록 조회와 충돌하지 않도록 제거 동사가 있는 요청만 기한 제거로 처리하도록 했다.
  - 기한 제거 자연어 판별 테스트, ID 기반 기한 제거 테스트, 최신 추가 할 일 기한 제거 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "방금 추가한 할 일 리마인더 제거해줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 자연어 알림 문장으로 할 일 생성 추가

- 작업 이름: `내일 오전 9시에 ... 알려줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `내일 오전 9시에 물 마시라고 알려줘`처럼 말하면 날짜와 시각이 있는 열린 할 일로 저장하도록 했다.
  - 자연어 알림 문장이 `내일 할 일 알려줘` 같은 목록 조회로 오인되지 않도록 날짜 목록 조회 판별을 보정했다.
  - 제목에서 `알려줘`, `하라고`, `라고` 같은 알림 지시 표현을 제거해 실제 할 일 제목만 저장하도록 했다.
  - 자연어 알림 생성 판별 테스트, 제목/기한 추출 테스트, 에이전트 저장 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "내일 오전 9시에 물 마시라고 알려줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 상대 시간 리마인더 추가

- 작업 이름: `30분 뒤 ... 알려줘` 처리
- 진행상황: 완료
- 진행내용:
  - `30분 뒤`, `2시간 후` 같은 분/시간 단위 상대 시간 표현을 할 일 기한으로 처리하도록 했다.
  - `오전 9시 30분` 같은 절대 시각 표현과 충돌하지 않도록 `뒤`, `후`가 붙은 분/시간 표현만 상대 시간으로 처리했다.
  - 자연어 알림 문장에서 상대 시간 표현을 제거해 제목만 깔끔하게 저장하도록 했다.
  - 상대 시간 제목/기한 추출 테스트와 에이전트 저장 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "30분 뒤 물 마시라고 알려줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 직전 발화 기반 할 일 생성 추가

- 작업 이름: `그거 할 일로 추가해줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 직전에 말한 내용을 다시 복사하지 않고 `그거 할 일로 추가해줘`, `방금 말한 거 할 일로 등록해줘`처럼 말해도 열린 할 일로 저장하도록 했다.
  - 현재 메시지는 처리 후 대화 기록에 저장되는 구조를 활용해, `ConversationStore.latest_user_message`로 직전 사용자 발화를 안전하게 참조하도록 했다.
  - `해야겠다`, `해야 해` 같은 말끝 표현을 할 일 제목에서 제거해 제목이 자연스럽게 저장되도록 했다.
  - 직전 발화에 날짜 표현이 있으면 기존 날짜 파서를 재사용해 기한도 함께 저장하도록 했다.
  - 직전 발화 기반 할 일 생성 판별 테스트와 에이전트 저장 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "그거 할 일로 추가해줘"`와 `assistant-admin route "방금 말한 거 할 일로 등록해줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 대명사형 직전 발화 기억 추가

- 작업 이름: `그거 기억해줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `그거 기억해줘`, `이것도 저장해줘`처럼 말하면 `그거` 자체가 아니라 직전 사용자 발화를 장기 기억으로 저장하도록 했다.
  - `이거 기억해줘: ...`처럼 현재 메시지에 실제 저장 내용이 있는 기존 흐름은 그대로 유지했다.
  - 대명사형 저장 요청을 실질 내용이 없는 기억 요청으로 판별해, 빈약한 메모가 저장되지 않도록 했다.
  - 대명사형 기억 판별 테스트와 실제 직전 발화 저장 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 최근 리마인더 스누즈 추가

- 작업 이름: `30분 뒤 다시 알려줘` 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 할 일 리마인더를 받은 뒤 ID 없이 `30분 뒤 다시 알려줘`, `2시간 후 나중에 알려줘`처럼 말하면 최근 리마인드된 열린 할 일을 자동으로 미루도록 했다.
  - 최근 리마인드된 열린 할 일을 조회하는 `TaskStore.latest_reminded_open`을 추가했다.
  - `제안서 할 일 내일 오전 9시 다시 알려줘`처럼 키워드로 특정한 미루기 요청은 기존 검색 기반 처리로 남기고, 키워드와 ID가 없는 요청만 스누즈로 처리하도록 했다.
  - `30분` 같은 숫자 표현이 할 일 ID로 부분 매칭되지 않도록 ID 추출 정규식을 보정했다.
  - 최근 리마인더 조회 테스트, 스누즈 에이전트 테스트, 기존 키워드 미루기 충돌 방지 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
  - `assistant-admin route "30분 뒤 다시 알려줘"` 실행으로 `manage_task` 라우팅을 확인했다.

## 2026-06-05 - 최종 문서 갱신

- 작업 이름: 구현 완료 후 문서 정리
- 진행상황: 완료
- 진행내용:
  - `README.md`에 직전 발화 기반 기억, 직전 발화 기반 할 일 생성, 자연어 알림 생성, 상대 시간 리마인더, 최근 리마인더 스누즈 흐름을 반영했다.
  - `README.md`의 에이전트 구조 설명을 `Router Agent`, `Conversation Agent`, `Memory Agent`, `Task Agent`, `Utility Agent` 기준으로 갱신했다.
  - `plan.md`의 라우팅 intent, 구현 상태, 자동 검증 결과를 현재 구현 기준으로 갱신했다.
  - 자동 검증 결과를 `python3 -m pytest` 149개 통과 기준으로 갱신했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 리마인더 DM 전용 발송 변경

- 작업 이름: 서버 요청 리마인더도 DM으로 발송
- 진행상황: 완료
- 진행내용:
  - 서버 채널이나 스레드에서 만든 할 일이라도 기한 도래 리마인더는 채널이 아니라 사용자 DM으로 보내도록 변경했다.
  - 리마인더 발송 시 저장된 `channel_id`를 사용하지 않고 사용자 ID 기준으로 DM 대상을 해석하도록 했다.
  - DM에서 만든 할 일과 서버에서 만든 할 일 모두 DM 발송 경로를 사용하는 테스트를 추가했다.
  - `README.md`와 `plan.md`에 리마인더는 생성 위치와 관계없이 DM으로 발송된다는 정책을 반영했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 에이전트 모듈화 계획 문서화

- 작업 이름: 에이전트 카탈로그 기반 라우팅 및 모듈화 계획 정리
- 진행상황: 완료
- 진행내용:
  - `agent_modularization_plan.md`를 새로 만들어 에이전트 목록화, 모듈화, registry dispatch, 라우터 프롬프트 자동 구성 계획을 정리했다.
  - 현재 구조의 수동 연결 지점과 목표 구조를 구분해 기록했다.
  - 새 에이전트 추가 절차, 테스트 계획, 적용 순서, 제외 범위, 결정된 기본값을 문서에 포함했다.

## 2026-06-05 - Tool Calling 도입 계획 문서화

- 작업 이름: 선택적 tool/function calling 도입 계획 정리
- 진행상황: 완료
- 진행내용:
  - `plan.md`에 앞으로 추가되는 모든 전문 에이전트는 개발 단계부터 tool calling 적용 여부를 검토한다는 설계 원칙을 추가했다.
  - `tool_calling_plan.md`를 새로 만들어 tool calling을 사용할 때와 사용하지 않을 때의 판단 기준을 정리했다.
  - Memory, Task, Conversation 계열에 선택적으로 tool calling을 도입하고 Router, Utility, 리마인더 루프, destructive 작업은 제외한다는 기본 정책을 기록했다.
  - `OpenAIService.tool_response`, tool executor, 에이전트별 allowlist, 테스트 계획, 에이전트 모듈화 계획과의 관계를 문서에 포함했다.

## 2026-06-05 - 에이전트 JSON 카탈로그 및 모듈화 적용

- 작업 이름: 에이전트 레지스트리 리팩터링 실행
- 진행상황: 완료
- 진행내용:
  - `agent_catalog.json`을 추가해 에이전트 intent, 이름, 목적, 설명, 예시를 JSON 설정 파일로 관리하도록 했다.
  - `assistant_bot/agent_registry.py`를 추가해 JSON 카탈로그를 로딩하고, Python handler map으로 실제 에이전트 실행 함수를 연결하도록 했다.
  - `RouterAgent`가 JSON 카탈로그 기반 `routing_prompt_block()`과 허용 intent 목록을 사용하도록 변경했다.
  - Discord 봇과 로컬 CLI의 일반 intent 실행 경로를 `AgentRegistry.dispatch()`로 통합했다.
  - 기존 `assistant_bot/agents.py`를 `assistant_bot/agents/` 패키지로 분리하고 `__init__.py`에서 기존 import 호환성을 유지했다.
  - `tests/test_agent_registry.py`를 추가해 카탈로그 로딩, prompt block 생성, fallback dispatch, handler 누락 검증을 테스트했다.
  - `README.md`, `plan.md`, `agent_modularization_plan.md`를 JSON 카탈로그 기반 구조와 현재 검증 결과에 맞춰 갱신했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - Tool Calling 1차 적용

- 작업 이름: Conversation Agent read-only tool calling 도입
- 진행상황: 완료
- 진행내용:
  - `assistant_bot/tool_calling.py`에 `ToolSpec`을 추가해 function tool schema와 handler를 한 객체로 묶도록 했다.
  - `OpenAIService.tool_response`를 추가해 Responses API function_call, tool 실행, function_call_output 재전송, 최종 응답 생성을 처리하도록 했다.
  - `assistant_bot/agent_toolkits.py`를 추가해 `ConversationAgent`가 사용할 read-only 기억/할 일 조회 도구를 구성하도록 했다.
  - `ConversationAgent`가 일반 대화에서 선제 embedding 검색을 하지 않고, 모델이 필요할 때 read-only tool을 호출하도록 변경했다.
  - `agent_catalog.json`과 `AgentDefinition`에 tool 이름 목록을 추가해 새 에이전트 설계 시 tool allowlist를 함께 관리할 수 있도록 했다.
  - `tests/test_openai_service.py`, `tests/test_agent_toolkits.py`, `tests/test_agent_registry.py`에 tool calling 실행 루프, read-only tool 실행, 카탈로그 tool 메타데이터 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - Memory Agent Tool Calling 적용

- 작업 이름: 일반 기억 회상 경로 tool calling 전환
- 진행상황: 완료
- 진행내용:
  - `assistant_bot/agent_toolkits.py`를 `build_memory_read_tools`, `build_task_read_tools`, `build_conversation_read_tools`로 분리해 에이전트별 도구 조합이 가능하도록 했다.
  - `get_memory_detail`, `get_document_detail` read-only tool을 추가했다.
  - `MemoryAgent.recall`의 최근 항목/ID 상세 조회는 deterministic 경로로 유지하고, 일반 자연어 회상 경로는 `OpenAIService.tool_response`를 사용하도록 변경했다.
  - `agent_catalog.json`의 `chat`, `recall` tool 목록에 memory detail 도구를 반영했다.
  - 일반 recall이 read-only tool 목록을 전달하는 테스트를 추가했다.

## 2026-06-05 - 리마인더 기능 문의 라우팅 보정

- 작업 이름: 리마인드 기능 질문 오분류 수정
- 진행상황: 완료
- 진행내용:
  - `리마인드 기능은 없나?` 같은 기능 문의가 `manage_task`로 라우팅되어 할 일을 저장하려는 문제를 재현했다.
  - 기능, 지원, 가능, 없나, 있나 같은 표현은 `help` intent로 먼저 라우팅하도록 보정했다.
  - `is_task_request`가 `리마인드` 단어 하나만으로 할 일 요청을 확정하지 않도록 좁혔다.
  - `리마인드 기능은 없나?`는 `help`, `30분 뒤 물 마시라고 알려줘`는 `manage_task`로 라우팅되는 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 라우팅 모델 우선 구조 전환

- 작업 이름: Router Agent 모델 우선 판단 적용
- 진행상황: 완료
- 진행내용:
  - 기존에는 고신뢰 휴리스틱이 먼저 실행되어 라우팅 모델 호출을 건너뛰는 구조였음을 확인했다.
  - `RouterAgent.route`가 현재 메시지와 최근 대화 맥락을 라우팅 모델에 먼저 전달하도록 변경했다.
  - 휴리스틱 라우팅은 모델 호출 실패 또는 라우터 JSON 파싱 실패 시 fallback으로만 사용하도록 변경했다.
  - Discord 봇과 로컬 `assistant-admin ask` 경로에서 최근 대화 8개를 라우터 입력에 포함하도록 했다.
  - 휴리스틱 기준으로는 `manage_task`가 될 수 있는 문장도 모델이 `help`로 판단하면 모델 판단을 따르는 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.
