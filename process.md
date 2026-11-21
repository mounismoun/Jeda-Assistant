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

## 2026-06-05 - Naver 웹검색 에이전트 1차 구현

- 작업 이름: `web_search` intent와 Naver Search API 기반 WebSearchAgent 추가
- 진행상황: 완료
- 진행내용:
  - `web_search` intent를 추가하고 Router Agent 휴리스틱에 명시적 웹검색 요청과 최신/현재 외부 정보 요청을 감지하도록 했다.
  - `웹검색 할 수 있어?` 같은 기능 문의는 `help`로 보내고, 저장 기억/문서/할 일 검색은 내부 intent로 유지하도록 라우팅 테스트를 고정했다.
  - Naver Search API provider를 추가해 `webkr`, `news`, `blog`, `shop` 결과를 공통 `SearchResult`로 정규화하도록 했다.
  - WebSearchAgent를 추가해 검색 category를 고르고, 검색 결과 snippet을 LLM으로 요약해 출처 URL을 포함해 답하도록 했다.
  - `agent_catalog.json`, `capabilities.py`, `README.md`, `plan.md`, `.env.example`에 Naver 웹검색 지원과 환경변수 예시를 반영했다.
  - 대상 테스트와 라우팅 미리보기로 `web_search`, 내부 기억 검색, 기능 문의 분리가 동작하는지 확인했다.
  - `assistant-admin doctor`에서 Naver 웹검색 환경변수 기본값 상태와 전체 설정 점검이 통과하는지 확인했다.
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

## 2026-06-05 - 봇 기능 인식 기준 통합

- 작업 이름: 지원/미지원 기능 단일 소스 적용
- 진행상황: 완료
- 진행내용:
  - `assistant_bot/capabilities.py`를 추가해 봇이 코드로 제공하는 기능과 제공하지 않는 기능을 한 곳에서 관리하도록 했다.
  - Router Agent 프롬프트에 지원/미지원 기능 목록을 주입해, OpenAI 모델이 일반적으로 할 수 있어 보이는 일이라도 현재 코드가 제공하지 않으면 `unsupported`로 분류하도록 했다.
  - Conversation Agent 프롬프트에도 같은 capability 목록을 주입해, 일반 대화에서 불가능한 작업을 가능하다고 말하지 않도록 했다.
  - 도움말과 unsupported 응답이 같은 capability 기준을 참조하도록 변경했다.
  - capability prompt, 도움말/unsupported 제한 안내, unavailable action 라우팅 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 할 일과 알림 요청 분리

- 작업 이름: 할 일 저장과 사용자 알림 예약 분리
- 진행상황: 완료
- 진행내용:
  - `reminders` SQLite 테이블과 `ReminderStore`, `ReminderAgent`를 추가해 `30분 뒤 물 마시라고 알려줘` 같은 요청이 할 일 목록이 아니라 알림 전용 저장소에 저장되도록 했다.
  - `agent_catalog.json`에 `manage_reminder` intent를 추가하고 `manage_task` 설명에서 알림 예약 책임을 분리해 라우팅 모델이 두 작업을 구분해 참조하도록 했다.
  - 자동 발송 루프와 `assistant-admin reminders`가 기한 있는 할 일이 아니라 알림 전용 저장소의 발송 대기 항목을 조회하도록 변경했다.
  - 알림은 요청 위치가 DM, 서버, 스레드 어디든 사용자 DM으로만 발송되도록 유지했다.
  - ID 없는 `30분 뒤 다시 알려줘`는 새 알림 예약으로 보고, 할 일 미루기는 `할 일 3 30분 뒤 다시 알려줘`처럼 대상 할 일을 명시하는 흐름으로 정리했다.
  - README, plan, capability 도움말 문구를 할 일/알림 분리 정책에 맞게 갱신했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 라우터 최근 대화 컨텍스트 확대

- 작업 이름: Router Agent 최근 대화 입력 16개 적용
- 진행상황: 완료
- 진행내용:
  - Discord 봇 메시지 처리 경로에서 라우터 모델에 전달하는 최근 대화 개수를 8개에서 16개로 늘렸다.
  - 로컬 `assistant-admin ask` 경로도 같은 기준을 쓰도록 최근 대화 개수를 16개로 맞췄다.

## 2026-06-05 - 현재 시간 컨텍스트 추가

- 작업 이름: Router/Conversation Agent 현재 시각 인지 보강
- 진행상황: 완료
- 진행내용:
  - `assistant_bot/time_utils.py`에 설정 타임존 기준 현재 날짜와 시간을 문자열로 제공하는 공통 함수를 추가했다.
  - Router Agent 입력에 현재 날짜와 시간을 포함해 `지금 몇시야` 같은 요청을 현재 코드가 알 수 없는 작업으로 오인하지 않도록 했다.
  - Conversation Agent 입력에 현재 날짜와 시간을 포함해 일반 답변에서도 설정 타임존 기준 현재 시각을 답할 수 있도록 했다.
  - Utility Agent 상태 응답에도 현재 날짜와 시간을 표시하도록 했다.
  - 라우터와 일반 대화 에이전트의 모델 입력에 현재 시간 컨텍스트가 포함되는지 테스트를 추가했다.

## 2026-06-05 - 현재 시간 요청 라우팅 수정

- 작업 이름: `지금 몇시야` unsupported 오분류 수정
- 진행상황: 완료
- 진행내용:
  - 현재 시간 컨텍스트를 제공했지만 capability 목록과 에이전트 카탈로그에 현재 시간 안내 기능이 없어 라우터가 unsupported로 분류할 수 있음을 확인했다.
  - `current_time` intent를 추가하고 Router Agent 카탈로그, RouteIntent, 휴리스틱 fallback, Agent Registry에 연결했다.
  - Utility Agent가 설정 타임존 기준 현재 날짜와 시간을 짧게 직접 답하도록 `current_time` 응답을 추가했다.
  - capability prompt, 도움말, unsupported 안내에 현재 시간 확인 기능을 반영했다.
  - `지금 몇시야?`가 `current_time`으로 라우팅되는 테스트와 카탈로그/capability 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 알림 조회와 발송 지연 개선

- 작업 이름: 알림 목록/최근 예약 조회 및 루프 간격 개선
- 진행상황: 완료
- 진행내용:
  - `ReminderStore`에 사용자별 미발송 알림 목록 조회와 최근 등록 알림 조회를 추가했다.
  - `ReminderAgent`가 `현재 등록되어 있는 알림 목록`, `내가 아까 몇시에 알림 보내달라고 했지?` 같은 조회형 요청에 답하도록 했다.
  - Router 휴리스틱과 `agent_catalog.json`에 알림 목록/최근 예약 시각 조회 예시를 반영했다.
  - 알림 발송 루프가 설정값이 커도 최대 15초 간격으로 대기 알림을 확인하도록 변경해 예약 시각보다 늦게 도착하는 폭을 줄였다.
  - 기본 `TASK_REMINDER_INTERVAL_MINUTES` 값을 60분에서 1분으로 낮추고 문서와 `.env.example`을 갱신했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - AI 최종 응답 구성 계층 추가

- 작업 이름: 하드코딩 응답 노출 축소
- 진행상황: 완료
- 진행내용:
  - `ResponseComposer`를 추가해 각 에이전트가 만든 실행 결과를 사용자에게 보내기 전 OpenAI 모델이 자연스러운 대화체 한국어로 다시 작성하도록 했다.
  - Discord 봇 메시지 처리 경로와 로컬 `assistant-admin ask` 경로가 모두 최종 응답 구성 계층을 지나도록 연결했다.
  - 응답 구성 프롬프트에는 실행 결과에 없는 사실을 만들지 말고 ID, 날짜, 시간, 숫자, 파일명, 안전 확인 문구의 의미를 보존하도록 명시했다.
  - 모델 호출이 실패하면 기존 실행 결과를 그대로 반환하도록 fallback을 두어 기능 실행 결과가 유실되지 않게 했다.
  - 앞으로 에이전트 내부 하드코딩 문구는 상태 변경 결과와 안전상 필요한 최소 안내로 제한하고, 사용자-facing 표현은 AI 응답 구성 계층에서 다듬는 원칙을 `plan.md`에 기록했다.
  - `ResponseComposer` 정상/실패 fallback 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 반복 고정 답변 완화

- 작업 이름: AI 최종 응답 반복 표현 억제
- 진행상황: 완료
- 진행내용:
  - 동일한 실행 결과가 들어올 때 최종 답변이 완전히 같은 문장으로 반복되는 문제가 남아 있음을 확인했다.
  - `ResponseComposer` 프롬프트에 실행 결과의 사실은 보존하되 문장은 그대로 복사하지 말라는 지침을 추가했다.
  - 최근 봇 답변 중 반복을 피해야 할 표현을 모델 입력에 함께 제공해 같은 첫 문장, 같은 문장 구조, 같은 마무리를 피하도록 했다.
  - 표현 변주 힌트와 더 높은 temperature를 적용해 같은 기능 응답도 더 자연스럽게 달라지도록 조정했다.

## 2026-06-05 - 사람 친화적 시간 표현 적용

- 작업 이름: 시스템식 시간 표기 완화
- 진행상황: 완료
- 진행내용:
  - `YYYY-MM-DD HH:MM` 형태가 사용자 답변에 그대로 노출되어 대화형 비서 느낌이 약해지는 문제를 확인했다.
  - `time_utils`에 `오늘 오전 7시 4분`, `내일 오후 3시`처럼 사람이 읽기 쉬운 시간 포맷 함수를 추가했다.
  - 현재 시간 조회, 상태 조회, DM 알림 발송 문구에서 사람 친화적 시간 표현을 사용하도록 변경했다.
  - 최종 응답 작성 프롬프트에서 날짜와 시간은 의미를 보존하되 자연스러운 한국어 표현으로 바꾸도록 지침을 조정했다.

## 2026-06-05 - 에이전트 공통 성격과 구조화 결과 도입

- 작업 이름: 에이전트별 말투 분열 완화
- 진행상황: 1차 완료
- 진행내용:
  - 에이전트별로 고정 문자열을 직접 반환해 말투가 갈라지고 반복되는 원인을 확인했다.
  - 공통 비서 persona를 추가해 일반 대화와 기능 응답이 같은 친근한 존댓말 기준을 참조하도록 했다.
  - `OperationResult`를 추가해 에이전트 실행 결과를 `status`, `summary`, `facts`, `items`, `next_actions`로 전달할 수 있게 했다.
  - `AgentRegistry`가 레거시 문자열도 `OperationResult`로 감싸도록 변경해 전체 응답 흐름을 구조화 결과 기반으로 전환할 발판을 만들었다.
  - `ReminderAgent`와 `UtilityAgent`는 알림 ID, 예약 시각, 상태, 현재 시간, 상태 통계 같은 실행 사실을 구조화 결과로 반환하도록 1차 전환했다.
  - `ResponseComposer`는 공통 persona와 구조화 실행 결과를 기반으로 최종 답변을 작성하도록 강화했다.

## 2026-06-05 - Task Agent 구조화 결과 2차 전환

- 작업 이름: 할 일 에이전트의 고정 문자열 노출 축소
- 진행상황: 3차 완료
- 진행내용:
  - `TaskAgent`의 할 일 생성, 중복 확인, 목록 조회, 완료 일괄 처리, 삭제 목록, 검색, 상세 조회, 기한 목록, 최근 대화 기반 할 일 추출/저장 경로를 `OperationResult` 기반으로 전환했다.
  - 할 일 ID, 제목, 상태, 우선순위, 기한, 사람이 읽기 쉬운 기한 표현을 구조화 필드로 전달해 최종 응답 작성자가 같은 persona로 자연스럽게 말할 수 있게 했다.
  - 첨부 저장 확인, 지원하지 않는 첨부 안내, 전체 기억 삭제 확인/취소/완료 같은 봇 직접 응답도 `OperationResult`를 반환하도록 바꿨다.
  - `TaskAgent`가 구조화 결과를 반환하는지 확인하는 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - Memory Agent 구조화 결과 전환

- 작업 이름: 기억 에이전트의 말투 통일 구조 완성
- 진행상황: 완료
- 진행내용:
  - `MemoryAgent`의 텍스트 기억 저장, 중복 확인, 상세 조회, 삭제, 복구, 삭제 목록, 기억 목록, 검색, 수정 경로를 `OperationResult` 기반으로 전환했다.
  - 기억 ID, 문서 ID, 제목, 저장 위치, 삭제/복구 개수, 검색 결과, 수정 대상 같은 실행 사실을 구조화 필드로 전달하도록 했다.
  - 기억 기반 질의 응답 프롬프트에도 공통 persona를 주입해 일반 대화와 기억 답변의 말투 차이를 줄였다.
  - `handle_remember`의 문서 저장/중복/첨부 실패 결과도 구조화 결과로 묶어 최종 응답 작성자가 같은 persona로 답하도록 했다.
  - `cancel_pending` 응답도 `OperationResult`로 전환해 대기 작업 취소 안내가 고정 문자열로 직접 노출되지 않게 했다.
  - 주요 에이전트 직접 반환 문자열 검색 결과, 사용자-facing 에이전트 경로는 `OperationResult` 또는 공통 persona 기반 모델 응답을 통과하도록 정리했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 메모 예고 문장 저장 방지

- 작업 이름: 빈 메모 의도 오저장 방지
- 진행상황: 완료
- 진행내용:
  - `메모 하나 할게`, `메모할게` 같은 저장 의도 예고 문장이 실제 메모 내용처럼 저장되는 문제를 확인했다.
  - 실질적인 기억 내용 판정에서 메모 예고 문장을 제외하도록 보정했다.
  - 라우터가 실수로 `remember`로 보낸 경우에도 `MemoryAgent`가 저장하지 않고 메모할 실제 내용을 물어보도록 안전장치를 추가했다.
  - 예고 문장이 저장되지 않는 휴리스틱 테스트와 에이전트 저장 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - AI 기반 메모 내용 판정 도입

- 작업 이름: 메모 요청과 메모 본문 구분
- 진행상황: 완료
- 진행내용:
  - `다음 내용 메모로 남겨줘`, `지금부터 메모 할게`, `지금부터 메모 하나 할게`처럼 저장 요청/예고 문장 자체가 메모로 저장되는 문제를 확인했다.
  - `MemoryAgent`에 AI 기반 메모 내용 판정 계층을 추가해, `remember` 라우팅 이후에도 실제 저장할 본문이 있는지 다시 판단하도록 했다.
  - 판정 모델은 JSON으로 `has_memory_content`, `memory_text`, `reason`을 반환하고, 저장할 본문이 없으면 저장하지 않고 내용을 물어보도록 했다.
  - 모델 호출 실패 시에는 기존 휴리스틱으로 fallback하되, 실질 내용이 없다고 판단되는 경우 저장하지 않도록 보수적으로 처리했다.
  - 저장 요청만 있는 문장을 거부하는 테스트와, 본문이 포함된 요청에서 본문만 저장하는 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 메모 대기 상태와 목록 분리 구현

- 작업 이름: 다음 메시지 메모 캡처 및 메모/파일 목록 분리
- 진행상황: 완료
- 진행내용:
  - `PendingMemoryCapture` 모델과 `pending_memory_captures` 테이블, `PendingMemoryCaptureStore`를 추가해 사용자/대화 위치별 메모 대기 상태를 관리하도록 했다.
  - `다음 내용 메모로 남겨줘`, `지금부터 메모 할게` 같은 예고 문장은 즉시 저장하지 않고 다음 사용자 메시지 1개를 메모 본문으로 받도록 변경했다.
  - 메모 대기 중 `메모 그만해`, `메모 취소해`, `저장하지 마` 계열 메시지가 오면 저장하지 않고 대기 상태를 종료하도록 했다.
  - 다음 메시지가 기존 메모와 정확히 같으면 새로 저장하지 않고 기존 ID를 안내하며, 유사도가 높은 메모는 수정/병합 여부를 묻도록 했다.
  - 라우터 프롬프트와 에이전트 카탈로그에 메모 대기 및 취소 의도를 반영해 AI가 요청과 본문을 더 명확히 구분하도록 했다.
  - `메모 목록 보여줘`는 텍스트 메모만, `파일 목록 보여줘`와 `문서 목록 보여줘`는 파일/문서만 보여주도록 목록 조회 필터를 분리했다.
  - Discord 봇 경로와 로컬 CLI `ask` 경로 모두 새 메모 대기 저장소를 사용하도록 맞췄다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 봇 상태 메시지 설정

- 작업 이름: Discord 봇 상태 메시지 적용
- 진행상황: 완료
- 진행내용:
  - 봇 로그인 직후 Discord presence를 설정하도록 `on_ready` 흐름에 상태 메시지 적용 코드를 추가했다.
  - 상태 메시지는 `범용 AI 비서입니다.`로 설정했다.

## 2026-06-05 - 봇 이름 인지 프롬프트 추가

- 작업 이름: SleepGPT 정체성 프롬프트 적용
- 진행상황: 완료
- 진행내용:
  - 공통 persona에 봇의 기본 이름을 `SleepGPT`, 한국어 표기를 `슬립지피티`로 명시했다.
  - 봇이 자신을 소개하거나 이름을 말할 때는 `SleepGPT`를 사용하도록 지침을 추가했다.
  - 최종 응답 작성자, 일반 대화 에이전트, 라우터 입력에 비서 이름 정보를 함께 제공하도록 했다.

## 2026-06-05 - 첨부 문서 요청 자동 저장 처리

- 작업 이름: 문서 첨부 후 즉시 요청 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 지원되는 첨부 파일과 함께 요청 문장을 보낸 경우, 별도 저장 확인을 묻지 않고 문서를 바로 저장하도록 변경했다.
  - `이 문서 요약해봐`처럼 첨부 문서에 대한 요약/분석/질문 요청이면 방금 저장한 문서 ID를 기준으로 즉시 답변을 생성하도록 했다.
  - 첨부가 있을 때 사용자 요청 문장 자체가 텍스트 메모로 저장되지 않도록 정리했다.
  - 첨부만 보낸 경우에는 기존처럼 저장 확인 대기 흐름을 유지했다.
  - 자동 저장 후 즉시 답변하는 봇 통합 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 확인 요청 버튼 응답 도입

- 작업 이름: 승인/거부 버튼 기반 확인 처리
- 진행상황: 완료
- 진행내용:
  - 실행 결과가 `confirm_required`이고 실제 대기 작업이 있는 경우 Discord 버튼을 붙이도록 공통 확인 View를 추가했다.
  - 첨부 저장 확인과 전체 기억 삭제 확인에 `승인`, `거부` 버튼을 제공하도록 했다.
  - 버튼은 요청한 사용자만 누를 수 있게 검증하고, 승인/거부에 따라 저장, 삭제, 취소 액션을 실행한 뒤 메시지를 갱신하도록 했다.
  - 첨부 저장 확인과 전체 기억 삭제 확인에 버튼이 붙는지 확인하는 테스트를 추가했다.
  - 도움말과 capability 목록에 버튼 기반 승인/거부 흐름을 반영했다.

## 2026-06-05 - ID 기반 기억 삭제 확인 추가

- 작업 이름: 특정 메모/문서 삭제 전 확인 대기
- 진행상황: 완료
- 진행내용:
  - `메모 8 삭제해`, `문서 5 삭제해`처럼 ID가 명시된 기억 삭제 요청이 즉시 삭제되는 문제를 확인했다.
  - 삭제 확인 대기 저장소에 `mode`, `memory_ids`, `document_ids`를 추가해 특정 삭제 대상도 pending 상태로 보관하도록 확장했다.
  - ID 기반 삭제 요청은 실제 삭제를 실행하지 않고 `confirm_required` 결과와 승인/거부 버튼을 먼저 띄우도록 변경했다.
  - 사용자가 승인 버튼을 누르거나 확인 답변을 하면 pending에 저장된 특정 메모/문서만 삭제하도록 했다.
  - 특정 메모와 문서 삭제가 확인 전에는 유지되고, 확인 후에만 삭제되는 통합 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 문서 분석 에이전트 분리와 비전 OCR 제한 도입

- 작업 이름: 문서 분석 고도화 및 이미지 분석 기반 추가
- 진행상황: 완료
- 진행내용:
  - `Document Analysis Agent`를 새로 분리해 첨부 파일 요약, 질문 답변, 문서 저장, 이미지 OCR, 스캔 PDF OCR, 비전 OCR 잔여 용량 조회를 전담하도록 했다.
  - 로컬 분석 지원 확장자를 `.txt`, `.md`, `.pdf`, `.docx`, `.xlsx`, `.csv`로 확장하고, 로컬에서 텍스트를 추출할 수 있는 문서는 비전 OCR 용량 제한에서 차감하지 않도록 했다.
  - 이미지 첨부 `.png`, `.jpg`, `.jpeg`, `.webp`와 텍스트 추출이 안 되는 스캔 PDF는 `gpt-5.4-mini` 비전 OCR로 분석하도록 했다.
  - 비전 OCR 요청의 이미지 detail 값을 `auto`로 고정했다.
  - 비전 OCR에만 1회 10MB, 사용자별 하루 50MB 제한을 적용하고, `vision_ocr_usage` 테이블과 전용 저장소로 사용량을 기록하도록 했다.
  - 사용자가 오늘 남은 분석 가능 용량을 물으면 문서 분석 에이전트가 남은 비전 OCR 용량과 한 번의 채팅 한도를 답하도록 했다.
  - 첨부 파일이 있는 분석/요약 요청이 기존 메모 저장 흐름으로 새지 않고 문서 분석 에이전트로 라우팅되도록 봇 처리 순서를 정리했다.
  - README, 계획 문서, `.env.example`, 운영 CLI 안내 문구에 새 지원 범위와 비전 OCR 제한을 반영했다.
  - 상태 메시지는 사용자 요청에 따라 기존 `멘션하여 슬립지피티를 호출해보세요.` 문구를 유지했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check` 검증을 통과했다.

## 2026-06-05 - Discord 확인 버튼 응답 안정화

- 작업 이름: 승인/거부 버튼 interaction 만료 오류 수정
- 진행상황: 완료
- 진행내용:
  - 이미지 첨부 후 `승인` 버튼을 눌렀을 때 `Unknown interaction` 오류가 발생하는 로그를 확인했다.
  - 버튼 클릭 직후 `interaction.response.defer()`로 먼저 Discord에 응답 확인을 보내도록 변경했다.
  - 실제 저장/삭제 작업이 끝난 뒤에는 interaction 직접 응답 대신 원본 버튼 메시지를 수정해 결과를 표시하도록 했다.
  - 원본 메시지 수정이 실패하면 후속 ephemeral 응답으로 대체하고, 만료된 interaction은 로그만 남기도록 방어했다.
  - 버튼 처리 시 defer 후 원본 메시지를 수정하는 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check` 검증을 통과했다.

## 2026-06-05 - 이미지 첨부 승인 후 분석 경로 보정

- 작업 이름: 승인 버튼으로 이미지 첨부 저장 시 문서 분석 에이전트 사용
- 진행상황: 완료
- 진행내용:
  - 이미지 첨부 후 `승인` 버튼을 누르면 기존 메모 저장 경로가 실행되어 `비전 OCR이 필요하지만 처리되지 않았다`는 답변이 나오는 문제를 확인했다.
  - pending 첨부 승인 시 원본 메시지를 가져온 뒤 이미지 첨부가 포함되어 있으면 `Memory Agent`가 아니라 `Document Analysis Agent`로 넘기도록 변경했다.
  - 승인된 이미지 분석도 `gpt-5.4-mini`와 detail `auto`를 사용하고, 분석 결과를 문서 기억으로 저장하도록 했다.
  - 비전 분석 프롬프트를 OCR 중심에서 이미지의 시각적 내용 설명과 텍스트 추출을 함께 수행하는 방향으로 보강했다.
  - `IMG_7700.jpg` 같은 이미지 첨부 승인 흐름이 비전 분석을 호출하고 문서로 저장되는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check` 검증을 통과했다.

## 2026-06-05 - 혼합 PDF 선택적 이미지 분석

- 작업 이름: 텍스트+이미지 혼합 PDF 비전 선별 분석
- 진행상황: 완료
- 진행내용:
  - 텍스트가 추출되는 PDF라도 이미지 리소스가 있으면 페이지 이미지를 렌더링해 비전 선별을 수행하도록 했다.
  - 비전 선별은 `gpt-5.4-mini`와 detail `auto`를 사용하며, 차트/표/그래프/도식/UI 캡처처럼 중요한 시각 자료가 있는 페이지만 본분석 대상으로 고른다.
  - 로고, 장식 이미지, 반복 헤더/푸터, 본문 텍스트와 중복되는 이미지는 분석하지 않도록 선별 프롬프트를 고정했다.
  - 사용자가 `텍스트만 요약해줘`라고 요청하면 혼합 PDF 이미지 선별과 분석을 모두 생략하도록 했다.
  - 혼합 PDF에서 비전 선별이 실행되면 PDF 원본 파일 크기 기준으로 비전 OCR 사용량을 1회만 기록하도록 했다.
  - 텍스트만 PDF, 장식 이미지 PDF, 중요 차트 PDF, 텍스트만 요청, 용량 초과 케이스 테스트를 추가했다.

## 2026-06-05 - 안정 포맷 파일 확장자 확대

- 작업 이름: 로컬 텍스트 추출 지원 확장자 추가
- 진행상황: 완료
- 진행내용:
  - 일반 텍스트 `.log`, `.text`, `.rst`, `.ini`, `.conf`, `.cfg`와 구조화 텍스트 `.json`, `.jsonl`, `.yaml`, `.yml`, `.xml`, `.html`, `.htm`, `.tsv`를 지원 목록에 추가했다.
  - 구조화 문서 `.pptx`, `.hwpx`와 오픈 문서 `.odt`, `.ods`를 로컬 ZIP/XML 기반 텍스트 추출 대상으로 추가했다.
  - `.pptx`는 슬라이드 텍스트와 speaker notes XML을 함께 추출하고, `.hwpx`는 내부 XML 본문과 표 셀 텍스트를 줄 단위로 정리하도록 했다.
  - `.hwp`, `.ppt`, `.xls`, `.doc`, `.pages`, `.key`, `.numbers`는 구형/전용 포맷으로 직접 지원하지 않고 변환 안내 대상으로 유지했다.
  - 새 지원 확장자와 제외 확장자 판별, JSON/JSONL/YAML/XML/HTML/TSV/PPTX/HWPX/ODT/ODS 추출 테스트를 추가했다.

## 2026-06-05 - 파일 관련 기억 삭제 범위 보정

- 작업 이름: 문서 삭제 요청과 전체 기억 삭제 확인 분리
- 진행상황: 완료
- 진행내용:
  - `파일 관련 기억 전부 삭제해` 요청이 텍스트 메모까지 포함한 전체 기억 삭제 확인으로 이어질 수 있는 문제를 확인했다.
  - 삭제 요청에 파일/문서 범위가 명시되고 메모 범위가 명시되지 않은 경우, 전체 기억 삭제가 아니라 문서 ID 전체에 대한 지정 삭제 확인을 만들도록 변경했다.
  - 전체 삭제 확인 대기 중 사용자가 `메모 한개 제외하고 모두 삭제해`, `파일만 전부 삭제해`처럼 조건을 바꾸면 기존 삭제 대기를 취소하고 새 요청을 요구하도록 했다.
  - 파일 관련 삭제는 문서만 대상으로 잡히고, 조건 변경 확인 문장은 삭제를 실행하지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check` 검증을 통과했다.

## 2026-06-05 - 웹검색 본문 확인과 검색 필요도 점수화

- 작업 이름: Naver 웹검색 결과 선별 본문 확인 및 라우터 검색 필요도 점수화
- 진행상황: 완료
- 진행내용:
  - Naver Search API 요청 결과 수 기본값을 10개로 변경했다.
  - Router Agent에 검색 필요도 점수와 `required`, `ask_user`, `not_needed` 결정을 추가했다.
  - 검색 필요도 70점 이상은 `web_search`, 45~69점은 `confirm_web_search`, 44점 이하는 일반 intent로 분기하도록 했다.
  - `메이플스토리 확률공개표 참고해서 ... 기댓값 메소`처럼 외부 기준표가 필요한 계산 요청을 확실한 검색 요청으로 분류하도록 했다.
  - 검색 필요성이 애매하면 사용자에게 검색해볼지 묻고, 승인 시 원래 질문으로 웹검색을 실행하는 pending store를 추가했다.
  - WebSearchAgent가 검색 결과 중 LLM 판단으로 최대 5개 링크의 공개 HTML 본문을 확인하도록 했다.
  - 일반 HTML과 Naver 블로그 모바일 URL 보정 기반 본문 추출 도구를 추가했다.
  - WebSearchAgent가 사용자 문장을 그대로 검색하지 않고 LLM이 검색 계획을 만들어 최대 4개 query로 나눠 검색하도록 변경했다.
  - 계산형 질문은 기준표, 비용, 확률, 규칙처럼 답변에 필요한 정보를 나눠 검색하도록 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `assistant-admin doctor` 검증을 통과했다.

## 2026-06-05 - OpenAI temperature 미지원 모델 오류 보정

- 작업 이름: temperature 미지원 모델 fallback 및 메시지 예외 처리 안정화
- 진행상황: 완료
- 진행내용:
  - OpenAI Responses API 호출에서 모델이 `temperature` 파라미터를 지원하지 않아 400 오류가 발생하는 문제를 확인했다.
  - `OpenAIService`가 `temperature` 미지원 오류를 감지하면 같은 요청을 `temperature` 없이 한 번 재시도하도록 변경했다.
  - `gpt-5` 계열 모델에는 처음부터 `temperature`를 보내지 않도록 해 fallback 전 400 로그가 반복되지 않게 했다.
  - Discord `on_message` 예외 처리 중 `raw_answer`가 할당되지 않아 `UnboundLocalError`가 추가로 발생하던 문제를 보정했다.
  - 웹검색 최종 요약 모델 호출이 시간 초과되면 검색 결과와 본문 확인 자료를 버리지 않고 fallback 답변을 반환하도록 했다.
  - temperature fallback과 `gpt-5` 계열 temperature 생략 회귀 테스트를 추가했다.
  - `python3 -m pytest`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests` 검증을 통과했다.

## 2026-06-05 - 장시간 답변 처리 진행 메시지 추가

- 작업 이름: OpenAI timeout 비활성화 및 15초 주기 진행 안내
- 진행상황: 완료
- 진행내용:
  - 정확한 답변을 위해 OpenAI SDK timeout을 비활성화하고 API가 실제 실패하지 않는 한 끝까지 기다리도록 변경했다.
  - Discord 메시지 처리 시간이 길어지면 진행 중 메시지를 한 번 보내고, 이후 15초마다 같은 메시지를 수정하도록 했다.
  - 진행 메시지는 횟수에 따라 다른 문구를 사용하고, 5회 이후에는 대략적인 경과 시간을 포함한다.
  - `OPENAI_TIMEOUT_SECONDS=0`을 timeout 비활성화 의미로 문서화하고 doctor 검증에서 0을 허용하도록 변경했다.
  - 진행 메시지 문구와 OpenAI timeout 비활성화 회귀 테스트를 추가했다.

## 2026-06-05 - 웹검색 캐시 도입

- 작업 이름: 웹검색 결과 및 페이지 본문 캐시 구현
- 진행상황: 완료
- 진행내용:
  - Naver Search API 결과와 선별 링크 본문을 SQLite에 저장하는 `web_search_cache`, `web_page_cache` 테이블을 추가했다.
  - 캐시 hit/miss는 저장소가 정규화 검색어, 정규화 URL, TTL, 파싱 성공 여부로 판단하도록 구현했다.
  - WebSearchAgent가 요청 문구를 기준으로 `allow_cache`, `prefer_fresh`, `bypass_cache` 정책을 정하도록 했다.
  - 일반 요청은 TTL 내 캐시를 먼저 사용하고, 최신성 높은 요청은 새 조회를 우선하며 실패 시 유효 캐시로 fallback하도록 했다.
  - 사용자가 새로 검색 또는 캐시 없이 검색을 명시하면 캐시 조회를 건너뛰고 새 결과로 캐시를 갱신하도록 했다.
  - 기본 TTL은 검색 결과 30분, 페이지 본문 360분으로 설정했다.
  - 봇 시작 시 만료 캐시를 자동 정리하고, `assistant-admin cleanup --target cache --force`로 만료 캐시를 정리할 수 있게 했다.
  - 서버 재시작 후에도 캐시가 유지되는지, 만료 캐시가 삭제되는지, WebSearchAgent가 캐시 hit/fallback을 사용하는지 테스트를 추가했다.

## 2026-06-05 - URL 직접 활용 기능 추가

- 작업 이름: 사용자 URL 본문 직접 확인 및 관련 검색 결합
- 진행상황: 완료
- 진행내용:
  - 라우터에 `web_url` intent를 추가해 URL 포함 메시지를 Naver 검색이 아니라 URL 직접 읽기 경로로 분류하도록 했다.
  - URL만 보낸 경우 본문을 짧게 요약하고 추가 요청사항이 있는지 묻도록 했다.
  - URL과 함께 요약, 분석, 질문 답변 요청이 있으면 URL 본문만 근거로 응답하도록 했다.
  - URL과 함께 관련 내용 검색을 명시한 경우 URL 본문을 먼저 읽고 Naver Search API 검색 결과와 선별 본문을 함께 활용하도록 했다.
  - URL 직접 읽기에도 페이지 본문 캐시를 적용해 같은 URL 반복 요청에서 TTL 내 재fetch를 피하도록 했다.
  - URL 감지, URL-only 판별, 라우팅, 직접 URL 요약, 캐시 hit, URL+관련 검색 결합 테스트를 추가했다.

## 2026-06-05 - 웹페이지 본문 읽기 지연 방지

- 작업 이름: 웹검색 선별 링크 본문 읽기 outer timeout 적용
- 진행상황: 완료
- 진행내용:
  - `urllib` 내부 timeout만으로는 DNS, TLS, 리다이렉트, 서버 응답 지연 상황에서 메시지 처리 전체가 오래 대기할 수 있는 문제를 확인했다.
  - WebSearchAgent의 페이지 본문 읽기에 `asyncio.wait_for` 기반 outer timeout을 추가했다.
  - 페이지 읽기가 `WEB_PAGE_TIMEOUT_SECONDS`를 넘기면 실패한 `PageContent`로 전환하고 다음 처리 단계로 진행하도록 했다.
  - 여러 선별 링크를 순차로 읽지 않고 병렬로 읽도록 바꿔, 최대 지연 시간이 `페이지 수 x timeout`으로 늘어나지 않게 했다.
  - 느린 URL reader가 전체 응답을 붙잡지 않고 실패 처리되는 회귀 테스트를 추가했다.

## 2026-06-05 - 공통 실행 컨텍스트 전달 구조 구현

- 작업 이름: 압축 요약과 focused context 기반 에이전트 컨텍스트 전달
- 진행상황: 완료
- 진행내용:
  - `ExecutionContext`를 추가해 압축 요약, 최근 대화, focused context, 라우터 판단 이유와 검색 필요도 정보를 묶도록 했다.
  - `ROUTER_CONTEXT_MESSAGES`, `AGENT_CONTEXT_MESSAGES`, `FOCUSED_CONTEXT_MAX_CHARS`, `RESPONSE_CONTEXT_MAX_CHARS` 설정을 추가했다.
  - Discord 봇과 로컬 CLI에서 메시지 처리 시작 시 라우터용 컨텍스트와 실행용 컨텍스트를 생성하도록 했다.
  - `AgentContext`에 실행 컨텍스트를 추가하고 registry dispatch를 통해 주요 에이전트에 전달하도록 했다.
  - ConversationAgent는 압축 요약과 최근 대화가 포함된 실행 컨텍스트를 사용할 수 있게 했다.
  - WebSearchAgent는 focused context와 라우터 판단 정보를 검색 계획 생성에 사용해 후속 질문의 생략된 대상을 복원하도록 했다.
  - MemoryAgent recall은 focused context를 함께 받아 저장 기억/문서 조회 질문의 후속 맥락을 활용할 수 있게 했다.
  - 컨텍스트 builder, 후속 질문 검색어 보강, 응답 composer 맥락 제한 테스트를 추가했다.

## 2026-06-05 - 컨텍스트 전달 및 압축 요약 보강

- 작업 이름: 문서 분석 컨텍스트 전달 및 전체 에이전트 응답 후 압축 갱신
- 진행상황: 완료
- 진행내용:
  - DocumentAnalysisAgent가 `ExecutionContext`를 받아 직전 대화 기준, 비교 대상, 분석 관점을 문서 분석 답변 프롬프트에 포함하도록 했다.
  - 혼합 PDF 시각 페이지 선별 프롬프트에도 관련 대화 맥락을 포함하도록 했다.
  - Discord 봇은 에이전트 종류와 관계없이 사용자/비서 메시지를 저장한 뒤 압축 요약 필요 여부를 확인하도록 했다.
  - 로컬 CLI 대화 경로도 같은 압축 요약 정책을 사용하도록 했다.
  - 압축 기준은 전체 최근 대화 문자 수가 아니라 마지막 요약 이후 새로 쌓인 대화 문자 수로 변경해 반복 요약 비용을 줄였다.
  - 새 요약을 만들 때 기존 요약과 최근 대화를 함께 입력해 오래된 핵심 맥락이 새 요약에서 누락되지 않도록 했다.
  - 문서 분석 프롬프트 컨텍스트 포함과 마지막 요약 이후 문자 수 계산 테스트를 추가했다.

## 2026-06-05 - 사용자 기준 다른 위치 맥락 전달 보강

- 작업 이름: DM/채널/스레드 이동 시 같은 사용자 최근 맥락 포함
- 진행상황: 완료
- 진행내용:
  - `ExecutionContext`에 같은 사용자의 다른 대화 위치 최근 맥락 필드를 추가했다.
  - 라우터, 전문 에이전트, 응답 작성자가 현재 대화 맥락과 별도로 다른 위치 맥락을 참고할 수 있도록 했다.
  - `USER_CONTEXT_CONVERSATIONS`, `USER_CONTEXT_MAX_CHARS` 설정을 추가해 포함할 다른 위치 수와 총 길이를 제한했다.
  - 다른 위치 맥락은 현재 대화 위치를 제외하고, 같은 `user_id`의 DM/채널/스레드 최근 요약 또는 최근 메시지 미리보기만 포함한다.
  - 같은 사용자 다른 위치 맥락 포함, 현재 위치 제외, 다른 사용자 제외 테스트를 추가했다.

## 2026-06-05 - 최근 메모 수정 맥락 개선

- 작업 이름: 방금 저장한 메모 덧붙임 및 예시 기반 수정 처리
- 진행상황: 완료
- 진행내용:
  - `방금 저장한 메모 뒤에 ... 덧붙여줘`, `메모 12에 ... 추가해줘` 같은 표현을 메모 수정 의도로 라우팅하도록 했다.
  - 메모 수정 파서에 append 전용 추출을 추가해 기존 메모 본문 뒤에 새 내용을 이어 붙일 수 있게 했다.
  - `그거`, `아까`, `그 메모` 같은 최근 대상 표현도 최근 메모 수정 대상으로 인식하도록 보강했다.
  - `네가 예를 들어준 내용 그대로 수정해줘`처럼 직전 봇 답변의 예시를 참조하는 표현은 최근 assistant 메시지의 백틱 예시에서 수정 본문을 추출하도록 했다.
  - 관련 휴리스틱 테스트와 메모 저장소 업데이트 테스트를 추가했다.

## 2026-06-05 - 공통 작업 상태 기반 후속 맥락 판단 도입

- 작업 이름: 라우터+에이전트 공통 작업 상태 연결 구조
- 진행상황: 완료
- 진행내용:
  - `OperationResult`에 `subject`, `slots`, `artifacts`, `available_actions`, `retryable` 필드를 추가해 다음 턴에서 재사용 가능한 실행 상태를 표현하도록 했다.
  - `conversation_turn_states` 테이블과 `ConversationTurnStateStore`를 추가해 에이전트 실행 결과를 사용자/대화 위치 기준 최근 작업 상태로 저장하도록 했다.
  - 라우터 입력에 최근 작업 상태 후보를 포함하고, 라우터 출력에 `context_link`, `linked_state_id`, `link_confidence`, `resolved_slots`, `clarification_question`을 추가했다.
  - 연결 확신이 낮으면 자동 실행하지 않고 확인 질문으로 멈추도록 Discord와 CLI 오케스트레이션에 가드레일을 추가했다.
  - Weather Agent가 linked state/resolved slots의 지역을 현재 메시지에 명시 지역이 없을 때만 사용하도록 적용했다.
  - Memory Agent가 linked state/resolved slots의 `memory_id`, `document_id`, `document_ids`를 조회/수정/삭제 후속 요청에서 사용하도록 했다.
  - WebSearchAgent가 `다시 검색해` 같은 짧은 후속 요청에서 linked state의 이전 query를 사용하도록 했다.
  - DocumentAnalysisAgent가 첨부 없이 `방금 문서 다시 분석해봐`처럼 요청해도 linked state의 저장 문서 ID로 재분석하도록 했다.
  - TaskAgent가 linked state의 `task_id`를 사용해 `그거 완료했어`, `그거 삭제해` 같은 후속 작업을 처리하도록 했다.
  - ReminderAgent 결과가 `reminder_id`, 예약 시각, 알림 텍스트를 공통 상태 필드로 남기도록 했다.
  - 문서 분석, 웹검색, 메모 저장/수정 결과가 공통 상태 필드를 직접 채우도록 보강했다.
  - 라우터 모델 실패 fallback도 짧은 후속 요청과 최근 작업 상태 후보를 함께 보고 기존 작업 intent를 이어받을 수 있게 했다.
  - 최근 작업 상태 후보가 여러 개이고 후속 요청 대상이 불명확하면 자동 실행하지 않고 확인 질문으로 멈추도록 했다.
  - 후속 요청에 후보 subject의 구체 토큰이 포함된 경우에만 해당 후보를 선택하고, 일반 토큰만으로는 연결하지 않도록 했다.
  - `다시해봐`처럼 짧은 메시지가 이전 작업과 무관하거나 후보가 모호할 때 에이전트 실행으로 새지 않는 회귀 테스트를 추가했다.
  - 라우터 fallback이 후보의 `slots`, `artifacts`, `actions`를 파싱해 ID 기반 문서 재분석, 대명사 기반 할 일 완료 같은 후속 요청도 공통 상태로 연결하도록 보강했다.
  - `오늘 저녁 뭐 먹지?`처럼 최근 작업 상태와 무관한 새 대화는 상태 후보가 있어도 연결하지 않는 회귀 테스트를 추가했다.
  - 라우터 모델 프롬프트에 `state_id`, `subject`, `slots`, `artifacts`, `actions`, `retryable` 해석 규칙과 연결/비연결 예시를 추가했다.
  - 모델이 정상 응답하는 경로에서도 새 지역/새 주제는 이전 상태에 연결하지 않고, 필요한 실행 값은 `resolved_slots`에 담도록 명시했다.
  - 라우터 프롬프트가 공통 작업 상태 필드와 비연결 예시를 계속 포함하는지 확인하는 회귀 테스트를 추가했다.
  - 최근 작업 상태 후보를 현재 대화 위치뿐 아니라 같은 사용자 다른 위치에서도 가져오도록 확장했다.
  - 다른 위치의 작업 상태는 `location=다른 위치`, `conversation_id=...`로 라벨링해 라우터와 에이전트가 위치 변경을 인지할 수 있게 했다.
  - linked state 조회도 같은 사용자 기준으로 허용해 서버에서 만든 작업 상태를 DM 후속 요청에서 이어받을 수 있게 했다.
  - 다른 위치 상태 후보 포맷을 라우터 fallback이 계속 읽을 수 있는지 확인하는 회귀 테스트를 추가했다.
  - 다른 위치 후보를 `그거`, `방금 것`, `아까 것` 같은 대명사로만 이어받는 경우에는 자동 실행하지 않고 “여기서 이어갈까요?” 확인 질문으로 전환했다.
  - `문서 7`처럼 대상 ID나 제목이 명확한 다른 위치 후속 요청은 바로 연결할 수 있도록 유지했다.
  - 라우터 모델 프롬프트에도 다른 위치 후보는 대명사만으로 자동 실행하지 말고 확인 질문을 하도록 명시했다.
  - 다른 위치 확인 질문이 단일 후보를 가리킬 때 `pending_linked_state_id`, `pending_intent`, `pending_context_link`, `pending_resolved_slots`를 저장하도록 했다.
  - 사용자가 직전 확인 질문에 `응`, `네`, `맞아`처럼 긍정하면 pending state 정보를 사용해 원래 작업 상태로 다시 라우팅하도록 했다.
  - `clarify` 라우팅에서도 단일 후보가 명확하면 `linked_state_id`와 `resolved_slots`를 보존하도록 모델 프롬프트, fallback, 파싱 테스트를 보강했다.
  - 사용자가 직전 확인 질문에 `아니`, `취소`, `하지마`처럼 거부하면 `cancel_pending`으로 라우팅하고 확인 상태를 만료 처리하도록 했다.
  - 거부된 확인 상태가 다음 긍정 답변에서 다시 살아나지 않도록 `ConversationTurnStateStore.expire()`를 추가했다.
  - 후속 작업 승인/거부 흐름을 라우터 fallback과 Discord 봇 단위 테스트로 검증했다.
  - 후속 확인 질문, 웹검색 확인처럼 `needs_input`/`confirm_required` 상태는 기본 24시간이 아니라 `pending_confirmation_ttl_minutes`만큼만 후보로 남도록 TTL을 조정했다.
  - 실패한 날씨 조회처럼 실제 재시도 가능한 작업 상태는 기존처럼 장시간 후보로 유지해 후속 요청 맥락을 놓치지 않도록 했다.
  - 확인 상태 TTL과 실제 작업 상태 TTL을 분리하는 회귀 테스트를 추가했다.
  - 후속 작업 확인 질문(`needs_input` + `clarify`)에도 승인/거부 버튼을 붙이도록 했다.
  - 승인 버튼을 누르면 저장된 `pending_linked_state_id`와 `pending_resolved_slots`로 원래 에이전트를 실행하고, 확인 상태는 만료 처리하도록 했다.
  - 거부 버튼을 누르면 채팅 거부와 동일하게 이어가기 상태를 취소하고 확인 상태를 만료 처리하도록 했다.
  - 후속 작업 확인 버튼 생성, 승인 dispatch, 거부 만료 회귀 테스트를 추가했다.
  - 작업 상태 후보 조회 시 현재 위치 후보가 limit을 모두 차지해도 같은 사용자 다른 위치 후보가 밀려나지 않도록 현재 위치와 다른 위치를 각각 조회해 합치도록 했다.
  - 채팅 위치를 옮긴 직후에도 다른 위치에서 하던 작업 후보가 라우터 컨텍스트에 남는지 확인하는 회귀 테스트를 추가했다.
  - `TURN_STATE_CURRENT_LIMIT`, `TURN_STATE_CROSS_LOCATION_LIMIT` 설정을 추가해 현재 위치/다른 위치 작업 상태 후보 수를 운영 중 조절할 수 있게 했다.
  - `.env.example`, README, plan 문서에 작업 상태 후보 수 설정을 추가했다.
  - context builder와 local CLI가 새 작업 상태 후보 수 설정을 사용하는지 확인하는 회귀 테스트를 추가했다.
  - fallback 라우터가 `삭제`, `수정`, `완료` 같은 액션 단어만으로 다른 intent의 최근 작업을 과연결하지 않도록 제한했다.
  - action 기반 연결은 현재 메시지가 대명사 후속 요청이거나, 후보 intent와 기본 라우팅 intent가 호환될 때만 허용하도록 했다.
  - `파일 관련 기억 전부 삭제해`가 최근 할 일 후보의 delete action에 빼앗기지 않는지, `그거 삭제해`는 최근 할 일 후보로 이어지는지 회귀 테스트를 추가했다.
  - 후보가 여러 개 있을 때도 명시적 새 요청은 `clarify`로 빼앗기지 않고 기본 라우팅을 유지하도록 했다.
  - 다중 후보 `clarify`는 `그거`, `방금`, `아까` 같은 대명사 후속 요청이거나 기본 라우팅이 일반 대화인 경우에만 허용했다.
  - 여러 후보가 있는 상황에서 `파일 관련 기억 전부 삭제해`는 기억 삭제로 유지되고, `그거 삭제해`는 확인 질문으로 가는 회귀 테스트를 추가했다.
  - 라우터 모델 프롬프트에도 후보가 여러 개여도 새 요청 대상이 명시되면 `clarify`하지 말고 원래 intent를 유지하도록 명시했다.
  - 모델 경로에서도 `파일 관련 기억 전부 삭제해` 예시와 다중 후보 확인 질문 제한 규칙이 유지되는지 회귀 테스트를 추가했다.
  - 라우터 JSON 파싱에서 자동 실행 링크와 확인 질문용 단일 후보 링크의 confidence 처리를 분리했다.
  - `clarify`가 단일 후보와 `resolved_slots`를 함께 제공하면 자동 실행 기준보다 낮은 confidence여도 `linked_state_id`를 보존해 버튼 승인 흐름이 끊기지 않도록 했다.
  - slots 없는 낮은 confidence clarification은 여전히 linked state를 제거해 모호한 후보가 버튼으로 실행되지 않도록 했다.
  - 후속 확인 질문 상태에 `pending_original_text`를 저장해 승인 버튼이나 채팅 승인 후에도 원래 사용자 요청 문장을 에이전트에 전달하도록 했다.
  - 버튼 승인 시 `버튼 승인` 문구가 아니라 원래 `그거 완료했어` 같은 액션 문구로 전문 에이전트를 실행하도록 했다.
  - 채팅 승인 라우팅 결과에도 `pending_original_text`를 resolved slots로 전달해 Discord/CLI dispatch가 같은 원문을 사용할 수 있게 했다.
  - 버튼 승인 후 최종 응답 작성자도 `버튼 승인` 대신 원래 사용자 요청 문장을 참고하도록 했다.
  - 원래 요청 문장이 에이전트 dispatch와 최종 응답 composer에 모두 전달되는지 회귀 테스트를 추가했다.
  - `pending_original_text`, `pending_linked_state_id` 같은 확인용 임시 슬롯이 성공한 작업 상태 후보에 장기 저장되지 않도록 정리했다.
  - 확인 대기 상태에는 pending 슬롯을 유지하고, 완료된 작업 상태에는 실제 실행 슬롯만 남기는 회귀 테스트를 추가했다.
  - 상태 후보 컨텍스트, 라우터 연결 메타데이터, 날씨 재시도 회귀 테스트를 추가했다.
  - `agent_catalog.json`에 에이전트별 `state_outputs`를 추가해 각 에이전트가 후속 맥락 판단에 남겨야 할 `subject`, `slots`, `artifacts`, `available_actions`, `retryable` 단서를 명시하도록 했다.
  - `AgentDefinition`과 라우터 프롬프트 블록이 `state_outputs`를 읽어 모델에게 “후속 맥락 단서”로 전달하도록 했다.
  - 새 에이전트 추가 시 `state_outputs`를 누락하면 카탈로그 빌드와 회귀 테스트에서 실패하도록 해, 앞으로 에이전트를 늘려도 맥락 상태 계약을 빠뜨리지 않게 했다.
  - `plan.md`에 에이전트 카탈로그가 목적/설명/예시뿐 아니라 tool 목록과 후속 맥락 상태 단서까지 관리한다는 원칙을 기록했다.
  - `ConversationAgent.chat`을 문자열 직접 반환에서 `OperationResult` 반환으로 전환해 일반 대화도 `subject`, `slots.topic`, `slots.location_label`, `available_actions.continue`를 남기도록 했다.
  - `UtilityAgent`의 도움말, 상태, 현재 시간, 오늘 브리핑, 대화 맥락 초기화 결과에 `subject`와 카탈로그에 맞는 `slots`/`artifacts`/`available_actions`를 추가했다.
  - 일반 대화와 유틸리티 응답이 후속 맥락 상태 필드를 실제로 채우는지 회귀 테스트를 추가했다.
  - `assistant_bot/route_validation.py`를 추가해 라우터가 반환한 `linked_state_id`를 실행 전에 한 번 더 검증하도록 했다.
  - `continue`, `retry`, `modify` 링크가 연결된 작업 상태의 intent 그룹, 사용 가능 action, retry 가능 여부와 맞지 않으면 자동 실행하지 않도록 했다.
  - 사용자가 새 대상을 명시한 요청에서는 잘못된 링크만 제거하고 원래 intent를 실행하며, `그거`, `방금`, `다시해봐` 같은 애매한 후속 요청에서는 확인 질문으로 전환하도록 했다.
  - Discord 봇과 로컬 CLI 모두 라우터 직후 동일한 링크 검증을 적용하도록 연결했다.
  - 모델 라우터가 최근 할 일 상태를 잘못 연결해도 `파일 관련 기억 찾아줘`는 링크 없이 기억 조회로 진행되고, `그거 삭제해`는 자동 삭제 대신 확인 질문으로 멈추는 회귀 테스트를 추가했다.
  - linked state와 `resolved_slots`의 `task_id`, `memory_id`, `document_id`, `reminder_id` 계열 값이 서로 맞는지 검증해, 링크는 맞지만 실행 ID가 틀어지는 상황을 방지했다.
  - 연결된 할 일 3 상태에 라우터가 `task_id=9`를 잘못 넣어도 `그거 완료했어`가 바로 실행되지 않고 확인 질문으로 멈추는 회귀 테스트를 추가했다.
  - 후속 작업 확인 버튼 승인 경로에도 동일한 route validation을 적용해, 저장된 pending 슬롯이 현재 linked state와 어긋나면 버튼 승인 후에도 dispatch하지 않도록 했다.
  - 버튼 승인 시 pending task 상태는 할 일 3인데 `pending_resolved_slots.task_id=9`인 경우, 전문 에이전트를 실행하지 않고 대상 재확인을 요청하는 회귀 테스트를 추가했다.
  - `assistant-admin turn-states` 명령을 추가해 라우터가 참고하는 최근 작업 상태 후보의 subject, slots, artifacts, available actions, retryable, expires_at을 운영 CLI에서 확인할 수 있게 했다.
  - user_id, conversation_id, status, 만료 상태 포함 여부로 작업 상태 후보를 필터링할 수 있도록 했다.
  - turn state 조회/포맷 테스트와 README/plan 문서 안내를 추가했다.
  - `assistant-admin route` 명령이 단순 휴리스틱만 보여주던 흐름에서 벗어나, user_id/conversation_id/channel_id/guild_id 기준 최근 작업 상태 후보와 실행 전 route validation까지 반영한 미리보기를 출력하도록 했다.
  - 로컬 route 미리보기에서 `그거 완료했어`가 저장된 할 일 상태 후보와 연결되는지 확인하는 회귀 테스트를 추가했다.
  - 최근 작업 상태 후보 조회를 단순 최신순에서 확인 대기 상태, 전문 에이전트 실행 상태, 일반 대화 상태 순으로 정렬하도록 바꿨다.
  - 일반 대화 상태가 여러 개 최신으로 쌓여도 오래된 할 일/문서/날씨 같은 실행 상태가 라우터 후보에서 밀려나지 않도록 했다.
  - 최신 일반 대화 3개가 있어도 할 일 상태 후보가 제한값 안에 포함되는지 회귀 테스트를 추가했다.
  - 작업 상태 후보 우선순위를 더 정교화해 확인 대기 상태, 후속 action/retry 가능한 상태, 그 밖의 전문 에이전트 상태, 일반 대화 상태 순으로 정렬하도록 조정했다.
  - `current_time`, `status`, `help`처럼 단순 유틸리티 상태가 최신이어도 후속 action이 있는 할 일/문서/날씨 상태를 밀어내지 않도록 했다.
  - 최신 현재 시간 조회 상태가 있어도 할 일 상태 후보가 제한값 안에 유지되는 회귀 테스트를 추가했다.
  - `assistant-admin turn-states` 조회 순서도 실제 라우터 후보 우선순위와 동일하게 맞추고, 출력에 priority 값을 추가했다.
  - turn-states CLI에서 후속 action이 있는 할 일 상태가 단순 현재 시간 조회 상태보다 먼저 출력되는지 회귀 테스트를 보강했다.
  - 작업 상태 저장 기준을 추가해 확인 대기, 실패/재시도, artifacts, 후속 action, 주요 ID 슬롯이 없는 단순 유틸리티 응답은 후보로 저장하지 않도록 했다.
  - `current_time` 같은 단순 시간 조회 결과가 slots를 갖고 있어도 turn state에 저장되지 않는 회귀 테스트를 추가했다.
  - 로컬 CLI ask 경로도 Discord 봇과 같은 `should_record_turn_state` 기준을 사용하도록 맞췄다.
  - 일반 `chat` 성공 결과는 turn state 후보로 저장하지 않고 conversation messages/summary가 담당하도록 경계를 조정했다.
  - `chat`이라도 후속 확인 질문처럼 `needs_input`/`clarify` 상태이면 계속 turn state에 저장해 승인/거부 흐름을 유지하도록 했다.
  - 일반 대화 결과가 turn state에 저장되지 않고, 후속 확인 상태는 저장되는 회귀 테스트를 추가했다.
  - 다른 대화 위치의 작업 상태를 라우터 모델이 실수로 `continue`/`retry`/`modify`로 바로 연결하더라도, 일반 메시지 경로에서는 실행 전 검증 계층이 `clarify`로 바꿔 “여기서 이어서 처리할까요?”라고 묻도록 했다.
  - 버튼 승인처럼 사용자가 이미 다른 위치 작업 이어가기를 승인한 흐름에서는 cross-location 실행을 허용하도록 `allow_cross_location` 예외를 두었다.
  - Discord 봇, 로컬 CLI ask, `assistant-admin route` 미리보기가 모두 현재 scope를 route validation에 넘기도록 맞췄다.
  - 다른 위치 링크가 승인 전에는 확인 질문으로 바뀌고, 승인 후에는 유지되는 회귀 테스트를 추가했다.
  - `assistant-admin route` 출력에 실행 기준 scope, 연결된 작업 상태, 최근 작업 상태 후보 목록을 함께 표시해 라우터가 어떤 상태를 보고 후속 맥락을 판단했는지 운영 중 확인할 수 있게 했다.
  - 다른 위치 후보가 있을 때 route 미리보기가 `clarify` 결과와 연결 상태/후보 목록을 함께 보여주는 회귀 테스트를 추가했다.
  - route 미리보기에서 실행 전 검증이 잘못된 링크를 제거한 경우에는 연결된 작업 상태를 `없음`으로 다시 계산해, 검증 전 후보와 최종 실행 상태가 혼동되지 않도록 했다.
  - 직전 확인 질문 승인/거부 판정을 부분 문자열이 아니라 짧고 명확한 확인 표현 중심으로 제한해 `네이버에서 검색해줘`, `아니메 추천해줘` 같은 새 요청이 pending 작업 승인/취소로 오인되지 않도록 했다.
  - pending 확인 상태가 있어도 `네이버에서 OpenAI 검색해줘`는 웹검색 새 요청으로 유지되고, `아니메 추천해줘`는 pending 취소로 처리되지 않는 회귀 테스트를 추가했다.
  - `할 일 추가`, `새 알림`, `새 메모`처럼 새 항목 생성이 명확한 요청은 최근 작업 상태의 수정 action과 겹쳐도 기존 상태에 연결하지 않도록 했다.
  - `할 일 3에 ... 추가`처럼 ID로 기존 대상이 명시된 경우에는 기존 상태 연결을 유지하도록 해, 새 생성과 기존 항목 수정의 경계를 테스트로 고정했다.
  - `새 알림 추가`, `새 메모 추가` 표현을 기본 heuristic이 각각 알림 생성과 기억 저장으로 인식하도록 marker를 보강했다.
  - `context_link=none`인 라우팅 결과에 `resolved_slots`가 들어와도 실행 전 검증에서 제거해, 연결 없는 슬롯이 전문 에이전트 실행값으로 새지 않도록 했다.
  - Weather Agent가 `context_link=none`인 실행 맥락의 `resolved_slots.location`을 지역 후보로 사용하지 않도록 하고, 링크 없는 원주 슬롯만 있는 요청은 지역 확인으로 멈추는 회귀 테스트를 추가했다.
  - Discord 봇 dispatch 직전 실행 맥락에서도 연결 없는 `resolved_slots`가 비워지는지 회귀 테스트를 추가했다.
  - 봇 공통 `is_positive_confirmation`, `is_negative_confirmation`도 부분 문자열 판정 대신 짧고 명확한 확인 표현 중심으로 제한했다.
  - 웹검색 확인 대기가 있어도 `네이버에서 OpenAI 검색해줘`는 이전 검색 승인으로 소비되지 않고 pending을 유지한 채 새 요청으로 라우터에 내려가도록 회귀 테스트를 추가했다.
  - `tests/test_context_routing_matrix.py`를 추가해 heuristic route, context-aware fallback, route validation을 한 번에 통과하는 고위험 맥락 판단 시나리오 매트릭스를 만들었다.
  - 매트릭스에는 현재 위치 할 일 완료, 명시적 기억 삭제, pending 확인 중 새 웹검색, 새 할 일 생성, 기존 할 일 수정, 다른 위치 대명사 후속, 다른 위치 명시 문서 재분석 확인 흐름을 포함했다.
  - 새 에이전트나 라우팅 규칙 추가 시 이 매트릭스를 확장해 맥락 판단 품질이 조용히 후퇴하지 않도록 하는 원칙을 `plan.md`에 기록했다.
  - `context_link=continue/retry/modify`인데 `linked_state_id`가 없는 라우팅 결과는 자동 실행하지 않도록 route validation을 보강했다.
  - state ID 없는 자동 실행 링크가 `다시해봐` 같은 모호한 후속 요청이면 확인 질문으로 전환하고, 명시적 새 요청이면 링크와 slots를 제거하도록 했다.
  - Weather Agent가 `context_link`는 있지만 linked state가 없는 `resolved_slots.location`도 직접 사용하지 않도록 추가 방어했다.
  - route validation, Weather Agent, Discord dispatch 직전 오케스트레이션 회귀 테스트를 추가했다.
  - 연결된 작업 상태의 `user_id`가 현재 사용자와 다르면 자동 실행하지 않고, 모호한 후속 요청에서도 다른 사용자의 `linked_state_id`와 slots를 보존하지 않도록 했다.
  - 다른 사용자 상태가 들어온 경우 모호한 후속 요청은 일반 확인 질문으로 멈추고, 명시적 새 요청은 링크를 제거하는 회귀 테스트를 추가했다.
  - route validation이 라우터 결과의 context link, linked state, confidence, resolved slots를 변경하면 `agent_logs`에 `route_validation` 로그를 남기도록 했다.
  - route validation 로그에 clarification question 변경도 포함해, 확인 질문이 일반 질문으로 바뀌거나 대상 subject가 붙는 변화를 운영 중 추적할 수 있게 했다.
  - Discord 봇과 로컬 CLI ask 경로 모두 validation 조정 로그를 기록하도록 하고, `assistant-admin logs --agent route_validation`으로 확인할 수 있게 했다.
  - route validation 로그가 실제로 저장되는지 봇 오케스트레이션 테스트와 CLI helper 테스트를 추가했다.
  - `agent_catalog.json`의 `state_outputs.available_actions.*`를 실제 에이전트가 반환하는 후속 action과 맞춰 정리했다.
  - Task/Reminder/Document/Web Search/Web URL의 핵심 후속 action이 카탈로그에 유지되는지 회귀 테스트를 추가했다.
  - route validation의 `INTENT_ACTIONS`도 카탈로그/실제 구현 action과 맞춰 `web_search.open_url`, `analyze_document.delete`를 반영하고, `manage_reminder.update`처럼 실제 구현과 맞지 않는 action을 제거했다.
  - 카탈로그 핵심 후속 action이 route validation의 intent action 계약에도 포함되는지 회귀 테스트를 추가했다.
  - 명시적 웹검색 요청이 최근 할 일 subject와 단어가 겹쳐도 기존 할 일 후속 작업으로 과연결되지 않도록 매트릭스 테스트를 추가했다.
  - `병원 예약 다시 검색해줘`처럼 후속 표현과 명시적 웹검색이 섞인 요청도 최근 할 일 subject 일치로 빼앗기지 않도록 fallback explicit match override 조건을 보강했다.
  - `문서 7 다시 분석해봐`처럼 기억/문서 계열 안에서 휴리스틱 intent가 낮게 잡힌 경우에는 ID와 action이 명확하면 저장 문서 분석 후보로 보정할 수 있도록 유지했다.
  - 명시적 날씨 재확인 요청은 같은 지역의 retryable 날씨 상태와 연결되도록 매트릭스 테스트를 추가했다.
  - `그거 말고 서울 날씨 알려줘`, `그거 말고 OpenAI 검색해줘`처럼 앞 맥락을 거부하고 새 요청으로 전환하는 문장은 대명사가 있어도 최근 작업 상태로 자동 연결하지 않도록 했다.
  - `그거 검색해줘`처럼 대명사로 이전 대상을 가리키면서 현재 동사는 웹검색인 요청은 최근 상태의 원래 에이전트가 빼앗지 않고, 웹검색 에이전트에 최근 상태 title/subject 기반 검색어를 넘기도록 했다.
  - Web Search Agent가 linked non-search state에서 전달된 `resolved_slots.query`를 실제 검색어로 사용하는 회귀 테스트를 추가했다.
  - `그거 기억해줘`, `그거 메모해줘`, `그거 저장해줘`처럼 대명사로 이전 대상을 가리키면서 현재 동사는 기억 저장인 요청도 최근 상태의 원래 에이전트가 빼앗지 않고, Memory Agent에 최근 상태 title/subject 기반 저장 본문을 넘기도록 했다.
  - Memory Agent가 linked state에서 전달된 `resolved_slots.memory_text`를 실제 메모 본문으로 저장하는 회귀 테스트를 추가했다.
  - 단일 최근 후보가 있어도 `그거 요약해줘`처럼 후보가 지원하지 않는 action이면 무조건 연결하지 않고 확인 질문으로 멈추도록 fallback 마지막 연결 규칙을 강화했다.
  - 같은 `그거 요약해줘`라도 최근 후보가 문서이고 `summarize` action을 지원하면 문서 분석으로 이어가도록 지원/미지원 action 경계를 매트릭스 테스트에 추가했다.
  - `그 링크 열어줘`, `방금 것 열어줘` 같은 URL 열기 후속 요청은 `open_url` action을 지원하는 웹검색/URL 후보에만 연결하도록 라우터 action 판정을 보강했다.
  - 최근 후보가 할 일처럼 `open_url`을 지원하지 않는 경우에는 `그거 열어줘`가 자동 연결되지 않고 확인 질문으로 멈추는 매트릭스 테스트를 추가했다.
  - `그거 비교해줘`, `그거 검토해줘` 같은 비교/검토 후속 요청은 `compare` action을 지원하는 문서 분석 후보에만 연결하도록 라우터 action 판정을 보강했다.
  - 최근 후보가 할 일처럼 `compare`를 지원하지 않는 경우에는 `그거 비교해줘`가 자동 연결되지 않고 확인 질문으로 멈추는 매트릭스 테스트를 추가했다.
  - 같은 사용자 다른 대화 위치 후보가 있어도 현재 메시지가 전혀 다른 새 주제이면 이어가기 확인을 묻지 않고 새 대화로 처리하도록 매트릭스 테스트를 추가했다.
  - 다른 대화 위치 작업을 여기서 이어갈지 묻는 route validation 확인 질문에 연결 후보 subject를 포함해, 사용자가 어떤 작업을 승인하는지 더 분명히 알 수 있도록 했다.
  - fallback 라우터의 다른 위치 확인 질문이 `intent=chat`으로 원래 작업 의도를 잃지 않도록, 확인 전 원래 route의 intent와 resolved slots를 보존하게 했다.
  - `그거 완료했어`, `그거 검색해줘`, `그거 기억해줘`가 다른 위치 후보를 가리키는 경우에도 승인 버튼 이후 각각 원래 작업/검색/기억 저장으로 이어질 수 있도록 매트릭스 테스트를 보강했다.
  - 사용자가 후속 작업 확인 질문에 답하지 않고 명시적 새 요청을 보내면 이전 pending context link를 자동 만료해, 이후 짧은 `응`이 오래된 확인 질문 승인으로 소비되지 않도록 했다.
  - 새 요청에서는 pending context가 만료되고, 이어가기 확인 흐름에서는 유지되는 Bot helper 회귀 테스트를 추가했다.
  - `응 서울 날씨 확인해줘`, `응 OpenAI 검색해줘`처럼 긍정 표현과 명시적 새 요청이 섞인 문장은 pending context 승인으로 소비하지 않고 새 요청으로 라우팅하도록 했다.
  - 순수 확인 응답인 `응 처리해줘`는 기존처럼 pending context 승인을 유지하고, 긍정 접두어가 붙은 날씨/웹검색 새 요청은 승인으로 오인하지 않는 매트릭스/라우터 테스트를 추가했다.
  - `아니 취소 말고 서울 날씨 알려줘`, `아니 그거 말고 OpenAI 검색해줘`처럼 거부 표현과 명시적 새 요청이 섞인 문장도 pending context 취소로 소비하지 않고 새 요청으로 라우팅하도록 했다.
  - 순수 취소 응답인 `아니 취소해`는 기존처럼 pending context 취소를 유지하고, 부정 접두어가 붙은 날씨/웹검색 새 요청은 취소로 오인하지 않는 매트릭스/라우터 테스트를 추가했다.
  - `context_link=clarify`도 pending 저장 전 route validation에서 linked state 존재 여부, 현재 사용자 일치 여부, resolved_slots 일치 여부를 검증하도록 했다.
  - 다른 사용자 state나 linked state와 맞지 않는 ID 슬롯이 clarify 상태로 보존되지 않는 회귀 테스트를 추가했다.
  - 비전 사용량과 오늘 브리핑 테스트가 실제 실행 날짜에 의존해 실패하지 않도록 봇 설정 timezone 기준 오늘 날짜를 사용하게 정리했다.
  - 다른 대화 위치의 작업을 현재 위치에서 이어갈지 묻는 확인 버튼을 승인했을 때, 원래 사용자 문장과 intent, resolved slots, cross-location linked state가 그대로 dispatch되는 회귀 테스트를 추가했다.
  - `tests/test_bot_helpers.py`, `ruff` 단독 검증으로 해당 버튼 승인 흐름이 통과하는지 확인했다.
  - 버튼 대신 채팅으로 `응`이라고 승인한 경우에도 현재 위치의 pending 확인 상태와 정확히 일치하면 cross-location linked state 실행을 허용하도록 `AssistantBot` 검증 경로를 보강했다.
  - 채팅 승인은 pending target state, intent, context_link, resolved slots, 원래 사용자 문장이 모두 일치할 때만 허용하고, 성공 시 pending 확인 상태를 만료하도록 했다.
  - `test_assistant_bot_chat_approval_allows_cross_location_pending_context`를 추가해 다른 위치 작업 확인 질문에 채팅으로 승인해도 원래 요청이 반복 확인으로 돌아가지 않고 실행되는지 고정했다.
  - 로컬 CLI `assistant-admin ask` 경로에도 같은 pending context 승인 기준을 적용해 Discord와 CLI의 맥락 처리 차이를 줄였다.
  - CLI helper 테스트를 추가해 `응` 같은 순수 승인은 pending context와 정확히 일치할 때만 허용하고, `응 서울 날씨 확인해줘`처럼 새 요청이 섞인 문장은 승인으로 소비하지 않도록 고정했다.
  - `assistant-admin route` 미리보기에도 같은 pending context 승인 기준을 적용해, 실제 ask에서는 실행될 승인 답변이 route 미리보기에서 다시 확인 질문으로 보이는 불일치를 제거했다.
  - route preview는 pending 상태를 만료하지 않고 결과만 보여주도록 유지했으며, 미리보기 후 pending 확인 상태가 남아 있는지 회귀 테스트를 추가했다.
  - Discord, CLI ask, route preview에 나뉘어 있던 pending context 승인 판정을 `route_validation` 공통 helper로 통합했다.
  - `latest_pending_context_state`, `matching_pending_context_approval_state`, 승인 문장 판정, 정수 ID 변환을 공통화해 향후 한 경로만 수정되어 맥락 판단이 갈라지는 위험을 줄였다.
  - 라우터 모델이 pending 확인 승인에서 `pending_original_text`를 누락하더라도 pending 상태에 저장된 원래 사용자 문장을 route에 보강하도록 `route_with_pending_context_original_text`를 추가했다.
  - Discord 채팅 승인 테스트를 원문 누락 fake route로 바꿔도 에이전트 dispatch에는 `그거 완료했어`가 전달되는지 확인했고, 잘못된 원문이 들어온 경우는 승인을 거부하는 route validation 단위 테스트를 추가했다.
  - `assistant-admin route` 미리보기 출력에도 pending 승인에서 복구된 원래 사용자 문장이 `resolved_slots.pending_original_text`로 표시되는지 테스트를 보강했다.
  - 라우터 모델이 pending 확인 승인에서 `resolved_slots`를 일부 또는 전체 누락하더라도 pending 상태의 실행 슬롯과 충돌하지 않으면 pending slots를 route에 보강하도록 했다.
  - route가 pending slots와 다른 값을 명시하면 기존처럼 승인하지 않으며, Discord 채팅 승인 테스트는 fake route가 빈 slots를 반환해도 `task_id`와 원래 사용자 문장이 복구되는지 확인하도록 강화했다.
  - 순수 승인 답변에서 route가 pending slots에 없는 추가 실행 슬롯을 반환하면 pending 승인으로 처리하지 않도록 했다.
  - `응` 승인 route에 `location=서울` 같은 추가 슬롯이 섞이면 hallucinated slot으로 보고 거부하는 route validation 단위 테스트를 추가했다.
  - 후속 대명사 marker를 `이거`, `이것`, `저거`, `저것`, `위에거`, `위의것`, `위것`, `이링크`, `저링크` 계열까지 확장했다.
  - `이거 요약해줘`는 현재 위치 문서 분석 후보로 이어지고, `위에거 완료했어`는 다른 위치 할 일 후보에 대해 바로 실행하지 않고 확인 질문으로 전환되는 매트릭스 테스트를 추가했다.
  - 라우터 fallback에서도 `이 문서`, `이 파일`, `저 문서`, `저 파일`, `위 문서`, `위 파일` 계열을 후속 지시 표현으로 인식하도록 compact marker를 보강했다.
  - `이 문서 요약해줘`가 최근 문서 분석 후보의 `document_ids`를 이어받는 매트릭스 테스트를 추가했다.
  - Web Search Agent 내부 후속 검색 marker도 `이거`, `저거`, `위에거`, `이 문서`, `위 파일` 계열을 인식하도록 확장했다.
  - `그거/이거/위에거/이 문서 검색해줘`가 linked non-search state의 `resolved_slots.query`를 실제 검색어로 사용하는지 테스트를 parameterize했다.
  - Memory helper의 최근 메시지 기억 요청 판정도 `저거 저장해줘`, `위에거 기억해줘`를 포함하도록 확장해 지시문 자체가 메모 본문으로 저장되는 위험을 줄였다.
  - Task helper의 최근 메시지 기반 할 일 생성 판정도 `이거`, `저거`, `위에거`, `위 내용` 계열을 포함하도록 확장했다.
  - `그거/이거/저거/위에거/위 내용 할 일로 추가해줘`가 직전 사용자 메시지에서 할 일을 생성하는지 Task Agent 테스트를 parameterize했다.
  - 다른 위치의 실패한 날씨 조회 뒤 현재 위치에서 `다시해봐`라고 하면 바로 재시도하지 않고 이어갈지 확인하도록 매트릭스 테스트를 추가했다.
  - 다른 위치의 날씨/검색 후보가 있어도 `서울 날씨 어때`, `OpenAI 최신 모델 검색해줘`처럼 새 대상이 명확하면 이어가기 확인을 묻지 않고 새 요청으로 처리하는 매트릭스 테스트를 추가했다.
  - 다른 위치에 재시도 가능한 날씨/검색 후보가 여러 개 있을 때 `다시해봐`가 특정 후보를 임의 선택하지 않고 대상 선택 확인으로 멈추는 매트릭스 테스트를 추가했다.
  - 현재 위치 후보와 다른 위치 후보가 동시에 `그거 완료했어`에 걸리면 현재 위치의 단일 후보를 우선하도록 fallback 라우터를 보강했다.
  - 현재 위치 단일 후보 우선순위를 context routing matrix와 Router Agent 단위 테스트로 고정했다.
  - `할 일 8 완료했어`처럼 사용자가 다른 위치 후보의 ID를 명시하면 현재 위치 후보가 있어도 명시 대상을 선택하고, 실행 전에는 다른 위치 확인으로 전환되는 회귀 테스트를 추가했다.
  - fallback 라우터 단위 테스트에도 명시적 다른 위치 ID가 현재 위치 후보에 빼앗기지 않는지 확인하는 케이스를 추가했다.
  - 같은 현재 위치에 할 일 후보가 여러 개 있을 때 `그거 완료했어`는 임의 선택하지 않고 대상 선택 확인으로 멈추며, `할 일 8 완료했어`처럼 ID가 명시되면 해당 할 일을 선택하는 매트릭스 테스트를 추가했다.
  - 같은 위치 다중 할 일 후보의 대명사/명시 ID 경계를 Router Agent 단위 테스트에도 추가했다.
  - pending context 확인 질문이 여러 개 쌓인 경우 첫 번째 최신 pending 후보만 승인 대상으로 사용하고, 오래된 pending에 맞는 route는 승인하지 않는 route validation 테스트를 추가했다.
  - router context가 최신 pending 확인 상태를 오래된 pending과 일반 작업 상태보다 앞에 배치하는지 context builder 테스트를 추가했다.
  - Router fallback이 pending 후보가 여러 개일 때도 첫 번째 최신 pending 후보로 승인/취소 route를 만들도록 보강했다.
  - 여러 pending 확인 질문이 쌓였을 때 `응`은 최신 pending만 승인하고, `아니 취소해`는 최신 pending만 취소하는 Router Agent 테스트를 추가했다.
  - Bot helper에서 pending 취소 실행 시 최신 pending만 만료되고 오래된 pending은 남는지 확인하는 테스트를 추가했다.
  - 명시적 새 요청이 들어오면 현재 위치의 pending context 확인 상태를 최신 하나만이 아니라 모두 만료하도록 Bot 경로를 보강했다.
  - CLI `ask` 실행 경로에도 같은 pending context 전체 만료 helper를 추가하고, route preview는 계속 읽기 전용으로 유지했다.
  - 새 요청 시 Bot/CLI가 여러 pending context 상태를 모두 만료하고, clarify 흐름에서는 pending을 유지하는지 회귀 테스트를 추가했다.
  - `ConversationTurnStateStore.pending_candidates`를 추가해 현재 위치의 살아있는 pending 후보 전체를 limit 없이 조회하도록 했다.
  - pending 후보가 5개를 초과해도 새 요청에서 전부 만료되는지 Bot/CLI 테스트를 강화하고, 저장소가 다른 위치 pending과 일반 상태를 섞지 않는지 테스트를 추가했다.
  - route validation에서 ID/slot 불일치 때문에 확인 질문으로 전환되는 경우, 불일치한 `resolved_slots`를 pending에 저장하지 않도록 보강했다.
  - slot mismatch 후 확인 질문과 Bot pending 저장값에 잘못된 task_id가 남지 않는지 route validation/Bot helper 테스트를 강화했다.
  - 비워진 pending slots를 버튼으로 승인해도 제거된 slot 값이 되살아나지 않고 linked state 기준으로 실행되는지 Bot helper 테스트를 추가했다.
  - 비워진 pending slots를 `응` 같은 채팅 답변으로 승인해도 제거된 slot 값이 되살아나지 않고 linked state 기준으로 실행되는지 Bot helper 테스트를 추가했다.
  - 에이전트 카탈로그의 `state_outputs`가 `subject`, `retryable`, `slots.*`, `artifacts.*`, `available_actions.*` 형식만 쓰도록 등록 단계 검증을 추가했다.
  - 카탈로그 action 단서가 route validation의 action 어휘와 맞는지, 지원하지 않는 state output 키가 들어오면 실패하는지 회귀 테스트를 추가했다.
  - `infer_available_actions`가 카탈로그/route validation이 모르는 `explain` action을 만들지 않도록 제거하고, 문서/웹/날씨/할 일의 핵심 후속 action을 카탈로그와 맞췄다.
  - fallback action 추론 결과가 route validation action 계약 안에 머무르는지 Bot helper 테스트를 추가했다.

## 2026-06-06 - 채팅 위치 변경 시 이어가기 확인 검증 보강

- 작업 이름: 다른 대화 위치 작업 자동 실행 방지
- 진행상황: 완료
- 진행내용:
  - 사용자가 DM, 서버 채널, 스레드처럼 다른 채팅 위치로 이동했을 때 같은 사용자 작업 상태는 라우터 컨텍스트에 유지하되, 자동 실행은 하지 않는 정책을 재확인했다.
  - 라우터 모델이 다른 위치 작업을 `continue`로 바로 반환하더라도 `AssistantBot.handle_message()`의 실행 전 검증이 `needs_input` 확인 질문으로 바꾸는 회귀 테스트를 추가했다.
  - 확인 질문에는 다른 대화 위치에서 하던 작업임을 드러내고, 사용자가 승인한 뒤에만 현재 위치에서 이어서 실행하도록 한다.

## 2026-06-06 - 최근 메모 후속 수정 라우팅 보강

- 작업 이름: 메모 저장 intent와 메모 수정 intent 분리
- 진행상황: 완료
- 진행내용:
  - `방금 저장한 메모 뒤에 ... 덧붙여줘`처럼 최근 메모를 수정하는 표현이 라우터 fallback에서 다시 `remember`로 바뀌는 빈틈을 확인했다.
  - 최근 상태가 `remember`로 저장된 메모라도 현재 사용자 요청이 `update_memory`, `delete_memory`, `restore_memory` 같은 조작 intent이면 현재 요청 intent를 유지하도록 라우터 fallback을 보강했다.
  - 문서 요약/재분석 후보는 기존처럼 `analyze_document` intent를 유지하도록 보존 범위를 좁혀, 메모 조작과 문서 분석 경계가 서로 침범하지 않게 했다.
  - 같은 위치의 최근 메모 덧붙이기는 `update_memory`로 이어지고, 다른 위치의 최근 메모 덧붙이기는 실행 전 확인 질문으로 전환되는 매트릭스 테스트를 추가했다.
  - Router Agent 단위 테스트에도 최근 메모 덧붙이기가 `update_memory`로 라우팅되는 케이스를 추가했다.

## 2026-06-06 - 다종 후보 혼재 시 대상 종류 필터 보강

- 작업 이름: 메모/문서/할 일/알림 후보 종류 우선 필터
- 진행상황: 완료
- 진행내용:
  - 메모 후보와 문서 후보가 함께 있을 때 `방금 저장한 메모 보여줘`가 불필요하게 대상 확인 질문으로 빠지는 빈틈을 확인했다.
  - 사용자 문장에 `메모`, `문서`, `파일`, `할 일`, `알림`, `날씨`, `링크`처럼 대상 종류가 명시되면 라우터 fallback이 먼저 해당 종류의 후보로 좁히도록 했다.
  - 후보 종류는 artifacts.kind, ID 슬롯, intent를 순서대로 보고 `memory/document/task/reminder/weather/web`으로 정규화한다.
  - 메모와 문서 후보가 함께 있어도 `방금 저장한 메모 보여줘`가 메모 후보를 선택하는 매트릭스/Router Agent 테스트를 추가했다.

## 2026-06-06 - 파일/문서 후속 조회와 날씨 오판 방지

- 작업 이름: 문서 단순 조회와 문서 분석 intent 경계 보강
- 진행상황: 완료
- 진행내용:
  - `방금 저장한 파일 보여줘`가 공백 제거 문자열 안의 `한파` 때문에 날씨 intent로 오판될 수 있는 문제를 확인했다.
  - 날씨 marker 판정은 원문 기준 매칭을 기본으로 하고, `비 와`, `눈 올`처럼 공백 변형이 필요한 marker만 공백 제거 문자열을 보조로 보도록 수정했다.
  - 메모/문서 후보가 함께 있을 때 `방금 저장한 문서 보여줘`는 문서 후보를 고르되 문서 분석이 아니라 저장 문서 조회(`recall`)로 이어지도록 했다.
  - `방금 저장한 문서 요약해줘`, `문서 7 다시 분석해봐`처럼 분석/요약/재분석 동사가 있으면 기존처럼 문서 분석 후보를 유지한다.
  - 파일 문자열 날씨 오판 방지, 문서 단순 조회 후보 선택 매트릭스/Router Agent 테스트를 추가했다.

## 2026-06-06 - 모델 라우터 성공 경로 모호 응답 보정

- 작업 이름: 모델 clarify 과잉 응답 후처리
- 진행상황: 완료
- 진행내용:
  - OpenAI 라우터가 정상 JSON을 반환한 경우에는 기존 deterministic context fallback이 적용되지 않아, 모델이 `chat + clarify`로 과하게 망설이면 명확한 후보도 놓칠 수 있는 구조를 확인했다.
  - 모델 route가 대상 없는 `clarify`이거나 낮은 confidence의 일반 `chat`일 때만 휴리스틱+context fallback을 한 번 적용해 더 구체적인 linked state가 나오면 보정하도록 했다.
  - 모델이 이미 명확한 intent/link를 선택한 경우에는 보정하지 않아 모델 판단을 불필요하게 뒤집지 않는다.
  - 메모/문서 후보가 함께 있어도 모델이 `방금 저장한 메모 보여줘`를 모호하다고 반환하면 메모 후보 `recall`로 보정되는 Router Agent 성공 경로 테스트를 추가했다.

## 2026-06-06 - context_link 의미 정리

- 작업 이름: retry와 continue 경계 보강
- 진행상황: 완료
- 진행내용:
  - 문서 분석 후보가 `retryable=True`이면 `방금 저장한 문서 보여줘`, `방금 저장한 문서 삭제해줘` 같은 조회/삭제 요청에도 `context_link=retry`가 붙는 문제를 확인했다.
  - 조회/수정/삭제/복구/저장/웹 URL 같은 대상 조작형 intent는 후보가 retryable이어도 `continue`를 사용하도록 `context_link_for_candidate_intent`를 추가했다.
  - 날씨 재시도, 문서 요약/재분석처럼 이전 실행을 다시 수행하는 요청은 기존처럼 `retry`를 유지한다.
  - 문서 단순 조회와 문서 삭제가 `continue`로 라우팅되는 매트릭스/Router Agent 테스트를 보강했다.

## 2026-06-06 - 모델 모호 응답 보정 우선순위 테스트 보강

- 작업 이름: 모델 성공 경로의 현재 위치/명시 대상 우선순위 고정
- 진행상황: 완료
- 진행내용:
  - 모델 라우터가 정상 JSON을 반환하더라도 대상 없는 `clarify`로 멈춘 경우 deterministic context fallback 보정이 적용되므로, 이 보정 경로도 기존 fallback과 같은 후보 우선순위를 따라야 한다.
  - 현재 위치 후보와 다른 위치 후보가 함께 있을 때 `그거 완료했어`는 현재 위치 후보를 우선하는 모델 보정 경로 테스트를 추가했다.
  - 현재 위치 후보가 있어도 `할 일 8 완료했어`처럼 다른 위치 대상 ID가 명시되면 명시 대상을 유지하는 모델 보정 경로 테스트를 추가했다.
  - 다른 위치 명시 대상은 RouterAgent에서 선택하되, Bot 실행 전 validation에서 확인 질문으로 전환되는 기존 방어선을 유지한다.

## 2026-06-06 - `작업` 표현의 할 일 맥락 보강

- 작업 이름: 작업/할 일 동의 표현 라우팅 정리
- 진행상황: 완료
- 진행내용:
  - `방금 작업 삭제해줘`, `작업 3 삭제해줘`가 할 일 요청으로 해석되지 않아 알림 후보와 섞이면 확인 질문으로 빠지거나 기억 삭제로 오판될 수 있는 문제를 확인했다.
  - `작업`을 `할 일`, `태스크`, `todo`와 같은 task 계열 marker로 추가했다.
  - task ID 추출, task 이름 변경, task 생성 문장 정리, task 검색/액션 query 정리 패턴에도 `작업`을 반영했다.
  - 할 일 후보와 알림 후보가 함께 있을 때 `방금 작업 삭제해줘`가 할 일 후보를 선택하는 매트릭스/Router Agent 테스트를 추가했다.
  - `작업 3 삭제해줘`가 `manage_task`로 라우팅되고 task ID 3을 추출하는 휴리스틱 테스트를 추가했다.

## 2026-06-06 - 알림 삭제와 리마인더 표현 보강

- 작업 이름: 알림/리마인드/리마인더 동의 표현과 삭제 실행
- 진행상황: 완료
- 진행내용:
  - `알림 5 삭제해줘`, `리마인더 5 삭제해줘`가 기억 삭제로 오판될 수 있고, ReminderAgent에 실제 삭제 실행이 없던 문제를 확인했다.
  - `알림`, `리마인드`, `리마인더`, `reminder`를 같은 알림 계열 표현으로 보고, 삭제 표현이 함께 있으면 `manage_reminder`로 라우팅하도록 했다.
  - `ReminderStore.delete_ids`와 `ReminderAgent.delete_reminders`를 추가해 ID 기반 또는 linked state 기반으로 예약 알림을 삭제할 수 있게 했다.
  - `방금 리마인더 삭제해줘`처럼 ID가 문장에 없어도 실행 컨텍스트의 `reminder_id`가 있으면 해당 알림을 삭제한다.
  - 알림 ID 삭제 라우팅, 알림 후보 선택, ReminderAgent 실제 삭제 테스트를 추가했다.
  - Bot `handle_message`에서 linked reminder 삭제 route가 실제 `ReminderAgent`까지 dispatch되어 저장소의 예약 알림을 삭제하는 통합 테스트를 추가했다.

## 2026-06-05 - 기상청 예특보 Weather Agent 도입

- 작업 이름: 날씨 예보/특보 조회 및 미세먼지 웹검색 보조
- 진행상황: 완료
- 진행내용:
  - `weather` intent와 Weather Agent를 추가해 날씨, 예보, 비, 눈, 우산, 기온, 특보, 미세먼지 요청을 라우팅하도록 했다.
  - 기상청 API허브 `getVilageFcst`, `getWthrSituation`, `getLandFcst` 호출용 KMA provider를 추가했다.
  - 사용자별 최근 날씨 지역 저장소와 KMA API 응답 캐시 테이블을 추가했다.
  - 지역명이 없는 후속 날씨 질문은 같은 사용자 기준 최근 날씨 지역을 재사용하도록 했다.
  - 미세먼지/대기질 요청은 Weather Agent에서 기존 Web Search Agent를 보조 도구로 호출하도록 했다.
  - 기본 지역 CSV와 확장 가능한 `KMA_LOCATION_RESOURCE_PATH` 설정을 추가했다.
  - `assistant-admin import-kma-locations` 명령을 추가해 기상청 동네예보 좌표 엑셀(`nxy.xlsx`)을 Weather Agent 지역 CSV로 변환할 수 있게 했다.
  - 공식 좌표 엑셀 변환 시 읍면동 alias를 생성하고, 기본 시드와 일치하는 주요 지역은 특보 코드를 보존하도록 했다.
  - 날씨 요청은 최신 정보/검색 표현이 섞여도 웹검색보다 Weather Agent로 우선 라우팅하도록 조정했다.
  - 특보 코드가 없는 확장 지역은 특보를 “없음”으로 단정하지 않고 단기예보만 확인했다고 안내하도록 했다.
  - API 키 누락, 지역 누락, API 실패에 대한 안전한 실패 응답을 추가했다.
  - Weather Agent 단위 테스트와 라우팅/카탈로그 테스트를 추가했다.

## 2026-06-06 - 위치 이동 후속 확인과 웹 결과 표현 보강

- 작업 이름: 다른 위치 맥락 확인 정책 및 웹 후보 marker 보강
- 진행상황: 완료
- 진행내용:
  - 같은 사용자가 채팅 위치를 옮긴 뒤 `다시해봐`, `사이트 열어줘`, `방금 것 요약해줘`처럼 이전 작업의 대상이 필요한 요청을 보내면, 다른 위치에서 하던 작업을 여기서 이어갈지 먼저 확인하는 정책을 문서에 명시했다.
  - `서울 날씨`, `OpenAI 최신 모델 검색해줘`, `새 메모 남겨줘`처럼 새 대상이 명확한 요청은 다른 위치 맥락과 엮지 않고 새 작업으로 처리해야 한다는 기준도 함께 정리했다.
  - 라우터 fallback의 웹 후보 종류 marker에 `사이트`, `페이지`, `웹페이지`, `검색결과`를 추가해 `검색 결과 열어줘`, `사이트 열어줘`, `페이지 요약해줘`가 최근 웹검색 결과를 더 안정적으로 고르도록 했다.
  - 최근 웹검색 결과와 할 일 후보가 섞여 있을 때 웹 표현이 웹 후보를 고르는 Router Agent 테스트와 맥락 매트릭스 테스트를 추가했다.

## 2026-06-06 - route validation 후속 표현 안전망 보강

- 작업 이름: 최종 검증 계층 marker 계약 정렬
- 진행상황: 완료
- 진행내용:
  - 라우터 fallback에는 웹 후속 표현이 반영됐지만, 실행 전 검증 계층의 후속 표현 marker에는 `링크`, `사이트`, `페이지`, `웹페이지`, `검색 결과`가 빠져 있어 모델이 state id 없는 자동 링크를 반환했을 때 새 요청처럼 정리될 수 있는 틈을 확인했다.
  - `route_validation`의 후속 표현 marker에 웹 링크/사이트/페이지 계열 표현을 추가해 `사이트 열어줘` 같은 대상 생략 요청은 linked state가 없으면 실행하지 않고 확인 질문으로 멈추도록 했다.
  - pending 확인 승인 판정의 새 요청 marker에도 `작업`, `태스크`, `리마인드`, `리마인더`, `링크`, `사이트`, `페이지`, `웹페이지`, `검색결과`를 추가했다.
  - `응 사이트 열어줘`처럼 긍정 표현과 새 웹 요청이 섞인 문장을 오래된 pending 승인으로 소비하지 않는 회귀 테스트를 추가했다.

## 2026-06-06 - 웹검색 확인 버튼 action 계약 정렬

- 작업 이름: confirm_web_search 버튼 확인 흐름 보강
- 진행상황: 완료
- 진행내용:
  - `agent_catalog.json`의 `confirm_web_search`는 `available_actions.confirm/cancel`을 선언하지만 실제 웹검색 확인 `OperationResult`에는 action이 비어 있어 버튼 생성과 후속 상태 기록이 카탈로그 설명과 어긋날 수 있는 문제를 확인했다.
  - 웹검색 진행 여부 확인 결과에 `subject`, `slots.pending_query`, `available_actions=("confirm", "cancel")`을 채우도록 수정했다.
  - `AssistantBot.confirmation_action_for`가 웹검색 확인 pending을 인식해 승인/거부 버튼을 띄우도록 했다.
  - 버튼 승인 시 기존 웹검색 승인 흐름으로, 버튼 거부 시 기존 웹검색 거부 후 일반 답변 흐름으로 들어가게 해 채팅 승인과 버튼 승인이 같은 pending 저장소를 공유하도록 했다.
  - 웹검색 확인 결과에 버튼이 붙고 `confirm/cancel` action이 유지되는 회귀 테스트를 추가했다.

## 2026-06-06 - confirm/cancel action 공통 계약 등록

- 작업 이름: 카탈로그 action과 route validation action 계약 일치
- 진행상황: 완료
- 진행내용:
  - `confirm/cancel`이 카탈로그에는 선언되어 있었지만 `INTENT_ACTIONS`에는 없어서 테스트가 별도 예외로 허용하고 있던 상태를 확인했다.
  - `confirm_web_search`의 `confirm`, `cancel` action을 `route_validation.INTENT_ACTIONS`에 정식 등록했다.
  - 카탈로그 action 검증 테스트에서 임시 `known_actions.update({"confirm", "cancel"})` 예외를 제거해, 모든 `available_actions.*`가 route validation의 공통 action 어휘에 등록되어야 통과하도록 강화했다.

## 2026-06-06 - 실제 OperationResult action literal 계약 검사

- 작업 이름: daily_briefing action 정리와 실제 반환값 계약 테스트
- 진행상황: 완료
- 진행내용:
  - `daily_briefing` 결과가 `show_tasks`라는 공통 계약 밖 action을 반환하고 있어, 최근 작업 상태 후보에 검증 계층이 모르는 action이 저장될 수 있는 문제를 확인했다.
  - `show_tasks`를 공통 action인 `show`로 바꾸고, `daily_briefing`의 `show`, `recall`, `continue` action을 `INTENT_ACTIONS`에 등록했다.
  - `agent_catalog.json`의 `daily_briefing.state_outputs`에도 `available_actions.show`, `available_actions.recall`을 추가해 카탈로그와 실제 결과를 맞췄다.
  - `assistant_bot` 코드 안의 literal `available_actions` 값이 route validation의 공통 action 어휘 또는 `clarify` 안에 있는지 검사하는 회귀 테스트를 추가했다.

## 2026-06-06 - intent 등록 집합 계약 테스트

- 작업 이름: 카탈로그, RouteIntent, route validation intent 집합 일치 검증
- 진행상황: 완료
- 진행내용:
  - 새 에이전트 추가 시 `agent_catalog.json`, `models.RouteIntent`, `route_validation.INTENT_GROUPS` 중 한 곳만 갱신하면 라우터/검증/실행 흐름이 서로 다른 intent 집합을 보게 되는 위험을 확인했다.
  - `tests/test_agent_registry.py`에 카탈로그 intent 집합, `RouteIntent` Literal 값, `INTENT_GROUPS` 키가 완전히 일치해야 하는 계약 테스트를 추가했다.
  - 이 테스트는 새 intent가 라우터 프롬프트에만 있고 타입/검증에는 없거나, 타입에는 있지만 카탈로그에는 없어 라우터가 선택하지 못하는 상태를 조기에 잡는다.

## 2026-06-06 - 라우터 기본 intent 목록 계약 테스트

- 작업 이름: DEFAULT_ALLOWED_INTENTS와 기본 라우팅 프롬프트 일치 검증
- 진행상황: 완료
- 진행내용:
  - 운영 경로는 registry 기반 allowed intents를 쓰지만, 모델 실패 fallback과 context fallback 일부는 `DEFAULT_ALLOWED_INTENTS`를 직접 참조하므로 새 intent가 기본 목록에서 빠지면 후속 맥락 연결이 실패할 수 있는 구조를 확인했다.
  - 카탈로그 intent 집합이 `DEFAULT_ALLOWED_INTENTS`와도 완전히 일치해야 하는 테스트를 추가했다.
  - `DEFAULT_ROUTING_PROMPT_BLOCK`이 모든 기본 intent를 `- intent:` 형식으로 언급하는지 확인하는 테스트를 추가해, 기본 프롬프트도 intent 계약에서 빠지지 않게 했다.

## 2026-06-06 - 실제 registry handler intent 계약 테스트

- 작업 이름: build_agent_registry handler 등록 집합 검증
- 진행상황: 완료
- 진행내용:
  - 기존 테스트는 카탈로그 항목에 fake handler를 붙여 빌드할 수 있는지만 확인해서, 실제 `build_agent_registry()` 내부 handler dict와 카탈로그 intent가 어긋나는 경우를 직접 잡지 못하는 구조를 확인했다.
  - `tests/test_agent_registry.py`에 실제 `assistant_bot/agent_registry.py`의 handler dict 키를 AST로 읽어 카탈로그 intent 집합과 완전히 일치하는지 확인하는 테스트를 추가했다.
  - 이 테스트는 카탈로그에 추가했지만 실행 handler를 연결하지 않은 intent, 또는 handler만 있고 라우터 카탈로그에는 없는 intent를 조기에 잡는다.

## 2026-06-06 - turn state 후보 포맷 안전화

- 작업 이름: 최근 작업 상태 후보 문자열 파서 안정성 보강
- 진행상황: 완료
- 진행내용:
  - `build_turn_state_context()`가 `subject=... | actions=... | slots=...` 형식의 한 줄 후보를 만들고, 라우터가 정규식으로 이 문자열을 파싱하는 구조를 확인했다.
  - 사용자 입력에서 온 subject, slot, artifact 값에 ` | `, 줄바꿈, `actions=`, `artifacts=` 같은 토큰이 들어오면 라우터 후보 파서가 실제 action/slot 구간을 잘못 읽을 수 있는 위험을 확인했다.
  - turn state context 출력 단계에서 문자열 값의 줄바꿈과 ` | ` 구분자를 정리하고, 라우터 필드명 토큰을 `actions:`처럼 값 안의 일반 텍스트로 바꾸도록 했다.
  - 위험한 구분자가 포함된 작업 상태도 `parse_state_candidates()`가 state id, subject, actions, slots, artifacts를 올바르게 복원하는 회귀 테스트를 추가했다.

## 2026-06-06 - 복합 artifact 상태의 현재 요청 intent 보존

- 작업 이름: 브리핑 artifact 후속 요청 라우팅 보강
- 진행상황: 완료
- 진행내용:
  - 오늘 브리핑처럼 여러 artifact를 담는 상태가 최근 후보에 있을 때 `방금 작업 완료했어` 같은 후속 요청이 `manage_task`가 아니라 `daily_briefing`으로 되돌아갈 수 있는 문제를 확인했다.
  - 라우터 fallback에서 후보 intent가 다르더라도 candidate kind가 현재 요청 대상 계열(task/reminder/memory/document)과 맞으면 현재 요청 intent를 보존하도록 했다.
  - artifact id에서 실행 slot을 복원할 때 문자열/정수 id만 안전하게 사용하도록 변환 helper를 추가했다.
  - route validation도 linked state의 slots/artifacts가 현재 intent 그룹을 제공하면 다른 intent 상태라도 연결을 허용하도록 보강했다.
  - 브리핑 후보 안의 task artifact를 보고 `방금 작업 완료했어`가 `manage_task + task_ids`로 이어지는 Router Agent 테스트와 validation 테스트를 추가했다.

## 2026-06-06 - fallback 라우터 allowed_intents 준수

- 작업 이름: 모델 실패/context fallback 허용 intent 제한 보강
- 진행상황: 완료
- 진행내용:
  - OpenAI 라우터 JSON 파싱은 `allowed_intents`를 적용하지만, 모델 실패 후 휴리스틱/context fallback과 모델 모호 응답 보정은 허용 intent 제한을 끝까지 강제하지 않는 구조를 확인했다.
  - fallback 최종 결과가 `allowed_intents` 밖 intent이면 `chat` fallback으로 정리하고 `context_link`, `linked_state_id`, `resolved_slots`를 제거하도록 했다.
  - 모델 모호 응답 보정에서도 context fallback 결과를 허용 intent로 한 번 더 검증해, 허용되지 않은 intent로 모델 route를 덮어쓰지 않게 했다.
  - 최근 weather 실패 후보가 있어도 RouterAgent가 `allowed_intents={"chat", "manage_task"}`로 생성된 경우 `다시해봐`가 weather로 반환되지 않는 회귀 테스트를 추가했다.

## 2026-06-06 - 웹검색 pending 승인 문구 보강

- 작업 이름: 웹검색 확인 전용 승인 판정 추가
- 진행상황: 완료
- 진행내용:
  - 웹검색 확인 안내와 버튼 경로는 `응, 검색해줘`를 승인 문구로 사용하지만, 공통 `is_positive_confirmation()`은 이 문장을 승인으로 보지 않아 사용자가 안내 문구 그대로 답하거나 버튼 승인을 눌러도 pending 웹검색이 실행되지 않을 수 있는 문제를 확인했다.
  - 공통 긍정 판정을 넓히지 않고 `is_web_search_confirmation_approval()`을 추가해 웹검색 pending에서만 `응, 검색해줘`, `검색해줘` 같은 짧은 검색 승인 문구를 허용하도록 했다.
  - `응 OpenAI 검색해줘`, `네이버에서 OpenAI 검색해줘`처럼 새 검색어가 섞인 문장은 pending 승인으로 소비하지 않고 새 요청으로 라우팅되도록 유지했다.
  - 웹검색 pending이 `응, 검색해줘`로 승인되면 저장된 원래 query로 Web Search Agent가 호출되고 pending이 resolve되는 테스트를 추가했다.
  - 로컬 CLI `assistant-admin ask` 경로에도 같은 pending 웹검색 확인 흐름을 추가해, Discord와 CLI의 확인 승인 동작이 갈라지지 않도록 했다.
  - CLI helper 테스트를 추가해 `응, 검색해줘`는 저장된 원래 query를 실행하고, `네이버에서 OpenAI 검색해줘`는 pending 승인으로 소비하지 않도록 고정했다.

## 2026-06-06 - 대화 위치 변경 맥락 힌트 보강

- 작업 이름: 다른 위치 작업 후보의 확인 필요성 명시
- 진행상황: 완료
- 진행내용:
  - 같은 사용자라도 채팅 위치가 바뀐 경우, 이전 위치의 작업 상태를 장기 맥락 후보로 보여주되 바로 실행 가능한 현재 작업처럼 오해하지 않도록 후보 문자열에 `location_note`를 추가했다.
  - 현재 위치 후보는 `현재 대화 위치의 작업`, 다른 위치 후보는 `다른 대화 위치의 작업, 모호한 후속 요청은 실행 전 사용자 확인 필요`로 표시해 라우터 모델이 위치 차이를 더 직접적으로 읽을 수 있게 했다.
  - Router Agent 지침에 `location_note`의 의미를 추가해, 다른 위치 후보는 사용자의 장기 맥락 후보일 뿐 현재 위치에서 바로 실행해도 된다는 뜻이 아니라고 명시했다.
  - 컨텍스트 빌더 테스트와 Router Agent 지침 테스트를 보강해 `location_note`가 출력되고 라우터 지침에 포함되는지 확인했다.

## 2026-06-06 - 다른 위치 최근 대화 요약의 배경 맥락화

- 작업 이름: cross-location conversation context 자동 실행 오해 방지
- 진행상황: 완료
- 진행내용:
  - 작업 상태 후보에는 `location_note`가 들어갔지만, 같은 사용자 다른 위치의 최근 대화 요약 섹션은 여전히 단순 목록이라 라우터가 배경 대화와 실행 대상 후보를 섞어 볼 수 있는 여지를 확인했다.
  - `build_cross_location_context()`가 다른 위치 대화 목록 앞에 “참고용 배경 맥락이며, 이어가기 여부가 불명확하면 먼저 확인한다”는 정책 줄을 추가하도록 했다.
  - 정책 줄이 들어가도 `USER_CONTEXT_CONVERSATIONS`가 의미하는 다른 위치 대화 개수 제한이 줄어들지 않도록 실제 대화 항목 수를 별도 카운터로 관리했다.
  - Router Agent 지침에도 같은 사용자 다른 위치 최근 맥락은 배경 참고용이며, 그 섹션의 주제만으로 이전 위치 작업 실행으로 연결하지 말라고 명시했다.
  - 실행 컨텍스트와 라우터 지침 테스트를 추가해 정책 문구가 모델 입력에 포함되는지 확인했다.

## 2026-06-06 - 후속 표현 marker 계약 보강

- 작업 이름: 라우터 fallback과 route validation 후속 표현 동기화
- 진행상황: 완료
- 진행내용:
  - 라우터 fallback은 `이링크`, `저링크`, `최근것` 같은 붙여 쓴 후속 표현을 일부 알고 있지만, route validation은 공백형 표현 위주라 마지막 검증 계층의 판단이 달라질 수 있는 틈을 확인했다.
  - `route_validation.FOLLOW_UP_MARKERS`에 `이링크`, `저링크`, `최근것`, `최근 것`, `최근 항목`을 추가했다.
  - 라우터 fallback의 후속 표현 marker에도 `이링크`, `저링크`, `최근항목`을 추가해 라우터와 검증 계층이 같은 의미권을 공유하도록 했다.
  - state id 없는 자동 링크가 `이링크 열어줘`, `저링크 열어줘`, `최근것 보여줘`, `최근 항목 다시 확인해줘`를 만나면 새 요청으로 흘리지 않고 확인 질문으로 멈추는 route validation 테스트를 추가했다.
  - `이링크 열어줘`가 최근 웹검색 결과 후보의 `open_url` 후속 요청으로 이어지는 context routing matrix 테스트를 추가했다.

## 2026-06-06 - Task Agent 상세 조회 linked context 우선 적용

- 작업 이름: 할 일 상세 조회의 원문 재해석 방지
- 진행상황: 완료
- 진행내용:
  - Task Agent가 완료/삭제/수정 계열 작업에서는 `ExecutionContext`의 linked task id를 사용하지만, `보여줘/상세` 분기에서는 execution context를 넘기지 않아 원문이나 현재 위치 최신 할 일에 다시 의존하는 문제를 확인했다.
  - `TaskAgent.handle()`의 상세 조회 분기에서 `execution_context`를 `show_task_detail()`로 전달하도록 변경했다.
  - `show_task_detail()`이 linked task id를 먼저 사용하고, 없을 때만 기존처럼 `방금 추가한 할 일` 최신 조회나 명시 ID 조회를 수행하도록 했다.
  - 상세 조회 by-id 로직을 `show_task_details_by_ids()`로 분리해 linked id 조회와 명시 ID 조회가 같은 출력/상태 기록 경로를 쓰도록 했다.
  - 다른 위치에서 생성된 할 일이 현재 위치 최신 할 일보다 오래됐더라도, 승인된 linked state가 있으면 linked task를 보여주는 회귀 테스트를 추가했다.

## 2026-06-06 - Reminder Agent 조회 linked context 우선 적용

- 작업 이름: 알림 조회의 원문 재해석 방지
- 진행상황: 완료
- 진행내용:
  - Reminder Agent는 삭제 요청에서는 `ExecutionContext`의 linked reminder id를 사용하지만, 최근 알림 조회 요청에서는 항상 사용자 기준 최신 알림만 보는 문제를 확인했다.
  - `asks_to_show_recent_reminder()` 분기에서 `execution_context`를 `show_latest_reminder()`로 전달하도록 변경했다.
  - `show_latest_reminder()`가 linked reminder id를 먼저 조회하고, 없거나 찾지 못할 때만 기존 최신 알림 조회로 fallback하도록 했다.
  - `ReminderStore.get()`을 추가해 user_id 기준으로 특정 알림을 조회할 수 있게 했다.
  - 다른 위치에서 생성된 알림이 현재 위치 최신 알림보다 오래됐더라도, 승인된 linked state가 있으면 linked reminder를 보여주는 회귀 테스트를 추가했다.

## 2026-06-06 - Memory Agent 조회 linked context 우선 적용

- 작업 이름: 저장 항목 조회의 최신 항목 재선택 방지
- 진행상황: 완료
- 진행내용:
  - Document Analysis Agent 자체는 linked document id를 먼저 사용하지만, 저장 문서 조회를 담당하는 Memory Agent `recall()`은 `방금 저장한 문서 보여줘` 같은 최신 항목 조회 문장을 먼저 처리해 linked document id가 있어도 최신 저장 항목을 다시 고를 수 있는 문제를 확인했다.
  - `recall()`에서 명시 ID와 linked memory/document id를 먼저 확인하고, linked 대상이 없을 때만 `asks_to_show_latest_memory()` 최신 항목 조회로 내려가도록 순서를 변경했다.
  - 다른 위치에서 저장된 문서가 현재 위치 최신 메모보다 오래됐더라도, 승인된 linked state가 있으면 linked document를 보여주는 회귀 테스트를 추가했다.

## 2026-06-06 - Task Agent 조작 linked context 우선 적용

- 작업 이름: 할 일 조작의 최신 항목 재선택 방지
- 진행상황: 완료
- 진행내용:
  - Task Agent가 `ExecutionContext`의 linked task id를 받은 뒤에도 `방금 추가한 할 일`, `방금 완료한 할 일` 같은 표현을 만나면 현재 위치의 최신 할 일로 대상을 다시 덮어쓸 수 있는 문제를 확인했다.
  - 기한 제거, 미루기, 제목 변경, 우선순위 변경, 삭제, 다시 열기 분기에서 명시 ID 또는 linked task id가 이미 있으면 최신 항목 fallback을 사용하지 않도록 변경했다.
  - 최신 항목 fallback은 대상 ID가 전혀 없을 때만 작동하도록 낮춰, 라우터가 이전 위치 작업을 이어가기로 확정한 경우 에이전트 내부에서도 같은 대상을 끝까지 유지하게 했다.
  - 현재 채널에 더 최신 할 일이 있어도 linked task id가 있으면 다른 위치에서 만든 할 일을 미루고, 삭제하고, 다시 여는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_memory_store.py -q`와 `python3 -m ruff check assistant_bot/agents/task.py tests/test_memory_store.py`를 통과했다.

## 2026-06-06 - Memory Agent 조작 linked context 우선 적용

- 작업 이름: 저장 항목 수정/삭제의 최신 항목 재선택 방지
- 진행상황: 완료
- 진행내용:
  - Memory Agent의 삭제 분기가 linked memory/document id를 확인하기 전에 `방금 저장한 거 지워줘` 같은 최신 항목 삭제 요청을 먼저 처리해, 다른 위치에서 연결된 저장 항목 대신 현재 위치 최신 항목을 삭제할 수 있는 문제를 확인했다.
  - Memory Agent의 수정 분기도 linked memory id가 있어도 `방금 저장한 메모를 ...로 수정해줘` 표현을 만나면 현재 위치 최신 저장 항목을 수정하려는 문제를 확인했다.
  - 삭제와 수정 모두 명시 ID 또는 linked memory/document id가 있으면 최신 항목 fallback을 사용하지 않도록 변경했다.
  - 다른 위치에서 저장된 메모를 현재 위치 최신 메모보다 우선해 수정/삭제하는 테스트와, 다른 위치에서 저장된 문서를 현재 위치 최신 메모보다 우선해 삭제하는 테스트를 추가했다.
  - `python3 -m pytest tests/test_memory_store.py -q`와 `python3 -m ruff check assistant_bot/agents/memory.py tests/test_memory_store.py`를 통과했다.

## 2026-06-06 - 조작 결과 후속 상태 보강

- 작업 이름: 삭제/완료 결과의 복구·다시열기 맥락 유지
- 진행상황: 완료
- 진행내용:
  - 삭제나 완료 같은 조작 결과가 다음 턴에서 `복구해줘`, `다시 열어줘`로 이어지려면 결과 상태에 대상 ID와 후속 action이 명확히 남아야 하는데, 일부 경로는 facts에만 ID가 있거나 `restore/reopen` action을 남기지 않는 문제를 확인했다.
  - 공통 `infer_turn_slots()`가 `task_ids`, `memory_ids`, `reminder_ids` 같은 복수 ID facts를 슬롯으로 끌어올리도록 보강했다.
  - `infer_available_actions()`와 route validation action 계약, 에이전트 카탈로그에 할 일 `restore/reopen` 후속 action을 추가했다.
  - Memory Agent 삭제 결과는 `restore` action과 메모/문서 ID 슬롯을 남기고, 복구 결과는 `show/delete` action과 복구된 ID 슬롯을 남기도록 했다.
  - Memory Agent `restore()`가 linked memory/document id를 받을 수 있도록 `ExecutionContext`를 전달하고, Agent Registry의 `restore_memory` handler도 execution context를 넘기도록 수정했다.
  - Task Agent 완료 결과는 `reopen`, 삭제 결과는 `restore`, 복구/다시열기 결과는 다시 일반 조작 action을 남기도록 했다.
  - linked 삭제 메모 복구, linked 삭제 할 일 복구, 복수 ID facts 슬롯 추론, action 계약 회귀 테스트를 추가·보강했다.
  - `python3 -m pytest tests/test_memory_store.py tests/test_bot_helpers.py tests/test_agent_registry.py tests/test_route_validation.py -q`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - Memory Agent 결과 intent 정밀화

- 작업 이름: 메모 계열 OperationResult intent 정합성 보강
- 진행상황: 완료
- 진행내용:
  - Memory Agent의 `_result()`가 모든 결과를 넓은 `memory` intent로 기록해, 라우터 검증 계층과 작업 상태 후보가 실제 작업 종류를 정확히 구분하지 못할 수 있는 문제를 확인했다.
  - `remember_text`, `recall`, `list_memories`, `search_memories`, `update`, `delete`, `restore`, `list_deleted_memories` 경로가 각각 `remember`, `recall`, `list_memory`, `update_memory`, `delete_memory`, `restore_memory` intent를 명시하도록 변경했다.
  - `restore_memory` 결과도 공통 subject 추론에서 메모/문서 ID를 읽을 수 있도록 `infer_turn_subject()`의 memory intent 집합을 보강했다.
  - 메모 저장부터 조회, 목록, 수정, 삭제, 복구까지 OperationResult intent가 라우터 intent와 일치하는 통합형 단위 테스트를 추가했다.
  - 향후 Memory Agent의 `_result()` 호출에서 intent를 빼먹으면 실패하는 정적 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_memory_store.py tests/test_agent_registry.py tests/test_bot_helpers.py -q`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - OperationResult intent 계약 검증

- 작업 이름: 카탈로그 밖 결과 intent 차단
- 진행상황: 완료
- 진행내용:
  - 봇 본체의 메시지 처리 예외 fallback이 `RouteIntent`에 없는 `error` intent를 사용하고 있어, 실패 상태가 turn state로 기록될 경우 후속 라우팅 검증에서 해석이 흐려질 수 있는 문제를 확인했다.
  - 예외 fallback을 `chat` intent의 실패 결과로 바꾸고, 원문 topic과 retryable 상태를 남기도록 수정했다.
  - `OperationResult(intent="...")`에 직접 쓰인 문자열이 `models.RouteIntent`에 포함되지 않으면 실패하는 정적 계약 테스트를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py tests/test_bot_helpers.py -q`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - Registry execution context 전달 계약 보강

- 작업 이름: remember handler의 linked context 전달 누락 수정
- 진행상황: 완료
- 진행내용:
  - Memory Agent `remember_text()`는 `ExecutionContext`를 받아 linked state의 `memory_text`를 저장 본문으로 사용할 수 있지만, Agent Registry의 `remember` handler가 `context.execution`을 넘기지 않아 라우터가 대상을 복원해도 실제 저장 단계에서 맥락이 사라질 수 있는 문제를 확인했다.
  - `remember` handler가 `execution_context=context.execution`을 전달하도록 수정했다.
  - context-aware 에이전트 호출이 `context.execution`을 누락하면 실패하는 정적 registry 계약 테스트를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 다른 대화 위치 후속 작업 확인 정책 보강

- 작업 이름: 채팅 위치 변경 시 이전 위치 작업 이어가기 확인
- 진행상황: 완료
- 진행내용:
  - 같은 사용자라도 DM, 채널, 스레드처럼 대화 위치가 바뀌면 이전 위치의 작업 상태를 바로 실행 대상으로 쓰지 않고, 후속 요청인지 먼저 확인해야 하는 요구를 반영했다.
  - 라우터 작업 상태 후보에 `confirm_policy`와 `suggested_question`을 추가해, 다른 위치 후보가 “승인 후 실행 후보”이고 새 요청에는 연결하지 않아야 한다는 신호를 명시했다.
  - Router Agent 프롬프트에 `confirm_policy=ask_before_execute_when_follow_up`와 `ignore_when_new_request`의 의미를 추가해, 모델이 다른 위치 작업을 이어갈지 물어볼 상황과 무시해야 할 새 요청을 구분하도록 했다.
  - fallback 라우터의 상태 후보 파서가 새 필드를 읽고, 다른 위치 후속 요청 확인 시 `suggested_question`을 그대로 사용하도록 변경했다.
  - 다른 위치 후보가 있을 때 `그거 완료했어`는 이어가기 확인 질문을 만들고, 새 요청은 기존처럼 연결하지 않는 회귀 테스트를 보강했다.
  - `python3 -m pytest -q tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_router_heuristics.py tests/test_route_validation.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 최종 응답 작성 컨텍스트 정합성 보강

- 작업 이름: ResponseComposer에 실제 실행 컨텍스트 전달
- 진행상황: 완료
- 진행내용:
  - Discord 본체와 로컬 `assistant-admin ask` 모두 라우팅과 에이전트 실행에는 linked `ExecutionContext`를 사용하지만, 최종 자연어 응답 작성에는 라우팅 전 기본 컨텍스트를 넘기고 있는 문제를 확인했다.
  - 이 경우 작업 실행 대상은 맞더라도 최종 답변이 linked state 또는 resolved slot을 모르는 듯한 어색한 표현을 만들 수 있다.
  - `AssistantBot.handle_message()`에 선택적 execution context sink를 추가해, `on_message()`가 실제 실행에 사용된 컨텍스트를 `ResponseComposer`에 넘기도록 했다.
  - 로컬 `run_local_text_interaction()`도 라우팅 이후 만든 실제 `execution_context`를 최종 응답 작성에 사용하도록 맞췄다.
  - 다른 위치 작업이 연결될 때 응답 작성용 컨텍스트에도 linked state와 resolved slot이 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_bot_helpers.py tests/test_cli.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 라우팅 미리보기 출처 표시

- 작업 이름: `assistant-admin route` 출력의 실제 실행 경로 혼동 방지
- 진행상황: 완료
- 진행내용:
  - 로컬 `assistant-admin route`는 OpenAI 라우터 모델을 호출하지 않고 휴리스틱 라우팅, 맥락 fallback, 실행 전 링크 검증을 빠르게 적용하는 미리보기 경로임을 확인했다.
  - 실제 `assistant-admin ask`와 Discord 본체는 모델 라우터를 먼저 호출하므로, 두 출력이 다를 수 있는 상황을 운영자가 혼동하지 않도록 `RoutePreview.route_source`를 추가했다.
  - `format_route_result()`가 `source: heuristic_context_validation`을 표시하도록 변경했다.
  - `python3 -m pytest -q tests/test_cli.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 모델 라우팅 미리보기 옵션 추가

- 작업 이름: `assistant-admin route --model` 지원
- 진행상황: 완료
- 진행내용:
  - 빠른 휴리스틱 미리보기만으로는 실제 Discord/ask 실행에서 OpenAI 라우터 모델이 어떤 판단을 했는지 재현하기 어렵다는 점을 확인했다.
  - `assistant-admin route --model` 옵션을 추가해, 실제 Agent Registry의 routing prompt와 allowed intent 목록을 사용하는 `RouterAgent`를 호출하도록 했다.
  - 모델 미리보기 결과도 휴리스틱 미리보기와 같은 pending context 승인 보강 및 실행 전 링크 검증을 거치도록 공통 `finalize_route_preview()` helper를 만들었다.
  - 출력 source는 `model_context_validation`으로 표시해 휴리스틱 미리보기와 구분되게 했다.
  - fake OpenAI로 모델 라우터 호출, 입력 메시지 전달, source 표시를 검증하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_cli.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 작업 상태 후보 우선순위 파싱 기반 정렬

- 작업 이름: 라우터 후보 우선순위의 JSON 문자열 비교 제거
- 진행상황: 완료
- 진행내용:
  - `ConversationTurnStateStore.recent_candidates()`가 `available_actions_json NOT IN ('[]', '["continue"]')` 같은 SQL 문자열 비교로 후보 우선순위를 정하고 있어, JSON 공백이나 action 순서에 따라 라우터 후보 순서가 흔들릴 수 있는 문제를 확인했다.
  - 후보 조회를 Python 정렬로 옮기고, 파싱된 `status`, `retryable`, `available_actions`, `intent`를 기준으로 우선순위를 계산하는 `turn_state_candidate_priority()` helper를 추가했다.
  - 운영 CLI `assistant-admin turn-states`도 같은 helper를 사용하게 해, 사람이 보는 후보 우선순위와 라우터가 실제 참고하는 후보 우선순위를 일치시켰다.
  - `available_actions_json`에 공백이 들어간 `["continue"]` 상태가 실질 action 후보보다 앞서지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_context_builder.py tests/test_cli.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 작업 상태 후보 생성 시각 노출

- 작업 이름: `방금`, `아까`, `최근` 판단용 시간 정보 보강
- 진행상황: 완료
- 진행내용:
  - 라우터가 참고하는 최근 작업 상태 후보에는 대상, action, slot은 있지만 후보가 언제 생성됐는지에 대한 `created_at`이 빠져 있어, 시간 의존 후속 표현을 판단할 정보가 부족한 문제를 확인했다.
  - `build_turn_state_context()`가 각 후보 라인에 `created_at`을 포함하도록 변경했다.
  - Router Agent 프롬프트에 `created_at`의 의미와 `방금`, `아까`, `최근` 표현 판단 시 현재 시간과 비교하라는 지침을 추가했다.
  - 라우터 컨텍스트와 프롬프트에 생성 시각 정보가 포함되는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - fallback 라우터의 최신 후보 선택 보강

- 작업 이름: 시간 표현 기반 최신 현재 위치 후보 선택
- 진행상황: 완료
- 진행내용:
  - 라우터 컨텍스트에 `created_at`을 노출했지만, 모델 실패 시 사용하는 fallback 라우터의 `StateCandidate`는 아직 해당 값을 구조적으로 읽지 않는 문제를 확인했다.
  - `StateCandidate`와 `parse_state_candidates()`가 `created_at`을 파싱하도록 변경했다.
  - `방금`, `아까`, `최근`, `마지막` 같은 시간 표현이 있고 현재 위치 후보가 여러 개면, `created_at`과 `state_id` 기준 최신 후보를 선택하도록 했다.
  - 단순 대명사만 있는 경우에는 기존처럼 모호한 후보를 자동 선택하지 않고 확인 질문을 유지한다.
  - 같은 현재 위치의 메모 후보가 여러 개 있을 때 `방금 저장한 메모 보여줘`가 최신 생성 시각 후보를 선택하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_context_builder.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - pending context link 의미 정합성 보강

- 작업 이름: 다른 위치 이어가기 확인의 실행 의미 보존
- 진행상황: 완료
- 진행내용:
  - 다른 위치의 작업 상태가 `retryable=True`이면 삭제, 조회, 수정 같은 후속 조작 요청도 확인 대기 상태에서 `retry`로 저장될 수 있는 문제를 확인했다.
  - `pending_context_link_for_route()`를 추가해 `retry`는 날씨, 웹 검색, URL, 문서 분석처럼 실제 재시도 성격의 intent에만 저장하도록 했다.
  - Discord 메시지 처리 경로와 로컬 CLI 경로가 같은 helper를 사용해, 채팅 위치가 바뀐 경우에도 승인 후 원래 intent와 resolved slots를 그대로 실행하도록 맞췄다.
  - retryable 문서 후보에 대해 `문서 7 삭제해줘`가 들어오면 바로 실행하지 않고 확인 질문으로 멈추되, pending `context_link`는 `continue`로 저장하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_bot_helpers.py tests/test_cli.py`와 `python3 -m ruff check assistant_bot/bot.py assistant_bot/cli.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-06 - 새 대상 요청의 이전 맥락 오연결 방지

- 작업 이름: 대상 슬롯 불일치 기반 context link 제거
- 진행상황: 완료
- 진행내용:
  - 라우터 모델이 다른 위치의 이전 작업 상태를 잘못 붙인 채 새 지역이나 새 검색어 요청을 반환하면, 실행 전 검증이 먼저 다른 위치 확인 질문으로 바꿀 수 있는 빈틈을 확인했다.
  - `validate_route_context_link()`가 다른 위치 확인으로 전환하기 전에 resolved slot과 연결 상태의 대상 슬롯을 비교하도록 순서를 조정했다.
  - 기존 ID 계열 슬롯뿐 아니라 `location`, `query`, `url` 같은 텍스트 대상 슬롯도 비교해 서로 다르면 링크를 제거하도록 했다.
  - `서울 날씨 어때`가 다른 위치의 `원주 날씨 조회` 재시도 상태에 묶이지 않고 새 요청으로 처리되는 테스트를 추가했다.
  - `OpenAI 최신 모델 검색해줘`가 다른 위치의 `파이썬 비동기 검색` 상태에 묶이지 않고 새 요청으로 처리되는 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_route_validation.py tests/test_context_routing_matrix.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - pending 승인과 유틸리티 새 요청 분리

- 작업 이름: 긍정어가 섞인 시간/상태/도움말 요청의 승인 오인 방지
- 진행상황: 완료
- 진행내용:
  - pending context 확인 질문 뒤에 사용자가 `응 확인 지금 몇시야`, `응 확인 상태 알려줘`처럼 긍정어와 새 유틸리티 요청을 함께 보낼 수 있는 상황을 점검했다.
  - 공통 pending 승인 판정의 새 요청 marker에 `몇시`, `시간`, `시각`, `상태`, `도움말`, `할 수 있...` 계열 표현을 추가했다.
  - 이런 문장이 오래된 pending 승인을 소비하지 않고 새 요청으로 다시 라우팅될 수 있도록 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_route_validation.py tests/test_cli.py tests/test_bot_helpers.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - pending 승인과 범용 새 요청 동사 분리

- 작업 이름: 목록/조회/정리/분석 요청의 승인 오인 방지
- 진행상황: 완료
- 진행내용:
  - 새 에이전트가 추가될수록 `목록 보여줘`, `정리해줘`, `분석해줘` 같은 범용 요청 동사가 오래된 pending 확인 답변과 섞일 수 있는 위험을 점검했다.
  - 공통 pending 승인 판정의 새 요청 marker에 `목록`, `리스트`, `보여줘`, `알려줘`, `정리`, `요약해`, `분석`을 추가했다.
  - `응 확인 목록 보여줘`, `응 확인 다시 정리해줘`, `응 확인 이거 분석해줘`가 pending 승인을 소비하지 않는 회귀 테스트를 추가했다.
  - 동시에 `응 처리해줘` 같은 순수 승인 문구는 계속 승인으로 처리되는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - fallback 라우터의 pending 승인 기준 공통화

- 작업 이름: 모델 실패 경로와 실행 전 검증의 승인 판정 일치
- 진행상황: 완료
- 진행내용:
  - `route_validation`에는 새 요청 marker가 계속 보강되고 있지만, fallback 라우터의 긍정 확인 판정은 별도 함수로 유지되어 기준이 갈라질 수 있는 문제를 확인했다.
  - Router Agent fallback의 `is_positive_context_confirmation()`이 `route_validation.is_context_link_approval_text()`를 사용하도록 변경했다.
  - 모델 호출 실패 상황에서도 `응 확인 목록 보여줘`가 pending context 승인으로 소비되지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - artifact 기반 대상 슬롯 검증 보강

- 작업 이름: slots가 비어 있는 URL/날씨 상태의 새 요청 오연결 방지
- 진행상황: 완료
- 진행내용:
  - 실행 전 대상 슬롯 비교가 `linked_state.slots`만 보고 있어, 이전 URL이나 날씨 대상이 `artifacts`에만 남은 경우 새 요청과의 불일치를 잡지 못할 수 있는 문제를 확인했다.
  - `location`, `query`, `url` 같은 텍스트 대상 비교가 `slots`와 `artifacts` 값을 모두 수집해 비교하도록 변경했다.
  - 명시 URL이 포함된 문장은 `이거` 같은 대명사가 함께 있어도 새 대상 신호로 우선하도록 했다.
  - 이전 URL artifact가 있는 상태에서 새 URL 요약 요청이 들어오면 링크를 제거하는 회귀 테스트를 추가했다.
  - 날씨 대상이 artifact에만 있는 상태에서도 새 지역 날씨 요청이 이전 상태에 묶이지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_route_validation.py tests/test_context_routing_matrix.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - URL 대상 정규화 보강

- 작업 이름: 같은 URL 표현 차이와 실제 다른 URL 분리
- 진행상황: 완료
- 진행내용:
  - URL 대상 비교가 단순 문자열 비교라 `https://EXAMPLE.com/article/`와 `https://example.com/article` 같은 표현 차이를 다른 대상으로 볼 수 있는 문제를 확인했다.
  - URL 비교 시 스킴과 호스트 대소문자를 정규화하고, 끝 슬래시와 fragment를 제거해 같은 URL 표현 차이를 흡수하도록 했다.
  - query string은 보존해 `?q=old`와 `?q=new`처럼 실제 조건이 다른 URL은 다른 대상으로 유지했다.
  - 등가 URL은 기존 context link를 유지하고, query가 다른 URL은 링크를 제거하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_route_validation.py tests/test_context_routing_matrix.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - pending 취소와 부정어 섞인 새 요청 분리

- 작업 이름: `아니/취소 말고 ...` 요청의 cancel_pending 오인 방지
- 진행상황: 완료
- 진행내용:
  - 긍정 승인 판정은 공통 helper를 쓰지만, 부정/취소 판정과 기본 heuristic 취소 판정은 별도 기준이라 `아니 취소 말고 목록 보여줘` 같은 문장을 pending 취소로 소비할 수 있는 문제를 확인했다.
  - `route_validation.is_context_link_rejection_text()`를 추가해 순수 취소 답변과 새 요청이 섞인 부정 표현을 구분하도록 했다.
  - Router Agent fallback의 부정 확인 판정이 공통 helper를 사용하도록 변경했다.
  - 기본 heuristic의 `cancel_pending` 판정도 부정/취소 prefix와 새 요청 marker가 섞인 경우에는 취소 라우팅을 억제하도록 보강했다.
  - `아니 취소 말고 목록 보여줘`가 pending 취소로 소비되지 않고, `아니 취소해`는 계속 취소로 처리되는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_router_agent.py tests/test_route_validation.py tests/test_router_heuristics.py tests/test_context_routing_matrix.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 일반 pending 확인의 부정어 새 요청 분리

- 작업 이름: 웹검색/삭제 확인에서 새 요청을 취소 답변으로 소비하지 않기
- 진행상황: 완료
- 진행내용:
  - context pending 외에도 웹검색 확인, 전체 기억 삭제 확인 같은 일반 pending 확인이 `is_negative_confirmation()`을 사용하고 있어, `아니 취소 말고 목록 보여줘` 같은 문장을 취소로 소비할 수 있는 문제를 확인했다.
  - `is_negative_confirmation()`이 `route_validation.is_context_link_rejection_text()`를 사용하도록 변경해 공통 새 요청 marker 기준을 따르게 했다.
  - 웹검색 pending이 있는 상태에서 `아니 취소 말고 목록 보여줘`를 보내도 pending 거부로 처리하지 않고 새 요청 라우팅에 맡기는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_bot_helpers.py tests/test_cli.py tests/test_route_validation.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 일반 pending 확인의 긍정어 새 요청 분리

- 작업 이름: 웹검색/삭제 확인에서 새 요청을 승인 답변으로 소비하지 않기
- 진행상황: 완료
- 진행내용:
  - 일반 pending 확인의 `is_positive_confirmation()`도 `응 확인 목록 보여줘`처럼 긍정어와 새 요청 marker가 섞인 문장을 승인으로 볼 수 있는지 점검했다.
  - `is_positive_confirmation()`이 공통 새 요청 marker를 확인하도록 변경해, context pending과 일반 pending의 긍정 승인 기준을 맞췄다.
  - `응`, `네`, `응 전부 삭제해` 같은 순수 승인/삭제 확인은 유지하고, `응 확인 목록 보여줘`, `응 확인 상태 알려줘`는 승인으로 소비하지 않도록 테스트를 추가했다.
  - 전체 기억 삭제 pending이 있는 상태에서 `응 확인 목록 보여줘`를 보내도 삭제를 실행하지 않고 pending을 유지하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_bot_helpers.py tests/test_cli.py tests/test_route_validation.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 비-prefix 취소 표현의 새 요청 분리

- 작업 이름: `메모 취소 말고 ...` 요청의 cancel_pending 오인 방지
- 진행상황: 완료
- 진행내용:
  - 기본 heuristic의 `cancel_pending` 판정이 `아니/취소`로 시작하는 문장만 새 요청 marker와 비교하고 있어, `메모 취소 말고 목록 보여줘`처럼 취소 표현이 문장 중간에 있는 새 요청은 여전히 취소로 라우팅될 수 있는 문제를 확인했다.
  - `should_route_cancel_pending()` helper를 추가해 부정 prefix 문장은 공통 rejection helper를 사용하고, 비-prefix 문장도 `말고/대신`과 새 요청 marker가 함께 있으면 취소 라우팅을 억제하도록 했다.
  - `메모 취소 말고 목록 보여줘`가 `cancel_pending`으로 분류되지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_router_heuristics.py tests/test_router_agent.py tests/test_context_routing_matrix.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 순수 확인 승인 표현 과차단 방지

- 작업 이름: `응 확인해줘` 승인 유지와 새 요청 분리
- 진행상황: 완료
- 진행내용:
  - 공통 새 요청 marker에 `확인`이 포함되어 있어, `응 확인해줘`처럼 자연스러운 승인 표현까지 새 요청으로 오해해 pending 승인을 막을 수 있는 문제를 확인했다.
  - `확인` 단독은 새 요청 marker에서 제외하고, `목록`, `상태`, `날씨`, `검색`, `분석` 같은 실제 대상/작업 marker가 함께 있을 때만 새 요청으로 보도록 조정했다.
  - `응 확인해줘`, `네 진행해줘`는 context pending 승인으로 유지하고, `응 확인 목록 보여줘`, `응 확인 상태 알려줘`는 승인으로 소비하지 않는 회귀 테스트를 추가했다.
  - 일반 pending 확인 helper에서도 `응 확인해줘`는 승인으로 유지되는 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_route_validation.py tests/test_bot_helpers.py tests/test_router_agent.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 일반 pending의 짧은 승인 표현 통일

- 작업 이름: `승인/진행/처리` 단독 답변 승인 처리
- 진행상황: 완료
- 진행내용:
  - context pending은 `승인`, `진행`, `처리` 단독 답변을 승인으로 처리하지만, 일반 pending의 `is_positive_confirmation()`은 같은 표현을 승인으로 보지 않아 경로별 응답 차이가 생길 수 있는 문제를 확인했다.
  - 일반 pending positive helper의 exact marker에 `승인`, `진행`, `처리`를 추가했다.
  - 웹검색 pending 확인에서 사용자가 `승인`이라고 답하면 원래 검색 요청을 실행하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_bot_helpers.py tests/test_cli.py tests/test_route_validation.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 새 요청 라우팅 후 일반 pending 만료

- 작업 이름: 오래된 웹검색/삭제 확인 대기의 짧은 승인 오실행 방지
- 진행상황: 완료
- 진행내용:
  - 웹검색 확인이나 기억 삭제 확인 pending이 열린 상태에서 사용자가 새 요청을 보내면 pending handler는 이를 소비하지 않지만, pending 자체가 남아 다음 턴의 `응`, `승인`을 오래된 확인으로 실행할 수 있는 문제를 확인했다.
  - `PendingMemoryDeletionStore.resolve_open()`을 추가했다.
  - Discord 메시지 경로에 `expire_stale_pending_confirmations()`를 추가해, 라우터가 `context_link=none`인 새 요청으로 확정하면 열린 웹검색 확인과 기억 삭제 확인을 만료하도록 했다.
  - 로컬 CLI에도 같은 `expire_stale_pending_confirmations()` helper를 추가했다.
  - 웹검색 pending이 있는 상태에서 `상태 알려줘`가 새 요청으로 처리되면 기존 웹검색 pending이 만료되는 Bot 회귀 테스트를 추가했다.
  - CLI helper가 웹검색 확인과 기억 삭제 확인을 함께 만료하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_bot_helpers.py tests/test_cli.py tests/test_memory_store.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 새 삭제 확인 생성 시 기존 삭제 pending 대체

- 작업 이름: 기억 삭제 확인 pending 단일화
- 진행상황: 완료
- 진행내용:
  - 웹검색 확인은 새 확인을 만들 때 기존 웹검색 pending을 닫지만, 기억 삭제 확인은 기존 삭제 pending을 그대로 남길 수 있어 `승인`이 어떤 삭제 요청에 적용되는지 혼란이 생길 수 있는 문제를 확인했다.
  - 전체 기억 삭제 확인과 지정 기억 삭제 확인을 만들기 전에 `PendingMemoryDeletionStore.resolve_open()`을 호출하도록 했다.
  - 로컬 CLI의 전체 기억 삭제 확인 생성도 같은 방식으로 기존 삭제 pending을 닫도록 했다.
  - Bot에서 전체 삭제 확인 뒤 지정 삭제 확인을 만들면 열린 삭제 pending이 최신 지정 삭제 1개만 남는 회귀 테스트를 추가했다.
  - CLI에서 기존 삭제 pending이 있는 상태로 새 전체 삭제 확인을 만들면 기존 pending을 대체하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_bot_helpers.py tests/test_cli.py tests/test_memory_store.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 새 context 확인 질문 생성 시 기존 context pending 대체

- 작업 이름: 후속 작업 확인 pending 단일화
- 진행상황: 완료
- 진행내용:
  - 새 `context_link=clarify` 확인 질문이 생성될 때 기존 context pending이 남아, 여러 “이어갈까요?” 후보가 라우터 컨텍스트에 쌓일 수 있는 문제를 확인했다.
  - Discord 메시지 경로에 `expire_existing_pending_context_links()`를 추가해 새 linked-state clarify를 반환하기 전에 기존 context pending을 만료하도록 했다.
  - 로컬 CLI에도 같은 `expire_existing_pending_context_links()` helper를 추가했다.
  - Bot에서 기존 context pending이 있을 때 새 context clarify가 오면 기존 pending이 만료되는 회귀 테스트를 추가했다.
  - CLI helper도 기존 context pending을 만료하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_bot_helpers.py tests/test_cli.py tests/test_context_builder.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - linked 없는 context clarify의 기존 pending 대체

- 작업 이름: 일반 clarify 질문 생성 시 이전 후속 확인 만료
- 진행상황: 완료
- 진행내용:
  - 기존 `expire_existing_pending_context_links()`가 `linked_state_id`가 있는 clarify에서만 기존 context pending을 만료해, 대상이 불명확한 일반 clarify가 뜰 때 이전 linked pending이 남을 수 있는 문제를 확인했다.
  - Discord와 CLI helper가 모든 `context_link=clarify`에서 기존 context pending을 만료하도록 변경했다.
  - Bot에서 linked 없는 clarify가 새로 나오면 기존 context pending이 만료되는 회귀 테스트를 추가했다.
  - CLI helper도 linked 없는 clarify에서 기존 context pending을 만료하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q tests/test_bot_helpers.py tests/test_cli.py tests/test_context_builder.py`와 관련 ruff 검사를 통과했다.

## 2026-06-06 - 응답 작성 컨텍스트 최신화

- 작업 이름: 처리 후 최신 맥락으로 최종 답변 작성
- 진행상황: 완료
- 진행내용:
  - `on_message()`가 라우팅 전 생성한 `conversation_context`를 그대로 `ResponseComposer`에 넘기면, `handle_message()` 중 만료된 context pending이 최종 답변 작성 단계에 남아 있을 수 있는 문제를 확인했다.
  - 메시지 처리 후 `build_router_context()`를 다시 호출해 최종 답변 작성용 `conversation_context`를 최신 상태로 생성하도록 했다.
  - 실제 실행에 사용된 `ExecutionContext`는 기존처럼 `response_execution_context_sink`의 마지막 값을 넘겨, 라우터가 선택한 대상과 답변 작성 대상이 어긋나지 않게 했다.
  - `on_message()` 통합 경로에서 새 요청이 기존 context pending을 만료한 뒤, composer가 만료된 pending 정보를 받지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 부분 제목 매칭과 action-only 후속 요청 분리

- 작업 이름: 이전 작업 자동 연결 과잉 방지
- 진행상황: 완료
- 진행내용:
  - fallback 라우터가 단일 후보에서 `완료/삭제/수정` 같은 action 단어만 보고 이전 작업을 과하게 이어갈 수 있는지 점검했다.
  - 제목, 파일명, artifact title 매칭을 보강해 전체 문자열이 직접 포함되거나 의미 있는 토큰 2개 이상이 일치할 때만 명시 대상 매칭으로 보도록 했다.
  - `완료했어`, `다시해봐`처럼 대상 없이 action만 있는 짧은 후속 요청은 계속 최근 단일 후보로 연결하되, `병원 완료했어`처럼 일부 제목 토큰만 섞인 요청은 자동 연결하지 않도록 했다.
  - `완료했어`, `병원 예약 완료했어`, `병원 완료했어` 라우팅 매트릭스 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py tests/test_router_heuristics.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`와 관련 ruff 검사를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - list_memory 실행 경로의 linked context 반영

- 작업 이름: 목록 intent로 들어온 linked 문서/메모 대상 보존
- 진행상황: 완료
- 진행내용:
  - `recall`, `delete_memory`, `update_memory`, `restore_memory`는 `ExecutionContext`의 linked ID를 사용하지만, `list_memory`는 registry에서 실행 컨텍스트를 받지 않아 라우터가 연결한 문서/메모 대상이 실행 단계에서 사라질 수 있는 문제를 확인했다.
  - `MemoryAgent.list_memories()`가 `execution_context`를 받도록 확장하고, linked memory/document ID가 있으면 일반 목록 대신 `recall_by_ids()`로 정확한 대상 상세 조회를 반환하도록 했다.
  - Agent Registry의 `list_memory` handler도 `context.execution`을 전달하도록 변경했다.
  - registry AST 테스트에 `memory_agent.list_memories`도 context-aware 호출 검증 대상으로 추가했다.
  - `list_memory`로 들어와도 linked 문서 본문을 보여주고 현재 위치 최신 메모로 흐르지 않는 agent 단위/봇 통합 회귀 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - linked 없는 clarify 상태 만료 정리

- 작업 이름: 오래된 대상 불명확 확인 상태의 라우터 후보 오염 방지
- 진행상황: 완료
- 진행내용:
  - 기존 `pending_context_states()`는 `pending_linked_state_id`가 있는 clarify만 다뤄서, linked 대상이 없는 “어느 작업을 말하나요?” 확인 상태가 새 요청 뒤에도 라우터 후보에 남을 수 있는 문제를 확인했다.
  - 승인/거부 처리용 pending과 만료 정리용 clarify 상태를 분리하기 위해 `context_clarification_states()` helper를 추가했다.
  - Discord Bot과 CLI의 새 요청/새 clarify 만료 경로가 linked ID 없는 clarify 상태도 함께 만료하도록 변경했다.
  - linked 없는 clarify는 승인 후보로 선택되지 않지만 만료 대상에는 포함되는 route validation 테스트를 추가했다.
  - Bot/CLI에서 새 요청 또는 새 clarify가 오래된 linked 없는 clarify 상태까지 정리하는 회귀 테스트를 추가했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 응답 작성 컨텍스트의 resolved slots 보존

- 작업 이름: 최종 답변 작성 단계의 실행 대상 보존
- 진행상황: 완료
- 진행내용:
  - `ExecutionContext.for_response()`가 linked state는 포함하지만 `resolved_slots`와 라우팅 근거를 포함하지 않아, 최종 응답 작성 모델이 실제 실행 대상 ID를 간접적으로만 볼 수 있는 문제를 확인했다.
  - 응답 작성용 컨텍스트에 `라우터 복원 슬롯`과 `라우팅 근거`를 포함하도록 변경했다.
  - `그거 보여줘`가 메모 8로 연결된 상황에서, 최근 봇 답변에 메모 9가 있어도 응답 작성 프롬프트에는 메모 8의 resolved slot과 라우팅 근거가 함께 들어가는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py -q`와 관련 ruff 검사를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 응답 컨텍스트 절단 시 실행 대상 우선 보존

- 작업 이름: 긴 맥락으로 인한 resolved slots 손실 방지
- 진행상황: 완료
- 진행내용:
  - `ExecutionContext.for_response()`가 전체 컨텍스트를 마지막에 자르기 때문에, 긴 요약이나 linked state 본문이 앞에 있으면 `resolved_slots`가 잘릴 수 있는 문제를 확인했다.
  - 응답 작성 컨텍스트에서 `라우터 복원 슬롯`과 `라우팅 근거`를 최상단에 배치하고, linked state와 긴 최근 맥락은 그 뒤로 보내도록 변경했다.
  - 긴 요약/최근 맥락/link state가 있어도 `memory_id` 같은 실행 대상 슬롯이 응답 컨텍스트에 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py -q`와 관련 ruff 검사를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - context fallback의 allowed intents 계약 강화

- 작업 이름: 허용되지 않은 intent의 후속 맥락 실행 방지
- 진행상황: 완료
- 진행내용:
  - 모델 실패 fallback과 모델 모호 응답 보정 경로가 일부 후보 생성 함수에서 전역 `DEFAULT_ALLOWED_INTENTS`를 직접 참고해, 실험용 라우터나 부분 카탈로그의 `allowed_intents` 제한을 우회할 수 있는지 점검했다.
  - `context_aware_fallback_route()`가 현재 RouterAgent의 `allowed_intents`를 후보 route 생성, base intent 보존, 다른 위치 확인 route 생성, pending 확인 승인까지 전달하도록 변경했다.
  - 허용되지 않은 pending intent는 `chat`으로만 바꾸고 링크를 유지하지 않도록, linked state와 resolved slots를 함께 제거했다.
  - 문서 분석 intent가 허용되지 않은 상황에서 문서 후보가 있어도 fallback이 `analyze_document`를 되살리지 않는 회귀 테스트를 추가했다.
  - 직전 확인 질문의 pending intent가 허용되지 않은 상황에서 `응`이라고 답해도 원래 작업을 승인하지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py -q`를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - Memory Agent 복수 메모 슬롯 실행 반영

- 작업 이름: `memory_ids` resolved slots 누락 보강
- 진행상황: 완료
- 진행내용:
  - Memory Agent의 linked document helper는 `document_id`와 `document_ids`를 모두 보지만, linked memory helper는 `memory_id`만 보고 `memory_ids`를 누락하는 문제를 확인했다.
  - 라우터가 복수 메모 후보를 `resolved_slots.memory_ids` 또는 linked state `slots.memory_ids`로 넘긴 경우, 실행 단계에서 해당 ID를 놓치고 최신 항목 fallback이나 원문 재파싱으로 흐를 수 있었다.
  - `_linked_memory_ids()`가 `resolved_slots.memory_ids`와 `linked_state.slots.memory_ids`를 모두 읽도록 변경했다.
  - 복수 메모 ID가 연결된 `그거 보여줘` 요청이 두 메모를 모두 상세 조회하는 회귀 테스트를 추가했다.
  - `plan.md`에 단수/복수 ID 슬롯을 모두 전문 에이전트 실행 계약으로 다룬다는 원칙을 추가했다.
  - `python3 -m pytest tests/test_memory_store.py -q`를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - Web URL 후속 맥락 실행 보강

- 작업 이름: linked URL/URLs 실행 대상 복원
- 진행상황: 완료
- 진행내용:
  - `web_url` 실행 경로가 현재 메시지에서 URL을 직접 추출하지 못하면, 라우터가 linked state를 연결해도 `URL 누락`으로 멈출 수 있는 문제를 확인했다.
  - `WebSearchAgent.read_urls()`가 현재 메시지에 URL이 없을 때 `resolved_slots.url`, `resolved_slots.urls`, linked state slots, URL artifacts에서 URL을 복원하도록 변경했다.
  - `web_url` 성공 결과의 slots에 `url` 단수와 `urls` 복수를 함께 남겨 다음 턴 라우터와 검증 계층이 같은 대상을 더 안정적으로 볼 수 있게 했다.
  - route validation이 `urls` 복수 슬롯도 URL 대상 슬롯으로 비교하고, artifact의 단수 `url` 값과도 대조하도록 보강했다.
  - `그 링크 다시 요약해줘`가 linked URL을 실제로 읽는 Web URL 회귀 테스트를 추가했다.
  - `resolved_slots.urls`가 linked URL artifact와 다르면 링크를 제거하는 route validation 회귀 테스트를 추가했다.
  - `plan.md`에 URL 기반 후속 요청도 `url`, `urls`, artifacts를 모두 실행 계약으로 다룬다는 원칙을 추가했다.
  - `python3 -m pytest tests/test_web_search_agent.py tests/test_route_validation.py -q`를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 웹검색 무결과/실패 후속 재시도 상태 보존

- 작업 이름: 웹검색 실패 상태의 query 슬롯과 retry action 보강
- 진행상황: 완료
- 진행내용:
  - 웹검색에서 결과가 없거나 Naver API 호출이 실패하면 `facts.queries`만 남고 `subject`, `slots.query`, `available_actions.retry`, `retryable`이 약해, 다음 턴의 `다시 검색해봐`가 이전 검색어에 안정적으로 연결되지 않을 수 있는 문제를 확인했다.
  - 단일 검색 계획에서는 원문 명령어가 아니라 LLM이 만든 대표 검색어를 `subject`와 `slots.query`로 남기도록 변경했다.
  - 무결과(`not_found`)와 실패(`failed`) 결과에도 `slots.query`, `slots.queries`, `available_actions`, `retryable`, `preserve_values`를 채우도록 했다.
  - 무결과 웹검색 결과가 재시도 가능한 작업 상태 단서를 남기는 회귀 테스트를 추가했다.
  - Naver API 실패 결과도 대표 검색어와 retry action을 남기는 회귀 테스트를 보강했다.
  - `plan.md`에 웹검색 무결과/실패도 후속 재시도 대상 상태로 남긴다는 원칙을 추가했다.
  - `python3 -m pytest tests/test_web_search_agent.py tests/test_bot_helpers.py -q`를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 명시 ID 부분 문자열 과연결 방지

- 작업 이름: `메모 10`이 `메모 1` 후보에 연결되는 위험 방지
- 진행상황: 완료
- 진행내용:
  - fallback 라우터의 ID 매칭이 단순 문자열 포함 검사라서, 후보가 `메모 1` 하나뿐일 때 `메모 10 삭제해줘`가 `메모 1`에 잘못 연결될 수 있는 위험을 확인했다.
  - `kind_identifier_matches()`가 ID를 숫자 경계 기준으로 비교하도록 `identifier_text_matches()`를 추가했다.
  - `메모 10 삭제해줘`가 `메모 1` 후보에 연결되지 않고 새 `delete_memory` 요청으로 남는 라우팅 매트릭스 회귀 테스트를 추가했다.
  - `plan.md`에 명시 ID 매칭은 숫자 부분 문자열 포함으로 처리하지 않는다는 원칙을 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py tests/test_router_agent.py -q`를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - Reminder Agent 복수 알림 슬롯 실행 반영

- 작업 이름: `reminder_ids` linked context 상세 조회 보강
- 진행상황: 완료
- 진행내용:
  - 라우터가 `resolved_slots.reminder_ids` 또는 linked state `slots.reminder_ids`로 여러 알림을 넘겨도, `show_latest_reminder()`가 첫 번째 알림만 조회하는 문제를 확인했다.
  - 단일 linked reminder는 기존 상세 응답을 유지하고, 복수 linked reminder는 연결된 알림들을 함께 조회하는 `show_reminders_by_ids()`를 추가했다.
  - linked reminder가 있는 조회형 문장은 일반 알림 목록 fallback보다 실행 컨텍스트를 우선하도록 처리 순서를 보정했다.
  - `방금 알림들 보여줘` 같은 후속 요청에서 복수 linked 알림 ID가 모두 응답과 slots에 남는 회귀 테스트를 추가했다.
  - `plan.md`에 `reminder_ids` 복수 연결 시 첫 번째만 처리하지 않는다는 실행 계약을 추가했다.
  - `python3 -m pytest tests/test_memory_store.py -q`와 관련 ruff 검사를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 실행 전 검증의 호환성 우선순위 보강

- 작업 이름: 다른 위치 확인 전 intent/link 호환성 검증
- 진행상황: 완료
- 진행내용:
  - 실행 전 route validation이 다른 대화 위치 여부를 intent 호환성보다 먼저 확인해, 서로 맞지 않는 작업도 “다른 위치 작업을 여기서 이어갈까요?”라는 질문으로 포장될 수 있는 순서 문제를 확인했다.
  - linked state와 route intent가 먼저 호환되는지 검증한 뒤, 호환되는 작업에 대해서만 다른 위치 확인 질문으로 전환하도록 순서를 조정했다.
  - 다른 위치의 메모 상태에 `그거 완료했어` 같은 할 일 후속 요청이 연결되면 위치 확인 질문이 아니라 호환성 문제로 일반 확인 질문에 머무는 회귀 테스트를 추가했다.
  - `plan.md`에 작업 호환성 검증이 위치 확인보다 먼저라는 순서 규칙을 추가했다.
  - `python3 -m pytest tests/test_route_validation.py -q`와 관련 ruff 검사를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 사용자 문장 action과 linked state action 대조

- 작업 이름: 같은 intent 안의 미지원 action 자동 실행 방지
- 진행상황: 완료
- 진행내용:
  - 실행 전 route validation이 같은 intent/group이면 넓게 통과시켜, linked state가 `show`, `complete`, `delete`만 지원해도 사용자의 `그거 미뤄줘` 같은 미지원 action이 자동 실행될 수 있는 빈틈을 확인했다.
  - 사용자 문장에서 `complete`, `postpone`, `rename`, `update`, `delete`, `restore`, `reopen`, `summarize`, `reanalyze`, `compare`, `open_url`, `show`, `retry` 계열 action을 추출해 linked state의 `available_actions`와 대조하도록 했다.
  - `다시 알려줘`처럼 generic `show`와 더 구체적인 action이 함께 잡히는 표현은 구체 action을 우선하도록 정리했다.
  - `할 일 3에 ...`처럼 사용자가 linked state ID를 직접 명시한 경우에는 대명사 자동 연결이 아니므로 action 대조를 완화해 기존 명시 ID 수정 흐름을 유지했다.
  - 복합 상태가 task/document 같은 artifact를 제공하는 경우에는 해당 대상 종류의 기본 action을 허용해, 오늘 브리핑에 포함된 할 일 완료 같은 기존 후속 흐름은 유지했다.
  - linked task가 미루기를 지원하지 않을 때 `그거 미뤄줘`가 자동 실행되지 않고, 지원하는 `그거 완료했어`는 계속 통과하는 회귀 테스트를 추가했다.
  - `plan.md`에 같은 intent라도 사용자 문장 action과 linked state action을 대조한다는 원칙을 추가했다.
  - `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py -q`와 관련 ruff 검사를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - clarify pending 저장 전 호환성 검증

- 작업 이름: 부정확한 후속 확인 pending 저장 방지
- 진행상황: 완료
- 진행내용:
  - `context_link=clarify` 경로가 사용자/slot 검증은 하지만, 승인 후 실행될 intent/action이 linked state와 호환되는지는 확인하지 않는 문제를 확인했다.
  - 이 상태로 pending을 저장하면 사용자가 다음 턴에 `응`이라고 답했을 때 원래 사용자 문장의 action 정보가 약해진 승인 route가 잘못 실행될 수 있다.
  - clarify route도 승인 후 `continue` 또는 `retry`로 실행될 흐름을 가정해 `route_link_is_compatible()` 검증을 통과해야 pending linked state를 유지하도록 변경했다.
  - 호환되지 않는 intent/action이면 `linked_state_id`와 `resolved_slots`를 제거한 일반 확인 질문으로 바꿔 `pending_linked_state_id`가 저장되지 않게 했다.
  - incompatible linked memory에 task 완료 요청이 들어온 clarify route와, 미루기를 지원하지 않는 linked task에 `그거 미뤄줘`가 들어온 clarify route 회귀 테스트를 추가했다.
  - `plan.md`에 clarify pending도 저장 전 승인 후 실행 가능성을 검증한다는 원칙을 추가했다.
  - `python3 -m pytest tests/test_route_validation.py -q`와 관련 ruff 검사를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - retry 링크의 action 검증 보강

- 작업 이름: retryable 상태의 파괴적 action 오연결 방지
- 진행상황: 완료
- 진행내용:
  - `context_link=retry` 경로가 상태의 `retryable` 또는 `retry` action만 보고 통과해, 라우터가 실수로 `문서 7 삭제해줘`를 `analyze_document + retry`로 반환해도 실행 전 검증이 막지 못할 수 있는 문제를 확인했다.
  - retry 링크에서도 사용자 문장 action을 추출해, `retry`, `reanalyze`, `summarize`, `compare`, `open_url`, `search_related`, `show_alerts`처럼 retryable 결과를 다시 활용하는 비파괴 action만 허용하도록 했다.
  - `delete`, `update`, `complete`, `restore` 같은 별도 실행 intent가 필요한 action이 retry 링크로 들어오면 링크를 제거하거나 확인 질문으로 전환한다.
  - `문서 7 삭제해줘`가 `analyze_document + retry`로 들어온 경우 차단하고, `문서 7 다시 분석해봐`는 retry로 유지하는 회귀 테스트를 추가했다.
  - 기존 문서 요약/비교, 웹 결과 열기 같은 retryable 후속 흐름은 유지되도록 매트릭스 테스트를 함께 확인했다.
  - `plan.md`에 retry 링크도 사용자 action을 검증한다는 원칙을 추가했다.
  - `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py -q`와 관련 ruff 검사를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 채팅 위치 이동 확인 UX 명시화

- 작업 이름: 다른 채팅 위치 작업 이어가기 확인 문구와 회귀 테스트 보강
- 진행상황: 완료
- 진행내용:
  - 같은 사용자가 DM, 서버 채널, 스레드 사이를 이동했을 때 다른 위치의 작업 상태는 장기 맥락 후보로 유지하되, 현재 요청이 맥락상 이어지는 경우에만 확인 질문을 띄우는 정책을 재확인했다.
  - 라우터 프롬프트에 “채팅 위치가 바뀐 경우에도 장기 맥락은 참고하되, 현재 요청이 이전 위치 작업과 확실히 이어질 때만 확인한다”는 규칙을 추가했다.
  - 다른 위치 작업 후보의 `location_note`와 `suggested_question`을 “채팅 위치가 바뀐 것 같아요”처럼 사용자가 이해하기 쉬운 문구로 바꿨다.
  - `여기서 이어서 요약해줘`가 다른 위치의 단일 문서 작업 후보에 걸리면 바로 실행하지 않고 이어갈지 확인하는 라우팅 매트릭스 회귀 테스트를 추가했다.
  - `여기서 이어서 해줘`처럼 실행 동작이 비어 있는 표현은 원래 intent를 복구해 실행하기보다 추가 확인이 필요한 표현으로 다루는 것이 안전하다고 정리했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_route_validation.py -q`를 통과했다.
  - `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - pending 승인 route 보강 후 검증 기준 정렬

- 작업 이름: 승인 답변 대신 원래 사용자 요청으로 후속 작업 검증
- 진행상황: 완료
- 진행내용:
  - pending 확인 승인에서 라우터가 `linked_state_id`를 빠뜨리면 pending slots와 원문은 복구하더라도 linked state 조회가 기존 route 기준으로 남을 수 있는 빈틈을 확인했다.
  - `matching_pending_context_approval_state()`가 순수 승인 답변이고 intent/context_link/slots가 pending state와 충돌하지 않으면, route의 `linked_state_id`가 비어 있어도 최신 pending state를 승인 대상으로 인정하도록 했다.
  - `route_with_pending_context_original_text()`가 pending state의 `pending_linked_state_id`까지 복구하도록 보강했다.
  - Discord 메시지 경로, CLI ask, route preview에서 pending 값으로 route를 보강한 뒤 linked state를 다시 조회하고, 실행 전 검증의 `user_text`는 `응` 같은 승인 답변이 아니라 pending 원래 요청 문장을 쓰도록 맞췄다.
  - 라우터가 승인 route의 `linked_state_id`를 빠뜨려도 `그거 완료했어` 원문과 linked task 상태가 보존되어 dispatch되는 Bot helper 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py tests/test_bot_helpers.py::test_assistant_bot_chat_approval_allows_cross_location_pending_context tests/test_bot_helpers.py::test_assistant_bot_chat_approval_recovers_missing_route_linked_state_id tests/test_bot_helpers.py::test_assistant_bot_chat_approval_with_empty_pending_slots_uses_linked_state -q`를 통과했다.
  - `python3 -m pytest tests/test_cli.py tests/test_context_routing_matrix.py -q`와 `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py -q`를 통과했다.

## 2026-06-06 - 실패한 URL 읽기 후속 맥락 보존

- 작업 이름: URL 직접 읽기 실패 상태의 재시도 대상 단서 보강
- 진행상황: 완료
- 진행내용:
  - URL 직접 읽기가 실패하면 `facts.urls`와 preserve 값은 남지만 `subject`, `slots`, `artifacts`, `available_actions`, `retryable`이 비어 있어 다음 턴의 `다시해봐`가 이전 URL을 안정적으로 재사용하기 어려운 문제를 확인했다.
  - `web_url` 실패 결과에도 `subject`, `slots.url`, `slots.urls`, URL artifact, `available_actions=("retry", "summarize", "search_related")`, `retryable=True`를 남기도록 했다.
  - 공통 작업 상태 추론도 `facts.queries`, `facts.urls` 복수 값을 슬롯과 subject 후보로 읽도록 확장했다.
  - URL 읽기 타임아웃 테스트에 실패 결과의 후속 맥락 단서를 검증하는 assertion을 추가했다.
  - `python3 -m pytest tests/test_web_search_agent.py::test_web_search_agent_times_out_slow_direct_url_page_read tests/test_bot_helpers.py::test_infer_turn_slots_keeps_plural_web_targets_for_context_linking tests/test_bot_helpers.py::test_infer_turn_slots_keeps_plural_id_facts_for_context_linking -q`를 통과했다.
  - `python3 -m ruff check assistant_bot/bot.py assistant_bot/agents/web_search.py tests/test_bot_helpers.py tests/test_web_search_agent.py`를 통과했다.

## 2026-06-06 - 대기질 unsupported 결과의 후속 맥락 보존

- 작업 이름: 미세먼지/대기질 웹검색 도구 누락 시 지역·검색어 단서 보강
- 진행상황: 완료
- 진행내용:
  - 미세먼지/대기질만 요청했는데 Weather Agent에 웹검색 도구가 없으면 `unsupported` 결과가 subject/slots/action 없이 끝나, 사용자가 `그럼 검색으로 해봐`처럼 이어갈 때 이전 지역과 검색 대상을 잃을 수 있는 문제를 확인했다.
  - 웹검색 도구가 없는 대기질 요청도 지역을 해석할 수 있으면 `subject`, `facts.query`, `facts.location`, `slots.query`, `slots.location`, `available_actions=("retry", "check_air_quality")`, `retryable=True`를 남기도록 했다.
  - `서울 미세먼지 어때?`가 unsupported일 때도 `서울특별시 미세먼지 대기질 현재 정보`를 후속 후보 단서로 남기는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_weather_agent.py::test_weather_agent_preserves_air_quality_context_when_web_search_missing tests/test_weather_agent.py::test_weather_agent_delegates_air_quality_to_web_search -q`를 통과했다.
  - `python3 -m ruff check assistant_bot/agents/weather.py tests/test_weather_agent.py`를 통과했다.

## 2026-06-06 - 순수 unsupported 상태 과저장 방지

- 작업 이름: 실행 대상 없는 미지원 기능을 후속 후보에서 제외
- 진행상황: 완료
- 진행내용:
  - 실패/unsupported 상태에 맥락 단서를 남기는 정책이 강화되면서, 음성 통화처럼 코드로 제공되지 않고 실행 대상도 없는 순수 `unsupported` 결과까지 `retryable=True`만으로 후속 후보가 될 수 있는 위험을 점검했다.
  - `should_record_turn_state()`에서 `chat`, `help`, `status`, `current_time`, `reset_context`, `unsupported` 같은 low-value intent는 pending/clarify이거나 artifacts/ID 대상이 있는 경우가 아니면 저장하지 않도록 순서를 보강했다.
  - 순수 unsupported retryable 결과는 저장하지 않고, Weather Agent의 대기질 unsupported처럼 실제 query/location 대상이 있는 도메인 결과는 계속 저장하는 단위 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_should_record_turn_state_skips_retryable_plain_unsupported_result tests/test_bot_helpers.py::test_should_record_turn_state_keeps_targeted_unsupported_domain_result tests/test_bot_helpers.py::test_assistant_bot_skips_low_value_utility_turn_state tests/test_bot_helpers.py::test_assistant_bot_records_actionable_state_with_default_long_ttl -q`를 통과했다.
  - `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-06 - 긴 작업 상태 후보 문자열 압축

- 작업 이름: 라우터 후보 프롬프트의 긴 사용자 입력 오염 방지
- 진행상황: 완료
- 진행내용:
  - subject나 artifact title이 매우 길면 최근 작업 상태 후보 한 줄이 과도하게 커져, 라우터 프롬프트에서 다른 후보와 최근 대화 맥락을 밀어낼 수 있는 위험을 확인했다.
  - `sanitize_turn_state_context_value()`가 delimiter와 필드명 오염을 정리한 뒤, 긴 문자열은 앞뒤 일부를 남기고 `...`로 압축하도록 했다.
  - 구조화 슬롯과 ID는 그대로 유지해, 긴 문서 제목을 압축하더라도 `document_ids` 같은 실행 대상 단서가 사라지지 않게 했다.
  - 긴 문서 제목과 artifact title이 후보에서 압축되면서도 `document_ids` 슬롯과 artifact ID가 파서 결과에 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_turn_state_context_sanitizes_delimiters_inside_state_values tests/test_context_builder.py::test_turn_state_context_compacts_long_user_controlled_values_without_losing_slots -q`를 통과했다.
  - `python3 -m ruff check assistant_bot/context_builder.py tests/test_context_builder.py`를 통과했다.

## 2026-06-06 - 복수 웹 슬롯 기반 후보 종류 판정 보강

- 작업 이름: `queries`/`urls` 슬롯을 웹 후속 후보로 인식
- 진행상황: 완료
- 진행내용:
  - 공통 작업 상태 추론은 `facts.queries`, `facts.urls`를 슬롯으로 남기지만, 라우터 후보 종류 판정은 단수 `query`와 `web_search/web_url` intent 위주라 복수 웹 슬롯만 있는 후보를 웹 후보로 좁히지 못할 수 있는 불일치를 확인했다.
  - `candidate_kind()`가 `query`, `queries`, `url`, `urls` 슬롯을 모두 웹 대상 신호로 보도록 보강했다.
  - query/url 슬롯은 intent보다 강한 대상 신호로 보아, Weather Agent의 대기질 unsupported 결과처럼 `intent=weather`라도 검색 query가 있으면 웹 후속 요청으로 이어질 수 있게 했다.
  - `그거 검색해줘`가 대기질 unsupported 후보의 query를 사용해 `web_search`로 이어지는 라우팅 매트릭스 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_router_agent.py::test_router_candidate_kind_treats_plural_web_slots_as_web_context -q`를 통과했다.
  - `python3 -m ruff check assistant_bot/agents/router.py tests/test_router_agent.py tests/test_context_routing_matrix.py`를 통과했다.

## 2026-06-06 - Web Search Agent 복수 query 슬롯 실행 반영

- 작업 이름: `queries`만 있는 linked 검색 상태 재시도 지원
- 진행상황: 완료
- 진행내용:
  - 라우터 후보와 공통 상태 추론은 `queries` 복수 슬롯을 웹 대상 신호로 다루지만, Web Search Agent의 `linked_search_text()`는 `query` 단수 슬롯만 읽어 `queries`만 남은 상태를 재시도할 때 검색어를 잃을 수 있는 불일치를 확인했다.
  - `linked_search_text()`가 `resolved_slots.queries`와 linked state `slots.queries`의 첫 번째 문자열도 검색어 후보로 읽도록 했다.
  - `다시해봐`가 `slots={"queries": ["OpenAI 최신 뉴스"]}` linked state에서 `OpenAI 최신 뉴스` 검색으로 이어지는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_web_search_agent.py::test_web_search_agent_reads_linked_plural_queries_for_retry tests/test_web_search_agent.py::test_web_search_agent_records_retryable_context_when_no_results -q`를 통과했다.
  - `python3 -m ruff check assistant_bot/agents/web_search.py tests/test_web_search_agent.py`를 통과했다.

## 2026-06-06 - 채팅 위치 변경 후속 작업 확인 정책 강화

- 작업 이름: 다른 위치 작업 상태의 자동 실행 방지
- 진행상황: 완료
- 진행내용:
  - 라우터 프롬프트에 “명시 ID/파일명/지역명처럼 대상이 직접 언급되면 다른 위치 후보도 연결할 수 있다”는 예외 문장이 남아 있어, 모델이 다른 위치 작업을 바로 실행해도 된다고 해석할 여지가 있음을 확인했다.
  - 프롬프트를 “다른 위치 후보를 이어받는 요청이면 대상이 명확하더라도 먼저 확인한다”는 단일 규칙으로 정리했다.
  - deterministic fallback에서도 `candidate_matches_current_message()`로 명시 대상이 잡힌 다른 위치 후보를 바로 `continue`하지 않고 `clarify`로 전환하도록 했다.
  - `할 일 8 완료했어`처럼 다른 채팅 위치의 명시 ID를 현재 위치에서 말한 경우, 대상은 정확히 고르되 실행 전 “채팅 위치가 바뀐 것 같아요…” 확인 질문을 내는 회귀 테스트로 기대값을 수정했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_explicit_cross_location_id_requires_confirmation tests/test_router_agent.py::test_router_model_refinement_keeps_explicit_cross_location_target_for_confirmation tests/test_context_routing_matrix.py -q`를 통과했다.
  - `python3 -m pytest -q`에서 549개 테스트를 통과했다.
  - `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 웹검색 결과 링크 열기 후속 라우팅 보강

- 작업 이름: `그 링크 열어줘`를 검색 재시도가 아닌 URL 직접 읽기로 연결
- 진행상황: 완료
- 진행내용:
  - 최근 웹검색 결과 후보가 `open_url` action과 URL artifact를 갖고 있어도, `그 링크 열어줘`, `사이트 열어줘`, `이링크 열어줘`가 `web_search` retry와 `query` 슬롯으로 남아 실제 링크 본문 읽기보다 검색어 재사용으로 흐를 수 있는 문제를 확인했다.
  - 라우터 fallback에서 웹 후보에 URL artifact가 있고 현재 문장이 URL 열기 요청이면 `web_url` intent로 전환하고, `resolved_slots.url/urls`에 실제 URL을 담도록 했다.
  - `resolved_slots_for_base_intent()`가 `web_url`의 `url`, `urls` 슬롯뿐 아니라 artifact의 `url`도 실행 슬롯으로 복원하도록 했다.
  - 라우팅 매트릭스에서 `그 링크 열어줘`, `사이트 열어줘`, `이링크 열어줘`가 `web_url + continue + urls`로 이어지는 기대값을 고정했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py -q`를 통과했다.

## 2026-06-06 - pending 승인/거부 판정 공통화

- 작업 이름: Discord/CLI/context pending 확인 응답 기준 통합
- 진행상황: 완료
- 진행내용:
  - context pending 승인/거부 판정은 `route_validation.py`에 있었지만, 일반 pending 승인, 웹검색 승인, 기억 삭제 확인, 삭제 범위 변경 판정은 `bot.py`에 남아 있어 경로별 기준이 갈라질 수 있는 구조를 확인했다.
  - `is_positive_confirmation_text()`, `is_negative_confirmation_text()`, `is_web_search_confirmation_approval_text()`, `is_memory_deletion_confirmation_text()`, `is_deletion_confirmation_scope_change_text()`, `asks_to_delete_document_scope_text()`를 `route_validation.py`에 추가했다.
  - `bot.py`는 새 공통 helper를 import alias로 재노출하게 바꿔 기존 Discord/CLI 호출부와 테스트 import를 유지하면서 실제 판단 기준은 한 곳으로 모았다.
  - 공통 helper가 `응 확인 목록 보여줘`, `네이버에서 OpenAI 검색해줘`, `아니메 추천해줘`, `아니 취소 말고 목록 보여줘`, `응 OpenAI 검색해줘`, `파일만 전부 삭제해`를 승인/거부로 오인하지 않는 테스트를 `tests/test_route_validation.py`에 추가했다.
  - `python3 -m pytest tests/test_route_validation.py tests/test_bot_helpers.py tests/test_cli.py -q`를 통과했다.
  - `python3 -m ruff check assistant_bot/route_validation.py assistant_bot/bot.py tests/test_route_validation.py`를 통과했다.

## 2026-06-06 - `OpenAI` 오인식 방지

- 작업 이름: URL 열기 action의 영어 `open` 부분일치 방지
- 진행상황: 완료
- 진행내용:
  - `requests_open_url()`가 `open`을 단순 부분문자열로 찾고 있어, `OpenAI 다시 검색해줘`의 `OpenAI` 안 `open`을 URL 열기 요청으로 오인하는 문제를 확인했다.
  - 한국어 `열어`, `오픈`은 기존처럼 URL 열기 신호로 유지하되, 영어 `open`은 알파벳 단어 경계가 있는 독립 동사일 때만 URL 열기 신호로 보도록 정규식 판정을 적용했다.
  - `OpenAI 다시 검색해줘`는 `web_search` retry로, `그 링크 open해줘`와 `그 링크 열어줘`는 `web_url` 직접 읽기로 갈라지는 동작을 확인했다.
  - 라우팅 매트릭스에 `openai_text_does_not_trigger_open_url_action` 케이스를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`와 `python3 -m ruff check assistant_bot/agents/router.py tests/test_context_routing_matrix.py`를 통과했다.

## 2026-06-06 - `말고/대신` 제외 대상 연결 방지

- 작업 이름: 명시 제목/ID가 포함된 교체 요청을 새 요청으로 유지
- 진행상황: 완료
- 진행내용:
  - 최근 할 일 `병원 예약`이 있는 상태에서 `병원 예약 말고 장보기 할 일 추가해줘`가 기존 `병원 예약` 후보에 `continue`로 연결되는 문제를 확인했다.
  - 기존 거부 신호는 `그거 말고`처럼 대명사가 있는 경우에만 동작했기 때문에, `말고/대신` 앞에 명시 제목이나 ID가 나온 경우를 제외 대상으로 인식하지 못했다.
  - `candidate_is_excluded_by_replacement_text()`를 추가해 `말고`, `대신` 앞부분이 후보 subject/slot/artifact와 맞으면 해당 후보 연결을 막도록 했다.
  - `병원 예약 말고 장보기 할 일 추가해줘`, `메모 8 말고 메모 10 삭제해줘`가 기존 후보에 연결되지 않는 라우팅 매트릭스 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`와 `python3 -m ruff check assistant_bot/agents/router.py tests/test_context_routing_matrix.py`를 통과했다.

## 2026-06-06 - 목록 후보의 단일 artifact 선택 보강

- 작업 이름: 다중 ID 후보에서 제목/ID가 가리키는 단일 대상만 실행 슬롯으로 전달
- 진행상황: 완료
- 진행내용:
  - 할 일 목록 상태가 `task_ids=[3,8]`와 여러 task artifacts를 담고 있을 때, `병원 예약 완료했어`가 `task_ids=[3,8]` 전체를 전달할 수 있는 위험을 확인했다.
  - 알림 목록 상태도 `물 마시기 알림 삭제해줘`처럼 하나의 알림만 가리켜도 `reminder_ids=[5,6]` 전체가 전달될 수 있어 다중 삭제 위험이 있음을 확인했다.
  - `matched_artifact_slots_for_intent()`와 `artifact_matches_current_text()`를 추가해 사용자가 제목/ID/시간으로 단일 artifact를 명확히 가리키면 `task_id`, `reminder_id`, `memory_id`, `document_id` 같은 단수 슬롯으로 좁히도록 했다.
  - 기본 intent가 `chat`이어도 제목만 맞는 것으로 연결하지 않고, 후보가 사용자의 action을 지원할 때만 연결하도록 좁혔다. 예를 들어 알림 후보는 `완료` action을 지원하지 않으므로 `병원 예약 완료했어`에 연결하지 않는다.
  - 사용자가 `알림`처럼 대상 종류를 명시했는데 해당 종류의 후보가 없으면, 다른 종류 후보로 되돌아가지 않고 원래 새 요청을 유지하도록 했다.
  - 라우팅 매트릭스에 `task_list_title_complete_narrows_to_single_task`, `task_list_title_delete_overrides_memory_delete_and_narrows_to_single_task`, `reminder_list_title_delete_narrows_to_single_reminder`, `reminder_list_unsupported_complete_action_does_not_link_by_title_only`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_router_agent.py -q`를 통과했다.

## 2026-06-06 - 시간 표현 기반 단일 artifact 선택 보강

- 작업 이름: 할 일/알림 목록 후속 요청의 시간 단서 보존
- 진행상황: 완료
- 진행내용:
  - 목록 조회 결과가 여러 할 일이나 알림을 담고 있을 때, 사용자가 제목이나 ID가 아니라 `오전 9시`, `오전 7시 4분`처럼 시간으로 대상을 가리키면 단일 항목을 좁히지 못할 수 있는 문제를 확인했다.
  - 공통 작업 상태 artifact 추론이 `task_id`, `reminder_id`와 함께 `due_at`, `remind_at`, `human_due_at`, `human_remind_at` 시간 필드를 보존하도록 했다.
  - Task Agent와 Reminder Agent의 실행 결과 artifact에 사람이 읽는 시간 표현을 함께 담아 라우터가 다음 턴에서 시간 단서를 비교할 수 있게 했다.
  - 라우터의 artifact 매칭 필드를 공통 상수로 정리하고, subject/slot/artifact 명시 매칭 경로와 단일 artifact narrowing 경로가 모두 시간 필드를 보도록 했다.
  - `오전 9시 작업 완료했어`, `오전 7시 4분 알림 삭제해줘`가 각각 `task_id`, `reminder_id` 단수 슬롯으로 이어지는 라우팅 매트릭스 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_infer_turn_artifacts_preserves_task_and_reminder_time_targets tests/test_context_routing_matrix.py::test_context_routing_matrix -q`를 통과했다.

## 2026-06-06 - 지시어+대상 종류 후속 표현 보강

- 작업 이름: `그 메모`, `그 작업`, `그 알림` 같은 자연어 후속 지시 인식
- 진행상황: 완료
- 진행내용:
  - 사용자가 `그 메모 삭제해줘`, `그 작업 완료했어`, `그 알림 삭제해줘`처럼 대상 종류를 함께 말하면, 기존에는 `메모/작업/알림` 종류 marker는 잡히지만 `그 대상`을 이전 상태로 가리키는 후속 지시로 충분히 인정하지 못할 수 있는 문제를 확인했다.
  - Router fallback의 후속 지시 marker에 `그/이/저 + 메모/기억/작업/할 일/알림/리마인드/문서/파일/항목`과 `방금 저장한`, `방금 등록한`, `아까 저장한`, `아까 등록한` 계열 표현을 추가했다.
  - 실행 전 검증 계층의 `FOLLOW_UP_MARKERS`에도 같은 의미권 표현을 추가해, 모델 라우팅과 deterministic fallback, route validation의 후속 판단이 갈라지지 않도록 했다.
  - 라우팅 매트릭스에 `그 메모 삭제해줘`, `그 작업 완료했어`, `그 알림 삭제해줘`가 각각 최근 memory/task/reminder 상태로 이어지는 회귀 테스트를 추가했다.
  - route validation 테스트에 같은 표현이 `linked_state_id` 없는 자동 링크를 안전하게 확인 질문으로 전환하는 케이스를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_route_validation.py::test_validate_route_context_link_clarifies_compact_follow_up_markers_without_state_id -q`를 통과했다.

## 2026-06-06 - 이전 대상을 재료로 새 할 일 생성

- 작업 이름: `그 메모 할 일로 추가해줘`의 intent 보존과 실행 제목 복원
- 진행상황: 완료
- 진행내용:
  - `그 메모 할 일로 추가해줘`가 새 할 일 생성이 아니라 기존 메모 상태의 `remember continue`처럼 연결될 수 있는 문제를 확인했다.
  - Router fallback에 “이전 대상을 재료로 새 할 일을 만드는 요청” 경로를 추가해, 최근 상태의 title/subject를 `resolved_slots.task_title`로 담고 intent는 `manage_task`로 유지하도록 했다.
  - 실행 전 route validation도 이 패턴을 허용해, memory 상태와 task intent가 다르다는 이유만으로 링크를 제거하지 않도록 했다.
  - Task Agent의 직전 메시지 기반 할 일 생성 경로가 `execution_context.resolved_slots.task_title`과 linked state artifact title을 우선 사용하게 해, 실제 저장 제목이 `그 메모`가 아니라 원래 메모 제목이 되도록 했다.
  - 라우팅 매트릭스에 `memory_reference_create_task_uses_memory_as_source_not_memory_update`를 추가했고, Task Agent 실행 테스트에 linked memory 기반 할 일 생성 케이스를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_memory_store.py::test_task_agent_creates_task_from_linked_memory_reference tests/test_router_heuristics.py::test_task_request_helpers -q`를 통과했다.

## 2026-06-06 - 이전 대상을 재료로 새 메모 생성

- 작업 이름: `그 작업 메모로 저장해줘`의 intent 보존과 메모 본문 복원
- 진행상황: 완료
- 진행내용:
  - `그 작업 메모로 저장해줘`가 `그 작업`의 task marker 때문에 `manage_task`로 먼저 분류되고, 이전 할 일 상태를 새 메모 본문으로 쓰지 못하는 문제를 확인했다.
  - 휴리스틱 라우팅에서 `메모로 저장/등록/남겨` 표현은 task marker보다 먼저 `remember`로 분류하도록 했다.
  - Router fallback에 “이전 대상을 재료로 새 메모를 만드는 요청” 경로를 추가해, 최근 상태의 title/subject를 `resolved_slots.memory_text`로 담고 intent는 `remember`로 유지하도록 했다.
  - 참조 기반 생성 요청은 linked state의 일반 action 목록에 없는 작업이어도 후보를 재료로 사용할 수 있도록 candidate action 판정을 보강했다.
  - 라우팅 매트릭스에 `task_reference_create_memory_uses_task_as_source_not_task_update`를 추가했고, 기존 Memory Agent의 `resolved_slots.memory_text` 실행 테스트와 함께 검증했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_memory_store.py::test_memory_agent_remembers_resolved_text_from_linked_state -q`를 통과했다.

## 2026-06-06 - 이전 대상을 재료로 새 알림 생성

- 작업 이름: `그 메모 30분 뒤 알림으로 등록해줘`의 intent 보존과 알림 본문 복원
- 진행상황: 완료
- 진행내용:
  - `그 메모 30분 뒤 알림으로 등록해줘`가 최근 메모 상태를 재료로 쓰지 못하고, `등록` 표현 때문에 알림 목록 조회로 빠질 수 있는 문제를 확인했다.
  - 알림 생성 판정에 `알림으로 등록`, `알림으로 추가` 표현을 추가하고, 시간이 포함된 생성 요청은 알림 목록 조회로 보지 않도록 했다.
  - Router fallback에 “이전 대상을 재료로 새 알림을 만드는 요청” 경로를 추가해, 최근 상태의 title/subject를 `resolved_slots.reminder_text`로 담고 intent는 `manage_reminder`로 유지하도록 했다.
  - 실행 전 route validation도 이 패턴을 허용해, memory/task 상태와 reminder intent가 다르다는 이유만으로 링크를 제거하지 않도록 했다.
  - Reminder Agent가 `resolved_slots.reminder_text`와 linked state artifact title을 실제 알림 본문으로 사용하도록 했다. 시간이 없는 경우에는 최신 알림 조회로 빠지지 않고 알림 시간을 물어보게 했다.
  - 라우팅 매트릭스에 `memory_reference_create_reminder_uses_memory_as_source_with_time`를 추가했고, Reminder Agent 실행 테스트에 linked memory 기반 알림 생성 케이스를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_memory_store.py::test_reminder_agent_creates_reminder_from_linked_memory_reference tests/test_router_heuristics.py::test_heuristic_route_manage_reminder -q`를 통과했다.

## 2026-06-06 - 채팅 위치 변경 후속 확인 정책 보강

- 작업 이름: 다른 위치 작업을 현재 위치에서 이어갈지 묻는 라우팅 기준 고정
- 진행상황: 완료
- 진행내용:
  - 같은 사용자라도 DM, 채널, 스레드처럼 대화 위치가 바뀌면 이전 작업 상태는 바로 실행 가능한 대상이 아니라 확인이 필요한 후보로 취급해야 한다는 요구를 반영했다.
  - 라우터 프롬프트에서 다른 위치 작업은 불명확하면 새 요청으로 처리하고, `다시해봐`, `이어서`, `그거`처럼 명확한 후속 요청일 때만 “여기서 이어서 처리할까요?”라고 묻도록 기준을 더 선명하게 정리했다.
  - 라우팅 매트릭스에 다른 위치의 `원주 날씨 조회` 상태가 있을 때 `여기서 이어서 해줘`는 `weather` 실행 전 `clarify`로 멈추고, 같은 상태에서 `서울 날씨 어때`나 일반 대화는 새 요청으로 유지하는 정책을 회귀 테스트로 고정했다.
  - 같은 흐름에서 `그 메모 알림으로 등록해줘`처럼 이전 대상을 새 알림으로 바꾸는 요청이 시간이 없으면 목록 조회나 즉시 저장으로 빠지지 않고 “언제 알려줄지”를 묻도록 Reminder Agent 분기 순서를 보정했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_memory_store.py::test_reminder_agent_asks_time_for_linked_memory_reference_without_time tests/test_memory_store.py::test_reminder_agent_creates_reminder_from_linked_memory_reference -q`를 통과했다.
  - `python3 -m ruff check assistant_bot/agents/router.py assistant_bot/agents/reminder.py tests/test_context_routing_matrix.py tests/test_memory_store.py`를 통과했다.

## 2026-06-06 - 다른 위치 배경 맥락 문구 정합성 보강

- 작업 이름: 라우터 입력의 교차 위치 정책 문구 충돌 제거
- 진행상황: 완료
- 진행내용:
  - Router Agent 지침은 “다른 위치 작업을 이어가려는지 불명확하면 새 요청으로 처리한다”고 되어 있었지만, `build_cross_location_context()`의 배경 맥락 안내는 “불명확하면 먼저 확인한다”고 되어 있어 모델 입력 안에서 정책이 흔들릴 수 있는 문제를 확인했다.
  - 같은 사용자 다른 위치 최근 맥락 안내를 “명확히 이어가려는 요청일 때만 확인하고, 불명확하거나 새 대상이 있으면 새 요청으로 처리한다”로 수정했다.
  - `plan.md`의 교차 위치 원칙도 같은 기준으로 맞춰, 문서와 라우터 입력이 서로 다른 기준을 주지 않도록 했다.
  - `tests/test_context_builder.py`에 새 문구 기준을 반영했고, `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py::test_context_routing_matrix -q`를 통과했다.

## 2026-06-06 - 후속 표현 부분 문자열 오인식 방지

- 작업 이름: `이어폰` 같은 새 요청을 `이어` 후속 요청으로 오인하지 않도록 라우팅 보정
- 진행상황: 완료
- 진행내용:
  - 최근 작업 상태 후보가 하나 있을 때 `이어폰 추천해줘`가 `이어` 부분 문자열 때문에 이전 할 일에 `continue`로 연결되는 문제를 확인했다.
  - Router fallback의 후속 신호에서 `이어` 단독 marker를 제거하고, `이어서`처럼 실제 후속 요청으로 보기 쉬운 표현만 유지했다.
  - `has_continuation_reference_signal()`도 `이어` 단독을 더 이상 후속 참조로 보지 않도록 좁혔다.
  - 라우팅 매트릭스에 `earphone_recommendation_does_not_link_by_partial_continuation_marker`를 추가해, `이어폰 추천해줘`는 최근 할 일과 무관한 새 `chat` 요청으로 유지하고 `이어서 해줘`는 기존처럼 후속 요청으로 처리되는지 확인했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`와 `python3 -m ruff check assistant_bot/agents/router.py tests/test_context_routing_matrix.py`를 통과했다.

## 2026-06-06 - 웹 일반명사 후속 오인식 방지

- 작업 이름: `사이트 추천`, `웹페이지 디자인`을 이전 웹검색 결과 재시도로 오인하지 않도록 라우팅 보정
- 진행상황: 완료
- 진행내용:
  - 최근 웹검색 결과가 있을 때 `사이트 추천해줘`, `웹페이지 디자인 알려줘`가 `사이트/웹페이지` marker 때문에 이전 검색 결과의 `web_search retry`로 연결되는 문제를 확인했다.
  - `사이트`, `페이지`, `웹페이지`, `검색결과`는 지시어가 없는 일반명사로 볼 수 있으므로 `has_pronoun_follow_up_signal()`과 action fallback의 강한 후속 marker에서 제거했다.
  - 대신 웹 후보에 대해 `사이트 열어줘`, `그 링크 열어줘`처럼 URL 열기 동작이 명확한 요청은 충분한 후속 참조로 인정하도록 `action_match_has_sufficient_reference()`를 보강했다.
  - `이어서`는 실제 후속 요청으로 유지하되 `이어` 단독은 계속 제외해, `이어폰 추천해줘` 같은 새 요청 오인식을 막았다.
  - 라우팅 매트릭스에 `site_recommendation_does_not_retry_previous_web_result`, `webpage_design_request_does_not_retry_previous_web_result`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`와 `python3 -m ruff check assistant_bot/agents/router.py tests/test_context_routing_matrix.py`를 통과했다.

## 2026-06-06 - 검증층 웹 일반명사 후속 오인식 방지

- 작업 이름: route validation의 `사이트/페이지/검색결과` 일반명사 확인 질문 오인 방지
- 진행상황: 완료
- 진행내용:
  - Router fallback은 `사이트 추천해줘`, `웹페이지 디자인 알려줘`를 새 요청으로 유지하도록 보정했지만, 모델이 실수로 linked state 없는 `continue`를 반환하면 route validation이 `사이트/웹페이지/검색결과`를 후속 참조로 보고 “이전 작업을 이어갈까요?” 확인 질문으로 바꿀 수 있음을 확인했다.
  - `route_validation.FOLLOW_UP_MARKERS`에서도 `링크`, `사이트`, `페이지`, `웹페이지`, `검색 결과`, `검색결과` 같은 일반 웹 명사를 제거했다.
  - `그 링크`, `이 링크`, `저 링크`처럼 지시어가 붙은 표현은 그대로 유지해 실제 후속 링크 요청은 계속 확인/검증 대상이 되도록 했다.
  - `has_ambiguous_follow_up_reference()`가 일반 웹 명사를 후속 참조로 보지 않고, `사이트 열어줘`, `그 링크 열어줘`처럼 열기 동작이 명확한 웹 후속 요청은 후속 참조로 보는 규칙을 추가했다.
  - linked state 없는 `continue`가 `사이트 추천해줘`에 들어와도 확인 질문이 아니라 `context_link=none`으로 정리되는 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_ambiguous_follow_up_reference_ignores_plain_web_nouns_without_demonstrative tests/test_route_validation.py::test_validate_route_context_link_clears_missing_state_for_plain_web_new_request tests/test_route_validation.py::test_validate_route_context_link_clarifies_web_follow_up_without_state_id tests/test_context_routing_matrix.py::test_context_routing_matrix -q`와 `python3 -m ruff check assistant_bot/route_validation.py tests/test_route_validation.py assistant_bot/agents/router.py tests/test_context_routing_matrix.py`를 통과했다.

## 2026-06-06 - 최신 항목 자연어 지시어 보강

- 작업 이름: `최근거`, `마지막거` 후속 요청 인식
- 진행상황: 완료
- 진행내용:
  - `방금거 보여줘`는 최근 작업 상태로 연결되지만 `최근거 보여줘`는 새 대화로 빠지는 문제를 확인했다.
  - Router fallback의 `has_follow_up_signal()`, `has_pronoun_follow_up_signal()`, `has_recent_time_reference_signal()`에 `최근거`, `마지막거` 계열 표현을 추가했다.
  - route validation의 `FOLLOW_UP_MARKERS`에도 `최근거`, `최근 거`, `마지막거`, `마지막 거`를 추가해 모델 라우팅과 fallback 라우팅의 실행 전 검증 기준을 맞췄다.
  - 라우팅 매트릭스에 `recent_thing_show_prefers_latest_created_at_candidate`, `last_thing_show_links_single_recent_task_candidate`를 추가했다.
  - route validation compact marker 테스트에도 `최근거 보여줘`, `마지막거 보여줘`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_route_validation.py::test_validate_route_context_link_clarifies_compact_follow_up_markers_without_state_id -q`와 `python3 -m ruff check assistant_bot/agents/router.py assistant_bot/route_validation.py tests/test_context_routing_matrix.py tests/test_route_validation.py`를 통과했다.

## 2026-06-06 - 목록 순서 지시어 맥락 연결 보강

- 작업 이름: `첫번째`, `두번째`, `2번` 같은 목록 기반 후속 요청을 최근 목록 artifact로 연결
- 진행상황: 완료
- 진행내용:
  - 할 일 목록을 보여준 뒤 `두번째 삭제해줘`, `첫번째 완료했어`, `2번 삭제해줘`처럼 말하면 라우터가 목록 순서를 실제 artifact ID로 좁히지 못하고 새 대화나 잘못된 삭제 intent로 빠지는 문제를 확인했다.
  - Router fallback에 순서 지시어 해석을 추가해, 최근 상태의 artifact 순서 기준으로 단일 항목을 찾아 `task_id`, `memory_id`, `document_id`, `reminder_id` 같은 실행 슬롯으로 변환하도록 했다.
  - `할 일 8 삭제해줘`처럼 명시 ID가 있는 요청은 기존처럼 ID 매칭을 우선하고, `2번 삭제해줘`처럼 종류 없이 숫자 순서만 말한 경우에만 목록 순서 참조로 처리하도록 했다.
  - `has_follow_up_signal()`, `has_pronoun_follow_up_signal()`, route validation의 후속 참조 판정에도 같은 순서 표현을 추가해 fallback과 실행 전 검증 기준이 어긋나지 않도록 했다.
  - 라우팅 매트릭스에 `task_list_second_ordinal_delete_selects_second_artifact`, `task_list_first_ordinal_complete_selects_first_artifact`, `task_list_plain_number_ordinal_selects_second_artifact`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 목록 순서 지시어 범위와 위치 변경 경계 검증

- 작업 이름: 순서 기반 후속 요청이 메모/문서/교차 위치에서도 공통 정책대로 동작하는지 고정
- 진행상황: 완료
- 진행내용:
  - `두번째 삭제해줘`, `2번 삭제해줘` 같은 목록 순서 표현이 할 일뿐 아니라 메모 목록과 문서 목록에서도 각각 `memory_id`, `document_id` 단일 슬롯으로 좁혀지는지 확인했다.
  - 같은 사용자라도 채팅 위치가 다른 후보의 목록 항목을 `두번째 삭제해줘`로 가리키면 바로 실행하지 않고 `context_link=clarify`로 멈추며, 실제 대상 슬롯은 `task_id`로 보존되는지 확인했다.
  - 실행 전 route validation에서 `문서 2 삭제해줘`, `메모 2 삭제해줘`처럼 명시 ID가 있는 새 요청은 후속 확인 질문으로 빼앗지 않고, `2번 삭제해줘`, `두번째 삭제해줘`처럼 목록 맥락이 필요한 표현만 확인 대상으로 남는지 재현했다.
  - 라우팅 매트릭스에 `cross_location_task_list_ordinal_requires_confirmation`, `memory_list_second_ordinal_delete_selects_second_artifact`, `document_list_second_ordinal_show_selects_second_artifact`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 확인 질문 이후 짧은 후보 선택 응답 복원

- 작업 이름: `어느 작업?` 확인 뒤 `두번째`, `장보기` 같은 답변을 원래 요청으로 이어받기
- 진행상황: 완료
- 진행내용:
  - 후보가 여러 개라 봇이 “어느 작업을 이어서 처리할까요?”라고 물은 뒤 사용자가 `두번째`, `2번`, `장보기`처럼 짧게 답하면 원래 요청의 action(`삭제해줘`, `완료했어`, `다시해봐`)을 잃고 다시 확인 질문으로 빠지는 문제를 재현했다.
  - 다중 후보 확인 라우팅 결과에 `pending_candidate_state_ids`와 `pending_original_text`를 남겨, 다음 턴에서 사용자의 선택 답변을 후보 state ID와 원래 사용자 문장으로 복원할 수 있게 했다.
  - Router fallback이 pending 후보 선택 상태를 먼저 확인하고, 순서 표현이나 후보 subject/artifact 제목이 단일 후보와 맞으면 원래 문장 기준으로 실행 라우트를 재구성하도록 했다.
  - 새 요청이 명확한 `서울 날씨 어때` 같은 메시지는 pending 후보 선택으로 흡수하지 않고 기존 새 요청 intent를 유지하도록 했다.
  - 실행 전 route validation은 `pending_candidate_state_ids`, `pending_original_text`만 제한적으로 보존하고, 확인 대상 없는 임의 실행 슬롯은 계속 제거하도록 안전장치를 추가했다.
  - Discord 봇과 CLI의 clarify 상태 저장 경로가 `route.resolved_slots`의 안전한 pending 선택 슬롯을 함께 저장하도록 맞췄다.
  - 라우팅 매트릭스에 `pending_candidate_second_selection_restores_original_task_delete`, `pending_candidate_title_selection_restores_original_task_delete`, `pending_candidate_new_weather_request_does_not_select_candidate`를 추가했다.
  - route validation과 봇 helper 테스트에 pending 후보 선택 슬롯 보존 케이스를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_bot_helpers.py::test_assistant_bot_stops_before_dispatch_when_route_needs_context_clarification -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 다른 위치 후보 선택 복원의 안전 경계 검증

- 작업 이름: 다른 위치 다중 후보 확인 뒤 선택 답변이 위치 변경 확인을 우회하지 않도록 고정
- 진행상황: 완료
- 진행내용:
  - 여러 다른 위치 후보 때문에 “어느 작업을 이어서 처리할까요?”라고 물은 뒤 사용자가 `원주`, `첫번째`, `두번째`, `OpenAI 모델`처럼 답할 때 현재 라우팅 결과를 재현했다.
  - pending 후보 선택 복원이 원래 요청(`다시해봐`)을 되살리더라도, 선택된 후보가 다른 위치의 작업이면 바로 실행하지 않고 `context_link=clarify`로 위치 변경 확인을 유지하는지 확인했다.
  - `서울 날씨 어때`처럼 새 요청이 명확한 경우에는 pending 후보 선택으로 흡수하지 않고 새 weather 요청으로 유지되는 기존 경계도 함께 확인했다.
  - 라우팅 매트릭스에 `pending_cross_location_candidate_title_selection_still_requires_confirmation`, `pending_cross_location_candidate_ordinal_selection_still_requires_confirmation`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 후보 선택 후 재확인 승인 원문 보존

- 작업 이름: `원주` 같은 후보 선택 답변이 승인 후 실행 원문을 덮어쓰지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 다른 위치 후보 선택 복원 뒤 다시 “여기서 이어서 처리할까요?” 확인이 생기는 경우, pending 저장 로직이 `route.resolved_slots.pending_original_text`의 원래 요청(`다시해봐`)을 현재 답변(`원주`)으로 덮어쓸 수 있음을 확인했다.
  - Discord 봇과 CLI의 clarify 상태 저장 경로에서 `agent_text_for_route()`를 사용해 복원된 원래 요청 문장을 `pending_original_text`로 저장하도록 수정했다.
  - `pending_resolved_slots`에는 실제 실행 슬롯만 남도록 `pending_original_text`, `pending_candidate_state_ids` 같은 임시 선택 슬롯을 제거하는 `pending_execution_slots()`를 추가했다.
  - 완료된 작업 상태에 pending 후보 선택 슬롯이 장기 저장되지 않도록 `pending_candidate_state_ids`를 pending 전용 슬롯 정리 목록에 포함했다.
  - 봇 helper 테스트에 `test_assistant_bot_preserves_restored_original_text_when_selected_cross_location_candidate`, `test_sanitized_turn_state_slots_removes_pending_candidate_selection_slots_after_success`를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_preserves_restored_original_text_when_selected_cross_location_candidate tests/test_bot_helpers.py::test_sanitized_turn_state_slots_removes_pending_candidate_selection_slots_after_success -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 후보 선택 정정 표현 처리 보강

- 작업 이름: `첫번째 말고 두번째`, `병원 예약 말고 장보기` 같은 정정형 선택 해석
- 진행상황: 완료
- 진행내용:
  - 후속 후보 확인 뒤 사용자가 `아니 두번째`, `그거 말고 두번째`처럼 답하면 이미 후보 선택으로 복원되지만, `병원 예약 말고 장보기`는 새 대화로 빠지고 `첫번째 말고 두번째`는 앞의 `첫번째`를 먼저 선택할 수 있는 문제를 재현했다.
  - pending 후보 선택 해석에서 `말고`, `대신` 뒤쪽 표현을 실제 선택 대상으로 우선 사용하도록 `pending_candidate_selection_text()`를 추가했다.
  - 순서 표현과 제목 선택 모두 정정 뒤쪽 대상만 기준으로 보게 해, 앞에서 부정한 후보가 잘못 선택되지 않도록 했다.
  - `아니 취소`, `취소` 같은 명확한 취소 표현은 기존처럼 `cancel_pending`으로 남는지 확인했다.
  - 라우팅 매트릭스에 `pending_candidate_ordinal_correction_selects_replacement_candidate`, `pending_candidate_title_correction_selects_replacement_candidate`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 후보 선택 부정 표현 잔여 후보 처리

- 작업 이름: `첫번째 말고`, `병원 예약 말고`처럼 대체 대상을 생략한 부정형 선택 해석
- 진행상황: 완료
- 진행내용:
  - 후속 후보 확인 뒤 사용자가 `첫번째 말고`, `병원 예약 말고`처럼 부정할 후보만 말하면, 기존 로직이 문장 전체에서 앞쪽 후보를 다시 찾아 부정한 대상을 그대로 실행할 수 있는 문제를 재현했다.
  - pending 후보 선택 해석을 `선택 대상`과 `제외 대상`으로 나누어, `말고`, `대신` 뒤쪽에 대체 대상이 있으면 기존처럼 뒤쪽을 선택하고, 뒤쪽이 비어 있으면 앞쪽 후보를 제외하도록 수정했다.
  - 제외 후 남은 후보가 정확히 하나일 때만 그 후보를 선택하게 해, 후보가 여러 개 남는 상황에서는 무리하게 실행하지 않도록 했다.
  - 라우팅 매트릭스에 `pending_candidate_ordinal_exclusion_selects_only_remaining_candidate`, `pending_candidate_title_exclusion_selects_only_remaining_candidate`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_router_heuristics.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - pending 확인 자연 승인 표현 보강

- 작업 이름: `응 계속`, `네 해줘`, `좋아 이어서 해줘` 같은 자연스러운 승인 답변 인식
- 진행상황: 완료
- 진행내용:
  - 채팅 위치 변경 확인이나 후속 작업 확인 뒤 사용자가 `응 계속`, `네 해줘`처럼 짧게 승인하면 기존 승인 판정이 너무 좁아 pending 작업을 이어받지 못하는 문제를 재현했다.
  - `is_context_link_approval_text()`의 승인 액션에 `계속`, `해줘`, `이어줘`, `이어서`를 추가해 자연스러운 승인 표현을 더 잘 받아들이도록 했다.
  - 동시에 `응 서울 날씨 확인해줘`, `응 OpenAI 검색해줘`, `응 확인 목록 보여줘`처럼 새 요청 마커가 있는 문장은 기존처럼 pending 승인으로 흡수하지 않도록 유지했다.
  - 라우팅 매트릭스에 `natural_continue_approval_restores_pending_context`를 추가했고, route validation 테스트에 자연 승인 표현을 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - pending 확인 자연 거절 표현 보강

- 작업 이름: `됐어`, `괜찮아`, `안 해도 돼` 같은 자연스러운 거절 답변 인식
- 진행상황: 완료
- 진행내용:
  - 후속 작업 확인 질문 뒤 사용자가 `됐어`, `괜찮아`, `안 해도 돼`처럼 자연스럽게 거절하면 기존 판정이 pending 취소로 인식하지 못하는 문제를 재현했다.
  - `is_context_link_rejection_text()`에 `됐어`, `괜찮아`, `필요없어`, `안 해도 돼` 계열 표현을 추가해 pending 확인 상태를 취소할 수 있도록 했다.
  - `됐어 서울 날씨 알려줘`처럼 거절 표현 뒤에 새 요청이 붙은 경우에는 기존처럼 pending 취소로 흡수하지 않고 새 요청으로 라우팅되도록 유지했다.
  - 라우팅 매트릭스에 `natural_rejection_cancels_pending_context`, `natural_rejection_with_new_weather_request_not_pending_cancel`을 추가했고, route validation 테스트에 자연 거절 표현을 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 이전 작업 지시 표현 보강

- 작업 이름: `전에 하던거`, `지난번 거`, `저번것` 같은 이전 작업 참조 표현 인식
- 진행상황: 완료
- 진행내용:
  - 사용자가 `전에 하던거 보여줘`처럼 말하면 최근 작업 상태 후보를 가리키는 표현이지만, 기존 라우터는 `전에 하던거`를 후속 지시로 보지 못해 일반 조회 쪽으로 빠지는 문제를 재현했다.
  - `이전` 단어 전체는 `이전 버전 알려줘` 같은 새 대화까지 과연결할 수 있으므로 추가하지 않고, `전에하던`, `전에했던`, `이전에하던`, `이전에했던`, `지난번거/것`, `저번거/것`처럼 대상 지시가 분명한 compact 표현만 후속 신호로 추가했다.
  - route validation의 후속 marker에도 같은 표현을 추가해, 모델이 linked state 없이 자동 실행 가능한 `continue`를 반환하면 확인 질문으로 멈추도록 안전망을 맞췄다.
  - 라우팅 매트릭스에 `previous_work_reference_show_links_current_task_candidate`, `previous_version_phrase_does_not_link_by_plain_previous_word`를 추가했고, route validation compact marker 테스트에 이전 작업 참조 표현을 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 날씨 위치 대명사 후속 맥락 보강

- 작업 이름: `거기 내일 날씨`, `그 지역 비 와?` 같은 이전 날씨 지역 참조 처리
- 진행상황: 완료
- 진행내용:
  - 사용자가 `원주 날씨`를 물은 뒤 `거기 내일 날씨 어때`처럼 이어가면, 기존 라우터는 weather intent는 잡지만 `거기`를 후속 위치 참조로 보지 못해 이전 `location` 슬롯을 연결하지 않는 문제를 재현했다.
  - `거기`, `거긴`, `그지역`, `그동네`, `그곳`이 `날씨`, `예보`, `비`, `눈`, `우산`, `기온`, `미세먼지` 같은 날씨 marker와 함께 있을 때만 이전 날씨 후보의 location을 사용하도록 보강했다.
  - weather intent의 `resolved_slots_for_base_intent()`에 `location` 슬롯을 포함해, 연결된 이전 지역이 전문 에이전트로 안정적으로 전달되도록 했다.
  - `거기 맛집 추천해줘`처럼 위치 대명사는 있지만 날씨 요청이 아닌 문장은 이전 날씨 상태에 빨려 들어가지 않도록 경계 테스트를 추가했다.
  - route validation에도 같은 위치 대명사+날씨 marker 판정을 추가해, 모델이 linked state 없이 자동 실행 링크를 반환하면 확인 질문으로 멈추도록 맞췄다.
  - 라우팅 매트릭스에 `weather_location_pronoun_uses_previous_location`, `location_pronoun_restaurant_request_does_not_continue_weather`를 추가했고, route validation compact marker 테스트에 날씨 위치 대명사 표현을 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 날씨 위치 대명사 축약 질문 보강

- 작업 이름: `거긴 어때?` 같은 짧은 위치 후속 질문을 이전 날씨 맥락으로 연결
- 진행상황: 완료
- 진행내용:
  - 이전에 `원주 날씨`를 물은 뒤 `거긴 어때?`처럼 짧게 이어 물으면, 명시적인 `날씨`, `비`, `기온` marker가 없어 라우터가 일반 대화로 처리하는 문제를 재현했다.
  - 명시적 날씨 marker가 있는 위치 대명사 표현과 별도로, `거기/거긴/그지역` 같은 위치 대명사와 `어때/어떠/괜찮/좋아`가 결합된 짧은 질문을 날씨 후속 질문으로 인식하는 보조 판정을 추가했다.
  - `맛집`, `식당`, `카페`, `추천`, `여행`, `숙소`, `교통`, `가격` 같은 비날씨 주제 marker가 있으면 짧은 질문 판정에서 제외해, 새 주제를 이전 날씨 상태에 잘못 연결하지 않도록 했다.
  - 기본 라우팅이 `chat`으로 잡힌 경우에도 최근 후보가 날씨이고 짧은 위치 후속 질문이면 `weather` intent로 승격해 이전 `location` 슬롯을 전달하도록 했다.
  - route validation에도 같은 판정을 추가해, 모델이 `거긴 어때?`를 linked state 없이 자동 실행하려 할 때 확인 질문으로 안전하게 멈출 수 있도록 맞췄다.
  - 라우팅 매트릭스에 `weather_location_pronoun_brief_question_uses_previous_location`, `location_pronoun_restaurant_question_does_not_continue_weather`를 추가했고, route validation compact marker 테스트에 `거긴 어때?`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`, `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clarifies_compact_follow_up_markers_without_state_id -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 날씨 위치 축약 질문 과연결 방지

- 작업 이름: `거긴 분위기 어때?` 같은 장소 평가 질문이 이전 날씨 맥락으로 빨려 들어가지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `원주 날씨` 뒤에 `거긴 분위기 어때?`라고 물으면, 짧은 위치 대명사 질문 보조 판정이 이를 날씨 후속 질문으로 잘못 연결하는 문제를 재현했다.
  - `분위기`, `장소`, `시설`, `메뉴`, `음식`, `서비스`, `좌석`, `영업`, `술집`, `뷰`, `소음` 등 장소 평가나 추천에 가까운 marker를 짧은 날씨 후속 판정의 제외 목록에 추가했다.
  - 같은 사용자 현재 위치의 `거긴 어때?`는 이전 날씨 지역으로 계속 연결되고, 다른 채팅 위치의 `거긴 어때?`는 바로 실행하지 않고 확인 질문으로 멈추는지 함께 고정했다.
  - route validation에도 같은 제외 marker를 추가해, 모델이 `거긴 분위기 어때?`를 linked state 없이 후속 실행으로 반환해도 자동 실행이나 확인 질문으로 과연결되지 않도록 맞췄다.
  - 라우팅 매트릭스에 `cross_location_weather_location_brief_question_requires_confirmation`, `location_pronoun_vibe_question_does_not_continue_weather`를 추가했고, route validation 반례 테스트에 `거긴 분위기 어때?`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`, `python3 -m pytest tests/test_route_validation.py::test_ambiguous_follow_up_reference_ignores_plain_web_nouns_without_demonstrative tests/test_route_validation.py::test_validate_route_context_link_clarifies_compact_follow_up_markers_without_state_id -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 최근 대화 소스 생성 요청 과연결 방지

- 작업 이름: `방금 생각난 거`, `방금 말한 거`를 기존 저장 항목이 아니라 새 대화 소스로 취급
- 진행상황: 완료
- 진행내용:
  - `방금 생각난 거 메모해줘`가 기존 메모 ID에 연결되고, `아까 생각난 거 할 일로 추가해줘`가 기존 할 일 제목을 새 할 일 제목으로 재사용하는 문제를 재현했다.
  - `방금 말한`, `아까 말한`, `방금 생각난`, `아까 생각난`, `위 내용`처럼 최근 대화나 새 생각을 소스로 삼는 생성 요청은 저장된 memory/task/reminder 후보가 현재 요청을 덮어쓰지 못하도록 라우터 후보 선택을 차단했다.
  - `방금 저장한`, `방금 추가한`, `아까 등록한`처럼 실제 저장 항목을 가리키는 표현은 기존처럼 최근 항목 조회·수정·삭제로 연결되도록 제외했다.
  - route validation에도 같은 판정을 추가해, 모델이 `방금 말한 거 메모해줘`에 기존 메모 ID를 붙여 반환해도 자동 실행이나 확인 질문이 아니라 링크 제거로 처리되도록 했다.
  - 라우팅 매트릭스에 `recent_thought_memory_request_does_not_link_previous_memory`, `recent_said_memory_request_does_not_link_previous_memory`, `recent_thought_task_request_does_not_use_previous_task_title`을 추가했고, route validation에 `test_validate_route_context_link_clears_recent_conversation_source_creation_link`를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_route_validation.py::test_validate_route_context_link_clears_recent_conversation_source_creation_link tests/test_route_validation.py::test_ambiguous_follow_up_reference_ignores_plain_web_nouns_without_demonstrative -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 최근 발화 메모·할 일 생성 실행 경로 보강

- 작업 이름: `방금 말한 거 메모해줘`, `위 내용 할 일로 만들어줘`가 실제 직전 사용자 발화를 소스로 쓰도록 고정
- 진행상황: 완료
- 진행내용:
  - 라우터가 기존 저장 항목 과연결을 막아도, 실행 단계에서 `방금 말한 거 메모해줘`가 직전 발화가 아니라 현재 명령문 자체를 저장할 수 있는 문제를 통합 테스트로 재현했다.
  - `asks_to_remember_recent_message()`가 `기억`, `저장`만 보고 `메모` 표현을 놓치고 있어, `방금 말한 거 메모해줘`가 직전 발화 참조가 아니라 일반 메모 본문 분류로 빠지는 원인을 확인했다.
  - 최근 발화 기억 요청 marker에 `메모`를 추가해 `방금 말한 거 메모해줘`도 직전 사용자 메시지를 저장하도록 수정했다.
  - 디스코드 핸들러 수준 통합 테스트에 `test_assistant_bot_remembers_previous_user_message_from_recent_reference`, `test_assistant_bot_creates_task_from_previous_user_message`를 추가해, 실제 `handle_message()` 경로에서 이전 사용자 메시지가 메모/할 일 소스로 쓰이는지 검증했다.
  - 테스트는 fake embedding/OpenAI로 구성해 네트워크 호출 없이 실행되도록 정리했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_remembers_previous_user_message_from_recent_reference tests/test_bot_helpers.py::test_assistant_bot_creates_task_from_previous_user_message tests/test_router_heuristics.py::test_substantive_memory_text_ignores_file_only_instruction -q`, `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_route_validation.py::test_validate_route_context_link_clears_recent_conversation_source_creation_link -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 본문 없는 최근 생각 메모 요청 방어

- 작업 이름: `방금 생각난 거 메모해줘` 같은 표현을 현재 명령문 그대로 저장하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `방금 생각난 거 메모해줘`, `아까 생각난 거 메모해줘`가 저장할 실제 본문이 없는데도 `has_substantive_memory_text()`에서 본문 있음으로 판정되는 문제를 재현했다.
  - 이 상태에서는 모델 분류 fallback이 잘못 판단하거나 테스트 fake 응답이 본문을 반환할 경우, 현재 명령문 자체가 메모로 저장될 수 있음을 확인했다.
  - `방금/아까/지금/직전` + `생각난/떠오른/떠올린` + `메모/기억/저장` 조합을 본문 없는 최근 생각 메모 요청으로 분류하는 `asks_to_remember_unspecified_recent_thought()`를 추가했다.
  - 메모 에이전트가 해당 표현을 모델 분류 전에 `needs_input`으로 처리해 저장할 실제 내용을 다시 물어보도록 했다.
  - 디스코드 핸들러 통합 테스트에 `test_assistant_bot_does_not_save_unspecified_recent_thought_as_memory`를 추가해 실제 `handle_message()` 경로에서도 저장되지 않도록 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_remembers_previous_user_message_from_recent_reference tests/test_bot_helpers.py::test_assistant_bot_does_not_save_unspecified_recent_thought_as_memory tests/test_bot_helpers.py::test_assistant_bot_creates_task_from_previous_user_message tests/test_memory_store.py::test_memory_agent_does_not_save_recent_thought_without_content tests/test_router_heuristics.py::test_substantive_memory_text_ignores_file_only_instruction -q`, `python3 -m pytest tests/test_memory_store.py tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_route_validation.py::test_validate_route_context_link_clears_recent_conversation_source_creation_link -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 본문 없는 최근 생각 할 일 요청 방어

- 작업 이름: `방금 생각난 거 할 일로 추가해줘`를 현재 명령문 그대로 할 일 제목으로 저장하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `방금 생각난 거 할 일로 추가해줘`, `아까 생각난 거 할 일로 추가해줘`가 최근 발화 참조가 아니라 일반 할 일 생성으로 빠져, 현재 명령문 전체가 할 일 제목이 될 수 있는 문제를 재현했다.
  - 기존 `asks_to_remember_unspecified_recent_thought()` 판정을 메모뿐 아니라 `할 일`, `작업`, `태스크`, `알림`, `리마인드`, `추가`, `등록` 계열 생성 요청까지 포함하도록 확장했다.
  - `방금 추가한 할 일`처럼 실제 최근 저장 항목을 가리키는 표현은 계속 최근 항목 참조로 동작하도록 유지하면서, `방금 생각난 거 할 일로 추가해줘`는 `asks_to_reference_latest_added_task()`에서 제외했다.
  - 할 일 에이전트가 일반 제목 추출 전에 본문 없는 최근 생각 생성 요청을 감지해 `needs_input`으로 처리하고, 추가할 할 일 제목을 다시 묻도록 했다.
  - 단위 테스트에 `test_task_agent_does_not_create_task_from_unspecified_recent_thought`, 디스코드 핸들러 통합 테스트에 `test_assistant_bot_does_not_create_task_from_unspecified_recent_thought`를 추가했다.
  - `python3 -m pytest tests/test_router_heuristics.py::test_task_request_helpers tests/test_memory_store.py::test_task_agent_does_not_create_task_from_unspecified_recent_thought tests/test_bot_helpers.py::test_assistant_bot_does_not_create_task_from_unspecified_recent_thought -q`, `python3 -m pytest tests/test_memory_store.py tests/test_bot_helpers.py::test_assistant_bot_does_not_create_task_from_unspecified_recent_thought tests/test_bot_helpers.py::test_assistant_bot_creates_task_from_previous_user_message tests/test_bot_helpers.py::test_assistant_bot_does_not_save_unspecified_recent_thought_as_memory tests/test_router_heuristics.py::test_task_request_helpers tests/test_router_heuristics.py::test_substantive_memory_text_ignores_file_only_instruction -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 본문 없는 최근 생각 알림 요청 방어

- 작업 이름: `방금 생각난 거 10분 뒤 알려줘`를 알림 본문으로 등록하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `방금 생각난 거 10분 뒤 알려줘`, `아까 생각난 거 내일 오전 9시에 알려줘`가 실제 알림 본문 없이도 `방금 생각난 거` 같은 문구를 알림 내용으로 등록할 수 있는 문제를 재현했다.
  - 본문 없는 최근 생각 생성 요청 판정에 `알려`, `챙겨` marker를 추가해, “알림”이라는 명사를 쓰지 않는 자연스러운 알림 요청도 감지하도록 했다.
  - 알림 에이전트가 등록 직전 해당 표현을 감지하면 시간이 있어도 알림을 만들지 않고 `무엇을 알려드릴지` 다시 묻도록 했다.
  - `방금 말한 거 10분 뒤 알려줘`처럼 실제 직전 발화를 참조하는 표현과는 구분되도록, 이번 보강은 `생각난/떠오른` 계열의 본문 없는 요청에만 적용했다.
  - 단위 테스트에 `test_reminder_agent_does_not_create_reminder_from_unspecified_recent_thought`, 디스코드 핸들러 통합 테스트에 `test_assistant_bot_does_not_create_reminder_from_unspecified_recent_thought`를 추가했다.
  - `python3 -m pytest tests/test_memory_store.py::test_reminder_agent_does_not_create_reminder_from_unspecified_recent_thought tests/test_bot_helpers.py::test_assistant_bot_does_not_create_reminder_from_unspecified_recent_thought tests/test_router_heuristics.py::test_task_request_helpers -q`, `python3 -m pytest tests/test_memory_store.py tests/test_bot_helpers.py::test_assistant_bot_does_not_create_reminder_from_unspecified_recent_thought tests/test_bot_helpers.py::test_assistant_bot_does_not_create_task_from_unspecified_recent_thought tests/test_bot_helpers.py::test_assistant_bot_does_not_save_unspecified_recent_thought_as_memory tests/test_router_heuristics.py::test_task_request_helpers tests/test_router_heuristics.py::test_substantive_memory_text_ignores_file_only_instruction -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 직전 발화 기반 알림 본문 보강

- 작업 이름: `방금 말한 거 10분 뒤 알려줘`가 직전 사용자 발화를 알림 본문으로 쓰도록 보강
- 진행상황: 완료
- 진행내용:
  - `방금 말한 거 10분 뒤 알려줘`, `위 내용 10분 뒤 알려줘`, `그거 10분 뒤 알려줘`가 현재는 `방금 말한 거`, `위 내용`, `그거` 자체를 알림 본문으로 추출하는 문제를 재현했다.
  - 공통 helper `asks_to_create_reminder_from_recent_message()`를 추가해, 시간이 있는 알림 요청 중 `방금 말한`, `위 내용`, `그거` 같은 최근 발화 참조 표현을 감지하도록 했다.
  - ReminderAgent가 선택적으로 `ConversationStore`를 받아 최근 사용자 메시지를 조회하고, 최근 발화 참조 알림 요청이면 그 직전 메시지를 알림 본문으로 사용하도록 했다.
  - 직전 사용자 메시지가 없거나 직전 메시지 자체가 다시 최근 발화 참조/본문 없는 최근 생각 요청이면 알림을 등록하지 않고 내용을 직접 물어보도록 했다.
  - 봇과 CLI의 ReminderAgent 생성 경로에 `conversations` 저장소를 전달하도록 배선을 맞췄다.
  - 단위 테스트에 `test_reminder_agent_creates_reminder_from_recent_user_message`, `test_reminder_agent_requires_previous_message_for_recent_reference`, 디스코드 핸들러 통합 테스트에 `test_assistant_bot_creates_reminder_from_previous_user_message`를 추가했다.
  - `python3 -m pytest tests/test_memory_store.py::test_reminder_agent_creates_reminder_from_recent_user_message tests/test_memory_store.py::test_reminder_agent_requires_previous_message_for_recent_reference tests/test_bot_helpers.py::test_assistant_bot_creates_reminder_from_previous_user_message -q`, `python3 -m pytest tests/test_router_heuristics.py::test_task_request_helpers tests/test_memory_store.py::test_reminder_agent_creates_reminder_from_recent_user_message tests/test_memory_store.py::test_reminder_agent_requires_previous_message_for_recent_reference tests/test_memory_store.py::test_reminder_agent_does_not_create_reminder_from_unspecified_recent_thought tests/test_bot_helpers.py::test_assistant_bot_creates_reminder_from_previous_user_message tests/test_bot_helpers.py::test_assistant_bot_does_not_create_reminder_from_unspecified_recent_thought -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 자연어 알림 후속 라우팅 경계 보강

- 작업 이름: `그거 10분 뒤 알려줘`와 `방금 말한 거 10분 뒤 알려줘`의 참조 대상을 분리
- 진행상황: 완료
- 진행내용:
  - 최근 메모 후보가 있는 상태에서 `그거 10분 뒤 알려줘`와 `방금 말한 거 10분 뒤 알려줘`가 모두 `remember` 후속 조회처럼 연결되는 문제를 재현했다.
  - `그거 10분 뒤 알려줘`는 최근 상태 후보를 알림 본문 소스로 쓰는 요청이므로 `manage_reminder` + `reminder_text`로 라우팅되도록 자연어 알림 생성 판정을 확장했다.
  - `방금 말한 거 10분 뒤 알려줘`는 저장된 메모 후보가 아니라 직전 사용자 발화를 소스로 쓰는 요청이므로, 후보 연결을 만들지 않고 ReminderAgent의 최근 발화 처리 경로로 남기도록 했다.
  - `방금 말한`, `위 내용` 같은 최근 대화 소스 생성 요청 감지에 `알려`, `챙겨` marker를 추가해 “알림으로 등록” 같은 명시 표현이 없어도 과연결을 차단하도록 했다.
  - route validation에도 같은 기준을 추가해, 모델이 자연어 알림 요청에 잘못된 linked state를 붙여도 `그거`는 유지하고 `방금 말한 거`는 링크를 제거하도록 방어했다.
  - 라우팅 매트릭스에 `memory_pronoun_create_reminder_uses_memory_as_source_with_time`, `recent_said_reminder_request_does_not_link_previous_memory`를 고정했고, route validation에 자연어 알림 링크 유지/제거 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_route_validation.py::test_validate_route_context_link_keeps_pronoun_reminder_creation_from_memory_reference tests/test_route_validation.py::test_validate_route_context_link_clears_recent_message_reminder_creation_link -q`, `python3 -m ruff check assistant_bot/agents/router.py assistant_bot/route_validation.py tests/test_context_routing_matrix.py tests/test_route_validation.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 일반 이어가기 표현 및 내부 행동 컨텍스트 보강

- 작업 이름: `계속 해줘`, `이어가줘` 같은 위치 이동 후속 표현과 내부 행동 기록 참고 구조 추가
- 진행상황: 완료
- 진행내용:
  - 다른 위치의 문서 분석 후보가 있을 때 `여기서 이어서 해줘`는 확인 질문으로 이어지지만, 더 자연스러운 `계속 해줘`, `이어가줘`는 일반 대화로 빠지는 문제를 확인했다.
  - `계속`, `계속 해줘`, `계속 진행해줘`, `이어가줘`, `이어줘`처럼 짧고 명령형인 표현만 후속 이어가기 신호로 추가했다.
  - `계속 졸려`처럼 단순 잡담에 `계속`이 포함된 경우에는 다른 위치 작업 확인으로 빨려 들어가지 않도록 반례를 함께 고정했다.
  - 기존 `agent_logs` 테이블을 재사용해 사용자에게 보이지 않는 최근 라우팅, 실행 전 검증, 모델 선택 기록을 `최근 내부 행동 기록` 컨텍스트로 만들었다.
  - `ExecutionContext`에 `internal_action_context`를 추가하고 라우터, 전문 에이전트, 최종 응답 작성자가 같은 내부 행동 요약을 참고할 수 있도록 했다.
  - Discord 봇 경로와 로컬 CLI/라우트 미리보기 경로 모두 `AgentLogStore`를 context builder에 전달하도록 맞췄다.
  - 운영 설정으로 `INTERNAL_ACTION_CONTEXT_LIMIT`, `INTERNAL_ACTION_CONTEXT_MAX_CHARS`를 추가하고 `.env.example`, `README.md`에 반영했다.
  - context builder 테스트에 내부 행동 기록이 라우터/에이전트/응답 컨텍스트에 포함되는지 확인하는 케이스를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_includes_recent_internal_action_logs tests/test_context_builder.py::test_build_execution_context_includes_internal_action_logs_for_agents_and_response tests/test_context_routing_matrix.py::test_context_routing_matrix -q`, `python3 -m ruff check assistant_bot/context_builder.py assistant_bot/stores.py assistant_bot/models.py assistant_bot/config.py assistant_bot/bot.py assistant_bot/cli.py tests/test_context_builder.py tests/test_context_routing_matrix.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 같은 사용자 다른 위치 내부 행동 기록 보강

- 작업 이름: 내부 행동 기록도 같은 사용자 기준으로 위치를 넘어 참고하도록 확장
- 진행상황: 완료
- 진행내용:
  - 기존 내부 행동 컨텍스트가 현재 conversation_id의 `agent_logs`만 읽어, 같은 사용자가 DM/채널/스레드를 옮긴 경우 이전 위치의 라우팅·검증 판단을 참고하지 못하는 한계를 확인했다.
  - `AgentLogStore.recent_for_conversations()`를 추가해 여러 conversation_id의 최근 내부 로그를 한 번에 조회하도록 했다.
  - `build_internal_action_context()`가 `ConversationStore.recent_conversations_for_user()`로 같은 사용자 최근 대화 위치를 가져오고, 현재 위치와 같은 사용자 다른 위치의 내부 로그를 함께 포함하도록 했다.
  - 내부 행동 로그 줄에 `location=현재 위치/다른 위치`, `conversation_id=...`를 표시해 라우터와 에이전트가 내부 판단의 출처 위치를 구분할 수 있게 했다.
  - 로그 테이블에 user_id가 없더라도 conversation store에서 같은 사용자 대화 위치를 먼저 고르므로 다른 사용자 내부 로그가 섞이지 않도록 했다.
  - context builder 테스트에 같은 사용자 다른 위치 로그는 포함되고 다른 사용자 로그는 제외되는 케이스를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_includes_recent_internal_action_logs tests/test_context_builder.py::test_build_router_context_includes_same_user_cross_location_internal_action_logs tests/test_context_builder.py::test_build_execution_context_includes_internal_action_logs_for_agents_and_response -q`, `python3 -m ruff check assistant_bot/context_builder.py assistant_bot/stores.py tests/test_context_builder.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 에이전트 실행 결과 내부 로그 보강

- 작업 이름: 최종 `OperationResult`를 내부 행동 기록으로 남겨 다음 턴 컨텍스트에서 참고
- 진행상황: 완료
- 진행내용:
  - 기존 내부 행동 컨텍스트는 `agent_logs`를 읽지만, 모든 최종 에이전트 실행 결과가 일관되게 로그로 남는 구조는 아니라는 점을 확인했다.
  - `record_internal_action_result()`와 `internal_action_result_reason()`을 추가해 최종 `OperationResult`의 agent, intent, status, summary, 주요 대상 슬롯, warnings, next_actions를 짧은 내부 로그로 저장하도록 했다.
  - Discord `on_message()`에서 사용자에게 답변을 구성한 뒤 raw `OperationResult`를 `agent:result` 형태의 내부 로그로 남기도록 했다.
  - 로컬 CLI `run_local_text_interaction()`도 같은 helper를 사용해 실제 운영 경로와 디버그 경로가 동일하게 최종 실행 결과를 기록하도록 했다.
  - 내부 로그 reason은 전체 답변 원문이 아니라 구조화된 요약과 주요 대상 슬롯 위주로 압축해, 다음 라우팅 컨텍스트에 과도한 텍스트가 들어가지 않도록 했다.
  - `test_record_internal_action_result_logs_operation_result_for_future_context`로 결과 로그가 다음 라우터 컨텍스트에 들어가는지 확인했고, `test_local_ask_extracts_recent_conversation_tasks`에 CLI 실제 실행 후 `task:result` 로그가 남는지 검증을 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_logs_operation_result_for_future_context tests/test_cli.py::test_local_ask_extracts_recent_conversation_tasks -q`, `python3 -m ruff check assistant_bot/bot.py assistant_bot/cli.py tests/test_bot_helpers.py tests/test_cli.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 내부 행동 기록 비노출 지침 보강

- 작업 이름: 내부 행동 기록은 참고하되 사용자 답변에는 노출하지 않도록 라우터/응답 작성 지침 정리
- 진행상황: 완료
- 진행내용:
  - `최근 내부 행동 기록`이 라우터와 최종 응답 작성자 입력에 들어가지만, 최종 응답 작성자에게 이를 사용자에게 드러내지 말라는 명시 지침이 부족한 점을 확인했다.
  - ResponseComposer 지침에 내부 행동 기록은 사용자에게 보이지 않는 라우팅/검증/실행 로그이며, 사용자가 직접 묻지 않는 한 로그 이름, agent명, model명, route_validation, `*:result`, 내부 슬롯, 내부 reason을 답변에 드러내지 않도록 추가했다.
  - 내부 행동 기록과 구조화된 실행 결과가 충돌하면 구조화된 실행 결과를 우선하도록 명시했다.
  - RouterAgent 지침에도 내부 행동 기록은 보조 신호일 뿐 사용자 메시지나 실행 대상 본문으로 취급하지 않도록 추가했다.
  - `test_response_composer_treats_internal_action_context_as_hidden_reference`로 내부 로그가 입력에는 들어가지만 응답 작성 지침에서 비노출 규칙이 제공되는지 고정했다.
  - `test_router_agent_prefers_model_route_over_heuristic`에 내부 행동 기록 취급 지침 검증을 추가했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_composer_treats_internal_action_context_as_hidden_reference tests/test_router_agent.py::test_router_agent_prefers_model_route_over_heuristic -q`, `python3 -m ruff check assistant_bot/response_composer.py assistant_bot/agents/router.py tests/test_response_composer.py tests/test_router_agent.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 내부 행동 기록 설계 계약 문서화

- 작업 이름: 새 에이전트 추가 시 따라야 할 내부 행동 기록과 위치 이동 맥락 계약을 `plan.md`에 고정
- 진행상황: 완료
- 진행내용:
  - `plan.md`의 Conversation Agent 설계에 내부 행동 기록이 실행 컨텍스트에 포함되며, 사용자 메시지나 저장 본문으로 취급하지 않는다는 원칙을 추가했다.
  - 같은 사용자 다른 대화 위치의 내부 기록은 자동 실행 근거가 아니라 위치 이동 확인 후보로만 사용하고, 새 대상이 명확하면 새 요청으로 처리하도록 문서화했다.
  - 하단 가정/계약에 새 전문 에이전트가 구조화된 `OperationResult`를 반환하고, 봇 본체가 이를 `agent:result` 내부 로그로 남기는 계약을 추가했다.
  - 내부 로그에는 전체 사용자 발화나 최종 답변 원문 대신 `status`, `summary`, 주요 slots, warnings, next actions 같은 짧은 구조화 단서만 남기도록 정리했다.
  - 내부 행동 기록은 같은 사용자 대화 위치에서만 수집하고, 사용자에게 직접 노출하지 않으며, 현재 메시지와 실제 실행 컨텍스트보다 낮은 우선순위로만 참고하도록 명시했다.

## 2026-06-06 - 추천 요청의 pending 승인 오인 방지

- 작업 이름: `응 저녁 메뉴 추천해줘` 같은 새 요청이 오래된 확인 상태를 승인하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `응 추천해줘`, `응 저녁 메뉴 추천해줘`처럼 긍정 표현으로 시작하지만 실제로는 새 추천 요청인 문장이 `is_context_link_approval_text()`에서 pending 승인처럼 해석될 수 있는 경계를 확인했다.
  - context link 새 요청 marker에 `추천`을 추가해, 오래된 다른 위치 이어가기 확인이나 후속 대상 확인이 떠 있어도 추천 요청은 새 대화 요청으로 남도록 했다.
  - `test_context_link_approval_accepts_plain_confirmation_but_not_new_request`에 `응 저녁 메뉴 추천해줘` 반례를 추가했다.
  - 라우팅 매트릭스에 `positive_prefix_recommendation_not_pending_approval`을 추가해, pending context 후보가 있어도 해당 문장이 `chat + context_link=none`으로 유지되는지 검증했다.
  - `python3 -m pytest tests/test_route_validation.py::test_context_link_approval_accepts_plain_confirmation_but_not_new_request tests/test_context_routing_matrix.py::test_context_routing_matrix -q`, `python3 -m ruff check assistant_bot/route_validation.py tests/test_route_validation.py tests/test_context_routing_matrix.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 설명/식사 잡담의 pending 승인·취소 오인 방지

- 작업 이름: `응 설명해줘`, `괜찮아 뭐 먹을까` 같은 새 대화 요청이 오래된 pending에 소비되지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `응 설명해줘`가 `응` + `해줘` 조합 때문에 context pending 승인처럼 해석될 수 있고, `괜찮아 뭐 먹을까`가 취소 표현으로 시작한다는 이유로 pending 취소처럼 해석될 수 있는 경계를 확인했다.
  - context link 새 요청 marker에 `설명`, `뭐먹`, `뭐할`, `뭐하지`, `뭐해`를 추가해, 자연스러운 설명 요청이나 식사/행동 추천 잡담은 이전 확인 상태를 승인·취소하지 않도록 했다.
  - 순수 승인/취소인 `응 처리해줘`, `괜찮아`는 기존 동작을 유지하는지 함께 확인했다.
  - `test_context_link_approval_accepts_plain_confirmation_but_not_new_request`와 `test_context_link_rejection_rejects_plain_cancel_but_not_new_request`에 반례를 추가했다.
  - 라우팅 매트릭스에 `positive_prefix_explanation_not_pending_approval`, `negative_prefix_food_chat_not_pending_cancel`을 추가해, pending context 후보가 있어도 해당 문장이 `chat + context_link=none`으로 유지되는지 검증했다.
  - `python3 -m pytest tests/test_route_validation.py::test_context_link_approval_accepts_plain_confirmation_but_not_new_request tests/test_route_validation.py::test_context_link_rejection_rejects_plain_cancel_but_not_new_request tests/test_context_routing_matrix.py::test_context_routing_matrix -q`, `python3 -m ruff check assistant_bot/route_validation.py tests/test_route_validation.py tests/test_context_routing_matrix.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 일반 pending 확인 helper 새 요청 경계 고정

- 작업 이름: context pending과 웹검색/삭제 pending이 같은 새 요청 경계를 쓰도록 테스트 계약 보강
- 진행상황: 완료
- 진행내용:
  - context pending에서 막은 `응 설명해줘`, `응 저녁 메뉴 추천해줘`, `괜찮아 뭐 먹을까` 같은 표현이 일반 pending helper에서도 승인/취소로 소비되지 않는지 점검했다.
  - `test_shared_confirmation_helpers_reject_new_requests`에 긍정 확인, 부정 확인, 웹검색 확인, 전체 기억 삭제 확인 helper별 반례를 추가했다.
  - `응 처리해줘`, `괜찮아`, `응, 검색해줘`, `응, 전부 삭제해` 같은 순수 승인/취소/명시 승인 표현은 기존처럼 유지되도록 함께 확인했다.
  - `python3 -m pytest tests/test_route_validation.py::test_shared_confirmation_helpers_reject_new_requests tests/test_route_validation.py::test_context_link_approval_accepts_plain_confirmation_but_not_new_request tests/test_route_validation.py::test_context_link_rejection_rejects_plain_cancel_but_not_new_request -q`, `python3 -m ruff check tests/test_route_validation.py assistant_bot/route_validation.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 에이전트 카탈로그 슬롯명과 내부 시간 로그 정렬

- 작업 이름: 라우터가 참고하는 `state_outputs`를 실제 실행 슬롯명과 맞추고 내부 로그 시간 단서 보강
- 진행상황: 완료
- 진행내용:
  - `agent_catalog.json`에서 현재 시간 에이전트는 실제로 `current_time`을 남기지만 카탈로그에는 `timezone`만 있었고, 알림 에이전트는 실제 `remind_at`을 쓰지만 카탈로그에는 `fire_at`이 남아 있는 불일치를 확인했다.
  - 날씨 에이전트의 `forecast_date`는 현재 실행 결과에 구조화 슬롯으로 남지 않으므로 카탈로그에서 제거해 라우터가 없는 슬롯을 기대하지 않도록 했다.
  - 현재 시간 카탈로그에는 `slots.current_time`을 추가하고, 알림 카탈로그에는 `slots.reminder_id`, `slots.remind_at`을 추가했다.
  - 내부 행동 결과 로그의 안전 슬롯 목록에 `due_at`, `human_due_at`, `remind_at`, `human_remind_at`, `current_time`, `timezone`, `briefing_date`를 추가해, 할 일/알림/시간 조회의 후속 질문에 필요한 시간 단서가 내부 컨텍스트에도 남도록 했다.
  - 카탈로그 프롬프트 테스트에 `slots.current_time`, `slots.remind_at`이 포함되고 `slots.fire_at`, `slots.forecast_date`가 빠지는지 검증을 추가했다.
  - 내부 행동 로그 테스트에 `due_at`, 사람이 읽기 쉬운 기한 표현이 기록되는지 검증을 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_registry_prompt_block_uses_catalog_examples tests/test_bot_helpers.py::test_record_internal_action_result_logs_operation_result_for_future_context -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_agent_registry.py tests/test_bot_helpers.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 취소/미지원 결과 구조화 슬롯 보강

- 작업 이름: `cancel_pending`, `unsupported` 결과도 카탈로그 state_outputs 계약에 맞게 구조화
- 진행상황: 완료
- 진행내용:
  - `cancel_pending` 카탈로그는 `slots.canceled_target`을 선언하지만, registry와 버튼/메시지 취소 경로 일부가 취소 대상을 slots에 남기지 않는 것을 확인했다.
  - 웹검색 확인 취소, 전체 기억 삭제 취소, 메모 대기 취소, 첨부 저장 취소, 후속 작업 이어가기 취소 결과에 `canceled_target` 슬롯을 추가했다.
  - `unsupported` handler가 문자열만 반환하던 구조를 `OperationResult`로 바꿔 `slots.unsupported_reason`을 남기도록 했다.
  - context pending 취소 통합 테스트에 `canceled_target=context_link`와 취소된 linked state ID가 남는지 검증을 추가했다.
  - `unsupported` handler가 구조화된 `OperationResult`를 반환하는지 AST 계약 테스트를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_unsupported_handler_returns_structured_operation_result tests/test_bot_helpers.py::test_assistant_bot_cancels_pending_context_link_and_expires_state tests/test_bot_helpers.py::test_assistant_bot_cancels_latest_pending_context_only -q`, `python3 -m ruff check assistant_bot/agent_registry.py assistant_bot/bot.py tests/test_agent_registry.py tests/test_bot_helpers.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 카탈로그 슬롯 단서 구현 계약 테스트 추가

- 작업 이름: `agent_catalog.json`의 `slots.*` state_outputs가 실제 코드에 존재하는지 검증
- 진행상황: 완료
- 진행내용:
  - 카탈로그가 선언한 슬롯 단서와 실제 코드 문자열을 대조해 `analyze_document`의 `slots.attachment_names`가 실제 결과에 남지 않는 불일치를 발견했다.
  - DocumentAnalysisAgent 성공 결과의 slots에 저장된 문서 제목 목록을 `attachment_names`로 함께 남기도록 수정했다.
  - 문서 분석 테스트에 `scan.png`가 `result.slots["attachment_names"]`로 남는지 검증을 추가했다.
  - `test_agent_catalog_slot_outputs_are_represented_in_code`를 추가해, 앞으로 카탈로그에 `slots.*`를 선언하면서 실제 코드에 해당 키가 없으면 테스트가 실패하도록 했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_agent_catalog_slot_outputs_are_represented_in_code tests/test_document_analysis_agent.py::test_document_analysis_agent_uses_fixed_vision_model_and_auto_detail tests/test_agent_registry.py::test_unsupported_handler_returns_structured_operation_result tests/test_bot_helpers.py::test_assistant_bot_cancels_pending_context_link_and_expires_state -q`, `python3 -m ruff check assistant_bot/agents/document_analysis.py assistant_bot/agent_registry.py assistant_bot/bot.py tests/test_agent_registry.py tests/test_document_analysis_agent.py tests/test_bot_helpers.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 카탈로그 아티팩트 단서 구현 계약 테스트 추가

- 작업 이름: `agent_catalog.json`의 `artifacts.*` state_outputs를 실제 artifact kind 구조와 맞춤
- 진행상황: 완료
- 진행내용:
  - 카탈로그의 `delete_memory`, `restore_memory`가 `artifacts.deleted_ids`, `artifacts.restored_ids`를 선언했지만 실제 코드는 별도 deleted/restored artifact key가 아니라 `kind=memory/document`와 ID로 대상을 남기는 구조임을 확인했다.
  - `delete_memory`, `restore_memory` 카탈로그 state_outputs를 `artifacts.memory_ids`, `artifacts.document_ids`로 수정해 실제 라우터 artifact 해석 구조와 맞췄다.
  - `test_agent_catalog_artifact_outputs_are_represented_by_known_artifact_kinds`를 추가해, 카탈로그에 지원하지 않는 artifact output 이름이 들어오면 테스트가 실패하도록 했다.
  - `memory_ids`, `document_ids`, `task_ids`, `reminder_ids`, `urls`는 실제 artifact kind인 `memory`, `document`, `task`, `reminder`, `url`로 대응해 검증한다.
  - `python3 -m pytest tests/test_agent_registry.py::test_agent_catalog_artifact_outputs_are_represented_by_known_artifact_kinds tests/test_agent_registry.py::test_agent_catalog_slot_outputs_are_represented_in_code tests/test_agent_registry.py::test_registry_prompt_block_uses_catalog_examples -q`, `python3 -m ruff check tests/test_agent_registry.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 내부 행동 로그 구조화 슬롯 보존 보강

- 작업 이름: 문서명, 취소 대상, 미지원 사유 같은 새 구조화 슬롯을 내부 행동 기록에도 남김
- 진행상황: 완료
- 진행내용:
  - `attachment_names`, `filenames`, `canceled_target`, `unsupported_reason`이 `OperationResult.slots`에는 들어갈 수 있지만 내부 행동 로그의 안전 슬롯 필터에는 빠져 있음을 확인했다.
  - 내부 행동 로그 안전 슬롯 목록에 `attachment_names`, `filenames`, `canceled_target`, `unsupported_reason`을 추가했다.
  - 문서 분석 결과는 파일명 단서를, 첨부/후속 작업 취소 결과는 취소 대상을, 미지원 결과는 미지원 사유를 다음 턴 라우터가 보조 신호로 참고할 수 있게 했다.
  - `test_record_internal_action_result_keeps_structured_context_slots`를 추가해 해당 슬롯들이 `agent_logs.reason`에 남는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_logs_operation_result_for_future_context tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 현재 대화 위치 컨텍스트 명시화

- 작업 이름: 채팅 위치 변경 상황에서 이전 작업 연결 여부를 더 명확히 판단하도록 현재 위치 정보 보강
- 진행상황: 완료
- 진행내용:
  - 라우터와 각 에이전트가 `conversation_id`만 보고 현재 위치와 다른 위치 후보를 비교해야 하는 구조를 점검했다.
  - `ExecutionContext`에 `current_location_context`를 추가하고, router/agent/response 컨텍스트에 현재 대화 위치, channel/guild 정보, 교차 위치 후속 처리 정책을 함께 전달하도록 했다.
  - `build_router_context()`에도 `현재 대화 위치` 섹션을 추가해, 라우터가 현재 위치와 `최근 작업 상태 후보`의 `location=다른 위치`를 명확히 대조할 수 있게 했다.
  - `RouterAgent.route()`의 OpenAI 입력에도 현재 위치 문구를 직접 포함해, 모델이 채팅 위치 변경 상황을 놓치지 않도록 했다.
  - `test_build_router_context_includes_summary_and_recent_messages`, `test_build_execution_context_links_selected_turn_state`, `test_router_agent_prefers_model_route_over_heuristic`에 현재 위치 컨텍스트 검증을 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_includes_summary_and_recent_messages tests/test_context_builder.py::test_build_execution_context_links_selected_turn_state tests/test_router_agent.py::test_router_agent_prefers_model_route_over_heuristic -q`, `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m ruff check assistant_bot/context_builder.py assistant_bot/models.py assistant_bot/agents/router.py tests/test_context_builder.py tests/test_router_agent.py`를 통과했다.

## 2026-06-06 - 위치 변경 확인 질문 응답 보존

- 작업 이름: 최종 응답 작성자가 교차 위치 확인 질문을 실행 완료 답변처럼 바꾸지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 라우터가 `needs_input + clarify`로 올바르게 멈춰도, 최종 응답 작성 모델이 이를 자연화하는 과정에서 확인 질문의 의미를 흐릴 수 있는 지점을 확인했다.
  - `ResponseComposer` 프롬프트에 `status=needs_input`이고 `available_actions`에 `clarify`가 있으면 이미 실행한 것처럼 말하지 말고, 짧은 확인 질문으로 유지하라는 규칙을 추가했다.
  - 특히 채팅 위치가 바뀐 다른 위치 작업을 이어갈지 묻는 결과는 그 의미를 유지하도록 명시했다.
  - `test_response_composer_preserves_cross_location_clarification_as_question`를 추가해, 현재 위치 컨텍스트와 pending linked state가 응답 작성 입력에 들어가고 확인 질문 보존 규칙이 프롬프트에 포함되는지 검증했다.
  - `python3 -m pytest tests/test_response_composer.py -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_response_composer.py tests/test_context_builder.py -q`, `python3 -m ruff check assistant_bot/response_composer.py tests/test_response_composer.py`를 통과했다.

## 2026-06-06 - pending 확인 슬롯 내부 로그 보존

- 작업 이름: 후속 작업 확인 질문의 원문과 복원 슬롯을 내부 행동 기록에 남김
- 진행상황: 완료
- 진행내용:
  - `needs_input + clarify` 상태는 turn state에는 저장되지만, 내부 행동 로그의 안전 슬롯 필터에는 `pending_linked_state_id`, `pending_resolved_slots`, `pending_original_text`가 빠져 있어 다음 턴 보조 맥락으로는 부족할 수 있음을 확인했다.
  - 내부 행동 로그 안전 슬롯 목록에 `pending_linked_state_id`, `pending_resolved_slots`, `pending_original_text`를 추가했다.
  - 라우터가 만든 확인 질문의 대상 state ID, 실행 복원 슬롯, 사용자의 원래 후속 요청 문장이 내부 행동 기록에도 남아 다음 라우팅 판단의 보조 신호가 되도록 했다.
  - `test_record_internal_action_result_keeps_structured_context_slots`에 pending 확인 질문 결과를 추가해 해당 슬롯과 원문이 `agent_logs.reason`에 남는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-06 - pending 확인 상태 대상명 명시화

- 작업 이름: 후속 작업 확인 상태의 subject/summary에 실제 대상명을 포함
- 진행상황: 완료
- 진행내용:
  - 교차 위치 또는 후속 작업 확인 질문이 `후속 요청 대상 확인`이라는 일반 subject로 저장되어, 라우터가 다음 턴에서 슬롯을 자세히 읽어야만 대상을 알 수 있는 지점을 확인했다.
  - linked state가 있는 clarify 결과는 linked state의 subject/summary를 사용해 `후속 요청 대상 확인: 할 일 3 병원 예약`처럼 대상명이 드러나도록 했다.
  - summary도 ``할 일 3 병원 예약` 작업을 이어갈지 확인 필요` 형태로 바꿔, turn state 후보 목록만 읽어도 어떤 작업을 확인 중인지 알 수 있게 했다.
  - `facts.linked_subject`도 함께 남겨 최종 응답 작성자와 내부 로그가 같은 대상명을 참고할 수 있게 했다.
  - `test_assistant_bot_preserves_cross_location_candidate_in_clarification_result`, `test_assistant_bot_records_linked_clarification_subject_for_context`에 대상명 subject/summary 보존 검증을 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_preserves_cross_location_candidate_in_clarification_result tests/test_bot_helpers.py::test_assistant_bot_records_linked_clarification_subject_for_context tests/test_bot_helpers.py::test_assistant_bot_records_clarification_state_with_pending_ttl -q`, `python3 -m pytest tests/test_bot_helpers.py -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-06 - 버튼 승인 결과 내부 행동 로그 기록

- 작업 이름: Discord 버튼으로 승인/거부한 작업 결과도 내부 행동 기록에 남김
- 진행상황: 완료
- 진행내용:
  - 일반 메시지 처리 경로는 `record_internal_action_result()`를 호출하지만, 버튼 확인 처리 경로는 대화 메시지와 turn state만 기록하고 내부 행동 로그를 남기지 않는 것을 확인했다.
  - `handle_confirmation_button()`의 성공적인 기록 블록에 `record_internal_action_result()` 호출을 추가해, 버튼으로 이어간 작업 결과도 다음 턴 라우터의 내부 맥락에 들어가도록 했다.
  - context continuation 버튼 승인 테스트에 bot user를 세팅해 실제 기록 블록을 실행시키고, `task:result`, `manage_task`, `task_id`, 실행 summary가 `agent_logs.reason`에 남는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_context_confirmation_button_approval_dispatches_original_intent -q`, `python3 -m pytest tests/test_bot_helpers.py -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-06 - CLI pending 확인 대상명 정책 정렬

- 작업 이름: 로컬 CLI 경로도 Discord 봇과 같은 후속 확인 대상명 기록 정책 적용
- 진행상황: 완료
- 진행내용:
  - Discord 봇 경로는 linked state가 있는 clarify 결과의 subject/summary에 실제 대상명을 남기지만, CLI `run_local_text_interaction()` 경로는 아직 `후속 요청 대상 확인`처럼 일반 subject를 쓰고 있음을 확인했다.
  - CLI clarify 생성부도 `linked_turn_state_subject()`를 사용해 `후속 요청 대상 확인: ...`, ``...` 작업을 이어갈지 확인 필요`, `facts.linked_subject`를 남기도록 맞췄다.
  - 로컬 실행/미리보기 환경에서도 turn state 후보를 읽을 때 확인 중인 대상이 더 직접적으로 드러나도록 했다.
  - `test_cli_clarification_result_records_linked_subject_contract`를 추가해 CLI clarify 경로가 linked subject, summary, facts, subject 정책을 유지하는지 검증했다.
  - `python3 -m pytest tests/test_cli.py::test_cli_clarification_result_records_linked_subject_contract tests/test_cli.py::test_preview_route_details_includes_linked_state_and_candidates -q`, `python3 -m pytest tests/test_cli.py -q`, `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py`를 통과했다.

## 2026-06-06 - context 버튼 거부 원문 보존

- 작업 이름: 후속 작업 이어가기 버튼 거부 결과에도 원래 요청과 복원 슬롯을 남김
- 진행상황: 완료
- 진행내용:
  - context continuation 버튼 승인 경로는 원래 요청 문장과 실행 슬롯을 복원하지만, 거부 경로는 취소 대상만 남기고 어떤 후속 요청을 거부했는지 단서가 부족한 것을 확인했다.
  - 버튼 거부 결과의 slots에 `pending_intent`, `pending_context_link`, `pending_resolved_slots`, `pending_original_text`를 함께 남기도록 했다.
  - 버튼 거부 후 내부 행동 기록에도 `pending_original_text`와 `pending_resolved_slots`가 남아 다음 턴 라우터가 “방금 어떤 이어가기 요청을 취소했는지” 참고할 수 있게 했다.
  - `test_context_confirmation_button_rejection_expires_pending_state`에 bot user를 세팅해 실제 기록 블록을 실행시키고, `router:result`, `cancel_pending`, `pending_original_text`, 원문, 복원 슬롯이 `agent_logs.reason`에 남는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_context_confirmation_button_rejection_expires_pending_state -q`, `python3 -m pytest tests/test_bot_helpers.py -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-06 - 후속 확인 결과 생성 공통화

- 작업 이름: Discord 봇과 CLI의 context clarify OperationResult 생성 로직을 공통 helper로 통합
- 진행상황: 완료
- 진행내용:
  - Discord 봇과 CLI 양쪽에 `needs_input + clarify` 결과 생성 로직이 중복되어, pending 대상명/복원 슬롯 정책이 나중에 한쪽만 바뀔 위험이 있음을 확인했다.
  - `build_context_clarification_result()` helper를 추가해 context link, pending linked state, pending intent, pending resolved slots, pending original text, linked subject 기록을 한 곳에서 생성하도록 했다.
  - `AssistantBot.handle_message()`와 CLI `run_local_text_interaction()` 모두 이 helper를 사용하도록 정리했다.
  - CLI 정적 계약 테스트를 “직접 구현 확인”에서 “공통 helper 사용 및 helper 내부 정책 확인”으로 바꿔, 앞으로 양쪽 경로가 같은 정책을 쓰는지 검증하게 했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_preserves_cross_location_candidate_in_clarification_result tests/test_bot_helpers.py::test_assistant_bot_records_linked_clarification_subject_for_context tests/test_cli.py::test_cli_clarification_result_records_linked_subject_contract -q`, `python3 -m pytest tests/test_bot_helpers.py -q`, `python3 -m pytest tests/test_cli.py -q`, `python3 -m ruff check assistant_bot/bot.py assistant_bot/cli.py tests/test_bot_helpers.py tests/test_cli.py`를 통과했다.

## 2026-06-06 - 후속 취소 결과 생성 공통화

- 작업 이름: 버튼 거부, 채팅 취소, CLI 취소의 context cancellation 결과 슬롯 정책 통합
- 진행상황: 완료
- 진행내용:
  - 버튼 거부 경로는 원래 요청/복원 슬롯을 남기도록 보강했지만, 채팅으로 `아니 하지마`처럼 취소하는 경로와 CLI 취소 경로는 여전히 취소 대상만 남기는 것을 확인했다.
  - `build_context_cancellation_result()` helper를 추가해 `canceled_target`, 취소된 context state ID, pending linked state ID, pending intent, pending context link, pending resolved slots, pending original text를 한 곳에서 생성하도록 했다.
  - Discord 버튼 거부, Discord 채팅 취소, CLI 취소 경로가 모두 이 helper를 사용하도록 정리했다.
  - `test_assistant_bot_cancels_pending_context_link_and_expires_state`에 채팅 취소 결과의 pending 원문/복원 슬롯 검증을 추가했다.
  - `test_cli_context_cancellation_uses_shared_result_contract`를 추가해 CLI도 공통 취소 helper를 사용하는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_cancels_pending_context_link_and_expires_state tests/test_bot_helpers.py::test_context_confirmation_button_rejection_expires_pending_state tests/test_cli.py::test_cli_context_cancellation_uses_shared_result_contract -q`, `python3 -m pytest tests/test_bot_helpers.py -q`, `python3 -m pytest tests/test_cli.py -q`, `python3 -m ruff check assistant_bot/bot.py assistant_bot/cli.py tests/test_bot_helpers.py tests/test_cli.py`를 통과했다.

## 2026-06-06 - 후속 취소 facts 단서 보강

- 작업 이름: context cancellation 결과의 facts에도 원래 요청과 복원 슬롯을 포함
- 진행상황: 완료
- 진행내용:
  - 후속 취소 결과의 slots에는 pending 원문/복원 슬롯이 남지만, 최종 응답 작성자가 우선 참고하는 `facts`에는 취소된 state ID만 있어 표현 안정성이 떨어질 수 있음을 확인했다.
  - `build_context_cancellation_result()`의 facts에 `pending_intent`, `pending_context_link`, `pending_resolved_slots`, `pending_original_text`를 추가했다.
  - 응답 작성자가 구조화된 실행 결과를 볼 때도 “어떤 후속 요청을 취소했는지”를 facts 영역에서 바로 확인할 수 있게 했다.
  - `test_assistant_bot_cancels_pending_context_link_and_expires_state`에 facts 검증을 추가했다.
  - `test_response_composer_gets_context_cancellation_facts`를 추가해 최종 응답 작성 입력에 취소 원문과 복원 슬롯이 포함되는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_cancels_pending_context_link_and_expires_state tests/test_response_composer.py::test_response_composer_gets_context_cancellation_facts -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_response_composer.py -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py tests/test_response_composer.py`를 통과했다.

## 2026-06-06 - 내부 행동 로그 facts 병합

- 작업 이름: OperationResult facts에 있는 안전한 맥락 단서도 내부 행동 기록에 반영
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그가 `result.slots` 또는 추론 슬롯 중심으로만 단서를 남겨, `facts`에만 들어 있는 pending 원문/linked subject 같은 정보가 누락될 수 있는 구조를 확인했다.
  - 내부 행동 로그 안전 키 목록을 `INTERNAL_ACTION_CONTEXT_KEYS`로 공통화하고, `facts`, 추론 슬롯, `slots`를 순서대로 병합해 안전한 단서를 기록하도록 했다.
  - `queries`, `validation_reason`, `linked_subject`도 안전 키에 포함해 웹/검증/후속 대상 단서를 더 잘 남기게 했다.
  - `test_record_internal_action_result_keeps_structured_context_slots`에 facts-only 후속 취소 결과를 추가해 `pending_original_text`, `pending_resolved_slots`, `linked_subject`가 내부 로그에 남는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`, `python3 -m pytest tests/test_bot_helpers.py -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-06 - 카탈로그 슬롯 내부 로그 계약 추가

- 작업 이름: 에이전트 카탈로그의 `slots.*` state_outputs가 내부 행동 로그 안전 키에도 포함되는지 검증
- 진행상황: 완료
- 진행내용:
  - `agent_catalog.json`의 `slots.topic`, `slots.memory_text`, `slots.pending_query`, `slots.conversation_id` 같은 라우터용 단서가 내부 행동 로그 안전 키에는 일부 빠져 있음을 확인했다.
  - 내부 행동 로그 안전 키에 `topic`, `location_label`, `memory_text`, `new_text`, `pending_query`, `conversation_id`를 추가했다.
  - `test_agent_catalog_slot_outputs_are_available_for_internal_action_context`를 추가해, 앞으로 에이전트 카탈로그에 새 `slots.*`를 선언하면 내부 행동 로그 안전 키나 ID 슬롯 키에 포함되어야 테스트가 통과하도록 했다.
  - 새 에이전트 추가 시 state_outputs에는 있지만 내부 로그에는 빠지는 불일치를 조기에 잡을 수 있게 했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_agent_catalog_slot_outputs_are_available_for_internal_action_context tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`, `python3 -m pytest tests/test_agent_registry.py -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_agent_registry.py`를 통과했다.

## 2026-06-06 - 내부 행동 로그 artifact 단서 보강

- 작업 이름: OperationResult artifacts의 대상 ID/URL도 내부 행동 기록에 요약
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그가 subject와 slots/facts만 기록하고 artifacts는 남기지 않아, 문서/메모/할 일/알림/URL 대상이 artifacts에만 있는 결과를 다음 턴에서 놓칠 수 있음을 확인했다.
  - `safe_internal_action_artifact_values()`를 추가해 `memory_ids`, `document_ids`, `task_ids`, `reminder_ids`, `urls`를 안전하게 요약하도록 했다.
  - `internal_action_result_reason()`이 artifact 요약을 함께 기록하도록 변경했다.
  - `test_record_internal_action_result_keeps_structured_context_slots`에 artifacts-only 결과를 추가해 memory/document/task/url 단서가 내부 로그에 남는지 검증했다.
  - `test_agent_catalog_artifact_outputs_are_available_for_internal_action_context`를 추가해 카탈로그의 `artifacts.*` 출력이 내부 행동 로그 artifact 요약 키로 보존되는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots tests/test_agent_registry.py::test_agent_catalog_artifact_outputs_are_available_for_internal_action_context -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_agent_registry.py -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py tests/test_agent_registry.py`를 통과했다.

## 2026-06-06 - 내부 행동 로그 artifact 제목 단서 보강

- 작업 이름: artifact ID뿐 아니라 제목/파일명도 내부 행동 기록에 남김
- 진행상황: 완료
- 진행내용:
  - artifact 내부 로그가 ID/URL만 남기면 사용자의 자연어 후속 지칭인 파일명, 메모 제목, 할 일 제목과 매칭하기 어려운 점을 확인했다.
  - `safe_internal_action_artifact_values()`가 `memory_titles`, `document_titles`, `task_titles`, `reminder_titles`, `url_titles`도 함께 요약하도록 했다.
  - artifact의 `title`, `filename`, `name` 중 사용 가능한 값을 제목 단서로 수집한다.
  - `test_record_internal_action_result_keeps_structured_context_slots`에 제목 단서 검증을 추가했다.
  - `test_agent_catalog_artifact_outputs_are_available_for_internal_action_context`도 샘플 artifact 제목 요약을 검증하도록 보강했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots tests/test_agent_registry.py::test_agent_catalog_artifact_outputs_are_available_for_internal_action_context -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_agent_registry.py -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py tests/test_agent_registry.py`를 통과했다.

## 2026-06-06 - 내부 행동 로그 최신순/트리밍 보강

- 작업 이름: 라우터 컨텍스트의 내부 행동 기록을 최신순으로 정리하고 핵심 지침이 잘리지 않도록 개선
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록이 오래된 순서로 보이고, max chars 제한이 걸릴 때 “현재 사용자 요청이 우선”이라는 지침이 밀려날 수 있는 구조를 확인했다.
  - `build_internal_action_context()`를 최신순 출력으로 바꾸고, 각 로그에 `recency=latest/older`를 명시했다.
  - 내부 행동 기록 헤더에 “현재 사용자 요청 > 현재 위치 작업 상태 > 명확한 후속 요청으로 연결된 다른 위치 작업 > 오래된 내부 기록” 우선순위를 고정했다.
  - `trim_context_lines_with_pinned_header()`를 추가해 문자 수 제한이 작아도 내부 행동 기록의 해석 지침과 최신 로그가 남도록 했다.
  - 최신 내부 행동 로그가 오래된 로그보다 먼저 나오고, 제한 상황에서도 최신 핵심 단서가 유지되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 명시적 새 대상 링크 검증 보강

- 작업 이름: 이전 작업 후속 표현과 명시적 새 대상 표현을 route validation 단계에서 더 정확히 분리
- 진행상황: 완료
- 진행내용:
  - 모델이 `문서 9 다시 분석해봐`, `contract_v2.pdf 다시 분석해봐`처럼 새 대상이 명시된 요청을 이전 문서 상태에 잘못 연결할 경우, 기존 검증이 `다시` 표현 때문에 확인 질문으로 흐를 수 있는 위험을 확인했다.
  - `has_explicit_new_target_reference()`를 URL뿐 아니라 메모/문서/할 일/알림 ID, 파일명, 명시적 날씨 지역 표현까지 감지하도록 확장했다.
  - 명시적 새 문서 ID나 새 파일명이 기존 linked state와 불일치하면 `context_link=clarify`가 아니라 `context_link=none`으로 링크를 끊도록 회귀 테스트를 추가했다.
  - 기존 task/weather/url mismatch 테스트와 함께, 새 대상은 현재 위치의 새 요청으로 처리하고 애매한 대명사 후속만 확인 질문으로 남기는 계약을 강화했다.
  - `python3 -m pytest tests/test_route_validation.py -q`, `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - CLI pending 작업 결과 구조화

- 작업 이름: 로컬 CLI의 메모 대기/삭제 확인 결과도 `OperationResult`로 반환해 내부 행동 기록에 남김
- 진행상황: 완료
- 진행내용:
  - Discord 경로는 pending 메모/삭제 결과를 `OperationResult`로 남기지만, 로컬 CLI helper는 문자열을 바로 반환해 최종 `record_internal_action_result()`에서 구조화 결과가 누락되는 것을 확인했다.
  - `handle_local_pending_memory_capture()`와 `handle_local_pending_memory_deletion()`이 저장, 취소, 중복, 유사 메모, 만료, 삭제 없음 결과를 모두 `OperationResult`로 반환하도록 변경했다.
  - 대기 중인 메모 저장 성공 facts에 `memory_text`를 추가해 내부 행동 로그의 안전 키 목록에 본문 단서가 남도록 했다. 같은 위험이 있는 Discord 메모 대기 저장 결과에도 `memory_text`를 추가했다.
  - CLI pending 메모 저장과 삭제 취소가 내부 행동 로그에 `memory_id`, `memory_text`, `canceled_target` 단서를 남기는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_cli.py::test_cli_pending_memory_capture_returns_operation_result_for_internal_context tests/test_cli.py::test_cli_pending_memory_deletion_cancel_returns_operation_result_for_internal_context tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`, `python3 -m pytest tests/test_cli.py -q`, `python3 -m pytest tests/test_bot_helpers.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 응답 컨텍스트 내부 행동 기록 우선순위 보강

- 작업 이름: 최종 응답 작성자가 긴 컨텍스트에서도 최신 내부 행동 기록을 볼 수 있도록 우선순위 조정
- 진행상황: 완료
- 진행내용:
  - `ExecutionContext.for_response()`가 앞에서부터 문자 수를 자르는데, 기존 순서에서는 `최근 내부 행동 기록`이 연결 상태/요약/최근 맥락 뒤에 있어 긴 컨텍스트에서 잘릴 수 있음을 확인했다.
  - 응답 작성자가 방금 수행된 실행 결과와 검증 로그를 참고할 수 있도록 `최근 내부 행동 기록`을 `연결된 이전 작업 상태`보다 앞에 배치했다.
  - 긴 요약/최근 맥락이 있어도 응답용 컨텍스트에 `memory:result`, `memory_text` 같은 내부 실행 단서가 남는 회귀 테스트를 보강했다.
  - 구조화된 실행 결과 자체가 여전히 최우선이며, 내부 행동 기록은 표현 안정화와 맥락 판단 보조 신호로만 사용하도록 기존 응답 작성자 프롬프트 정책을 유지했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_keeps_resolved_slots_when_truncated -q`, `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 에이전트 카탈로그 후속 액션 계약 보강

- 작업 이름: 라우터가 참조하는 에이전트 목록과 실제 `OperationResult` 후속 액션을 일치시킴
- 진행상황: 완료
- 진행내용:
  - 실제 날씨 에이전트는 `show_alerts`, `check_air_quality` 후속 액션을 반환할 수 있지만 `agent_catalog.json`에는 `retry`만 선언되어 있어 라우터 프롬프트의 후속 맥락 단서가 부족한 점을 확인했다.
  - 오늘 브리핑 결과도 `continue` 액션을 반환하지만 카탈로그에는 빠져 있어, `daily_briefing`의 후속 처리 가능성이 라우터 목록에 덜 드러나는 점을 확인했다.
  - `agent_catalog.json`의 `weather`에 `available_actions.show_alerts`, `available_actions.check_air_quality`를 추가하고, `daily_briefing`에 `available_actions.continue`를 추가했다.
  - 코드에 literal로 선언된 `OperationResult(intent=..., available_actions=...)`가 카탈로그에 빠지면 실패하는 AST 기반 회귀 테스트를 추가했다.
  - 라우터 fallback과 route validation이 `미세먼지/대기질`을 `check_air_quality`, `특보/경보/주의보`를 `show_alerts` 후속 액션으로 인식하도록 보강했다.
  - 이전 날씨 후보 뒤에 `미세먼지도 봐줘`, `특보도 확인해줘`라고 했을 때 같은 날씨 상태의 지역을 이어받는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py tests/test_router_agent.py::test_router_fallback_links_weather_air_quality_follow_up tests/test_router_agent.py::test_router_fallback_links_weather_alert_follow_up tests/test_route_validation.py::test_requested_actions_from_text_detects_weather_follow_up_actions -q`, `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 후보 선택 pending 상태 만료 보강

- 작업 이름: 여러 후속 대상 후보 중 하나를 선택한 뒤 확인용 pending state가 남지 않도록 정리
- 진행상황: 완료
- 진행내용:
  - `그거 삭제해`처럼 후보가 여러 개라 확인 질문을 만든 뒤, 사용자가 `두번째`, `장보기`처럼 후보를 선택하면 라우팅은 복원되지만 후보 선택용 pending state가 만료되지 않을 수 있음을 확인했다.
  - `matching_pending_candidate_selection_states()`를 추가해 복원된 route의 `pending_original_text`와 후보 선택 pending state를 안전하게 매칭하도록 했다.
  - Discord 봇의 `expire_selected_pending_candidate_context_links()`와 CLI의 동일 helper를 추가해, 선택이 처리된 후보 확인 pending state만 만료하도록 했다.
  - unrelated pending 후보 확인은 유지하고, 실제 선택된 확인 state만 만료되는 회귀 테스트를 route validation, CLI, Discord bot helper에 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_matching_pending_candidate_selection_states_matches_original_text tests/test_cli.py::test_cli_expires_selected_pending_candidate_context_link tests/test_bot_helpers.py::test_assistant_bot_expires_selected_pending_candidate_context -q`, `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_cli.py tests/test_bot_helpers.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 현재 위치 내부 행동 로그 보존

- 작업 이름: 다른 위치 로그가 더 최신이어도 현재 대화 위치의 내부 행동 기록이 라우터 컨텍스트에서 밀리지 않도록 개선
- 진행상황: 완료
- 진행내용:
  - `build_internal_action_context()`가 현재 위치와 다른 위치 conversation_id를 합쳐 최신 N개만 가져와, 다른 위치 로그가 많이 쌓이면 현재 위치의 중요한 route validation/result 로그가 빠질 수 있음을 확인했다.
  - 현재 위치 로그를 먼저 최소 절반가량 확보하고, 남은 슬롯을 같은 사용자 다른 위치 로그로 채우는 방식으로 수집 정책을 변경했다.
  - `AgentLogStore.recent()`도 `conversation_id`를 함께 반환하도록 맞춰 내부 행동 로그 포맷이 현재/다른 위치를 일관되게 구분하게 했다.
  - 다른 위치 로그가 더 최신으로 많이 쌓여도 `현재위치핵심단서`가 컨텍스트에 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_keeps_current_location_internal_logs_when_cross_location_is_newer tests/test_context_builder.py::test_build_router_context_includes_recent_internal_action_logs tests/test_context_builder.py::test_build_router_context_includes_same_user_cross_location_internal_action_logs -q`, `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py::test_record_internal_action_result_logs_operation_result_for_future_context tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 직전 assistant 예시 참조 focused context 보강

- 작업 이름: 사용자가 “네가 예를 들어준 내용 그대로”처럼 직전 봇 예시를 참조할 때 최근 assistant 답변을 안정적으로 보존
- 진행상황: 완료
- 진행내용:
  - 메모 에이전트 자체에는 직전 assistant 예시를 파싱하는 로직이 있지만, 공통 `build_focused_context()`는 `네가 예를`, `예시`, `그대로` 같은 표현을 후속 참조로 분류하지 않아 모델 기반 에이전트가 늘어날수록 직전 봇 예시를 놓칠 수 있는 구조를 확인했다.
  - `is_follow_up_question()`에 `네가 예`, `너가 예`, `니가 예`, `예로 든`, `예시`, `그대로` 후속 참조 신호를 추가했다.
  - 사용자가 `네가 예를 들어준 내용 그대로 수정해줘`라고 말하면 직전 assistant 예시 문장이 focused context에 남는 회귀 테스트를 추가했다.
  - 기존 메모 에이전트의 `test_memory_agent_updates_from_recent_assistant_example`도 함께 확인해, 공통 컨텍스트 보강과 에이전트별 파싱이 같은 방향으로 작동하는지 검증했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_focused_context_keeps_recent_assistant_example_reference tests/test_context_builder.py::test_build_execution_context_focuses_follow_up_question -q`, `python3 -m pytest tests/test_context_builder.py tests/test_memory_store.py::test_memory_agent_updates_from_recent_assistant_example -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 공통 맥락 판별 정책 컨텍스트 추가

- 작업 이름: 라우터·에이전트·응답 생성기가 같은 후속 요청 판별 기준을 공유하도록 컨텍스트 보강
- 진행상황: 완료
- 진행내용:
  - 채팅 위치가 바뀐 경우 이전 위치 작업을 이어갈지 물어보는 구조는 들어갔지만, 라우터 프롬프트에 흩어진 정책을 실행 에이전트와 응답 생성기도 같은 형태로 보지 못하는 점을 확인했다.
  - `build_context_decision_context()`를 추가해 “현재 사용자 메시지 우선”, “다른 위치 작업은 확인 후 실행”, “새 지역/파일/ID/URL/검색어/주제는 새 요청”, “짧은 응답은 직전 확인 질문이 있을 때만 승인/거부” 규칙을 공통 컨텍스트로 만들었다.
  - `build_router_context()`와 `ExecutionContext.for_agent()`, `ExecutionContext.for_response()`에 `맥락 판별 정책` 섹션을 포함해 라우터 이후 단계도 같은 경계 조건을 참고하도록 했다.
  - 라우터 컨텍스트와 에이전트 실행 컨텍스트에 정책 문구가 포함되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 높은 confidence chat 응답의 pending 확인 복원 보강

- 작업 이름: 라우터 모델이 짧은 승인/거부를 일반 대화로 판단해도 직전 확인 상태를 놓치지 않도록 보정
- 진행상황: 완료
- 진행내용:
  - 기존 라우터 보정은 모델이 `chat/context none`을 낮은 confidence로 반환할 때만 맥락 후보 fallback을 시도해, 모델이 `응`, `아니 취소해`를 높은 confidence의 일반 대화로 판단하면 pending 확인 상태를 놓칠 수 있음을 확인했다.
  - `model_route_needs_context_refinement()`가 순수한 context 승인/거부 문장에서는 confidence와 무관하게 맥락 후보 fallback을 한 번 시도하도록 변경했다.
  - 사용자가 새 요청을 붙인 `응 서울 날씨 알려줘`, `아니 취소 말고 목록 보여줘`류는 기존 새 요청 방어 로직을 유지해 승인/거부로 소비하지 않도록 했다.
  - 모델이 높은 confidence로 `chat`을 반환해도 `응`은 pending 원래 작업으로 복원되고, `아니 취소해`는 pending 취소로 복원되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_refines_high_confidence_chat_for_pending_context_approval tests/test_router_agent.py::test_router_refines_high_confidence_chat_for_pending_context_rejection tests/test_router_agent.py::test_router_fallback_does_not_approve_pending_context_for_positive_prefixed_weather_request tests/test_router_agent.py::test_router_fallback_does_not_cancel_pending_context_for_negative_prefixed_web_request -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 높은 confidence chat 응답의 명확한 후속 요청 복원 보강

- 작업 이름: 라우터 모델이 명확한 후속 요청을 일반 대화로 오판해도 작업 후보를 다시 연결
- 진행상황: 완료
- 진행내용:
  - 기존 보정은 낮은 confidence의 `chat/context none` 또는 순수 승인/거부 답변에 주로 작동해, 모델이 `그거 완료했어`, `다시해봐` 같은 명확한 후속 요청을 높은 confidence의 일반 대화로 판단하면 후보 연결을 놓칠 수 있음을 확인했다.
  - `model_route_needs_context_refinement()`가 `chat/context none`이면서 후속 요청 신호가 있는 경우 confidence와 무관하게 fallback 후보 검사를 수행하도록 확장했다.
  - fallback이 이전 후보 연결이 아니라 명시적인 비-chat intent를 복원한 경우도 모델의 `chat` 오판보다 우선할 수 있도록 `refined_route_recovers_explicit_intent()`를 추가했다.
  - `그거 완료했어`는 현재 task 후보로 복원되고, `서울 날씨 알려줘`는 task 후보에 빨려 들어가지 않고 weather 새 요청으로 복원되는 회귀 테스트를 추가했다.
  - 허용되지 않은 intent는 allowlist에 맞춰 `chat`으로 떨어지도록 기존 테스트 계약을 정리했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_refines_high_confidence_chat_for_clear_follow_up_candidate tests/test_router_agent.py::test_router_high_confidence_chat_refinement_does_not_steal_new_target_request tests/test_router_agent.py::test_router_refines_high_confidence_chat_for_pending_context_approval tests/test_router_agent.py::test_router_fallback_does_not_approve_pending_context_for_positive_prefixed_weather_request -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - non-chat route의 누락된 context_link 복원 보강

- 작업 이름: 라우터 모델이 intent는 맞췄지만 후속 대상 연결을 빠뜨린 경우 작업 후보를 다시 연결
- 진행상황: 완료
- 진행내용:
  - `그거 완료했어`처럼 명확한 후속 요청에서 모델이 `manage_task` intent는 맞히더라도 `context_link=none`과 빈 슬롯을 반환하면, task 에이전트가 대상 없는 요청을 받게 되는 위험을 확인했다.
  - `model_route_needs_context_refinement()`가 `chat`뿐 아니라 non-chat route에서도 `context_link=none`이고 후속 요청 신호가 있으면 fallback 후보 검사를 수행하도록 확장했다.
  - fallback 결과가 실제 작업 후보와 연결되는 경우에만 모델 route를 덮어써서, `새 할일 추가해줘` 같은 새 항목 생성 요청은 기존 후보에 잘못 연결하지 않도록 유지했다.
  - 모델이 `manage_task/context none`을 반환해도 `그거 완료했어`는 task 후보의 `task_id`로 복원되고, 새 할 일 생성 요청은 연결하지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_refines_model_intent_without_context_link_for_follow_up_candidate tests/test_router_agent.py::test_router_does_not_refine_model_intent_without_context_link_for_new_item_creation tests/test_router_agent.py::test_router_refines_high_confidence_chat_for_clear_follow_up_candidate -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - context_link none 잔여 linked_state 정규화

- 작업 이름: 연결 없음 route에 남은 linked_state_id/link_confidence가 실행 컨텍스트를 오염시키지 않도록 검증 강화
- 진행상황: 완료
- 진행내용:
  - `validate_route_context_link()`가 `context_link=none`이면서 `resolved_slots`가 남은 경우는 정리하지만, `linked_state_id`만 남은 route는 그대로 통과시킬 수 있음을 확인했다.
  - 실행 컨텍스트 생성 단계는 `route.linked_state_id`가 있으면 linked state를 로드하므로, `context_link=none` route에 잔여 ID가 남으면 새 요청인데도 이전 작업 상태가 에이전트/응답 컨텍스트에 들어갈 위험이 있었다.
  - `context_link=none`이면 `linked_state_id`, `link_confidence`, `resolved_slots`를 모두 정규화하도록 route validation을 보강했다.
  - 모델이 `context_link=none`인데 `linked_state_id`만 남긴 경우 이를 제거하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clears_resolved_slots_without_context_link tests/test_route_validation.py::test_validate_route_context_link_clears_linked_state_without_context_link -q`, `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 라우터 내부 행동 로그 메타데이터 보강

- 작업 이름: 성공한 라우팅 선택도 다음 턴 컨텍스트에서 참고할 수 있도록 연결 메타데이터 기록
- 진행상황: 완료
- 진행내용:
  - route validation 보정 로그는 조정된 필드를 남기지만, 라우터가 처음부터 잘 고른 경우의 내부 로그는 모델 reason 중심이라 `context_link`, `linked_state_id`, `resolved_slots` 같은 실제 연결 단서가 부족한 점을 확인했다.
  - `route_log_reason()`을 추가해 모델 라우팅과 휴리스틱 fallback 모두 `intent`, `context_link`, `linked_state_id`, `link_confidence`, `resolved_slots`, 검색 판단, reason을 한 줄로 남기도록 했다.
  - 모델 경로에서 `context_link=continue`, `linked_state_id`, `resolved_slots`가 내부 행동 로그에 기록되는 회귀 테스트를 추가했다.
  - 모델 실패 후 휴리스틱 fallback이 pending/cross-location 후보를 연결한 경우에도 같은 메타데이터가 로그에 남는지 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_agent_logs_model_route_context_metadata tests/test_router_agent.py::test_router_fallback_uses_pending_cross_location_confirmation_on_positive_reply -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 라우터 내부 행동 로그 길이 제한

- 작업 이름: 라우터 로그가 내부 행동 컨텍스트를 과도하게 차지하지 않도록 압축
- 진행상황: 완료
- 진행내용:
  - 라우터 로그에 `resolved_slots`, 검색 이유, 라우팅 reason을 함께 남기도록 보강한 뒤, 긴 슬롯 값이나 긴 reason이 내부 행동 컨텍스트의 제한 글자 수를 과도하게 소비할 수 있음을 확인했다.
  - `route_log_reason()`에 전체 길이 제한을 추가하고, prefix, `resolved_slots`, `search_reason`, `reason`을 각각 압축해 핵심 메타데이터는 유지하되 긴 값은 `[...]`로 줄이도록 했다.
  - 긴 route 로그에서도 `intent`, `context_link`, `linked_state_id`, `link_confidence`, `resolved_slots` 단서가 남고 전체 길이가 제한되는 회귀 테스트를 추가했다.
  - 기존 모델 라우팅 로그와 휴리스틱 fallback 로그의 메타데이터 테스트도 함께 확인했다.
  - `python3 -m pytest tests/test_router_agent.py::test_route_log_reason_compacts_long_values_but_keeps_core_metadata tests/test_router_agent.py::test_router_agent_logs_model_route_context_metadata tests/test_router_agent.py::test_router_fallback_uses_pending_cross_location_confirmation_on_positive_reply -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-06 - 응답용 내부 행동 컨텍스트 비공개화

- 작업 이름: 내부 라우팅/검증 로그가 최종 답변 말투에 새어 나오지 않도록 응답 컨텍스트 정리
- 진행상황: 완료
- 진행내용:
  - 라우터와 에이전트는 내부 로그 원문을 참고해야 하지만, 최종 응답 작성자에게 `agent=...`, `route_validation`, `model=...`, `*:result` 같은 기계적인 필드가 그대로 전달되면 사용자가 보는 답변에 섞일 위험이 있음을 확인했다.
  - `ExecutionContext.for_response()`에서는 내부 로그 원문 대신 `비공개 내부 참고` 섹션을 사용하도록 변경했다.
  - `response_safe_internal_action_context()`를 추가해 내부 로그의 핵심 reason/status/사용자 관련 값만 남기고, agent명·model명·내부 로그 이름은 응답용 컨텍스트에서 제거했다.
  - 에이전트 실행과 라우터 판단용 `for_agent()`, `for_router()`는 기존처럼 원문 내부 로그를 유지해 맥락 판단 성능을 보존했다.
  - 응답 컴포저와 실행 컨텍스트 테스트를 보강해 응답용 컨텍스트에는 `route_validation`, `agent=...`, `model=...`이 들어가지 않고, 메모/할 일 ID 같은 사용자 관련 단서는 유지되는지 확인했다.
  - `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 명시 ID 기반 잘못된 상태 연결 차단

- 작업 이름: 사용자 문장에 명시된 ID와 라우터가 연결한 작업 상태 ID가 다를 때 실행 전 차단
- 진행상황: 완료
- 진행내용:
  - 기존 실행 전 검증은 라우터의 `resolved_slots`가 연결 상태와 다른 경우는 잡았지만, 라우터가 슬롯을 비운 채 잘못된 `linked_state_id`만 연결하면 사용자 문장 속 `문서 9`, `할 일 9`, `메모 9` 같은 명시 ID와 연결 상태 ID 불일치를 직접 막지 못할 수 있음을 확인했다.
  - `explicit_text_id_mismatch_linked_state()`와 `explicit_ids_from_text()`를 추가해 사용자 문장의 메모/문서/할 일/알림 ID를 추출하고, 연결 상태의 slots/artifacts ID와 다르면 `context_link`를 제거하거나 모호한 후속 요청에서는 확인으로 전환하도록 했다.
  - `그 메모 30분 뒤 알림으로 등록해줘`의 `30분`처럼 시간 단위 숫자를 ID로 오인하지 않도록 ID 추출 정규식을 보강했다.
  - `문서 9 다시 분석해봐`가 문서 7 상태에 잘못 붙는 경우, `할 일 9 완료했어`가 할 일 3에 붙는 경우, `메모 9 수정해줘`가 메모 3에 붙는 경우를 모두 차단하는 회귀 테스트를 추가했다.
  - 기존의 `그 메모 30분 뒤 알림으로 등록해줘`처럼 이전 메모를 소스로 삼아 알림을 만드는 정상 후속 요청은 계속 연결되는지 라우팅 매트릭스로 확인했다.
  - `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 명시 텍스트 대상 기반 잘못된 상태 연결 차단

- 작업 이름: 사용자 문장에 새 지역·URL·검색어가 있는데 이전 작업 상태가 잘못 연결되는 경우 실행 전 차단
- 진행상황: 완료
- 진행내용:
  - 기존 검증은 `resolved_slots.location/query/url`이 연결 상태와 다른 경우는 막았지만, 라우터가 슬롯을 비운 채 이전 `원주 날씨`, `파이썬 비동기 검색`, 이전 URL 상태만 연결하면 새 요청과 과연결될 수 있음을 확인했다.
  - `explicit_text_target_mismatch_linked_state()`를 추가해 사용자 문장에서 명시 날씨 지역, URL, 검색어를 추출하고 연결 상태의 slots/artifacts 값과 다르면 실행 전 `context_link`를 제거하도록 했다.
  - `서울 날씨 어때`는 이전 `원주 날씨` 상태에 붙지 않게 막고, `거기 내일 날씨 어때`처럼 명확한 지역 대명사 후속 요청은 기존 지역을 이어쓰도록 추출기를 보수적으로 조정했다.
  - `https://new.example.com/article 이거 요약해줘`가 이전 URL 상태에 붙는 경우와 `OpenAI 최신 모델 검색해줘`가 이전 검색어 상태에 붙는 경우를 차단하는 회귀 테스트를 추가했다.
  - `OpenAI 다시 검색해줘`처럼 기존 검색어를 다시 검색하는 정상 retry 표현은 새 검색어로 오인하지 않도록 `다시/재/한 번 더` suffix를 정리했다.
  - `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - route validation 내부 로그 압축

- 작업 이름: 실행 전 검증 조정 로그가 내부 행동 컨텍스트를 과도하게 차지하지 않도록 압축
- 진행상황: 완료
- 진행내용:
  - route validation 로그는 `after.reason`을 포함해 왜 링크가 제거·수정됐는지 남기지만, 긴 `resolved_slots`나 긴 검색어/파일명/질문이 포함되면 내부 행동 컨텍스트 예산을 크게 소모할 수 있음을 확인했다.
  - `compact_route_validation_summary()`와 `compact_route_validation_value()`를 추가해 전체 route validation 로그와 각 필드 값을 따로 압축하도록 했다.
  - 단순 전체 문자열 자르기가 아니라 `resolved_slots`, `clarification_question`, `reason`을 각각 압축해 `context_link`, `linked_state_id`, 핵심 reason이 보존되도록 했다.
  - 긴 검색어가 포함된 route validation 조정 로그에서도 `context_link continue->none`, `linked_state_id 30->None`, `web query 불일치`가 내부 로그에 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment tests/test_cli.py::test_log_route_validation_if_changed_compacts_long_adjustment -q`, `python3 -m pytest tests/test_cli.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 에이전트 실행 결과 내부 로그 전체 길이 제한

- 작업 이름: 에이전트 실행 결과 로그가 내부 행동 컨텍스트를 과도하게 차지하지 않도록 최종 압축
- 진행상황: 완료
- 진행내용:
  - `*:result` 내부 행동 로그는 summary, slots, artifacts, warnings, next_actions를 개별 압축하지만, 여러 필드가 함께 길어지면 전체 reason이 내부 행동 컨텍스트 예산을 많이 차지할 수 있음을 확인했다.
  - `compact_internal_action_result_reason()`을 추가해 `internal_action_result_reason()`의 최종 문자열에도 길이 제한을 적용했다.
  - 전체 압축은 앞쪽의 `status`, summary, 핵심 slots를 보존하고 뒤쪽 tail도 일부 남겨 긴 로그에서도 후속 판단 단서가 사라지지 않도록 했다.
  - 긴 문서 분석 결과 로그에서도 `status=success`, `document_ids`, 파일명이 남고, 과도하게 긴 reason은 제한 길이 안으로 줄어드는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_logs_operation_result_for_future_context tests/test_bot_helpers.py::test_record_internal_action_result_compacts_long_result_reason tests/test_bot_helpers.py::test_compact_internal_action_result_reason_preserves_head_and_tail tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_agent_registry.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 라우터 작업 상태 후보 연결 기준 보강

- 작업 이름: 라우터가 이전 작업 상태를 새 요청과 혼동하지 않도록 후보별 연결 기준을 명시
- 진행상황: 완료
- 진행내용:
  - 기존 `최근 작업 상태 후보`는 subject, slots, actions 중심이라 라우터가 “어떤 경우에 이 후보를 이어도 되는지”와 “어떤 경우에는 새 요청으로 봐야 하는지”를 후보별로 직접 비교하기 어려울 수 있음을 확인했다.
  - `build_turn_state_context()`에 `summary`, `target_hints`, `link_guidance`를 추가해 각 후보의 결과 요약, 연결 대상 단서, 연결/차단 기준을 함께 전달하도록 했다.
  - `link_guidance`에는 명확한 후속 표현 또는 동일 대상일 때만 연결, 새 ID/지역/파일명/URL/검색어/주제가 있으면 연결 금지, 다른 위치 후보는 실행 전 사용자 확인 필요 같은 공통 정책을 후보별로 반복 명시했다.
  - `parse_state_candidates()`와 `StateCandidate`도 새 필드를 읽도록 보강해 라우터 휴리스틱이 subject 뒤의 새 필드를 오염된 subject로 잘못 읽지 않게 했다.
  - 구분자(`|`, `=`)가 포함된 사용자 값과 긴 문서 제목에서도 subject, summary, target_hints, link_guidance, slots가 각각 분리되어 유지되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 라우터 target_hints 기반 후보 매칭 적용

- 작업 이름: 작업 상태 후보의 대상 단서를 라우터 휴리스틱이 실제 매칭에 사용하도록 보강
- 진행상황: 완료
- 진행내용:
  - 이전 작업에서 `target_hints`, `summary`, `link_guidance`를 라우터 컨텍스트에 추가했지만, 휴리스틱 매칭은 여전히 subject, slots, artifacts 위주로 동작해 새 필드가 실제 후보 선택에 충분히 쓰이지 않을 수 있음을 확인했다.
  - `candidate_matches_current_message()`가 subject뿐 아니라 summary와 target_hints도 현재 사용자 메시지와 비교하도록 변경했다.
  - 후속 표현이 약하더라도 현재 문장에 후보의 명시 대상 단서가 직접 등장하면 후보 비교 단계까지 진행하도록 `context_aware_fallback_route()`의 조기 반환 조건을 보강했다.
  - `candidate_reference_text()`와 다른 위치 확인 질문 생성에서도 target_hints를 보조 참조 텍스트로 사용해 subject가 빈약한 후보도 사용자에게 더 구체적으로 안내하도록 했다.
  - `errors.pptx 다시 요약해줘`처럼 subject보다 파일명 target hint가 더 명확한 문장이 현재 위치 후보에 연결되고, 다른 위치 후보에서는 바로 실행하지 않고 확인으로 전환되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_context_builder.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 에이전트 실행 결과 로그에 라우팅 맥락 기록

- 작업 이름: 실제 에이전트 실행 결과와 연결된 route metadata를 내부 행동 로그에 함께 저장
- 진행상황: 완료
- 진행내용:
  - 주요 에이전트는 `resolved_slots`와 `linked_state`를 사용하지만, 내부 결과 로그에는 실행 당시의 `context_link`, `linked_state_id`, `link_confidence`, 라우터 복원 슬롯이 일관되게 남지 않아 다음 턴에서 왜 해당 작업이 선택됐는지 추적 단서가 약해질 수 있음을 확인했다.
  - `record_internal_action_result()`에 선택 인자 `execution_context`를 추가해 디스코드 메시지 처리와 CLI 실행 경로에서 마지막 실행 컨텍스트를 내부 결과 로그에 넘기도록 했다.
  - `internal_action_result_reason()`이 `context_link`, `linked_state_id`, `linked_intent`, `linked_subject`, `link_confidence`, 안전한 `resolved_slots`를 압축된 `route=` 필드로 기록하도록 했다.
  - `context_link=none`인 새 요청은 불필요한 route metadata를 남기지 않고, 연결된 후속 요청만 실행 맥락을 남기도록 제한했다.
  - `ignored` 같은 불필요한 슬롯은 내부 로그에 남지 않고, `pending_original_text`, `task_id` 같은 후속 판단 단서만 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_logs_operation_result_for_future_context tests/test_bot_helpers.py::test_record_internal_action_result_logs_execution_context_link tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_context_builder.py tests/test_response_composer.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 내부 행동 로그 위치 우선순위 보강

- 작업 이름: 현재 위치 내부 로그를 우선 보존하고 다른 위치 로그는 배경 참고로 명시
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그에 route metadata가 추가되면서 로그 한 줄이 길어졌고, 작은 컨텍스트 예산에서는 최신 다른 위치 로그가 현재 위치 핵심 로그를 밀어낼 수 있음을 확인했다.
  - `build_internal_action_context()`를 현재 위치 로그 우선, 다른 위치 로그 보조 순서로 구성하도록 변경했다.
  - `AgentLogStore.recent()`가 오래된 순서로 반환하는 것을 반영해, 각 위치 묶음은 별도로 뒤집어 최신순으로 출력하도록 정렬을 보정했다.
  - 각 내부 로그 행에 `location_priority`와 `context_policy`를 추가해 현재 위치 로그는 명확한 후속 요청일 때만 참고하고, 다른 위치 로그는 배경 참고이며 실행 전 확인이 필요하다는 정책을 행 단위로 명시했다.
  - 작은 `internal_action_context_max_chars`에서도 현재 위치 핵심 로그가 유지되고, 다른 위치 로그에는 `background_only_ask_before_execute_when_follow_up` 정책이 표시되는 회귀 테스트를 보강했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_orders_internal_action_logs_latest_first tests/test_context_builder.py::test_build_router_context_keeps_latest_internal_action_when_trimmed tests/test_context_builder.py::test_build_router_context_keeps_current_location_internal_logs_when_cross_location_is_newer -q`, `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_response_composer.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 대상 없는 위험 액션 자동 연결 방지

- 작업 이름: 짧은 삭제·수정 명령이 단일 최근 후보에 과하게 연결되지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 기존 라우터 fallback은 단일 최근 후보가 있고 `삭제해`, `수정해` 같은 액션만 있는 짧은 문장이 오면, 대명사나 명시 대상이 없어도 최근 후보에 연결할 수 있음을 확인했다.
  - `is_risky_action_only_follow_up()`을 추가해 삭제, 지우기, 수정, 변경, 연기, 복구 같은 위험 액션은 대상 없는 action-only 문장만으로는 후속 작업 연결이 충분하지 않다고 판단하도록 했다.
  - `그거 삭제해`, `메모 10 삭제해줘`, `병원 예약 완료했어`처럼 대명사·명시 ID·명시 제목이 있는 경우는 기존처럼 연결 가능하게 유지했다.
  - `완료했어`처럼 상대적으로 안전하고 자연스러운 단일 할 일 완료 후속 요청은 계속 최근 할 일에 연결되도록 기존 케이스를 보존했다.
  - `삭제해`가 최근 할 일을 임의 삭제하지 않고 `context_link=none`으로 남는 케이스와, `수정해`가 최근 메모를 임의 수정하지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_context_builder.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 모델 라우터 위험 액션 연결 검증 보강

- 작업 이름: 모델이 직접 반환한 `context_link`에도 대상 없는 위험 액션 방어 규칙 적용
- 진행상황: 완료
- 진행내용:
  - 이전 작업에서 fallback 라우터는 `삭제해`, `수정해` 같은 대상 없는 위험 action-only 문장을 최근 후보에 자동 연결하지 않게 했지만, 모델 라우터가 직접 `context_link=continue`와 `linked_state_id`를 반환하면 route validation 경로에서 통과할 수 있음을 확인했다.
  - `route_validation.text_action_is_supported()`에 `risky_action_only_text()` 검사를 추가해 모델 결과와 fallback 결과가 같은 안전 기준을 쓰도록 했다.
  - `삭제해`처럼 대상 없는 위험 액션은 linked state가 delete/update action을 지원하더라도 실행 전 링크를 제거한다.
  - `그거 삭제해`, `할 일 3 삭제해`, `메모 10 삭제해`처럼 대명사나 명시 ID/대상이 있는 경우는 기존 연결 또는 확인 흐름을 유지한다.
  - 모델이 `삭제해`를 최근 할 일 상태에 직접 연결해도 validation에서 제거되는 케이스와, `할 일 3 삭제해`는 명시 대상이 있으므로 유지되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_blocks_risky_action_only_link tests/test_route_validation.py::test_validate_route_context_link_keeps_explicit_target_risky_action_link tests/test_route_validation.py::test_validate_route_context_link_clarifies_incompatible_ambiguous_follow_up -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 버튼 승인 실행 결과 route metadata 보존

- 작업 이름: 버튼으로 후속 작업을 승인한 경우에도 실행 맥락을 결과 로그와 작업 상태에 남김
- 진행상황: 완료
- 진행내용:
  - 일반 메시지/CLI 실행 경로는 `record_internal_action_result()`에 `ExecutionContext`를 넘겨 route metadata를 내부 로그에 남기지만, Discord 버튼 승인으로 이어간 작업은 함수 경계상 실행 컨텍스트가 결과 로그에 직접 전달되지 않을 수 있음을 확인했다.
  - `attach_execution_context_metadata()`를 추가해 `OperationResult`에 `context_link`, `linked_state_id`, `linked_intent`, `linked_subject`, `link_confidence`, 안전한 `resolved_slots`를 slots/facts로 보존하도록 했다.
  - `handle_context_link_confirmation_button()`에서 버튼 승인 dispatch 결과에 `pending_original_text`와 실행 맥락 metadata를 함께 붙이도록 변경했다.
  - `INTERNAL_ACTION_CONTEXT_KEYS`에 route metadata 키를 추가해 버튼 승인 결과도 내부 행동 로그에서 다음 턴 라우터가 참고할 수 있게 했다.
  - 버튼 승인 결과에 route slots가 붙고, 원래 결과의 task_id 같은 실행 결과 슬롯도 유지되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_attach_execution_context_metadata_adds_route_slots_for_button_results tests/test_bot_helpers.py::test_record_internal_action_result_logs_execution_context_link -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_context_builder.py tests/test_response_composer.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 응답용 구조화 결과 route metadata 비공개 처리

- 작업 이름: 내부 route metadata가 사용자 답변 생성 입력에 직접 노출되지 않도록 필터링
- 진행상황: 완료
- 진행내용:
  - 버튼 승인 결과에 `context_link`, `linked_state_id`, `linked_intent`, `linked_subject`, `link_confidence`, `resolved_slots`를 보존하면서, 이 값들이 `OperationResult.to_prompt_text()`를 통해 응답 생성 모델의 "구조화된 실행 결과"에 직접 들어갈 수 있음을 확인했다.
  - `public_operation_result_for_response()`를 추가해 성공/일반 결과에서는 내부 route metadata 키를 facts/slots에서 제거한 뒤 응답 생성 모델에 전달하도록 했다.
  - `needs_input`, `confirm_required`, `clarify` 결과는 확인 질문과 버튼 처리에 필요한 pending 정보를 유지해야 하므로 기존 구조화 결과를 그대로 사용하도록 했다.
  - route metadata는 응답용 구조화 결과에서는 숨기되, `ExecutionContext.for_response()`의 비공개 내부 참고와 내부 행동 로그에는 계속 남아 다음 턴 라우팅 판단에 활용되도록 했다.
  - 성공 결과의 `task_id` 같은 사용자 관련 실행 결과는 유지되고, `context_link=continue`, `linked_state_id`, `resolved_slots` 같은 내부 route metadata는 응답 생성 입력에서 빠지는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_composer_hides_private_route_metadata_from_success_result tests/test_response_composer.py::test_response_composer_preserves_cross_location_clarification_as_question -q`, `python3 -m pytest tests/test_response_composer.py tests/test_bot_helpers.py tests/test_context_builder.py tests/test_cli.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 응답용 linked_state 안전 요약 적용

- 작업 이름: 연결된 이전 작업 상태의 내부 route metadata가 응답 컨텍스트에 직접 노출되지 않도록 축약
- 진행상황: 완료
- 진행내용:
  - 성공 결과의 facts/slots에서 route metadata를 제거해도, `ExecutionContext.for_response()`가 `linked_state.to_prompt_text()`를 그대로 포함하면 작업 상태 slots 안의 `context_link`, `linked_state_id`, `linked_intent`, `resolved_slots`가 응답 생성 입력에 다시 들어갈 수 있음을 확인했다.
  - `response_safe_turn_state_context()`를 추가해 응답용 linked state에는 state_id, intent, status, subject, summary, 사용자 의미가 있는 ID/제목/파일명/URL/시간 슬롯과 artifacts만 남기도록 했다.
  - 에이전트/라우터용 `for_agent()`는 기존처럼 원문 linked state를 유지해 실행 판단 성능을 보존하고, 사용자 응답용 `for_response()`만 안전 요약을 사용하도록 분리했다.
  - linked state slots에 route metadata가 포함되어 있어도 응답 컨텍스트에는 `task_id`와 `병원 예약` 같은 사용자 관련 단서만 남고, 내부 route metadata는 제거되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_hides_private_route_metadata_from_linked_state tests/test_response_composer.py::test_execution_context_response_keeps_resolved_slots_when_truncated -q`, `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_bot_helpers.py tests/test_cli.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 라우터 프롬프트 후보 필드 정합성 보강

- 작업 이름: 실제 작업 상태 후보 필드와 라우터 모델 지침을 일치시켜 target_hints/link_guidance 활용 강화
- 진행상황: 완료
- 진행내용:
  - `build_turn_state_context()`는 `summary`, `target_hints`, `link_guidance`를 제공하지만, 라우터 프롬프트의 후보 필드 설명은 subject, slots, artifacts 중심으로 남아 있어 모델 라우터가 새 단서를 충분히 활용하지 못할 수 있음을 확인했다.
  - 라우터 프롬프트의 상태 후보 형식에 `summary`, `target_hints`, `link_guidance`를 명시했다.
  - `target_hints`는 파일명, 제목, ID, 지역, URL처럼 현재 메시지와 직접 대조할 대상 단서이고, `link_guidance`는 후보별 연결/차단 조건이라는 설명을 추가했다.
  - 현재 메시지의 파일명·제목·지역·URL·ID가 `target_hints`와 강하게 일치하면 명시 대상 후보로 보되, `link_guidance`가 사용자 확인 또는 연결 금지를 말하면 그 지침을 우선하도록 지시했다.
  - 라우터 프롬프트 테스트가 새 필드 설명과 target_hints/link_guidance 사용 지침을 확인하도록 보강했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_agent_prefers_model_route_over_heuristic -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 명시 파일명 기반 잘못된 문서 연결 차단

- 작업 이름: 사용자 문장에 새 파일명이 있는데 모델이 이전 문서 상태를 잘못 연결하는 경우 실행 전 차단
- 진행상황: 완료
- 진행내용:
  - 기존 실행 전 검증은 문서 ID 불일치는 막았지만, `errors.pptx 다시 요약해줘`처럼 파일명만 명시된 요청을 모델이 `contract.pdf` 문서 상태에 연결하고 `resolved_slots`를 비우면 파일명 불일치를 직접 막지 못할 수 있음을 확인했다.
  - `explicit_document_filenames_from_text()`를 추가해 사용자 문장 안의 `.pdf`, `.docx`, `.pptx`, `.hwpx`, 이미지 등 지원 파일명 패턴을 추출하도록 했다.
  - `explicit_text_target_mismatch_linked_state()`가 document filename을 비교하도록 확장했다.
  - `collect_text_values_from_state()`가 linked_state의 `filename`, `filenames`, `title`, `subject`, artifact `filename/title/name`을 문서 대상 값으로 수집하도록 보강했다.
  - `errors.pptx 다시 요약해줘`가 `contract.pdf` 상태에 잘못 연결되면 validation에서 링크를 제거하고, `contract.pdf 다시 요약해줘`처럼 파일명이 일치하면 기존 링크를 유지하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_link_when_explicit_filename_is_only_in_text tests/test_route_validation.py::test_validate_route_context_link_keeps_link_when_explicit_filename_matches_text -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - 명시 제목 기반 잘못된 작업 연결 차단

- 작업 이름: 사용자 문장에 제목이 명시된 작업을 모델이 다른 최근 상태에 잘못 연결하는 경우 실행 전 차단
- 진행상황: 완료
- 진행내용:
  - 기존 실행 전 검증은 ID, 파일명, URL, 날씨 지역 같은 명시 대상은 막았지만, `장보기 삭제해줘`처럼 제목만 있는 요청을 모델이 `병원 예약` 할 일 상태에 연결하고 `resolved_slots`를 비우면 제목 불일치를 직접 막지 못할 수 있음을 확인했다.
  - `explicit_named_targets_from_text()`를 추가해 삭제, 수정, 완료, 조회, 요약 등 액션 앞의 명시 제목 후보를 보수적으로 추출하도록 했다.
  - `explicit_text_target_mismatch_linked_state()`가 named target을 linked_state의 subject, summary, title/name 계열 slots, artifact title/name/filename과 비교하도록 확장했다.
  - ID가 명시된 문장, 파일명이 명시된 문장, `그거`, `방금`, `아까`, `전에 하던거`, `여기서 이어서`, `두번째` 같은 후속 표현은 named target 추출에서 제외해 기존 확인/연결 흐름을 유지했다.
  - `장보기 삭제해줘`가 `병원 예약` 상태에 잘못 연결되면 validation에서 링크를 제거하고, 할 일 목록 상태에 `장보기` artifact가 있으면 링크를 유지하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_blocks_mismatched_named_task_target tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_named_task_target -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - subject-only 상태 명시 제목 연결 보존

- 작업 이름: artifact/title 없이 subject만 남은 작업 상태에서도 사용자가 말한 제목을 정확히 연결
- 진행상황: 완료
- 진행내용:
  - `subject="할 일 3 병원 예약"`처럼 상태 subject만 있고 artifact title이 없는 경우, 사용자의 `병원 예약 완료했어`가 named target 불일치로 잘못 차단될 수 있음을 확인했다.
  - `named_target_aliases_from_state_text()`를 추가해 `할 일 3`, `메모 8`, `알림 5`, `문서 7` 같은 상태 접두어와 ID를 제거한 사람이 말하는 제목 조각을 함께 비교하도록 했다.
  - 기존 전체 subject 값도 계속 보존해 내부 로그나 요약 상태가 다양한 형태로 들어와도 비교 단서가 사라지지 않게 했다.
  - artifact가 없는 할 일 상태의 `병원 예약 완료했어`와 artifact가 없는 메모 상태의 `운동 루틴 보여줘`가 올바르게 연결되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_named_target_from_subject_only tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_memory_target_from_subject_only tests/test_route_validation.py::test_validate_route_context_link_blocks_mismatched_named_task_target tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_named_task_target -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - subject-only 문서 파일명 연결 보존

- 작업 이름: artifact/title 없이 subject만 남은 문서 상태에서도 사용자가 말한 파일명을 정확히 연결
- 진행상황: 완료
- 진행내용:
  - `subject="문서 7 contract.pdf"` 또는 `subject="문서 linked.md"`처럼 문서 상태 subject만 있고 artifact filename/title이 없는 경우, 사용자의 `contract.pdf 다시 요약해줘`나 `linked.md 요약해줘`가 파일명 불일치로 잘못 차단될 수 있음을 확인했다.
  - `filename_aliases_from_state_text()`와 `filename_alias_variants()`를 추가해 subject/summary에서 파일명을 추출하고, `문서 7`, `파일`, `document` 같은 상태 접두어를 제거한 실제 파일명 alias도 비교하도록 했다.
  - 기존 전체 subject 기반 파일명 값도 유지해 긴 파일명이나 상태 요약 형태가 다양해도 비교 단서가 사라지지 않게 했다.
  - artifact가 없는 `문서 7 contract.pdf`와 `문서 linked.md` 상태에서 명시 파일명 요청이 올바르게 연결되는 회귀 테스트를 추가했다.
  - `errors.pptx 다시 요약해줘`처럼 다른 파일명이 명시된 요청은 계속 기존 문서 상태에 연결되지 않도록 기존 차단 테스트를 함께 확인했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_filename_from_subject_only tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_filename_without_id_from_subject_only tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_link_when_explicit_filename_is_only_in_text tests/test_route_validation.py::test_validate_route_context_link_keeps_link_when_explicit_filename_matches_text -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - subject-only 날씨 지역 연결 검증 보강

- 작업 이름: 슬롯이나 artifact 없이 subject만 남은 날씨 상태에서도 지역 일치 여부를 정확히 판단
- 진행상황: 완료
- 진행내용:
  - `subject="원주 날씨 조회"`처럼 날씨 상태 subject만 있고 `location` slot/artifact가 없는 경우, 사용자의 `서울 날씨 어때` 같은 새 지역 요청을 이전 원주 날씨 상태에 잘못 연결하거나, 반대로 `원주 날씨 다시 확인해줘`를 named target 불일치로 잘못 차단할 수 있음을 확인했다.
  - `explicit_named_targets_from_text()`가 날씨 지역 표현을 제목 후보로 보지 않도록 해 `원주 날씨`가 named target 검증에서 오인되지 않게 했다.
  - `weather_location_aliases_from_state_text()`를 추가해 subject/summary의 `원주 날씨 조회`, `서울특별시 미세먼지` 같은 표현에서 지역 alias를 추출하고 location 검증에 사용하도록 했다.
  - subject-only 원주 날씨 상태에서 `서울 날씨 어때`는 차단되고, `원주 날씨 다시 확인해줘`는 유지되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_weather_link_from_subject_only_location tests/test_route_validation.py::test_validate_route_context_link_keeps_weather_link_from_subject_only_location tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_weather_link_when_new_location_is_only_in_text tests/test_route_validation.py::test_validate_route_context_link_blocks_mismatched_named_task_target -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - subject-only 웹검색 쿼리 연결 검증 보강

- 작업 이름: 슬롯이나 artifact 없이 subject만 남은 웹검색 상태에서도 검색어 일치 여부를 정확히 판단
- 진행상황: 완료
- 진행내용:
  - `subject="OpenAI 모델 검색"`처럼 웹검색 상태 subject만 있고 `query` slot/artifact가 없는 경우, 사용자의 `파이썬 비동기 검색해줘` 같은 새 검색어 요청이 이전 OpenAI 검색 상태에 잘못 연결될 수 있음을 확인했다.
  - `search_query_aliases_from_state_text()`를 추가해 subject/summary의 `OpenAI 모델 검색`, `파이썬 비동기 찾아` 같은 표현에서 실제 검색어 alias를 추출하고 query 검증에 사용하도록 했다.
  - `다시 검색해줘`처럼 검색어 없는 후속 표현은 기존 `explicit_search_queries_from_text()` 규칙에 따라 alias로 만들지 않아 과연결을 피하도록 했다.
  - subject-only OpenAI 검색 상태에서 `파이썬 비동기 검색해줘`는 차단되고, `OpenAI 모델 다시 검색해줘`는 유지되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_search_link_from_subject_only_query tests/test_route_validation.py::test_validate_route_context_link_keeps_search_link_from_subject_only_query tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_search_link_when_new_query_is_only_in_text tests/test_route_validation.py::test_validate_route_context_link_clears_cross_location_old_search_for_new_query -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - subject-only URL 연결 검증 보강

- 작업 이름: 슬롯이나 artifact 없이 subject만 남은 URL 분석 상태에서도 URL 일치 여부를 정확히 판단
- 진행상황: 완료
- 진행내용:
  - `subject="URL https://example.com/article 분석"`처럼 URL 상태 subject만 있고 `url` slot/artifact가 없는 경우, 같은 URL 재요약 요청이 named target 불일치로 잘못 차단되고, 새 URL 요청도 URL 전용 검증 전에 부정확하게 처리될 수 있음을 확인했다.
  - `explicit_named_targets_from_text()`가 URL이 포함된 문장을 제목 후보로 보지 않도록 해 URL 요청은 URL 전용 검증에서 처리되게 했다.
  - `url_aliases_from_state_text()`를 추가해 subject/summary에 들어 있는 URL을 추출하고 `url`, `urls` 검증에 모두 사용하도록 했다.
  - subject-only URL 상태에서 `https://example.com/article 다시 요약해줘`는 유지되고, `https://new.example.com/article 요약해줘`는 차단되는 회귀 테스트를 추가했다.
  - 기존처럼 같은 path라도 query string이 다르면 다른 URL로 판단하는 검증도 함께 확인했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_keeps_url_link_from_subject_only_url tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_url_link_from_subject_only_url tests/test_route_validation.py::test_validate_route_context_link_clears_artifact_url_for_new_url_request tests/test_route_validation.py::test_validate_route_context_link_clears_same_path_different_query_url_request tests/test_route_validation.py::test_validate_route_context_link_keeps_equivalent_artifact_url_request -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - subject-only 리마인더 제목 연결 회귀 고정

- 작업 이름: artifact/title 없이 subject만 남은 리마인더 상태에서 명시 제목 연결과 차단을 검증
- 진행상황: 완료
- 진행내용:
  - `subject="알림 5 물 마시기"`처럼 리마인더 상태 subject만 있고 artifact title이 없는 경우에도 기존 named target alias 규칙이 `물 마시기`를 올바르게 이어받고, `병원 예약` 같은 다른 제목은 차단함을 확인했다.
  - 삭제 계열 리마인더 요청은 잘못 연결되면 사용자에게 직접 피해가 생길 수 있으므로, 현재 동작을 회귀 테스트로 고정했다.
  - `물 마시기 삭제해줘`는 subject-only 알림 상태에 연결되고, `병원 예약 삭제해줘`는 같은 알림 상태에 연결되지 않는 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_reminder_target_from_subject_only tests/test_route_validation.py::test_validate_route_context_link_blocks_mismatched_reminder_target_from_subject_only tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_named_target_from_subject_only tests/test_route_validation.py::test_validate_route_context_link_blocks_mismatched_named_task_target -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - subject-only 명시 ID 연결 검증 보강

- 작업 이름: slots/artifacts 없이 subject만 남은 상태에서도 명시 ID 일치 여부를 정확히 판단
- 진행상황: 완료
- 진행내용:
  - `subject="문서 7 contract.pdf"`, `subject="할 일 3 병원 예약"`, `subject="메모 8 운동 루틴"`, `subject="알림 5 물 마시기"`처럼 상태 subject만 있고 ID slots/artifacts가 없는 경우, 사용자의 `문서 9 다시 분석해봐`, `할 일 9 완료했어`, `메모 9 보여줘`, `알림 9 삭제해줘`가 잘못 연결될 수 있음을 확인했다.
  - `collect_ids_from_state()`를 추가해 ID 비교 시 slots, artifacts뿐 아니라 subject/summary의 명시 ID도 함께 수집하도록 했다.
  - `explicitly_mentions_linked_state_id()`, `explicit_text_id_mismatch_linked_state()`, `resolved_slots_mismatch_linked_state()`가 모두 같은 state ID 수집 규칙을 사용하도록 정리했다.
  - subject-only 상태에서 문서, 할 일, 메모, 알림 ID가 다르면 차단되고, 같은 ID면 연결이 유지되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_blocks_mismatched_id_from_subject_only_state tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_id_from_subject_only_state tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_task_and_memory_links_from_text_id tests/test_route_validation.py::test_validate_route_context_link_keeps_link_when_explicit_document_id_matches_text -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-06 - subject-only cross-location 확인 슬롯 보존

- 작업 이름: 다른 대화 위치의 subject-only 상태를 이어갈지 확인할 때 승인 후 실행 슬롯이 비지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 채팅 위치가 바뀐 경우 기존처럼 사용자 확인은 요구하지만, linked_state가 `subject="문서 7 contract.pdf"`처럼 subject-only 상태이고 route의 `resolved_slots`가 비어 있으면 `pending_resolved_slots`도 비어 버튼 승인 후 실행 대상이 흐려질 수 있음을 확인했다.
  - `enrich_resolved_slots_from_linked_state()`를 추가해 cross-location 확인으로 바뀌는 순간 linked_state의 subject/summary, slots, artifacts에서 안전하게 추출 가능한 실행 슬롯을 보강하도록 했다.
  - 문서/할 일/메모/알림 ID, 날씨 location, 웹검색 query, URL 분석 url을 보강 대상으로 삼고, 이미 route가 슬롯을 갖고 있으면 기존 값을 우선하도록 했다.
  - subject-only 상태에서 문서, 할 일, 날씨, 웹검색, URL 작업이 다른 대화 위치에서 확인 대기로 바뀔 때 `resolved_slots`가 실행 가능한 형태로 보존되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_enriches_cross_location_slots_from_subject_only_state tests/test_route_validation.py::test_validate_route_context_link_clarifies_cross_location_link_before_execution tests/test_route_validation.py::test_validate_route_context_link_allows_cross_location_link_after_approval -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - subject-only cross-location 승인 대기 슬롯 통합 검증

- 작업 이름: 다른 대화 위치 subject-only 상태의 보강 슬롯이 bot 응답의 pending 슬롯까지 이어지는지 검증
- 진행상황: 완료
- 진행내용:
  - route validation 단계에서 subject-only 상태의 실행 슬롯을 보강하더라도, 실제 `AssistantBot.handle_message()`가 만든 확인 대기 결과의 `pending_resolved_slots`에 들어가지 않으면 버튼 승인 후 실행 대상이 다시 흐려질 수 있음을 점검했다.
  - 모델 라우터가 다른 위치의 문서 상태에 `linked_state_id`만 주고 `resolved_slots`를 비우는 상황을 재현하는 `FakeCrossLocationContinueWithoutSlotsRouter`를 추가했다.
  - 다른 위치의 `subject="문서 7 contract.pdf"` 상태가 slots/artifacts 없이 저장되어 있어도, 현재 위치에서 `문서 7 다시 분석해봐` 요청을 받으면 바로 실행하지 않고 확인 대기로 전환하며 `pending_resolved_slots={"document_id": 7}`을 보존하는 통합 테스트를 추가했다.
  - 응답 생성용 execution context에도 보강된 `document_id`가 들어가고, 확인 전에는 agent dispatch가 호출되지 않음을 함께 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_enriches_cross_location_pending_slots_from_subject_only_state tests/test_bot_helpers.py::test_assistant_bot_clarifies_model_cross_location_continue_before_dispatch tests/test_route_validation.py::test_validate_route_context_link_enriches_cross_location_slots_from_subject_only_state -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 승인 오인 방지 회귀 고정

- 작업 이름: 확인 대기 중 긍정어와 새 명시 대상 요청이 섞인 문장을 승인으로 오인하지 않도록 검증
- 진행상황: 완료
- 진행내용:
  - 확인 대기 상태에서 사용자가 `응 문서 9 다시 분석해줘`, `응 문서 7 다시 분석해줘`처럼 긍정어와 새 요청을 함께 보내면 이를 단순 승인으로 처리하면 안 됨을 점검했다.
  - 현재 `matching_pending_context_approval_state()`는 approval text 판정, route slot 충돌, pending original text 검증을 통해 이런 문장을 승인으로 받아들이지 않음을 확인했다.
  - `응 문서 9 다시 분석해줘`가 다른 문서 ID를 포함할 때, 같은 문서 ID를 포함하더라도 새 요청 문장일 때, route 슬롯이 비어 있어도 새 명시 요청일 때 모두 pending 승인으로 매칭되지 않는 회귀 테스트를 추가했다.
  - 기존의 순수 승인 표현인 `응 처리해줘`는 계속 승인으로 받아들여지는지도 함께 확인했다.
  - `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_rejects_positive_text_with_explicit_new_target_request tests/test_route_validation.py::test_pending_context_approval_rejects_extra_route_slot tests/test_route_validation.py::test_pending_context_approval_still_accepts_plain_positive_action -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 거절 표현과 새 요청 혼합 통합 검증

- 작업 이름: 확인 대기 중 `아니 취소 말고 ...` 형태의 새 요청을 cancel_pending으로 오인하지 않도록 검증
- 진행상황: 완료
- 진행내용:
  - route/router 레벨에서는 `아니 취소 말고 서울 날씨 알려줘`가 cancel_pending으로 가지 않는 테스트가 있었지만, 실제 `AssistantBot.handle_message()`에서 pending 상태가 존재할 때 새 요청 dispatch까지 이어지는지 추가로 점검했다.
  - `FakeWeatherRouter`를 추가해 pending context 상태가 있는 상황에서 라우터가 `weather/context_link=none` 새 요청을 반환하는 흐름을 재현했다.
  - `아니 취소 말고 서울 날씨 알려줘`가 pending 취소로 처리되지 않고 weather dispatch로 진행되며, 기존 pending context state는 새 요청 라우팅으로 만료되는 통합 테스트를 추가했다.
  - 순수 거절 표현인 `아니 하지마`는 여전히 cancel_pending으로 처리되는 기존 테스트와 함께 확인했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_routes_negative_prefixed_new_request_instead_of_cancel_pending tests/test_bot_helpers.py::test_assistant_bot_cancels_pending_context_link_and_expires_state -q`, `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q -k 'negative_prefix_weather_request_not_pending_cancel or pending_context_rejection_cancels_latest_pending'`, `python3 -m pytest tests/test_router_agent.py::test_router_fallback_does_not_cancel_pending_context_for_negative_prefixed_web_request tests/test_router_agent.py::test_router_fallback_does_not_cancel_pending_context_for_negative_prefixed_generic_request -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 승인 슬롯 단수/복수 동등성 보강

- 작업 이름: 같은 대상 ID가 단수/복수 슬롯 키 차이만으로 pending 승인에서 거절되지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - pending 확인 상태가 `document_id=7`을 갖고 있는데 승인 라우트가 `document_ids=[7]`을 반환하거나, 반대로 `task_ids=[3]`과 `task_id=3`처럼 같은 대상인데 슬롯 키 형태만 다르면 기존 비교가 충돌로 판단할 수 있음을 확인했다.
  - `equivalent_pending_slot_key()`와 `slot_values_equivalent()`를 추가해 task, memory, document, reminder ID 계열은 단수/복수 키를 같은 ID 집합으로 비교하도록 했다.
  - 일반 슬롯은 기존처럼 엄격히 비교하고, ID 집합이 다르거나 route에 pending에 없는 추가 슬롯이 있으면 계속 승인 매칭을 거절하도록 유지했다.
  - 할 일, 메모, 문서, 알림의 단수/복수 ID 슬롯이 같은 대상을 가리키면 승인 매칭되고, 다른 ID는 거절되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_accepts_equivalent_singular_plural_id_slots tests/test_route_validation.py::test_pending_context_approval_rejects_different_singular_plural_id_slots tests/test_route_validation.py::test_pending_context_approval_rejects_extra_route_slot tests/test_route_validation.py::test_pending_context_approval_enriches_missing_resolved_slots -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 승인 문자열 슬롯 정규화 비교 보강

- 작업 이름: 같은 URL·검색어·지역이 표현 차이만으로 pending 승인에서 거절되지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - pending 확인 상태가 `url=https://example.com/article`를 갖고 있는데 승인 라우트가 `https://EXAMPLE.com/article/`처럼 대소문자나 trailing slash만 다른 URL을 반환하면 기존 문자열 비교가 충돌로 판단할 수 있음을 확인했다.
  - `slot_values_equivalent()`가 URL, query, location, filename, title 계열 슬롯은 기존 정규화 함수로 비교하도록 변경했다.
  - `url`과 `urls`도 단수/복수 키 동등성 대상에 포함해 같은 URL 집합이면 승인 매칭되도록 했다.
  - 같은 URL, 같은 검색어의 대소문자 차이, 같은 지역은 승인 매칭되고, 다른 URL·검색어·지역은 계속 거절되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_accepts_equivalent_normalized_text_slots tests/test_route_validation.py::test_pending_context_approval_rejects_different_normalized_text_slots tests/test_route_validation.py::test_pending_context_approval_accepts_equivalent_singular_plural_id_slots tests/test_route_validation.py::test_pending_context_approval_rejects_different_singular_plural_id_slots -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 승인 실행 슬롯 보존 보강

- 작업 이름: 확인 승인 후 실행 단계에서 pending 대상 슬롯이 route 표기 차이로 흔들리지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - pending 승인 매칭은 `document_id=7`과 `document_ids=[7]`, `url=https://example.com/article`와 `https://EXAMPLE.com/article/`를 같은 대상으로 받아들이지만, 승인 후 `route_with_pending_context_values()`가 같은 키의 route 값을 다시 덮어쓰면 실행 컨텍스트의 표기와 슬롯 형태가 흔들릴 수 있음을 확인했다.
  - `route_with_pending_context_values()`가 pending 확인 상태에 저장된 `pending_resolved_slots`를 실행 슬롯의 기준값으로 보존하도록 변경했다.
  - 단수 pending 슬롯인 `document_id`가 route의 `document_ids`와 매칭된 뒤에도 실행 슬롯에는 `document_id`만 남고, 정규화된 pending URL도 route의 대소문자/trailing slash 표현에 덮이지 않도록 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py -q`, `python3 -m pytest tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 내부 행동 기록 라우팅 힌트 보강

- 작업 이름: 사용자에게 보이지 않는 내부 행동 기록을 라우터가 더 안정적으로 참고하도록 구조화 힌트 추가
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록은 라우터 컨텍스트에 포함되어 있었지만 `reason=...` 문자열 안에 summary, subject, slots, artifacts, route 값이 섞여 있어 라우터가 현재 메시지와 연결 가능한 단서인지 배경 정보인지 판단하기 어렵다는 점을 점검했다.
  - `build_internal_action_context()`가 내부 행동 기록마다 `target_hints`와 `link_guidance`를 함께 출력하도록 보강했다.
  - `summary`, `subject`, `slots`, `artifacts`, `route`에 들어 있는 문서/메모/할 일/알림 ID, 파일명, 제목, URL, 검색어, 지역 같은 값을 안전하게 추출해 target hint로 제공한다.
  - 내부 행동 기록의 guidance에는 “보조 단서”, “명확한 후속 표현이나 같은 대상일 때만 참고”, “새 대상이 명시되면 연결 금지”, “다른 위치 기록은 확인 후 사용” 원칙을 명시했다.
  - 라우터 컨텍스트 테스트와 실제 `record_internal_action_result()`로 남긴 결과가 다음 라우터 컨텍스트의 target hint로 이어지는 통합 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py::test_record_internal_action_result_logs_operation_result_for_future_context tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots tests/test_bot_helpers.py::test_record_internal_action_result_logs_execution_context_link -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 내부 행동 힌트의 휴리스틱 라우터 활용 보강

- 작업 이름: 모델 라우팅 실패·모호 응답 시 내부 행동 기록의 target hint를 기존 작업 상태 후보에 병합
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록은 라우터 프롬프트에는 들어가지만, 휴리스틱 fallback은 `state_id=`가 있는 최근 작업 상태 후보만 파싱하고 내부 행동 기록 라인의 target hint는 활용하지 못하는 점을 확인했다.
  - 내부 행동 기록을 독립 실행 후보로 만들면 실제 turn state 검증이 어려워질 수 있으므로, `route.linked_state_id`가 기록된 내부 로그만 같은 state_id의 기존 후보에 보조 target hint로 병합하도록 구현했다.
  - `parse_state_candidates()`가 내부 행동 기록의 `linked_state_id`와 `target_hints`를 읽어 기존 `StateCandidate.target_hints`에 중복 없이 추가한다.
  - 예를 들어 작업 상태 후보 subject가 일반적인 “문서 분석 결과”뿐이어도, 내부 실행 로그에 `linked_state_id=21`, `contract.pdf` 힌트가 남아 있으면 `contract.pdf 다시 요약해줘`를 해당 문서 상태로 연결할 수 있게 했다.
  - `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 내부 행동 힌트 숫자 오연결 방지 보강

- 작업 이름: 내부 행동 기록에서 나온 숫자 target hint가 새 시간·알림 요청을 기존 문서/작업 후속으로 오인하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록의 `target_hints`에 `7` 같은 순수 숫자 값이 병합되면 `7시에 다시 알려줘`처럼 새 알림 요청의 시간 표현을 기존 `문서 7` 후속 요청으로 오인할 수 있는 위험을 확인했다.
  - 내부 행동 기록의 `route.resolved_slots`를 파싱해 `document_id`, `memory_id`, `task_id`, `reminder_id`, `location`, `url`, `query`, `filename` 같은 안전 슬롯은 기존 `StateCandidate.slots`에 병합하도록 했다.
  - 순수 숫자 target hint는 target hint 병합에서 제외하고, ID 매칭은 슬롯/아티팩트의 kind-aware 비교(`문서 7`, `메모 7`처럼 종류가 명시된 경우)로만 처리되도록 했다.
  - `contract.pdf 다시 요약해줘`는 내부 힌트로 계속 연결되지만, `7시에 다시 알려줘`는 문서 7 후속으로 빼앗기지 않고 새 알림 요청으로 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 내부 행동 linked_state_id 오인 파싱 방지

- 작업 이름: 내부 로그의 `pending_linked_state_id`·`cancelled_pending_linked_state_id`를 실제 실행 연결 상태로 오인하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 내부 행동 힌트를 기존 작업 상태 후보에 병합할 때 단순 정규식으로 `linked_state_id`를 찾으면 `cancelled_pending_linked_state_id` 같은 필드도 실제 연결 대상처럼 잡힐 수 있음을 확인했다.
  - `parse_internal_action_linked_state_id()`가 내부 로그 전체 문자열을 직접 검색하지 않고, `route={...}` 딕셔너리 안의 실제 `linked_state_id`만 파싱하도록 변경했다.
  - route 딕셔너리가 없는 취소/거절 로그에 `cancelled_pending_linked_state_id=21`과 `contract.pdf` 힌트가 있어도, 기존 문서 상태 후보에 해당 힌트가 병합되지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 내부 복원 문서 슬롯의 검증 단계 보존

- 작업 이름: 내부 행동 로그로 복원한 문서 슬롯이 실행 전 링크 검증에서 일반 subject 문자열과 충돌하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 라우터가 내부 행동 로그에서 `document_id=7`, `contract.pdf` 힌트를 복원해도, `validate_route_context_link()`가 linked state의 일반 subject인 `문서 분석 결과`를 filename 값으로 취급하면 사용자 문장의 `contract.pdf`와 불일치한다고 판단해 연결을 제거할 수 있음을 확인했다.
  - `collect_text_values_from_state()`의 filename 계열 수집에서 subject 원문 전체를 파일명 후보로 넣지 않도록 수정했다.
  - 실제 파일명은 `filename`/`filenames` 슬롯, title 슬롯, artifacts, subject/summary 안의 파일명 패턴(`*.pdf`, `*.pptx` 등)으로만 수집되도록 유지했다.
  - linked state에 충돌 대상이 없으면 내부 로그로 복원된 `document_id` route 슬롯을 보존하고, linked state가 명확히 다른 문서 ID를 갖고 있으면 계속 제거하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 실행 슬롯 없는 내부 힌트 병합 방지

- 작업 이름: 내부 행동 로그가 실행 가능한 슬롯 없이 target hint만 가진 경우 라우터 후보를 강화하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그에 `route.linked_state_id`와 `contract.pdf` target hint는 있지만 `resolved_slots`가 없으면, 라우터가 문서 후보를 선택하더라도 실제 실행에 필요한 문서 ID가 빈 상태로 넘어갈 수 있음을 확인했다.
  - `internal_action_context_by_linked_state()`가 `document_id`, `memory_id`, `task_id`, `reminder_id`, `location`, `url`, `query`, `filename` 등 안전한 실행 슬롯을 하나 이상 복원할 수 있을 때만 target hint도 병합하도록 변경했다.
  - 실행 슬롯이 없는 내부 로그의 `contract.pdf` 힌트만으로는 `contract.pdf 다시 요약해줘`를 기존 상태에 연결하지 않는 회귀 테스트를 추가했다.
  - 기존처럼 `resolved_slots={'document_id': 7}`이 함께 있는 내부 로그는 `contract.pdf` 힌트와 문서 ID를 정상 병합하고, 숫자/취소 로그 오연결 방지 테스트도 함께 유지했다.
  - `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 다른 위치 내부 힌트 확인 질문 대상명 보강

- 작업 이름: 다른 채팅 위치의 내부 행동 힌트로 매칭된 작업을 확인할 때 사용자에게 더 정확한 대상명을 보여주도록 보강
- 진행상황: 완료
- 진행내용:
  - 다른 위치의 작업 상태 subject가 `문서 분석 결과`처럼 일반적이고, 내부 행동 로그 target hint가 `contract.pdf`처럼 실제 매칭 대상인 경우에도 확인 질문은 기존 subject를 그대로 사용할 수 있음을 확인했다.
  - `candidate_reference_text_for_message()`를 추가해 현재 사용자 문장과 실제로 매칭된 artifact/title/filename/url 또는 target hint를 우선 대상명으로 고르도록 했다.
  - `clarify_cross_location_candidate()`가 일반 subject만 담긴 suggested question보다 현재 메시지와 맞는 대상명을 우선 사용하도록 변경했다.
  - 단, 기존 suggested question이 `Errors in C 발표자료`처럼 구체적인 후보 힌트를 이미 담고 있으면 기존 문구를 유지해 더 좋은 제목을 덮어쓰지 않도록 했다.
  - `contract.pdf 다시 요약해줘`가 다른 위치 내부 힌트로 매칭될 때 확인 질문에 `contract.pdf`가 들어가는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 복원 문서 슬롯의 에이전트 실행 컨텍스트 전달 보강

- 작업 이름: 내부 행동 힌트로 복원된 문서 슬롯이 봇 통합 실행 직전까지 보존되도록 검증 및 호환성 보강
- 진행상황: 완료
- 진행내용:
  - route validation 단독으로는 `document_id` 복원 슬롯이 보존되지만, 봇 통합 흐름에서는 `recall`이 `analyze_document` 상태를 이어받는 경우 `보여줘` 액션이 문서 분석 상태의 actions에 없다는 이유로 context_link가 제거될 수 있음을 확인했다.
  - `text_action_is_supported()`에서 `recall`이 `analyze_document` 상태를 이어받는 경우 recall 계열 조회 액션(`show`, `recall`, `summarize`, `continue`)도 지원 액션으로 인정하도록 보강했다.
  - linked state가 일반 subject와 빈 slots/artifacts만 갖고 있어도 라우터가 복원한 `document_id`가 `AgentContext.execution.resolved_slots`로 dispatch 직전까지 전달되는 통합 테스트를 추가했다.
  - 실행 컨텍스트의 `for_agent()`에도 라우터 복원 슬롯이 포함되어 에이전트가 다음 행동과 답변에 참고할 수 있음을 함께 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 구조화 값 없는 내부 검증 로그의 target hint 제외

- 작업 이름: route validation 조정 로그 같은 긴 내부 reason이 라우터 대상 힌트로 오인되지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록의 `reason`에 구조화된 summary/subject/slots/artifacts/route 값이 없을 때, 기존 fallback이 전체 reason 문자열을 target hint로 넣을 수 있음을 확인했다.
  - 특히 `route_validation` 조정 로그는 “context_link continue->none ...” 같은 긴 내부 설명을 담는데, 이 값은 내부 참고로는 유용하지만 사용자 대상 매칭 힌트로 쓰면 오연결과 컨텍스트 노이즈를 만들 수 있다.
  - `internal_action_target_hints()`에서 구조화 값이 없을 때 reason 전체를 target hint로 추가하던 fallback을 제거했다.
  - 구조화된 작업 결과 로그는 기존처럼 summary, subject, slots, artifacts, route에서 target hint를 생성하고, 검증/라우팅 판단 로그는 reason만 참고 정보로 남기며 `target_hints=-`로 표시되도록 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 내부 행동 ID 힌트 타입 표기 보강

- 작업 이름: 내부 행동 기록의 순수 숫자 ID 힌트를 타입 있는 대상 힌트로 변환
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록 target hint에 `7`, `3` 같은 순수 숫자가 그대로 들어가면 모델 라우터가 시간/수량 표현과 ID를 혼동할 수 있음을 점검했다.
  - `add_internal_action_target_hints()`가 ID 계열 키를 별도 처리하도록 바꾸어 `document_id=7`은 `문서 7`, `task_id=3`은 `할 일 3`, `memory_id`는 `메모 N`, `reminder_id`는 `알림 N` 형태로 target hint를 만들도록 했다.
  - 내부 행동 기록의 일반 문자열 힌트에서는 순수 숫자만 단독으로 target hint에 넣지 않도록 했다.
  - 문서 작업 결과 로그의 target hint는 `문서 분석 완료`, `문서 7 contract.pdf`, `문서 7`, `contract.pdf`처럼 표시되고, 할 일 결과 로그는 `할 일 3 완료`, `할 일 3`처럼 표시되도록 테스트 기대값을 갱신했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 최근 작업 상태 ID 힌트 타입 표기 보강

- 작업 이름: 최근 작업 상태 후보의 순수 숫자 ID target hint를 타입 있는 표현으로 변환
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록뿐 아니라 `최근 작업 상태 후보`의 `target_hints`에도 슬롯/아티팩트 ID가 `7`, `3`처럼 순수 숫자로 들어가 모델 라우터와 휴리스틱 라우터 모두에서 시간/수량 표현과 헷갈릴 수 있음을 확인했다.
  - `turn_state_target_hints()`가 `document_id`, `task_id`, `memory_id`, `reminder_id` 계열 슬롯과 artifact ID를 각각 `문서 N`, `할 일 N`, `메모 N`, `알림 N` 형태로 출력하도록 변경했다.
  - location/query/url/filename 같은 비 ID 힌트는 유지하되, 순수 숫자만 단독으로 들어오는 값은 target hint에 추가하지 않도록 했다.
  - cross-location 문서 후보는 `문서 7`, 작업 후보는 `할 일 3`처럼 표시되도록 context builder 테스트 기대값을 갱신했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 비 ID 경로 정수 target hint 제외

- 작업 이름: 타입을 알 수 없는 artifact ID나 비 ID 슬롯 값이 순수 숫자 target hint로 노출되지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - ID 계열 슬롯은 타입 있는 힌트로 바뀌었지만, `kind=external` 같은 타입 미확정 artifact의 `id=7`이나 비 ID 경로의 정수 값은 여전히 `7`로 target hint에 들어갈 수 있음을 점검했다.
  - `add_non_numeric_target_hint()`가 문자열 숫자뿐 아니라 `int`, `float`, `bool` 값도 target hint로 추가하지 않도록 변경했다.
  - 타입이 확실한 memory/document/task/reminder ID는 기존처럼 `메모 N`, `문서 N`, `할 일 N`, `알림 N` 형태로 유지된다.
  - 타입 미확정 external artifact의 `id=7`은 target hint에서 제외되고 subject/summary 같은 의미 있는 텍스트만 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 타입 있는 ID 힌트 라우터 매칭 검증

- 작업 이름: `문서 7` 형태 target hint가 명시 문서 요청에는 매칭되고 시간 표현에는 매칭되지 않는지 검증
- 진행상황: 완료
- 진행내용:
  - 최근 작업 상태 후보와 내부 행동 기록의 ID 힌트를 `문서 7`, `할 일 3`처럼 타입 있는 표현으로 바꾼 뒤, 라우터 매칭이 의도대로 동작하는지 직접 검증했다.
  - `target_hints=['문서 7']` 후보가 있을 때 `문서 7 다시 분석해줘`는 해당 문서 분석 후보에 연결되는 테스트를 추가했다.
  - 같은 후보가 있어도 `7시에 다시 알려줘`는 문서 후속 요청으로 연결되지 않고 새 알림 요청으로 유지되는 테스트를 추가했다.
  - 기존 순수 숫자 내부 힌트 오연결 방지 테스트와 함께 확인해, 타입 있는 ID 힌트가 명시 대상 매칭력은 유지하면서 시간 표현 오연결은 막는다는 점을 고정했다.
  - `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 타입 있는 ID 힌트 후보 선택/대체 검증

- 작업 이름: 확인 질문 뒤 후보 선택 응답에서 타입 있는 문서 ID를 안전하게 처리하도록 보강
- 진행상황: 완료
- 진행내용:
  - pending 후보 선택 상태에서 사용자가 `문서 7로 해`처럼 답하면, 라우터 기본 휴리스틱이 `recall`로 잡히더라도 직전 확인 질문에 대한 선택 답변으로 해석해야 함을 확인했다.
  - `route_from_pending_candidate_selection()`이 `chat`뿐 아니라 선택 답변처럼 보이는 짧은 ID/순번/대체 표현도 pending 후보 선택으로 복원하도록 보강했다.
  - 반대로 `문서 7 삭제해줘`, `문서 7 분석해줘`처럼 새 행동이 분명한 문장은 pending 선택으로 가로채지 않도록 명시 액션 마커 게이트를 추가했다.
  - `문서 7 말고 문서 9`처럼 제외/대체 표현이 있을 때 검증기가 앞쪽 제외 대상 ID까지 충돌로 보지 않도록, 명시 대상 검증에서 `말고/대신` 뒤쪽을 실질 대상 텍스트로 사용하게 했다.
  - `문서 7로 해`, `문서 7 말고 문서 9`, `7시에` 케이스를 라우팅 행렬에 추가해 선택/대체/시간 표현 오인 방지를 함께 고정했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_route_validation.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 자연스러운 승인/거절 답변 인식 보강

- 작업 이름: 확인 질문 뒤 사용자의 짧은 자연어 답변을 pending 맥락 승인/거절로 더 잘 인식하도록 보강
- 진행상황: 완료
- 진행내용:
  - 기존 승인/거절 판별이 `응 계속`, `네 진행해줘`, `됐어` 같은 비교적 정형화된 답변 위주라서 `그걸로 해`, `그대로 해`, `그래 해줘`, `아 하지마`, `그건 하지마` 같은 실제 대화 표현을 놓칠 수 있음을 확인했다.
  - `is_context_link_approval_text()`와 `is_positive_confirmation_text()`에 `그걸로`, `그대로`, `그래`, `ㅇㅇ` 계열 표현을 추가했다.
  - `is_context_link_rejection_text()`에 `아 하지마`, `그건 하지마`, `그건 됐어`, `그거 하지마` 계열 표현을 추가했다.
  - `그래 서울 날씨 알려줘`, `아 검색해줘`, `아침 메뉴 추천해줘`처럼 새 요청이거나 감탄사/일반 단어로 시작하는 문장은 승인/거절로 오인하지 않도록 회귀 테스트를 추가했다.
  - pending context가 있을 때 `그걸로 해`는 원래 작업으로 복원되고, `그건 하지마`는 pending 취소로 이어지는 라우팅 행렬 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py -q`, `python3 -m pytest tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 승인/감탄사 접두 새 요청 오인 방지 행렬 보강

- 작업 이름: 자연스러운 승인 표현 확장 후에도 새 요청을 pending 맥락으로 잘못 승인/취소하지 않도록 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - `그걸로 해`, `그대로 해`, `그래 해줘`, `아 하지마` 같은 표현을 승인/거절로 확장한 뒤, 비슷한 접두어가 붙은 새 요청이 직전 pending 작업으로 오인될 수 있는지 점검했다.
  - pending context가 있는 상태에서 `그래 서울 날씨 알려줘`, `그걸로 서울 날씨 알려줘`는 기존 pending 승인으로 이어지지 않고 새 weather 요청으로 유지되는지 행렬 테스트를 추가했다.
  - `그대로 OpenAI 검색해줘`, `아 OpenAI 검색해줘`는 pending 승인/취소가 아니라 새 web_search 요청으로 유지되는지 행렬 테스트를 추가했다.
  - 이 테스트들은 “이전 맥락과 무관한 요청인데도 관련지어 처리하는 문제”를 막기 위한 공통 라우팅 안전망으로, 새 에이전트를 추가해도 동일한 원칙을 검증하는 기준이 된다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 웹 검색 결과 내부 행동 힌트 보강

- 작업 이름: `web_result` artifact가 내부 행동 기록의 URL/제목 힌트로 보존되도록 보강
- 진행상황: 완료
- 진행내용:
  - `web_search` 에이전트는 검색 결과를 `artifacts=[{'kind': 'web_result', 'title': ..., 'url': ...}]` 형태로 반환하지만, 내부 행동 로그 보존 함수는 기존에 `kind='url'`만 `urls`/`url_titles`로 보존하고 있었다.
  - 이 때문에 웹 검색 직후 사용자가 `그 링크 열어줘`, `OpenAI 결과 보여줘`처럼 후속 요청을 했을 때, 라우터 컨텍스트의 내부 행동 기록에서 검색 결과 URL과 제목 단서가 약해질 수 있음을 확인했다.
  - `safe_internal_action_artifact_values()`가 `url`뿐 아니라 `web_result` artifact도 `urls`와 `url_titles`로 보존하도록 변경했다.
  - `internal_action_target_hints()`가 `url_title`/`url_titles`도 target hint로 사용할 수 있도록 허용했다.
  - 웹 검색 결과 OperationResult를 내부 행동 로그로 기록했을 때 reason과 라우터 컨텍스트에 `https://openai.com`, `OpenAI Docs` 같은 URL/제목 힌트가 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_agent_catalog_artifact_outputs_are_available_for_internal_action_context tests/test_bot_helpers.py::test_record_internal_action_result_preserves_web_result_artifacts_for_future_context -q`, `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py tests/test_agent_registry.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 후속 가능 액션 기록 보강

- 작업 이름: 내부 행동 로그에 `available_actions`와 `retryable` 정보를 남겨 다음 라우팅 판단 단서를 강화
- 진행상황: 완료
- 진행내용:
  - 내부 행동 결과 로그에는 status, summary, route, slots, artifacts, warnings, next_actions는 남지만, 실제 검증 계층과 에이전트가 사용하는 `available_actions`와 `retryable` 값은 남지 않는 점을 확인했다.
  - 이 값이 없으면 라우터 모델이 내부 행동 기록만 보고 `open_url`, `summarize`, `retry`, `delete`, `complete` 같은 후속 행동 가능성을 판단하기 어려울 수 있다.
  - `internal_action_result_reason()`이 OperationResult의 `available_actions`를 `actions=...` 형태로 기록하고, `retryable=True` 또는 실패/부분 성공 상태이면 `retryable=True`를 기록하도록 보강했다.
  - 명시 actions가 없는 결과도 `infer_available_actions()`를 통해 가능한 경우 action contract 기반의 후속 행동을 내부 로그에 남기도록 했다.
  - 작업 결과 로그와 웹 검색 결과 로그에 actions/retryable 정보가 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_logs_operation_result_for_future_context tests/test_bot_helpers.py::test_record_internal_action_result_preserves_web_result_artifacts_for_future_context tests/test_bot_helpers.py::test_record_internal_action_result_compacts_long_result_reason -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_agent_registry.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 로그 액션의 휴리스틱 라우터 병합 보강

- 작업 이름: 내부 행동 로그의 actions/retryable 정보를 기존 작업 후보에 병합해 fallback 라우터도 활용하도록 보강
- 진행상황: 완료
- 진행내용:
  - 내부 행동 결과 로그에 `actions=...`, `retryable=True`가 남아도, 휴리스틱 fallback 라우터는 기존 작업 상태 후보에 target_hints와 resolved_slots만 병합하고 actions/retryable은 병합하지 않는 점을 확인했다.
  - `internal_action_context_by_linked_state()`가 안전한 `route.resolved_slots`를 복원할 수 있는 내부 로그에 한해 actions와 retryable도 같은 state_id 후보에 병합하도록 변경했다.
  - 기존 후보 action을 덮어쓰지 않고 내부 로그 action을 뒤에 추가하며, 기존 후보나 내부 로그 중 하나라도 retryable이면 후보를 retryable로 올리도록 했다.
  - 실제 내부 로그 reason은 `| subject=`, `| artifacts=`, `| actions=`, `| retryable=`처럼 pipe 구분으로 이어질 수 있으므로, `parse_internal_action_route_value()`가 이 구분자를 만나면 route dict 파싱을 안전하게 끊도록 보강했다.
  - 웹 검색 결과 내부 로그가 `url`, `actions=retry, summarize, open_url`, `retryable=True`를 가진 경우, 기존 web_search 후보가 `OpenAI 링크 열어줘` 후속 요청을 web_url로 이어받는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_enriches_state_candidate_hints_from_internal_action_log tests/test_router_agent.py::test_router_fallback_enriches_state_candidate_actions_from_internal_action_log -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 추론 액션 내부 로그 회귀 검증

- 작업 이름: 명시 `available_actions`가 없는 OperationResult도 내부 행동 로그에 후속 가능 액션을 남기는지 검증
- 진행상황: 완료
- 진행내용:
  - 내부 행동 결과 로그는 `result.available_actions`가 비어 있으면 `infer_available_actions()`를 통해 action contract 기반 후속 행동을 기록하도록 구현되어 있었다.
  - 하지만 이 경로를 직접 검증하는 테스트가 없어, 새 에이전트나 기존 에이전트가 명시 actions를 빼먹을 때 내부 로그의 후속 행동 단서가 사라지는 회귀를 놓칠 수 있음을 확인했다.
  - 명시 `available_actions` 없이 `intent=analyze_document`, `slots.document_id=7`인 OperationResult를 기록했을 때 `summarize`, `reanalyze`, `compare`, `delete`가 내부 로그 reason에 남는 회귀 테스트를 추가했다.
  - 이 테스트는 agent catalog와 route validation action contract가 내부 행동 기록까지 이어지는 최소 안전망 역할을 한다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_logs_inferred_available_actions tests/test_bot_helpers.py::test_record_internal_action_result_logs_operation_result_for_future_context -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_agent_registry.py tests/test_context_builder.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 실제 내부 로그 포맷 파서 회귀 검증

- 작업 이름: `internal_action_result_reason()`이 만든 실제 reason 문자열을 라우터 내부 로그 파서가 복원하는지 검증
- 진행상황: 완료
- 진행내용:
  - 기존 라우터 파서 테스트는 대부분 수동으로 작성한 내부 로그 문자열을 사용했기 때문에, 실제 `internal_action_result_reason()` 출력 포맷과 파서 계약이 어긋나도 놓칠 수 있었다.
  - `OperationResult`와 `ExecutionContext`로 실제 내부 행동 reason을 생성한 뒤, 이 문자열을 `internal_action_context_by_linked_state()`에 넣어 `linked_state_id`, `resolved_slots.url`, `actions`, `retryable`, `target_hints`가 모두 복원되는 테스트를 추가했다.
  - 이 테스트는 내부 로그 생성 포맷과 라우터 파서가 함께 움직이도록 묶어, 향후 로그 reason 포맷을 바꿔도 fallback 라우터의 맥락 복원이 깨지는지 즉시 확인할 수 있게 한다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_parses_actual_internal_action_result_reason -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - catalog와 추론 후속 action 계약 정렬

- 작업 이름: agent catalog의 `available_actions` 선언과 내부 로그 추론 action이 어긋나지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `infer_available_actions()`가 memory 계열 결과에 `show`, `update`, `delete` 같은 후속 action을 추론하지만, `agent_catalog.json`의 `list_memory`, `update_memory`, `restore_memory` state_outputs에는 일부 action이 빠져 있음을 확인했다.
  - 이 불일치가 있으면 라우터 프롬프트에는 어떤 후속 행동이 가능한지 덜 보이고, 내부 행동 로그에는 더 많은 action이 남아 두 맥락 단서가 서로 다른 계약을 말할 수 있다.
  - `list_memory`, `update_memory`, `restore_memory` catalog state_outputs에 실제 추론 가능한 `available_actions.show/update/delete` 계열을 보강했다.
  - 모든 intent에 대해 `infer_available_actions()`가 반환하는 action이 catalog의 `available_actions.*` state_outputs에 선언되어 있는지 검증하는 테스트를 추가했다.
  - 새 에이전트를 추가하거나 후속 action 추론 규칙을 바꿀 때 catalog, 내부 로그, route validation action contract가 함께 맞춰지도록 자동 안전망을 강화했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`, `python3 -m pytest tests/test_agent_registry.py tests/test_bot_helpers.py tests/test_context_builder.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 모델 라우팅 resolved_slots 실행 전 검증 회귀 보강

- 작업 이름: 실제 모델 JSON 라우팅 결과의 `resolved_slots`가 실행 전 검증을 반드시 거치는지 확인
- 진행상황: 완료
- 진행내용:
  - `RouterAgent`의 JSON 파싱 결과가 `AssistantBot.handle_message()`에서 `validate_route_context_link()`를 통과한 뒤 실행 컨텍스트로 전달되는 현재 경로를 확인했다.
  - 기존 회귀 테스트는 직접 만든 `RoutingResult` 중심이라, 실제 모델 응답 JSON을 파싱한 경로에서 슬롯 보존/제거가 깨져도 놓칠 수 있는 빈틈을 확인했다.
  - `FakeModelRouteOpenAI`를 추가해 실제 `RouterAgent`가 모델 JSON을 파싱하고, 그 결과가 봇의 링크 검증과 디스패치 직전 `ExecutionContext`까지 이어지는 테스트를 추가했다.
  - 연결된 문서 상태와 `resolved_slots.document_id`가 일치하면 슬롯이 보존되어 에이전트 컨텍스트에 전달되는지 검증했다.
  - 연결된 상태의 문서 ID와 모델이 준 `resolved_slots.document_id`가 다르면 즉시 실행하지 않고 확인 요청으로 전환하며, 디스패치가 발생하지 않는지 검증했다.
  - `context_link=none`인데 모델이 실행 슬롯을 반환한 경우에는 `resolved_slots`를 제거한 뒤 에이전트에 전달하는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_validates_parsed_model_resolved_slots_before_dispatch tests/test_bot_helpers.py::test_assistant_bot_clarifies_parsed_model_resolved_slot_mismatch_before_dispatch tests/test_bot_helpers.py::test_assistant_bot_clears_parsed_model_resolved_slots_without_context_link_before_dispatch -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 새 요청 과연결 방지 라우팅 행렬 보강

- 작업 이름: 후속 표현처럼 보이는 새 요청이 최근 작업 후보에 잘못 연결되지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 다중 작업 후보가 있는 상황에서 `방금 생각난 아이디어 정리해줘`, `방금 뉴스 알려줘`, `아까 말한거 말고 오늘 저녁 뭐 먹지` 같은 새 요청이 기존 후보 확인 질문이나 특정 후보 실행으로 새는 문제를 확인했다.
  - `RouterAgent` fallback이 `방금생각난`, `아까생각난`, `지금생각난` 표현을 새 발상/새 내용 요청으로 보고 기존 작업 후보 연결을 시도하지 않도록 했다.
  - `말고/대신` 같은 거절 표현과 공통 새 요청 마커가 함께 있고, 특정 후보와 명시적으로 일치하지 않으면 기존 후보 확인으로 끌고 가지 않고 base route를 유지하도록 했다.
  - `뉴스`를 라우터 후보 종류의 web 계열과 공통 새 요청 마커에 추가해, 최근 알림/할 일의 `show` action이 `방금 뉴스 알려줘` 같은 새 정보 요청을 빼앗지 않도록 했다.
  - 다중 후보 행렬 테스트에 새 발상 요청, 뉴스 요청, 이전 맥락 거절 후 저녁 추천 요청이 모두 `context_link=none`으로 남는 회귀 케이스를 추가했다.
  - 기존 `방금 작업 삭제해줘`처럼 진짜 후속 요청은 여전히 할 일 후보로 이어지는지 함께 확인했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 최근 대화 원문 저장/등록 요청 보호

- 작업 이름: `아까 말한 내용 기억해줘` 같은 새 저장 요청이 작업 후보 확인으로 새지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 다중 작업 후보가 있는 상황에서 `아까 말한 내용 기억해줘`가 새 기억 저장 요청이 아니라 “어느 작업을 이어갈까요?” 확인 질문으로 새는 문제를 샘플링으로 확인했다.
  - `방금 말한 거 메모해줘`, `전에 말한거 할 일로 추가해줘`, `위 내용 알림으로 등록해줘`처럼 최근 대화 원문을 새 메모/할 일/알림으로 만드는 요청은 기존 작업 후보 연결을 시도하지 않고 base route를 유지하도록 했다.
  - 이 보호는 `remember`, `manage_task`, `manage_reminder`처럼 새 항목 생성 의도가 있는 base intent에만 적용해, `그거 기억해줘`처럼 기존 작업/메모를 새 기억으로 변환하는 정상 후속 요청은 계속 연결되도록 했다.
  - 처음에는 `기억`을 memory 후보 종류 필터에 추가했지만, 이것이 `그거 기억해줘` 정상 변환을 막는 것을 행렬 테스트가 잡아내어 제거했다.
  - 다중 후보 상황에서 `아까 말한 내용 기억해줘`, `전에 말한거 할 일로 추가해줘`, `위 내용 알림으로 등록해줘`가 모두 `context_link=none`으로 유지되는 회귀 테스트를 추가했다.
  - 기존 `그거 기억해줘`, cross-location `그거 기억해줘`, `그 메모 알림으로 등록해줘` 같은 참조 기반 변환 케이스가 계속 통과하는지 함께 확인했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 명시 출처 기반 변환 요청 라우팅 보강

- 작업 이름: `그 메모 할일로`, `그 작업 메모로`처럼 출처와 목적이 함께 있는 변환 요청을 정확히 연결
- 진행상황: 완료
- 진행내용:
  - 여러 작업 후보가 있을 때 `그 메모 할일로 만들어줘`, `그 작업 메모로 저장해줘`, `그 작업 내일 알려줘` 같은 요청이 목적 후보까지 같이 남아 확인 질문으로 새는 문제를 샘플링으로 확인했다.
  - `그 메모`, `그 작업/그 할일`, `그 알림`, `그 문서/그 파일`, `그 링크/그 검색결과`처럼 출처 종류가 명시된 변환 요청은 목적 intent보다 출처 후보를 먼저 고르도록 했다.
  - 변환 요청의 목적 intent는 base heuristic에만 의존하지 않고 `메모로`, `할일로/작업으로`, `알림으로/리마인드로`, `내일 알려줘` 같은 표현에서 직접 계산하도록 했다.
  - `바꿔`, `변환` 표현도 기존 항목 수정뿐 아니라 출처 기반 새 항목 변환으로 인식할 수 있도록 메모/할 일/알림 생성 마커에 포함했다.
  - 다중 후보 행렬에 `그 메모 할일로 만들어줘`, `그 작업 메모로 저장해줘`, `그 작업 내일 알려줘` 케이스를 추가해 목적 후보가 출처 선택을 흐리지 않도록 고정했다.
  - 기존 단일 후보 변환, 메모를 알림으로 등록, 대명사 기반 새 메모/할 일/알림 생성 케이스가 계속 통과하는지 함께 확인했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 모델 라우터 프롬프트 경계 규칙 동기화

- 작업 이름: fallback 라우터에서 보강한 새 요청/변환 요청 경계를 모델 라우터 프롬프트에도 반영
- 진행상황: 완료
- 진행내용:
  - fallback 라우터에는 새 요청 과연결 방지, 최근 대화 원문 저장/등록, 명시 출처 기반 변환 요청 규칙이 보강되었지만, 모델 정상 응답 경로의 프롬프트에는 같은 경계가 충분히 구체적으로 표현되지 않은 점을 확인했다.
  - 라우터 프롬프트에 `방금 생각난 아이디어 정리해줘`, `방금 뉴스 알려줘`, `아까 말한거 말고 오늘 저녁 뭐 먹지`는 새 요청으로 보고 `context_link=none`을 유지하라는 예시를 추가했다.
  - `아까 말한 내용 기억해줘`, `전에 말한거 할 일로 추가해줘`, `위 내용 알림으로 등록해줘`는 최근 작업 후보를 이어받는 것이 아니라 최근 대화 원문을 새 항목으로 저장/등록하는 요청임을 명시했다.
  - `그 메모 할일로 만들어줘`, `그 작업 메모로 저장해줘`, `그 작업 내일 알려줘`처럼 출처 종류와 목적 종류가 함께 명시된 변환 요청은 출처 후보를 `linked_state_id`로 고르고 목적 intent로 실행하라고 명시했다.
  - 프롬프트가 이 경계 예시와 `resolved_slots.task_title`, `resolved_slots.memory_text`, `resolved_slots.reminder_text` 지침을 계속 포함하는지 라우터 프롬프트 회귀 테스트를 보강했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_agent_prefers_model_route_over_heuristic -q`, `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 모델 오답 링크 실행 전 차단 회귀 검증

- 작업 이름: 모델 라우터가 최근 대화 원문 저장 요청을 기존 작업 상태에 잘못 연결해도 실행 전 검증이 차단하는지 확인
- 진행상황: 완료
- 진행내용:
  - 프롬프트를 보강해도 모델 정상 응답 경로에서 `전에 말한거 할 일로 추가해줘` 같은 새 생성 요청에 `linked_state_id`와 `task_id`를 잘못 붙일 수 있는 위험을 확인했다.
  - `validate_route_context_link()`는 이미 `asks_to_create_from_recent_conversation_source()`를 통해 이런 링크를 제거하고 있었지만, 실제 모델 JSON 파싱부터 `AssistantBot.handle_message()` 디스패치 직전까지 이어지는 통합 회귀 테스트는 부족했다.
  - `FakeModelRouteOpenAI`가 `intent=manage_task`, `context_link=continue`, `linked_state_id=<기존 할 일 상태>`, `resolved_slots.task_id=3`을 반환하도록 구성한 통합 테스트를 추가했다.
  - 봇이 실행 전 검증 후 `context_link=none`, `linked_state=None`, `resolved_slots={}` 상태로 전문 에이전트에 전달하는지 확인했다.
  - route validation 로그에 `linked_state_id`와 `resolved_slots` 조정이 남아, 모델 오답 링크가 내부 행동 기록으로 추적 가능한지도 확인했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_clears_parsed_model_link_for_recent_conversation_source_creation -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 명시 출처 변환 오답 링크 검증 보강

- 작업 이름: 모델이 `그 메모 할일로` 같은 변환 요청에서 목적 후보를 잘못 연결해도 실행 전 검증이 차단하도록 보강
- 진행상황: 완료
- 진행내용:
  - `그 메모 할일로 만들어줘`, `그 작업 메모로 저장해줘`, `그 작업 내일 알려줘`에서 모델이 출처 후보가 아니라 목적 후보를 `linked_state_id`로 반환하면 기존 검증이 통과시키는 빈틈을 확인했다.
  - `explicit_source_reference_groups()`를 추가해 `그 메모`, `그 작업/그 할일`, `그 알림`, `그 문서/그 파일`, `그 링크/그 검색결과`처럼 사용자가 명시한 출처 종류를 추출하도록 했다.
  - 실행 전 링크 검증에서 명시 출처 종류가 있으면 linked state가 해당 종류의 슬롯/artifact를 제공하는지 확인하고, 맞지 않으면 링크를 제거하도록 했다.
  - `그 문서 다시 보여줘` 같은 일반 대명사 참조까지 과도하게 새 대상으로 보지 않도록, `has_explicit_source_conversion_request()`를 추가해 명시 출처+목적 변환 표현일 때만 clear 경로로 보내도록 좁혔다.
  - route validation 단위 테스트로 잘못 연결된 task 후보는 제거하고, 올바르게 연결된 memory 후보는 유지하는 케이스를 추가했다.
  - 봇 통합 테스트로 모델 JSON이 `그 메모 할일로 만들어줘`를 기존 task 후보에 잘못 연결해도 `context_link=none`, `linked_state=None`, `resolved_slots={}`로 전문 에이전트에 전달되는지 확인했다.
  - 기존 `그 문서 다시 보여줘`의 잘못된 문서 슬롯 mismatch는 여전히 확인 질문으로 남는지 함께 회귀 검증했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clears_mismatched_explicit_source_reference tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_explicit_source_reference tests/test_bot_helpers.py::test_assistant_bot_clears_parsed_model_link_for_mismatched_explicit_source_reference -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 출처 기반 정상 변환 요청 검증 보정

- 작업 이름: 검증 강화 후 `그 알림 할 일로 추가해줘` 같은 정상 변환 요청이 끊기지 않도록 보정
- 진행상황: 완료
- 진행내용:
  - 명시 출처 검증을 강화한 뒤 정상 요청이 과도하게 차단되는지 샘플링했다.
  - `그 알림 할 일로 추가해줘`는 알림을 출처로 새 할 일을 만드는 정상 변환 요청인데, route validation의 `asks_to_create_task_from_linked_reference()`가 알림/문서/링크 출처를 허용하지 않아 링크를 제거하는 문제를 확인했다.
  - 할 일 생성 변환 검증에서 메모/작업뿐 아니라 알림, 문서, 링크/검색결과 출처도 허용하도록 reference markers를 확장했다.
  - 알림 생성 변환 검증도 같은 출처 종류를 사용할 수 있게 확장하고, `바꿔`, `변환` 표현을 생성/변환 마커에 포함했다.
  - `그 알림 할 일로 추가해줘`가 linked reminder 상태를 유지하는 route validation 단위 테스트를 추가했다.
  - 다중 후보 행렬에 알림 후보와 할 일 후보가 함께 있을 때 `그 알림 할 일로 추가해줘`가 알림 후보를 출처로 선택해 `task_title`을 채우는 케이스를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_keeps_reminder_to_task_source_conversion tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 검색 결과 출처 표현 변환 보강

- 작업 이름: `그 검색 결과`처럼 띄어 쓴 웹 결과 참조를 메모/할 일/알림 변환 출처로 인식
- 진행상황: 완료
- 진행내용:
  - 문서/링크/검색 결과를 메모, 할 일, 알림으로 변환하는 요청을 샘플링했다.
  - `그 문서 메모로 저장해줘`, `그 링크 할 일로 추가해줘` 등은 정상 연결되었지만, `그 검색 결과 메모로 저장해줘`처럼 띄어 쓴 표현은 fallback이 출처로 잡지 못하거나 validation이 `그`를 새 검색어로 오해하는 문제를 확인했다.
  - 라우터의 대명사 후속 참조 목록에 `그검색결과`, `이검색결과`, `저검색결과`를 추가해 `그 검색 결과` 표현이 web_result 후보를 출처로 사용할 수 있도록 했다.
  - route validation의 FOLLOW_UP_MARKERS에도 `그 검색 결과`, `이 검색 결과`, `저 검색 결과` 계열을 추가했다.
  - `explicit_search_queries_from_text()`가 `그 검색 결과 ...`에서 `그`를 검색어로 추출하지 않도록 `그/이/저` 단독 query를 후속 참조로 제외했다.
  - 검색 결과 후보와 메모 후보가 함께 있을 때 `그 검색 결과 메모로 저장해줘`가 web_result 후보를 연결하고 `memory_text`를 채우는 행렬 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_explicit_text_target_extractors_ignore_pronoun_follow_ups tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 웹 결과 출처 변환 검증 회귀 보강

- 작업 이름: `그 검색 결과` 변환 요청에서 올바른 web_result 출처는 유지하고 잘못된 목적 후보 링크는 제거하는 검증 테스트 추가
- 진행상황: 완료
- 진행내용:
  - 검색 결과 출처 표현은 fallback 행렬에서 보강되었지만, route validation 단위에서 web_result 출처의 유지/차단 양방향 회귀 테스트가 부족한 점을 확인했다.
  - `그 검색 결과 메모로 저장해줘`에서 linked state가 `web_result` artifact를 가진 web_search 상태이면 `context_link=continue`와 `memory_text`를 유지하는 테스트를 추가했다.
  - 같은 문장에서 모델이 목적 후보인 기존 memory 상태를 잘못 linked state로 반환하면 `context_link=none`, `linked_state_id=None`, `resolved_slots={}`로 제거하는 테스트를 추가했다.
  - 이 테스트는 라우터와 validation의 명시 출처 해석이 갈라져 검색 결과 변환 요청이 잘못 실행되는 회귀를 막기 위한 안전망이다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_keeps_web_result_source_conversion tests/test_route_validation.py::test_validate_route_context_link_clears_mismatched_web_result_source_conversion -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 출처 참조 계약 회귀 테스트 추가

- 작업 이름: 라우터와 실행 전 검증이 명시 출처 참조를 같은 그룹으로 해석하는지 계약 테스트로 고정
- 진행상황: 완료
- 진행내용:
  - 명시 출처 변환 요청은 fallback 라우터와 route validation 양쪽에 동일한 출처 그룹 규칙이 필요하지만, 두 구현이 별도 함수로 관리되어 새 표현 추가 시 어긋날 위험이 있음을 확인했다.
  - `그 메모`, `그 작업/그 할 일`, `그 알림/그 리마인드`, `그 문서/그 파일`, `그 링크/그 검색 결과` 계열 문장을 공통 계약 케이스로 추가했다.
  - `explicit_source_reference_kinds()`와 `explicit_source_reference_groups()`가 같은 입력에서 같은 출처 그룹을 반환하는지 검증하는 회귀 테스트를 추가했다.
  - 이 테스트는 새 에이전트나 새 출처 표현을 추가할 때 라우터는 한쪽 후보를 선택하고 validation은 다른쪽 후보를 차단하는 식의 맥락 불일치를 조기에 잡기 위한 안전망이다.
  - `python3 -m pytest tests/test_route_validation.py::test_router_and_route_validation_share_explicit_source_reference_contract -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 출처 변환 목적 intent 계약 회귀 테스트 추가

- 작업 이름: 명시 출처 변환 요청에서 라우터의 목적 intent 판단과 실행 전 검증의 허용 판단을 같은 방향으로 고정
- 진행상황: 완료
- 진행내용:
  - 출처 그룹 계약은 추가되었지만, `그 메모 할일로`, `그 작업 알림으로`, `그 링크 기억으로`처럼 목적 intent가 달라지는 변환 요청의 판별 계약은 별도 안전망이 부족한 점을 확인했다.
  - 라우터의 `reference_creation_target_intent()`가 반환하는 목적 intent와 route validation의 `asks_to_create_task_from_linked_reference()`, `asks_to_create_reminder_from_linked_reference()` 결과가 함께 맞는지 검증하는 계약 테스트를 추가했다.
  - 메모 목적 변환은 validation에서 별도 생성 함수가 아니라 `remember` continue 호환 경로를 사용하므로, `has_explicit_source_conversion_request()`가 명시 변환 요청으로 인식하고 할 일/알림 생성 판별은 거짓으로 남는지 확인했다.
  - 이 테스트는 새 목적 표현이나 새 에이전트가 추가될 때 라우터는 변환 요청으로 보지만 validation은 일반 후속 요청으로 보거나, 반대로 validation이 잘못 허용하는 회귀를 막기 위한 안전망이다.
  - `python3 -m pytest tests/test_route_validation.py::test_router_and_route_validation_share_source_target_conversion_contract -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 라우팅 표현 마커 공유 상수화

- 작업 이름: 라우터와 실행 전 검증이 참조하는 명시 출처/목적 표현표를 공유 모듈로 정리
- 진행상황: 완료
- 진행내용:
  - 명시 출처 그룹, 할 일/메모/알림 변환 목적 마커, 생성 마커, 알림 시간 마커가 라우터와 route validation에 각각 중복 정의되어 있어 새 표현 추가 시 한쪽만 바뀔 위험이 있음을 확인했다.
  - `assistant_bot/routing_markers.py`를 추가해 `EXPLICIT_SOURCE_REFERENCE_MARKERS`, `TASK_TARGET_MARKERS`, `MEMORY_TARGET_MARKERS`, `REMINDER_TARGET_MARKERS`, 생성 마커, 알림 시간 마커를 공통 상수로 분리했다.
  - 라우터의 `explicit_source_reference_kinds()`, `requests_task_creation_from_reference()`, `requests_memory_creation_from_reference()`, `requests_reminder_creation_from_reference()`가 공유 상수를 사용하도록 변경했다.
  - route validation의 `explicit_source_reference_groups()`, `has_explicit_source_conversion_request()`, `asks_to_create_task_from_linked_reference()`, `asks_to_create_reminder_from_linked_reference()`도 같은 상수를 사용하도록 변경했다.
  - 기존 계약 테스트와 전체 테스트를 통과해 동작은 유지하면서 규칙 출처를 더 좁혔다.
  - `python3 -m pytest tests/test_route_validation.py::test_router_and_route_validation_share_explicit_source_reference_contract tests/test_route_validation.py::test_router_and_route_validation_share_source_target_conversion_contract -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 기록 구조화 컨텍스트 보강

- 작업 이름: 라우터가 사용자에게 보이지 않는 내부 실행 결과를 더 잘 참고하도록 내부 행동 컨텍스트 구조화
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록은 이미 라우터 컨텍스트에 포함되고 있었지만, route 정보, 실행 가능 action, retryable 여부가 긴 reason 문자열 안에 묻혀 있어 모델이 안정적으로 참고하기 어려운 점을 확인했다.
  - `build_internal_action_context()`가 원문 reason에서 `route_context`, `executable_actions`, `retryable`을 추출해 내부 행동 기록 라인에 별도 필드로 노출하도록 보강했다.
  - 라우터의 내부 행동 파서가 기존 `actions=`뿐 아니라 새 `executable_actions=` 필드도 실행 가능 action 단서로 읽도록 확장했다.
  - `context_builder`가 에이전트 패키지의 common 유틸을 import하면서 단독 import 시 순환 import가 발생하는 문제를 확인하고, 필요한 포맷 유틸을 `context_builder` 내부로 분리해 import 순서 의존성을 제거했다.
  - 내부 행동 결과 로그가 router context에 구조화된 action/retryable 값을 포함하는지, 문서 분석 route_context가 노출되는지, 라우터 fallback이 `executable_actions`를 후보 action으로 병합하는지 테스트를 보강했다.
  - `python3 -c "import assistant_bot.context_builder; print('ok')"`, `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 구조화 필드 응답 비노출 검증

- 작업 이름: 라우터용 내부 행동 구조화 필드가 사용자 응답 프롬프트에 내부 표기로 새지 않도록 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록에 `route_context`, `executable_actions`, `retryable` 필드를 추가한 뒤, 해당 값이 라우터에는 유용하지만 최종 답변 생성 프롬프트에는 내부 키 그대로 드러나면 대화형 비서 느낌을 해칠 수 있음을 확인했다.
  - `ResponseComposer`가 `ExecutionContext.for_response()`를 통해 내부 행동 기록을 `비공개 내부 참고`로 안전 변환할 때 `route_context`, `executable_actions`, `linked_state_id`, agent/model 내부 표기가 그대로 포함되지 않는지 테스트를 보강했다.
  - 기존 안전 변환이 구조화 필드를 직접 노출하지 않는 것을 확인했고, 관련 응답/컨텍스트/라우터 테스트 묶음으로 회귀를 검증했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_composer_treats_internal_action_context_as_hidden_reference -q`, `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 구조화 내부 route_context 파서 보강

- 작업 이름: reason의 route 정보가 축약되어도 별도 `route_context` 필드로 후속 슬롯을 복원하도록 라우터 파서 보강
- 진행상황: 완료
- 진행내용:
  - 내부 행동 컨텍스트에 `route_context`를 추가했지만, 라우터의 내부 기록 파서는 여전히 reason 안의 `route=`만 읽고 있어 reason이 길어 축약되면 복원 슬롯을 잃을 수 있음을 확인했다.
  - `parse_internal_action_route_value()`가 `route_context=`를 우선 파싱하고, 없을 때 기존 `route=`를 읽도록 보강했다.
  - `executable_actions=('show', 'complete', 'delete')`처럼 튜플 문자열로 표시되는 action도 깨끗한 action 이름으로 파싱하도록 literal string 파서를 리스트/튜플/셋에 대응하게 확장했다.
  - reason의 route가 축약된 내부 행동 기록에서도 `linked_state_id`, `resolved_slots`, `executable_actions`, `retryable`, `target_hints`가 올바르게 복원되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_parses_structured_internal_route_context_when_reason_route_is_trimmed tests/test_router_agent.py::test_router_parses_actual_internal_action_result_reason tests/test_router_agent.py::test_router_fallback_enriches_state_candidate_actions_from_internal_action_log -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_bot_helpers.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 빌더 출력-라우터 파서 연결 검증

- 작업 이름: `build_router_context()`가 실제 출력한 내부 행동 구조화 필드를 라우터 파서가 그대로 복원하는지 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - route_context 파서는 보강되었지만, 컨텍스트 빌더의 sanitize/compact 과정이 실제 출력 문자열을 바꾸면 라우터가 다시 읽지 못할 수 있음을 확인했다.
  - `build_router_context()`로 생성한 실제 router context를 `internal_action_context_by_linked_state()`에 넣어 `linked_state_id`, `resolved_slots`, `executable_actions`, `retryable`, `target_hints`가 복원되는지 확인하는 테스트를 추가했다.
  - 이 테스트는 내부 행동 기록 생성부와 라우터 파서가 문자열 계약을 공유한다는 점을 직접 검증해, 추후 포맷 변경 시 맥락 복원이 조용히 깨지는 일을 막기 위한 안전망이다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_internal_route_context_is_parseable_by_router tests/test_context_builder.py::test_build_router_context_adds_internal_action_target_hints_and_guidance -q`, `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_bot_helpers.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 컨텍스트 길이 제한 복원성 보강

- 작업 이름: 내부 행동 기록이 길이 제한으로 잘려도 라우터 복원 단서가 살아남도록 필드 순서와 target_hints 정리
- 진행상황: 완료
- 진행내용:
  - `internal_action_context_max_chars`가 작거나 reason이 긴 경우, 기존 출력 순서에서는 `route_context`가 잘리고 `target_hints` 일부만 남아 후속 슬롯 복원이 불가능해지는 문제를 테스트로 확인했다.
  - 라우터가 실제로 사용하는 `route_context`, `executable_actions`, `retryable`, `target_hints`를 내부 행동 라인의 끝부분에 배치해 trim 시 보존될 가능성을 높였다.
  - 긴 summary가 target_hints에 들어가 라인 끝을 과도하게 차지하지 않도록, 120자를 넘는 내부 action summary는 대상 힌트에서 제외했다.
  - 길이 제한이 걸린 실제 `build_router_context()` 출력에서도 `internal_action_context_by_linked_state()`가 `linked_state_id`, `resolved_slots`, action, retryable, target_hints를 복원하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_keeps_parseable_internal_route_context_when_trimmed -q`, `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_response_composer.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation 조정 로그 구조화 보강

- 작업 이름: 실행 전 검증이 링크/슬롯을 제거하거나 수정한 기록을 구조화해 다음 라우팅 컨텍스트에 보존
- 진행상황: 완료
- 진행내용:
  - route validation 로그는 `context_link continue->none` 같은 자연어 요약만 남아, 다음 라우팅에서 어떤 before/after 판단이 있었는지 구조적으로 참조하기 어려운 점을 확인했다.
  - `route_validation_summary()`에 `validation_context={'before': ..., 'after': ...}`를 추가해 intent, context_link, linked_state_id, resolved_slots, clarification_question의 조정 전후 값을 남기도록 했다.
  - `build_internal_action_context()`가 route validation 로그의 `validation_context`를 별도 필드로 끌어올려 router context에 보존하도록 보강했다.
  - 라우터의 `route_context` 파서가 새 `validation_context` 필드를 delimiter로 인식하도록 수정해 기존 route_context 파싱이 깨지지 않게 했다.
  - 장문 로그에서는 핵심 자연어 사유와 구조화 context가 모두 남도록 요약 순서와 압축 길이를 조정했다.
  - `python3 -m pytest tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment tests/test_cli.py::test_log_route_validation_if_changed_compacts_long_adjustment tests/test_context_builder.py::test_build_router_context_does_not_turn_validation_reason_into_target_hint -q`, `python3 -m pytest tests/test_cli.py tests/test_context_builder.py tests/test_bot_helpers.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation 조정 안내 힌트 보강

- 작업 이름: 검증에서 제거되거나 확인으로 바뀐 자동 연결 이력을 라우터가 이해하기 쉬운 안내 문장으로 보존
- 진행상황: 완료
- 진행내용:
  - `validation_context`는 구조화 값으로 남지만, 모델 라우터가 곧바로 해석하기에는 before/after dict만으로는 의미가 덜 직접적인 점을 확인했다.
  - `internal_action_validation_guidance()`를 추가해 검증에서 특정 `state_id` 자동 연결이 제거된 경우 “현재 메시지가 같은 대상을 명확히 다시 가리킬 때만 재연결”이라는 안내를 내부 행동 컨텍스트에 추가했다.
  - 검증 결과가 자동 실행에서 확인 질문으로 바뀐 경우도 “같은 유형이면 바로 실행하지 말고 확인”하도록 안내 문장을 생성하게 했다.
  - 구조화 정보가 없는 단순 내부 로그에는 빈 구조 필드를 길게 붙이지 않고 `reason_hint` 중심의 짧은 형식으로 출력해, 길이 제한 상황에서도 최신 핵심 로그와 다른 위치 로그가 함께 남도록 조정했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_does_not_turn_validation_reason_into_target_hint tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment -q`, `python3 -m pytest tests/test_context_builder.py tests/test_cli.py tests/test_router_agent.py tests/test_bot_helpers.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 모델 라우터 validation_guidance 해석 지침 보강

- 작업 이름: 모델 라우터가 내부 행동 기록의 `validation_guidance`를 과연결 방지 규칙으로 해석하도록 프롬프트에 명시
- 진행상황: 완료
- 진행내용:
  - `validation_guidance`는 router context에 남지만, 모델 라우터 프롬프트에는 해당 필드의 의미와 우선순위가 직접 설명되어 있지 않은 점을 확인했다.
  - 라우터 프롬프트에 `validation_guidance`가 실행 전 검증이 방금 막거나 확인으로 바꾼 자동 연결 이력이라는 설명을 추가했다.
  - `자동 연결이 제거됨`이면 현재 메시지가 같은 대상을 명확히 다시 가리키지 않는 한 같은 `state_id`를 다시 `linked_state_id`로 선택하지 말라고 명시했다.
  - `바로 실행하지 말고 확인`이면 같은 유형의 후속 요청을 `context_link=clarify`로 확인하라고 명시했다.
  - 모델 라우터 프롬프트 테스트에 해당 지침 문구를 고정해, 향후 프롬프트 수정 중 내부 검증 안내 해석 규칙이 빠지지 않도록 했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_agent_prefers_model_route_over_heuristic -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_cli.py tests/test_bot_helpers.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - validation_guidance 응답 비노출 검증

- 작업 이름: 라우터용 `validation_guidance`가 최종 응답 프롬프트에 내부 지침 그대로 새지 않도록 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - `validation_guidance`는 라우터에는 필요한 과연결 방지 힌트지만, 최종 사용자 응답에는 `state_id`, 자동 연결, 재연결 같은 내부 표현이 그대로 드러나면 대화 품질을 해칠 수 있음을 확인했다.
  - 기존 내부 행동 기록 비노출 테스트에 `validation_guidance=최근 검증에서 state_id:12 자동 연결이 제거됨...` 케이스를 추가했다.
  - `ResponseComposer`의 응답 생성 프롬프트에 `validation_guidance`, `자동 연결이 제거됨`, `재연결`, `linked_state_id` 같은 내부 표기가 포함되지 않는지 검증했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_composer_treats_internal_action_context_as_hidden_reference -q`, `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - fallback 라우터 validation 제거 이력 반영

- 작업 이름: 실행 전 검증에서 제거된 state 후보를 fallback 라우터가 암묵적 후속 요청에 다시 자동 연결하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `validation_guidance`는 모델 라우터 프롬프트에는 반영되었지만, fallback 라우터는 validation 제거 이력을 실제 후보 선택에 쓰지 않는 점을 확인했다.
  - `internal_validation_removed_state_ids()`를 추가해 내부 행동 기록의 `validation_context`에서 `context_link=continue -> none`, `linked_state_id -> None`으로 제거된 state_id를 추출하도록 했다.
  - fallback 라우터가 후보를 고르기 전에 검증에서 제거된 state 후보를 암묵적 후속 요청에서는 제외하도록 했다.
  - 단, 사용자가 `contract.pdf`, `문서 7`, 명확한 제목/ID처럼 같은 대상을 직접 말한 경우에는 재연결을 허용해 정당한 재시도까지 막지 않도록 했다.
  - 암묵적 `그거 보여줘`는 제거된 state를 다시 쓰지 않고, 명시적 `contract.pdf 다시 요약해줘`는 같은 state를 다시 사용할 수 있음을 회귀 테스트로 고정했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_parses_internal_validation_removed_state_ids tests/test_router_agent.py::test_router_fallback_does_not_reuse_validation_removed_state_for_implicit_follow_up tests/test_router_agent.py::test_router_fallback_allows_validation_removed_state_when_user_explicitly_names_target -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - fallback 라우터 validation 확인 전환 이력 반영

- 작업 이름: 실행 전 검증에서 자동 실행이 확인 질문으로 바뀐 state 후보를 fallback 라우터가 다시 바로 실행하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 검증에서 `context_link=clarify`로 바뀐 이력은 모델 라우터 프롬프트에는 안내되지만, fallback 라우터는 여전히 암묵적 후속 요청을 바로 실행할 수 있는 점을 확인했다.
  - `internal_validation_clarified_state_ids()`를 추가해 내부 행동 기록의 `validation_context`에서 확인 질문으로 전환된 state_id를 추출하도록 했다.
  - fallback 라우터가 실행 직전 후보가 확인 전환 이력이 있는 state이고, 현재 메시지가 해당 대상을 명확히 다시 말하지 않은 경우 `context_link=clarify`로 확인 질문을 반환하도록 했다.
  - summary의 `완료` 같은 일반 action 단어가 명시 대상 매치로 오판되지 않도록, validation 확인 이력 판단에는 summary를 제외한 subject/target_hints/slots/artifacts 기반 명시성만 사용하게 했다.
  - 암묵적 `그거 완료했어`는 확인 질문으로 돌리고, 명시적 `할 일 9 완료했어`는 바로 연결할 수 있음을 회귀 테스트로 고정했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_parses_internal_validation_clarified_state_ids tests/test_router_agent.py::test_router_fallback_clarifies_validation_clarified_state_for_implicit_action tests/test_router_agent.py::test_router_fallback_allows_validation_clarified_state_when_user_explicitly_names_target -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - validation_context 빌더-라우터 파싱 계약 검증

- 작업 이름: context_builder가 원문 로그에서 추출한 `validation_context`와 router가 출력 context에서 다시 파싱한 값이 일치하도록 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - `validation_context`는 route validation reason 안에도 있고, `build_internal_action_context()`가 별도 필드로도 출력하므로 라우터 파서가 잘린 reason 내부 값을 잘못 잡을 위험을 확인했다.
  - 라우터의 `parse_internal_action_validation_context()`가 ` | validation_context=`처럼 실제 필드 구분자로 시작하는 값만 파싱하도록 좁혔다.
  - `build_router_context()`의 실제 출력 라인을 router 파서에 넣어 before/after dict가 원문 reason에서 추출한 값과 같은지 검증하는 계약 테스트를 추가했다.
  - 이 테스트는 빌더의 sanitize/compact/필드 순서 변경이 라우터의 validation 제거/확인 이력 복원을 깨뜨리는 회귀를 막기 위한 안전망이다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router tests/test_context_builder.py::test_build_router_context_does_not_turn_validation_reason_into_target_hint tests/test_router_agent.py::test_router_parses_internal_validation_removed_state_ids tests/test_router_agent.py::test_router_parses_internal_validation_clarified_state_ids -q`, `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_cli.py tests/test_bot_helpers.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - validation_context 응답 비노출 검증

- 작업 이름: 라우터용 `validation_context` before/after 구조가 최종 응답 프롬프트에 내부 표기로 새지 않도록 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - `validation_context`에는 before/after route, linked_state_id 같은 내부 라우팅 값이 들어가므로 사용자 응답 프롬프트에는 그대로 드러나지 않아야 함을 확인했다.
  - 내부 행동 기록 비노출 테스트에 `validation_context={'before': ..., 'after': ...}` 케이스를 추가했다.
  - `ResponseComposer`의 응답 생성 프롬프트에 `validation_context`, `before`, `after`, `linked_state_id` 같은 내부 표기가 포함되지 않는지 검증했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_composer_treats_internal_action_context_as_hidden_reference -q`, `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_router_agent.py -q`, `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 슬롯 없는 내부 행동 액션 힌트 복원

- 작업 이름: 내부 행동 로그에 `linked_state_id`와 실행 액션은 있지만 `resolved_slots`가 없는 경우에도 라우터 후보 단서를 일부 복원
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그에서 `route.linked_state_id`는 실제 실행 연결 근거로 확인되지만, `resolved_slots`가 비어 있으면 같은 줄의 `executable_actions`, `retryable`, `target_hints`까지 모두 버려지는 점을 확인했다.
  - 이 경우 문서 분석이나 웹 결과처럼 파일명/대상 힌트와 후속 액션은 남아 있는데 슬롯만 비어 있는 결과가 다음 턴 라우팅에 도움을 주지 못할 수 있다.
  - `internal_action_context_by_linked_state()`가 안전 슬롯이 없어도 실행 액션 또는 재시도 가능성이 있으면 해당 state의 내부 단서를 복원하도록 수정했다.
  - 단, `target_hints`만 있고 실행 가능한 슬롯/액션/재시도 근거가 없는 내부 로그는 기존처럼 병합하지 않도록 유지해 과연결 위험을 막았다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_parses_internal_actions_without_resolved_slots tests/test_router_agent.py::test_router_fallback_does_not_merge_internal_hints_without_executable_slots tests/test_router_agent.py::test_router_parses_structured_internal_route_context_when_reason_route_is_trimmed -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - 첨부 파일명 작업 상태 힌트 보강

- 작업 이름: 문서 분석 작업 상태의 `attachment_names`가 라우터 대상 힌트로 보존되도록 개선
- 진행상황: 완료
- 진행내용:
  - `agent_catalog.json`의 문서 분석 에이전트는 `slots.attachment_names`를 후속 맥락 단서로 선언하지만, `turn_state_target_hints()`는 `filename/filenames`만 보고 `attachment_names`는 보지 않는 점을 확인했다.
  - 이 경우 subject가 `문서 분석 결과`처럼 일반적이고 파일명이 슬롯에만 남은 상태에서는 `contract.pdf 다시 요약해줘` 같은 후속 요청을 기존 문서 분석 상태에 연결하는 단서가 약해질 수 있다.
  - `TURN_STATE_TARGET_HINT_SLOT_KEYS`를 추가하고 `attachment_name`, `attachment_names`를 최근 작업 상태 후보의 `target_hints`에 포함하도록 했다.
  - 카탈로그가 선언한 대상형 슬롯이 실제 작업 상태 힌트 슬롯 목록에도 포함되는지 확인하는 계약 테스트를 추가해, 새 에이전트가 추가될 때 같은 누락이 반복되지 않게 했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_turn_state_hints tests/test_context_builder.py::test_build_router_context_uses_attachment_names_as_target_hints tests/test_context_builder.py::test_build_router_context_adds_cross_location_link_guidance -q`, `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - 내부 라우트 첨부 파일명 슬롯 복원

- 작업 이름: 내부 행동 로그의 `route.resolved_slots.attachment_names`를 라우터 후보 슬롯으로 복원
- 진행상황: 완료
- 진행내용:
  - 최근 작업 상태 후보에는 `attachment_names`가 대상 힌트로 들어가지만, 내부 행동 로그의 `route.resolved_slots`를 병합하는 `SAFE_INTERNAL_ROUTE_SLOT_KEYS`에는 아직 포함되지 않은 점을 확인했다.
  - 문서 분석 작업이 실행 직후 내부 로그에는 첨부 파일명을 남기고 저장된 후보 slots가 비어 있는 경우, 라우터가 파일명 기반 후속 요청을 이어받는 단서가 약해질 수 있다.
  - `SAFE_INTERNAL_ROUTE_SLOT_KEYS`에 `attachment_name`, `attachment_names`를 추가해 내부 로그의 파일명 슬롯도 후보 슬롯으로 복원되게 했다.
  - `contract.pdf 다시 요약해줘`가 내부 행동 로그의 `attachment_names=['contract.pdf']` 단서를 통해 기존 문서 분석 상태에 연결되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_enriches_attachment_name_slots_from_internal_action_log tests/test_router_agent.py::test_router_fallback_enriches_state_candidate_hints_from_internal_action_log -q`, `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - 응답/검증 첨부 파일명 계약 보강

- 작업 이름: `attachment_names`가 최종 응답 참고와 실행 전 파일명 검증에도 반영되도록 개선
- 진행상황: 완료
- 진행내용:
  - 라우터 후보와 내부 행동 로그에는 `attachment_names`가 보존되지만, `ExecutionContext.for_response()`가 사용하는 안전 작업 상태 컨텍스트에는 해당 슬롯이 빠져 있어 응답 작성자가 파일명을 참고하지 못할 수 있음을 확인했다.
  - `RESPONSE_SAFE_TURN_STATE_SLOT_KEYS`에 `attachment_name`, `attachment_names`를 추가해 사용자에게 의미 있는 파일명은 유지하고, `context_link`, `linked_state_id` 같은 내부 메타데이터는 계속 숨기도록 했다.
  - 실행 전 검증의 파일명 값 수집도 `filename/filenames`만 보고 있어, linked state가 `attachment_names=['contract.pdf']`만 가진 경우 `invoice.pdf 다시 요약해줘` 같은 잘못된 연결을 충분히 걸러내지 못할 수 있음을 확인했다.
  - `collect_text_values_from_state()`가 `attachment_name`, `attachment_names`도 문서 파일명 값으로 수집하도록 보강했다.
  - 응답 컨텍스트에 `contract.pdf`는 남고 내부 라우팅 메타데이터는 숨겨지는지, 실행 전 검증이 첨부 파일명 일치/불일치를 구분하는지 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_keeps_attachment_names_from_linked_state tests/test_route_validation.py::test_validate_route_context_link_uses_attachment_names_for_filename_match -q`, `python3 -m pytest tests/test_response_composer.py tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - artifact 첨부 파일명 맥락 경로 보강

- 작업 이름: slots가 아니라 artifacts에 저장된 `attachment_name(s)`도 후속 맥락 판단과 응답에 반영
- 진행상황: 완료
- 진행내용:
  - 새 에이전트나 문서 분석 결과가 파일명을 slots가 아닌 artifacts에만 남기는 경우, 기존 보강만으로는 `contract.pdf 다시 요약해줘` 같은 후속 요청 연결 단서가 약해질 수 있음을 확인했다.
  - `add_turn_state_artifact_target_hints()`가 artifact의 `attachment_name`, `attachment_names`를 `target_hints`에 포함하도록 확장했다.
  - `response_safe_turn_state_context()`가 artifact의 `filenames`, `attachment_name`, `attachment_names`도 사용자 응답 작성용 안전 컨텍스트에 남기도록 했다.
  - 실행 전 검증의 파일명 수집도 artifact의 `filenames`, `attachment_name`, `attachment_names`를 함께 보도록 보강했다.
  - artifact에만 `attachment_names=['contract.pdf']`가 있는 경우에도 라우터 컨텍스트, 최종 응답 컨텍스트, 실행 전 파일명 일치/불일치 검증이 모두 동작하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_uses_artifact_attachment_names_as_target_hints tests/test_response_composer.py::test_execution_context_response_keeps_artifact_attachment_names_from_linked_state tests/test_route_validation.py::test_validate_route_context_link_uses_artifact_attachment_names_for_filename_match -q`, `python3 -m pytest tests/test_context_builder.py tests/test_response_composer.py tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - artifact 다중 파일명 target_hints 보강

- 작업 이름: artifacts의 `filenames` 배열도 라우터 대상 힌트로 보존
- 진행상황: 완료
- 진행내용:
  - artifact의 `filenames`는 응답 안전 컨텍스트와 실행 전 파일명 검증에는 반영되어 있었지만, 최근 작업 상태 후보의 `target_hints` 생성에는 빠져 있는 점을 확인했다.
  - 다중 파일 비교/분석 결과가 `artifacts.filenames=['contract.pdf', 'invoice.pdf']`처럼 저장되면, 사용자가 다음 턴에 특정 파일명으로 이어갈 때 라우터 후보 매칭 단서가 약해질 수 있다.
  - `add_turn_state_artifact_target_hints()`가 artifact의 `filenames`를 `target_hints`에 포함하도록 보강했다.
  - 문서 비교 상태의 artifact에 `filenames`만 있어도 `contract.pdf`, `invoice.pdf`가 라우터 컨텍스트의 대상 힌트로 출력되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_uses_artifact_filenames_as_target_hints tests/test_context_builder.py::test_build_router_context_uses_artifact_attachment_names_as_target_hints -q`, `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - 첨부 파일명 슬롯 검증 정규화

- 작업 이름: `attachment_name(s)`를 실행 전 검증의 문서 파일명 슬롯 계약에 포함
- 진행상황: 완료
- 진행내용:
  - `attachment_name`, `attachment_names`는 라우터 후보와 응답 컨텍스트에는 반영되었지만, `TEXT_SLOT_FAMILIES`와 pending 승인 슬롯 비교에서는 아직 문서 파일명 계열로 정규화되지 않는 점을 확인했다.
  - `TEXT_SLOT_FAMILIES["document"]`에 `attachment_name`, `attachment_names`를 추가해 라우터의 `resolved_slots`가 linked state와 맞는지 검증할 때 첨부 파일명도 비교하도록 했다.
  - pending 확인 승인 경로에서도 `attachment_name`과 `attachment_names`를 서로 대응되는 키로 보고, 대소문자 차이를 정규화해 비교하도록 했다.
  - 모델이 `resolved_slots.attachment_names=['invoice.pdf']`를 잘못 붙였는데 linked state는 `contract.pdf`인 경우 자동 실행하지 않고 확인으로 전환하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_accepts_equivalent_normalized_text_slots tests/test_route_validation.py::test_validate_route_context_link_clears_attachment_name_resolved_slot_mismatch -q`, `python3 -m pytest tests/test_route_validation.py tests/test_bot_helpers.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - URL artifact 배열 맥락 경로 보강

- 작업 이름: artifacts의 `urls` 배열도 라우터 힌트, 응답 컨텍스트, 실행 전 검증에 반영
- 진행상황: 완료
- 진행내용:
  - 웹검색/URL 결과는 여러 URL을 artifact에 배열로 남길 수 있지만, 기존 흐름은 artifact의 `url` 단수 값 위주로 target hint와 검증 값을 수집하는 점을 확인했다.
  - `add_turn_state_artifact_target_hints()`가 artifact의 `urls` 배열을 `target_hints`에 포함하도록 보강했다.
  - `response_safe_turn_state_context()`가 artifact의 `urls`, `url_titles`를 사용자 응답 작성용 안전 컨텍스트에 보존하도록 했다.
  - `collect_text_values_from_state()`가 linked state의 slots/artifacts 양쪽에서 `url`과 `urls`를 함께 수집하도록 해, 모델이 단수 `url` resolved slot을 반환해도 artifact의 복수 URL 배열과 비교할 수 있게 했다.
  - artifact에만 `urls=['https://openai.com', 'https://openai.com/models']`가 있는 경우 라우터 컨텍스트와 응답 컨텍스트에 URL들이 남는지, artifact URL과 다른 resolved slot URL은 실행 전 검증에서 확인으로 전환되는지 테스트했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_uses_artifact_urls_as_target_hints tests/test_response_composer.py::test_execution_context_response_keeps_artifact_urls_from_linked_state tests/test_route_validation.py::test_validate_route_context_link_uses_artifact_urls_for_url_resolved_slot_match -q`, `python3 -m pytest tests/test_context_builder.py tests/test_response_composer.py tests/test_route_validation.py tests/test_router_agent.py tests/test_web_search_agent.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - URL 제목 힌트와 artifact URL 배열 실행 슬롯 보강

- 작업 이름: 웹 artifact의 `url_titles`와 `urls` 배열을 후속 URL 실행에 더 직접적으로 활용
- 진행상황: 완료
- 진행내용:
  - 웹검색 결과는 사용자가 URL 문자열보다 제목으로 이어갈 가능성이 높지만, artifact의 `url_titles`는 응답 컨텍스트에는 남고 라우터 `target_hints`에는 빠져 있는 점을 확인했다.
  - `add_turn_state_artifact_target_hints()`가 artifact의 `url_title`, `url_titles`를 대상 힌트로 출력하도록 보강했다.
  - 라우터의 `artifact_urls()`가 artifact의 `url` 단수뿐 아니라 `urls` 배열도 읽도록 수정했다.
  - `검색 결과 링크 열어줘`처럼 URL을 직접 다시 쓰지 않은 요청에서도 artifact `urls=['https://openai.com', 'https://openai.com/models']`를 `resolved_slots.url/urls`로 복원할 수 있게 했다.
  - URL 제목과 URL 배열이 target_hints에 함께 출력되는지, artifact `urls` 배열만으로 web_url 실행 슬롯이 복원되는지 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_uses_artifact_urls_as_target_hints tests/test_router_agent.py::test_router_fallback_uses_artifact_urls_array_for_web_url_slots -q`, `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_web_search_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - 웹 결과 제목 기반 URL 선택 보강

- 작업 이름: 사용자가 URL 제목으로 특정 웹 결과를 가리키면 해당 URL만 실행 슬롯으로 복원
- 진행상황: 완료
- 진행내용:
  - `url_titles`를 라우터 힌트로 출력해도, web_url 실행 슬롯 복원은 artifact URL 배열의 첫 번째 URL을 기본으로 사용해 `Models 링크 열어줘`가 첫 링크를 열 가능성이 있음을 확인했다.
  - web_url용 `matched_web_url_artifact_slots()`를 추가해 artifact의 `urls` 배열과 `url_titles` 배열을 인덱스 기준으로 매칭하도록 했다.
  - 현재 사용자 문장이 URL 문자열 또는 해당 인덱스의 제목과 일치하면 그 URL 하나만 `resolved_slots.url/urls`로 복원한다.
  - URL 열기 전용 fallback 분기가 `resolved_slots_for_base_intent()`에 현재 사용자 문장을 넘기도록 수정해 제목 기반 매칭이 실제 실행 경로에서 작동하게 했다.
  - `Models 링크 열어줘`가 `https://openai.com/models`만 실행 슬롯으로 복원하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_uses_artifact_urls_array_for_web_url_slots tests/test_router_agent.py::test_router_fallback_uses_artifact_url_title_to_choose_specific_url -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_web_search_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - URL 제목 인덱스 정렬 보강

- 작업 이름: artifact 전체 제목이 있어도 `url_titles`와 `urls`의 인덱스 매칭이 밀리지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 웹 artifact에 전체 `title/name`과 개별 URL용 `url_titles`가 함께 있으면, 기존 helper가 모든 제목을 한 배열로 합쳐 `url_titles` 인덱스가 URL 배열과 어긋날 수 있음을 확인했다.
  - 개별 URL 선택에는 `url_title`, `url_titles`만 인덱스 기준 제목으로 사용하도록 `artifact_aligned_url_title_values()`를 분리했다.
  - artifact의 전체 `title/name`은 URL이 하나뿐인 경우에만 공유 제목으로 매칭 보조에 사용하도록 했다.
  - `title='OpenAI 검색 결과'`, `urls=['https://openai.com', 'https://openai.com/models']`, `url_titles=['Home', 'Models']`인 상태에서 `Models 링크 열어줘`가 두 번째 URL로 정확히 복원되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_uses_artifact_url_title_to_choose_specific_url tests/test_router_agent.py::test_router_fallback_keeps_url_titles_aligned_when_artifact_has_shared_title -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_web_search_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - 모호한 웹 URL 제목 매칭 확인 전환

- 작업 이름: 여러 URL이 같은 제목/검색어 단서에 걸릴 때 첫 URL을 임의 실행하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 제목 기반 URL 선택이 실패하거나 여러 URL에 동시에 매칭되면 기존 fallback이 다시 전체 URL 배열을 복원해 첫 URL 실행으로 흐를 수 있음을 확인했다.
  - `ambiguous_web_url_artifact_reference()`를 추가해 URL 후보가 여러 개이고 현재 메시지가 후보 제목/검색어에는 걸리지만 특정 URL 하나로 좁혀지지 않는 경우를 감지하도록 했다.
  - 이 경우 `context_link=clarify`로 전환해 “어떤 링크를 열까요?” 확인 질문으로 멈추도록 했다.
  - `OpenAI 링크 열어줘`가 `OpenAI Home`, `OpenAI Models` 두 결과에 모두 걸리는 경우 첫 URL을 임의 선택하지 않고 확인으로 전환하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_does_not_pick_first_url_when_title_matches_multiple_urls tests/test_router_agent.py::test_router_fallback_uses_artifact_url_title_to_choose_specific_url tests/test_router_agent.py::test_router_fallback_uses_artifact_urls_array_for_web_url_slots -q`, `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_web_search_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - 모호한 웹 URL 확인 후보 슬롯 보존

- 작업 이름: 여러 링크 중 어떤 URL을 열지 확인할 때 후보 URL/제목을 pending 슬롯에 남기는 기반 추가
- 진행상황: 완료
- 진행내용:
  - 모호한 웹 링크 요청은 확인 질문으로 전환되지만, `pending_resolved_slots`에 URL 후보가 없으면 다음 답변에서 어떤 URL 중 선택하는지 판단할 단서가 약한 점을 확인했다.
  - `ambiguous_web_url_artifact_reference()` 경로가 `pending_candidate_urls`, `pending_candidate_url_titles`를 `resolved_slots`에 남기도록 했다.
  - `safe_unlinked_clarify_slots()`가 링크 없는 clarify 라우트에서도 안전한 http/https URL 후보와 문자열 제목 후보를 보존하도록 확장했다.
  - 잘못된 `url` 실행 슬롯이나 잘못된 URL 문자열은 제거하고 후보 URL/제목/원문만 남기는 회귀 테스트를 추가했다.
  - `OpenAI 링크 열어줘`처럼 여러 웹 결과에 동시에 걸리는 요청이 확인 질문으로 전환될 때 후보 URL과 제목을 함께 남기는지 확인했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_does_not_pick_first_url_when_title_matches_multiple_urls tests/test_route_validation.py::test_validate_route_context_link_preserves_safe_unlinked_clarify_url_candidate_slots -q`, `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_bot_helpers.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - pending URL 후보 선택 라우팅 구현

- 작업 이름: 모호한 링크 확인 질문 이후 번호나 제목 답변으로 URL 하나를 선택
- 진행상황: 완료
- 진행내용:
  - URL 후보를 pending 슬롯에 남기는 기반은 생겼지만, 다음 사용자 답변이 `두 번째`, `Models`처럼 URL 후보 중 하나를 선택하는 경우 실제 `web_url` 실행 라우트로 복원하는 경로가 없음을 확인했다.
  - `route_from_pending_url_candidate_selection()`을 추가해 `pending_candidate_urls`, `pending_candidate_url_titles`가 있는 clarify 상태를 우선 확인하도록 했다.
  - `두 번째` 같은 순서 표현은 URL 배열 인덱스로 선택하고, 제목 조각은 `pending_candidate_url_titles`와 비교해 단일 URL로 좁히도록 했다.
  - 선택 성공 시 `web_url`, `context_link=continue`, 기존 `pending_linked_state_id`, 선택된 `url/urls`, `pending_original_text`를 복원한다.
  - 제목 선택 전용 매칭은 `OpenAI Models` 중 `Models`처럼 짧은 제목 조각만 답해도 후보 하나로 좁힐 수 있게 했다.
  - `두 번째`와 `Models` 답변이 각각 `https://openai.com/models`를 실행 슬롯으로 복원하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_does_not_pick_first_url_when_title_matches_multiple_urls tests/test_router_agent.py::test_router_fallback_selects_pending_url_candidate_by_ordinal tests/test_router_agent.py::test_router_fallback_selects_pending_url_candidate_by_title -q`, `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_bot_helpers.py tests/test_context_routing_matrix.py -q`를 통과했다.

## 2026-06-07 - pending URL 후보 선택 상태 만료 보강

- 작업 이름: URL 후보 선택 후 이전 확인 대기가 다음 맥락에 남지 않도록 정리
- 진행상황: 완료
- 진행내용:
  - `두 번째`, `Models`처럼 pending URL 후보 중 하나를 고른 뒤에도 기존 확인 상태가 남으면 다음 턴 라우터 컨텍스트에 오래된 후보가 다시 들어갈 수 있음을 확인했다.
  - `matching_pending_candidate_selection_states()`가 `pending_candidate_state_ids`뿐 아니라 top-level 또는 `pending_resolved_slots` 안의 `pending_candidate_urls`도 후보 선택 상태로 인식하도록 했다.
  - 선택 라우트의 `pending_original_text`가 기존 확인 상태와 일치할 때만 만료되므로, 다른 URL 확인 대기나 다른 원문의 확인 대기는 유지된다.
  - route validation 함수 테스트와 CLI 저장소 기반 만료 테스트를 추가해 URL 후보 확인 상태가 선택 후 만료되고 무관한 pending 상태는 유지되는지 검증했다.
  - `python3 -m pytest tests/test_route_validation.py::test_matching_pending_candidate_selection_states_matches_url_candidate_original_text tests/test_cli.py::test_cli_expires_selected_pending_url_candidate_context_link -q`를 통과했다.

## 2026-06-07 - 모델 라우터 pending 후보 선택 지침 보강

- 작업 이름: 모델 경로에서도 확인 후보 선택 답변을 일반 대화로 흘리지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - fallback은 `두 번째`, `Models` 같은 pending URL 후보 선택 답변을 복원하지만, 모델 프롬프트에는 pending 후보 선택 규칙이 충분히 명시되어 있지 않음을 확인했다.
  - 라우터 프롬프트에 `pending_candidate_state_ids`, `pending_candidate_urls`, `pending_original_text` 해석 규칙을 추가했다.
  - URL 후보 제목이 `OpenAI Home`, `OpenAI Models`일 때 사용자가 `두 번째` 또는 `Models`라고 답하면 `web_url`, `context_link=continue`, 선택 URL 하나, 기존 `pending_original_text`를 반환해야 한다고 명시했다.
  - 모델이 `Models` 같은 짧은 후보 제목 답변을 `chat`으로 잘못 분류해도 pending 후보가 있는 경우 fallback 보정이 한 번 개입하도록 `model_route_may_be_pending_candidate_selection()`을 추가했다.
  - 프롬프트 회귀 테스트와 모델 오분류 보정 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_agent_prefers_model_route_over_heuristic tests/test_router_agent.py::test_router_refines_model_chat_for_pending_url_candidate_title_selection -q`와 `python3 -m ruff check assistant_bot/agents/router.py tests/test_router_agent.py`를 통과했다.

## 2026-06-07 - pending URL 후보 취소 흐름 보강

- 작업 이름: URL 후보 확인 대기도 `아니/취소` 답변으로 깨끗하게 종료
- 진행상황: 완료
- 진행내용:
  - 일반 후속 작업 승인 대기는 `pending_linked_state_id`를 기준으로 취소되지만, URL 후보 확인처럼 `pending_candidate_urls`만 있는 대기 상태는 취소 경로에서 빠질 수 있음을 확인했다.
  - route validation에 `state_has_pending_confirmation()`을 추가해 pending linked state와 pending 후보 선택 상태를 같은 대기 확인 범주로 다루도록 했다.
  - 라우터 fallback이 부정/취소 답변을 처리할 때 `pending_linked_state_id`가 없는 URL 후보 선택 대기도 `cancel_pending`으로 라우팅하도록 했다.
  - Discord 봇 실행층의 pending context 취소도 `pending_candidate_urls` 대기를 인식해 해당 turn state를 만료하도록 바꿨다.
  - 라우터, route validation, 봇 실행층 테스트를 추가해 `아니 취소해`가 URL 후보 확인 대기를 취소하고 상태를 만료하는지 검증했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_cancels_pending_url_candidate_without_linked_state tests/test_route_validation.py::test_validate_route_context_link_allows_cancel_pending_url_candidate_state tests/test_bot_helpers.py::test_assistant_bot_cancels_pending_url_candidate_context_and_expires_state -q`를 통과했다.

## 2026-06-07 - 최종 응답 pending 내부 슬롯 비노출 보강

- 작업 이름: 응답 작성 모델 입력에서 pending 후보/라우팅 내부 슬롯 제거
- 진행상황: 완료
- 진행내용:
  - 최종 응답 composer는 성공 결과의 route 메타데이터는 숨기지만, `needs_input` 확인 질문이나 `cancel_pending` 성공 결과에서는 `pending_original_text`, `pending_resolved_slots`, `pending_candidate_urls` 같은 내부 슬롯이 구조화 결과로 전달될 수 있음을 확인했다.
  - `RESPONSE_PRIVATE_ROUTE_KEYS`에 pending linked state, pending 후보 URL/제목, pending 원문, 취소 대상 state id 계열 키를 추가했다.
  - `public_operation_result_for_response()`가 상태와 무관하게 항상 facts/slots를 sanitizing하도록 바꿔, 확인 질문 상태에서도 fallback_text/summary는 유지하되 내부 pending 슬롯은 최종 응답 작성 입력에서 제거한다.
  - cross-location 확인 질문, context cancellation, URL 후보 확인 응답에서 내부 pending 슬롯이 입력에 노출되지 않는 회귀 테스트를 추가/수정했다.
  - `python3 -m pytest tests/test_response_composer.py -q`, `python3 -m pytest tests/test_response_composer.py tests/test_bot_helpers.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`, `python3 -m ruff check assistant_bot/response_composer.py tests/test_response_composer.py`를 통과했다.

## 2026-06-07 - CLI pending 후보 취소 계약 동기화

- 작업 이름: 로컬 CLI에서도 URL 후보 확인 대기 취소를 Discord와 동일하게 처리
- 진행상황: 완료
- 진행내용:
  - Discord 봇 경로는 `pending_candidate_urls`만 있는 URL 후보 확인 대기도 취소/만료하도록 보강했지만, 로컬 CLI 경로는 여전히 `pending_linked_state_id`만 확인하고 있음을 확인했다.
  - CLI의 `cancel_pending` 처리 조건을 `state_has_pending_confirmation()` 기반으로 바꿔 pending linked state와 pending 후보 선택 대기를 같은 확인 대기 범주로 처리하도록 했다.
  - `handle_local_pending_context_cancellation()` helper를 분리해 CLI 실행 경로와 테스트가 같은 취소/만료 계약을 공유하도록 했다.
  - URL 후보 확인 pending state를 직접 만든 뒤 CLI helper가 `cancel_pending` 결과를 반환하고 turn state를 만료하는지 검증하는 테스트를 추가했다.
  - `python3 -m pytest tests/test_cli.py::test_cli_context_cancellation_uses_shared_result_contract tests/test_cli.py::test_cli_pending_context_cancellation_handles_url_candidate_state -q`, `python3 -m pytest tests/test_cli.py tests/test_route_validation.py tests/test_router_agent.py -q`, `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py`를 통과했다.

## 2026-06-07 - URL 후보 확인 버튼 취소 지원

- 작업 이름: URL 후보 확인 대기도 Discord 확인 버튼으로 취소 가능하게 보강
- 진행상황: 완료
- 진행내용:
  - `pending_candidate_urls`만 있는 URL 후보 확인 대기는 채팅 취소와 CLI 취소 경로에서는 처리되지만, `latest_pending_context_state()`와 버튼 표시 조건이 `pending_linked_state_id` 기준이라 Discord 버튼 경로에서는 대기 상태를 찾지 못할 수 있음을 확인했다.
  - `pending_context_states()`를 `state_has_pending_confirmation()` 기반으로 바꿔 pending linked state와 pending 후보 선택 상태를 모두 최신 확인 대기 상태로 반환하도록 했다.
  - `confirmation_action_for()`가 URL 후보 확인 같은 pending 후보 선택 상태에도 `continue_context` 확인 버튼을 붙이도록 `operation_result_has_pending_confirmation()`을 추가했다.
  - URL 후보 확인 응답에 승인/거부 버튼이 붙는지, 거부 버튼을 누르면 해당 pending turn state가 만료되고 `cancel_pending` 결과가 기록되는지 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_pending_context_states_include_url_candidate_confirmation tests/test_bot_helpers.py::test_assistant_bot_attaches_buttons_to_url_candidate_clarification tests/test_bot_helpers.py::test_context_confirmation_button_rejection_expires_pending_url_candidate_state -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_route_validation.py tests/test_cli.py tests/test_router_agent.py -q`, `python3 -m ruff check assistant_bot/bot.py assistant_bot/route_validation.py tests/test_bot_helpers.py tests/test_route_validation.py`를 통과했다.

## 2026-06-07 - URL 후보 선택 버튼 실행 구현

- 작업 이름: “어떤 링크를 열까요?” 확인에 후보 선택 버튼 제공
- 진행상황: 완료
- 진행내용:
  - URL 후보 확인에 단순 승인/거부 버튼을 붙이면 사용자가 실제로 고를 후보를 다시 채팅으로 입력해야 하므로, 확인 질문의 버튼 UX가 충분히 자연스럽지 않음을 확인했다.
  - `URLCandidateSelectionView`, `URLCandidateButton`, `URLCandidateCancelButton`을 추가해 URL 후보가 있는 확인 결과에는 `1. 제목`, `2. 제목`, `취소` 버튼을 표시하도록 했다.
  - 후보 버튼을 누르면 최신 pending URL 후보 상태에서 선택 URL을 복원하고, pending turn state를 만료한 뒤 `web_url` 에이전트에 선택 URL과 실행 컨텍스트를 전달하도록 했다.
  - 선택 결과에는 `selected_url`, `selected_url_title`, `selected_url_index`와 `url/urls/url_title` 슬롯을 남겨 내부 행동 기록과 후속 맥락에서 선택 사실을 참고할 수 있게 했다.
  - 일반 후속 작업 확인은 기존처럼 승인/거부 버튼을 유지하고, URL 후보 확인만 후보 선택 버튼으로 바뀌는지 테스트했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_attaches_buttons_to_context_clarification tests/test_bot_helpers.py::test_assistant_bot_attaches_buttons_to_url_candidate_clarification tests/test_bot_helpers.py::test_url_candidate_button_selection_dispatches_selected_url tests/test_bot_helpers.py::test_context_confirmation_button_rejection_expires_pending_url_candidate_state -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_route_validation.py tests/test_response_composer.py -q`, `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-07 - URL 후보 버튼 선택 맥락 기록 보강

- 작업 이름: URL 후보 버튼 선택 결과를 후속 맥락과 내부 행동 로그에 제목까지 보존
- 진행상황: 완료
- 진행내용:
  - URL 후보 버튼 선택은 선택 URL을 실행하지만, 후속 요청에서 사용자가 본 링크 제목(`OpenAI Models`)을 다시 가리킬 수 있으므로 URL 제목도 turn state와 내부 행동 로그에 남겨야 함을 확인했다.
  - `INTERNAL_ACTION_CONTEXT_KEYS`와 `infer_turn_slots()`에 `url_title`, `url_titles`, `selected_url`, `selected_url_title`을 추가해 버튼 선택 결과의 제목/선택 URL 단서가 내부 로그와 turn state 슬롯에 보존되도록 했다.
  - response-safe turn state 슬롯에도 `url_title`, `url_titles`를 추가해 최종 응답 작성 맥락에서 안전하게 링크 제목을 참고할 수 있게 했다.
  - URL 후보 버튼 선택 후 저장되는 turn state에 `url`, `urls`, `url_title`이 남고, 내부 행동 로그에 `url_title=OpenAI Models`가 포함되는지 검증했다.
  - `ExecutionContext.for_response()`가 linked state의 `url_title` 슬롯을 안전하게 보존하는 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_url_candidate_button_selection_dispatches_selected_url tests/test_response_composer.py::test_execution_context_response_keeps_url_title_slot_from_linked_state tests/test_context_builder.py tests/test_response_composer.py -q`, `python3 -m ruff check assistant_bot/bot.py assistant_bot/models.py tests/test_bot_helpers.py tests/test_response_composer.py`를 통과했다.

## 2026-06-07 - URL 제목 기반 후속 라우팅 검증 보강

- 작업 이름: 버튼으로 선택한 링크 제목을 다음 턴 라우터/검증층이 실제 대상 단서로 사용
- 진행상황: 완료
- 진행내용:
  - `url_title`을 turn state에 저장해도, route validation의 web 텍스트 패밀리는 `query/url/urls`만 검사해 제목 기반 슬롯 일치 여부를 충분히 검증하지 못함을 확인했다.
  - `TEXT_SLOT_FAMILIES["web"]`에 `url_title`, `url_titles`를 추가해 라우터가 복원한 URL 제목 슬롯도 linked state와 일치하는지 검증하도록 했다.
  - 라우터 fallback이 `OpenAI Models`처럼 복합 영문 제목 중 사용자가 `Models 다시 봐줘`처럼 일부 제목만 말하는 경우를 놓치는 문제를 확인했다.
  - `url_title/url_titles` 슬롯에는 단일 중요 토큰 매칭을 허용해, 사용자가 버튼에서 본 짧은 제목 조각으로도 최근 URL 상태를 이어받을 수 있게 했다.
  - `Models 다시 봐줘`가 `web_url`, `context_link=continue`, 선택 URL과 `url_title=OpenAI Models`를 복원하는 회귀 테스트를 추가했다.
  - 일치하는 URL 제목은 검증에서 유지되고, 다른 제목이 들어오면 자동 실행하지 않고 확인으로 전환되는 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_uses_url_title_slot_for_web_url_follow_up tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_url_title_request tests/test_route_validation.py::test_validate_route_context_link_clears_mismatched_url_title_request -q`, `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m ruff check assistant_bot/agents/router.py assistant_bot/route_validation.py tests/test_router_agent.py tests/test_route_validation.py`를 통과했다.

## 2026-06-07 - 에이전트 카탈로그 URL 제목 상태 단서 반영

- 작업 이름: `agent_catalog.json`의 웹 에이전트 후속 맥락 단서에 URL 제목 계약 추가
- 진행상황: 완료
- 진행내용:
  - 코드와 테스트는 URL 후보 선택 후 `url_title/url_titles`를 저장하고 라우팅/검증에 활용하지만, `agent_catalog.json`의 `state_outputs`에는 아직 URL 제목 단서가 선언되어 있지 않음을 확인했다.
  - `web_search` state_outputs에 `artifacts.url_titles`를 추가해 검색 결과 URL 배열과 제목 배열을 함께 남기는 계약을 명시했다.
  - `web_url` state_outputs에 `slots.urls`, `slots.url_title`, `slots.url_titles`, `artifacts.url_titles`를 추가해 직접 읽은 URL과 사용자가 본 링크 제목을 후속 맥락 단서로 선언했다.
  - registry prompt block 테스트가 `slots.url_title`, `artifacts.url_titles`를 포함하는지 확인하도록 보강했다.
  - artifact state output contract에서 `url_titles`를 URL artifact 계열로 인정하도록 테스트 계약을 업데이트했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`, `python3 -m pytest tests/test_agent_registry.py tests/test_router_agent.py tests/test_context_builder.py -q`, `python3 -m ruff check tests/test_agent_registry.py`를 통과했다.

## 2026-06-07 - 운영 CLI URL 제목 대상 단서 출력 보강

- 작업 이름: route/turn-states 운영 출력에서 라우터 대상 단서 확인 가능하게 보강
- 진행상황: 완료
- 진행내용:
  - turn state와 route preview 출력은 slots/artifacts JSON을 그대로 보여주지만, 라우터가 실제로 대조하는 `target_hints`가 별도로 보이지 않아 Discord 수동 테스트 중 후속 맥락 원인 추적이 어렵다는 점을 확인했다.
  - `format_turn_states()`와 route preview의 `format_route_state()`가 `turn_state_target_hints()`를 사용해 파일명, 제목, ID, URL 같은 대상 단서를 `target_hints` 줄로 출력하도록 했다.
  - turn-state 슬롯 기반 대상 단서 목록에 `queries`, `urls`, `url_title`, `url_titles`를 추가해 버튼으로 선택한 링크 제목이 artifact뿐 아니라 slots에만 있어도 라우터와 운영 출력 모두에서 같은 단서로 취급되도록 했다.
  - URL 제목과 URL이 `format_turn_states()` 출력의 `target_hints`에 포함되는지, route preview 출력에 `target_hints`가 포함되는지 테스트를 추가했다.
  - 슬롯에만 저장된 `url_title`도 라우터 컨텍스트의 `target_hints`에 포함되는지 직접 검증하는 테스트를 추가했다.
  - `python3 -m pytest tests/test_cli.py -q`, `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py -q`, `python3 -m pytest -q`(`824 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 채팅 기반 URL 후보 선택 제목 보존

- 작업 이름: 버튼이 아닌 채팅으로 URL 후보를 고를 때도 선택 URL 제목을 후속 맥락에 남김
- 진행상황: 완료
- 진행내용:
  - Discord 버튼으로 URL 후보를 선택하는 경로는 `selected_url_title`과 `url_title`을 남기지만, 라우터 fallback에서 사용자가 `두 번째`, `Models`처럼 채팅으로 후보를 선택하는 경로는 URL만 복원하고 제목을 잃는 점을 확인했다.
  - `select_pending_url_candidate()`가 선택 URL과 제목을 함께 반환하도록 바꾸고, pending URL 후보 선택 route의 `resolved_slots`에 `url_title`, `url_titles`를 함께 보존하도록 했다.
  - ordinal 선택, 제목 선택, 모델 모호 응답 보정 경로 모두 선택한 `OpenAI Models` 제목이 resolved slots에 남는지 테스트 기대값을 보강했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_selects_pending_url_candidate_by_ordinal tests/test_router_agent.py::test_router_fallback_selects_pending_url_candidate_by_title tests/test_router_agent.py::test_router_refines_model_chat_for_pending_url_candidate_title_selection tests/test_router_agent.py::test_router_fallback_uses_url_title_slot_for_web_url_follow_up -q`, `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest tests/test_bot_helpers.py tests/test_response_composer.py tests/test_context_builder.py -q`, `python3 -m pytest -q`(`824 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 로그 URL 제목 슬롯 복원 계약 보강

- 작업 이름: 내부 행동 로그의 `route.resolved_slots.url_title`도 라우터 후보 슬롯으로 복원
- 진행상황: 완료
- 진행내용:
  - `url_title/url_titles`는 turn state, 응답 안전 컨텍스트, 채팅/버튼 URL 후보 선택 경로에는 남지만, 내부 행동 로그의 `route.resolved_slots`를 라우터 후보 슬롯으로 병합하는 whitelist에는 빠져 있음을 확인했다.
  - `SAFE_INTERNAL_ROUTE_SLOT_KEYS`에 `url_title`, `url_titles`를 추가해 내부 행동 기록만 남아 있는 상황에서도 선택한 웹페이지 제목이 후속 맥락 슬롯으로 복원되도록 했다.
  - 내부 행동 로그 파서가 `url`과 `url_title`을 함께 slots로 복원하는 테스트를 추가했다.
  - `agent_catalog.json`에 선언된 대상 슬롯이 turn state `target_hints`뿐 아니라 내부 route slot merge whitelist에도 포함되는지 검증하는 카탈로그 계약 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_parses_internal_route_context_url_title_slots tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_internal_route_slot_merge tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_turn_state_hints -q`, `python3 -m pytest tests/test_agent_registry.py tests/test_router_agent.py tests/test_context_builder.py -q`, `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`(`826 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - Web URL 실행 결과 URL 제목 보존

- 작업 이름: 라우터가 넘긴 `url_title`을 Web URL Agent 결과에도 유지
- 진행상황: 완료
- 진행내용:
  - 라우터와 내부 행동 로그는 URL 후보 선택 제목을 보존하지만, `WebSearchAgent.read_urls()` 실행 결과는 `slots/artifacts`에 URL만 남겨 다음 턴으로 넘어가기 전에 제목 단서가 사라질 수 있음을 확인했다.
  - `linked_url_titles()`, `web_url_slots()`, `web_url_artifacts()` helper를 추가해 실행 컨텍스트의 `url_title/url_titles`와 linked state artifact 제목을 URL 순서에 맞춰 복원하도록 했다.
  - URL 읽기 성공/실패 결과 모두 `slots.url_title`, `slots.url_titles`, artifact `url_title/title`, facts `url_titles`를 가능한 경우 보존하도록 했다.
  - `Models 다시 봐줘`처럼 URL 문자열이 없는 후속 요청에서도 실행 결과에 `OpenAI Models` 제목이 남는지 테스트를 추가했다.
  - `python3 -m pytest tests/test_web_search_agent.py -q`, `python3 -m pytest tests/test_web_search_agent.py tests/test_router_agent.py tests/test_response_composer.py tests/test_context_builder.py -q`, `python3 -m pytest tests/test_agent_registry.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`(`827 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - Task Agent 생성 결과 후속 맥락 단서 명시

- 작업 이름: linked memory/task 변환으로 만든 할 일 결과에 task 슬롯과 artifact를 직접 남김
- 진행상황: 완료
- 진행내용:
  - `TaskAgent.create_task_from_title()`은 생성된 할 일의 ID와 제목을 facts에는 남기지만 `slots/artifacts/available_actions`를 직접 지정하지 않아, 공통 추론에 의존하고 있음을 확인했다.
  - 신규 할 일 생성 결과에 `subject`, `slots.task_id/task_ids`, task artifact, `show/complete/postpone/rename/delete` action을 명시하도록 했다.
  - 중복 열린 할일을 발견한 경우에도 기존 할 일 ID와 artifact/action을 남겨, 사용자가 바로 `그거 보여줘`, `그 작업 완료했어`처럼 이어갈 수 있게 했다.
  - 메모를 할 일로 추가하는 linked memory 변환 테스트에서 생성 결과의 subject, slots, artifacts, available_actions를 검증하도록 보강했다.
  - `python3 -m pytest tests/test_memory_store.py::test_task_agent_creates_task_from_linked_memory_reference -q`, `python3 -m pytest tests/test_memory_store.py -q`, `python3 -m pytest tests/test_bot_helpers.py::test_infer_available_actions_uses_route_validation_action_contract tests/test_agent_registry.py::test_agent_catalog_declares_literal_operation_result_actions tests/test_agent_registry.py::test_literal_operation_result_actions_match_route_validation_actions -q`, `python3 -m pytest -q`(`827 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - Reminder Agent 본문 슬롯 계약 정렬

- 작업 이름: 알림 본문을 `reminder_text` 표준 슬롯으로 보존
- 진행상황: 완료
- 진행내용:
  - 라우터는 메모/할 일에서 알림을 만들 때 `resolved_slots.reminder_text`를 사용하지만, Reminder Agent 실행 결과는 본문을 `text` 슬롯에만 남겨 카탈로그와 내부 맥락 계약이 어긋나는 점을 확인했다.
  - `agent_catalog.json`의 `manage_reminder.state_outputs`에 `slots.reminder_text`, `slots.human_remind_at`을 추가했다.
  - Reminder Agent의 알림 등록/상세 조회 결과가 `reminder_text`, `remind_at`, `human_remind_at`을 슬롯으로 함께 남기도록 했다.
  - 내부 행동 컨텍스트, turn state target hints, 내부 route slot merge whitelist, route validation 텍스트 슬롯 가족에 `reminder_text`를 추가해 후속 라우팅과 검증에서 같은 이름을 사용하도록 했다.
  - linked memory 기반 알림 생성과 linked reminder 조회 테스트에서 `reminder_text/human_remind_at` 보존을 검증하도록 보강했다.
  - `python3 -m pytest tests/test_memory_store.py::test_reminder_agent_creates_reminder_from_linked_memory_reference tests/test_memory_store.py::test_reminder_agent_show_prefers_linked_reminder_context -q`, `python3 -m pytest tests/test_agent_registry.py::test_registry_prompt_block_uses_catalog_examples tests/test_agent_registry.py::test_agent_catalog_slot_outputs_are_available_for_internal_action_context tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_turn_state_hints tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_internal_route_slot_merge -q`, `python3 -m pytest tests/test_memory_store.py tests/test_agent_registry.py -q`, `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`, `python3 -m pytest -q`(`827 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답 안전 컨텍스트 시간 슬롯 보존 계약 보강

- 작업 이름: linked state의 원본 기한/알림 시간을 최종 응답 작성 컨텍스트에 보존
- 진행상황: 완료
- 진행내용:
  - 응답 안전 컨텍스트에는 `human_due_at`, `human_remind_at`은 남지만 원본 `due_at`, `remind_at`은 빠져 있어, 사람이 읽는 시간 슬롯이 없는 오래된 상태에서는 최종 응답 작성자가 시간을 놓칠 수 있음을 확인했다.
  - `RESPONSE_SAFE_TURN_STATE_SLOT_KEYS`에 `due_at`, `remind_at`을 추가해 linked task/reminder 상태의 원본 시간도 응답 작성 모델에 전달되도록 했다.
  - linked task/reminder 상태에 사람이 읽는 시간 슬롯이 없어도 `2026-06-08 09:00`, `2026-06-08 10:00` 같은 원본 시간이 `ExecutionContext.for_response()`에 남는지 테스트를 추가했다.
  - `agent_catalog.json`의 사용자에게 보여도 되는 슬롯 출력이 응답 안전 컨텍스트 whitelist에도 포함되는지 검증하는 카탈로그 계약 테스트를 추가했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_keeps_raw_due_and_remind_times_from_linked_state tests/test_agent_registry.py::test_agent_catalog_user_visible_slot_outputs_are_available_for_response_context -q`, `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py tests/test_context_builder.py -q`, `python3 -m pytest tests/test_memory_store.py tests/test_route_validation.py tests/test_router_agent.py -q`, `python3 -m pytest -q`(`829 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 에이전트 카탈로그 ID 슬롯 단수/복수 계약 보강

- 작업 이름: 후속 행동 대상 ID를 단수/복수 슬롯 모두로 선언하고 실행 결과와 정렬
- 진행상황: 완료
- 진행내용:
  - 카탈로그 `state_outputs`에서 `memory_id`만 선언하거나 `memory_ids`만 선언하는 식의 단수/복수 불일치가 있으면 라우터가 후속 발화의 대상을 안정적으로 고르기 어렵다는 점을 확인했다.
  - `remember`, `update_memory`, `recall`, `list_memory`, `delete_memory`, `restore_memory`, `analyze_document`, `manage_task`, `web_search`의 `state_outputs`에 누락된 단수/복수 슬롯을 보강했다.
  - `MemoryAgent.remember_text()`와 검색 기반 메모 수정 성공 결과가 `subject`, `slots.memory_id/memory_ids`, memory artifact, 후속 action을 명시적으로 남기도록 정리했다.
  - `manage_task`, `analyze_document`, `web_search`가 실제 후속 행동에 필요한 슬롯을 카탈로그에 선언하는지 검증하는 테스트를 보강했다.
  - 어떤 ID 계열 슬롯이든 `slots.*_id`와 `slots.*_ids`를 함께 선언하도록 강제하는 카탈로그 계약 테스트를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_agent_catalog_state_outputs_include_actual_follow_up_actions tests/test_agent_registry.py::test_agent_catalog_declares_id_slot_variants_for_follow_up_targets -q`, `python3 -m pytest tests/test_agent_registry.py tests/test_memory_store.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_builder.py -q`, `python3 -m pytest -q`(`830 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 실행 결과 ID 슬롯 단수/복수 정렬

- 작업 이름: Task/Reminder/Document Agent 실행 결과가 후속 맥락 ID를 일관되게 남기도록 정리
- 진행상황: 완료
- 진행내용:
  - 카탈로그 계약은 단수/복수 ID 슬롯을 모두 선언하지만, 일부 실제 실행 결과는 단일 대상일 때 `task_id`, `reminder_id`, `document_id` 또는 복수 슬롯 중 하나만 남기는 경로가 있음을 확인했다.
  - `TaskAgent`의 할 일 생성, 최근 할 일 상세 조회, ID 기반 상세 조회 결과가 `_task_slots()`를 사용해 단일 결과에서는 `task_id/task_ids`를 함께 남기도록 했다.
  - `ReminderAgent`에 `_reminder_slots()`를 추가하고 알림 생성, 목록, ID 기반 조회, 상세 조회, 삭제 결과가 단일 결과에서는 `reminder_id/reminder_ids`를 함께 남기도록 했다.
  - `DocumentAnalysisAgent`에 `_document_slots()`를 추가하고 저장 문서 재분석 및 첨부 파일 분석 결과가 단일 문서에서는 `document_id/document_ids`를 함께 남기도록 했다.
  - linked task/reminder 상세 조회 테스트 기대값을 새 슬롯 계약에 맞게 보강했다.
  - `rg`로 에이전트 코드의 단수 ID only 슬롯 패턴을 재점검했고, 남은 직접 dict 슬롯은 단수/복수를 함께 선언하는 경로만 확인했다.
  - `python3 -m pytest tests/test_memory_store.py tests/test_document_analysis_agent.py tests/test_response_composer.py -q`(`130 passed`), `python3 -m pytest -q`(`830 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 target hint 계약 보강

- 작업 이름: 내부 행동 로그의 대상 단서도 카탈로그 target 슬롯 계약과 정렬
- 진행상황: 완료
- 진행내용:
  - turn state target hint, 내부 route slot merge, 응답 안전 컨텍스트는 `reminder_text`를 보존하지만, 내부 행동 로그에서 target hint를 만드는 키 목록에는 `reminder_text`가 빠져 있음을 확인했다.
  - 내부 행동 로그만 남은 상황에서도 “물 마시기 알림 다시 봐줘” 같은 후속 요청이 알림 본문과 대조될 수 있도록 `INTERNAL_ACTION_TARGET_HINT_KEYS`에 `reminder_text`를 추가했다.
  - 카탈로그가 선언한 target 슬롯이 내부 행동 target hint 키에도 포함되는지 검증하는 계약 테스트를 추가했다.
  - 내부 로그 reason의 `slots.reminder_text`가 router context의 `target_hints`에 포함되는지 컨텍스트 빌더 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_uses_internal_reminder_text_as_target_hint tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_internal_action_target_hints -q`, `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`408 passed`), `python3 -m pytest -q`(`832 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 검증 보정 슬롯 단수/복수 정렬

- 작업 이름: 라우터 검증 단계에서 보강한 pending/resolved ID 슬롯도 단수/복수 계약을 유지
- 진행상황: 완료
- 진행내용:
  - 에이전트 실행 결과와 카탈로그는 단일 대상 ID를 `*_id`와 `*_ids`로 함께 남기지만, `validate_route_context_link()`가 linked state에서 슬롯을 보강하는 경로는 단수 또는 복수 중 하나만 남기는 점을 확인했다.
  - `add_single_or_many_slot()`이 단일 ID를 보강할 때 단수/복수 슬롯을 함께 채우고, 이미 한쪽만 있는 경우 빠진 짝을 보충하도록 수정했다.
  - 다만 resolved slot mismatch처럼 검증기가 의도적으로 슬롯을 비운 clarify 결과는 다시 채우지 않도록 `build_context_clarification_result()`의 보강 조건을 좁혔다.
  - 직접 `clarify`로 들어온 정상 교차 위치 확인 경로와, `continue`가 검증에서 `clarify`로 바뀐 경로 모두 pending 슬롯에 단수/복수 ID가 함께 남는지 테스트 기대값을 보강했다.
  - mismatch로 인한 clarify에서는 `pending_resolved_slots`가 빈 상태로 유지되어 잘못된 대상에 대한 버튼 승인/후속 실행이 생기지 않도록 기존 안전 테스트를 유지했다.
  - `python3 -m pytest tests/test_route_validation.py -q`(`121 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py tests/test_cli.py -q`(`392 passed`), `python3 -m pytest -q`(`834 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 결과 슬롯 파싱 보강

- 작업 이름: 내부 행동 로그의 `slots` 구간을 라우터 후보 슬롯으로 복원
- 진행상황: 완료
- 진행내용:
  - 내부 행동 결과 로그는 `slots={...}`를 남기고 target hint 생성에는 활용하지만, 라우터의 `internal_action_context_by_linked_state()`는 route의 `resolved_slots`만 후보 슬롯으로 복원하고 있어 결과 슬롯 일부가 구조화 컨텍스트로 쓰이지 못하는 점을 확인했다.
  - `parse_internal_action_result_slots()`를 추가해 내부 행동 로그의 `slots` 구간을 안전하게 파싱하고, `SAFE_INTERNAL_ROUTE_SLOT_KEYS`에 포함된 슬롯만 후보 슬롯으로 병합하도록 했다.
  - route `resolved_slots`가 있으면 그것을 우선하고, 결과 `slots`는 빠진 값을 보완하도록 해 라우터의 직접 판단을 덮어쓰지 않게 했다.
  - 실제 `internal_action_result_reason()`으로 생성된 로그에서 route resolved slots가 비어 있어도 결과 `task_id/task_ids`가 후보 슬롯으로 복원되는 테스트를 추가했다.
  - 기존 웹 검색 내부 행동 로그 파싱 테스트는 결과 `slots.query`도 복원되는 새 계약에 맞게 기대값을 보강했다.
  - `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py -q`(`127 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`(`504 passed`), `python3 -m pytest -q`(`835 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 artifact 슬롯 복원 보강

- 작업 이름: 내부 행동 로그의 `artifacts` 구간도 라우터 후보 슬롯으로 복원
- 진행상황: 완료
- 진행내용:
  - 내부 행동 결과 로그는 artifact 기반으로 `document_ids`, `task_ids`, `urls`, `url_titles` 같은 값을 남기지만, 라우터 후보 슬롯 복원은 route/result slots만 읽어 artifact-only 결과의 구조화 ID 비교가 약해질 수 있음을 확인했다.
  - `parse_internal_action_artifact_slots()`를 추가해 내부 행동 로그의 `artifacts` 구간에서 안전한 ID/URL 계열 값만 후보 슬롯으로 복원하도록 했다.
  - 단일 artifact ID 또는 URL인 경우 `document_id/document_ids`, `task_id/task_ids`, `url/urls`, `url_title/url_titles`처럼 단수/복수 슬롯을 함께 채우도록 했다.
  - 병합 우선순위는 artifact slots < result slots < route resolved_slots로 두어, 라우터가 직접 선택한 슬롯을 artifact가 덮어쓰지 않게 했다.
  - 실제 `internal_action_result_reason()`이 artifact만 남긴 문서 분석 결과에서도 `document_id/document_ids`가 후보 슬롯으로 복원되는 테스트를 추가했다.
  - 웹 검색 내부 행동 후보는 artifact의 URL 제목까지 구조화 슬롯으로 복원되도록 기대값을 보강했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_parses_actual_internal_action_result_reason tests/test_router_agent.py::test_router_parses_internal_action_result_slots_without_route_resolved_slots tests/test_router_agent.py::test_router_parses_internal_action_artifacts_as_candidate_slots -q`, `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`(`505 passed`), `python3 -m pytest -q`(`836 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation 이력 압축 파싱 보존

- 작업 이름: 긴 route validation 로그에서도 자동 연결 제거/확인 이력을 라우터가 읽을 수 있게 보존
- 진행상황: 완료
- 진행내용:
  - 긴 검색어/긴 reason 때문에 route validation 로그가 압축될 때 `validation_context` dict의 시작 부분이 잘려 라우터가 `internal_validation_removed_state_ids()`로 제거 이력을 복원하지 못하는 점을 테스트로 확인했다.
  - `route_validation_summary()`가 `validation_context` 전체를 통째로 자르지 않고, snapshot 내부의 긴 slot 값만 개별 압축하도록 변경했다.
  - 전체 요약 압축 시 `validation_context=` 구간은 시작부터 온전히 보존하도록 `compact_route_validation_summary()`를 보강했다.
  - 라우터의 `parse_internal_action_validation_context()`가 구조화된 `| validation_context=`를 우선 읽고, 원본 저장 로그처럼 세미콜론/공백 뒤에 오는 `validation_context=`도 fallback으로 읽도록 했다.
  - 긴 route validation 로그에서도 제거된 state id가 `{30}`으로 복원되는지 CLI 테스트를 보강했다.
  - `python3 -m pytest tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment tests/test_cli.py::test_log_route_validation_if_changed_compacts_long_adjustment tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router tests/test_router_agent.py::test_router_parses_internal_validation_removed_state_ids tests/test_router_agent.py::test_router_parses_internal_validation_clarified_state_ids -q`, `python3 -m pytest tests/test_cli.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`(`552 passed`), `python3 -m pytest -q`(`836 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 route 정보 압축 파싱 보존

- 작업 이름: 긴 route resolved slot이 있어도 내부 행동 route dict를 라우터가 파싱 가능하게 보존
- 진행상황: 완료
- 진행내용:
  - 내부 행동 결과 로그의 `route={...}` 구간은 `linked_state_id`, `context_link`, `resolved_slots`를 담지만, 기존에는 route dict 전체 문자열을 길이 기준으로 잘라 dict 구조가 깨질 수 있음을 확인했다.
  - `safe_internal_action_route_values()`가 route dict 전체를 자르기보다 resolved slot 값만 개별적으로 압축하도록 변경했다.
  - `internal_action_result_reason()`은 이미 압축된 구조화 route 값을 그대로 기록하도록 바꿔 라우터가 `parse_internal_action_route_value()`로 다시 읽을 수 있게 했다.
  - 긴 `query`와 긴 `pending_original_text`가 포함된 실제 `internal_action_result_reason()` 출력에서도 `linked_state_id=34`와 `resolved_slots.query`가 복원되는 테스트를 추가했다.
  - `pending_original_text`는 라우터 후보 슬롯으로는 복원하지 않는 기존 안전 정책을 유지했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_parses_internal_action_route_context_with_long_resolved_slot_value tests/test_router_agent.py::test_router_parses_actual_internal_action_result_reason tests/test_context_builder.py::test_build_router_context_keeps_parseable_internal_route_context_when_trimmed -q`, `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py tests/test_cli.py -q`(`553 passed`), `python3 -m pytest -q`(`837 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 artifact 파서 공통 계약 보강

- 작업 이름: 새 에이전트 artifact 출력이 라우터 후보 슬롯 복원에서 누락되지 않도록 계약화
- 진행상황: 완료
- 진행내용:
  - 개별 문서/웹 artifact 파싱 테스트는 있었지만, `agent_catalog.json`에 선언된 artifact 출력이 모두 내부 route slot merge whitelist와 맞는지 확인하는 공통 계약이 약한 점을 확인했다.
  - 카탈로그의 `artifacts.*` 출력 키가 `SAFE_INTERNAL_ROUTE_SLOT_KEYS`에 포함되는지 검증하는 테스트를 추가했다.
  - `parse_internal_action_artifact_slots()`가 메모, 문서, 할 일, 알림, URL, URL 제목 계열 artifact 출력을 모두 안전 슬롯으로 복원하고 단일 값이면 단수/복수 슬롯을 함께 채우는지 테스트를 추가했다.
  - 이 계약으로 새 에이전트가 artifact 출력을 추가할 때, 라우터 후보 슬롯 복원 whitelist를 함께 갱신하지 않으면 테스트가 실패하도록 했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_internal_action_artifact_slots_cover_known_artifact_outputs tests/test_router_agent.py::test_router_parses_internal_action_artifacts_as_candidate_slots tests/test_agent_registry.py::test_agent_catalog_artifact_outputs_are_available_for_internal_route_slot_merge -q`, `python3 -m pytest tests/test_agent_registry.py tests/test_router_agent.py tests/test_context_builder.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`(`508 passed`), `python3 -m pytest -q`(`839 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 구조화 컨텍스트 trim 필드 경계 보존

- 작업 이름: router context가 길어질 때 내부 행동 라인을 중간 글자에서 자르지 않도록 개선
- 진행상황: 완료
- 진행내용:
  - `trim_context_lines()`가 첫 body 라인이 너무 길면 문자열 꼬리를 임의 위치에서 잘라 넣어, 내부 행동/turn state 라인이 필드 중간에서 시작할 수 있는 점을 확인했다.
  - 구조화 라인이 잘릴 때는 ` | ` 필드 경계 이후부터 보존하도록 `trim_context_line_tail_at_field_boundary()`를 추가했다.
  - 기존처럼 최신 내부 행동의 핵심 `route_context`, `target_hints` 같은 후반 필드는 유지하되, 잘린 라인이 임의 토큰 중간에서 시작하는 위험을 줄였다.
  - 긴 내부 행동 로그가 trim된 상황에서도 raw 장문 값은 빠지고, `linked_state_id`가 포함된 route context와 target hint가 보존되는지 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_does_not_include_partial_internal_action_line_when_trimmed tests/test_context_builder.py::test_build_router_context_keeps_latest_internal_action_when_trimmed tests/test_context_builder.py::test_build_router_context_keeps_parseable_internal_route_context_when_trimmed -q`, `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py tests/test_cli.py -q`(`555 passed`), `python3 -m pytest -q`(`840 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 실행 컨텍스트 슬롯 보강 계약화

- 작업 이름: 라우터가 확정한 linked state의 ID/아티팩트 단서를 에이전트 실행 컨텍스트까지 보존
- 진행상황: 완료
- 진행내용:
  - `validate_route_context_link()`는 일부 경로에서 linked state 기반 슬롯 보강을 수행하지만, `build_execution_context()` 자체는 라우터의 `resolved_slots`를 그대로 넘겨 다른 호출 경로나 향후 에이전트 추가 시 실행 컨텍스트 단서가 약해질 수 있음을 확인했다.
  - `build_execution_context()`가 linked state를 실제로 찾은 경우 `enrich_resolved_slots_from_linked_state()`를 통해 단수/복수 ID 슬롯과 artifact 기반 대상 슬롯을 중앙에서 보강하도록 변경했다.
  - 이 보강은 `linked_state_id`가 검증 후 살아 있고 linked state가 조회된 경우에만 수행되므로, 새 요청을 이전 맥락에 억지로 연결하지 않는다.
  - 문서 artifact만 있는 linked state에서도 `document_id/document_ids`가 실행 컨텍스트에 복원되는지, 라우터가 넘긴 `pending_original_text` 같은 슬롯은 유지하면서 `task_id/task_ids`만 보강되는지 테스트를 추가했다.
  - 버튼 승인/채팅 승인/모델 라우팅 후 dispatch 테스트 기대값을 새 계약에 맞춰 보강해, 연결 확정 뒤 에이전트가 단수/복수 ID 양쪽을 안정적으로 참조할 수 있게 했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_route_validation.py tests/test_bot_helpers.py -q`(`254 passed`), `python3 -m pytest -q`(`842 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 날씨 에이전트 실행 슬롯 활용 보강

- 작업 이름: linked state 객체가 없어도 검증된 실행 슬롯의 지역 정보를 날씨 재시도에 사용
- 진행상황: 완료
- 진행내용:
  - 에이전트별로 `execution_context.resolved_slots`를 실제 행동 판단에 우선 활용하는지 점검했다.
  - 메모, 문서, 할 일, 알림, 웹 URL/검색은 resolved slot을 먼저 보고 linked state를 보조로 쓰는 구조가 이미 잡혀 있음을 확인했다.
  - 날씨 에이전트는 `context_link`가 살아 있고 `resolved_slots.location`이 있어도 linked state 객체가 없으면 지역을 무시해, 라우터가 복원한 슬롯이 실행 단계에서 사라질 수 있는 취약점을 확인했다.
  - `context_link="none"`인 새 요청에서는 슬롯을 계속 무시하되, `retry/continue/modify`처럼 검증된 실행 컨텍스트에서는 `resolved_slots.location`만으로도 지역을 복원하도록 수정했다.
  - `다시 확인해줘` 요청에서 `context_link=retry`와 `location=원주` 슬롯만 있어도 원주 날씨를 조회하는 테스트를 추가하고, `context_link=none`에서는 여전히 지역을 묻는 안전 테스트를 유지했다.
  - `python3 -m pytest tests/test_weather_agent.py tests/test_bot_helpers.py tests/test_context_routing_matrix.py -q`(`240 passed`), `python3 -m pytest -q`(`842 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 버튼 실행 결과 내부 route 로그 복원

- 작업 이름: 버튼 승인으로 실행된 결과도 내부 행동 로그에서 라우터가 같은 형식으로 읽을 수 있게 보강
- 진행상황: 완료
- 진행내용:
  - 일반 메시지 실행 결과는 `execution_context`를 함께 넘겨 내부 행동 로그에 `route={...}`가 남지만, 버튼 승인 결과는 `attach_execution_context_metadata()`로 결과 슬롯/팩트에만 route 메타데이터가 붙는 경로가 있음을 확인했다.
  - `record_internal_action_result()`가 별도 `execution_context`를 받지 못해도 결과의 `context_link`, `linked_state_id`, `linked_intent`, `linked_subject`, `resolved_slots`에서 안전한 route dict를 복원하도록 보강했다.
  - 버튼 승인 결과처럼 결과 객체에만 route 메타데이터가 있는 경우에도 내부 행동 로그가 `route={...}`를 포함하고, 라우터의 `internal_action_context_by_linked_state()`가 다시 `task_id/task_ids`를 복원하는 테스트를 추가했다.
  - `pending_original_text`는 로그에는 보존하되 라우터 후보 슬롯으로는 복원하지 않는 기존 안전 정책을 유지했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_restores_route_from_attached_result_metadata tests/test_bot_helpers.py::test_record_internal_action_result_logs_execution_context_link tests/test_router_agent.py::test_router_parses_actual_internal_action_result_reason -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_router_agent.py tests/test_context_builder.py -q`(`227 passed`), `python3 -m pytest -q`(`843 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 메모 대기 결과 구조화 단서 보강

- 작업 이름: 메모 대기 저장/취소 결과가 다음 라우팅 컨텍스트에 충분한 슬롯과 artifact로 남도록 개선
- 진행상황: 완료
- 진행내용:
  - Discord 메모 대기 처리 결과가 CLI 경로보다 `subject`, `slots`, `artifacts`, `available_actions`를 덜 채워, 저장 자체는 성공해도 다음 맥락 후보와 내부 행동 로그 단서가 약해질 수 있음을 확인했다.
  - 메모 대기 취소 결과에는 `canceled_target=memory_capture` 슬롯을 추가해 취소 대상이 내부 로그에 구조화되도록 했다.
  - 메모 대기 중 정확한 중복, 유사 메모 제안, 새 메모 저장 성공 결과에 `memory_id/memory_ids`, `memory_text` 또는 `new_text`, memory artifact, 후속 action을 명시하도록 보강했다.
  - 직접 `handle_pending_memory_capture()` 테스트는 응답 구조를 확인하도록 확장했고, 실제 `on_message()` 흐름에서도 저장 결과가 turn state와 `memory:result` 내부 행동 로그에 남는지 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_saves_next_message_from_pending_memory_capture tests/test_bot_helpers.py::test_on_message_records_pending_memory_capture_as_context_state_and_internal_log tests/test_bot_helpers.py::test_assistant_bot_cancels_pending_memory_capture -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_agent_registry.py tests/test_context_builder.py tests/test_router_agent.py -q`(`257 passed`), `python3 -m pytest -q`(`844 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 응답용 resolved slot 비공개 키 필터링

- 작업 이름: 최종 응답 생성 컨텍스트에서 내부 라우팅 보조 슬롯을 숨김
- 진행상황: 완료
- 진행내용:
  - 에이전트 실행용 `ExecutionContext.for_agent()`는 `pending_original_text`, `pending_resolved_slots` 같은 내부 보조 슬롯까지 볼 필요가 있지만, 최종 응답 생성용 `for_response()`가 같은 원본 dict를 그대로 넘기면 사용자-facing 답변 모델 입력에 내부 route 키가 섞일 수 있음을 확인했다.
  - `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`와 `response_safe_resolved_slots()`를 추가해 `for_response()`의 `라우터 복원 슬롯`에는 실제 대상 단서(`task_id`, `memory_id` 등)만 남기고 내부 pending/link 메타데이터는 제거하도록 했다.
  - `for_agent()`에는 원본 슬롯이 유지되고 `for_response()`에서만 숨겨지는지 테스트를 추가해, 실행 정확도와 응답 안전성을 분리했다.
  - 기존 linked state/내부 행동 로그 숨김 테스트와 함께 검증하여 `pending_original_text`, `pending_linked_state_id`, `pending_resolved_slots`, `linked_state_id`, `resolved_slots`가 응답 컨텍스트에 노출되지 않도록 고정했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_hides_private_route_metadata_from_resolved_slots tests/test_response_composer.py::test_execution_context_response_hides_private_route_metadata_from_linked_state tests/test_response_composer.py::test_response_composer_treats_internal_action_context_as_hidden_reference -q`(`3 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_bot_helpers.py -q`(`152 passed`), `python3 -m pytest -q`(`845 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 응답 비공개 route 키 공통 계약화

- 작업 이름: 응답 결과 필터와 실행 컨텍스트 응답 필터가 같은 비공개 route 키 목록을 사용하도록 정리
- 진행상황: 완료
- 진행내용:
  - `response_composer.py`와 `models.py`가 거의 같은 비공개 route/pending 키 목록을 각각 들고 있어, 새 pending 키가 추가될 때 한쪽만 갱신될 위험을 확인했다.
  - `response_composer.py`가 `models.RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`를 공유하도록 바꿔 `OperationResult` 공개화와 `ExecutionContext.for_response()`가 같은 기준으로 내부 키를 숨기게 했다.
  - `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`의 모든 키를 샘플링해 `public_operation_result_for_response()`와 `ExecutionContext.for_response()` 양쪽에서 제거되는지 확인하는 계약 테스트를 추가했다.
  - 실제 대상 슬롯인 `task_id`는 유지되도록 해 응답 정확성에 필요한 단서는 보존하고 내부 라우팅 메타데이터만 숨기도록 했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context tests/test_response_composer.py::test_response_composer_hides_private_route_metadata_from_success_result tests/test_response_composer.py::test_execution_context_response_hides_private_route_metadata_from_resolved_slots -q`(`3 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_agent_registry.py -q`(`87 passed`), `python3 -m pytest -q`(`846 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답 컨텍스트 우선순위 기반 절단

- 작업 이름: 최종 답변 모델이 연결된 작업 상태를 내부 행동 로그보다 먼저 보도록 응답 컨텍스트 절단 방식 개선
- 진행상황: 완료
- 진행내용:
  - `ExecutionContext.for_response()`가 전체 문자열을 단순 앞부분 기준으로 자르면, 내부 행동 로그나 긴 보조 맥락이 연결된 이전 작업 상태를 밀어내 답변 모델이 실제 대상 ID/제목을 놓칠 수 있는 위험을 확인했다.
  - 응답용 컨텍스트 생성 순서를 라우터 복원 슬롯, 라우팅 근거, 연결된 이전 작업 상태, 비공개 내부 참고 순으로 조정해 실제 후속 답변에 필요한 단서를 먼저 보존하도록 했다.
  - `join_context_parts_limited()`와 `truncate_context_block()`을 추가해 컨텍스트 조각 단위로 제한 길이를 적용하고, 마지막 조각은 라벨을 유지한 채 안전하게 줄이도록 했다.
  - 긴 내부 행동 로그가 있어도 `메모 8` 같은 연결 상태 정보가 먼저 유지되고, 오래된 내부 검증 로그는 제한 길이 밖으로 밀리는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_keeps_resolved_slots_when_truncated tests/test_response_composer.py::test_execution_context_response_prioritizes_linked_state_over_internal_action_when_truncated tests/test_response_composer.py::test_response_composer_treats_internal_action_context_as_hidden_reference -q`(`3 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_bot_helpers.py -q`(`154 passed`), `python3 -m pytest -q`(`847 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 후속 후보 선택 순서 고정

- 작업 이름: 사용자가 본 pending 후보 순서와 라우터의 서수 선택 순서를 일치시킴
- 진행상황: 완료
- 진행내용:
  - 후속 요청 대상 후보가 여러 개라 `pending_candidate_state_ids=[12, 22]`처럼 저장된 뒤, 사용자가 `첫 번째`, `두 번째`로 고르는 흐름을 점검했다.
  - 기존 `select_pending_candidate()`는 저장된 후보 ID 순서가 아니라 현재 라우터 컨텍스트 후보 목록 순서로 `target_candidates`를 만들 수 있어, 후보 목록이 최신순/우선순위로 재정렬되면 사용자가 본 1번과 실제 선택 대상이 달라질 수 있음을 확인했다.
  - 후보 선택 시 `pending_candidate_state_ids`에 저장된 순서를 기준으로 `target_candidates`를 재구성하도록 수정해, 사용자가 확인 질문에서 본 순서가 실제 실행 순서로 유지되게 했다.
  - 후보 목록이 `[22, 12]` 역순으로 들어와도 `pending_candidate_state_ids=[12, 22]`이면 `첫 번째`가 state 12를 선택하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_select_pending_candidate_uses_saved_candidate_id_order_for_ordinals tests/test_router_agent.py::test_router_fallback_selects_pending_url_candidate_by_ordinal -q`(`2 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`350 passed`), `python3 -m pytest -q`(`848 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다중 후속 후보 공개 목록 보강

- 작업 이름: 대상 후보가 여러 개인 확인 질문에서 답변 모델이 후보 목록을 잃지 않도록 공개 `items` 추가
- 진행상황: 완료
- 진행내용:
  - 다중 후보 확인 라우팅은 `pending_candidate_state_ids`를 슬롯에 저장하지만, 응답 생성 단계에서는 이 슬롯이 내부 route 키로 숨겨져 후보 목록 설명이 fallback 문장에만 의존할 수 있음을 확인했다.
  - `build_context_clarification_result()`가 `execution_context.turn_state_context`에서 pending 후보의 `subject`, `intent`, `location`을 찾아 공개 `items`로 포함하도록 보강했다.
  - pending ID와 원문 같은 실행용 내부 슬롯은 계속 숨기되, 사용자가 실제로 선택해야 하는 후보 순번/제목/종류/위치는 구조화된 실행 결과로 응답 모델에 전달되게 했다.
  - 실제 저장된 작업 상태 후보가 있는 상황에서 `pending_candidate_state_ids=[8, 7]` 순서 그대로 `OpenAI 최신 뉴스`, `원주 날씨` 후보 목록이 `items`에 들어가는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_stops_before_dispatch_when_route_needs_context_clarification tests/test_response_composer.py::test_response_composer_preserves_cross_location_clarification_as_question -q`(`2 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_response_composer.py tests/test_context_builder.py -q`(`154 passed`), `python3 -m pytest -q`(`848 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다중 후보 확인의 잘못된 승인 버튼 제거

- 작업 이름: 대상 후보가 여러 개인 확인 질문에는 승인/거부 버튼을 붙이지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - `pending_candidate_state_ids`가 있는 다중 후보 확인 결과도 기존에는 `operation_result_has_pending_confirmation()` 때문에 일반 `승인/거부` 버튼이 붙을 수 있음을 확인했다.
  - 다중 후보 상황에서 `승인`은 어느 후보를 승인하는지 의미가 없고, 버튼 승인 경로에서 대상 없이 실행 검증 실패로 이어질 수 있어 사용자 경험과 맥락 정확도를 해치는 위험으로 판단했다.
  - `confirmation_action_for()`가 `pending_linked_state_id`가 있는 단일 작업 이어가기 확인에만 `continue_context` 승인/거부 버튼을 붙이도록 조건을 좁혔다.
  - URL 후보는 기존처럼 URL 전용 선택 버튼을 유지하고, 다중 작업 후보는 공개 `items`와 텍스트 선택(`첫 번째`, `두 번째`) 흐름으로 처리되도록 분리했다.
  - 단일 작업 확인에는 `승인/거부`가 유지되고, URL 후보에는 URL 선택 버튼이 유지되며, 다중 작업 후보에는 잘못된 승인/거부 버튼이 붙지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_attaches_buttons_to_context_clarification tests/test_bot_helpers.py::test_assistant_bot_attaches_candidate_buttons_to_multiple_candidate_clarification tests/test_bot_helpers.py::test_assistant_bot_attaches_buttons_to_url_candidate_clarification -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_response_composer.py -q`(`115 passed`), `python3 -m pytest -q`(`849 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다중 후속 후보 선택 버튼 도입

- 작업 이름: 여러 작업 후보 확인 질문에서 사용자가 버튼으로 후보를 직접 선택할 수 있게 개선
- 진행상황: 완료
- 진행내용:
  - 다중 작업 후보에는 잘못된 `승인/거부` 버튼을 제거했지만, 사용자가 여전히 채팅으로 `첫 번째`, `두 번째`라고 답해야 하는 불편함이 남아 있음을 확인했다.
  - 공개 `items`에 들어간 후보 목록을 기반으로 `StateCandidateSelectionView`, `StateCandidateButton`, `StateCandidateCancelButton`을 추가해 Discord에서 후보 선택 버튼을 표시하도록 했다.
  - 후보 버튼을 누르면 새 전용 실행 로직을 만들지 않고, 기존 라우터에 `첫 번째` 같은 선택 텍스트를 다시 전달해 채팅 선택과 동일한 pending 후보 선택, route validation, dispatch 흐름을 재사용하도록 했다.
  - 선택된 후보 route가 `clarify`로 바뀌면 기존 확인 질문 생성 흐름으로 돌아가고, 실행 가능한 `continue/retry/modify`이면 원래 `pending_original_text`를 전문 에이전트에 전달하도록 했다.
  - 버튼 선택 결과도 대화 기록, 작업 상태, 내부 행동 로그에 남기도록 기존 버튼 처리 패턴과 맞췄다.
  - 다중 후보 확인에는 `1. OpenAI 최신 뉴스`, `2. 원주 날씨`, `취소` 버튼이 붙고, 1번 버튼 선택 시 pending 후보가 만료되며 선택된 `web_search` 상태로 dispatch되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_attaches_candidate_buttons_to_multiple_candidate_clarification tests/test_bot_helpers.py::test_state_candidate_button_selection_routes_and_dispatches_selected_state tests/test_bot_helpers.py::test_assistant_bot_attaches_buttons_to_url_candidate_clarification tests/test_bot_helpers.py::test_url_candidate_button_selection_dispatches_selected_url -q`(`4 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`326 passed`), `python3 -m pytest -q`(`850 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 버튼 선택 결과 응답 컨텍스트 복원

- 작업 이름: 버튼으로 실행된 후속 작업도 최종 답변 모델과 내부 로그가 실행 컨텍스트를 참고하도록 보강
- 진행상황: 완료
- 진행내용:
  - 일반 메시지 실행 경로는 `ResponseComposer`에 `execution_context`를 넘기지만, 버튼 승인/URL 후보 선택/작업 후보 선택 경로는 결과 메타데이터만 있고 composer 호출에는 실행 컨텍스트가 빠질 수 있음을 확인했다.
  - `execution_context_from_result_metadata()`를 추가해 버튼 실행 결과에 붙은 `context_link`, `linked_state_id`, `link_confidence`, `resolved_slots`에서 응답용 실행 컨텍스트를 복원하도록 했다.
  - 버튼 응답 composer와 내부 행동 로그 기록이 복원된 실행 컨텍스트를 함께 받도록 바꿔, 버튼으로 실행된 작업도 연결된 이전 작업 상태와 라우터 복원 슬롯을 응답 모델이 볼 수 있게 했다.
  - URL 후보 버튼 선택 결과에는 `url_title/url_titles`도 라우터 복원 슬롯에 포함해 다음 턴과 내부 로그에서 선택한 URL 제목 단서를 유지하도록 했다.
  - URL 후보 버튼 선택, 작업 후보 버튼 선택, 단일 작업 승인 버튼 모두 composer에 실행 컨텍스트가 전달되는지 회귀 테스트를 보강했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_url_candidate_button_selection_dispatches_selected_url tests/test_bot_helpers.py::test_state_candidate_button_selection_routes_and_dispatches_selected_state tests/test_bot_helpers.py::test_context_confirmation_button_approval_dispatches_original_intent -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_response_composer.py tests/test_router_agent.py -q`(`210 passed`), `python3 -m pytest -q`(`850 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 버튼 취소 대상 pending 고정

- 작업 이름: 오래된 확인/후보 버튼이 최신 pending을 잘못 취소하지 않도록 버튼 생성 시점의 pending 상태 ID를 고정
- 진행상황: 완료
- 진행내용:
  - URL 후보 버튼과 다중 후속 후보 버튼의 `취소` 경로가 기존에는 `scope` 기준 최신 pending을 다시 찾아 취소하므로, 사용자가 오래된 버튼을 누르면 그 사이 생성된 최신 확인 대기를 잘못 만료할 수 있음을 확인했다.
  - `ConfirmationView`, `URLCandidateSelectionView`, `StateCandidateSelectionView`에 버튼 생성 시점의 `pending_state_id`를 저장하고, 승인/거부/후보 선택/후보 취소 핸들러가 해당 pending만 조회하도록 보강했다.
  - `pending_context_state()` 헬퍼를 추가해 지정 ID가 있으면 그 상태가 아직 유효한 확인 대기인지 검증하고, 지정 ID가 없는 기존 호출은 최신 pending fallback을 유지하도록 했다.
  - 오래된 다중 후보 취소 버튼과 오래된 URL 후보 취소 버튼을 눌러도 더 최근 pending은 살아 있고, 버튼에 묶인 pending만 취소되는 회귀 테스트를 추가했다.
  - URL 후보 선택과 다중 후속 후보 선택 테스트도 더 최근 pending이 있는 상황으로 보강해, 선택 버튼 역시 버튼에 묶인 pending을 기준으로 실행하고 최신 pending은 보존하는지 확인했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_state_candidate_cancel_button_expires_bound_pending_only tests/test_bot_helpers.py::test_url_candidate_cancel_button_expires_bound_pending_only tests/test_bot_helpers.py::test_url_candidate_button_selection_dispatches_selected_url tests/test_bot_helpers.py::test_state_candidate_button_selection_routes_and_dispatches_selected_state tests/test_bot_helpers.py::test_context_confirmation_button_rejection_expires_pending_state -q`(`5 passed`), `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_attaches_candidate_buttons_to_multiple_candidate_clarification tests/test_bot_helpers.py::test_assistant_bot_attaches_buttons_to_url_candidate_clarification tests/test_bot_helpers.py::test_context_confirmation_button_approval_dispatches_original_intent tests/test_bot_helpers.py::test_context_confirmation_button_blocks_mismatched_pending_slots tests/test_bot_helpers.py::test_context_confirmation_button_rejection_expires_pending_url_candidate_state tests/test_bot_helpers.py::test_confirmation_button_defers_before_editing_original_message -q`(`6 passed`), `python3 -m pytest tests/test_bot_helpers.py::test_url_candidate_button_selection_dispatches_selected_url tests/test_bot_helpers.py::test_state_candidate_button_selection_routes_and_dispatches_selected_state tests/test_bot_helpers.py::test_state_candidate_cancel_button_expires_bound_pending_only tests/test_bot_helpers.py::test_url_candidate_cancel_button_expires_bound_pending_only -q`(`4 passed`), `python3 -m pytest -q`(`852 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 확인 질문 표준화

- 작업 이름: 라우터 모델이 다른 위치 작업을 애매한 확인 질문으로 반환해도 검증층에서 위치 변경 질문과 실행 슬롯을 표준화
- 진행상황: 완료
- 진행내용:
  - 라우터가 이미 `context_link=clarify`를 반환한 경우에는 실행 전 검증이 cross-location 질문 문구와 누락 슬롯을 다시 정리하지 않아, 모델 질문이 “이 작업을 계속할까요?”처럼 왜 확인하는지 부족하게 남을 수 있음을 확인했다.
  - `validate_route_context_link()`의 `clarify` 경로에서도 연결 상태가 현재 대화 위치와 다르면 `clarify_cross_location_link()`를 적용해 “채팅 위치가 바뀐 것 같아요...” 문구로 통일하고, `task_id/task_ids`, `document_id/document_ids`, `memory_id/memory_ids` 같은 실행 대상 슬롯을 보강하도록 했다.
  - cross-location 확인 질문 문구를 라우터/컨텍스트 빌더 계약과 맞춰 “다른 대화 위치에서 하던 `대상` 작업을 여기서 이어서 처리할까요?” 형태로 정리했다.
  - 라우터 모델이 약한 질문과 빈 슬롯을 반환해도 봇 통합 경로에서 표준 질문, pending 슬롯, 응답용 실행 컨텍스트가 보강되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_standardizes_model_cross_location_clarify_question tests/test_bot_helpers.py::test_assistant_bot_standardizes_model_cross_location_clarify_before_reply tests/test_bot_helpers.py::test_assistant_bot_clarifies_model_cross_location_continue_before_dispatch tests/test_bot_helpers.py::test_assistant_bot_chat_approval_allows_cross_location_pending_context -q`(`4 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`135 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`351 passed`), `python3 -m pytest -q`(`854 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation 보정 이력 컨텍스트 검증

- 작업 이름: 다른 위치 확인 질문 표준화가 내부 행동 로그와 다음 라우터 컨텍스트에도 남는지 회귀 테스트 보강
- 진행상황: 완료
- 진행내용:
  - route validation이 `clarification_question`과 `resolved_slots`를 보정해도, 그 이력이 내부 로그에 남고 다음 라우터 컨텍스트에서 파싱 가능한지 명시적으로 검증되어 있지 않은 점을 확인했다.
  - `test_assistant_bot_standardizes_model_cross_location_clarify_before_reply`를 보강해 route validation 로그에 보정 전후 슬롯, 질문 문구, `validation_context`가 저장되는지 확인하도록 했다.
  - 같은 테스트에서 `build_router_context()`를 다시 호출해 최근 내부 행동 기록에 `agent=route_validation`, `linked_state_id`, `validation_guidance=최근 검증에서 state_id...자동 실행 대신 확인 질문으로 변경됨`이 포함되는지 확인했다.
  - 이를 통해 모델이 같은 유형의 다른 위치 후속 요청을 다시 자동 실행하려 할 때, 라우터가 직전 검증 이력을 참고해 확인 질문으로 멈출 수 있는 근거를 고정했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_standardizes_model_cross_location_clarify_before_reply -q`(`1 passed`), `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_standardizes_model_cross_location_clarify_before_reply tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router tests/test_context_builder.py::test_build_router_context_does_not_turn_validation_reason_into_target_hint tests/test_router_agent.py::test_router_parses_internal_validation_clarified_state_ids tests/test_router_agent.py::test_router_fallback_clarifies_validation_clarified_state_for_implicit_action -q`(`5 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py::test_assistant_bot_standardizes_model_cross_location_clarify_before_reply -q`(`258 passed`), `python3 -m pytest -q`(`854 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - CLI 경로 route validation 컨텍스트 보존

- 작업 이름: 로컬 `ask` 경로에서도 다른 위치 확인 보정과 route validation 이력이 다음 라우터 컨텍스트에 보존되도록 보강
- 진행상황: 완료
- 진행내용:
  - Discord 경로와 달리 로컬 CLI `run_local_text_interaction()`은 테스트에서 라우터 모델 출력을 직접 주입하기 어려워, cross-location clarify 표준화 통합 테스트가 부족한 점을 확인했다.
  - `run_local_text_interaction()`에 선택적 `openai` 인자를 추가해 기본 운영 동작은 그대로 유지하면서, 테스트에서는 fake OpenAI로 라우터 응답과 최종 답변을 제어할 수 있게 했다.
  - CLI local ask 통합 테스트를 추가해 라우터가 “이 작업을 계속할까요?” 같은 약한 cross-location clarify를 반환해도 표준 질문으로 답하고, route validation 로그에 보정 전후 슬롯과 질문 문구가 남는지 확인했다.
  - 내부 행동 컨텍스트가 길어질 때 최신 `router:result` 로그만 남고 직전 `route_validation` 로그가 잘릴 수 있음을 확인해, 현재 위치의 `route_validation` 로그를 일반 결과 로그보다 우선 보존하도록 `build_internal_action_context()` 정렬 우선순위를 조정했다.
  - CLI 테스트에서 다음 `build_router_context()` 호출 결과에 `agent=route_validation`, `linked_state_id`, `validation_guidance=최근 검증에서 state_id...자동 실행 대신 확인 질문으로 변경됨`이 포함되는지 확인했다.
  - `python3 -m pytest tests/test_cli.py::test_local_ask_standardizes_cross_location_clarify_and_logs_validation tests/test_context_builder.py::test_build_router_context_orders_internal_action_logs_latest_first tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router tests/test_context_builder.py::test_build_router_context_keeps_latest_internal_action_when_trimmed -q`(`4 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py::test_router_parses_internal_validation_clarified_state_ids tests/test_router_agent.py::test_router_fallback_clarifies_validation_clarified_state_for_implicit_action -q`(`42 passed`), `python3 -m pytest tests/test_cli.py tests/test_context_builder.py -q`(`116 passed`), `python3 -m pytest tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_bot_helpers.py::test_assistant_bot_standardizes_model_cross_location_clarify_before_reply -q`(`230 passed`), `python3 -m pytest -q`(`855 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route preview 경로 cross-location 표준화 검증

- 작업 이름: `assistant-admin route --model` 미리보기도 실제 `ask`와 같은 cross-location 확인 기준을 쓰는지 회귀 테스트 보강
- 진행상황: 완료
- 진행내용:
  - 계획 문서에서 `assistant-admin route` 미리보기도 실제 `ask` 실행과 같은 pending/context 기준을 써야 한다고 명시되어 있어, 모델 기반 route preview의 다른 위치 확인 표준화가 테스트로 고정되어 있는지 확인했다.
  - `preview_model_route_details()`는 코드상 `finalize_route_preview()`를 통해 실제 검증 계층을 공유하지만, 라우터 모델이 약한 `context_link=clarify` 질문과 빈 슬롯을 반환하는 cross-location 시나리오는 직접 테스트되어 있지 않았다.
  - 모델 route preview 테스트를 추가해 “이 작업을 계속할까요?” 같은 약한 질문이 “채팅 위치가 바뀐 것 같아요...” 질문으로 표준화되고, `task_id/task_ids` 슬롯과 연결 상태가 유지되는지 확인했다.
  - route preview 출력에도 `source=model_context_validation`, 보강된 `resolved_slots`, 연결된 다른 위치 작업 상태가 드러나는지 확인해 운영자가 미리보기와 실제 ask 사이에서 다른 판단을 보지 않도록 했다.
  - `python3 -m pytest tests/test_cli.py::test_preview_model_route_details_standardizes_cross_location_clarify tests/test_cli.py::test_preview_model_route_details_uses_openai_router_model tests/test_cli.py::test_preview_route_details_includes_linked_state_and_candidates tests/test_cli.py::test_preview_route_details_allows_exact_pending_context_approval -q`(`4 passed`), `python3 -m pytest tests/test_cli.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`306 passed`), `python3 -m pytest -q`(`856 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending context 전체 만료 보증

- 작업 이름: 새 요청 또는 새 확인 질문이 제한 개수 밖의 오래된 pending context까지 모두 정리하는지 검증
- 진행상황: 완료
- 진행내용:
  - “응”, “다시해봐” 같은 짧은 답변이 오래된 확인 질문에 잘못 연결되는 문제를 막으려면, 새 요청 또는 새 확인 질문이 들어올 때 현재 대화 위치의 살아있는 pending context 전체를 만료해야 함을 다시 확인했다.
  - `AssistantBot.expire_stale_pending_context_link()`와 `expire_existing_pending_context_links()`가 `recent_candidates(limit=5)`가 아니라 `pending_candidates(scope=scope)` 전체를 사용하고 있어, 최근 후보 제한 밖으로 밀린 확인 대기도 정리되는 구조임을 확인했다.
  - Discord 봇 헬퍼 경로에 회귀 테스트를 추가해 새 `context_link=clarify`가 생성될 때 최근 후보 제한보다 많은 기존 후속 확인 대기가 모두 만료되고, 일반 성공 상태는 유지되는지 검증했다.
  - CLI 경로의 전체 pending 만료 테스트와 함께 실행해 로컬 `ask`와 Discord 봇 경로가 같은 안전 기준을 유지하는지 확인했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_expires_stale_pending_context_on_new_request tests/test_bot_helpers.py::test_assistant_bot_expires_all_existing_pending_context_links_on_new_clarify tests/test_cli.py::test_cli_expires_all_stale_pending_context_links_on_new_request tests/test_cli.py::test_cli_expires_existing_pending_context_links_on_new_clarify -q`(`4 passed`), `python3 -m pytest -q`(`857 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 로그 우선 보존 후보 풀 확대

- 작업 이름: 최신 일반 로그가 많이 쌓여도 route validation 같은 안전 판단 로그가 라우터 컨텍스트에 남도록 보강
- 진행상황: 완료
- 진행내용:
  - 기존 `build_internal_action_context()`는 내부 로그를 표시 개수만큼만 DB에서 가져온 뒤 우선순위 정렬을 수행해, 중요한 `route_validation` 로그가 최신 일반 로그 몇 개에 밀리면 정렬 전에 이미 사라질 수 있음을 확인했다.
  - 내부 행동 로그를 표시 개수보다 넉넉한 후보 풀로 가져온 뒤, 현재 위치 `route_validation`, 현재 위치 일반 로그, 다른 위치 `route_validation`, 다른 위치 일반 로그 순으로 정렬하고 마지막에 표시 개수로 제한하도록 바꿨다.
  - 이 변경으로 라우터가 다음 턴에서 “최근 검증에서 자동 연결이 제거됨”, “자동 실행 대신 확인 질문으로 변경됨” 같은 비공개 판단 이력을 더 안정적으로 참고할 수 있게 했다.
  - 현재 위치에서 route validation 이후 일반 라우터 로그가 많이 쌓여도 검증 로그와 `validation_guidance`가 내부 컨텍스트에 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_keeps_current_route_validation_when_newer_current_logs_overflow_limit tests/test_context_builder.py::test_build_router_context_keeps_current_location_internal_logs_when_cross_location_is_newer tests/test_context_builder.py::test_build_router_context_keeps_latest_internal_action_when_trimmed -q`(`3 passed`), `python3 -m pytest -q`(`858 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 새 일반 요청 오연결 검증층 방어

- 작업 이름: 라우터가 새 일반/유틸리티 요청을 이전 작업 상태에 잘못 연결해도 실행 전 검증층에서 제거
- 진행상황: 완료
- 진행내용:
  - 사용자가 “오늘 저녁 뭐 먹지?”, “지금 몇시야?”처럼 이전 작업과 무관한 새 요청을 보냈는데 라우터 모델이 이전 `weather` 상태에 `retry/continue`로 연결하면, 같은 intent 계열이나 retry 가능 상태라는 이유로 검증층을 통과할 수 있는 여지를 확인했다.
  - `unrelated_new_request_mismatch_linked_state()`를 추가해 명확한 후속 표현, 명시 ID, 출처 변환 요청이 없는 새 일반 추천/식사 질문 또는 새 유틸리티 요청은 이전 상태 연결을 제거하도록 했다.
  - 이 방어는 라우터 모델 출력 이후의 공통 `validate_route_context_link()`에 들어가므로, 새 에이전트가 추가되더라도 이전 상태에 억지로 붙는 명백한 새 요청은 실행 전에 한 번 더 걸러진다.
  - “미세먼지도 알려줘” 같은 정상 날씨 세부 후속 요청이 named target 불일치로 잘못 제거되는 기존 경계도 함께 확인해, 날씨 세부 액션(`check_air_quality`, `show_alerts`)은 일반 named target 추출에서 제외하도록 정리했다.
  - 새 일반 식사 질문과 새 시간 질문은 이전 날씨 retry 링크를 제거하고, 정상 날씨 세부 후속 요청은 연결을 유지하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clears_unrelated_food_request_from_weather_retry tests/test_route_validation.py::test_validate_route_context_link_clears_unrelated_utility_request_from_weather_retry tests/test_route_validation.py::test_validate_route_context_link_keeps_weather_detail_follow_up -q`(`3 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`354 passed`), `python3 -m pytest -q`(`861 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 대상 없는 clarify 새 요청 차단

- 작업 이름: 라우터가 명시적 새 요청을 대상 없는 확인 질문으로 잘못 바꿔도 검증층에서 원래 요청으로 되돌림
- 진행상황: 완료
- 진행내용:
  - `context_link=clarify`인데 `linked_state_id`가 없는 모델 결과는 기존 검증층에서 그대로 통과해, “서울 날씨 알려줘”, “오늘 저녁 뭐 먹지?” 같은 명시적 새 요청도 불필요한 “무엇을 이어갈까요?” 질문으로 멈출 수 있음을 확인했다.
  - `should_clear_unlinked_clarify_for_new_request()`와 `clear_unlinked_new_request_clarify()`를 추가해, 대명사/후속 표현이 없는 명시적 새 요청은 대상 없는 clarify를 `context_link=none`으로 되돌리도록 했다.
  - 확인 후보 선택 슬롯(`pending_candidate_state_ids`, `pending_candidate_urls`)이 있는 안전한 unlinked clarify는 그대로 보존해, 실제 다중 후보 선택 흐름은 깨지지 않게 했다.
  - “그거 삭제해”처럼 후속 대상이 모호한 요청은 대상 없는 clarify를 유지하고, “서울 날씨 알려줘”, “오늘 저녁 뭐 먹지?”는 clarify를 제거하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clears_unlinked_clarify_for_explicit_new_weather_request tests/test_route_validation.py::test_validate_route_context_link_clears_unlinked_clarify_for_new_food_chat_request tests/test_route_validation.py::test_validate_route_context_link_keeps_unlinked_clarify_for_ambiguous_follow_up tests/test_route_validation.py::test_validate_route_context_link_preserves_safe_unlinked_clarify_candidate_slots tests/test_route_validation.py::test_validate_route_context_link_preserves_safe_unlinked_clarify_url_candidate_slots -q`(`5 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`357 passed`), `python3 -m pytest -q`(`864 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 대상 없는 clarify 보정 이력 guidance 추가

- 작업 이름: route validation이 대상 없는 확인 질문을 새 요청으로 되돌린 이력을 다음 라우터 컨텍스트에서 읽기 쉽게 보존
- 진행상황: 완료
- 진행내용:
  - `context_link=clarify`였지만 `linked_state_id`가 없는 모델 결과를 `context_link=none`으로 되돌리는 보정은 내부 로그에 남지만, 기존 `validation_guidance`는 state_id가 있는 자동 연결 제거/확인 전환만 설명해 이 케이스가 다음 턴 라우터에게 충분히 해석되지 않을 수 있음을 확인했다.
  - `internal_action_validation_guidance()`에 `before.context_link=clarify`, `before.linked_state_id=None`, `after.context_link=none` 패턴을 추가해 “대상 없는 확인 질문이 새 요청으로 변경됨”이라는 guidance를 생성하도록 했다.
  - 이 guidance는 “명시적 새 요청은 확인 질문으로 멈추지 말고 바로 라우팅”이라는 지침으로 라우터 컨텍스트에 들어가, 같은 유형의 불필요한 확인 질문 반복을 줄이는 데 쓰인다.
  - state_id 없는 validation guidance가 `internal_validation_removed_state_ids()`나 `internal_validation_clarified_state_ids()`의 state id 집합을 오염시키지 않는지도 회귀 테스트로 고정했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_guides_unlinked_clarify_cleared_to_new_request tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router tests/test_router_agent.py::test_router_ignores_unlinked_validation_guidance_for_state_id_sets tests/test_router_agent.py::test_router_parses_internal_validation_removed_state_ids tests/test_router_agent.py::test_router_parses_internal_validation_clarified_state_ids -q`(`5 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py -q`(`137 passed`), `python3 -m pytest -q`(`866 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - fallback 라우터의 대상 없는 clarify guidance 반영

- 작업 이름: 모델 실패/fallback 경로에서도 대상 없는 확인 질문 보정 이력을 실제 라우팅 행동에 반영
- 진행상황: 완료
- 진행내용:
  - 내부 로그에 “대상 없는 확인 질문이 새 요청으로 변경됨” guidance가 남아도, fallback 라우터는 이 패턴을 별도로 파싱하지 않아 base route가 대상 없는 `clarify`인 경우 같은 불필요한 확인 질문을 반복할 수 있음을 확인했다.
  - `internal_validation_unlinked_clarify_new_request_seen()`를 추가해 `before.context_link=clarify`, `before.linked_state_id=None`, `after.context_link=none` 패턴을 내부 validation context에서 감지하도록 했다.
  - `context_aware_fallback_route()`가 이 guidance를 보고, 현재 문장에 후속 표현이 없고 base route가 대상 없는 `clarify`이면 `context_link=none`으로 되돌리도록 했다.
  - “서울 날씨 알려줘” 같은 새 요청은 fallback에서도 확인 질문을 제거하고, “그거 다시해봐” 같은 실제 후속 요청은 기존 clarify를 유지하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_ignores_unlinked_validation_guidance_for_state_id_sets tests/test_router_agent.py::test_router_fallback_uses_unlinked_clarify_guidance_for_new_request tests/test_router_agent.py::test_router_fallback_keeps_unlinked_clarify_guidance_for_follow_up_request -q`(`3 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py -q`(`139 passed`), `python3 -m pytest -q`(`868 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation 로그 압축 구조 보존

- 작업 이름: 긴 route validation 보정 로그에서도 `validation_context`가 파싱 가능한 형태로 보존되도록 압축 방식 개선
- 진행상황: 완료
- 진행내용:
  - route validation 로그는 900자 이하로 압축되지만, `resolved_slots`에 긴 값과 많은 키가 함께 들어가면 `validation_context` dict 중간이 잘려 다음 턴 라우터가 보정 이력을 파싱하지 못할 수 있음을 확인했다.
  - `route_validation_snapshot()`에서 `resolved_slots` 전체를 `compact_route_validation_snapshot_value()`로 압축하도록 바꿔, 슬롯 키 개수와 값 길이를 함께 제한했다.
  - snapshot 문자열, 리스트, 튜플, 딕셔너리 압축 한도를 더 낮춰 `validation_context` tail이 로그 최대 길이 안에 안정적으로 들어오도록 했다.
  - 많은 슬롯이 포함된 보정 로그에서도 `internal_validation_removed_state_ids()`가 `linked_state_id` 제거 이력을 읽을 수 있는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_cli.py::test_log_route_validation_if_changed_compacts_long_adjustment tests/test_cli.py::test_log_route_validation_if_changed_preserves_parseable_context_with_many_slots tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router tests/test_router_agent.py::test_router_parses_internal_validation_removed_state_ids -q`(`4 passed`), `python3 -m pytest tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment tests/test_cli.py::test_log_route_validation_if_changed_compacts_long_adjustment tests/test_cli.py::test_log_route_validation_if_changed_preserves_parseable_context_with_many_slots tests/test_context_builder.py tests/test_router_agent.py -q`(`142 passed`), `python3 -m pytest -q`(`869 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - unsupported turn state 후보 오염 방지

- 작업 이름: 순수 지원 불가 결과가 후속 맥락 후보로 남아 다음 라우팅을 오염시키지 않도록 저장 기준 강화
- 진행상황: 완료
- 진행내용:
  - `intent=unsupported` 결과는 실행 가능한 후속 작업 후보가 아니므로, subject나 retryable, artifacts가 붙어도 `conversation_turn_states`에 저장하지 않는 것이 더 안전하다고 판단했다.
  - `should_record_turn_state()`에서 `needs_input`/`confirm_required`/`clarify` 대기 상태를 제외한 순수 `unsupported` intent는 항상 저장하지 않도록 했다.
  - 날씨 미세먼지처럼 도메인 에이전트가 `intent=weather`, `status=unsupported`로 반환하고 query/location/action을 가진 경우는 기존처럼 저장해, 나중에 웹검색 설정 후 재시도할 수 있는 맥락 후보를 유지했다.
  - artifacts와 retryable이 붙은 순수 unsupported 결과도 저장하지 않고, 도메인별 targeted unsupported 결과는 저장하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_should_record_turn_state_skips_retryable_plain_unsupported_result tests/test_bot_helpers.py::test_should_record_turn_state_skips_unsupported_result_even_with_artifacts tests/test_bot_helpers.py::test_should_record_turn_state_keeps_targeted_unsupported_domain_result -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py -q`(`241 passed`), `python3 -m pytest -q`(`870 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답 컨텍스트 route validation 원문 숨김

- 작업 이름: 라우터/에이전트에는 route validation 보정 이력을 유지하되 최종 응답 모델에는 내부 검증 원문이 노출되지 않도록 경계 강화
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그는 라우터 맥락 판단에는 필요하지만, 최종 응답 작성 모델에 `route_validation` 줄의 reason 원문까지 들어가면 답변이 내부 시스템 설명처럼 흐를 수 있음을 확인했다.
  - `response_safe_internal_action_context()`에서 `agent=route_validation` 줄은 응답용 내부 참고에서 제외하도록 했다.
  - 라우터/에이전트 컨텍스트에는 기존처럼 route validation 보정 이력이 남아 다음 턴 라우팅과 전문 에이전트 실행에는 계속 활용된다.
  - 최종 응답 context에는 작업 결과 로그의 공개 가능한 슬롯/아티팩트 단서만 남고, route validation reason과 내부 검증 문구는 빠지는 회귀 테스트로 경계를 고정했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_composer_treats_internal_action_context_as_hidden_reference tests/test_context_builder.py::test_build_execution_context_includes_internal_action_logs_for_agents_and_response tests/test_response_composer.py::test_execution_context_response_prioritizes_linked_state_over_internal_action_when_truncated -q`(`3 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py -q`(`61 passed`), `python3 -m pytest -q`(`870 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답용 라우팅 근거 내부 검증 문구 제거

- 작업 이름: 최종 응답 컨텍스트의 `route_reason`에서 route validation 세부 문구와 private 슬롯명이 새지 않도록 정리
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그는 응답 컨텍스트에서 숨겼지만, `ExecutionContext.for_response()`가 `route_reason`을 그대로 넣어 `실행 전 링크 검증`, `context_link`, `linked_state_id`, `resolved_slots`, `validation_context` 같은 내부 검증 문구가 최종 응답 모델 입력에 남을 수 있음을 확인했다.
  - `response_safe_route_reason()`을 추가해 응답용 라우팅 근거에서는 ` / 실행 전 ...` 이후의 검증층 세부 문구와 private route metadata를 제거하도록 했다.
  - 일반적인 사용자 맥락 설명인 “대명사 후속 요청을 메모 8에 연결” 같은 라우팅 근거는 계속 유지해, 응답 모델이 어떤 이전 상태를 참고하는지 자연스럽게 알 수 있게 했다.
  - 검증층 문구가 붙은 route reason에서 내부 키와 validation context가 빠지고, 정상 라우팅 근거는 유지되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_hides_validation_details_from_route_reason tests/test_response_composer.py::test_response_composer_includes_execution_resolved_slots -q`(`2 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py -q`(`62 passed`), `python3 -m pytest -q`(`871 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 확인 정책 파싱 보강

- 작업 이름: 라우터 fallback이 위치 라벨뿐 아니라 confirm_policy로도 다른 위치 후보를 확인 대상으로 판단
- 진행상황: 완료
- 진행내용:
  - fallback 라우터의 `StateCandidate.is_cross_location`이 `location=다른 위치` 문자열에만 의존하고 있어, 후보 포맷이 바뀌거나 위치 라벨이 생략되면 `confirm_policy=ask_before_execute_when_follow_up` 후보를 바로 실행할 수 있는 취약점을 확인했다.
  - `is_cross_location`이 `ask_before_execute_when_follow_up` 정책과 “다른 위치 + 사용자 확인 필요” link guidance를 함께 읽도록 보강했다.
  - 이 변경으로 새 에이전트가 turn state 후보를 만들 때 location 라벨이 약간 달라져도, 다른 채팅 위치에서 하던 작업은 먼저 사용자에게 이어갈지 확인하는 공통 정책을 유지한다.
  - `location` 필드가 없는 후보라도 `confirm_policy`만으로 `context_link=clarify`가 되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_uses_confirm_policy_when_location_label_is_missing_for_cross_location tests/test_router_agent.py::test_router_fallback_clarifies_cross_location_target_hint_match -q`(`2 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`135 passed`), `python3 -m pytest -q`(`872 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - typed artifact ID 맥락 복원 보강

- 작업 이름: 새 에이전트가 `id` 대신 `document_id` 같은 타입별 ID를 artifact에 담아도 라우터가 실행 슬롯을 복원하도록 개선
- 진행상황: 완료
- 진행내용:
  - 일부 에이전트/테스트가 artifact를 `{"kind": "document", "document_id": 7}`처럼 타입별 ID 키로 표현할 수 있는데, 라우터의 artifact 슬롯 복원과 내부 행동 로그 요약은 주로 공통 `id` 키만 읽고 있음을 확인했다.
  - `artifact_identifier()` 계열 helper를 추가해 memory/document/task/reminder artifact에서 `id`와 타입별 ID(`memory_id`, `document_id`, `task_id`, `reminder_id`)를 모두 같은 대상으로 처리하도록 했다.
  - 라우터 fallback은 typed artifact ID만 있는 문서 후보에서도 `문서 7 다시 분석해줘`를 `document_id=7`로 복원할 수 있게 됐다.
  - turn state context와 내부 행동 로그도 typed artifact ID를 target hint와 내부 artifact 요약에 반영하도록 맞춰, 새 에이전트가 약간 다른 artifact 형태를 써도 후속 맥락 단서가 사라지지 않게 했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_restores_slot_from_typed_document_artifact_id tests/test_context_builder.py::test_turn_state_context_uses_typed_document_artifact_id_hint tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`(`3 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_bot_helpers.py -q`(`244 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`135 passed`), `python3 -m pytest -q`(`874 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - plural typed artifact ID 맥락 복원 보강

- 작업 이름: 복수 대상 artifact의 `document_ids` 같은 plural typed ID도 후속 요청에서 안전하게 복원
- 진행상황: 완료
- 진행내용:
  - 비교/목록형 결과가 artifact에 `document_ids`, `task_ids`, `memory_ids`, `reminder_ids`처럼 복수 ID를 담으면, 기존 라우터는 공통 `id`나 singular typed ID 중심으로만 슬롯을 복원해 특정 대상 후속 요청에서 단서가 약해질 수 있음을 확인했다.
  - 라우터 artifact ID helper를 plural typed ID까지 확장해, `문서 7 다시 분석해줘`처럼 명시적 ID가 있는 경우 `[7, 8]` 중 `document_id=7`만 복원하도록 했다.
  - 반대로 `contract.pdf 다시 분석해줘`처럼 여러 ID가 들어 있는 artifact의 파일명만 매칭되는 경우에는 ID와 파일명 정렬을 확신하지 않고 슬롯을 비워, 잘못된 대상 실행을 피하도록 했다.
  - artifact match field에 `filenames`, `attachment_names`, `urls`, `url_titles` 같은 plural 필드를 추가하고, 리스트형 artifact 텍스트도 매칭할 수 있게 했다.
  - turn state context와 내부 행동 로그도 plural typed ID를 target hint와 artifact 요약에 반영하도록 맞춰 새 에이전트의 복수 대상 결과가 라우터 컨텍스트에서 사라지지 않게 했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_restores_specific_slot_from_plural_typed_document_artifact_ids tests/test_router_agent.py::test_router_fallback_keeps_plural_typed_document_artifact_filename_match_ambiguous tests/test_context_builder.py::test_turn_state_context_uses_plural_typed_document_artifact_id_hints tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`(`4 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_bot_helpers.py -q`(`247 passed`), `python3 -m pytest tests/test_context_routing_matrix.py tests/test_agent_registry.py -q`(`164 passed`), `python3 -m pytest -q`(`877 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - plural URL artifact 실행 복원 보강

- 작업 이름: 라우터가 연결한 웹 결과의 `urls` artifact를 Web URL Agent 실행에서도 그대로 읽도록 개선
- 진행상황: 완료
- 진행내용:
  - 라우터와 컨텍스트는 `artifacts.urls`를 후속 맥락 단서로 보존하지만, `WebSearchAgent.linked_urls()`는 연결된 상태 artifact의 단일 `url`만 읽고 plural `urls`는 읽지 않아 “그 링크들 다시 요약해줘” 같은 후속 실행에서 URL을 놓칠 수 있음을 확인했다.
  - `linked_urls()`가 linked state artifact의 `url`과 `urls`를 모두 수집하도록 바꿨다.
  - `linked_url_titles()`는 이미 artifact의 `urls`/`url_titles` 정렬을 지원하고 있어, URL 수집만 보강해도 실행 결과 슬롯과 artifact에 제목까지 함께 복원된다.
  - `web_result` artifact에 `urls`와 `url_titles`만 들어 있는 상태에서 후속 URL 읽기 요청이 실제 두 URL을 모두 읽고 제목 슬롯을 보존하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_web_search_agent.py::test_web_search_agent_reads_linked_plural_artifact_urls_when_follow_up_has_no_url tests/test_web_search_agent.py::test_web_search_agent_reads_linked_url_when_follow_up_has_no_url tests/test_web_search_agent.py::test_web_search_agent_preserves_linked_url_title_from_execution_context -q`(`3 passed`), `python3 -m pytest tests/test_web_search_agent.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`262 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py -q`(`146 passed`), `python3 -m pytest -q`(`878 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - plural artifact 텍스트 실행 복원 보강

- 작업 이름: 메모/할일/알림 에이전트가 연결된 복수 artifact의 제목·파일명·URL 제목을 실행 본문으로 복원하도록 개선
- 진행상황: 완료
- 진행내용:
  - 라우터와 컨텍스트는 `artifacts.filenames`, `artifacts.url_titles`, `artifacts.urls` 같은 복수 필드를 후속 맥락 단서로 보존하지만, 메모/할일/알림 실행 helper는 단일 `title`, `filename`, `name` 중심으로만 읽고 있어 실행 단계에서 대상명이 약해질 수 있음을 확인했다.
  - `assistant_bot/agents/common.py`에 `first_artifact_text()`와 `first_text_value()`를 추가해 단수/복수 artifact 텍스트 필드를 같은 규칙으로 읽도록 공통화했다.
  - `MemoryAgent`, `TaskAgent`, `ReminderAgent`의 linked state 본문 복원 경로가 이 공통 helper를 사용하도록 바꿨다.
  - 할일 생성 일반 경로에서도 linked artifact 제목을 먼저 확인하도록 보강해, `그 파일 할 일로 추가해줘` 같은 문장을 할일 제목으로 저장하지 않고 실제 연결된 파일명으로 저장하게 했다.
  - `url_titles`만 있는 웹 결과를 메모/알림 본문으로 복원하고, `filenames`만 있는 문서 결과를 할일 제목으로 복원하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_memory_store.py::test_reminder_agent_creates_reminder_from_linked_plural_web_artifact tests/test_memory_store.py::test_task_agent_creates_task_from_linked_plural_document_artifact tests/test_memory_store.py::test_memory_agent_remembers_linked_plural_web_artifact_text -q`(`3 passed`), `python3 -m pytest tests/test_memory_store.py -q`(`107 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_web_search_agent.py tests/test_memory_store.py -q`(`369 passed`), `python3 -m pytest -q`(`881 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 문서/검색 artifact 실행 복원 보강

- 작업 이름: 문서분석과 웹검색 에이전트가 linked artifact만으로도 후속 대상과 검색어를 복원하도록 개선
- 진행상황: 완료
- 진행내용:
  - `DocumentAnalysisAgent._linked_documents()`가 `resolved_slots`와 linked state slots의 `document_id/document_ids`만 읽고, artifact에만 남은 `document_ids`는 읽지 않아 새 에이전트 출력 형태에 따라 `그 문서 다시 분석해봐`가 대상을 잃을 수 있음을 확인했다.
  - 문서 artifact의 `id`, `document_id`, `document_ids`를 추가로 수집해 linked state slots가 비어 있어도 저장된 문서를 다시 분석할 수 있게 했다.
  - `WebSearchAgent.linked_search_text()`가 linked query 슬롯이 없으면 artifact 제목/파일명/URL 제목을 검색어로 복원하지 못해 `그 파일 검색해줘` 같은 후속 요청이 약해질 수 있음을 확인했다.
  - 웹검색 후속 검색어 복원에 `first_artifact_text()`를 적용해 `filenames`, `url_titles`, `titles` 같은 artifact 텍스트를 검색어 후보로 사용할 수 있게 했다.
  - artifact에만 `document_ids`가 있는 문서를 재분석하는 테스트와, artifact `filenames`만 있는 문서를 검색어로 복원하는 테스트를 추가했다.
  - `python3 -m pytest tests/test_document_analysis_agent.py::test_document_analysis_agent_reanalyzes_document_id_from_linked_artifact tests/test_web_search_agent.py::test_web_search_agent_uses_linked_artifact_title_when_query_slot_is_missing -q`(`2 passed`), `python3 -m pytest tests/test_document_analysis_agent.py tests/test_web_search_agent.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`274 passed`), `python3 -m pytest -q`(`883 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 로그 plural artifact 보존 보강

- 작업 이름: 내부 행동 기록이 복수 URL·파일명 artifact 단서를 후속 라우팅 컨텍스트에 남기도록 개선
- 진행상황: 완료
- 진행내용:
  - 실행 에이전트는 `urls`, `url_titles`, `filenames` 같은 복수 artifact를 읽도록 보강했지만, 내부 행동 로그 요약은 단일 `url/title/filename` 중심으로만 artifact 단서를 축약해 DB turn state가 아닌 내부 로그만 남은 상황에서 라우터가 복수 URL/제목을 덜 볼 수 있음을 확인했다.
  - `safe_internal_action_artifact_values()`가 `web_result`와 `url` artifact의 `url`뿐 아니라 `urls`도 수집하도록 바꿨다.
  - artifact 제목 수집을 `title`, `titles`, `filename`, `filenames`, `name`, `url_title`, `url_titles`까지 넓혀 새 에이전트가 복수 제목/파일명 형태로 결과를 남겨도 내부 로그에 보존되게 했다.
  - `infer_turn_artifact_from_item()`도 `filenames`, `urls`, `url_title`, `url_titles`, plural typed IDs를 보존하도록 넓혔다. 단, `task_id` 같은 singular typed ID는 기존처럼 공통 `id`로 정규화해 중복 노이즈를 만들지 않게 했다.
  - plural web result artifact가 내부 로그와 router context에 URL/제목을 남기는 테스트와, item 기반 plural artifact 추론 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_preserves_plural_web_result_artifacts_for_future_context tests/test_bot_helpers.py::test_infer_turn_artifacts_preserves_plural_item_targets tests/test_bot_helpers.py::test_record_internal_action_result_preserves_web_result_artifacts_for_future_context tests/test_bot_helpers.py::test_record_internal_action_result_keeps_structured_context_slots -q`(`4 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`384 passed`), `python3 -m pytest -q`(`885 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 실행 에이전트 artifact-only ID 복원 보강

- 작업 이름: 메모/할일/알림 에이전트가 linked state slots 없이 artifact ID만으로도 후속 대상을 복원하도록 개선
- 진행상황: 완료
- 진행내용:
  - 라우터와 컨텍스트는 artifact의 typed ID와 plural typed ID를 보존하지만, `MemoryAgent`, `TaskAgent`, `ReminderAgent`의 linked ID helper는 실행 컨텍스트 slots만 읽고 artifact ID를 읽지 않아 실행층 안전망이 약한 점을 확인했다.
  - `assistant_bot/agents/common.py`에 `artifact_id_values()`를 추가해 `id`, `memory_id/memory_ids`, `document_id/document_ids`, `task_id/task_ids`, `reminder_id/reminder_ids`를 kind별로 읽도록 공통화했다.
  - 메모 에이전트의 linked memory/document ID 복원, 할일 에이전트의 linked task ID 복원, 알림 에이전트의 linked reminder ID 복원이 linked state artifacts도 함께 참고하도록 바꿨다.
  - slots가 비어 있고 artifact에만 `document_id`, `task_id`, `reminder_id`가 있는 상황에서 문서 삭제, 할일 삭제, 알림 조회가 정상 동작하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_memory_store.py::test_reminder_agent_show_uses_linked_reminder_artifact_id_when_slots_missing tests/test_memory_store.py::test_task_agent_delete_uses_linked_task_artifact_id_when_slots_missing tests/test_memory_store.py::test_memory_agent_delete_uses_linked_document_artifact_id_when_slots_missing -q`(`3 passed`), `python3 -m pytest tests/test_memory_store.py tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`494 passed`), `python3 -m pytest -q`(`888 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation typed artifact ID 검증 보강

- 작업 이름: 실행 전 검증층이 artifact의 typed/plural ID도 대상 일치 검증에 사용하도록 개선
- 진행상황: 완료
- 진행내용:
  - 실행 에이전트는 artifact-only typed ID를 읽도록 보강했지만, route validation의 `collect_ids_from_artifacts()`는 artifact의 공통 `id`만 읽고 `document_id`, `document_ids` 같은 typed ID를 보지 않아 실행 전 대상 충돌 검증이 약해질 수 있음을 확인했다.
  - `collect_ids_from_artifacts()`가 task/memory/document/reminder별 singular/plural typed ID를 모두 수집하도록 바꿨다.
  - `resolved_slots.document_id=7`인데 linked artifact가 `document_id=9`인 경우는 자동 연결을 제거하고, linked artifact가 `document_ids=[7, 8]`인 경우는 유지하는 회귀 테스트를 추가했다.
  - 이 변경으로 라우터가 내부 행동 힌트에서 슬롯을 복원했더라도, 연결된 작업 상태 artifact와 ID가 맞지 않으면 실행 전 검증층이 새 요청으로 분리할 수 있다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_rejects_restored_slot_when_artifact_typed_id_conflicts tests/test_route_validation.py::test_validate_route_context_link_accepts_restored_slot_when_artifact_plural_typed_id_matches tests/test_route_validation.py::test_validate_route_context_link_still_rejects_restored_slot_when_state_has_conflicting_target tests/test_route_validation.py::test_validate_route_context_link_allows_restored_slot_when_state_has_no_conflicting_target -q`(`4 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_bot_helpers.py tests/test_context_routing_matrix.py -q`(`514 passed`), `python3 -m pytest -q`(`890 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation artifact URL 제목 검색 검증 보강

- 작업 이름: 검색 후속 요청 검증층이 artifact의 제목과 URL 제목을 검색 대상 단서로 사용하도록 개선
- 진행상황: 완료
- 진행내용:
  - 웹 검색 결과가 `url_titles` 같은 artifact 제목 단서만 갖고 있고 `slots.query`가 비어 있으면, `OpenAI Docs 다시 검색해줘` 같은 후속 요청을 같은 대상으로 검증하기 어렵고 `Python asyncio 다시 검색해줘` 같은 새 검색어도 `다시` 때문에 모호한 후속 요청으로 남을 수 있음을 확인했다.
  - `collect_text_values_from_state(..., key="query")`가 linked state slots/artifacts의 `title`, `titles`, `url_title`, `url_titles`도 검색 query 단서로 수집하도록 보강했다.
  - `has_explicit_new_target_reference()`가 `explicit_search_queries_from_text()` 결과를 새 target으로 인정하도록 바꿔, 명시적 새 검색어가 있으면 잘못된 이전 링크를 `clarify`가 아니라 `none`으로 제거하게 했다.
  - artifact `url_titles=["OpenAI Docs"]`만 있는 상태에서 `OpenAI Docs 다시 검색해줘`는 링크를 유지하고, `Python asyncio 다시 검색해줘`는 링크를 제거하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_keeps_search_link_from_artifact_url_title_query tests/test_route_validation.py::test_validate_route_context_link_clears_search_link_when_artifact_url_title_query_differs tests/test_route_validation.py::test_validate_route_context_link_keeps_search_link_from_subject_only_query tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_search_link_from_subject_only_query -q`(`4 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_bot_helpers.py tests/test_context_routing_matrix.py -q`(`516 passed`), `python3 -m pytest -q`(`892 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - web_url 복수 URL 슬롯 보강

- 작업 이름: 연결된 웹 결과의 복수 URL과 URL 제목을 실행 슬롯으로 복원
- 진행상황: 완료
- 진행내용:
  - `WebSearchAgent` 실행층은 linked artifact의 `urls`를 읽을 수 있지만, 실행 전 검증층의 `enrich_resolved_slots_from_linked_state()`는 `web_url` intent에서 단일 `url`만 보강해 교차 위치 확인이나 버튼 승인 같은 경로에서 복수 링크 단서가 약해질 수 있음을 확인했다.
  - `web_url` 슬롯 보강을 `url/urls` 쌍으로 확장해, 단일 URL은 `url`과 `urls`를 함께 남기고 복수 URL은 `urls`로 보존하도록 했다.
  - `url_title/url_titles`도 함께 보강하되, 사용자에게 보일 수 있는 제목의 대소문자와 표기는 정규화하지 않고 원문을 보존하도록 별도 display text 수집 경로를 추가했다.
  - artifact에 `urls`와 `url_titles`만 있는 상태, artifact에 단일 `url`과 `url_title`만 있는 상태를 각각 회귀 테스트로 고정했다.
  - `python3 -m pytest tests/test_route_validation.py::test_enrich_resolved_slots_backfills_plural_web_url_slots_from_artifacts tests/test_route_validation.py::test_enrich_resolved_slots_backfills_single_web_url_slot_from_artifact -q`(`2 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_web_search_agent.py -q`(`161 passed`, 이후 타이밍 민감 테스트 단독 재실행 `1 passed`), `python3 -m pytest -q`(`894 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 라우터 source reference 복수 artifact 텍스트 보강

- 작업 이름: 라우터 fallback이 복수 제목·파일명·URL 제목 artifact를 변환 요청 본문으로 사용하도록 개선
- 진행상황: 완료
- 진행내용:
  - `candidate_reference_text()`와 `candidate_reference_text_for_message()`가 artifact의 단일 `title`, `filename`, `name`, `url`만 읽고 있어, 새 에이전트가 `filenames`, `url_titles`, `titles` 같은 복수 필드만 남기면 `그 파일 할 일로 추가해줘`, `그 링크 메모로 저장해줘` 같은 변환 요청에서 본문이 `문서 분석 결과` 같은 일반 subject로 떨어질 수 있음을 확인했다.
  - artifact 참조 텍스트 수집 helper를 추가해 `title/titles`, `filename/filenames`, `attachment_name/attachment_names`, `name`, `url_title/url_titles`, `url/urls`를 같은 규칙으로 읽도록 했다.
  - 이 변경으로 새 에이전트가 단수 필드 대신 복수 artifact 필드를 남겨도 라우터 fallback이 사람이 읽기 좋은 대상명을 새 메모 본문, 할 일 제목, 알림 본문으로 복원할 수 있다.
  - `url_titles=["OpenAI Docs"]`만 있는 웹 결과를 `그 링크 메모로 저장해줘`의 `memory_text`로 쓰는 케이스와, `filenames=["contract.pdf"]`만 있는 문서 결과를 `그 파일 할 일로 추가해줘`의 `task_title`로 쓰는 케이스를 회귀 테스트에 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`(`137 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`372 passed`), `python3 -m pytest -q`(`896 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - turn state artifact 제목 target_hints 보강

- 작업 이름: 라우터 모델 컨텍스트의 target_hints가 artifact 제목 필드를 직접 포함하도록 개선
- 진행상황: 완료
- 진행내용:
  - turn state의 raw `artifacts`에는 `title`, `titles`, `name`이 남아 있어 fallback 파서는 읽을 수 있지만, 라우터 모델에게 명시적으로 전달되는 `target_hints`에는 해당 일반 제목 필드가 빠져 있어 모델 경로의 대상 일치 신호가 약해질 수 있음을 확인했다.
  - `add_turn_state_artifact_target_hints()`가 artifact의 `title`, `titles`, `name`도 target hint로 추가하도록 보강했다.
  - 새 에이전트가 메모/문서/작업/웹 결과 artifact에 일반 제목만 남겨도, 라우터 모델이 `target_hints`에서 사람이 읽기 쉬운 대상명을 직접 볼 수 있게 됐다.
  - `memory_ids=[8, 9]`와 `titles=["병원 예약", "장보기"]`만 있는 memory artifact가 `target_hints`에 `메모 8`, `메모 9`, `병원 예약`, `장보기`를 함께 남기는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_uses_artifact_titles_as_target_hints tests/test_context_builder.py::test_build_router_context_uses_artifact_attachment_names_as_target_hints tests/test_context_builder.py::test_build_router_context_uses_artifact_filenames_as_target_hints tests/test_context_builder.py::test_build_router_context_uses_artifact_urls_as_target_hints tests/test_context_builder.py::test_build_router_context_uses_slot_url_titles_as_target_hints -q`(`5 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`283 passed`), `python3 -m pytest -q`(`897 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - target_hints 목록형 결과 보존 한도 보강

- 작업 이름: ID가 많은 목록형 결과에서도 사람이 읽기 쉬운 제목 hint가 잘리지 않도록 개선
- 진행상황: 완료
- 진행내용:
  - `target_hints`가 8개로 잘리면서 `memory_ids`처럼 ID가 많은 목록형 결과에서는 뒤쪽의 artifact 제목이 raw artifacts에는 남아도 라우터 모델이 직접 보는 target_hints에서 사라질 수 있음을 확인했다.
  - target hint 보존 한도를 공통 상수 `TARGET_HINT_LIMIT=12`로 늘리고, turn state와 내부 행동 기록 target hint 생성이 같은 한도를 사용하도록 맞췄다.
  - `memory_ids=[1..8]`와 `titles=["병원 예약"]`이 함께 있는 기억 조회 결과에서 `병원 예약`이 target_hints 안에 남는 회귀 테스트를 추가했다.
  - 이 변경으로 목록형 결과에서도 ID 단서와 제목 단서가 함께 전달되어, 사용자가 “병원 예약 보여줘”처럼 제목으로 후속 요청할 때 모델 경로의 대상 판단 근거가 더 안정적으로 남는다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_keeps_artifact_title_when_many_ids_fill_target_hints tests/test_context_builder.py::test_build_router_context_uses_artifact_titles_as_target_hints tests/test_context_builder.py::test_build_router_context_uses_artifact_filenames_as_target_hints tests/test_context_builder.py::test_build_router_context_adds_internal_action_target_hints_and_guidance -q`(`4 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`284 passed`), `python3 -m pytest -q`(`898 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 목록형 artifact 제목 기반 슬롯 복원 보강

- 작업 이름: 정렬된 artifact 제목으로 특정 목록 항목 ID를 복원하도록 개선
- 진행상황: 완료
- 진행내용:
  - 목록형 artifact가 `memory_ids=[10, 12]`, `titles=["병원 예약", "장보기"]`처럼 ID와 제목을 같은 순서로 담고 있어도, 사용자가 `장보기 메모 보여줘`라고 말하면 라우터 fallback이 후보는 고르지만 실행 슬롯은 전체 `memory_ids=[10, 12]`로 남기는 문제를 확인했다.
  - `matched_artifact_slots_for_intent()`에 정렬된 `titles/title` 기반 ID 매칭을 추가해, 제목과 ID 개수가 일치하고 제목이 현재 메시지와 맞으면 해당 위치의 ID 하나로 좁히도록 했다.
  - 기존 정책상 `filenames` 기반 복수 문서 매칭은 파일명과 ID 정렬을 확신하지 않는 경우가 있어 그대로 애매하게 유지했다.
  - `장보기 메모 보여줘`가 `memory_id=12`로 복원되는 회귀 테스트를 추가하고, 기존 `contract.pdf 다시 분석해줘`가 복수 문서 ID에서 여전히 애매하게 남는 테스트를 함께 검증했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_fallback_restores_specific_memory_slot_from_aligned_artifact_titles tests/test_router_agent.py::test_router_fallback_keeps_plural_typed_document_artifact_filename_match_ambiguous -q`(`2 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`373 passed`), `python3 -m pytest -q`(`899 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation 복수 제목 단서 검증 보강

- 작업 이름: 실행 전 검증층이 artifact `titles`와 관련 제목 필드를 named target 검증에 사용하도록 개선
- 진행상황: 완료
- 진행내용:
  - 라우터 fallback은 `titles=["병원 예약", "장보기"]` 같은 복수 제목으로 특정 항목 ID를 복원할 수 있지만, route validation의 `title` 값 수집은 artifact `titles`를 보지 않아 `장보기 메모 보여줘`처럼 라우터가 고른 링크를 검증층이 잘못 제거할 수 있음을 확인했다.
  - `collect_text_values_from_state(..., key="title")`가 slots와 artifacts의 `titles`, `url_title`, `url_titles`, `filenames`, `attachment_names` 등 사람이 대상명으로 말할 수 있는 제목 계열 필드를 함께 수집하도록 보강했다.
  - `titles=["병원 예약", "장보기"]`가 있는 기억 조회 상태에서 `장보기 메모 보여줘`는 연결을 유지하고, `운동 루틴 메모 보여줘`는 named target mismatch로 연결을 제거하는 회귀 테스트를 추가했다.
  - 이 변경으로 라우터 후보 선택과 실행 전 검증이 같은 대상 단서를 공유해, 새 에이전트가 복수 제목 artifact를 남겨도 검증층과 라우터 판단이 엇갈릴 가능성이 줄었다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_named_target_from_artifact_titles tests/test_route_validation.py::test_validate_route_context_link_blocks_mismatched_named_target_from_artifact_titles tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_named_task_target tests/test_route_validation.py::test_validate_route_context_link_blocks_mismatched_named_task_target -q`(`4 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`375 passed`), `python3 -m pytest -q`(`901 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation 제목-ID 정렬 검증 보강

- 작업 이름: 실행 전 검증층이 복수 artifact 제목과 ID의 정렬 관계까지 확인하도록 개선
- 진행상황: 완료
- 진행내용:
  - 라우터가 `titles=["병원 예약", "장보기"]`와 `memory_ids=[10, 12]`를 보고 `장보기 메모 보여줘`를 `memory_id=12`로 좁힐 수 있지만, 모델 라우터가 실수로 `memory_id=10`을 반환해도 기존 검증층은 10이 상태의 ID 목록에 포함된다는 이유로 통과시킬 수 있음을 확인했다.
  - `resolved_slots_mismatch_linked_state()`가 사용자 문장의 named target과 artifact `titles/title`을 비교하고, 제목과 ID 개수가 정렬 가능한 경우 해당 제목 위치의 ID만 허용하도록 보강했다.
  - pending 승인 경로에서도 원래 사용자 문장(`pending_original_text`)을 사용해 같은 정렬 검증을 수행하도록 했다.
  - `장보기 메모 보여줘`에 대해 `memory_id=10`이 들어오면 aligned title ID `12`와 불일치해 연결을 제거하고, `memory_id=12`는 유지하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_rejects_wrong_id_for_matching_artifact_title tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_named_target_from_artifact_titles -q`(`2 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`376 passed`), `python3 -m pytest -q`(`902 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 제목-ID 정렬 검증 family별 회귀 보강

- 작업 이름: task/reminder에서도 제목-ID 정렬 안전망이 작동하는지 검증
- 진행상황: 완료
- 진행내용:
  - 제목-ID 정렬 검증 helper가 memory뿐 아니라 task/document/reminder typed ID도 읽도록 구현되어 있지만, 회귀 테스트는 memory 중심이라 family별 안전망이 약해질 수 있음을 확인했다.
  - `task_ids=[3, 8]`, `titles=["병원 예약", "장보기"]`인 상태에서 `장보기 완료했어`에 `task_id=3`이 잘못 들어오면 aligned title ID `8`과 불일치해 연결을 제거하는 테스트를 추가했다.
  - `reminder_ids=[5, 6]`, `titles=["물 마시기", "운동"]`인 상태에서 `물 마시기 알림 삭제해줘`에 `reminder_id=5`가 들어오면 연결을 유지하는 테스트를 추가했다.
  - 문서 filename 기반 복수 ID 정책은 기존처럼 애매함을 유지하고, 이번 보강은 명시적 `titles/title` 정렬에만 한정했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_rejects_wrong_task_id_for_matching_artifact_title tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_reminder_id_for_artifact_title tests/test_route_validation.py::test_validate_route_context_link_rejects_wrong_id_for_matching_artifact_title -q`(`3 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`378 passed`), `python3 -m pytest -q`(`904 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 제목-ID 정렬 기반 슬롯 enrichment 보강

- 작업 이름: 모델이 resolved_slots를 비웠을 때도 제목으로 특정 목록 항목 ID를 복원
- 진행상황: 완료
- 진행내용:
  - 모델 라우터가 `장보기 메모 보여줘`를 이전 기억 조회 상태와 연결했지만 `resolved_slots`를 비워 두면, 기존 enrichment는 `memory_ids=[10, 12]` 전체를 실행 슬롯으로 채워 실제 에이전트가 목록 전체를 대상으로 삼을 수 있음을 확인했다.
  - `enrich_resolved_slots_from_linked_state()`가 선택적으로 `user_text`를 받아, artifact `titles/title`과 ID가 정렬 가능한 경우 전체 ID 목록보다 사용자 문장의 named target에 맞는 단일 ID를 우선 채우도록 보강했다.
  - `build_execution_context()`와 후속 확인 질문 생성 경로가 원래 사용자 문장을 enrichment에 전달하도록 연결했다.
  - `장보기 메모 보여줘`는 `memory_id=12`, `memory_ids=[12]`로 복원하고, 제목 단서가 없는 `메모 목록 보여줘`는 기존처럼 `memory_ids=[10, 12]`를 유지하는 회귀 테스트를 추가했다.
  - 실제 `ExecutionContext` 생성 경로에서도 `장보기 메모 보여줘`가 단일 `memory_id=12`로 들어가는지 검증했다.
  - `python3 -m pytest tests/test_route_validation.py::test_enrich_resolved_slots_uses_aligned_title_id_before_full_id_list tests/test_route_validation.py::test_enrich_resolved_slots_keeps_full_id_list_without_aligned_title tests/test_context_builder.py::test_build_execution_context_enriches_aligned_title_id_from_linked_state -q`(`3 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`427 passed`), `python3 -m pytest -q`(`907 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 확인 질문 pending 슬롯 enrichment 보강

- 작업 이름: 확인 버튼/확인 질문 경로에서도 제목 기반 대상 슬롯을 보존
- 진행상황: 완료
- 진행내용:
  - 일반 실행 컨텍스트는 `장보기 메모 보여줘`처럼 제목 단서가 있는 후속 요청을 `memory_id=12`로 복원하지만, 확인 질문 결과를 만들 때는 `route.resolved_slots`가 비어 있으면 linked state enrichment를 건너뛰어 pending 슬롯이 빈 dict로 저장될 수 있음을 확인했다.
  - `build_context_clarification_result()`가 linked state와 원문을 갖고 있으면 빈 슬롯 상태에서도 enrichment를 시도하도록 수정했다.
  - 다만 모델이 잘못된 ID를 반환해 route validation이 `resolved_slots ... 일치하지 않음` 사유로 슬롯을 비운 경우에는, 검증기가 일부러 비운 결정을 존중하도록 자동 보강을 막았다.
  - `memory_ids=[10, 12]`, `titles=["병원 예약", "장보기"]`인 linked state에서 `장보기 메모 보여줘` 확인 질문의 `pending_resolved_slots`가 `{"memory_id": 12, "memory_ids": [12]}`로 저장되는 회귀 테스트를 추가했다.
  - 동시에 잘못된 `document_id=7`이 `문서 9 other.pdf` 상태와 충돌해 확인 질문으로 넘어가는 경우에는 `pending_resolved_slots`를 빈 dict로 유지하는 기존 안전 테스트를 함께 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_build_context_clarification_result_enriches_empty_slots_from_linked_title tests/test_bot_helpers.py::test_assistant_bot_clarifies_parsed_model_resolved_slot_mismatch_before_dispatch -q`(`2 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_route_validation.py tests/test_context_builder.py -q`(`293 passed`), `python3 -m pytest -q`(`908 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 기록 최신성 표시 보강

- 작업 이름: 내부 기록 우선순위 정렬과 실제 최신성 표시 분리
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록 컨텍스트가 현재 위치와 route validation 로그를 우선 보존하도록 정렬하면서, 정렬 후 순서를 기준으로 `recency=latest/older`를 붙이고 있음을 확인했다.
  - 이 구조에서는 오래된 `route_validation` 로그가 우선순위 때문에 위로 올라오면 실제 최신 로그가 아닌데도 `recency=latest`로 표시되어, 라우터가 최신 맥락을 잘못 판단할 수 있었다.
  - `AgentLogStore.recent()`와 `recent_for_conversations()`가 로그 `id`를 함께 반환하도록 바꾸고, `build_internal_action_context()`가 정렬 전에 실제 최신순 기준으로 recency label을 계산하도록 수정했다.
  - 우선순위상 오래된 검증 로그가 최신 라우터 로그보다 위에 표시되더라도, 검증 로그는 `recency=older`, 실제 최신 라우터 로그는 `recency=latest`로 남는 회귀 테스트를 추가했다.
  - 이 변경으로 내부 기록은 여전히 중요한 검증 로그를 보존하되, 라우터가 “가장 최근 내부 판단”을 착각하지 않도록 최신성 단서를 더 정확하게 전달한다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_keeps_actual_internal_action_recency_after_priority_sort tests/test_context_builder.py::test_build_router_context_orders_internal_action_logs_latest_first -q`(`2 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_cli.py -q`(`228 passed`), `python3 -m pytest -q`(`909 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 자연어 교체 표현 기반 새 대상 차단 보강

- 작업 이름: `아니고/아니라/대신에` 표현으로 새 대상을 말할 때 이전 맥락 과연결 방지
- 진행상황: 완료
- 진행내용:
  - route validation은 `말고`, `대신` 뒤의 텍스트를 새 대상 판단에 우선 사용하지만, 사용자가 자연스럽게 쓰는 `아니고`, `아니라`, `대신에` 표현은 분리하지 못할 수 있음을 확인했다.
  - `replacement_effective_user_text()`가 `말고`, `대신`, `대신에`, `아니고`, `아니라`를 모두 새 대상 분리 마커로 인식하도록 보강했다.
  - `원주 아니고 서울 날씨 알려줘`처럼 이전 날씨 상태와 다른 지역을 말하는 경우, linked state를 유지하지 않고 새 요청으로 처리하도록 route validation 회귀 테스트를 추가했다.
  - 함수 단위 테스트도 추가해 `원주 말고/대신에/아니고/아니라 서울 날씨 알려줘`가 모두 `서울날씨알려줘`를 새 판단 텍스트로 사용함을 검증했다.
  - 이 변경으로 내부 기록이나 최근 작업 후보가 있더라도, 사용자가 교체 표현으로 새 대상을 말한 경우 이전 맥락에 과연결될 가능성을 줄였다.
  - `python3 -m pytest tests/test_route_validation.py::test_replacement_effective_user_text_handles_natural_replacement_markers tests/test_route_validation.py::test_validate_route_context_link_clears_replacement_marker_new_weather_target -q`(`2 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`382 passed`), `python3 -m pytest -q`(`911 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 새 요청 전환 접두어 대상 정규화 보강

- 작업 이름: `이번엔/이번에는/새로` 표현의 대상 오염 방지
- 진행상황: 완료
- 진행내용:
  - `이번엔 서울 날씨 알려줘` 같은 표현은 이전 상태와 다른 대상임을 감지할 수는 있지만, 새 대상 텍스트가 `이번엔서울`처럼 오염되어 이후 지역/검색어 판단 품질이 떨어질 수 있음을 확인했다.
  - `replacement_effective_user_text()`에 전환 접두어 제거 helper를 추가해 `이번엔`, `이번에는`, `이번에`, `새로`, `새롭게`를 새 대상 판단 텍스트에서 제거하도록 했다.
  - 교체 표현 뒤에 `이번엔 새로 ...`처럼 전환 접두어가 겹쳐도 최대 3회까지 앞부분을 정리하도록 했다.
  - `이번엔 서울 날씨 알려줘`가 `서울날씨알려줘`로 정규화되고, `이번엔 Python 검색해줘`가 검색어 `python`으로 추출되는 함수 단위 회귀 테스트를 추가했다.
  - 실제 route validation에서도 `이번엔 서울 날씨 알려줘`가 기존 `원주 날씨` 상태와 연결되지 않고 새 요청으로 처리되며, 검증 사유에 `이번엔서울` 같은 오염 대상이 남지 않음을 확인했다.
  - `python3 -m pytest tests/test_route_validation.py::test_replacement_effective_user_text_handles_natural_replacement_markers tests/test_route_validation.py::test_validate_route_context_link_clears_transition_prefix_new_weather_target tests/test_route_validation.py::test_validate_route_context_link_clears_replacement_marker_new_weather_target -q`(`3 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`383 passed`), `python3 -m pytest -q`(`912 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - TaskAgent 제목 변경 linked context 보강

- 작업 이름: 할 일 제목 변경도 linked task ID를 사용하도록 개선
- 진행상황: 완료
- 진행내용:
  - TaskAgent의 완료/삭제/미루기/상세 조회는 `ExecutionContext`의 `resolved_slots`와 `linked_state`에서 task ID를 읽지만, 제목 변경(`rename`) 분기는 linked task ID를 사용하지 않아 `그거 제목 바꿔줘` 같은 후속 요청이 다시 ID 요청으로 멈출 수 있음을 확인했다.
  - 제목 변경 분기도 기존에 계산된 `task_ids`를 그대로 사용하고, ID가 없을 때는 `resolve_task_ids_from_text()`로 제목 단서 검색을 시도하도록 수정했다.
  - 이 변경으로 라우터가 이미 `linked_state_id`와 `resolved_slots.task_id`를 정확히 넘긴 경우, TaskAgent가 최신 할 일이 아니라 연결된 할 일을 제목 변경 대상으로 사용한다.
  - 다른 위치에서 만든 linked task와 현재 위치 최신 task가 함께 있을 때 `방금 추가한 할 일을 고객 미팅 준비로 바꿔줘`가 linked task만 변경하고 현재 위치 최신 task는 그대로 두는 회귀 테스트를 추가했다.
  - 이 보강은 “라우터가 잘 고른 대상이 전문 에이전트에서 다시 흐려지는 문제”를 줄여, 공통 작업 상태 기반 맥락 판단이 실제 실행 단계까지 이어지도록 한다.
  - `python3 -m pytest tests/test_memory_store.py::test_task_agent_rename_prefers_linked_task_context_over_latest_item -q`(`1 passed`), `python3 -m pytest tests/test_memory_store.py tests/test_agent_registry.py tests/test_context_routing_matrix.py -q`(`277 passed`), `python3 -m pytest -q`(`913 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - ReminderAgent linked subject 본문 정규화 보강

- 작업 이름: linked reminder subject에서 새 알림 본문을 깔끔하게 추출
- 진행상황: 완료
- 진행내용:
  - linked reminder 상태에 `reminder_text`나 artifact title이 없으면 새 알림 생성 본문이 subject에서 오는데, `알림 5 물 마시기` 같은 subject가 그대로 본문이 될 수 있음을 확인했다.
  - ReminderAgent에 `normalize_context_reminder_text()`를 추가해 subject/summary 앞의 `알림 5` 같은 ID 접두어와 구분 기호를 제거하도록 했다.
  - `그 알림 30분 뒤 다시 알려줘`가 linked reminder subject `알림 5 물 마시기`를 참고할 때, 새 알림 본문을 `물 마시기`로 저장하는 회귀 테스트를 추가했다.
  - 이 변경으로 라우터가 기존 알림 상태를 정확히 연결하더라도 최종 알림 본문이 시스템식 ID 문자열로 오염되는 일을 줄였다.
  - `python3 -m pytest tests/test_memory_store.py::test_reminder_agent_normalizes_linked_reminder_subject_as_new_reminder_text -q`(`1 passed`), `python3 -m pytest tests/test_memory_store.py tests/test_context_routing_matrix.py tests/test_agent_registry.py -q`(`278 passed`), `python3 -m pytest -q`(`914 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 로그 item 대상명 보존 보강

- 작업 이름: 목록형 OperationResult item도 후속 맥락 target hint로 남기기
- 진행상황: 완료
- 진행내용:
  - 내부 행동 결과 로그는 `artifacts`를 중심으로 대상 ID/제목을 남기지만, 일부 에이전트가 `items`에만 `memory_text`, `attachment_name`, `name` 같은 사용자 지칭 가능 필드를 넣으면 다음 턴 라우터가 “방금 본 항목”을 덜 정확히 연결할 수 있음을 확인했다.
  - `infer_turn_artifact_from_item()`가 `name`, `attachment_name(s)`, `memory_text`, `task_title`, `reminder_text`를 보존하고, 명시적 `title`이 없을 때 이 값들을 artifact title로 승격하도록 수정했다.
  - 내부 로그의 artifact 제목 수집도 같은 필드를 읽도록 보강해, `items` 기반 목록 결과가 `memory_titles`, `document_titles` 같은 구조 단서로 남게 했다.
  - `build_internal_action_context()`의 target hint 키에 `memory_text`, `task_title`, `name`, `text`를 추가해 라우터가 내부 기록에서 자연어 대상명을 직접 참고할 수 있게 했다.
  - `memory_id=12`, `memory_text=오늘 저녁 뭐먹을지 고민해보기`, `document_id=7`, `attachment_name=회의록.pdf` 형태의 item만 있어도 내부 로그와 라우터 컨텍스트에 `메모 12`, `문서 7`, 각 제목이 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_preserves_item_title_fields_as_target_hints -q`(`1 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py -q`(`256 passed`), `python3 -m pytest -q`(`915 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 공통 artifact 텍스트 필드 표준 확장

- 작업 이름: linked state artifact의 도메인별 텍스트 필드를 에이전트 공통 helper에서 인식
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그는 `memory_text`, `task_title`, `reminder_text`, `text`를 target hint로 보존하도록 보강했지만, 실제 에이전트들이 linked state artifact에서 본문을 꺼낼 때 쓰는 `first_artifact_text()`는 아직 해당 필드를 읽지 않음을 확인했다.
  - `DEFAULT_ARTIFACT_TEXT_FIELDS`에 `memory_text`, `task_title`, `reminder_text`, `text`를 추가해 MemoryAgent, TaskAgent, ReminderAgent가 같은 artifact 텍스트 표준을 공유하도록 수정했다.
  - 이 변경으로 새 에이전트나 목록 결과가 명시적 `title` 없이 도메인별 텍스트 필드만 남겨도, “그 메모 할 일로 만들어줘”, “그 작업 메모로 저장해줘”, “그 알림 다시 알려줘” 같은 변환형 후속 요청에서 대상 본문을 더 안정적으로 복원할 수 있다.
  - `first_artifact_text()`가 `memory_text`, `task_title`, `reminder_text`, `text`를 순서대로 읽는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_memory_store.py::test_first_artifact_text_reads_domain_specific_text_fields -q`(`1 passed`), `python3 -m pytest tests/test_memory_store.py tests/test_context_routing_matrix.py tests/test_agent_registry.py -q`(`279 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py -q`(`256 passed`), `python3 -m pytest -q`(`916 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - WebSearchAgent 긴 후속 검색 resolved query 보존

- 작업 이름: 긴 재검색 요청에서도 라우터가 복원한 검색어를 우선 사용
- 진행상황: 완료
- 진행내용:
  - `linked_search_text()`가 문장 길이 24자를 넘으면 linked query 복원을 중단해, “아까 검색했던 내용 캐시 쓰지 말고 다시 검색해줘”처럼 자연스러운 긴 후속 요청에서 라우터가 이미 `resolved_slots.query`를 넘겼는데도 검색어를 잃을 수 있음을 확인했다.
  - 라우터 검증을 통과해 `ExecutionContext.resolved_slots.query/queries`에 들어온 검색어는 문장 길이와 무관하게 우선 사용하도록 수정했다.
  - linked state의 slots/artifacts만으로 추론하는 막연한 검색어 복원은 기존처럼 짧고 명확한 후속 표현에만 동작하도록 유지해, 새 요청을 이전 검색에 과연결할 위험은 줄였다.
  - `아까 검색했던 내용 캐시 쓰지 말고 다시 검색해줘`가 `resolved_slots.query=OpenAI 최신 뉴스`를 사용해 검색하고, 캐시 정책은 사용자 문장 기준으로 `bypass_cache`가 유지되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_web_search_agent.py::test_web_search_agent_uses_resolved_query_for_long_retry_request -q`(`1 passed`), `python3 -m pytest tests/test_web_search_agent.py -q`(`28 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`287 passed`), `python3 -m pytest -q`(`917 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답 컨텍스트 artifact 텍스트 필드 보존

- 작업 이름: 최종 응답 생성에서도 도메인별 artifact 텍스트를 참고하도록 보강
- 진행상황: 완료
- 진행내용:
  - 라우터와 에이전트 공통 helper는 `memory_text`, `task_title`, `reminder_text`, `text`를 linked artifact 텍스트로 인식하지만, `ExecutionContext.for_response()`의 안전 필터는 이 필드를 제외해 최종 응답 작성자가 실제 대상 본문을 덜 볼 수 있음을 확인했다.
  - 응답용 linked state artifact 필터에 `memory_text`, `task_title`, `reminder_text`, `text`를 추가했다.
  - 내부 route metadata, pending 슬롯, 검증 로그는 계속 숨기면서도, 사용자에게 자연스러운 답변을 만드는 데 필요한 실제 메모/할 일/알림/일반 텍스트 단서는 보존하도록 정리했다.
  - `memory_text=오늘 저녁 뭐먹을지 고민해보기`, `task_title=병원 예약`, `reminder_text=물 마시기`, `text=회의록 정리`가 응답 컨텍스트에 남는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_keeps_domain_specific_artifact_text_fields -q`(`1 passed`), `python3 -m pytest tests/test_response_composer.py -q`(`21 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py -q`(`154 passed`), `python3 -m pytest -q`(`918 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - Route validation artifact 도메인 텍스트 정렬 보강

- 작업 이름: ID 목록과 도메인별 텍스트 목록을 정렬해 단일 대상 복원/검증
- 진행상황: 완료
- 진행내용:
  - 라우터와 에이전트, 응답 컨텍스트는 `memory_text`, `task_title`, `reminder_text`, `text`를 대상 텍스트로 인식하지만, route validation의 `aligned_artifact_title_values()`는 `title/titles`만 사용해 `memory_ids`와 `memory_text` 목록을 정렬하지 못할 수 있음을 확인했다.
  - `aligned_artifact_title_values()`가 `titles/title`뿐 아니라 `memory_text`, `task_title`, `reminder_text`, `text`, 파일명, URL 제목, 이름 필드를 후보로 읽도록 확장했다.
  - 여러 텍스트 필드가 동시에 있을 때는 ID 개수와 같은 길이의 필드 그룹을 우선 선택하도록 바꿔, `titles`와 `memory_text`가 함께 있는 artifact에서 제목 개수가 중복되어 정렬이 깨지는 일을 피했다.
  - `memory_ids=[10, 12]`, `memory_text=["병원 예약", "장보기"]`인 상태에서 `장보기 메모 보여줘`는 `memory_id=12`로 좁히고, 라우터가 잘못 `memory_id=10`을 고르면 검증 단계에서 연결을 제거하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_enrich_resolved_slots_uses_aligned_domain_text_id_before_full_id_list tests/test_route_validation.py::test_validate_route_context_link_rejects_wrong_id_for_matching_artifact_domain_text -q`(`2 passed`), `python3 -m pytest tests/test_route_validation.py -q`(`146 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`287 passed`), `python3 -m pytest -q`(`920 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - Route validation named target 도메인 텍스트 mismatch 보강

- 작업 이름: 명시적 대상명 검증에서도 artifact 도메인 텍스트를 사용
- 진행상황: 완료
- 진행내용:
  - `aligned_artifact_title_values()`는 도메인별 텍스트를 보도록 보강했지만, `explicit_text_target_mismatch_linked_state()`가 사용하는 `collect_text_values_from_state(..., key="title")`의 artifact 수집 경로는 여전히 `memory_text`, `task_title`, `reminder_text`, `text`를 제외하고 있음을 확인했다.
  - 이 상태에서는 linked artifact에 `memory_text`만 있는 경우, 사용자가 명시한 `운동 루틴 메모 보여줘` 같은 새 대상명이 기존 `장보기` 상태와 불일치해도 state title 값이 비어 있어 검증을 지나칠 수 있었다.
  - artifact title 수집 경로에 `memory_text`, `task_title`, `reminder_text`, `text`를 추가해, 단일 대상 복원뿐 아니라 explicit target mismatch 방어선도 같은 artifact 텍스트 표준을 쓰도록 맞췄다.
  - `memory_text=["병원 예약", "장보기"]` 상태에서 `장보기 메모 보여줘`는 유지하고, `운동 루틴 메모 보여줘`는 named target mismatch로 링크를 제거하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_named_target_from_artifact_domain_text tests/test_route_validation.py::test_validate_route_context_link_blocks_mismatched_named_target_from_artifact_domain_text -q`(`2 passed`), `python3 -m pytest tests/test_route_validation.py -q`(`148 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`287 passed`), `python3 -m pytest -q`(`922 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 에이전트 카탈로그 후속 맥락 계약 보강

- 작업 이름: 새 에이전트 추가 시 도메인별 대상 텍스트 누락 방지
- 진행상황: 완료
- 진행내용:
  - `agent_catalog.json`의 `state_outputs` 계약은 존재하지만, 실제 라우터 artifact 매칭과 turn state target hint 생성 경로가 `title` 중심으로 남아 있어 `memory_text`, `task_title`, `reminder_text`, `text`만 가진 artifact를 새 에이전트가 만들면 후속 맥락 인식이 약해질 수 있음을 확인했다.
  - `TURN_STATE_TARGET_HINT_SLOT_KEYS`와 artifact target hint 수집 필드에 `memory_text`, `task_title`, `reminder_text`, `text`를 추가해 최근 작업 상태 후보가 도메인별 본문을 target hint로 제공하도록 했다.
  - 라우터의 `ARTIFACT_MATCH_FIELDS`, `artifact_aligned_title_values()`, `artifact_reference_text_values()`도 같은 도메인별 텍스트 필드를 읽도록 맞춰, ID-텍스트 정렬, 대상명 매칭, 후속 참조 텍스트 추출이 같은 필드 표준을 공유하게 했다.
  - 라우터의 artifact 매칭 필드가 공통 `DEFAULT_ARTIFACT_TEXT_FIELDS`를 직접 사용하도록 정리해, 향후 에이전트 공통 artifact 텍스트 필드를 확장할 때 라우터 대상 매칭만 따로 누락되는 위험을 줄였다.
  - 카탈로그 테스트에 도메인별 artifact 텍스트 필드가 라우터 대상 매칭 계약에 포함되는지 확인하는 검증을 추가했고, context builder 테스트에 turn state target hint가 `memory_text`, `task_title`, `reminder_text`를 실제로 노출하는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_artifact_domain_text_fields_are_available_for_router_target_matching tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_turn_state_hints tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_internal_action_target_hints tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_internal_route_slot_merge tests/test_context_builder.py::test_turn_state_target_hints_include_domain_specific_artifact_text_fields -q`(`5 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py -q`(`329 passed`), `python3 -m pytest tests/test_agent_registry.py::test_artifact_domain_text_fields_are_available_for_router_target_matching tests/test_context_builder.py::test_turn_state_target_hints_include_domain_specific_artifact_text_fields tests/test_router_agent.py tests/test_context_builder.py -q`(`153 passed`), `python3 -m pytest -q`(`924 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - ConversationAgent 실행용 맥락 사용 보강

- 작업 이름: 일반 대화 답변에서도 linked state와 라우터 복원 슬롯을 직접 참고
- 진행상황: 완료
- 진행내용:
  - 전문 에이전트들은 `ExecutionContext.for_agent()`를 사용하지만, ConversationAgent는 실행 단계에서도 `for_router()`를 재사용해 라우터 후보 목록은 보면서 `연결된 이전 작업 상태`와 `라우터 복원 슬롯` 섹션을 놓칠 수 있음을 확인했다.
  - 일반 대화가 “그 기준으로 더 이야기해줘”, “아까 그 메모 기준으로 답해줘”처럼 작업 상태와 이어지는 답변을 만들 때 필요한 linked state와 resolved slot을 직접 볼 수 있도록 `execution_context.for_agent()`를 사용하게 변경했다.
  - `memory_id=12`, `memory_text=오늘 저녁 메뉴 고민`이 연결된 상태에서 ConversationAgent 프롬프트에 `연결된 이전 작업 상태`, `라우터 복원 슬롯`, 실제 메모 제목/본문이 포함되는 회귀 테스트를 추가했다.
  - 이 변경으로 라우터가 맥락을 올바르게 연결했는데도 일반 대화 에이전트가 최종 답변에서 그 연결 정보를 덜 참고하는 실행 단계 손실을 줄였다.
  - `python3 -m pytest tests/test_memory_store.py::test_conversation_agent_includes_current_time_context tests/test_memory_store.py::test_conversation_agent_uses_agent_execution_context_for_linked_state tests/test_memory_store.py::test_conversation_agent_compress_context_preserves_previous_summary -q`(`3 passed`), `python3 -m pytest tests/test_memory_store.py tests/test_context_builder.py tests/test_response_composer.py tests/test_agent_registry.py -q`(`214 passed`), `python3 -m pytest -q`(`925 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - ConversationAgent linked state 단독 맥락 보강

- 작업 이름: 요약/최근 대화 없이 linked state만 있어도 실행용 맥락 사용
- 진행상황: 완료
- 진행내용:
  - ConversationAgent가 `for_agent()`를 쓰도록 바꿨지만 조건이 `latest_summary` 또는 `recent_context` 존재 여부에 묶여 있어, 라우터가 `linked_state`와 `resolved_slots`만 넘긴 경우에는 여전히 기존 최근 대화 컨텍스트로 fallback할 수 있음을 확인했다.
  - `execution_context.for_agent()` 결과가 비어 있지 않으면 항상 실행용 컨텍스트를 사용하도록 조건을 변경했다.
  - `latest_summary`, `recent_context`, `focused_context`가 비어 있고 `linked_state=할 일 15 병원 예약`, `resolved_slots.task_id=15`만 있는 경우에도 ConversationAgent 프롬프트에 `연결된 이전 작업 상태`와 `라우터 복원 슬롯`이 포함되는 회귀 테스트를 추가했다.
  - 이 변경으로 라우터가 최소한의 구조화 맥락만 복원한 후속 일반 대화도 실행 단계에서 이전 작업 대상을 잃지 않게 했다.
  - `python3 -m pytest tests/test_memory_store.py::test_conversation_agent_uses_agent_execution_context_for_linked_state tests/test_memory_store.py::test_conversation_agent_uses_linked_state_even_without_recent_context -q`(`2 passed`), `python3 -m pytest tests/test_memory_store.py tests/test_context_builder.py tests/test_response_composer.py -q`(`185 passed`), `python3 -m pytest -q`(`926 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답 컨텍스트 내부 로그 필드명 한글화 보강

- 작업 이름: 최종 응답 작성자가 내부 키 이름을 덜 끌고 오도록 정리
- 진행상황: 완료
- 진행내용:
  - `response_safe_internal_action_context()`는 내부 행동 기록을 최종 응답 작성자에게 비공개 참고로 제공하지만, `_humanize_internal_values()`가 `memory_text` 정도만 한글화하고 `task_title`, `reminder_text`, `filenames`, `url_titles` 같은 도메인별 필드는 시스템식 키로 남길 수 있음을 확인했다.
  - 내부 값 한글화 로직을 복수형 우선 매핑 방식으로 바꿔 `memory_ids`가 `메모 IDs`처럼 어색하게 변환되는 일을 막았다.
  - `task_ids`, `reminder_ids`, `filenames`, `url_titles`, `task_title`, `reminder_text`, `document_title` 등 후속 맥락 대상/본문 필드를 사람이 읽기 쉬운 한국어 라벨로 바꾸도록 확장했다.
  - 최종 응답 컨텍스트에서 내부 행동 기록이 `할 일 ID 목록`, `할 일 제목`, `알림 내용`, `파일명 목록`, `링크 제목 목록`으로 노출되고 원래 시스템 키가 남지 않는 회귀 테스트를 추가했다.
  - 이 변경으로 내부 행동 로그는 계속 답변 작성의 힌트로 쓰되, 모델이 사용자 답변에 `task_title`, `reminder_text` 같은 기계적인 필드명을 흘릴 가능성을 줄였다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_humanizes_internal_domain_fields tests/test_response_composer.py::test_execution_context_response_prioritizes_linked_state_over_internal_action_when_truncated tests/test_response_composer.py::test_execution_context_response_hides_private_route_metadata_from_resolved_slots -q`(`3 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_bot_helpers.py -q`(`177 passed`), `python3 -m pytest -q`(`927 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 새 요청 라우팅 시 첨부 저장 대기 만료 보강

- 작업 이름: 오래된 첨부 저장 확인이 새 요청 뒤에 남아 맥락을 오염시키지 않도록 정리
- 진행상황: 완료
- 진행내용:
  - 새 요청 라우팅 시 삭제 확인과 웹검색 확인 대기는 만료되지만, 첨부 저장 확인 대기는 남아 있어 이후의 `응 기억해줘` 같은 승인 문장이 오래된 파일 저장으로 이어질 수 있음을 확인했다.
  - `PendingAttachmentStore.resolve_open()`을 추가하고, 봇/CLI의 일반 pending 만료 흐름에서 첨부 저장 대기도 함께 닫도록 변경했다.
  - 만료 로그에 `pending_attachment_requests` 개수를 포함해, 내부 행동 기록과 라우터 컨텍스트에서 어떤 대기 작업이 정리됐는지 확인할 수 있게 했다.
  - 디스코드 경로에서 첨부 저장 대기 중 `응 확인 상태 알려줘`처럼 확인 표현과 새 요청이 섞인 메시지가 오면 상태 요청을 처리하고 오래된 첨부 대기를 제거하는 회귀 테스트를 추가했다.
  - CLI 경로의 일반 pending 만료 테스트도 첨부 저장 대기까지 포함하도록 확장했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_expires_stale_general_pending_on_new_request tests/test_bot_helpers.py::test_assistant_bot_expires_stale_pending_attachment_on_new_request tests/test_cli.py::test_cli_expires_stale_general_pending_confirmations_on_new_request -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_route_validation.py tests/test_context_builder.py tests/test_response_composer.py -q`(`404 passed`), `python3 -m pytest -q`(`928 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 첨부 저장 대기 채팅 승인 보존 보강

- 작업 이름: 새 요청 만료 정책과 `응 기억해줘` 첨부 저장 승인의 충돌 방지
- 진행상황: 완료
- 진행내용:
  - 첨부 저장 대기를 새 요청에서 만료하도록 바꾼 뒤, 사용자가 실제 안내 문구대로 `응, 기억해줘`라고 채팅 승인하면 `remember` 라우팅 중 pending 첨부가 먼저 만료되어 원본 파일을 저장하지 못할 수 있음을 확인했다.
  - `is_pending_attachment_approval_text()`를 추가해 `기억해/저장해` 문구이면서 실제 저장 본문이 없는 경우를 첨부 저장 승인으로 분리했다.
  - 봇과 CLI의 일반 pending 만료 흐름에서 `remember` 라우팅이라도 본문 없는 첨부 저장 승인 문구는 첨부 pending을 유지하고, `기억해줘: 새 메모 내용`처럼 본문이 있는 새 메모 요청은 오래된 첨부 pending을 만료하도록 조정했다.
  - 디스코드 경로에서 `응, 기억해줘`가 원본 첨부 메시지를 fetch해 문서로 저장하고 pending을 종료하는 통합 회귀 테스트를 추가했다.
  - 반대로 `기억해줘: 새 메모 내용`은 오래된 첨부 pending을 만료하고 내부 로그에 `pending_attachment_requests=1`을 남기는 테스트를 추가했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_expires_stale_pending_attachment_on_new_request tests/test_bot_helpers.py::test_assistant_bot_keeps_pending_attachment_for_chat_approval tests/test_bot_helpers.py::test_assistant_bot_expires_pending_attachment_for_substantive_new_memory -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_route_validation.py tests/test_context_builder.py tests/test_response_composer.py -q`(`406 passed`), `python3 -m pytest -q`(`930 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 새 메모 본문 요청의 과잉 맥락 연결 방지

- 작업 이름: `remember` 후속 연결 검증에서 새 메모 본문 우선 처리
- 진행상황: 완료
- 진행내용:
  - 라우터/컨텍스트 후보 포맷은 `sanitize_turn_state_context_value()`와 기존 회귀 테스트로 구분자, 줄바꿈, 긴 사용자 값을 방어하고 있음을 확인했다.
  - 다음 위험 지점으로 `remember` intent가 “그 검색 결과 메모로 저장해줘” 같은 출처 변환을 지원하기 위해 여러 이전 상태와 호환될 수 있는 구조를 확인했다.
  - 이 구조에서는 라우터가 실수로 `운동 루틴은 아침에 하는 게 좋다 기억해줘` 같은 새 메모 본문 요청을 직전 문서/작업 상태에 연결하면, 실제 사용자는 새 메모 저장을 원했는데 이전 작업 후속 처리처럼 실행될 가능성이 있었다.
  - `unrelated_new_request_mismatch_linked_state()`에 새 메모 본문 저장 요청 방어선을 추가해, 명시적 출처 변환이나 애매한 후속 참조가 아닌 실질적 메모 본문 요청은 실행 전 검증 단계에서 `context_link=none`으로 정리하도록 했다.
  - 순환 import를 피하기 위해 `has_substantive_memory_text()`는 검증 함수 내부의 지연 import로 호출한다.
  - `운동 루틴은 아침에 하는 게 좋다 기억해줘`가 이전 `contract.pdf` 문서 상태와 잘못 연결되지 않는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_route_validation.py -q`(`149 passed`), `python3 -m pytest tests/test_router_agent.py::test_router_fallback_does_not_link_unrelated_new_chat_to_recent_state tests/test_context_builder.py::test_turn_state_context_sanitizes_delimiters_inside_state_values -q`(`2 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`437 passed`), `python3 -m pytest -q`(`931 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 에이전트 카탈로그 슬롯 출력 계약 보강

- 작업 이름: 실제 `OperationResult` 슬롯과 카탈로그 `state_outputs` 불일치 방지
- 진행상황: 완료
- 진행내용:
  - 기존 카탈로그 테스트는 선언된 `state_outputs`가 컨텍스트 빌더, 내부 로그, 라우터 검증에서 보존되는지는 잘 확인했지만, 코드가 새 slot을 반환하면서 카탈로그에 선언하지 않는 경우를 일부 놓칠 수 있음을 확인했다.
  - 실제 리터럴 `OperationResult(slots={...})`를 점검해 `help`의 `topic`, `remember`/`delete_memory`의 `canceled_target`이 카탈로그에 선언되지 않은 채 반환되는 경로를 찾았다.
  - `agent_catalog.json`의 `help`, `remember`, `delete_memory` 항목에 각각 `slots.topic`, `slots.canceled_target`을 추가해 라우터 프롬프트와 내부 행동 기록 계약이 실제 출력과 맞도록 정리했다.
  - `test_agent_catalog_declares_literal_operation_result_slots`를 추가해 앞으로 새 에이전트나 새 결과 슬롯이 추가될 때 카탈로그 선언 누락을 테스트가 잡도록 했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`31 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py -q`(`331 passed`), `python3 -m pytest -q`(`932 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 에이전트 카탈로그 artifact 추론 계약 보강

- 작업 이름: `items` 기반 artifact 추론과 내부 로그 보존 계약 고정
- 진행상황: 완료
- 진행내용:
  - `OperationResult.artifacts`가 직접 채워지는 경우뿐 아니라 `items`에서 `infer_turn_artifacts()`로 artifact가 추론되는 경로도 후속 맥락 판단의 핵심임을 확인했다.
  - 기존 카탈로그 테스트는 선언된 artifact 출력명이 내부 행동 로그에 보존되는지는 샘플로 확인했지만, `items -> infer_turn_artifacts -> safe_internal_action_artifact_values` 흐름까지 직접 고정하지는 않았다.
  - 카탈로그가 선언한 artifact 출력명(`memory_ids`, `document_ids`, `task_ids`, `reminder_ids`, `urls`, `url_titles`)이 `items` 기반 추론 결과에서도 내부 로그용 값으로 살아남는지 확인하는 회귀 테스트를 추가했다.
  - 이 테스트는 `memory_text`, `filenames`, `task_title`, `reminder_text`, `url_titles` 같은 도메인별 대상 텍스트가 artifact title 후보로 보존되는지도 함께 확인한다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`32 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py -q`(`441 passed`), `python3 -m pytest -q`(`933 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 에이전트 카탈로그 facts 슬롯 계약 보강

- 작업 이름: `facts` 기반 turn state 슬롯 추론과 카탈로그 선언 일치 검증
- 진행상황: 완료
- 진행내용:
  - 일부 에이전트는 실행 결과의 대상 ID, URL, 쿼리, 지역 등을 `slots`가 아니라 `facts`에 담고, `infer_turn_slots()`와 내부 행동 로그가 이를 후속 맥락 단서로 사용할 수 있음을 확인했다.
  - 현재 코드에서 리터럴 `OperationResult(facts={...})` 중 turn state 슬롯으로 승격 가능한 키가 카탈로그에 누락된 사례는 없음을 확인했다.
  - 이 상태를 유지하기 위해 `infer_turn_slots()`가 보존하는 fact 키를 샘플로 계산하고, 해당 키가 리터럴 `facts`에 들어간 경우 각 intent의 `state_outputs`에 `slots.<key>`로 선언되어 있는지 검사하는 회귀 테스트를 추가했다.
  - 이 테스트는 통계성 fact(`deleted_count`, `answer` 등)는 과하게 요구하지 않고, 실제 후속 맥락 연결에 쓰이는 `memory_ids`, `document_ids`, `task_ids`, `reminder_ids`, `location`, `query`, `url` 계열 키만 대상으로 삼는다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`33 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_response_composer.py -q`(`464 passed`), `python3 -m pytest -q`(`934 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 에이전트 카탈로그 target_hints 노출 계약 보강

- 작업 이름: 카탈로그 슬롯이 라우터 대상 힌트에 실제로 보이는지 검증
- 진행상황: 완료
- 진행내용:
  - 새 에이전트가 `state_outputs`에 대상 슬롯을 선언하더라도, 그 슬롯이 `turn_state_target_hints()`를 통해 라우터 컨텍스트의 사람이 읽을 수 있는 대상 단서로 노출되지 않으면 LLM이 이전 맥락과 새 요청을 구분하기 어렵다는 위험을 확인했다.
  - `test_agent_catalog_target_slot_outputs_are_visible_in_turn_state_hints`를 추가해 카탈로그가 선언한 대상 슬롯마다 샘플 turn state를 만들고, `메모 11`, `문서 21`, `contract.pdf`, `OpenAI Blog`, `오늘 저녁 메뉴 고민` 같은 실제 target hint가 생성되는지 검증하도록 했다.
  - 이 계약은 새 에이전트나 새 슬롯이 추가될 때 단순히 코드 어딘가에 키가 존재하는 수준이 아니라, 라우터가 볼 수 있는 맥락 힌트까지 이어지는지를 확인한다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`34 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_route_validation.py tests/test_router_agent.py tests/test_response_composer.py -q`(`356 passed`), `python3 -m pytest -q`(`935 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 라우터 fallback 내부 로그 오염 방지 회귀 테스트

- 작업 이름: 내부 행동 로그의 이전 파일명이 새 명시 파일 요청을 가로채지 않도록 고정
- 진행상황: 완료
- 진행내용:
  - LLM 라우터 실패나 JSON 파싱 실패 시 `context_aware_fallback_route()`가 내부 행동 로그를 참고해 후보 슬롯과 target hint를 보강하는 구조를 재확인했다.
  - 기존 테스트는 내부 로그의 `contract.pdf` 같은 파일명이 현재 요청과 일치할 때 후속 문서 분석으로 연결되는 경로를 검증했지만, 사용자가 `invoice.pdf`처럼 새 파일명을 명시했을 때 이전 내부 로그가 잘못 연결되지 않는지 명시적으로 고정하지는 않았다.
  - `test_router_fallback_does_not_link_different_file_name_from_internal_action_log`를 추가해 내부 로그가 `contract.pdf`를 보강하더라도 현재 메시지가 `invoice.pdf 다시 요약해줘`라면 `context_link=none`으로 남고 `linked_state_id`를 선택하지 않도록 검증했다.
  - 이 회귀 테스트는 내부 행동 기록을 맥락 참고로 쓰되, 현재 사용자 메시지의 명시 대상이 우선한다는 목표를 fallback 경로까지 고정한다.
  - `python3 -m pytest tests/test_router_agent.py -q`(`103 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_route_validation.py tests/test_agent_registry.py -q`(`335 passed`), `python3 -m pytest -q`(`936 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 웹 fallback 새 URL/검색어 오염 방지

- 작업 이름: 내부 행동 로그의 이전 URL/검색어가 새 명시 웹 요청을 가로채지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - `context_aware_fallback_route()`에서 사용자가 `https://new.example.com/article 다시 요약해줘`처럼 새 URL을 명시했는데, 내부 행동 로그에 남아 있던 이전 웹 후보 `https://old.example.com/article`로 잘못 연결될 수 있음을 재현했다.
  - 새 검색어 `Python asyncio 다시 검색해줘`는 기존 검색 후보와 연결되지 않았지만, 같은 계열의 위험을 함께 고정할 필요가 있다고 판단했다.
  - `candidate_match_may_override_base_route()`에 `explicit_web_target_mismatches_candidate()` 방어선을 추가해, 현재 메시지에 명시 URL 또는 명시 검색어가 있고 후보의 웹 대상과 다르면 fallback 후보 연결을 허용하지 않도록 했다.
  - 후보 웹 대상 비교는 후보 `slots`, `artifacts`, `target_hints`, `subject`를 정규화해 수행하며, 같은 검색어인 `OpenAI 모델 다시 검색해줘`는 기존 후보와 계속 연결되도록 유지했다.
  - `test_router_fallback_does_not_link_different_url_from_internal_action_log`, `test_router_fallback_does_not_link_different_search_query_from_internal_action_log`, `test_router_fallback_keeps_same_search_query_from_internal_action_log`를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py -q`(`106 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_context_builder.py -q`(`441 passed`), `python3 -m pytest -q`(`939 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 날씨 fallback 지역 경계 회귀 테스트

- 작업 이름: 내부 행동 로그의 이전 날씨 지역과 새 명시 지역 구분 고정
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그가 `원주` 날씨 후보를 보강하고 있을 때, 현재 메시지가 `서울 날씨 다시 확인해줘`처럼 새 지역을 명시하면 이전 후보에 연결되지 않는지 재현했다.
  - 현재 구현은 `서울` 새 지역 요청은 `context_link=none`으로 처리하고, `원주 날씨 다시 확인해줘` 또는 `거기 미세먼지도 봐줘`처럼 이전 지역을 명확히 이어받는 요청은 `context_link=retry`, `resolved_slots.location=원주`로 연결함을 확인했다.
  - 이 균형을 유지하기 위해 `test_router_fallback_does_not_link_different_weather_location_from_internal_action_log`, `test_router_fallback_keeps_same_weather_location_from_internal_action_log`, `test_router_fallback_keeps_weather_pronoun_from_internal_action_log`를 추가했다.
  - 이 회귀 테스트는 “새 지역은 새 요청, 대명사/같은 지역은 후속 요청”이라는 날씨 에이전트 맥락 판단 기준을 fallback 경로까지 고정한다.
  - `python3 -m pytest tests/test_router_agent.py -q`(`109 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_context_builder.py -q`(`444 passed`), `python3 -m pytest -q`(`942 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 이름 기반 대상 fallback 오염 방지

- 작업 이름: 새 할 일/알림/메모 이름이 이전 후보와 다를 때 자동 연결 차단
- 진행상황: 완료
- 진행내용:
  - `context_aware_fallback_route()`에서 이전 후보가 `병원 예약` 할 일인데 사용자가 `장보기 완료했어`라고 말하면 `task_id=3`으로 잘못 연결되는 문제를 재현했다.
  - 이전 후보가 `물 마시기` 알림인데 사용자가 `커피 마시기 알림 삭제해줘`라고 말해도 기존 알림으로 연결되는 문제를 함께 확인했다.
  - `candidate_match_may_override_base_route()`에 `explicit_named_target_mismatches_candidate()` 방어선을 추가했다.
  - 현재 메시지에서 추출한 명시 이름 대상이 있고, 후보 종류가 메모/할 일/알림이며 후보의 `target_hints`, `memory_text`, `task_title`, `reminder_text`, artifact 제목/본문, subject/summary와 맞지 않으면 fallback 연결을 차단한다.
  - `장보기 완료했어`, `커피 마시기 알림 삭제해줘`, `운동 루틴 메모 보여줘`는 이전 후보에 붙지 않고, `병원 예약 완료했어`, `물 마시기 알림 삭제해줘`, `점심 메뉴 메모 보여줘`는 기존 후보에 연결되는 회귀 테스트를 추가했다.
  - `python3 -m pytest tests/test_router_agent.py -q`(`115 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_context_builder.py -q`(`450 passed`), `python3 -m pytest -q`(`948 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 모델 라우트 검증 계층 이름 대상 계약 보강

- 작업 이름: OpenAI 라우터가 잘못 연결한 알림 이름 대상도 실행 전 검증에서 차단
- 진행상황: 완료
- 진행내용:
  - fallback 라우터뿐 아니라 모델 라우터가 직접 `linked_state_id`와 `resolved_slots`를 잘못 반환한 경우도 실행 전 `validate_route_context_link()`가 막아야 한다는 점을 재확인했다.
  - `장보기 완료했어`, `커피 마시기 알림 삭제해줘` 같은 재현 케이스를 검증 계층에 직접 넣어보니 기존 코드가 이미 named target 불일치를 제거하고 있음을 확인했다.
  - 이 계약을 더 선명하게 고정하기 위해 subject가 일반적인 `알림 조회 결과`이고 실제 대상명이 `slots.reminder_text`에만 있는 경우를 추가했다.
  - `물 마시기 알림 삭제해줘`는 `reminder_text=물 마시기` 후보에 연결되고, `커피 마시기 알림 삭제해줘`는 같은 후보에 연결되지 않는 회귀 테스트를 추가했다.
  - 이 테스트는 내부 행동 로그나 turn state 보강으로 대상명이 슬롯에만 남은 경우에도 모델 라우트 검증 계층이 현재 사용자 메시지의 명시 이름을 우선하도록 고정한다.
  - `python3 -m pytest tests/test_route_validation.py -q`(`151 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_context_builder.py -q`(`452 passed`), `python3 -m pytest -q`(`950 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 이름 대상 방어선의 후속 요청 유지 계약 보강

- 작업 이름: 이름 불일치 차단이 대명사/ID 기반 진짜 후속 요청을 막지 않도록 고정
- 진행상황: 완료
- 진행내용:
  - 이름 기반 대상 불일치 방어선이 추가된 뒤에도 `그거 완료했어`, `할 일 3 완료했어`, `그 알림 삭제해줘`, `알림 5 삭제해줘`, `그 메모 보여줘`, `메모 8 보여줘` 같은 진짜 후속 요청은 계속 연결되어야 함을 확인했다.
  - `context_aware_fallback_route()`에 직접 재현해본 결과 대명사/ID 기반 요청은 각각 기존 task/reminder/memory 후보에 정상 연결되고 실행 슬롯도 유지됨을 확인했다.
  - 이 균형을 회귀 테스트로 고정하기 위해 `test_router_fallback_keeps_pronoun_and_id_references_after_named_target_guard`를 추가했다.
  - 이 테스트는 “이름이 다른 새 대상은 차단하되, 대명사나 명시 ID로 이전 대상을 가리키는 요청은 차단하지 않는다”는 맥락 판단의 양방향 균형을 보장한다.
  - `python3 -m pytest tests/test_router_agent.py -q`(`116 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_context_builder.py -q`(`453 passed`), `python3 -m pytest -q`(`951 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 승인 문장 새 대상 혼합 방지

- 작업 이름: `응`과 새 요청이 섞인 문장을 이전 확인 승인으로 소비하지 않도록 고정
- 진행상황: 완료
- 진행내용:
  - 사용자가 확인 질문에 `응`만 답하면 pending context 승인으로 처리해야 하지만, `응 장보기 완료했어`처럼 새 요청이 붙은 문장은 이전 확인을 승인하는 답변으로 소비하면 안 된다는 경계를 점검했다.
  - 현재 `matching_pending_context_approval_state()`는 `응 장보기 완료했어`, `응 사이트 열어줘`, `응 문서 9 다시 분석해줘` 같은 혼합 문장을 승인으로 보지 않음을 재현했다.
  - 기존 테스트가 유틸리티/일반 액션 혼합은 다루고 있었지만, 이름 기반 새 대상 혼합을 직접 고정하지는 않아 `test_pending_context_approval_rejects_positive_text_with_named_new_target`를 추가했다.
  - 새 테스트는 `응 장보기 완료했어`, `응 커피 마시기 알림 삭제해줘`, `응 운동 루틴 메모 보여줘`가 기존 pending task 승인을 통과하지 못하도록 검증한다.
  - 이 회귀 테스트는 확인 질문 답변과 새 요청이 한 문장에 섞였을 때 현재 사용자 메시지의 새 대상을 우선한다는 원칙을 pending 승인 경로까지 고정한다.
  - `python3 -m pytest tests/test_route_validation.py -q`(`152 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_context_builder.py -q`(`454 passed`), `python3 -m pytest -q`(`952 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 모델 라우트 검증 이력 컨텍스트 연결 보강

- 작업 이름: 모델이 잘못 연결한 이름 대상 링크를 제거하고 다음 라우터 컨텍스트에 남기는 통합 계약 고정
- 진행상황: 완료
- 진행내용:
  - fallback 경로뿐 아니라 OpenAI 라우터가 직접 이전 `병원 예약` 상태를 `linked_state_id`로 반환한 뒤 사용자가 `장보기 삭제해줘`처럼 새 이름 대상을 명시하는 경우를 봇 핸들러 단위로 점검했다.
  - `test_assistant_bot_clears_model_link_for_different_named_task_target`를 추가해 실행 전 `validate_route_context_link()`가 잘못된 `context_link=continue`, `linked_state_id`, `resolved_slots`를 제거하고 에이전트 dispatch에는 연결 없는 새 요청으로 넘기는지 검증했다.
  - 같은 테스트에서 `route_validation` 내부 로그에 `named target` 불일치와 `validation_context`가 남고, `build_router_context()`가 이를 `validation_guidance=최근 검증에서 state_id ... 자동 연결이 제거됨` 형태로 다시 제공하는지 확인했다.
  - 이 회귀 테스트는 사용자에게 보이지 않는 내부 검증 행동이 다음 라우터 판단에 참고 가능한 형태로 남되, 현재 메시지의 명시 대상이 이전 내부 기록보다 우선한다는 핵심 원칙을 통합 흐름에서 고정한다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_clears_model_link_for_different_named_task_target -q`(`1 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`564 passed`), `python3 -m pytest -q`(`953 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 버튼 후보 선택 결과 내부 컨텍스트 보강

- 작업 이름: 버튼으로 선택한 후속 작업 결과도 다음 라우터가 참고할 수 있도록 회귀 검증
- 진행상황: 완료
- 진행내용:
  - 사용자가 텍스트가 아니라 버튼으로 후속 작업 후보를 선택한 경우에도, 그 선택과 실행 결과가 다음 대화 맥락에 남아야 한다는 점을 점검했다.
  - `test_state_candidate_button_selection_routes_and_dispatches_selected_state`를 보강해 후보 선택 버튼이 `web_search` 후속 작업을 실행한 뒤 `task:result` 내부 결과 로그에 `route`, `linked_state_id`, `resolved_slots.query`를 보존하는지 확인했다.
  - 같은 테스트에서 `build_router_context()`가 버튼 실행 결과 로그를 `agent=task:result`, `route_context={'context_link': 'retry', ...}`, `OpenAI 최신 뉴스` target hint가 포함된 형태로 다시 제공하는지 검증했다.
  - 이 회귀 테스트는 사용자에게 보이지 않는 버튼 상호작용도 일반 채팅 메시지와 동일하게 내부 행동 기록으로 남고, 다음 라우터 판단에서 후속 요청의 근거로 사용할 수 있음을 고정한다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_state_candidate_button_selection_routes_and_dispatches_selected_state -q`(`1 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`564 passed`), `python3 -m pytest -q`(`953 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 카탈로그 facts 슬롯 맥락 보존 보강

- 작업 이름: 새 에이전트가 `facts`만 반환해도 카탈로그 슬롯이 내부 맥락에 남도록 확장
- 진행상황: 완료
- 진행내용:
  - 에이전트 카탈로그에는 `due_at`, `human_due_at`, `reminder_text`, `remind_at`, `current_time`, `briefing_date` 같은 슬롯이 선언되어 있지만, `infer_turn_slots()`가 일부 ID/웹 슬롯만 `facts`에서 자동 추론하고 있음을 확인했다.
  - `infer_turn_slots()`가 시간, 알림 본문, 메모 본문, 첨부명, 현재 시간, 브리핑 날짜, 취소 대상, unsupported 이유 등 카탈로그에 선언된 주요 슬롯을 `facts`에서 보존하도록 확장했다.
  - `internal_action_target_hints()`가 `due_at`, `human_due_at`, `remind_at`, `human_remind_at`, `current_time`, `briefing_date`, `pending_query`, `new_text`도 라우터 target hint로 사용할 수 있도록 보강했다.
  - `test_agent_catalog_declares_literal_operation_result_fact_slots`의 샘플을 확장해 앞으로 새 에이전트가 literal `OperationResult.facts`에 카탈로그 슬롯을 반환하면 `agent_catalog.json` 선언 누락을 잡도록 했다.
  - `test_infer_turn_slots_keeps_catalog_fact_slots_for_context_linking`, `test_record_internal_action_result_preserves_catalog_fact_slots_for_future_context`를 추가해 `facts`만으로 반환된 시간/알림 슬롯이 내부 로그와 다음 라우터 컨텍스트에 보존되는지 검증했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`34 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_agent_registry.py -q`(`600 passed`), `python3 -m pytest -q`(`955 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - facts 슬롯 추론 공통 계약 단일화

- 작업 이름: `infer_turn_slots()`가 내부 컨텍스트 키 집합을 직접 사용하도록 정리
- 진행상황: 완료
- 진행내용:
  - 직전 보강 후에도 `infer_turn_slots()`가 별도 하드코딩 튜플을 유지하고 있어, 앞으로 `INTERNAL_ACTION_CONTEXT_KEYS`에 새 슬롯을 추가해도 `facts` 추론 경로에는 빠질 수 있음을 확인했다.
  - `infer_turn_slots()`를 `TURN_STATE_ID_SLOT_KEYS | INTERNAL_ACTION_CONTEXT_KEYS` 기반으로 변경해, turn state ID 슬롯과 내부 행동 컨텍스트 슬롯이 `facts`에서 자동 보존되는 단일 계약을 사용하도록 했다.
  - `test_infer_turn_slots_uses_common_internal_context_key_contract`를 추가해 공통 키 집합 전체가 `facts`에서 slots로 이동하는지 검증했다.
  - 이 변경은 새 에이전트가 카탈로그와 내부 컨텍스트 키 계약에 맞는 값을 `OperationResult.facts`로 반환하기만 해도 다음 라우터 판단 단서가 누락되지 않도록 하는 안전장치다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_infer_turn_slots_uses_common_internal_context_key_contract tests/test_bot_helpers.py::test_infer_turn_slots_keeps_catalog_fact_slots_for_context_linking tests/test_bot_helpers.py::test_record_internal_action_result_preserves_catalog_fact_slots_for_future_context -q`(`3 passed`), `python3 -m pytest tests/test_agent_registry.py -q`(`34 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_agent_registry.py -q`(`601 passed`), `python3 -m pytest -q`(`956 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - turn state 슬롯 병합 보강

- 작업 이름: 에이전트가 일부 `slots`만 반환해도 `facts` 기반 맥락 단서를 잃지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 봇과 CLI의 turn state 저장 경로가 `result.slots or infer_turn_slots(result)`를 사용하고 있어, 에이전트가 `slots`를 하나라도 직접 반환하면 `facts`에서 추론 가능한 `due_at`, `human_due_at`, `task_id` 같은 보조 단서가 버려질 수 있음을 확인했다.
  - `turn_state_slots_from_result()`를 추가해 `infer_turn_slots(result)`를 먼저 채우고 `result.slots`를 덮어쓰는 방식으로 병합하도록 했다.
  - `AssistantBot.record_turn_state()`, CLI 로컬 상호작용 저장 경로, `should_record_turn_state()`가 모두 이 병합 helper를 사용하도록 바꿨다.
  - `test_turn_state_slots_from_result_merges_inferred_facts_and_explicit_slots`, `test_should_record_turn_state_uses_fact_ids_even_when_slots_are_partial`, `test_assistant_bot_record_turn_state_merges_fact_slots_with_explicit_slots`를 추가했다.
  - 이 변경은 새 에이전트가 직접 slots를 일부만 채워도, facts 기반 ID/시간/대상 단서가 turn state와 다음 라우터 후보에서 누락되지 않도록 한다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_turn_state_slots_from_result_merges_inferred_facts_and_explicit_slots tests/test_bot_helpers.py::test_should_record_turn_state_uses_fact_ids_even_when_slots_are_partial tests/test_bot_helpers.py::test_assistant_bot_record_turn_state_merges_fact_slots_with_explicit_slots -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_agent_registry.py -q`(`228 passed`), `python3 -m pytest -q`(`959 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - turn state artifact 병합 보강

- 작업 이름: 에이전트가 일부 `artifacts`만 반환해도 `items` 기반 대상 단서를 잃지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 봇과 CLI의 turn state 저장 경로, 내부 행동 결과 로그 경로가 `result.artifacts or infer_turn_artifacts(result)`를 사용하고 있어, 에이전트가 artifact를 하나라도 직접 반환하면 `items`에서 추론 가능한 문서/할 일/알림 artifact가 버려질 수 있음을 확인했다.
  - `turn_state_artifacts_from_result()`를 추가해 직접 반환한 artifact와 `items`에서 추론한 artifact를 병합하도록 했다.
  - 같은 대상 ID/URL/제목을 가진 artifact는 중복 저장하지 않고, 직접 artifact 값을 우선하면서 추론 artifact의 빠진 제목, 파일명, 기한 같은 필드를 보충한다.
  - `AssistantBot.record_turn_state()`, CLI 로컬 상호작용 저장 경로, `safe_internal_action_artifact_values()`가 모두 병합 helper를 사용하도록 바꿨다.
  - `test_turn_state_artifacts_from_result_merges_explicit_and_inferred_artifacts`, `test_record_internal_action_result_merges_explicit_and_inferred_artifacts_for_context`, `test_assistant_bot_record_turn_state_merges_explicit_and_inferred_artifacts`를 추가했다.
  - 이 변경은 새 에이전트가 일부 artifact만 직접 채워도, items 기반 문서/할 일/알림/URL 단서가 turn state와 내부 행동 로그, 다음 라우터 컨텍스트에서 누락되지 않도록 한다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_turn_state_artifacts_from_result_merges_explicit_and_inferred_artifacts tests/test_bot_helpers.py::test_record_internal_action_result_merges_explicit_and_inferred_artifacts_for_context tests/test_bot_helpers.py::test_assistant_bot_record_turn_state_merges_explicit_and_inferred_artifacts -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_agent_registry.py tests/test_context_builder.py -q`(`280 passed`), `python3 -m pytest -q`(`962 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - turn state available_actions 병합 보강

- 작업 이름: 에이전트가 일부 `available_actions`만 반환해도 카탈로그 기반 후속 행동을 잃지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 봇과 CLI의 turn state 저장 경로가 에이전트가 직접 반환한 `available_actions`만 저장하면, 카탈로그와 intent로 추론 가능한 `postpone`, `rename`, `compare`, `open_url` 같은 후속 행동 후보가 내부 맥락에서 빠질 수 있음을 확인했다.
  - `turn_state_available_actions_from_result()`를 추가해 직접 반환한 액션과 `infer_available_actions(result)`를 순서 보존 방식으로 병합하도록 했다.
  - `AssistantBot.record_turn_state()`, CLI 로컬 상호작용 저장 경로, `should_record_turn_state()`, `internal_action_result_reason()`가 모두 병합 helper를 사용하도록 바꿨다.
  - 내부 행동 로그의 `actions=` 값도 병합된 액션을 기록하므로, 다음 라우터가 이전 결과에 대해 사용자가 할 수 있는 후속 행동을 더 넓고 일관되게 참고할 수 있다.
  - `test_turn_state_available_actions_from_result_merges_explicit_and_inferred_actions`, `test_should_record_turn_state_uses_inferred_actions_when_explicit_actions_are_empty`, `test_assistant_bot_record_turn_state_merges_explicit_and_inferred_actions`를 추가했다.
  - 라우터 내부 행동 파싱 테스트도 병합된 actions를 기대하도록 갱신해, 내부 로그 문자열에서 추출된 후속 행동 후보가 다음 라우팅 판단에 유지되는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_turn_state_available_actions_from_result_merges_explicit_and_inferred_actions tests/test_bot_helpers.py::test_should_record_turn_state_uses_inferred_actions_when_explicit_actions_are_empty tests/test_bot_helpers.py::test_record_internal_action_result_logs_operation_result_for_future_context tests/test_bot_helpers.py::test_assistant_bot_record_turn_state_merges_explicit_and_inferred_actions -q`(`4 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_agent_registry.py tests/test_context_builder.py -q`(`283 passed`), `python3 -m pytest -q`(`965 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 현재 메시지 맥락 진단 컨텍스트 보강

- 작업 이름: 라우터가 현재 사용자 문장의 후속/새 요청 신호를 구조화해서 참고하도록 수정
- 진행상황: 완료
- 진행내용:
  - 기존 컨텍스트에는 “현재 메시지를 우선한다”는 정책 문장이 있었지만, 현재 문장 자체가 후속 요청인지 새 요청인지에 대한 공통 진단 결과는 라우터 입력에 구조화되어 있지 않았다.
  - `build_current_message_context()`를 추가해 `follow_up_reference`, `explicit_new_target`, `new_request_marker`, `unrelated_general_request`, `unrelated_utility_request`, 확인 승인/거부 가능성, `replacement_target` 신호를 한 줄로 요약하도록 했다.
  - `build_context_decision_context()`가 현재 메시지 진단을 포함하도록 확장하고, `build_router_context()`가 `user_text`를 받을 수 있게 변경했다.
  - Discord 봇과 CLI의 라우터 호출 경로가 현재 사용자 문장을 `build_router_context()`에 전달하도록 연결했다.
  - `말고/대신`처럼 이전 대상을 배제하고 새 대상을 말하는 문장은 `아까` 같은 후속 표현이 포함되어도 `likely_new_request_do_not_link_previous_state`로 진단되도록 했다.
  - `test_build_current_message_context_marks_clear_follow_up_reference`, `test_build_router_context_includes_current_message_new_target_diagnostics`를 추가해 `다시해봐`와 `아까 말고 서울 날씨 알려줘`의 맥락 진단을 고정했다.
  - `python3 -m pytest tests/test_context_builder.py -q`(`53 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_route_validation.py tests/test_bot_helpers.py -q`(`578 passed`), `python3 -m pytest -q`(`967 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation 현재 메시지 진단 로그 보강

- 작업 이름: 실행 전 라우트 보정 로그에 현재 메시지 맥락 진단을 함께 저장
- 진행상황: 완료
- 진행내용:
  - 라우터 입력에는 `현재 메시지 맥락 진단`이 포함되지만, 실행 전 검증이 라우트를 제거하거나 확인으로 바꾼 경우 내부 로그에는 어떤 현재 메시지 신호가 보정 근거였는지 구조화되어 남지 않는 빈틈을 확인했다.
  - `route_validation_summary()`가 선택적으로 `user_text`를 받아 `current_message_context=...`를 `validation_context` 앞에 기록하도록 확장했다.
  - Discord 봇과 CLI의 `log_route_validation_if_changed()` 경로가 검증에 사용한 문장을 함께 넘기도록 연결했다.
  - 기존 `validation_context` 파싱이 깨지지 않도록 `current_message_context`는 별도 필드로 앞쪽에 추가하고, `validation_context`는 기존 literal dict 형식을 유지했다.
  - `test_log_route_validation_if_changed_records_adjustment`를 보강해 `아까 말고 서울 날씨 알려줘`가 `effective_text=서울날씨알려줘`, `decision_hint=likely_new_request_do_not_link_previous_state`로 로그에 남고, 기존 `validation_context`도 파싱 가능한지 검증했다.
  - `python3 -m pytest tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment tests/test_cli.py::test_log_route_validation_if_changed_compacts_long_adjustment tests/test_cli.py::test_log_route_validation_if_changed_preserves_parseable_context_with_many_slots tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router -q`(`4 passed`), `python3 -m pytest tests/test_cli.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_bot_helpers.py -q`(`519 passed`), `python3 -m pytest -q`(`967 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - fallback 라우터 현재 메시지 진단 활용 보강

- 작업 이름: 모델 프롬프트용 맥락 진단을 deterministic fallback 판단에도 연결
- 진행상황: 완료
- 진행내용:
  - `현재 메시지 맥락 진단`은 라우터 프롬프트와 route validation 로그에는 남지만, `context_aware_fallback_route()`가 `decision_hint`를 직접 읽지는 않아 fallback 경로에서는 같은 새 요청 우선 신호를 충분히 활용하지 못할 수 있음을 확인했다.
  - `current_message_decision_hint()`를 추가해 라우터 컨텍스트의 `현재 메시지 맥락 진단` 섹션에서 `decision_hint`를 파싱하도록 했다.
  - fallback 라우터가 `decision_hint=likely_new_request_do_not_link_previous_state`이고 현재 메시지와 명시적으로 일치하는 후보가 없으면, 후보 연결이나 대상 없는 확인 질문으로 넘어가지 않고 base route를 새 요청으로 유지하도록 했다.
  - base route가 이미 `clarify` 또는 linked state/resolved slots를 갖고 있으면 `context_link=none`, `linked_state_id=None`, 빈 slots로 정리해 “이전 작업을 이어갈까요?” 같은 불필요한 확인 질문을 줄이도록 했다.
  - `test_current_message_decision_hint_parses_router_context_diagnostic`, `test_router_fallback_uses_current_message_new_request_diagnostic_to_skip_candidate_link`를 추가해 `아까 말고 서울 날씨 알려줘`가 최근 task 후보를 물고 들어가지 않는지 검증했다.
  - `python3 -m pytest tests/test_router_agent.py::test_current_message_decision_hint_parses_router_context_diagnostic tests/test_router_agent.py::test_router_fallback_uses_current_message_new_request_diagnostic_to_skip_candidate_link tests/test_router_agent.py::test_router_fallback_links_weather_air_quality_follow_up -q`(`3 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_context_builder.py tests/test_bot_helpers.py -q`(`580 passed`), `python3 -m pytest -q`(`969 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 에이전트 구조화 결과 반환 계약 보강

- 작업 이름: 후속 맥락 단서를 선언한 에이전트가 문자열 반환으로 맥락을 잃지 않도록 registry 계약 강화
- 진행상황: 완료
- 진행내용:
  - `agent_catalog.json`의 `state_outputs`는 후속 턴에 남길 slots, artifacts, available_actions를 선언하지만, handler가 문자열만 반환하면 `AgentRegistry.dispatch()`가 legacy `OperationResult`로 감싸면서 선언된 단서가 실제 turn state와 내부 행동 로그에 남지 않는 빈틈을 확인했다.
  - `definition_requires_structured_result()`를 추가해 `subject` 외 `slots.*`, `artifacts.*`, `available_actions.*`, `retryable` 같은 후속 맥락 단서를 선언한 에이전트는 반드시 `OperationResult`를 반환하도록 했다.
  - 이 계약을 위반하면 dispatch 단계에서 `ValueError`를 발생시켜, 새 에이전트를 추가할 때 카탈로그에는 맥락 단서를 적었지만 실제 결과에는 단서를 누락하는 실수를 조기에 잡도록 했다.
  - `subject`만 선언한 legacy handler는 기존처럼 문자열 반환을 허용해 단순 fallback 테스트와 호환성을 유지했다.
  - `plan.md`의 에이전트 구조 섹션에 같은 규칙을 문서화했다.
  - `test_registry_dispatch_rejects_string_result_when_context_outputs_are_declared`를 추가해 `slots.task_id`, `available_actions.show`를 선언한 handler가 문자열만 반환하면 실패하는지 검증했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`35 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_bot_helpers.py tests/test_cli.py tests/test_context_builder.py -q`(`286 passed`), `python3 -m pytest -q`(`970 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - registry 결과 intent 정합성 계약 보강

- 작업 이름: 에이전트가 등록되지 않은 intent 결과를 남기지 못하도록 dispatch 검증 추가
- 진행상황: 완료
- 진행내용:
  - 새 에이전트가 `OperationResult`를 반환하더라도 `intent` 오타나 카탈로그에 없는 intent를 넣으면, 라우터/검증 계층이 모르는 작업 상태가 turn state와 내부 행동 로그에 남을 수 있음을 확인했다.
  - `AgentRegistry.dispatch()`가 `OperationResult.intent`를 registry 등록 intent 집합과 대조하도록 했다.
  - 결과 intent가 등록되어 있지 않으면 `ValueError`로 실패시켜, 카탈로그/라우터/검증 계층과 실행 결과의 intent 어휘가 어긋나는 문제를 개발 단계에서 잡는다.
  - 날씨 에이전트가 대기질 요청을 등록된 `web_search` intent로 위임하는 것처럼, 등록된 다른 intent로 위임하는 경로는 허용한다.
  - `plan.md`에 결과 intent는 registry에 등록된 intent 중 하나여야 한다는 계약을 문서화했다.
  - `test_registry_dispatch_rejects_unregistered_result_intent`, `test_registry_dispatch_allows_registered_result_intent_delegation`을 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`37 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_bot_helpers.py tests/test_cli.py tests/test_memory_store.py tests/test_weather_agent.py -q`(`364 passed`), `python3 -m pytest -q`(`972 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답 컨텍스트 현재 메시지 진단 숨김 보강

- 작업 이름: 최종 응답 작성 모델에 내부 라우팅 진단 신호가 노출되지 않도록 정리
- 진행상황: 완료
- 진행내용:
  - `ExecutionContext.for_response()`가 `맥락 판별 정책`을 그대로 응답 작성 모델에 전달하면서, 라우터용 `현재 메시지 맥락 진단`과 `decision_hint`가 최종 응답 입력에 포함될 수 있음을 확인했다.
  - `response_safe_context_decision_context()`를 추가해 응답용 컨텍스트에서는 `현재 메시지 맥락 진단` 섹션을 제거하고, 사용자에게 보여도 안전한 맥락 판별 정책만 남기도록 했다.
  - 라우터, fallback, route validation 로그는 계속 현재 메시지 진단을 사용하지만, 최종 응답 작성자는 `decision_hint`, `effective_text`, `follow_up_reference` 같은 내부 판단 토큰을 보지 않도록 경계를 분리했다.
  - `test_execution_context_response_hides_current_message_diagnostics_from_decision_context`, `test_response_composer_hides_current_message_diagnostics_from_model_input`를 추가했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_hides_current_message_diagnostics_from_decision_context tests/test_response_composer.py::test_response_composer_hides_current_message_diagnostics_from_model_input -q`(`2 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_bot_helpers.py -q`(`197 passed`), `python3 -m pytest -q`(`974 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 에이전트 내부 모델 입력 현재 메시지 진단 숨김 보강

- 작업 이름: 대화/문서/웹검색 에이전트 OpenAI 입력에도 라우팅 진단 토큰이 노출되지 않도록 정리
- 진행상황: 완료
- 진행내용:
  - `ConversationAgent`, `DocumentAnalysisAgent`, `WebSearchAgent`가 `execution_context.for_agent()`를 OpenAI 입력에 사용하고 있어, 라우터용 `현재 메시지 맥락 진단`과 `decision_hint`가 에이전트 내부 생성 결과에 섞일 수 있음을 확인했다.
  - `ExecutionContext.for_agent()`도 `response_safe_context_decision_context()`를 사용하도록 변경해, 에이전트 내부 모델에는 안전한 맥락 판별 정책만 전달하고 현재 메시지 진단 섹션은 제거하도록 했다.
  - `ExecutionContext.for_router()`는 기존처럼 현재 메시지 진단을 유지해 라우터와 deterministic fallback은 계속 해당 신호를 사용할 수 있게 했다.
  - `test_execution_context_agent_context_hides_current_message_diagnostics_but_router_keeps_them`를 추가해 라우터 컨텍스트와 에이전트 컨텍스트의 경계를 고정했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_agent_context_hides_current_message_diagnostics_but_router_keeps_them tests/test_response_composer.py::test_response_composer_hides_current_message_diagnostics_from_model_input -q`(`2 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_document_analysis_agent.py tests/test_web_search_agent.py tests/test_memory_store.py::test_conversation_agent_uses_agent_execution_context_for_linked_state -q`(`65 passed`), `python3 -m pytest -q`(`975 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 로그 실행 결과 보존 보강

- 작업 이름: route validation 로그가 많아도 실제 실행 결과 단서가 라우터 컨텍스트에 남도록 개선
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그 선택 로직이 현재 위치 `route_validation` 로그를 최우선으로 두고 있어, 검증 로그가 많이 쌓이면 `task:result` 같은 실제 실행 결과가 `INTERNAL_ACTION_CONTEXT_LIMIT` 밖으로 밀릴 수 있음을 확인했다.
  - `select_internal_action_rows()`를 추가해 최신 현재 위치 검증 로그와 최신 현재 위치 실행 결과를 각각 최소 1개씩 보존하도록 했다.
  - 현재 위치의 `*:result` 실행 결과 우선순위를 검증 로그보다 높여, 문자 제한이 걸려도 실제 대상, route context, executable actions가 먼저 남도록 했다.
  - 구조화된 내부 로그는 `reason` 원문 전체 대신 `status`, `summary`, `subject`, 검증 사유를 압축해서 표시하고, `route_context`, `validation_context`, `executable_actions`, `target_hints` 같은 파싱 가능한 필드를 보존하도록 했다.
  - 기본 `INTERNAL_ACTION_CONTEXT_MAX_CHARS`를 `1200`에서 `2400`으로 올리고 `.env.example`도 같은 값으로 맞춰, 교차 위치 확인 상태에서 실행 결과와 route validation 로그가 함께 들어갈 수 있게 했다.
  - `test_build_router_context_keeps_current_execution_result_when_validation_logs_fill_limit`를 추가해 검증 로그가 한도를 채워도 `할 일 12 수정 완료`, `linked_state_id`, 실행 가능 액션, target hint가 남는지 검증했다.
  - `python3 -m pytest tests/test_context_builder.py -q`(`52 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_bot_helpers.py -q`(`240 passed`), `python3 -m pytest tests/test_cli.py::test_local_ask_standardizes_cross_location_clarify_and_logs_validation -q`(`1 passed`), `python3 -m pytest -q`(`976 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - OperationResult 런타임 카탈로그 계약 보강

- 작업 이름: 실제 에이전트 반환 슬롯과 액션이 agent_catalog 선언 밖으로 벗어나지 않도록 dispatch 검증 추가
- 진행상황: 완료
- 진행내용:
  - 기존 테스트는 주로 literal `OperationResult`와 카탈로그 정합성을 확인했지만, 동적으로 만들어지는 `slots`나 `available_actions`는 선언 밖으로 새어 나갈 수 있음을 확인했다.
  - `AgentRegistry.dispatch()`가 `OperationResult.intent` 확인 후, 해당 intent의 `agent_catalog.json state_outputs`와 실제 `result.slots`, `result.available_actions`를 대조하도록 했다.
  - 선언되지 않은 slot/action이 있으면 `ValueError`로 실패시켜, 새 에이전트 개발 중 후속 맥락 후보가 라우터/검증 계층이 모르는 단서를 남기는 문제를 조기에 잡도록 했다.
  - 내부 확인 질문용 `clarify` action은 사용자 후속 action이 아니라 실행 대기 표시로 쓰이므로 런타임 계약 예외로 유지했다.
  - 새 계약을 적용하면서 알림 에이전트가 `reminder_text`와 중복으로 남기던 `slots.text`를 제거해 알림 본문 슬롯을 `reminder_text`로 표준화했다.
  - `plan.md`에 런타임 dispatch 단계에서도 `OperationResult.slots`와 `OperationResult.available_actions`가 카탈로그 선언 범위를 벗어나면 실패한다는 규칙을 추가했다.
  - `test_registry_dispatch_rejects_result_slots_not_declared_in_catalog`, `test_registry_dispatch_rejects_result_actions_not_declared_in_catalog`, `test_registry_dispatch_allows_internal_clarify_action_without_catalog_output`를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`40 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_memory_store.py tests/test_weather_agent.py tests/test_document_analysis_agent.py tests/test_web_search_agent.py -q`(`366 passed`), `python3 -m pytest -q`(`979 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - OperationResult artifact 런타임 계약 보강

- 작업 이름: 링크 가능한 대상 없는 artifact가 후속 맥락 후보에 남지 않도록 dispatch 검증 추가
- 진행상황: 완료
- 진행내용:
  - `OperationResult.slots`와 `available_actions`는 런타임 카탈로그 검증을 받지만, `artifacts`는 아직 동적 반환값이 카탈로그 선언 밖으로 벗어나거나 ID/URL 없는 대상 단서를 남길 수 있음을 확인했다.
  - `AgentRegistry.dispatch()`의 결과 계약 검증에 artifact 검사를 추가했다.
  - 지원 artifact kind를 `memory`, `document`, `task`, `reminder`, `url`, `web_result`로 고정하고, kind별로 필요한 `artifacts.memory_ids`, `artifacts.document_ids`, `artifacts.task_ids`, `artifacts.reminder_ids`, `artifacts.urls` 선언이 있는지 확인하도록 했다.
  - memory/document/task/reminder artifact는 `id`, `{kind}_id`, `{kind}_ids` 중 하나를, url/web_result artifact는 `url` 또는 `urls`를 반드시 포함해야 하도록 했다.
  - 이 계약을 통해 새 에이전트가 라우터가 해석할 수 없는 artifact kind나 링크할 대상 없는 artifact를 turn state와 내부 행동 로그에 남기는 일을 개발 단계에서 차단한다.
  - `plan.md`에 런타임 dispatch 단계에서 `OperationResult.artifacts`도 카탈로그 선언 범위와 링크 가능한 ID/URL 보유 여부를 검증한다는 규칙을 추가했다.
  - `test_registry_dispatch_rejects_result_artifacts_not_declared_in_catalog`, `test_registry_dispatch_rejects_result_artifacts_without_linkable_target`, `test_registry_dispatch_allows_declared_linkable_result_artifacts`를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`43 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_memory_store.py tests/test_weather_agent.py tests/test_document_analysis_agent.py tests/test_web_search_agent.py -q`(`366 passed`), `python3 -m pytest -q`(`982 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - OperationResult retryable 런타임 계약 보강

- 작업 이름: 선언되지 않은 재시도 가능 상태가 라우터 후보에 남지 않도록 dispatch 검증 추가
- 진행상황: 완료
- 진행내용:
  - `OperationResult.retryable=True`는 사용자의 `다시해봐` 같은 후속 요청을 retry 연결로 이끄는 핵심 단서지만, 카탈로그 선언과 런타임 결과가 어긋나도 막는 검증이 없음을 확인했다.
  - `AgentRegistry.dispatch()`의 결과 계약 검증에 `retryable=True`일 때 해당 intent의 `state_outputs`에 `retryable`이 선언되어 있어야 한다는 규칙을 추가했다.
  - 문서 분석 에이전트가 재분석 가능한 결과를 남기므로 `analyze_document` 카탈로그에 `retryable`을 추가했다.
  - 메시지 처리 오류 fallback은 `chat` intent이지만 사용자가 재시도할 수 있어야 하므로 `chat` 카탈로그에 `available_actions.retry`, `retryable`을 추가하고, route validation의 `INTENT_ACTIONS["chat"]`에도 `retry`를 추가했다.
  - literal `OperationResult(retryable=True)`가 있는 intent는 카탈로그에 `retryable`을 선언해야 한다는 정적 테스트를 추가해 새 에이전트의 누락을 잡도록 했다.
  - `plan.md`에 런타임 dispatch 단계에서 `OperationResult.retryable`도 카탈로그 선언 범위를 벗어나면 실패한다는 규칙을 추가했다.
  - `test_registry_dispatch_rejects_retryable_result_not_declared_in_catalog`, `test_registry_dispatch_allows_retryable_result_declared_in_catalog`, `test_agent_catalog_declares_literal_operation_result_retryable`를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`46 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py tests/test_cli.py -q`(`607 passed`), `python3 -m pytest -q`(`985 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - facts 기반 런타임 슬롯 계약 보강

- 작업 이름: `OperationResult.facts`가 후속 맥락 슬롯으로 승격될 때도 카탈로그 선언을 강제
- 진행상황: 완료
- 진행내용:
  - `infer_turn_slots()`가 `facts.location`, `facts.current_time`, `facts.query` 같은 값을 후속 맥락 슬롯으로 승격할 수 있으므로, 실제 런타임 결과가 `slots`는 비워도 `facts`만으로 라우터 후보를 오염시킬 수 있음을 확인했다.
  - `AgentRegistry.dispatch()`의 결과 계약 검증에 `FACT_CONTEXT_SLOT_KEYS`를 추가해, 후속 맥락 슬롯으로 승격 가능한 fact 키가 `agent_catalog.json state_outputs`에 선언되어 있지 않으면 `ValueError`로 실패하도록 했다.
  - `FACT_CONTEXT_SLOT_KEYS`가 실제 `infer_turn_slots()`의 `TURN_STATE_ID_SLOT_KEYS | INTERNAL_ACTION_CONTEXT_KEYS`와 항상 같도록 회귀 테스트를 추가했다.
  - `status`와 `daily_briefing`, `chat` 결과의 표시용 현재 위치 fact를 날씨 지역 대상인 `location`이 아니라 `location_label`로 정리했다.
  - `status`의 표시용 현재 시각 fact는 `current_time` 대신 `status_checked_at`으로 바꿔, “지금 몇 시야” 같은 시간 실행 슬롯과 상태 조회 점검 시각이 섞이지 않게 했다.
  - `reset_context`의 삭제 개수와 장기 기억 유지 여부는 후속 라우팅 대상이 아니므로 `slots`가 아니라 `facts`에만 남기도록 정리했다.
  - `daily_briefing`은 후속 조회/회상에서 최근 할 일, 메모, 문서를 정확히 이어갈 수 있도록 단수/복수 ID 슬롯과 document artifact 선언을 카탈로그에 맞췄다.
  - `test_registry_dispatch_rejects_result_fact_slots_not_declared_in_catalog`, `test_registry_dispatch_allows_declared_result_fact_slots`, `test_registry_fact_context_slot_keys_match_turn_state_inference_keys`를 추가했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`49 passed`), `python3 -m pytest tests/test_utility_agent.py tests/test_bot_helpers.py::test_assistant_bot_expires_stale_general_pending_on_new_request tests/test_bot_helpers.py::test_assistant_bot_expires_stale_pending_attachment_on_new_request -q`(`6 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_memory_store.py tests/test_weather_agent.py tests/test_document_analysis_agent.py tests/test_web_search_agent.py -q`(`366 passed`)를 통과했다.
  - 최종 검증으로 `python3 -m pytest -q`(`988 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 봇 직접 OperationResult 계약 검증 보강

- 작업 이름: registry를 우회한 봇/버튼 직접 결과가 turn state와 내부 로그를 오염시키지 않도록 차단
- 진행상황: 완료
- 진행내용:
  - `AgentRegistry.dispatch()`를 통과한 결과는 런타임 카탈로그 검증을 받지만, Discord 봇 본체와 버튼 처리 경로가 직접 만든 `OperationResult`는 같은 검증을 우회할 수 있음을 확인했다.
  - `validate_registered_operation_result()` 공통 helper를 추가하고, 봇의 `record_turn_state()`, `record_internal_action_result()`, `confirmation_view_for()` 앞단에서 같은 카탈로그 계약을 확인하도록 했다.
  - 계약을 위반한 직접 결과는 사용자 답변 자체를 막지 않고, 다음 턴 라우터가 참고하는 turn state, 내부 행동 로그, 확인 버튼 후보에 저장하지 않도록 했다.
  - 운영 CLI의 로컬 ask 경로는 검증 도구 성격이 강하므로, 응답 기록 전에 같은 계약을 검증하고 위반 시 바로 실패하도록 연결했다.
  - `pending_*`, `context_link`, `linked_state_id`, 후보 선택 정보, 버튼 선택 정보처럼 오케스트레이션이 붙이는 내부 메타데이터는 intent별 기능 슬롯이 아니므로 공통 내부 슬롯 예외로 분리했다.
  - `task_title`은 라우터 resolved slot과 응답 컨텍스트에서 실제로 사용하는 할 일 대상 슬롯이므로 `manage_task` 카탈로그와 내부 route slot 병합 키에 추가했다.
  - `remember` 결과가 메모 artifact를 남기는 경로를 카탈로그가 설명하도록 `artifacts.memory_ids`를 선언했다.
  - `test_assistant_bot_skips_invalid_direct_result_context_recording`을 추가해 선언되지 않은 슬롯을 가진 직접 결과가 turn state와 내부 행동 로그에 저장되지 않는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_skips_invalid_direct_result_context_recording tests/test_bot_helpers.py::test_assistant_bot_record_turn_state_merges_fact_slots_with_explicit_slots tests/test_agent_registry.py::test_registry_fact_context_slot_keys_match_turn_state_inference_keys -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_agent_registry.py -q`(`250 passed`), `python3 -m pytest -q`(`989 passed`)를 통과했다.

## 2026-06-07 - OperationResult literal 통합 계약 테스트 추가

- 작업 이름: 코드에 직접 작성된 `OperationResult`가 카탈로그 계약을 정적으로 따르는지 검증
- 진행상황: 완료
- 진행내용:
  - 기존 테스트는 literal `slots`, `facts`, `available_actions`, `retryable`을 각각 검사했지만, `artifacts`까지 포함한 전체 `OperationResult` 계약을 한 번에 검증하지는 않았음을 확인했다.
  - `test_literal_operation_results_follow_catalog_contract`를 추가해 `assistant_bot` 코드에 직접 쓰인 literal `OperationResult`를 구성한 뒤 `validate_operation_result_contract()`로 카탈로그 선언과 대조하도록 했다.
  - 이 테스트는 `remember` 결과처럼 artifact를 남기는 직접 응답이 `agent_catalog.json`에 `artifacts.memory_ids`를 선언하지 않는 문제를 런타임 전에 잡기 위한 안전장치다.
  - `python3 -m pytest tests/test_agent_registry.py::test_literal_operation_results_follow_catalog_contract -q`(`1 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_bot_helpers.py tests/test_cli.py -q`(`251 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`459 passed`), `python3 -m pytest -q`(`990 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 일반 문서 분석 후속 요청 맥락 연결 보강

- 작업 이름: `문서 요약해줘` 같은 일반 후속 요청을 최근 문서 후보와 안전하게 연결
- 진행상황: 완료
- 진행내용:
  - `문서 요약해줘`, `파일 분석해줘`처럼 대명사는 없지만 대상 종류와 분석 동작이 명확한 문장이 기존 fallback에서는 `recall` 새 요청으로 남아 최근 문서 분석 상태를 이어받지 못하는 문제를 확인했다.
  - `context_aware_fallback_route()`가 일반 문서/파일 분석 요청을 만나면, 최근 현재 위치 문서 후보가 있는 경우 후보 매칭 단계까지 진행하도록 보강했다.
  - 최근 문서 후보가 정확히 하나이고 `document_ids` 또는 문서 artifact처럼 실행 가능한 대상이 있으면 `analyze_document`로 이어가고, 후보가 여러 개이면 자동 선택하지 않고 `pending_candidate_state_ids`를 담은 확인 질문으로 전환하도록 했다.
  - 실행 가능한 문서 대상이 없는 내부 행동 로그 후보는 자동 연결에서 제외해, `contract.pdf` 내부 힌트나 취소된 pending state가 `invoice.pdf 다시 요약해줘` 같은 새 파일 요청을 빼앗지 않도록 했다.
  - `generic_document_summary_links_single_recent_document`, `generic_document_summary_clarifies_multiple_recent_documents` 매트릭스 케이스를 추가했다.
  - `plan.md`에 일반 문서/파일 분석 후속 요청의 단일 후보 연결, 다중 후보 확인, 실행 대상 없는 후보 제외 규칙을 문서화했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`(`139 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`461 passed`), `python3 -m pytest -q`(`992 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 일반 문서 조회 후속 요청 맥락 연결 보강

- 작업 이름: `문서 보여줘` 같은 조회형 문서 요청을 최근 문서 후보와 안전하게 연결
- 진행상황: 완료
- 진행내용:
  - 최근 문서 후보가 정확히 하나 있어도 `문서 보여줘`, `파일 확인해줘`처럼 대명사 없이 대상 종류와 조회 동작만 말하는 문장은 fallback 라우터가 일반 `recall` 새 요청으로 남기는 문제를 확인했다.
  - 일반 문서/파일 조회 요청 판정(`is_generic_document_read_request`)을 추가하고, `document_ids`나 문서 artifact처럼 실행 가능한 문서 대상이 있는 후보에 한해서 후보 매칭 단계와 action 참조 판정을 통과하도록 했다.
  - 삭제, 수정, 복구처럼 위험하거나 변경성 있는 문서 동작은 이 일반 조회 규칙에서 제외해 `문서 삭제해줘` 같은 요청이 단일 최근 문서에 바로 자동 연결되지 않도록 했다.
  - `generic_document_read_links_single_recent_document`, `generic_document_delete_does_not_auto_link_single_recent_document` 매트릭스 케이스를 추가했다.
  - `plan.md`에 대명사 없는 문서/파일 조회 요청의 단일 후보 연결, 다중 후보 확인, 실행 대상 없는 후보 제외, 위험 동작 자동 연결 제외 규칙을 문서화했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`(`141 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`463 passed`), `python3 -m pytest -q`(`994 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 문서 조회 후속 요청 확인 계약 고정

- 작업 이름: 채팅 위치가 바뀐 문서 조회 요청은 실행 전 확인을 거치도록 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - `문서 보여줘`처럼 대명사 없는 조회형 문서 요청이 최근 문서 후보 하나에 연결되도록 보강된 뒤, 같은 규칙이 다른 채팅 위치 후보를 바로 실행하지 않는지 점검했다.
  - 실제 fallback과 route validation 흐름에서 다른 위치의 `문서 7 contract.pdf` 후보는 `recall + clarify`로 남고, 사용자 확인 전에는 바로 실행되지 않음을 확인했다.
  - 현재 위치 후보와 다른 위치 후보가 함께 있을 때는 현재 위치 단일 후보를 우선하는 동작도 수동 재현으로 확인했다.
  - `cross_location_generic_document_read_requires_confirmation` 매트릭스 케이스를 추가해 다른 위치 문서 조회 요청이 `linked_state_id`와 `document_ids`를 보존하되 `context_link=clarify`로 멈추는 계약을 고정했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`(`142 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`464 passed`), `python3 -m pytest -q`(`995 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 후보 선택 답변의 새 실행 동작 우선 처리

- 작업 이름: pending 후보 선택 중 사용자가 새 동작을 말하면 현재 문장을 실행 기준으로 사용
- 진행상황: 완료
- 진행내용:
  - `문서 요약해줘`가 여러 문서 후보 때문에 확인 질문으로 전환된 뒤 사용자가 `두번째 문서 보여줘`라고 답하면, 기존 라우터는 `두번째` 후보 선택만 보고 원래 pending 요청인 “요약”을 복원하는 문제를 확인했다.
  - `route_from_pending_candidate_selection()`에서 후보 선택 답변에 `보여줘`, `요약`, `삭제`, `수정` 같은 실행 동작이 포함되어 있으면 원래 pending 문장 대신 현재 사용자 문장을 route 기준으로 사용하도록 했다.
  - 문서 조회형 선택 답변은 `recall`, 문서 분석형 선택 답변은 `analyze_document`로 보정해 `두번째`처럼 후보만 고른 답변과 `두번째 문서 보여줘`처럼 동작까지 바꾼 답변을 구분했다.
  - 문서 후보가 여러 개인 상태에서 `문서 보여줘`가 새 `recall`로 빠지지 않고 다시 대상 확인 질문으로 남도록, 다중 문서 후보 확인 분기를 조회형 요청에도 적용했다.
  - `generic_document_read_clarifies_multiple_recent_documents`, `pending_candidate_selection_with_new_document_read_action_uses_current_action` 매트릭스 케이스를 추가했다.
  - `plan.md`에 후보 선택 답변에 새 실행 동작이 함께 있으면 원래 pending 요청보다 현재 문장의 동작을 우선한다는 규칙을 문서화했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`(`144 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`466 passed`), `python3 -m pytest -q`(`997 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 메모 후보 선택 답변의 조회 동작 보정

- 작업 이름: pending 후보 선택에서 `두번째 보여줘`가 메모 저장 intent로 남지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 비문서 후보에도 “후보 선택 답변의 새 동작 우선” 원칙을 대입해 보니, 메모 후보 확인 상태에서 `두번째 보여줘`가 `remember` intent로 통과하는 문제를 확인했다.
  - 사용자는 두 번째 메모를 새로 저장하려는 것이 아니라 조회하려는 것이므로, 후보 선택 답변이 메모 후보를 가리키고 조회 동작(`보여`, `알려`, `확인`, `상세`)을 포함하면 base intent를 `recall`로 보정하도록 했다.
  - 삭제 요청은 기존처럼 `delete_memory`를 유지하고, 지원하지 않는 완료 같은 동작은 실행 전 검증이 확인 질문으로 보류하는 기존 방어선을 유지했다.
  - `pending_candidate_selection_with_new_memory_read_action_uses_recall` 매트릭스 케이스를 추가했다.
  - `plan.md`에 메모 후보 선택에서 조회 동작이 명시되면 새 저장(`remember`)이 아니라 저장 항목 조회(`recall`)로 처리한다는 규칙을 문서화했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`(`145 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`467 passed`), `python3 -m pytest -q`(`998 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 후보 제목 기반 변환 요청 맥락 연결 보강

- 작업 이름: `장보기 메모로 저장해줘`처럼 제목으로 후보를 고른 변환 요청을 linked state 재료로 처리
- 진행상황: 완료
- 진행내용:
  - pending 후보 확인 상태에서 `두번째 메모로 저장해줘`는 정상적으로 선택 후보를 새 메모 본문으로 사용했지만, `장보기 메모로 저장해줘`처럼 후보 제목을 직접 말하면 조기 반환 때문에 후보 선택을 건너뛰고 새 메모 요청으로 빠지는 문제를 확인했다.
  - `route_from_pending_candidate_selection()`이 base intent와 action 충돌만 보고 즉시 빠지지 않고, 먼저 pending 후보 제목/ID 선택을 시도하도록 순서를 조정했다.
  - 제목으로 선택된 후보를 다른 종류의 새 항목으로 변환할 수 있도록 라우터에 `selected_candidate_*_creation_request()` helper를 추가했다.
  - route validation에도 linked state 제목이 사용자 문장에 명시된 메모/알림 변환 요청을 허용하는 검증 helper를 추가했다.
  - 변환 요청에서 `memory_text`, `reminder_text`는 기존 상태의 슬롯과 반드시 같아야 하는 대상 식별자가 아니라 새 항목 본문이므로, 해당 변환 요청에 한해 불일치 차단에서 예외 처리했다.
  - `pending_candidate_title_selection_with_memory_creation_uses_selected_source`, `pending_candidate_title_selection_with_reminder_creation_uses_selected_source` 매트릭스 케이스를 추가했다.
  - `plan.md`에 후보 제목 자체가 출처인 변환 요청도 대명사 변환 요청과 동일하게 linked state를 재료로 사용한다는 규칙을 문서화했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`(`147 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`469 passed`), `python3 -m pytest -q`(`1000 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 제목 기반 변환 요청 route validation 직접 테스트 추가

- 작업 이름: 검증 계층 단위에서 제목 기반 메모/알림 변환 허용 계약 고정
- 진행상황: 완료
- 진행내용:
  - 후보 제목 기반 변환 요청은 라우터와 route validation이 함께 맞아야 하므로, 통합 매트릭스뿐 아니라 route validation 단위 테스트가 필요함을 확인했다.
  - `장보기 메모로 저장해줘`가 `manage_task` linked state를 새 메모 본문으로 쓰는 경우를 직접 검증하는 `test_validate_route_context_link_keeps_named_task_to_memory_conversion`을 추가했다.
  - `장보기 알림으로 등록해줘`가 `manage_task` linked state를 새 알림 본문으로 쓰는 경우를 직접 검증하는 `test_validate_route_context_link_keeps_named_task_to_reminder_conversion`을 추가했다.
  - 이 테스트는 새 메모 본문 오저장 방어와 `reminder_text` 불일치 방어가 제목 기반 변환 요청을 다시 차단하지 않도록 고정한다.
  - `python3 -m pytest tests/test_route_validation.py -q`(`154 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`471 passed`), `python3 -m pytest -q`(`1002 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 제목 기반 메모 변환/조회 경계 보강

- 작업 이름: 후보 제목으로 메모 변환은 허용하되 메모 조회 오연결은 차단
- 진행상황: 완료
- 진행내용:
  - pending 후보 확인 상태에서 `장보기 기억해줘`, `장보기 기억으로 바꿔줘`처럼 후보 제목과 메모 변환 동작이 함께 오면, 기존 후보의 제목을 새 메모 본문으로 쓰도록 라우터를 보강했다.
  - `장보기 메모 보여줘`처럼 조회 대상 종류가 메모로 명시됐는데 실제 pending 후보가 할 일뿐인 경우에는 제목이 같더라도 할 일 후보를 메모 조회 대상으로 자동 연결하지 않도록 후보 종류 충돌 검사를 추가했다.
  - `기억으로 바꿔줘` 같은 변환 표현에서 route validation이 `장보기 기억으로` 전체를 대상명으로 오인해 링크를 제거하지 않도록, 명시적 대상 추출에서 변환 목적어 접미사를 분리했다.
  - `pending_candidate_title_selection_with_memory_remember_uses_selected_source`, `pending_candidate_title_selection_with_memory_conversion_uses_selected_source`, `pending_candidate_title_memory_read_does_not_select_task_candidate` 매트릭스 케이스를 추가했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`(`150 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`474 passed`), `python3 -m pytest -q`(`1005 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 같은 제목 다종 후보 선택 보강

- 작업 이름: 동일 제목의 할 일/메모 후보가 있을 때 명시 대상 종류로 선택 범위 축소
- 진행상황: 완료
- 진행내용:
  - `장보기`라는 제목의 할 일과 메모가 동시에 pending 후보에 있을 때 `장보기 메모 보여줘`가 제목 매칭 후보 2개를 보고 포기하거나, fallback에서 `remember`로 남아 검증층이 링크를 끊는 문제를 확인했다.
  - pending 후보 선택에서 명시 제목 매칭 후보가 여러 개이고 요청이 조회/수정처럼 대상 종류를 말하는 경우, `메모`, `할 일`, `알림`, `문서` 등 요청 종류에 맞는 후보로 먼저 좁히도록 했다.
  - `메모로 저장`, `알림으로 등록`처럼 기존 후보를 재료로 다른 종류의 새 항목을 만드는 변환 요청은 이 종류 필터에서 제외해, 출처 후보 선택 흐름을 막지 않도록 했다.
  - `pending_candidate_title_memory_read_selects_memory_over_same_title_task` 매트릭스 케이스를 추가해 같은 제목의 할 일과 메모 중 메모 후보가 `recall`로 선택되는 계약을 고정했다.
  - `python3 -m pytest tests/test_context_routing_matrix.py -q`(`151 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`475 passed`), `python3 -m pytest -q`(`1006 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 버튼 응답 작성 컨텍스트 보강

- 작업 이름: 확인/후보 선택 버튼 경로에서도 최신 라우터 컨텍스트를 응답 작성자에게 전달
- 진행상황: 완료
- 진행내용:
  - 일반 메시지 처리 경로는 실행 후 최신 라우터 컨텍스트와 실행 컨텍스트를 `ResponseComposer`에 넘기지만, 버튼 기반 승인/거부/후보 선택 경로는 `conversation_context=""`로 응답을 작성해 최근 대화와 작업 상태 후보를 보지 못하는 구조를 확인했다.
  - `button_response_conversation_context()` helper를 추가하고, 확인 버튼, URL 후보 선택 버튼, 작업 상태 후보 선택 버튼의 응답 작성 호출에서 최신 `build_router_context()` 결과를 전달하도록 했다.
  - 기존 result metadata 기반 `ExecutionContext` 복원은 유지해, 버튼 실행 대상 ID와 resolved slots는 그대로 보존하면서 답변 작성 모델이 최근 대화/내부 행동 기록도 함께 참고할 수 있게 했다.
  - 버튼 테스트를 보강해 일반 확인 버튼, URL 후보 버튼, 작업 상태 후보 버튼의 composer 호출에 `최근 작업 상태 후보`와 선택 대상명이 포함되는지 확인했다.
  - `python3 -m pytest tests/test_bot_helpers.py -q`(`123 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_response_composer.py tests/test_context_builder.py -q`(`200 passed`), `python3 -m pytest -q`(`1006 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - CLI 응답 작성 컨텍스트 재빌드 보강

- 작업 이름: 로컬 `ask` 경로도 실행 후 최신 라우터 컨텍스트로 답변 작성
- 진행상황: 완료
- 진행내용:
  - Discord 일반 메시지 경로는 `handle_message()` 실행 후 최신 라우터 컨텍스트를 다시 빌드해 `ResponseComposer`에 넘기지만, CLI `ask` 경로는 실행 전 `conversation_context`를 그대로 사용하고 있음을 확인했다.
  - `run_local_text_interaction()`에서 에이전트 실행 결과를 만든 뒤 `response_conversation_context = build_router_context(...)`를 다시 계산하고, 최종 응답 작성에는 이 최신 컨텍스트를 전달하도록 변경했다.
  - 이 변경으로 CLI 재현에서도 라우팅 검증 로그, 만료된 pending 상태, 실행 중 추가된 내부 행동 단서가 가능한 최신 상태로 답변 작성자에게 전달된다.
  - `test_cli_response_composer_uses_post_execution_router_context`를 추가해 CLI 응답 작성이 실행 후 재빌드된 컨텍스트를 사용하는 계약을 고정했다.
  - `python3 -m pytest tests/test_cli.py -q`(`79 passed`), `python3 -m pytest tests/test_cli.py tests/test_context_builder.py tests/test_response_composer.py -q`(`156 passed`), `python3 -m pytest -q`(`1007 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 로그 사용자 격리 보강

- 작업 이름: 같은 서버 채널의 다른 사용자 내부 로그가 라우터 컨텍스트에 섞이지 않도록 차단
- 진행상황: 완료
- 진행내용:
  - 기존 내부 행동 컨텍스트는 다른 대화 위치의 로그는 `recent_conversations_for_user()`로 같은 사용자 대화만 가져왔지만, 현재 `conversation_id`가 서버 채널처럼 여러 사용자가 공유하는 위치이면 `agent_logs`에 user_id가 없어 다른 사용자 로그가 섞일 수 있음을 확인했다.
  - `agent_logs` 테이블에 `user_id` 컬럼을 추가하고, 신규 DB 생성과 기존 DB migration 모두에서 컬럼을 보장하도록 했다.
  - `AgentLogStore.add()`에 선택적 `user_id`를 추가하고, 라우터 로그, route validation 로그, 내부 실행 결과 로그, pending 만료/승인/메모 저장 관련 운영 로그가 scope의 user_id를 함께 저장하도록 보강했다.
  - `build_internal_action_context()`는 현재 사용자 user_id로 로그를 필터링한다. user_id가 없는 과거 로그는 사용자 ID가 conversation_id에 포함된 DM/로컬 같은 사용자 전용 위치에서만 레거시 참고자료로 허용하고, 공유 채널에서는 제외한다.
  - `test_build_router_context_excludes_other_user_internal_logs_in_same_channel`을 추가해 같은 conversation_id 안에서도 user_id가 다른 내부 로그가 라우터 컨텍스트에 포함되지 않는 계약을 고정했다.
  - `python3 -m pytest tests/test_context_builder.py -q`(`53 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`(`373 passed`), `python3 -m pytest -q`(`1008 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 전문 에이전트 로그 user_id 보존 보강

- 작업 이름: 각 에이전트 운영 로그도 사용자 격리 필터를 통과하도록 user_id 저장
- 진행상황: 완료
- 진행내용:
  - `agent_logs.user_id`를 도입한 뒤 라우터/검증/오케스트레이션 로그는 사용자별로 저장되지만, Memory/Task/Reminder/Weather/Web/Document Analysis/Utility/Conversation 에이전트의 직접 로그는 여전히 user_id 없이 남아 공유 채널에서 내부 행동 컨텍스트에 포함되지 않을 수 있음을 확인했다.
  - 전문 에이전트의 `logs.add()` 호출에 `user_id=scope.user_id`를 추가해, 사용자 격리 정책을 유지하면서도 각 에이전트의 모델 선택, 검색/조회/저장/분석 로그가 다음 턴 맥락 단서로 남도록 했다.
  - 봇/CLI의 pending 만료, 웹검색 승인, 메모 대기 저장, 첨부 중복 방지 같은 scope 기반 운영 로그도 user_id를 함께 저장하도록 확인했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_memory_store.py tests/test_weather_agent.py tests/test_web_search_agent.py tests/test_document_analysis_agent.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`(`539 passed`), `python3 -m pytest -q`(`1008 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 로그 user_id 계약 회귀 테스트 추가

- 작업 이름: 새 에이전트가 logs.add 호출에 user_id를 빠뜨리지 않도록 테스트 고정
- 진행상황: 완료
- 진행내용:
  - `agent_logs.user_id` 기반 사용자 격리 정책은 새 에이전트가 추가될 때 `logs.add()`에 user_id를 빼먹으면 공유 채널에서 내부 행동 기록이 누락되거나 레거시 처리로 오해될 수 있음을 확인했다.
  - `tests/test_agent_registry.py`에 `test_scope_based_agent_logs_include_user_id`를 추가해 `assistant_bot/bot.py`, `assistant_bot/cli.py`, `assistant_bot/agents/*.py`의 `logs.add()`/`self.logs.add()` 호출이 모두 `user_id` keyword를 포함하도록 검사한다.
  - 이 테스트는 새 전문 에이전트나 오케스트레이션 경로가 내부 행동 로그를 추가할 때 사용자 격리 계약을 자동으로 확인한다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`51 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`(`424 passed`), `python3 -m pytest -q`(`1009 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 레거시 내부 로그 사용자 ID 정확 매칭 보강

- 작업 이름: user_id 없는 과거 agent_logs가 비슷한 사용자 ID에 부분 매칭되지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - `agent_logs.user_id`가 없는 과거 로그를 사용자 전용 conversation_id에서만 레거시 참고자료로 허용하는 과정에서, 기존 helper가 단순 부분 문자열 포함으로 `user_id in conversation_id`를 사용하고 있음을 확인했다.
  - 이 방식은 `user-1`이 `dm:user-10`에도 매칭될 수 있어, user_id가 비슷한 다른 사용자의 과거 내부 로그가 맥락에 섞일 위험이 있었다.
  - `conversation_id_mentions_user()`를 정규식 기반 정확 토큰 매칭으로 바꿔, 영숫자/하이픈/언더스코어 경계 밖에서만 사용자 ID가 일치하도록 했다.
  - `test_build_router_context_legacy_user_log_match_requires_exact_user_token`을 추가해 `dm:user-1` 레거시 로그는 유지하고 `dm:user-10` 레거시 로그는 제외하는 계약을 고정했다.
  - `python3 -m pytest tests/test_context_builder.py -q`(`54 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_agent_registry.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`(`425 passed`), `python3 -m pytest -q`(`1010 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 최근 작업 상태 사용자 격리 회귀 테스트 추가

- 작업 이름: 공유 채널의 다른 사용자 turn state가 라우터 컨텍스트와 pending 후보에 섞이지 않도록 테스트 고정
- 진행상황: 완료
- 진행내용:
  - `ConversationTurnStateStore`의 `recent_candidates`, `pending_candidates`, `get`, `expire` 조회 경로가 현재 사용자 `user_id`를 기준으로 필터링하는지 확인했다.
  - 공유 서버 채널처럼 여러 사용자가 같은 `conversation_id`를 쓰는 경우에도 다른 사용자의 실패/대기 상태가 현재 사용자 라우터 컨텍스트에 들어가면 “다시해봐”, “그거 처리해” 같은 후속 요청이 잘못 연결될 수 있음을 점검했다.
  - `test_build_router_context_excludes_other_user_turn_states_in_shared_channel`을 추가해 같은 conversation_id 안의 다른 사용자 최근 작업 상태가 `build_router_context()`와 `recent_candidates()` 결과에서 제외되는 계약을 고정했다.
  - `test_turn_state_store_pending_candidates_returns_all_current_pending_states`에 같은 conversation_id의 다른 사용자 pending 상태도 제외되는 검증을 추가했다.
  - `plan.md`에 `conversation_turn_states`는 현재 사용자 `user_id` 기준으로 조회해야 하며, 다른 위치 후보도 같은 사용자 상태만 허용한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_context_builder.py -q`(`55 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_agent_registry.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`(`426 passed`), `python3 -m pytest -q`(`1011 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 최근 대화 컨텍스트 사용자 중심 필터 추가

- 작업 이름: 공유 채널의 다른 사용자 최근 대화가 라우터 판단에 섞이지 않도록 차단
- 진행상황: 완료
- 진행내용:
  - `ConversationStore.recent_messages()`에 선택적 `user_id` 필터를 추가해, 현재 사용자 메시지와 그 직후의 봇 답변만 최근 대화 컨텍스트에 포함할 수 있게 했다.
  - `build_router_context()`와 `build_execution_context()`가 최근 대화를 만들 때 현재 `scope.user_id`를 넘기도록 변경했다.
  - conversation 단위 요약은 사용자 ID가 conversation_id에 정확히 들어간 사용자 전용 위치에서만 사용하도록 `latest_summary_for_scope()`를 추가했다. 공유 conversation_id의 요약은 다른 사용자 대화가 섞였을 수 있으므로 라우터/실행 컨텍스트에서 제외한다.
  - `test_build_router_context_filters_recent_messages_to_current_user_in_shared_channel`을 추가해 공유 채널에서 다른 사용자의 메시지, 그에 대한 봇 답변, 공유 요약이 현재 사용자 라우터 컨텍스트에 들어가지 않는 계약을 고정했다.
  - `plan.md`에 최근 대화와 conversation 요약도 사용자 격리 대상이라는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_context_builder.py -q`(`56 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_agent_registry.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`(`427 passed`), `python3 -m pytest -q`(`1012 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 최근 맥락 미리보기 사용자 격리 보강

- 작업 이름: 같은 사용자 다른 위치 후보의 최신 미리보기가 다른 사용자 메시지로 오염되지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - `recent_conversations_for_user()`는 현재 사용자가 참여한 conversation을 고르지만, 각 conversation의 `latest_content`는 전체 최신 메시지를 가져와 공유 채널에서 다른 사용자의 마지막 메시지가 cross-location 맥락에 표시될 수 있음을 확인했다.
  - `ConversationStore.latest_user_context_preview()`를 추가해 현재 사용자 메시지와 그 직후 봇 답변으로 구성된 최근 대화 미리보기를 가져오도록 했다.
  - `build_cross_location_context()`는 사용자 전용 conversation_id의 요약만 사용하고, 공유 위치에서는 현재 사용자 중심 미리보기만 사용하도록 변경했다.
  - `test_cross_location_context_uses_current_user_preview_in_shared_other_location`을 추가해 다른 위치 공유 채널의 다른 사용자 메시지, 그에 대한 봇 답변, 공유 요약이 현재 사용자 cross-location 맥락에 들어가지 않는 계약을 고정했다.
  - `plan.md`에 같은 사용자 다른 위치 최근 맥락도 현재 사용자 중심 미리보기만 사용해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_context_builder.py -q`(`57 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_agent_registry.py tests/test_router_agent.py tests/test_bot_helpers.py tests/test_cli.py -q`(`428 passed`), `python3 -m pytest -q`(`1013 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 대화 요약/압축 사용자별 저장 보강

- 작업 이름: 공유 conversation에서 대화 압축 요약과 최근 대화 기반 기능이 다른 사용자 맥락을 섞지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - `conversation_summaries` 테이블에 `user_id` 컬럼을 추가하고, 기존 DB migration에서도 컬럼을 보장하도록 했다.
  - `ConversationStore.latest_summary()`와 `add_summary()`가 선택적 `user_id`를 받도록 변경했다. user_id가 없는 레거시 요약은 conversation_id가 사용자 전용임이 확인될 때만 호환 조회하고, 공유 conversation에서는 사용자별 요약만 조회한다.
  - `ConversationAgent.chat()`와 `compress_context()`가 최근 대화, 이전 요약, 압축 트리거 글자 수, 새 요약 저장을 모두 현재 `scope.user_id` 기준으로 처리하도록 했다.
  - 봇 일반 메시지 경로와 CLI `ask` 경로의 context compression 호출도 `ConversationScope`를 전달하도록 변경했다.
  - `MemoryAgent`의 “네가 예로 든 내용 그대로 수정” 참고 문장 추출과 `TaskAgent`의 “최근 대화에서 할 일 추출” 기능도 현재 사용자 중심 최근 대화만 사용하도록 바꿨다.
  - 사용자 전용 DM/채널 conversation의 과거 assistant-only 메시지는 레거시 호환을 위해 유지하되, 공유 conversation에서는 현재 사용자 메시지 뒤의 봇 답변만 현재 사용자 컨텍스트로 인정한다.
  - `test_build_router_context_uses_user_specific_summary_in_shared_channel`과 `test_conversation_agent_compress_context_uses_current_user_messages_in_shared_channel`을 추가해 공유 conversation의 사용자별 요약 조회, 압축 입력, 압축 결과 저장이 다른 사용자와 분리되는 계약을 고정했다.
  - `plan.md`에 conversation summary도 user_id 기준으로 저장/조회해야 하며, 최근 대화 기반 에이전트 기능도 현재 사용자 중심 입력만 사용해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_context_builder.py tests/test_memory_store.py -q`(`174 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_memory_store.py tests/test_bot_helpers.py tests/test_cli.py -q`(`376 passed`), `python3 -m pytest -q`(`1015 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 대화 맥락 초기화 사용자 범위 보강

- 작업 이름: 공유 conversation에서 현재 사용자 맥락만 초기화하도록 reset_context 수정
- 진행상황: 완료
- 진행내용:
  - `UtilityAgent.reset_context()`가 `ConversationStore.clear_conversation(scope.conversation_id)`를 호출해 conversation 전체 메시지와 요약을 삭제하고 있음을 확인했다.
  - `ConversationStore.clear_conversation()`에 선택적 `user_id`를 추가하고, 사용자 범위 삭제용 `clear_conversation_for_user()`를 구현했다. 기존 관리자 CLI의 명시 conversation 전체 삭제 호출은 그대로 유지된다.
  - 사용자 범위 삭제는 현재 사용자의 user 메시지와 사용자별 conversation summary만 삭제한다. 공유 conversation에서 assistant 메시지는 여러 사용자 응답일 수 있으므로 직접 삭제하지 않고, 사용자 중심 recent context 필터가 현재 사용자 메시지 삭제 후 자연스럽게 제외하게 둔다.
  - `UtilityAgent.reset_context()`는 현재 `scope.user_id`를 전달해, 공유 conversation에서 다른 사용자의 메시지와 요약을 삭제하지 않도록 변경했다.
  - `test_utility_reset_context_clears_only_current_user_context_in_shared_channel`을 추가해 현재 사용자 메시지와 요약만 삭제되고 다른 사용자 맥락은 유지되는 계약을 고정했다.
  - `plan.md`에 대화 맥락 초기화도 현재 사용자 범위만 지워야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_utility_agent.py tests/test_memory_store.py -q`(`121 passed`), `python3 -m pytest tests/test_utility_agent.py tests/test_memory_store.py tests/test_context_builder.py tests/test_bot_helpers.py tests/test_cli.py -q`(`381 passed`), `python3 -m pytest -q`(`1016 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 버튼 확인 경로 사용자 격리 회귀 테스트 추가

- 작업 이름: 공유 채널 버튼을 다른 사용자가 눌러도 pending 작업이 실행/만료되지 않도록 테스트 고정
- 진행상황: 완료
- 진행내용:
  - 일반 확인 버튼, URL 후보 선택 버튼, 후속 작업 후보 선택 버튼 핸들러가 모두 `interaction.user.id`와 `scope.user_id`를 비교해 요청한 사용자만 처리하는지 확인했다.
  - 구현은 이미 다른 사용자 클릭 시 ephemeral 안내 후 반환하도록 되어 있었으므로, 기능 변경 없이 회귀 테스트를 추가했다.
  - `test_confirmation_button_rejects_other_user_without_expiring_pending_state`를 추가해 다른 사용자가 일반 확인 버튼을 눌러도 에이전트 dispatch, 응답 작성, 메시지 edit, pending 만료가 발생하지 않는 계약을 고정했다.
  - `test_url_candidate_button_rejects_other_user_without_expiring_pending_state`를 추가해 URL 후보 버튼도 같은 사용자 격리 규칙을 지키는지 확인했다.
  - `test_state_candidate_button_rejects_other_user_without_expiring_pending_state`를 추가해 후속 작업 후보 선택 버튼도 다른 사용자 클릭으로 pending 상태가 소모되지 않도록 고정했다.
  - `plan.md`에 확인/후보 선택 버튼은 요청한 사용자만 처리해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_bot_helpers.py -q`(`126 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_memory_store.py tests/test_utility_agent.py tests/test_cli.py -q`(`384 passed`), `python3 -m pytest -q`(`1019 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 저장소 사용자 격리 회귀 테스트 추가

- 작업 이름: 공유 conversation에서 다른 사용자 pending 확인/저장 대기 작업이 latest/resolve 대상이 되지 않도록 테스트 고정
- 진행상황: 완료
- 진행내용:
  - `PendingAttachmentStore`, `PendingMemoryDeletionStore`, `PendingMemoryCaptureStore`, `PendingWebSearchConfirmationStore`의 `latest`, `unresolved_count`, `resolve_open`, `resolve_expired` 경로가 `conversation_id`, `user_id`, `guild_id` 기준으로 필터링되는지 확인했다.
  - 구현은 이미 현재 사용자 scope 기준으로 안전하게 필터링하고 있었으므로 기능 변경 없이 회귀 테스트를 추가했다.
  - `test_pending_stores_ignore_other_user_requests_in_shared_conversation`을 추가해 같은 공유 conversation_id 안의 다른 사용자 pending 요청이 현재 사용자의 latest/resolve_open 대상이 되지 않는 계약을 고정했다.
  - `plan.md`에 첨부 저장 대기, 기억 삭제 확인, 다음 메시지 메모 캡처, 웹검색 확인 같은 pending 저장소도 현재 사용자 `user_id` 기준으로만 조회/해결해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_memory_store.py -q`(`117 passed`), `python3 -m pytest tests/test_memory_store.py tests/test_bot_helpers.py tests/test_cli.py -q`(`322 passed`), `python3 -m pytest -q`(`1020 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 찾을 수 없는 linked state pending 슬롯 제거 보강

- 작업 이름: 다른 사용자 state id가 라우터 결과에 들어와도 확인 대기에 재보존되지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - `validate_route_context_link()`는 현재 사용자와 다른 linked state를 제거하는 테스트가 있었지만, 실제 봇 경로에서는 다른 사용자 state id를 현재 사용자 scope로 조회하면 `linked_state=None`이 되고, 이 경우 모호한 후속 요청을 clarify로 바꾸면서 기존 `linked_state_id`가 pending 슬롯에 남을 수 있음을 확인했다.
  - 이 상태는 즉시 dispatch되지는 않지만, 확인 대기 상태에 찾을 수 없는 state id가 남아 다음 승인 흐름의 잘못된 후보가 될 수 있다.
  - `clear_or_clarify_missing_linked_state()`를 추가해 linked state를 찾지 못한 경우에도 `linked_state_id`, `link_confidence`, `resolved_slots`를 반드시 제거하도록 했다.
  - `test_validate_route_context_link_drops_missing_linked_state_for_follow_up`을 추가해 route validation 단위에서 찾을 수 없는 linked state id가 clarify 결과에 남지 않는 계약을 고정했다.
  - `test_validate_route_context_link_drops_missing_linked_state_for_clarify`를 추가해 라우터가 애초에 `clarify`로 반환한 경우에도 찾을 수 없는 linked state id와 resolved slots가 남지 않는 계약을 고정했다.
  - `test_assistant_bot_clears_other_user_linked_state_from_router`를 추가해 라우터가 다른 사용자 state id를 반환해도 봇이 dispatch하지 않고, pending 확인 슬롯에도 해당 id와 resolved slots를 남기지 않는지 검증했다.
  - `plan.md`에 linked state를 찾지 못했거나 현재 사용자와 일치하지 않으면 자동 실행뿐 아니라 pending 확인 슬롯에서도 id와 slots를 제거해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_route_validation.py -q`(`156 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_cli.py -q`(`538 passed`), `python3 -m pytest -q`(`1023 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 최근 대화 조회 user_id 계약 회귀 테스트 추가

- 작업 이름: 새 에이전트가 recent_messages 호출에 사용자 범위를 빠뜨리지 않도록 테스트 고정
- 진행상황: 완료
- 진행내용:
  - 라우터/실행 컨텍스트와 최근 대화 기반 에이전트 기능은 현재 사용자 중심 최근 대화를 사용하도록 보강했지만, 새 에이전트가 추가될 때 `recent_messages(scope.conversation_id)`를 직접 호출하면 공유 채널에서 다른 사용자 대화가 다시 섞일 수 있음을 확인했다.
  - `test_scope_based_recent_message_reads_include_user_id`를 추가해 `assistant_bot/bot.py`, `assistant_bot/cli.py`, `assistant_bot/context_builder.py`, `assistant_bot/agents/*.py`의 `recent_messages()` 호출이 모두 `user_id` keyword를 포함하도록 검사한다.
  - 이 테스트는 새 전문 에이전트나 오케스트레이션 경로가 최근 대화를 직접 읽을 때 현재 사용자 범위를 반드시 넘기도록 강제한다.
  - `plan.md`에 `ConversationStore.recent_messages()` 직접 호출 시 `user_id=scope.user_id` 같은 현재 사용자 범위를 반드시 전달해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`52 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_memory_store.py tests/test_bot_helpers.py tests/test_cli.py -q`(`433 passed`), `python3 -m pytest -q`(`1024 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답 작성 컨텍스트 전달 계약 회귀 테스트 추가

- 작업 이름: ResponseComposer 호출이 최신 대화 컨텍스트와 실행 컨텍스트를 빠뜨리지 않도록 테스트 고정
- 진행상황: 완료
- 진행내용:
  - 일반 메시지, 버튼, CLI 응답 작성 경로가 모두 `conversation_context`와 `execution_context`를 전달하는지 확인했다.
  - 구현은 이미 최신 라우터 컨텍스트와 실제 실행 컨텍스트를 넘기고 있었으므로, 새 오케스트레이션 경로가 추가될 때 계약이 깨지지 않도록 소스 레벨 테스트를 추가했다.
  - `test_response_composer_calls_include_context_contract`를 추가해 `assistant_bot/bot.py`, `assistant_bot/cli.py`의 `ResponseComposer.compose()` 호출이 모두 `conversation_context`와 `execution_context` keyword를 포함하도록 검사한다.
  - `plan.md`에 응답 작성 단계에서도 실행 대상과 resolved slots가 보존되어야 하며, `ResponseComposer.compose()` 호출 시 두 컨텍스트를 반드시 함께 전달해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_agent_registry.py -q`(`53 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_response_composer.py tests/test_bot_helpers.py tests/test_cli.py -q`(`284 passed`), `python3 -m pytest -q`(`1025 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 실행 결과 metadata 보존 경로 보강

- 작업 이름: OperationResult가 실행 컨텍스트 metadata를 잃지 않도록 Discord/CLI 경로 수정
- 진행상황: 완료
- 진행내용:
  - 버튼 후보 실행 경로는 이미 `attach_execution_context_metadata()`를 통과하고 있었지만, 일반 메시지의 기본 dispatch, unsupported dispatch, 문서/이미지 분석, remember, 삭제 확인, 첨부 확인, CLI `ask` 경로는 결과 객체 자체에 실행 metadata를 붙이지 않는 경로가 있음을 확인했다.
  - Discord 일반 메시지 경로에서 `ExecutionContext`가 만들어진 뒤 반환되는 주요 `OperationResult`에 `context_link`, `linked_state_id`, `linked_subject`, `resolved_slots` 같은 route metadata를 붙이도록 보강했다.
  - 이미지 첨부 승인 버튼에서 비전 분석으로 바로 넘어가는 경로도 문서 분석 결과를 즉시 반환하지 않고 `attach_execution_context_metadata()`를 거치도록 수정했다.
  - CLI `ask` 경로는 응답 작성과 내부 행동 기록 전에 `OperationResult`에 실행 metadata를 붙여, 로컬 재현 환경도 Discord 경로와 같은 결과 계약을 따르도록 했다.
  - `test_discord_execution_results_are_attached_before_return`을 추가해 Discord 오케스트레이션이 dispatch/analyze 결과를 바로 반환하지 못하도록 고정했다.
  - `test_cli_attaches_execution_metadata_before_response_recording`을 추가해 CLI가 `raw_answer` 기록 전 실행 metadata를 붙이는 계약을 고정했다.
  - `plan.md`에 실행 결과 객체에도 `ExecutionContext` metadata를 보존해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_agent_registry.py tests/test_bot_helpers.py tests/test_cli.py -q`(`261 passed`), `python3 -m pytest -q`(`1027 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 웹검색 확인 승인 경로 실행 컨텍스트 보강

- 작업 이름: `응, 검색해줘` 같은 짧은 승인에서도 원래 검색어 기준 컨텍스트 유지
- 진행상황: 완료
- 진행내용:
  - 웹검색 확인 대기 승인/거부는 라우터 전에 처리되는 early-return 경로라서, 실제 실행은 대기 중이던 원래 query로 하더라도 응답 작성 컨텍스트가 현재 확인 문장(`응`, `승인`) 중심으로 남을 수 있음을 확인했다.
  - Discord `handle_pending_web_search_confirmation()`이 pending query 기준 `ExecutionContext`를 만들고, `resolved_slots.query`, `query_text`, `pending_query`, `pending_original_text`를 보존하도록 수정했다.
  - 승인 시 웹검색 에이전트 결과에도 `attach_execution_context_metadata()`를 적용하고, `handle_message()`의 `response_execution_context_sink`에도 pending query 기준 실행 컨텍스트를 넣도록 했다.
  - 거부 시에도 원래 query를 `query_text`/`pending_query`로 남겨, 내부 기록과 응답 작성자가 어떤 검색 요청을 거부했는지 볼 수 있게 했다.
  - 로컬 CLI `handle_local_pending_web_search_confirmation()`도 같은 pending query 기준 실행 컨텍스트를 만들고 결과 metadata를 붙이도록 수정했다.
  - CLI `ask` 경로는 pending 확인 결과에 붙은 metadata에서 실행 컨텍스트를 복원해, 최종 응답 작성 단계가 현재 확인 문장보다 원래 query를 우선 보도록 했다.
  - `test_pending_web_search_confirmation_accepts_search_approval_phrase`를 보강하고 `test_handle_message_uses_original_query_context_for_pending_web_search_approval`을 추가해 Discord 직접/상위 경로 모두 원래 query를 실행 컨텍스트와 결과 metadata에 남기는지 검증했다.
  - `test_handle_local_pending_web_search_confirmation_runs_original_query`를 보강해 CLI 승인 경로도 같은 metadata 계약을 따르는지 확인했다.
  - `plan.md`에 라우터 전 확인 경로도 실제 실행 대상 기준 `ExecutionContext`를 사용해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_pending_web_search_confirmation_accepts_search_approval_phrase tests/test_bot_helpers.py::test_handle_message_uses_original_query_context_for_pending_web_search_approval tests/test_cli.py::test_handle_local_pending_web_search_confirmation_runs_original_query -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_agent_registry.py -q`(`262 passed`), `python3 -m pytest -q`(`1028 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 기억 삭제/메모 캡처 pending 경로 실행 컨텍스트 보강

- 작업 이름: 라우터 전 기억 삭제 확인과 다음 메시지 메모 저장의 실제 대상 metadata 보존
- 진행상황: 완료
- 진행내용:
  - 기억 삭제 확인과 다음 메시지 메모 캡처는 라우터 전에 처리되는 early-return 경로라서, 사용자가 `응`, `메모 그만해`처럼 짧게 답하면 응답 작성 컨텍스트가 실제 삭제 대상이나 저장 본문보다 확인 문장 자체에 머물 수 있음을 확인했다.
  - Discord `handle_pending_memory_deletion_confirmation()`이 pending 삭제 대상 기준 `ExecutionContext`를 만들고, 대상 `memory_ids`, `document_ids`, 취소 대상 `canceled_target`을 `resolved_slots`에 남기도록 수정했다.
  - Discord `handle_pending_memory_capture()`가 실제 저장할 다음 메시지 본문을 `resolved_slots.memory_text`로 남기고, 취소 시 `resolved_slots.canceled_target=memory_capture`를 남기도록 수정했다.
  - 두 경로 모두 `response_execution_context_sink`를 갱신해, 최종 응답 작성자가 `응` 같은 확인 문장이 아니라 실제 처리 대상 기준으로 답변을 구성할 수 있게 했다.
  - 로컬 CLI의 `handle_local_pending_memory_deletion()`과 `handle_local_pending_memory_capture()`도 같은 pending 실행 컨텍스트를 만들고 `attach_execution_context_metadata()`를 적용하도록 수정했다.
  - CLI `ask` 경로는 memory deletion/capture pending 결과에 붙은 metadata에서도 실행 컨텍스트를 복원해, Discord와 같은 맥락 조건에서 로컬 재현이 가능하도록 했다.
  - `test_assistant_bot_saves_next_message_from_pending_memory_capture`, `test_on_message_records_pending_memory_capture_as_context_state_and_internal_log`, `test_assistant_bot_file_related_delete_targets_documents_only` 등을 보강해 결과 metadata와 응답 실행 컨텍스트 sink가 실제 대상 기준으로 남는지 검증했다.
  - `test_cli_pending_memory_capture_returns_operation_result_for_internal_context`, `test_cli_pending_memory_deletion_cancel_returns_operation_result_for_internal_context`를 보강해 CLI pending 경로도 같은 metadata 계약을 따르는지 확인했다.
  - `plan.md`에 라우터 전 기억 삭제/메모 캡처 pending 경로도 실제 처리 대상 기준 `ExecutionContext`를 사용해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py -q`(`207 passed`), `python3 -m pytest -q`(`1028 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 첨부 저장 pending 경로 실행 컨텍스트 보강

- 작업 이름: 첨부 저장 승인/거부에서 실제 파일명 metadata 보존
- 진행상황: 완료
- 진행내용:
  - 첨부 저장 pending 경로는 사용자가 버튼을 누르거나 `응, 기억해줘`처럼 짧게 답하는 흐름이므로, 응답 작성자와 내부 행동 기록이 확인 문장보다 실제 파일명을 우선 봐야 함을 확인했다.
  - 이미지 첨부 버튼 승인 경로는 이미 실행 metadata를 붙이고 있었지만, 일반 파일 첨부 저장 승인과 저장 거부 경로는 `filenames`, `attachment_names`, `canceled_target`이 실행 컨텍스트에 안정적으로 남지 않는 구간이 있었다.
  - `pending_attachment_execution_context()`를 추가해 pending 첨부 파일명을 `resolved_slots.filenames`, `resolved_slots.attachment_names`로 보존하고, 거부 시 `resolved_slots.canceled_target=attachment_save`를 남기도록 했다.
  - 버튼 거부 경로의 `OperationResult`와 일반 파일 버튼 승인 경로의 `handle_remember()` 결과에 `attach_execution_context_metadata()`를 적용했다.
  - 채팅 답장 승인으로 pending 첨부를 저장하는 `handle_remember()` 내부 경로도 pending 첨부 기준 실행 컨텍스트를 사용하도록 보강했다.
  - pending 첨부 저장 완료 여부 판단을 문자열 포함 검사보다 구조화 필드(`document_id`, `document_ids`, `duplicate_document_id`) 기준으로 정리했다.
  - `agent_catalog.json`의 `cancel_pending` state_outputs에 `slots.filenames`, `slots.attachment_names`를 추가해 첨부 저장 거부 결과가 카탈로그 계약을 통과하도록 했다.
  - `test_assistant_bot_keeps_pending_attachment_for_chat_approval`을 보강하고 `test_attachment_save_rejection_preserves_pending_filename_context`를 추가해 승인/거부 모두 실제 파일명 metadata가 결과와 응답 실행 컨텍스트에 남는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_keeps_pending_attachment_for_chat_approval tests/test_bot_helpers.py::test_attachment_save_rejection_preserves_pending_filename_context tests/test_bot_helpers.py::test_confirmation_button_approves_pending_image_with_document_analysis -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_agent_registry.py -q`(`184 passed`), `python3 -m pytest -q`(`1029 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 첨부 저장 실패 경로 파일명 metadata 보강

- 작업 이름: 첨부 승인 실패/unsupported 결과도 원래 파일명을 잃지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 첨부 저장 승인 중 원본 채널이 없거나 원본 메시지를 찾지 못하거나 지원 가능한 첨부가 없는 경우, 사용자에게는 실패를 알리지만 결과 metadata에 원래 파일명이 충분히 남지 않는 경로를 확인했다.
  - `handle_pending_attachment_approval()`에서 pending 요청을 찾은 직후 파일명 기준 `ExecutionContext`를 만들고, 채널 없음/원본 메시지 조회 실패/지원 파일 없음 결과에도 `attach_execution_context_metadata()`를 적용했다.
  - 실패 결과의 `facts`, `slots`, `preserve_values`에 `filenames`와 `attachment_names`를 넣어, 내부 행동 기록과 후속 응답 작성자가 어떤 첨부 저장이 실패했는지 볼 수 있게 했다.
  - `agent_catalog.json`의 `remember` state_outputs에 `slots.filenames`, `slots.attachment_names`를 추가해 첨부 실패/저장 결과가 카탈로그 계약을 통과하도록 했다.
  - `test_pending_attachment_approval_without_channel_preserves_filename_context`와 `test_pending_attachment_approval_with_no_supported_file_preserves_filename_context`를 추가해 실패/unsupported 경로도 파일명 metadata를 보존하는지 검증했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_pending_attachment_approval_without_channel_preserves_filename_context tests/test_bot_helpers.py::test_pending_attachment_approval_with_no_supported_file_preserves_filename_context tests/test_bot_helpers.py::test_attachment_save_rejection_preserves_pending_filename_context tests/test_bot_helpers.py::test_assistant_bot_keeps_pending_attachment_for_chat_approval -q`(`4 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_agent_registry.py -q`(`186 passed`), `python3 -m pytest -q`(`1031 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답 작성 내부 metadata 비노출 계약 보강

- 작업 이름: 풍부해진 실행 metadata 중 공개 대상 단서와 내부 route 키의 경계 테스트 고정
- 진행상황: 완료
- 진행내용:
  - 최근 pending/버튼/첨부 경로에 `ExecutionContext` metadata를 많이 보강했으므로, 최종 답변 작성 모델 입력에서 내부 route 키가 사용자-facing 실행 결과로 새지 않는지 확인했다.
  - 기존 `ResponseComposer`는 내부 행동 기록을 비공개 참고로만 쓰도록 지시하고, `public_operation_result_for_response()`와 `ExecutionContext.for_response()`가 `context_link`, `linked_state_id`, `resolved_slots`, `pending_*` 같은 private route key를 제거하고 있음을 확인했다.
  - `test_response_composer_keeps_attachment_filename_but_hides_pending_route_metadata`를 추가해 첨부 pending 취소 결과에서 `filenames`, `attachment_names`, `canceled_target`은 모델 입력에 남지만, `context_link`와 `resolved_slots`는 공개 실행 결과에서 사라지는 계약을 고정했다.
  - `plan.md`에 실행 metadata가 풍부해져도 route 내부 키는 최종 답변 작성 모델 입력의 공개 실행 결과에서 제거하고, 사용자가 확인해야 하는 대상 단서는 보존한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_composer_keeps_attachment_filename_but_hides_pending_route_metadata tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context tests/test_response_composer.py::test_response_composer_treats_internal_action_context_as_hidden_reference -q`(`3 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py -q`(`81 passed`), `python3 -m pytest -q`(`1032 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 묶음 실행 결과 nested metadata 비노출 보강

- 작업 이름: OperationResult.items 내부 route metadata도 최종 답변 모델 입력에서 제거
- 진행상황: 완료
- 진행내용:
  - `public_operation_result_for_response()`가 top-level `facts`와 `slots`의 private route key는 제거하지만, 여러 하위 결과를 묶은 `items`는 그대로 전달하고 있음을 확인했다.
  - 새 에이전트나 묶음 저장 결과가 `items[].facts.resolved_slots`, `items[].slots.linked_state_id` 같은 중첩 route metadata를 포함하면 최종 답변 작성 모델 입력에 내부 키가 노출될 수 있었다.
  - `sanitize_private_route_values()`와 `sanitize_private_route_items()`를 추가해 dict/list/tuple 내부의 `context_link`, `linked_state_id`, `resolved_slots`, `pending_*` 같은 private route key를 재귀적으로 제거하도록 했다.
  - `test_response_private_route_keys_are_filtered_from_nested_items`를 추가해 nested item 안의 파일명과 문서 ID는 보존하면서 내부 route key는 제거되는 계약을 고정했다.
  - `plan.md`에 묶음 실행 결과의 `items` 안에 들어간 중첩 facts/slots도 같은 공개/비공개 필터를 통과해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_nested_items tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context tests/test_response_composer.py::test_response_composer_keeps_attachment_filename_but_hides_pending_route_metadata -q`(`3 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py -q`(`82 passed`), `python3 -m pytest -q`(`1033 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답 작성 실패 fallback metadata 정리

- 작업 이름: ResponseComposer 실패 시 fallback_text의 내부 route key 노출 방지
- 진행상황: 완료
- 진행내용:
  - `ResponseComposer`가 OpenAI 응답 작성에 실패하면 원래 `fallback_text`를 그대로 반환하고 있어, 새 에이전트가 실수로 fallback 문장에 `context_link`, `linked_state_id`, `resolved_slots` 같은 내부 키를 넣으면 사용자에게 노출될 수 있음을 확인했다.
  - `sanitize_private_route_text()`를 추가해 fallback 반환 전 private route key의 `key=value`, `key: value`, JSON-like 표현을 제거하도록 했다.
  - 일반적인 자연어 fallback은 그대로 유지하고, 내부 metadata가 섞인 fallback만 정리되도록 기존 fallback 테스트와 새 테스트를 함께 검증했다.
  - `test_response_composer_sanitizes_private_route_metadata_from_failed_fallback`을 추가해 composer 실패 시에도 사용자에게 필요한 자연어 내용은 보존되고 내부 route key는 제거되는 계약을 고정했다.
  - `plan.md`에 최종 답변 작성 모델 호출이 실패해 fallback 문장을 반환해야 할 때도 private route key를 정리해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_composer_falls_back_to_raw_response tests/test_response_composer.py::test_response_composer_sanitizes_private_route_metadata_from_failed_fallback -q`(`2 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py -q`(`83 passed`), `python3 -m pytest -q`(`1034 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 metadata only fallback 안전 문구 대체

- 작업 이름: fallback sanitization 후 빈 값이 되면 원문 대신 안전 문구 반환
- 진행상황: 완료
- 진행내용:
  - `sanitize_private_route_text()`가 private route key를 제거한 뒤 빈 문자열이 되면 원문을 되돌리고 있어, fallback_text 전체가 내부 metadata뿐인 경우 노출 방지 목적이 깨질 수 있음을 확인했다.
  - 정리 후 빈 값이면 `처리 결과를 확인했어요.`라는 안전한 일반 문구를 반환하도록 수정했다.
  - `test_response_composer_replaces_all_private_route_fallback_with_safe_text`를 추가해 `context_link`, `linked_state_id`, `resolved_slots`만 들어 있는 fallback이 원문으로 되돌아가지 않는 계약을 고정했다.
  - 기존 `test_response_composer_falls_back_to_raw_response`와 함께 검증해 정상 자연어 fallback은 그대로 유지되는지 확인했다.
  - `plan.md`에 fallback 문장이 private route metadata만으로 구성되어 정리 후 빈 값이 되면 원문을 되돌리지 않고 안전한 일반 문구로 대체해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_composer_falls_back_to_raw_response tests/test_response_composer.py::test_response_composer_sanitizes_private_route_metadata_from_failed_fallback tests/test_response_composer.py::test_response_composer_replaces_all_private_route_fallback_with_safe_text -q`(`3 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py -q`(`84 passed`), `python3 -m pytest -q`(`1035 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route/debug 키 비공개 응답 계약 보강

- 작업 이름: 내부 행동 기록 키와 응답 비공개 키 목록의 불일치 방지
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록에 남기는 `INTERNAL_ACTION_CONTEXT_KEYS`와 최종 응답 작성에서 숨기는 `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`가 별도 목록으로 관리되고 있어, 새 route/debug 키가 추가될 때 공개 응답으로 새어 나갈 수 있는지 점검했다.
  - `validation_reason`은 라우팅 검증 내부 사유로 쓰이는 경우가 많아 내부 행동 기록에는 보존하되 최종 응답 공개 실행 결과에서는 숨기는 쪽이 안전하다고 판단했다.
  - `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`에 `validation_reason`을 추가했다.
  - `test_internal_route_context_keys_are_private_for_response_composer`를 추가해 내부 행동 기록 키 중 `pending_*` 제어 키, `linked_*`, `cancelled_*`, `context_link`, `link_confidence`, `resolved_slots`, `validation_reason`이 응답 비공개 키 목록에 포함되도록 고정했다.
  - 사용자에게 보여도 되는 `pending_query`와 `unsupported_reason`은 비공개 키로 묶지 않도록 테스트에 명시했다.
  - `plan.md`에 내부 행동 기록에서 보존하는 route/debug 성격 키와 최종 응답에서 숨기는 private key 목록을 함께 관리해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_internal_route_context_keys_are_private_for_response_composer tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context tests/test_response_composer.py::test_response_composer_sanitizes_private_route_metadata_from_failed_fallback -q`(`3 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_response_composer.py -q`(`85 passed`), `python3 -m pytest -q`(`1036 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 에이전트 실행 컨텍스트 내부 진단값 정제

- 작업 이름: 라우터용 내부 행동 기록과 전문 에이전트용 실행 힌트 분리
- 진행상황: 완료
- 진행내용:
  - `ExecutionContext.for_agent()`가 기존에는 `internal_action_context`, `linked_state.to_prompt_text()`, `resolved_slots`를 거의 그대로 전달해 `route_context`, `validation_context`, `linked_state_id`, `pending_original_text`, 중첩 `resolved_slots` 같은 라우터 진단값이 전문 에이전트 입력에 노출될 수 있음을 확인했다.
  - 라우터는 원본 내부 행동 기록을 계속 볼 수 있도록 `for_router()`를 유지하고, 전문 에이전트에는 `agent_safe_internal_action_context()`, `agent_safe_turn_state_context()`, `agent_safe_resolved_slots()`를 거친 정제 컨텍스트만 전달하도록 수정했다.
  - 정제된 내부 행동 기록은 위치, 의도, 상태, 근거, 연결 주의, 검증 주의, 가능한 행동, 재시도 가능 여부, 대상 단서만 남기고 agent명, model명, raw `route_context`, raw `validation_context`를 제거한다.
  - 연결된 이전 작업 상태는 state id, conversation/channel id, intent, status, subject, summary, 안전한 slots/artifacts, available actions, retryable만 남기도록 정리했다.
  - `test_execution_context_agent_context_hides_raw_route_diagnostics_but_keeps_target_hints`를 추가해 라우터 컨텍스트에는 원본 진단값이 남고, 에이전트 컨텍스트에는 작업 대상과 가능한 행동만 남는 계약을 고정했다.
  - 기존 `test_execution_context_response_hides_private_route_metadata_from_resolved_slots`와 `test_build_execution_context_includes_internal_action_logs_for_agents_and_response`를 새 에이전트 컨텍스트 정제 기준에 맞춰 갱신했다.
  - `plan.md`에 라우터, 전문 에이전트, 최종 응답 컨텍스트의 노출 범위를 단계별로 분리해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_response_hides_private_route_metadata_from_resolved_slots tests/test_response_composer.py::test_execution_context_agent_context_hides_raw_route_diagnostics_but_keeps_target_hints tests/test_context_builder.py::test_build_execution_context_includes_internal_action_logs_for_agents_and_response tests/test_context_builder.py::test_build_execution_context_links_cross_location_turn_state_for_same_user -q`(`4 passed`)와 `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_agent_registry.py -q`(`144 passed`)를 통과했다.
  - 줄 길이 정리 후 `python3 -m pytest tests/test_response_composer.py::test_execution_context_agent_context_hides_raw_route_diagnostics_but_keeps_target_hints -q`(`1 passed`), `python3 -m pytest -q`(`1037 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 중첩 라우터 슬롯 private key 필터링 보강

- 작업 이름: `ExecutionContext.resolved_slots` 안의 nested route/debug metadata 제거
- 진행상황: 완료
- 진행내용:
  - 실행 결과 공개 필터는 이미 dict/list/tuple 내부를 재귀적으로 정리하지만, `ExecutionContext.for_agent()`와 `ExecutionContext.for_response()`의 `resolved_slots` 필터는 top-level key만 제거하고 있음을 확인했다.
  - 새 에이전트가 후보 목록이나 target 객체 안에 `linked_state_id`, `context_link`, `resolved_slots`, `pending_resolved_slots` 같은 내부 제어값을 중첩해서 넣으면 에이전트/응답 컨텍스트에 남을 수 있었다.
  - `route_safe_values()`를 추가하고 `response_safe_resolved_slots()`와 `agent_safe_resolved_slots()`가 이 재귀 필터를 사용하도록 수정했다.
  - `test_execution_context_filters_nested_private_route_metadata_from_safe_slots`를 추가해 nested dict/list 안의 private route key는 제거하면서 `task_id`, 제목 같은 안전한 대상 단서는 보존하는 계약을 고정했다.
  - `plan.md`에 private route key 필터가 top-level뿐 아니라 dict/list/tuple 내부까지 적용되어야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_filters_nested_private_route_metadata_from_safe_slots tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context tests/test_response_composer.py::test_execution_context_agent_context_hides_raw_route_diagnostics_but_keeps_target_hints -q`(`3 passed`)와 `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py -q`(`87 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1038 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 기록 문자열 세그먼트 private key 정리

- 작업 이름: `slots=`/`artifacts=` 문자열 안의 route/debug metadata 제거
- 진행상황: 완료
- 진행내용:
  - `ExecutionContext.resolved_slots`는 재귀 필터를 통과하지만, 내부 행동 기록의 `slots=...`, `artifacts=...`, `target_hints=...` 같은 문자열 세그먼트는 `_humanize_internal_values()`만 거쳐 private key가 섞일 수 있음을 확인했다.
  - `internal_safe_segment()`를 추가해 문자열 세그먼트를 `ast.literal_eval()`로 파싱할 수 있으면 `route_safe_values()` 재귀 필터를 적용하고, 파싱할 수 없는 경우 `sanitize_private_route_segment_text()`로 private route key 패턴을 제거하도록 했다.
  - 에이전트용 `agent_safe_internal_action_context()`와 응답용 `response_safe_internal_action_context()` 모두 이 세그먼트 sanitizer를 사용하도록 수정했다.
  - `test_execution_context_filters_private_route_metadata_from_internal_action_segments`를 추가해 `slots`/`artifacts` 문자열 안의 `pending_original_text`, `linked_state_id`, `resolved_slots`는 제거되고 `task_id`, `task_title`, title 같은 작업 단서는 남는지 검증했다.
  - `plan.md`에 내부 행동 기록 문자열 세그먼트도 literal 파싱 또는 패턴 제거를 거쳐 에이전트/응답용 참고 정보로 전달해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_response_composer.py::test_execution_context_filters_private_route_metadata_from_internal_action_segments tests/test_response_composer.py::test_response_composer_treats_internal_action_context_as_hidden_reference tests/test_response_composer.py::test_execution_context_agent_context_hides_raw_route_diagnostics_but_keeps_target_hints tests/test_response_composer.py::test_execution_context_filters_nested_private_route_metadata_from_safe_slots -q`(`4 passed`)와 `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py -q`(`90 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1039 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 공개 OperationResult 전체 필드 private key 정리

- 작업 이름: 최종 응답 작성 모델 입력에 들어가는 artifacts/preserve/fallback metadata 제거
- 진행상황: 완료
- 진행내용:
  - `public_operation_result_for_response()`가 `facts`, `slots`, `items`는 private route key를 제거하지만, `artifacts`, `preserve_values`, `warnings`, `next_actions`, `subject`, `summary`, `fallback_text`는 그대로 전달하고 있음을 확인했다.
  - 새 에이전트가 내부 실행 결과나 fallback 문장에 `context_link`, `linked_state_id`, `resolved_slots`, `pending_*`를 넣으면 최종 답변 작성 모델 입력에 raw route/debug 값이 들어갈 수 있었다.
  - `public_operation_result_for_response()`에서 `artifacts`는 `items`와 같은 재귀 필터를 적용하고, 텍스트 tuple 필드(`warnings`, `next_actions`, `preserve_values`)와 `summary`, `subject`, `fallback_text`도 private route key 패턴을 제거하도록 수정했다.
  - `sanitize_private_route_text()`에 `empty_fallback` 인자를 추가하고, tuple용 `sanitize_private_route_text_tuple()`을 추가해 공개 모델 입력에서는 private metadata만 남은 값을 비우거나 안전 문구로 바꾸게 했다.
  - `test_response_private_route_keys_are_filtered_from_artifacts_and_text_fields`를 추가해 artifacts의 nested metadata와 preserve/fallback/summary/subject 문자열 metadata가 모델 입력에서 제거되는지 검증했다.
  - `plan.md`에 공개 `OperationResult`는 모든 구조화 필드가 private route key 정리를 거쳐야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_artifacts_and_text_fields tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_nested_items tests/test_response_composer.py::test_response_composer_sanitizes_private_route_metadata_from_failed_fallback tests/test_response_composer.py::test_response_composer_replaces_all_private_route_fallback_with_safe_text -q`(`4 passed`)와 `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py -q`(`89 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1040 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - turn state 저장용 slots/artifacts private key 정리

- 작업 이름: 다음 턴 작업 후보 저장값에서 route/debug metadata 제거
- 진행상황: 완료
- 진행내용:
  - 최종 응답 모델 입력은 정리했지만, `record_turn_state()`가 저장하는 `slots`와 `artifacts`에는 `context_link`, `linked_state_id`, `resolved_slots`, `pending_*` 같은 내부 metadata가 남을 수 있음을 확인했다.
  - 일반 완료/실패 turn state 후보는 다음 턴 라우터가 작업 대상을 찾기 위한 자료이므로, 내부 연결 제어값이 아니라 실제 대상 단서만 남기는 것이 더 안전하다고 판단했다.
  - `sanitized_turn_state_slots()`가 일반 상태에서 `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`와 `PENDING_TURN_STATE_SLOT_KEYS`를 제거하고, 값 내부도 `route_safe_values()`로 재귀 정리하도록 수정했다.
  - `turn_state_artifacts_from_result()`도 explicit/inferred artifact 병합 후 `route_safe_values()`를 통과해 artifacts 안의 nested private route key를 제거하도록 수정했다.
  - `needs_input`, `confirm_required`, `clarify` 상태는 pending 복원에 필요한 key가 있으므로 기존처럼 pending slots를 유지한다.
  - `test_sanitized_turn_state_slots_removes_private_route_metadata_for_completed_state`와 `test_turn_state_artifacts_from_result_removes_private_route_metadata`를 추가했다.
  - pending memory capture 완료 상태 테스트를 갱신해 일반 저장 완료 turn state에는 `context_link`와 `resolved_slots`가 남지 않고, 실행 컨텍스트와 내부 로그에는 실제 메모 대상이 보존되는지 확인했다.
  - `plan.md`에 일반 turn state 저장값은 실제 작업 대상만 남기고 pending 확인 상태에서만 pending key를 유지한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_sanitized_turn_state_slots_removes_private_route_metadata_for_completed_state tests/test_bot_helpers.py::test_turn_state_artifacts_from_result_removes_private_route_metadata tests/test_bot_helpers.py::test_turn_state_artifacts_from_result_merges_explicit_and_inferred_artifacts -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py::test_on_message_records_pending_memory_capture_as_context_state_and_internal_log tests/test_bot_helpers.py::test_sanitized_turn_state_slots_removes_private_route_metadata_for_completed_state tests/test_bot_helpers.py::test_turn_state_artifacts_from_result_removes_private_route_metadata -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py -q`(`191 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1042 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - turn state 저장 경로 sanitizer 계약 고정

- 작업 이름: Discord/CLI 런타임 turn state 저장 경로의 sanitizer 사용 보장
- 진행상황: 완료
- 진행내용:
  - `assistant_bot/bot.py`와 `assistant_bot/cli.py`의 실제 런타임 `turn_states.add()` 호출을 점검해, Discord 일반 메시지/버튼 후속 실행과 CLI 실행 경로가 모두 `sanitized_turn_state_slots()`와 `turn_state_artifacts_from_result()`를 거쳐 저장하고 있음을 확인했다.
  - 새 우회 저장 경로가 생기면 raw `OperationResult.slots`나 raw `OperationResult.artifacts`를 직접 저장할 위험이 있으므로 source-level 회귀 테스트를 추가했다.
  - `test_runtime_turn_state_writes_use_sanitized_slots_and_artifacts`를 추가해 `assistant_bot/bot.py`, `assistant_bot/cli.py`의 `turn_states.add()` 호출이 sanitized local `slots`와 `turn_state_artifacts_from_result()`를 사용하는지 검증한다.
  - `plan.md`에 turn state를 저장할 수 있는 모든 런타임 경로는 같은 sanitizer를 통과해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_runtime_turn_state_writes_use_sanitized_slots_and_artifacts tests/test_bot_helpers.py::test_sanitized_turn_state_slots_removes_private_route_metadata_for_completed_state tests/test_bot_helpers.py::test_turn_state_artifacts_from_result_removes_private_route_metadata -q`(`3 passed`)와 `python3 -m pytest tests/test_agent_registry.py tests/test_bot_helpers.py -q`(`190 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1043 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - legacy turn state 출력 단계 private key 정리

- 작업 이름: 과거 저장된 raw turn state metadata가 라우터 컨텍스트로 새지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 새 turn state 저장 경로는 sanitizer를 통과하지만, 과거 버전에서 이미 DB에 저장된 `context_link`, `linked_state_id`, `resolved_slots`, `pending_*`가 라우터 컨텍스트에 출력될 수 있음을 확인했다.
  - `build_turn_state_context()`가 turn state의 `slots`와 `artifacts`를 출력할 때만 `route_safe_values()`를 적용하도록 수정했다.
  - 처음에는 공통 `sanitize_turn_state_context_value()`에 무조건 필터를 적용해 내부 행동 로그의 `route_context`/`validation_context`까지 제거되는 문제가 테스트에서 드러났다.
  - 이를 `filter_private_route` 옵션으로 분리해, turn state 후보 출력에는 private key 필터를 적용하고 내부 행동 로그에는 라우터가 파싱해야 하는 raw route/validation context를 유지하도록 고쳤다.
  - 전체 테스트 중 pending context 승인 CLI 미리보기에서, `needs_input`/`clarify` 상태의 pending key까지 출력 필터가 제거해 승인 복원이 실패하는 문제를 추가로 확인했다.
  - 저장 단계와 같은 규칙으로 `needs_input`, `confirm_required`, `clarify` 상태는 출력 단계에서도 pending key를 유지하고, 일반 완료/실패 상태에만 private route key 필터를 적용하도록 조정했다.
  - `test_turn_state_context_filters_private_route_metadata_from_legacy_state_values`를 추가해 legacy state의 nested private route key는 출력에서 제거되고 `task_id`, `task_title`, 제목 같은 대상 단서는 남는지 검증했다.
  - `plan.md`에 legacy turn state 출력 필터는 turn state slots/artifacts에만 적용하고, 내부 행동 로그의 route/validation context는 라우터 판단 자료로 유지한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_context_builder.py::test_turn_state_context_filters_private_route_metadata_from_legacy_state_values tests/test_context_builder.py::test_build_router_context_internal_route_context_is_parseable_by_router tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router tests/test_context_builder.py::test_build_router_context_keeps_current_execution_result_when_validation_logs_fill_limit -q`(`4 passed`)와 `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_router_heuristics.py -q`(`228 passed`)를 통과했다.
  - pending 예외 조정 후 `python3 -m pytest tests/test_cli.py::test_preview_route_details_allows_exact_pending_context_approval tests/test_context_builder.py::test_turn_state_context_filters_private_route_metadata_from_legacy_state_values -q`(`2 passed`)와 `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_router_heuristics.py tests/test_cli.py::test_preview_route_details_allows_exact_pending_context_approval -q`(`229 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1044 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 짧은 재시도 후속 요청 라우팅 보강

- 작업 이름: `아 다시해봐` 같은 자연어 재시도 표현의 이전 상태 연결
- 진행상황: 완료
- 진행내용:
  - 사용자가 `원주 날씨 어때` 요청 실패 뒤 `아 다시해봐`처럼 짧게 말하면, 라우터 fallback이 이전 `weather` 상태의 `retryable=True`와 `actions=retry`를 보고도 일반 대화로 분류하는 문제를 재현했다.
  - 실패 원인은 `다시해봐` 자체는 retry action으로 인식되지만, 앞의 감탄사 `아`가 남아 action-only 후속 요청 판정이 실패하는 것이었다.
  - `is_action_only_follow_up()`의 filler 표현에 `아`, `어`, `음`, `흠`을 추가해 한국어 대화에서 흔한 짧은 감탄사/머뭇거림을 제거한 뒤 후속 action 여부를 판단하도록 수정했다.
  - 위험한 action-only 요청(`삭제`, `수정`, `복구` 등)은 기존 `is_risky_action_only_follow_up()` 경로를 유지해, 감탄사가 붙어도 대상 확인 없이 자동 실행되지 않게 했다.
  - `test_context_routing_matrix`에 `brief_same_location_weather_retry_uses_failed_weather_state` 케이스를 추가해 `아 다시해봐`가 같은 위치의 실패한 `weather` 상태 7번에 `context_link=retry`, `resolved_slots.location=원주`로 연결되는 계약을 고정했다.
  - `plan.md`에 짧은 감탄사/머뭇거림이 붙은 재시도 표현도 action-only 후속 요청으로 보되, 위험 action-only 요청은 자동 실행하지 않는 원칙을 문서화했다.
  - `python3 -m pytest 'tests/test_context_routing_matrix.py::test_context_routing_matrix[brief_same_location_weather_retry_uses_failed_weather_state]' -q`(`1 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`152 passed`), `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_router_heuristics.py -q`(`477 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1045 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - filler 포함 위험 action-only 과연결 방지 고정

- 작업 이름: `아 삭제해줘` 같은 짧은 위험 요청의 자동 연결 차단
- 진행상황: 완료
- 진행내용:
  - 짧은 감탄사/머뭇거림을 action-only 후속 요청 판별에서 제거하도록 보강한 뒤, 같은 규칙이 삭제/수정/복구 같은 위험 작업까지 최근 단일 후보에 과하게 연결할 가능성을 점검했다.
  - `single_task_filler_risky_delete_does_not_use_recent_task` 매트릭스 케이스를 추가해 `아 삭제해줘`가 최근 `manage_task` 후보에 자동 연결되지 않고 기존 독립 삭제 intent(`delete_memory`, `context_link=none`)로 남는지 검증했다.
  - `test_validate_route_context_link_blocks_filler_prefixed_risky_action_only_link`를 추가해 모델이 `아 삭제해`, `음 수정해줘`, `어 복구해줘`를 실수로 linked task 상태에 연결하더라도 실행 전 검증이 `linked_state_id`와 `resolved_slots`를 제거하는지 고정했다.
  - `tests/test_route_validation.py`에 `pytest` import를 추가해 새 parametrized test를 사용할 수 있게 했다.
  - `plan.md`에 filler가 붙은 위험 action-only 문장도 명시 대상 없이는 자동 연결하지 않고, 모델 실수는 route validation에서 제거해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest 'tests/test_context_routing_matrix.py::test_context_routing_matrix[single_task_filler_risky_delete_does_not_use_recent_task]' 'tests/test_route_validation.py::test_validate_route_context_link_blocks_filler_prefixed_risky_action_only_link' -q`(`4 passed`)와 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`312 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1049 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 filler 재시도 확인 라우팅 고정

- 작업 이름: `아 다시해봐`가 다른 채팅 위치 작업을 바로 실행하지 않도록 보장
- 진행상황: 완료
- 진행내용:
  - 같은 위치의 실패한 날씨 후보에는 `아 다시해봐`를 `context_link=retry`로 연결해야 하지만, 후보가 다른 채팅 위치에 있으면 사용자 의도와 위치 전환 여부를 먼저 확인해야 한다.
  - 현재 fallback 동작을 점검해 `아 다시해봐`와 `원주 다시해봐`는 다른 위치의 `원주 날씨` 실패 후보에 `context_link=clarify`로 연결되고, `서울 날씨 어때`처럼 새 지역 요청은 `context_link=none`으로 유지되는지 확인했다.
  - `cross_location_filler_weather_retry_requires_confirmation` 매트릭스 케이스를 추가해 다른 위치의 실패한 weather 후보가 있을 때 `아 다시해봐`가 바로 실행되지 않고 `linked_state_id=21`, `resolved_slots.location=원주`, `context_link=clarify`로 확인 대기를 만드는 계약을 고정했다.
  - `plan.md`에 filler 포함 재시도 표현이라도 다른 채팅 위치 후보를 가리키면 “여기서 이어갈까요?” 확인을 먼저 만들어야 한다는 원칙을 문서화했다.
  - `python3 -m pytest 'tests/test_context_routing_matrix.py::test_context_routing_matrix[cross_location_filler_weather_retry_requires_confirmation]' -q`(`1 passed`)와 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_router_heuristics.py -q`(`482 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1050 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 확인 승인 후 retry 컨텍스트 복원

- 작업 이름: cross-location 확인 승인 뒤 원래 재시도 작업 실행 컨텍스트 보존
- 진행상황: 완료
- 진행내용:
  - 다른 위치 작업에 대해 `아 다시해봐`가 먼저 `context_link=clarify` 확인을 만들더라도, 사용자가 `응`이라고 승인한 뒤에는 원래 `weather` 재시도 intent, `retry` 링크, `location=원주` 슬롯을 잃지 않아야 한다.
  - `cross_location_weather_retry_approval_restores_pending_retry_context` 매트릭스 케이스를 추가해 pending 확인 상태의 `pending_intent=weather`, `pending_context_link=retry`, `pending_resolved_slots.location=원주`, `pending_original_text=아 다시해봐`가 승인 답변 후 복원되는지 검증했다.
  - 첫 실행에서 fallback은 `retry`를 잘 복원했지만, 매트릭스의 실행 전 검증 단계가 승인 후 cross-location 허용 조건을 반영하지 않아 다시 `clarify`로 되돌리는 문제를 발견했다.
  - 테스트 harness에 일반 규칙을 추가했다. 긍정 승인 문장이고, route가 `continue/retry/modify` 자동 실행 링크이며, linked state가 현재 위치와 다른 경우에는 승인 후 검증으로 보고 `allow_cross_location=True`를 넘긴다.
  - 이 변경은 테스트 harness의 실제 운영 조건 반영이며, route validation 자체의 사용자/호환성 검증은 그대로 유지한다.
  - `plan.md`에 다른 위치 확인 질문 승인 후에는 pending 상태의 intent/link/slots/original text를 복원하고, 이미 확인된 cross-location linked state를 다시 clarify로 되돌리지 않는 원칙을 문서화했다.
  - `python3 -m pytest 'tests/test_context_routing_matrix.py::test_context_routing_matrix[cross_location_weather_retry_approval_restores_pending_retry_context]' -q`(`1 passed`)와 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_router_heuristics.py -q`(`483 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1051 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 런타임 cross-location 승인 검증 계약 고정

- 작업 이름: Discord/CLI 실행 경로의 `allow_cross_location` 사용 조건 보장
- 진행상황: 완료
- 진행내용:
  - 매트릭스 테스트가 승인 후 cross-location 실행 조건을 반영하도록 보강한 뒤, 실제 Discord 일반 메시지 경로와 CLI 실행/preview 경로도 같은 계약을 지키는지 소스에서 점검했다.
  - `assistant_bot/bot.py`의 일반 메시지 처리 경로와 `assistant_bot/cli.py`의 로컬 실행 및 route preview 경로는 `matching_pending_context_approval_state()`로 pending 승인 상태를 확인하고, `route_with_pending_context_original_text()`로 pending 슬롯을 복원한 뒤, `pending_context_approval_state is not None`일 때만 `allow_cross_location=True`를 넘기고 있음을 확인했다.
  - `test_runtime_route_validation_allows_cross_location_only_after_pending_context_approval`를 추가해 `bot.py`에는 해당 승인 게이트가 1곳, `cli.py`에는 2곳 존재하고, pending approval matching과 pending context 복원 호출이 함께 유지되는지 고정했다.
  - 이 계약은 새 런타임 경로가 추가될 때 pending 승인 없이 cross-location 자동 실행 허용이 넓어지는 일을 막기 위한 source-level 회귀 테스트다.
  - `plan.md`에는 이미 Discord 일반 메시지 경로, CLI 로컬 실행 경로, CLI route preview 경로가 pending context 승인 상태가 확인된 경우에만 `allow_cross_location=True`로 실행 전 검증을 호출해야 한다는 원칙이 반영되어 있음을 확인했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_runtime_route_validation_allows_cross_location_only_after_pending_context_approval 'tests/test_context_routing_matrix.py::test_context_routing_matrix[cross_location_weather_retry_approval_restores_pending_retry_context]' -q`(`2 passed`)와 `python3 -m pytest tests/test_agent_registry.py tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_cli.py::test_preview_route_details_allows_exact_pending_context_approval -q`(`373 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1052 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 승인 복원 route 내부 기록 보존

- 작업 이름: 승인 후 복원된 cross-location retry 컨텍스트의 내부 로그 단서 보장
- 진행상황: 완료
- 진행내용:
  - 사용자가 다른 위치 작업 확인 질문에 승인한 뒤 실행되는 route가 다음 턴 라우터에 도움이 되려면, 실제 실행 결과 로그뿐 아니라 route validation 요약에도 복원된 intent, context_link, linked_state_id, resolved_slots, 원래 사용자 문장 단서가 남아야 한다.
  - 기존 `test_record_internal_action_result_logs_cross_location_retry_approval_context`가 실행 결과 내부 로그에 `context_link=retry`, `linked_state_id=21`, `linked_intent=weather`, `location=원주`, `pending_original_text=아 다시해봐`를 남기고, 라우터 fallback이 이 로그에서 안전한 slots/actions/retryable 값을 복원할 수 있음을 확인했다.
  - `test_route_validation_summary_preserves_pending_cross_location_retry_context`를 추가해 pending 승인 복원으로 route가 `chat/none`에서 `weather/retry`로 바뀔 때 route validation 요약에도 `intent chat->weather`, `context_link none->retry`, `linked_state_id None->21`, `location=원주`, `pending_original_text=아 다시해봐`, `validation_context`가 남는지 고정했다.
  - `plan.md`에 pending 승인으로 복원된 route가 실행되면 내부 행동 기록과 route validation 요약에도 다음 턴 라우터가 참고할 수 있는 안전한 실행 단서가 남아야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_logs_cross_location_retry_approval_context tests/test_bot_helpers.py::test_route_validation_summary_preserves_pending_cross_location_retry_context tests/test_context_builder.py tests/test_agent_registry.py::test_runtime_route_validation_allows_cross_location_only_after_pending_context_approval -q`(`62 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1054 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 승인 validation 로그의 router context 안전 변환

- 작업 이름: 정상 승인 복원 로그가 validation guidance로 오해되지 않도록 고정
- 진행상황: 완료
- 진행내용:
  - pending 승인으로 `chat/none`에서 `weather/retry`로 복원된 route validation 로그가 router context에 들어갈 때, 자동 연결 제거나 확인 전환 같은 경고성 `validation_guidance`로 해석되면 다음 턴 라우터가 불필요하게 실행을 보류할 수 있음을 점검했다.
  - `test_build_router_context_pending_approval_validation_log_is_not_guidance`를 추가했다.
  - 이 테스트는 `route_validation_summary()`로 만든 정상 승인 복원 로그가 router context에 `validation_context`로 남고, `after.linked_state_id=21`, `after.context_link=retry`, 안전한 `resolved_slots.location=원주`가 파싱되는지 확인한다.
  - 동시에 `validation_guidance=-`, `target_hints=-`를 확인해 이 로그가 자동 연결 제거/확인 전환 경고나 대상 힌트로 오염되지 않도록 고정했다.
  - route validation snapshot은 `pending_original_text`를 제거하고 실제 실행 슬롯만 보존하므로, router context 파싱 결과는 `location=원주`만 남기고 pending/debug 값은 다음 실행 대상 슬롯으로 복원하지 않는다.
  - `plan.md`에 정상 승인 복원 route validation 로그는 `validation_guidance`를 만들지 않고 정상 승인 실행 기록으로만 참고해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router tests/test_context_builder.py::test_build_router_context_pending_approval_validation_log_is_not_guidance -q`(`2 passed`)와 `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py::test_route_validation_summary_preserves_pending_cross_location_retry_context tests/test_bot_helpers.py::test_record_internal_action_result_logs_cross_location_retry_approval_context -q`(`62 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1056 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 검증 경고보다 최신 정상 실행 기록 우선

- 작업 이름: 오래된 route validation 경고가 최신 정상 route를 계속 막지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `internal_validation_removed_state_ids()`와 `internal_validation_clarified_state_ids()`가 router context 안의 모든 validation 로그를 누적해서 읽고 있어, 오래된 “자동 연결 제거”/“자동 실행 대신 확인” 경고가 같은 state의 최신 정상 실행 기록 뒤에도 계속 남을 수 있음을 확인했다.
  - 내부 행동 기록은 오래된 로그가 먼저, 최신 로그가 나중에 출력되므로 라인 순서대로 읽으면서 같은 `linked_state_id`에 대해 이후 `route_context.context_link`가 `continue/retry/modify`인 정상 실행 기록이 나오면 기존 removed/clarified 경고를 해제하도록 수정했다.
  - `successful_route_context_linked_state_id()`를 추가해 내부 행동 기록의 `route_context`에서 정상 실행 링크와 linked state id를 추출하게 했다.
  - `test_router_validation_removed_state_is_cleared_by_later_successful_route_context`, `test_router_validation_removed_state_survives_when_removal_is_latest`, `test_router_validation_clarified_state_is_cleared_by_later_successful_route_context`를 추가했다.
  - 매트릭스 테스트 harness도 운영 경로와 맞췄다. pending context 승인이 확인된 경우에만 `agent_text_for_route()`로 원래 요청을 검증 텍스트로 사용하고, 후보 선택/교정 답변은 현재 선택 문장을 검증 텍스트로 유지한다.
  - `plan.md`에 같은 state_id에 대한 오래된 validation 경고와 최신 정상 실행 기록이 함께 있으면 최신 정상 실행 기록이 우선해야 한다는 recency 원칙을 문서화했다.
  - `python3 -m pytest tests/test_router_agent.py::test_router_validation_removed_state_is_cleared_by_later_successful_route_context tests/test_router_agent.py::test_router_validation_removed_state_survives_when_removal_is_latest tests/test_router_agent.py::test_router_validation_clarified_state_is_cleared_by_later_successful_route_context tests/test_router_agent.py::test_router_parses_internal_validation_clarified_state_ids -q`(`4 passed`)와 `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`338 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1062 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 최신 정상 route_context의 fallback 차단 해제 회귀 테스트

- 작업 이름: 오래된 검증 경고가 fallback 라우팅을 계속 막지 않도록 통합 테스트 보강
- 진행상황: 완료
- 진행내용:
  - 내부 로그 파서 단위에서는 최신 정상 `route_context`가 오래된 removed/clarified 경고를 해제하지만, 실제 `context_aware_fallback_route()` 후보 선택에서도 같은 원칙이 적용되는지 추가로 점검했다.
  - removed 경고 해제 fallback 테스트가 이미 들어가 있음을 확인하고, 대칭적으로 clarified 경고가 오래되었을 때 최신 정상 task 실행 기록이 있으면 `그거 완료했어`를 다시 확인 질문으로 돌리지 않고 원래 `manage_task/continue` 실행으로 연결하는 테스트를 추가했다.
  - `test_router_fallback_reuses_state_when_later_successful_route_context_clears_clarify_warning`를 추가해 `state_id=31`, `task_id=9`가 최신 정상 `route_context`로 확인되면 오래된 “자동 실행 대신 확인” 경고가 후보 연결을 막지 않는 계약을 고정했다.
  - `plan.md`에 이 recency 해제가 내부 로그 파서뿐 아니라 deterministic fallback 라우팅의 후보 차단/확인 전환 판단에도 적용되어야 한다고 명시했다.
  - 추가한 테스트와 기존 removed 해제 테스트를 각각 단독 실행해 `2 passed`를 확인했다.
  - 관련 묶음 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`340 passed`)를 통과했다.
  - 전체 검증 중 pending 승인 새 요청 차단 케이스가 일시적으로 실패했으나, 현재 코드 상태에서 해당 6개 회귀 케이스를 재실행해 `6 passed`를 확인했고 전체 재검증도 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1064 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 최신 실행 결과 내부 로그 보존

- 작업 이름: 현재 위치 로그가 많아도 cross-location 실행 결과 1개를 컨텍스트에 유지
- 진행상황: 완료
- 진행내용:
  - 같은 사용자 다른 위치 맥락은 자동 실행 근거가 아니라 확인 질문의 배경 근거지만, 사용자가 위치를 바꿔 “그거 다시해봐”, “아까 하던 거 이어서”라고 말하면 이전 위치의 최신 실행 결과가 subject, slots, actions, retryable 복원에 필요하다.
  - 기존 내부 행동 기록 선택 로직은 현재 위치 로그를 우선 보존하고 최신 현재 route validation/result를 고정했지만, 현재 위치 일반 로그가 많은 경우 다른 위치의 최신 `*:result`가 제한에 밀려 사라질 수 있었다.
  - `internal_action_required_rows()`에 최신 cross-location 실행 결과를 required row로 추가해, 같은 사용자 다른 위치의 최신 실행 결과 1개는 현재 위치 로그가 많아도 컨텍스트에 남도록 했다.
  - `test_build_router_context_keeps_latest_cross_location_execution_result_when_current_logs_fill_limit`를 추가해 현재 위치 router 로그가 10개 있어도 DM의 `weather:result` 실패 기록, `route_context`, `slots.location=원주`, `actions=retry/show_alerts`, `retryable=True`가 보존되는지 고정했다.
  - `plan.md`에 현재 위치 내부 로그가 많아도 같은 사용자 다른 위치 최신 실행 결과(`*:result`)는 최소 1개 보존한다는 원칙을 문서화했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_router_context_keeps_latest_cross_location_execution_result_when_current_logs_fill_limit -q`(`1 passed`), 주변 우선순위 테스트 3개(`3 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`343 passed`)를 통과했다.
  - 전체 검증 중 병렬 실행에서 이전 import 상태로 보이는 일시 실패가 있었으나, 실패 대표 케이스 4개와 `ruff`를 단독 재실행해 통과를 확인했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1067 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - URL 후보 pending 슬롯의 완료 상태 오염 방지

- 작업 이름: URL 후보 선택 내부 슬롯을 완료 turn state에서 명시적으로 제거
- 진행상황: 완료
- 진행내용:
  - 성공/완료 상태로 저장되는 turn state에는 실제 후속 대상 단서만 남아야 하며, 후보 선택용 `pending_*` 내부 슬롯이 남으면 다음 턴 라우터가 후보 목록 전체를 실제 작업 대상으로 오해할 수 있다.
  - 기존 공개 응답 private key 목록에는 `pending_candidate_urls`, `pending_candidate_url_titles`가 포함되어 있었지만, turn state 전용 pending key 목록에는 명시되어 있지 않아 계약이 분산되어 있었다.
  - `PENDING_TURN_STATE_SLOT_KEYS`에 `pending_candidate_urls`, `pending_candidate_url_titles`를 추가해 완료 상태 저장 시 URL 후보 선택 내부 슬롯도 명시적으로 제거되도록 했다.
  - `test_sanitized_turn_state_slots_removes_pending_url_candidate_slots_after_success`를 추가해 URL 후보 선택 완료 후에는 실제 선택된 `url`만 남고, 후보 URL 목록과 제목, `pending_original_text`가 제거되는지 고정했다.
  - `plan.md`에 URL 후보 선택용 pending 슬롯은 완료 상태 turn state에 남기지 않고, 실제 선택된 `url`/`urls`만 다음 턴 대상 단서로 남겨야 한다고 문서화했다.
  - 관련 검증으로 pending 후보 슬롯 테스트 2개(`2 passed`)와 response/private key 계약 테스트 2개(`2 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1070 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 기록 user_id 저장 계약 고정

- 작업 이름: 모든 런타임 `logs.add()` 호출에 사용자 ID 포함 강제
- 진행상황: 완료
- 진행내용:
  - 공유 채널에서 같은 `conversation_id` 안에 여러 사용자가 섞일 수 있으므로, 내부 행동 기록에 `user_id`가 빠지면 다음 턴 라우터 컨텍스트에 다른 사용자의 실행 결과가 섞일 위험이 있다.
  - 현재 소스의 `logs.add()` 호출을 AST로 점검해 누락된 `user_id` 호출이 없음을 확인했다.
  - 새 에이전트나 오케스트레이션 경로가 추가될 때 이 계약이 다시 깨지지 않도록 `test_runtime_agent_logs_always_include_user_id`를 추가했다.
  - 이 테스트는 `assistant_bot` 아래 모든 `self.logs.add(...)`와 `logs.add(...)` 호출을 검사해 `user_id` keyword가 없으면 실패한다.
  - `plan.md`에 모든 런타임 내부 행동 기록은 `user_id` 없이 저장하지 않는다는 원칙을 명시했다.
  - 관련 검증으로 source-level 런타임 계약 테스트 3개(`3 passed`)와 내부 로그 사용자 격리 컨텍스트 테스트 2개(`2 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1074 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 로그 값 구분자 오염 방지

- 작업 이름: 사용자 값 안의 로그 포맷 토큰이 라우터 파서를 속이지 않도록 정리
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록은 `status=... | summary=... | slots=...`처럼 ` | `와 `key=` 포맷을 라우터가 다시 파싱한다.
  - 사용자 입력이나 실행 결과 값 안에 ` | route_context=...`, `slots=...`, `artifacts=...` 같은 문자열이 들어오면 실제 구조화 세그먼트처럼 보일 수 있어, 내부 로그 파서와 라우터 컨텍스트가 오염될 가능성을 점검했다.
  - `compact_internal_log_value()`에서 값 안의 ` | `를 ` / `로 바꾸고, `route_context=`, `validation_context=`, `linked_state_id=`, `resolved_slots=`, `context_link=`, `slots=`, `artifacts=`, `actions=`, `retryable=`, `target_hints=`를 `:` 형태의 일반 텍스트로 치환하도록 보강했다.
  - 실제 로그 세그먼트 구분자는 `compact_internal_action_result_reason()`에서 유지하므로, 라우터가 읽어야 하는 정상 `route=...`, `slots=...`, `actions=...` 구조는 계속 파싱 가능하다.
  - `test_record_internal_action_result_sanitizes_delimiters_inside_values_for_future_context`를 추가해 summary, subject, task_title 값 안에 포맷 토큰이 있어도 내부 로그와 router context에서 가짜 `route_context=`/`slots=`/`artifacts=`로 남지 않는지 고정했다.
  - `plan.md`에 내부 행동 기록 값 안의 포맷 토큰은 일반 텍스트로 치환해야 한다는 원칙을 문서화했다.
  - 관련 검증으로 새 테스트 단독(`1 passed`), 내부 로그 주변 테스트 4개(`4 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py -q`(`184 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1075 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - runtime cross-location 승인 검증 경로 계약 고정

- 작업 이름: Discord/CLI 실행 경로의 `allow_cross_location` 승인 조건 보장
- 진행상황: 완료
- 진행내용:
  - `assistant_bot/bot.py`와 `assistant_bot/cli.py`의 실제 route validation 호출을 점검해, Discord 일반 메시지 경로와 CLI 로컬 실행/route preview 경로가 `pending_context_approval_state is not None`일 때만 `allow_cross_location=True`를 넘기고 있음을 확인했다.
  - 운영 코드에는 이미 승인 후 cross-location 실행 허용 조건이 반영되어 있었지만, 이 계약이 source-level 테스트로 고정되어 있지 않았다.
  - `test_runtime_route_validation_allows_cross_location_only_after_pending_context_approval`를 추가해 `bot.py`에는 승인 게이트가 1곳, `cli.py`에는 2곳 존재하고, 두 파일 모두 `matching_pending_context_approval_state()`와 `route_with_pending_context_original_text()`를 거친 뒤 검증하는지 확인한다.
  - 이 테스트는 새 일반 메시지/CLI 경로가 생겼을 때 pending 승인 없이 cross-location 자동 실행을 넓히거나, 승인 후 pending slots 복원을 빼먹는 회귀를 잡기 위한 소스 계약이다.
  - `plan.md`에 Discord 일반 메시지, CLI 로컬 실행, CLI route preview는 pending context 승인 상태가 확인된 경우에만 `allow_cross_location=True`를 사용해야 한다는 운영 원칙을 문서화했다.
  - `python3 -m pytest tests/test_agent_registry.py::test_runtime_route_validation_allows_cross_location_only_after_pending_context_approval 'tests/test_context_routing_matrix.py::test_context_routing_matrix[cross_location_weather_retry_approval_restores_pending_retry_context]' -q`(`2 passed`)와 `python3 -m pytest tests/test_agent_registry.py tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_cli.py::test_preview_route_details_allows_exact_pending_context_approval -q`(`373 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1052 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 승인 실행 결과 내부 로그 계약 보강

- 작업 이름: cross-location retry 승인 실행의 내부 행동 기록 보존
- 진행상황: 완료
- 진행내용:
  - pending 승인 후 route validation이 변경을 만들지 않는 정상 케이스에서는 `route_validation` 로그가 없을 수 있으므로, 실제 실행 결과 내부 로그가 다음 턴 라우터의 주요 보조 신호가 된다.
  - `test_record_internal_action_result_logs_cross_location_retry_approval_context`를 추가해 다른 위치 `원주 날씨` 실패 작업을 `아 다시해봐` 확인 승인으로 재시도한 결과 로그에 `context_link=retry`, `linked_state_id=21`, `linked_intent=weather`, `linked_subject=원주 날씨 조회`, `resolved_slots.location=원주`, `pending_original_text=아 다시해봐`가 남는지 검증했다.
  - 같은 테스트에서 `internal_action_context_by_linked_state()`가 내부 로그를 다시 파싱할 때는 `location=원주`, 실행 가능 action, `retryable=True`처럼 실제 후속 실행에 필요한 안전 값만 복원하고, `pending_original_text`는 실행 슬롯으로 넘기지 않는지 확인했다.
  - 기존 `test_route_validation_summary_preserves_pending_cross_location_retry_context`와 함께 route validation 요약도 pending 승인으로 복원된 intent/link/slots/original text를 구조화해서 남기는지 재확인했다.
  - `plan.md`의 내부 행동 기록 원칙을 갱신해 로그 원문에는 승인 추적 단서를 남기되, 파싱/에이전트/응답 단계에서는 pending/debug 값을 정제한다는 기준을 명확히 했다.
  - `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_logs_cross_location_retry_approval_context tests/test_bot_helpers.py::test_record_internal_action_result_logs_execution_context_link tests/test_bot_helpers.py::test_route_validation_summary_preserves_pending_cross_location_retry_context -q`(`3 passed`)와 `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_agent_registry.py -q`(`251 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1054 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending weather retry 오승인 방지와 validation snapshot 보존

- 작업 이름: `응 서울 날씨 알려줘`를 기존 `원주` 재시도 승인으로 오해하지 않도록 고정
- 진행상황: 완료
- 진행내용:
  - pending weather retry가 있는 상태에서 사용자가 `응 서울 날씨 알려줘`라고 말하면, 문장은 긍정 승인처럼 시작하지만 실제 의도는 `서울`이라는 새 지역 날씨 요청이다.
  - 현재 동작을 점검해 이 문장이 pending `원주` retry 승인으로 처리되지 않고 `context_link=none`인 새 `weather` 요청으로 남는지 확인했다.
  - `positive_prefix_new_weather_location_not_pending_weather_retry_approval` 매트릭스 케이스를 추가해 pending intent가 `weather`, pending link가 `retry`, pending location이 `원주`인 경우에도 `응 서울 날씨 알려줘`는 새 요청으로 처리되는 계약을 고정했다.
  - 전체 테스트 중 `test_build_router_context_pending_approval_validation_log_is_not_guidance`가 실패하며, `route_validation_snapshot()`이 `pending_original_text`를 validation context의 `resolved_slots`에서 제거하고 있음을 확인했다.
  - route validation 요약은 공개 응답이 아니라 라우터용 내부 진단 자료이므로, pending 승인 복원 흐름을 추적할 수 있도록 `route_validation_snapshot()`에서 `pending_original_text`를 보존하도록 수정했다.
  - `plan.md`에 승인처럼 시작해도 새 지역/새 대상/새 주제가 명확하면 pending 승인이 아니라 새 요청으로 처리해야 한다는 원칙을 문서화했다.
  - `python3 -m pytest 'tests/test_context_routing_matrix.py::test_context_routing_matrix[positive_prefix_new_weather_location_not_pending_weather_retry_approval]' -q`(`1 passed`), `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_router_heuristics.py -q`(`484 passed`), `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_router_heuristics.py tests/test_context_builder.py tests/test_bot_helpers.py -q`(`679 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1056 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending weather retry 동일 대상 재언급 승인

- 작업 이름: `응 원주 날씨 다시 알려줘`를 pending `원주` 재시도 승인으로 복원
- 진행상황: 완료
- 진행내용:
  - pending weather retry가 있는 상태에서 사용자가 `응 원주 날씨 다시 알려줘`처럼 승인 표현과 같은 대상을 함께 말하면, 단순 새 요청이 아니라 확인 중이던 `원주 날씨` 재시도 승인으로 처리되어야 한다.
  - `explicit_weather_locations_from_text()`가 승인 prefix를 먼저 제거하도록 보강해 `응원주`가 아니라 `원주`를 지역 슬롯으로 추출하게 했다.
  - `matching_pending_context_approval_state()`는 순수 승인뿐 아니라 승인 prefix가 붙은 같은 대상 재언급도 pending 확인 상태와 매칭할 수 있게 했다. 단, linked state와 pending slots가 같은 경우에만 허용해 `응 서울 날씨 알려줘` 같은 새 지역 요청은 계속 새 요청으로 남긴다.
  - 승인 후 route 복원 과정에서 pending의 `pending_intent`와 `pending_context_link`도 함께 되살려 `chat/none`이나 `clarify`로 흐르지 않고 원래 `weather/retry` 실행 컨텍스트를 유지하도록 했다.
  - `retry` 검증은 현재 승인 문장뿐 아니라 pending에 저장된 원래 요청 문장(`아 다시해봐`)도 참고해, 승인 문장이 자연어상 `다시 알려줘`처럼 표현되어도 원래 재시도 의도를 잃지 않게 했다.
  - `positive_prefix_same_weather_location_restores_pending_weather_retry_approval`, `positive_prefix_new_weather_location_not_pending_weather_retry_approval`, `test_pending_context_approval_accepts_same_weather_location_restatement`, `test_pending_context_approval_rejects_different_weather_location_restatement`를 추가해 동일 대상 승인과 다른 대상 새 요청의 경계를 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_accepts_same_weather_location_restatement tests/test_route_validation.py::test_pending_context_approval_rejects_different_weather_location_restatement 'tests/test_context_routing_matrix.py::test_context_routing_matrix[positive_prefix_same_weather_location_restores_pending_weather_retry_approval]' 'tests/test_context_routing_matrix.py::test_context_routing_matrix[positive_prefix_new_weather_location_not_pending_weather_retry_approval]' -q`(`4 passed`)와 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_router_heuristics.py -q`(`490 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1063 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 승인 prefix가 붙은 명시 ID 요청의 pending 오소비 방지

- 작업 이름: `응 할 일 3 완료해줘`를 pending 승인 답변이 아니라 명시 요청으로 유지
- 진행상황: 완료
- 진행내용:
  - pending 확인 상태가 있을 때 `응 할 일 3 완료해줘`처럼 긍정 표현과 명시 ID/행동이 함께 있는 문장을 pending 승인으로 소비할지 점검했다.
  - 처음에는 같은 ID 재언급을 pending 승인으로 허용하는 방안을 시도했지만, 기존 회귀 테스트가 `응 문서 7 다시 분석해줘`, `응 사이트 열어줘`, `응 확인 지금 몇시야` 같은 명시 요청을 pending 승인으로 먹지 않도록 보호하고 있음을 확인했다.
  - 따라서 안전 계약을 유지했다. 명시 ID/대상/행동이 있는 문장은 pending 승인 답변으로 소비하지 않고, 현재 문장 자체의 요청으로 라우팅한다.
  - `positive_prefix_same_task_id_executes_explicit_current_request_without_pending_consumption` 매트릭스 케이스를 추가해, pending task 확인 상태가 있어도 `응 할 일 3 완료해줘`는 현재 위치의 `할 일 3` 명시 요청으로 실행되고 `pending_original_text`를 붙이지 않는지 고정했다.
  - `positive_prefix_different_task_id_stays_new_explicit_request` 매트릭스 케이스를 추가해, `응 할 일 4 완료해줘`는 기존 pending `할 일 3`으로 이어지지 않고 새 요청으로 남는지 고정했다.
  - 관련 검증으로 `python3 -m pytest 'tests/test_context_routing_matrix.py::test_context_routing_matrix[positive_prefix_same_task_id_executes_explicit_current_request_without_pending_consumption]' 'tests/test_context_routing_matrix.py::test_context_routing_matrix[positive_prefix_different_task_id_stays_new_explicit_request]' tests/test_route_validation.py::test_pending_context_approval_rejects_positive_text_with_explicit_new_target_request tests/test_route_validation.py::test_pending_context_approval_rejects_positive_text_with_named_new_target -q`(`4 passed`)와 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_router_heuristics.py -q`(`494 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1066 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 명시 요청 처리 후 stale pending context 만료

- 작업 이름: 같은 linked state를 명시 요청으로 처리한 뒤 오래된 확인 대기 제거
- 진행상황: 완료
- 진행내용:
  - `응 할 일 3 완료해줘`처럼 현재 문장 자체가 명시 요청으로 처리되는 경우, 기존 pending 확인 상태를 승인으로 소비하지 않는 것은 맞지만 pending 상태가 계속 남으면 다음 턴의 짧은 `응`이 오래된 확인에 붙을 수 있음을 점검했다.
  - `matching_resolved_pending_context_states()`를 추가해 route가 `continue/retry/modify`로 같은 linked state와 같은 intent를 실제 처리했고, route 실행 슬롯이 pending 슬롯과 충돌하지 않는 경우에만 해당 pending 확인 상태를 “명시 요청으로 해소됨”으로 판정한다.
  - Discord 일반 메시지 경로에는 `expire_resolved_pending_context_links()`를 추가했고, CLI 로컬 실행 경로에도 같은 helper를 추가해 운영/재현 경로가 같은 pending 정리 계약을 공유하게 했다.
  - `test_cli_expires_resolved_pending_context_link_on_explicit_same_target_request`를 추가해 같은 linked state의 pending은 만료되는지 검증했다.
  - `test_cli_keeps_pending_context_link_when_explicit_target_conflicts`를 추가해 route 슬롯이 pending 슬롯과 충돌하면 pending을 지우지 않는지 검증했다.
  - `test_assistant_bot_expires_resolved_pending_context_on_explicit_same_target_request`, `test_assistant_bot_keeps_pending_context_when_explicit_target_conflicts`를 추가해 Discord Bot 메서드도 CLI와 같은 기준으로 pending 확인 상태를 만료하거나 유지하는지 직접 검증했다.
  - source-level 계약 테스트에 Discord/CLI가 명시 요청 해소 pending 만료 경로를 호출하는지 추가했다.
  - 관련 검증으로 `python3 -m pytest tests/test_cli.py::test_cli_expires_resolved_pending_context_link_on_explicit_same_target_request tests/test_cli.py::test_cli_keeps_pending_context_link_when_explicit_target_conflicts tests/test_agent_registry.py::test_runtime_route_validation_allows_cross_location_only_after_pending_context_approval -q`(`3 passed`)와 `python3 -m pytest tests/test_cli.py tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_agent_registry.py::test_runtime_route_validation_allows_cross_location_only_after_pending_context_approval -q`(`402 passed`)를 통과했다.
  - Discord/CLI 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_expires_resolved_pending_context_on_explicit_same_target_request tests/test_bot_helpers.py::test_assistant_bot_keeps_pending_context_when_explicit_target_conflicts tests/test_cli.py::test_cli_expires_resolved_pending_context_link_on_explicit_same_target_request tests/test_cli.py::test_cli_keeps_pending_context_link_when_explicit_target_conflicts -q`(`4 passed`)와 `python3 -m pytest tests/test_bot_helpers.py tests/test_cli.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`539 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1072 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 공개 응답 구조의 문자열 내부 route metadata 제거

- 작업 이름: `facts/items/slots` 문자열 값에 들어간 내부 route metadata 노출 방지
- 진행상황: 완료
- 진행내용:
  - 공개 응답용 `OperationResult` 필터가 dict key의 `context_link`, `linked_state_id`, `resolved_slots`, `pending_*`는 제거하지만, `facts.note`나 `items[].note` 같은 문자열 값 안의 `context_link=...` 패턴은 그대로 남길 수 있음을 확인했다.
  - `sanitize_private_route_values()`가 문자열 값에도 `sanitize_private_route_text()`를 재귀 적용하도록 수정했다.
  - `test_response_private_route_metadata_is_filtered_from_nested_string_values`를 추가해 `facts`, 중첩 dict, list 안의 item 문자열, `slots.note`에 들어간 `context_link`, `linked_state_id`, `resolved_slots`, `pending_original_text`, `validation_reason`, `pending_context_link`가 최종 prompt에서 제거되는지 검증했다.
  - 정상 사용자-facing 값인 `task_id`, `할 일 3`, `병원 예약`, `완료 처리`는 보존되는지 함께 확인했다.
  - 관련 검증으로 `python3 -m pytest tests/test_response_composer.py::test_response_private_route_metadata_is_filtered_from_nested_string_values tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_nested_items tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_artifacts_and_text_fields -q`(`3 passed`)와 `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_bot_helpers.py::test_record_internal_action_result_logs_execution_context_link tests/test_bot_helpers.py::test_record_internal_action_result_logs_cross_location_retry_approval_context -q`(`97 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1074 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 에이전트 실행 컨텍스트 문자열 내부 route metadata 제거

- 작업 이름: 내부 행동 기록의 중첩 문자열 값도 에이전트/응답 컨텍스트에서 안전하게 정화
- 진행상황: 완료
- 진행내용:
  - `route_safe_values()`가 dict/list 내부 private key는 제거하지만, literal로 파싱된 내부 행동 기록 안의 문자열 값에 `context_link=...`, `linked_state_id=...`, `pending_original_text=...`가 들어가면 에이전트 실행 컨텍스트에 남을 수 있음을 확인했다.
  - `test_execution_context_filters_private_route_metadata_from_internal_action_segments`를 확장해 `slots.nested.note`, `artifacts.note` 같은 문자열 값 내부 private metadata가 에이전트/응답 컨텍스트에서 제거되는지 검증했다.
  - 처음에는 문자열 값 전체에 세그먼트용 sanitizer를 적용했지만, `test_turn_state_context_sanitizes_delimiters_inside_state_values`가 일반 문자열의 ` | ` 포맷 보존 회귀를 잡았다.
  - 그래서 `sanitize_private_route_value_text()`를 분리했다. private metadata가 실제로 제거된 경우에만 구분자 정리를 수행하고, private metadata가 없는 일반 문자열은 원문을 유지한다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_builder.py::test_turn_state_context_sanitizes_delimiters_inside_state_values tests/test_response_composer.py::test_execution_context_filters_private_route_metadata_from_internal_action_segments -q`(`2 passed`)와 `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_bot_helpers.py::test_record_internal_action_result_logs_execution_context_link tests/test_bot_helpers.py::test_record_internal_action_result_logs_cross_location_retry_approval_context -q`(`97 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1075 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 에이전트 카탈로그 private route metadata 선언 방지

- 작업 이름: 새 에이전트 추가 시 `state_outputs`에 내부 route/debug 슬롯을 선언하지 못하게 고정
- 진행상황: 완료
- 진행내용:
  - 새 에이전트를 추가할 때 카탈로그에 후속 맥락 단서를 선언하는 구조는 유지하되, `context_link`, `linked_state_id`, `resolved_slots`, `pending_*` 같은 내부 route/debug metadata가 사용자 작업 대상 슬롯처럼 선언되면 라우터가 잘못된 단서를 학습할 수 있음을 점검했다.
  - `test_agent_catalog_state_outputs_do_not_declare_private_route_metadata`를 추가해 `agent_catalog.json`의 `state_outputs`가 `slots.*`나 `artifacts.*` 형태로 private route/debug key를 선언하지 않는지 고정했다.
  - `test_catalog_target_slot_names_do_not_include_private_route_metadata`를 추가해 카탈로그 target slot 허용 목록도 private route/debug key와 섞이지 않는지 검증했다.
  - 이 계약은 `OperationResult.slots`에 런타임 내부 metadata를 보존할 수 있는 것과 별개로, 라우터가 참고하는 에이전트 카탈로그에는 실제 사용자 작업 대상 단서만 남기기 위한 것이다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_agent_catalog_state_outputs_do_not_declare_private_route_metadata tests/test_agent_registry.py::test_agent_catalog_state_outputs_use_supported_context_contract_keys tests/test_agent_registry.py::test_agent_catalog_intents_match_actual_registry_handlers -q`(`3 passed`)와 `python3 -m pytest tests/test_agent_registry.py -q`(`61 passed`)를 통과했다.

## 2026-06-07 - 내부 로그 값 축약 전 포맷 토큰 정리 회귀 테스트

- 작업 이름: 긴 내부 로그 값이 축약될 때 가짜 route/context 토큰이 남지 않도록 고정
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록 값은 라우터가 다음 턴에서 참고하는 중요한 힌트지만, 사용자 입력이나 실행 결과 값 안에 `route_context=`, `slots=`, `artifacts=` 같은 문자열이 들어가면 구조화 필드처럼 잘못 해석될 수 있다.
  - 기존 구현은 포맷 토큰을 먼저 일반 텍스트 형태로 치환한 뒤 길이 축약을 수행하고 있었으나, 이 순서가 리팩터링 중 바뀌면 긴 값의 앞부분에 남은 토큰이 라우터 컨텍스트를 오염시킬 수 있어 회귀 테스트로 고정했다.
  - `test_compact_internal_log_value_sanitizes_format_tokens_before_truncation`를 추가해 `compact_internal_log_value()`가 `route_context=`, `validation_context=`, `slots=`, `artifacts=`와 값 내부 ` | `를 치환한 뒤 말줄임 처리하는지 검증했다.
  - 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_compact_internal_log_value_sanitizes_format_tokens_before_truncation tests/test_bot_helpers.py::test_record_internal_action_result_sanitizes_delimiters_inside_values_for_future_context -q`(`2 passed`)와 `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`(`644 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1078 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1077 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.


## 2026-06-07 - 에이전트 카탈로그 tools 어휘 계약 보강

- 작업 이름: 새 에이전트의 도구 선언 오타와 미구현 도구명 방지
- 진행상황: 완료
- 진행내용:
  - `agent_catalog.json`의 `tools` 목록은 라우터가 각 에이전트의 사용 가능 도구를 판단하는 공개 계약이므로, 오타나 구현되지 않은 도구명이 들어가면 라우터가 실제보다 넓은 능력을 가진 것으로 오해할 수 있음을 점검했다.
  - `KNOWN_AGENT_TOOL_NAMES`를 테스트에 추가하고, `test_agent_catalog_tools_use_known_tool_names`로 카탈로그의 `tools`가 알려진 도구 어휘 안에 들어오는지 검증했다.
  - `test_registry_prompt_block_uses_catalog_examples`를 보강해 `get_document_detail`, `search_tasks`, `kma_forecast`, `kma_weather_alerts`, `web_search` 같은 도구명이 registry routing prompt에 실제로 노출되는지 확인했다.
  - 이 계약은 OpenAI tool calling 도구와 코드 내부 도구가 함께 있는 현재 구조를 고려해, 모든 도구를 ToolSpec 빌더와 1:1 매칭하지 않고 “라우터에게 알려도 되는 도구 어휘” 기준으로 검증한다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_agent_catalog_tools_use_known_tool_names tests/test_agent_registry.py::test_registry_prompt_block_uses_catalog_examples tests/test_agent_registry.py -q`(`64 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1079 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 전문 에이전트 resolved_slots 접근 계약 고정

- 작업 이름: 새 에이전트가 내부 route/debug 슬롯을 실행 대상처럼 직접 읽지 못하게 방지
- 진행상황: 완료
- 진행내용:
  - `ExecutionContext.for_agent()`와 응답 작성 컨텍스트는 private route metadata를 정리하지만, 전문 에이전트 구현은 `execution_context.resolved_slots` 객체에 직접 접근할 수 있으므로 새 에이전트 추가 시 내부 제어 슬롯을 잘못 읽을 위험이 있다.
  - `test_specialist_agents_read_only_safe_execution_resolved_slots`를 추가해 `assistant_bot/agents/*.py`에서 `execution_context.resolved_slots.get(...)` 또는 subscript 접근에 사용하는 키가 `SAFE_INTERNAL_ROUTE_SLOT_KEYS` 안에 있는지 소스 레벨로 검증했다.
  - 이 계약으로 `memory_id`, `document_id`, `task_id`, `reminder_id`, `location`, `query`, `url`, `filename`처럼 실제 실행 대상 단서는 허용하고, `pending_original_text`, `pending_resolved_slots`, `context_link`, `linked_state_id` 같은 내부 route/debug 값은 전문 에이전트의 직접 실행 입력으로 쓰지 못하게 했다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_specialist_agents_read_only_safe_execution_resolved_slots -q`(`1 passed`)와 `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py tests/test_response_composer.py -q`(`158 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1082 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 카탈로그 tools와 실제 ToolSpec 이름 일치 검증

- 작업 이름: tool calling 사용 에이전트의 카탈로그 도구 선언과 실제 toolkit 동기화
- 진행상황: 완료
- 진행내용:
  - `chat`과 `recall`은 실제 OpenAI tool calling 경로에서 read-only toolkit을 사용하므로, 카탈로그 `tools` 목록과 실제 `ToolSpec.name` 집합이 어긋나면 라우터가 보는 도구 설명과 모델 호출에 제공되는 도구가 달라질 수 있음을 점검했다.
  - `test_agent_catalog_chat_tools_match_conversation_read_toolkit`를 추가해 `agent_catalog.json`의 `chat.tools`가 `build_conversation_read_tools()`가 만드는 도구명과 정확히 일치하는지 검증했다.
  - `test_agent_catalog_recall_tools_match_memory_read_toolkit`를 추가해 `recall.tools`가 `build_memory_read_tools()` 도구명과 정확히 일치하는지 검증했다.
  - 두 toolkit 모두 `read_only=True` 도구만 제공하는지도 함께 확인해, 대화/회상용 tool calling이 조회 전용 계약을 유지하는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_toolkits.py -q`(`3 passed`)와 `python3 -m pytest tests/test_agent_toolkits.py tests/test_memory_store.py::test_memory_agent_general_recall_uses_read_only_tools tests/test_agent_registry.py::test_agent_catalog_tools_use_known_tool_names tests/test_agent_registry.py::test_registry_prompt_block_uses_catalog_examples -q`(`6 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1082 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 런타임 AgentContext 실행 컨텍스트 전달 계약 고정

- 작업 이름: 봇/CLI dispatch 경로가 전문 에이전트에 ExecutionContext를 빠뜨리지 않도록 방지
- 진행상황: 완료
- 진행내용:
  - 라우터와 검증 계층이 올바른 `linked_state`와 `resolved_slots`를 만들더라도, 봇/CLI가 `AgentContext`를 만들 때 `execution`을 넘기지 않으면 전문 에이전트는 원문 재파싱이나 최신 항목 fallback으로 다른 대상을 처리할 수 있다.
  - `test_runtime_agent_context_construction_includes_execution_context`를 추가해 `assistant_bot/bot.py`, `assistant_bot/cli.py`의 모든 `AgentContext(...)` 생성이 `execution=` 키워드를 포함하는지 소스 레벨로 검증했다.
  - 이 계약으로 일반 메시지, 버튼 후보 선택, 버튼 승인, CLI 재현 경로에서 에이전트 실행 단계가 항상 실제 라우팅/검증 결과 기준의 `ExecutionContext`를 받도록 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_runtime_agent_context_construction_includes_execution_context -q`(`1 passed`)와 `python3 -m pytest tests/test_agent_registry.py::test_runtime_agent_context_construction_includes_execution_context tests/test_agent_registry.py::test_response_composer_calls_include_context_contract tests/test_agent_registry.py::test_discord_execution_results_are_attached_before_return tests/test_agent_registry.py::test_cli_attaches_execution_metadata_before_response_recording tests/test_agent_registry.py::test_specialist_agents_read_only_safe_execution_resolved_slots -q`(`5 passed`)를 통과했다.
  - `python3 -m ruff check .` 실행 중 `tests/test_memory_store.py` import 정렬 문제가 발견되어 `python3 -m ruff check tests/test_memory_store.py --fix`로 정리했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1084 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 결과 기록 실행 컨텍스트 전달 계약 고정

- 작업 이름: 내부 행동 로그가 실제 실행 linked state와 resolved slots를 잃지 않도록 방지
- 진행상황: 완료
- 진행내용:
  - 봇/CLI가 에이전트 실행 결과를 내부 행동 기록으로 남길 때 `ExecutionContext`를 함께 넘기지 않으면, 다음 턴 라우터가 참고할 `route_context`, `linked_state_id`, `resolved_slots`가 빠질 수 있다.
  - `test_runtime_internal_action_result_records_include_execution_context`를 추가해 `assistant_bot/bot.py`, `assistant_bot/cli.py`의 런타임 `record_internal_action_result(...)` 호출이 `execution_context=`를 포함하는지 소스 레벨로 검증했다.
  - 봇 본체의 wrapper 메서드 내부에서 실제 store helper로 위임하는 호출은 예외로 두고, 메시지 처리/버튼 처리/CLI 기록 경로의 호출만 검사하도록 했다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_runtime_internal_action_result_records_include_execution_context -q`(`1 passed`)와 `python3 -m pytest tests/test_agent_registry.py::test_runtime_internal_action_result_records_include_execution_context tests/test_agent_registry.py::test_runtime_agent_context_construction_includes_execution_context tests/test_agent_registry.py::test_response_composer_calls_include_context_contract tests/test_agent_registry.py::test_discord_execution_results_are_attached_before_return tests/test_agent_registry.py::test_cli_attaches_execution_metadata_before_response_recording -q`(`5 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1086 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - turn state resolved_slots 대상 단서 승격

- 작업 이름: 실행 컨텍스트의 안전한 대상 슬롯이 작업 상태 후보에서 사라지지 않도록 보존
- 진행상황: 완료
- 진행내용:
  - `attach_execution_context_metadata()`는 실제 실행 대상인 `resolved_slots`를 결과에 붙이지만, 완료 상태 turn state 저장에서는 raw `resolved_slots`가 private route key로 제거된다.
  - 에이전트가 `task_id`, `document_id`, `url`, `query` 같은 대상 슬롯을 직접 결과에 채우지 못한 경우, 실행 컨텍스트에는 대상이 있었는데 다음 턴 라우터 후보에서는 대상 단서가 사라질 수 있음을 확인했다.
  - `turn_state_slots_from_result()`가 `facts.resolved_slots`와 `slots.resolved_slots` 안의 안전한 실행 대상 슬롯을 일반 turn state 슬롯으로 승격하도록 보강했다.
  - `pending_original_text`, `context_link`, 중첩 `linked_state_id` 같은 내부 route/debug 값은 `route_safe_values()`와 허용 슬롯 목록으로 계속 제거한다.
  - `test_turn_state_slots_from_result_promotes_safe_resolved_slots_for_future_context`를 추가해 안전한 `task_id`는 저장 후보로 남고 private metadata는 제거되는지 검증했다.
  - `test_turn_state_slots_from_result_keeps_explicit_slot_over_resolved_slot`를 추가해 에이전트가 명시적으로 채운 슬롯이 `resolved_slots`보다 우선하는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_turn_state_slots_from_result_promotes_safe_resolved_slots_for_future_context tests/test_bot_helpers.py::test_turn_state_slots_from_result_keeps_explicit_slot_over_resolved_slot tests/test_bot_helpers.py::test_sanitized_turn_state_slots_removes_private_route_metadata_for_completed_state -q`(`3 passed`)와 `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py -q`(`326 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1089 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 승격된 turn state 슬롯의 라우터 파싱 경로 고정

- 작업 이름: 저장된 실행 대상 슬롯이 라우터 후보와 fallback resolved_slots까지 이어지는지 검증
- 진행상황: 완료
- 진행내용:
  - `resolved_slots`에서 승격한 안전 대상 슬롯이 turn state에 저장되더라도, 라우터 컨텍스트 문자열이나 `parse_state_candidates()` 단계에서 읽히지 않으면 다음 턴 라우팅에는 도움이 되지 않는다.
  - `test_build_router_context_exposes_promoted_resolved_slots_as_candidate_hints`를 추가해 저장된 `document_id`가 라우터 컨텍스트의 `slots={'document_id': 7}`와 `target_hints`의 `문서 7`로 노출되고, `parse_state_candidates()` 결과의 `candidate.slots`에도 남는지 검증했다.
  - `test_router_fallback_uses_promoted_resolved_document_slot_from_candidate`를 추가해 `방금 문서 다시 요약해줘` 같은 후속 요청에서 fallback 라우터가 후보의 `document_id`를 `resolved_slots`로 복원하는지 확인했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_router_context_exposes_promoted_resolved_slots_as_candidate_hints tests/test_router_agent.py::test_router_fallback_uses_promoted_resolved_document_slot_from_candidate -q`(`2 passed`)와 `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_bot_helpers.py -q`(`328 passed`)를 통과했다.
  - `FACT_CONTEXT_SLOT_KEYS`와 `INTERNAL_ACTION_CONTEXT_KEYS`의 `tool_call_trace` 계약 불일치를 정리하고, `assistant_bot/openai_service.py`의 tool trace 기록 호출 줄 길이를 ruff 기준에 맞게 정리했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1093 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 일반 기억 회상 tool calling 결과 구조화

- 작업 이름: `recall` tool calling 답변을 `OperationResult`로 반환
- 진행상황: 완료
- 진행내용:
  - `recall` intent는 카탈로그 `state_outputs`가 있는 구조화 에이전트인데, ID가 없는 일반 회상 경로는 `openai.tool_response()`의 문자열 답변을 그대로 반환하고 있음을 확인했다.
  - 이 경우 registry dispatch를 거치면 구조화 결과가 아니라는 이유로 실패하거나, 내부 행동 기록/turn state/후속 라우팅 단서가 끊길 수 있다.
  - `MemoryAgent.recall()`의 일반 tool calling 경로가 `OperationResult`를 반환하도록 수정했다. 답변은 `fallback_text`와 `facts.answer`에 보존하고, `subject`에는 사용자 질문, `available_actions`에는 `show`를 남긴다.
  - registry의 `recall` handler 반환 타입도 실제 반환과 맞게 `OperationResult`로 정리했다.
  - `test_memory_agent_general_recall_uses_read_only_tools`를 구조화 결과 기준으로 갱신했고, `test_memory_agent_general_recall_satisfies_registry_structured_contract`를 추가해 registry dispatch에서도 일반 recall이 계약을 만족하는지 검증했다.
  - 관련 검증으로 `python3 -m pytest tests/test_memory_store.py::test_memory_agent_general_recall_uses_read_only_tools tests/test_memory_store.py::test_memory_agent_general_recall_satisfies_registry_structured_contract -q`(`2 passed`)와 `python3 -m pytest tests/test_memory_store.py tests/test_agent_toolkits.py tests/test_agent_registry.py -q`(`185 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1084 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - registry handler 반환 타입 계약 정리

- 작업 이름: 구조화 필수 에이전트 handler가 문자열 반환을 광고하지 않도록 고정
- 진행상황: 완료
- 진행내용:
  - `build_agent_registry()` 내부 wrapper 중 다수가 실제로는 `OperationResult`를 반환하면서 `-> str`로 표시되어 있음을 확인했다.
  - 런타임은 `OperationResult`를 받으므로 동작상 문제는 없지만, 새 에이전트 추가자가 이를 보고 카탈로그 `state_outputs`가 있는 handler도 문자열을 반환해도 된다고 오해할 수 있다.
  - `remember`, `list_memory`, `update_memory`, `delete_memory`, `restore_memory`, `help`, `status`, `current_time`, `daily_briefing`, `reset_context`, `manage_task`, `manage_reminder`, `analyze_document`, `web_search`, `weather`, `web_url`, `confirm_web_search`, `cancel_pending` wrapper 반환 타입을 `OperationResult`로 정리했다.
  - `test_registry_handlers_do_not_advertise_string_returns_for_structured_agents`를 추가해 registry handler dict에 등록된 함수가 `-> str`을 광고하지 않는지 source-level로 검증했다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_registry_handlers_do_not_advertise_string_returns_for_structured_agents tests/test_agent_registry.py::test_literal_operation_results_follow_catalog_contract -q`(`2 passed`)와 `python3 -m pytest tests/test_agent_registry.py tests/test_memory_store.py::test_memory_agent_general_recall_satisfies_registry_structured_contract tests/test_memory_store.py::test_memory_agent_general_recall_uses_read_only_tools -q`(`68 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1086 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - 카탈로그 전체 구조화 반환 강제 테스트

- 작업 이름: `state_outputs`가 있는 모든 intent의 문자열 반환 거부 보장
- 진행상황: 완료
- 진행내용:
  - registry dispatch에는 `definition_requires_structured_result()` 기반 문자열 반환 거부 로직이 있지만, 카탈로그 전체 intent를 대상으로 이 계약을 직접 검증하는 테스트가 부족했다.
  - `test_catalog_structured_agents_reject_string_handler_results`를 추가해 `agent_catalog.json`의 각 항목을 임시 registry에 등록하고, handler가 문자열만 반환할 때 구조화 필수 intent는 `OperationResult를 반환해야` 오류를 내는지 검증했다.
  - 향후 `subject`만 선언하는 레거시 호환 intent가 생기면 문자열 fallback을 허용하되, 현재처럼 `slots.*`, `artifacts.*`, `available_actions.*`, `retryable`을 선언한 intent는 문자열 반환을 거부한다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_catalog_structured_agents_reject_string_handler_results tests/test_agent_registry.py::test_registry_handlers_do_not_advertise_string_returns_for_structured_agents tests/test_agent_registry.py -q`(`69 passed`)와 `python3 -m pytest tests/test_agent_registry.py tests/test_agent_toolkits.py tests/test_memory_store.py::test_memory_agent_general_recall_satisfies_registry_structured_contract -q`(`71 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1089 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-07 - tool calling 실행 흔적 내부 컨텍스트 기록

- 작업 이름: 도구 기반 에이전트 답변의 내부 실행 단서 보존
- 진행상황: 완료
- 진행내용:
  - `OpenAIService.tool_response()`가 도구를 실행하더라도 호출한 도구 이름과 인자가 호출자에게 돌아오지 않아, 다음 턴 라우터가 “방금 어떤 자료를 조회했는지”를 참고하기 어렵다는 점을 확인했다.
  - `tool_trace_sink` 선택 인자를 추가해 tool calling 실행 시 `tool_call_trace`를 수집하도록 했다.
  - trace에는 도구 이름, query/id 같은 핵심 인자, JSON 출력의 `ok` 여부만 작게 남기고 `token`, `api_key`, `password`, `secret` 계열 인자는 제거한다.
  - `MemoryAgent.recall()`과 `ConversationAgent`의 read-only tool calling 경로가 수집된 trace를 `OperationResult.facts.tool_call_trace`에 비공개 메타데이터로 싣도록 했다.
  - `tool_call_trace`를 응답 작성용 private key로 등록해 최종 사용자 답변 프롬프트에서는 제거하고, 내부 행동 기록 허용 키에는 추가해 `record_internal_action_result()`가 다음 라우팅 컨텍스트에 남길 수 있도록 했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_openai_service.py tests/test_bot_helpers.py::test_record_internal_action_result_logs_private_tool_trace_for_future_context tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context tests/test_agent_registry.py::test_registry_fact_context_slot_keys_match_turn_state_inference_keys tests/test_agent_registry.py::test_internal_route_context_keys_are_private_for_response_composer`(`12 passed`)와 `python3 -m pytest -q tests/test_memory_store.py::test_memory_agent_general_recall_uses_read_only_tools tests/test_memory_store.py::test_memory_agent_general_recall_satisfies_registry_structured_contract tests/test_agent_registry.py tests/test_response_composer.py`(`103 passed`)를 통과했다.

## 2026-06-07 - tool calling trace 라우터 컨텍스트 요약 노출

- 작업 이름: 내부 도구 사용 흔적을 라우터가 읽기 쉬운 형태로 변환
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그에 `tool_call_trace`가 저장되더라도 라우터 컨텍스트에서는 도구명과 핵심 인자가 별도 필드로 정리되지 않아, 모델이 “어떤 도구를 어떤 질의로 썼는지”를 한눈에 보기 어렵다는 점을 확인했다.
  - `build_internal_action_context()`가 내부 행동 기록을 만들 때 `tool_context` 필드를 추가하도록 보강했다.
  - `tool_context`는 `tool_call_trace`의 도구 이름, 안전한 인자, `ok` 여부만 포함하고, `token`, `api_key`, `password`, `secret` 계열 인자는 제거한다.
  - trace 내부의 `query` 같은 대상 단서는 기존 `target_hints` 재귀 추출 흐름을 통해 함께 노출되도록 유지했다.
  - `test_build_router_context_exposes_private_tool_trace_as_internal_tool_context`를 추가해 라우터 컨텍스트에 `tool_context`와 `target_hints`가 남고 비밀 인자는 제거되는지 검증했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_context_builder.py::test_build_router_context_exposes_private_tool_trace_as_internal_tool_context tests/test_context_builder.py::test_build_router_context_adds_internal_action_target_hints_and_guidance tests/test_bot_helpers.py::test_record_internal_action_result_logs_private_tool_trace_for_future_context`(`3 passed`)와 `python3 -m pytest -q tests/test_context_builder.py tests/test_bot_helpers.py::test_record_internal_action_result_logs_private_tool_trace_for_future_context tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_nested_items tests/test_openai_service.py::test_tool_response_records_compact_tool_trace`(`67 passed`)를 통과했다.

## 2026-06-07 - tool_context 라우터 해석 규칙 고정

- 작업 이름: 내부 도구 사용 흔적의 과잉 연결 방지
- 진행상황: 완료
- 진행내용:
  - 라우터 프롬프트가 `tool_context` 자체를 설명하지 않아, 모델이 내부 도구 조회 흔적을 현재 사용자 요청의 본문이나 자동 연결 근거로 과대 해석할 여지가 있음을 확인했다.
  - 라우터 instructions에 `tool_context`는 내부 read-only 도구 조회 근거를 이해하는 보조 단서이며, 명확한 후속 요청과 `target_hints` 일치가 있을 때만 연결 후보로 참고하라는 규칙을 추가했다.
  - `tool_context`가 있다는 이유만으로 현재 메시지를 이전 작업에 자동 연결하지 말라는 금지 규칙을 명시했다.
  - `tool_context` 필드가 내부 행동 로그 라인 중간에 들어와도 route, validation, slots, artifacts 파싱을 오염시키지 않도록 fallback 파서 정규식 경계를 보강했다.
  - `test_router_agent_prefers_model_route_over_heuristic`에 프롬프트 계약 검증을 추가했고, `test_router_internal_action_parsers_stop_before_tool_context`로 파서 경계 회귀 테스트를 추가했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_router_agent.py::test_router_agent_prefers_model_route_over_heuristic tests/test_router_agent.py::test_router_internal_action_parsers_stop_before_tool_context tests/test_context_builder.py::test_build_router_context_exposes_private_tool_trace_as_internal_tool_context`(`3 passed`)와 `python3 -m pytest -q tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py`(`347 passed`)를 통과했다.

## 2026-06-07 - tool_call_trace 안전한 결과 요약 추가

- 작업 이름: 도구 조회 결과 후보를 후속 맥락 단서로 보존
- 진행상황: 완료
- 진행내용:
  - 기존 `tool_call_trace`는 도구명과 입력 인자 위주라, 도구가 반환한 메모/문서/할 일 후보 ID와 제목이 내부 맥락에 충분히 남지 않는 문제가 있었다.
  - `OpenAIService.compact_tool_call_trace()`가 JSON 도구 출력에서 `results` 또는 `result`를 읽어 `result_summary`를 만들도록 보강했다.
  - `result_summary`에는 결과 개수와 각 결과의 `kind`, `id`, `title`, `url`, `status`, `due_at`, `remind_at`, `source_location`, `created_at`만 남긴다.
  - `preview`, `text`, `detail`처럼 본문성이 강하거나 길어질 수 있는 값은 trace와 라우터 컨텍스트에 남기지 않는다.
  - `build_internal_action_context()`의 `tool_context`가 `result_summary`를 보존하고, 결과 제목도 `target_hints`로 추출되도록 했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_openai_service.py::test_tool_response_records_compact_tool_trace tests/test_context_builder.py::test_build_router_context_exposes_private_tool_trace_as_internal_tool_context tests/test_bot_helpers.py::test_infer_turn_slots_excludes_internal_log_only_tool_trace tests/test_agent_registry.py::test_registry_treats_tool_call_trace_as_internal_result_metadata`(`4 passed`)와 `python3 -m pytest -q tests/test_openai_service.py tests/test_context_builder.py tests/test_router_agent.py tests/test_bot_helpers.py::test_infer_turn_slots_excludes_internal_log_only_tool_trace tests/test_agent_registry.py::test_registry_treats_tool_call_trace_as_internal_result_metadata`(`198 passed`)를 통과했다.

## 2026-06-07 - tool 결과 요약 기반 turn state artifact 추론

- 작업 이름: 도구 조회 결과 후보를 후속 작업 후보로 안전하게 보존
- 진행상황: 완료
- 진행내용:
  - `recall`이나 일반 대화 agent가 read-only 도구로 메모/문서/할 일 후보를 조회하더라도, 기존 turn state 후보에는 도구 결과의 ID/제목이 artifact로 남지 않아 fallback 라우터가 “방금 찾은 것”을 이어받기 어려울 수 있음을 확인했다.
  - `infer_turn_artifacts()`가 `tool_call_trace.result_summary.items`에서 안전한 `memory`, `document`, `task`, `reminder`, `web_result` artifact를 추론하도록 보강했다.
  - `search_tasks`, `list_tasks`, `list_due_tasks`처럼 결과 item에 `kind`가 없는 도구는 도구명으로 `task` artifact를 추론한다.
  - `should_record_turn_state()`가 명시 artifact뿐 아니라 추론 artifact도 고려하도록 바꿔, 도구 조회 결과가 실제 후속 후보로 남게 했다.
  - `tool_call_trace` 자체는 여전히 turn state slot이나 카탈로그 후속 슬롯으로 승격하지 않고, 결과 요약의 안전한 후보만 artifact로 남긴다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_tool_call_trace_result_summary_infers_turn_artifacts tests/test_bot_helpers.py::test_tool_call_trace_result_summary_infers_task_artifacts_from_tool_name tests/test_context_builder.py::test_build_router_context_exposes_private_tool_trace_as_internal_tool_context tests/test_openai_service.py::test_tool_response_records_compact_tool_trace`(`4 passed`)와 `python3 -m pytest -q tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py`(`497 passed`)를 통과했다.

## 2026-06-07 - tool 결과 artifact 기반 fallback 후속 연결 검증

- 작업 이름: 도구 조회 결과 후보가 라우터 후보와 fallback 라우팅까지 이어지는지 고정
- 진행상황: 완료
- 진행내용:
  - `tool_call_trace.result_summary`에서 추론한 artifact가 turn state에는 남더라도, 라우터 컨텍스트와 fallback 라우터가 실제로 이를 후속 후보로 읽는지 직접 검증하는 테스트가 부족했다.
  - `test_build_router_context_exposes_tool_trace_result_summary_artifacts_as_turn_state_hints`를 추가해 도구 결과 요약에서 추론한 memory artifact가 라우터 컨텍스트의 `artifacts`와 `target_hints`에 노출되는지 검증했다.
  - `test_router_fallback_links_recent_tool_result_memory_artifact`를 추가해 “방금 찾은 메모 보여줘”가 도구 결과로 남은 memory artifact 후보에 연결되고 `memory_id`와 `memory_ids`를 함께 복원하는지 검증했다.
  - 일반 artifact fallback 복원 시 단일 후보라면 singular 슬롯(`memory_id`, `document_id`, `task_id`, `reminder_id`)도 함께 채우도록 보강했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_context_builder.py::test_build_router_context_exposes_tool_trace_result_summary_artifacts_as_turn_state_hints tests/test_router_agent.py::test_router_fallback_links_recent_tool_result_memory_artifact tests/test_router_agent.py::test_router_fallback_restores_specific_memory_slot_from_aligned_artifact_titles`(`3 passed`)와 `python3 -m pytest -q tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py tests/test_context_routing_matrix.py`(`503 passed`)를 통과했다.

## 2026-06-07 - tool 결과 task artifact 조작형 후속 연결 검증

- 작업 이름: 도구로 조회한 할 일을 완료/삭제 같은 작업으로 이어받기
- 진행상황: 완료
- 진행내용:
  - `list_tasks` 같은 read-only 도구 결과에서 추론된 task artifact가 조회형 후속뿐 아니라 “방금 조회한 할 일 완료해줘” 같은 조작형 후속에도 연결되는지 확인했다.
  - `test_context_routing_matrix`에 `tool_result_single_task_artifact_complete_restores_task_id` 케이스를 추가했다.
  - 해당 케이스는 후보 `slots={}` 상태에서 artifact만으로 `manage_task`, `context_link=continue`, `linked_state_id`, `task_id`, `task_ids`가 복원되는지 검증한다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_context_routing_matrix.py::test_context_routing_matrix --maxfail=1 -k tool_result_single_task_artifact_complete_restores_task_id`(`1 passed`)와 `python3 -m pytest -q tests/test_router_agent.py::test_router_fallback_links_recent_tool_result_memory_artifact tests/test_context_builder.py::test_build_router_context_exposes_tool_trace_result_summary_artifacts_as_turn_state_hints tests/test_bot_helpers.py::test_tool_call_trace_result_summary_infers_task_artifacts_from_tool_name`(`3 passed`)를 통과했다.

## 2026-06-07 - tool_call_trace 슬롯 후보 오염 방지

- 작업 이름: 내부 도구 추적값과 실제 후속 대상 슬롯 분리
- 진행상황: 완료
- 진행내용:
  - `tool_call_trace`는 사용자에게 보이지 않는 도구 실행 흔적이지만, 공통 추론 키에 포함되면 turn state 슬롯으로 저장되어 다음 라우터 후보를 오염시킬 수 있음을 확인했다.
  - `tool_call_trace`를 `FACT_CONTEXT_SLOT_KEYS`와 `INTERNAL_ACTION_CONTEXT_KEYS`에서 제외하고, `INTERNAL_RESULT_SLOT_KEYS` 및 내부 로그 전용 context key로 분리했다.
  - `record_internal_action_result()`는 기존처럼 `tool_call_trace`를 내부 행동 로그에 남기지만, `infer_turn_slots()`와 turn state 후보 저장은 이 값을 실제 대상 슬롯으로 승격하지 않도록 했다.
  - `test_infer_turn_slots_excludes_internal_log_only_tool_trace`를 추가해 도구 추적값이 turn state 슬롯에서 제외되는지 검증했다.
  - `test_registry_treats_tool_call_trace_as_internal_result_metadata`를 추가해 에이전트 카탈로그가 `tool_call_trace`를 후속 슬롯으로 선언하지 않아도 계약 위반이 아니며, 동시에 `FACT_CONTEXT_SLOT_KEYS`에는 포함되지 않는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_infer_turn_slots_excludes_internal_log_only_tool_trace tests/test_bot_helpers.py::test_record_internal_action_result_logs_private_tool_trace_for_future_context tests/test_agent_registry.py::test_registry_fact_context_slot_keys_match_turn_state_inference_keys tests/test_agent_registry.py::test_registry_treats_tool_call_trace_as_internal_result_metadata tests/test_context_builder.py::test_build_router_context_exposes_private_tool_trace_as_internal_tool_context -q`(`5 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1096 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 같은 지역명 새 주제의 날씨 후보 오연결 방지

- 작업 이름: 단일 지역명 겹침과 실제 날씨 후속 요청 분리
- 진행상황: 완료
- 진행내용:
  - 최근 후보가 `원주 날씨`이고 현재 메시지가 `원주 맛집 알려줘`처럼 같은 지역명만 공유하는 경우, 후보에 `show` 액션이 있으면 fallback 라우터가 weather 후보에 연결할 수 있는 경로를 확인했다.
  - `weather_candidate_matches_only_location_for_new_topic()`를 추가해 weather 후보는 현재 문장에 맛집, 식당, 여행, 숙소, 교통 같은 비날씨 지역 주제 표지가 있고 날씨/예보/기온/미세먼지 같은 날씨 표지가 없으면 연결 후보로 쓰지 않도록 했다.
  - `same_location_name_new_non_weather_topic_does_not_continue_weather` 매트릭스 케이스를 추가해 `원주 맛집 알려줘`가 `원주 날씨` 후보에 붙지 않고 새 `chat` 요청으로 유지되는지 검증했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`(`160 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1098 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 저장 항목 제목과 일반 정보 질문 분리

- 작업 이름: 할 일/메모/알림 제목 매칭이 일반 지식 질문을 빼앗지 않도록 방지
- 진행상황: 완료
- 진행내용:
  - 최근 후보가 `할 일 3 병원 예약`이고 현재 메시지가 `병원 예약 방법 알려줘`인 경우, 제목은 강하게 겹치지만 사용자의 의도는 저장된 할 일 조회가 아니라 일반 정보 질문이다.
  - `stored_item_candidate_matches_general_information_request()`를 추가해 메모/할 일/알림 후보는 `방법`, `어떻게`, `가이드`, `설명`, `추천`, `절차` 같은 일반 정보 표지가 있고 대명사, 명시 종류명, 완료/삭제/수정/보여 같은 저장 항목 조작 표지가 없으면 후보 연결을 거부하도록 했다.
  - `task_title_general_information_request_does_not_continue_task` 매트릭스 케이스를 추가해 `병원 예약 방법 알려줘`가 `manage_task`로 오염되지 않고 `chat` 새 요청으로 남는지 검증했다.
  - 같은 재현에서 `병원 예약 완료했어`, `병원 예약 보여줘`는 계속 `manage_task` 후속 요청으로 연결되는지도 직접 확인했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`(`161 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1099 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 웹/문서 제목과 일반 정보 질문 분리

- 작업 이름: 검색 결과와 문서 제목 매칭이 새 설명 질문을 빼앗지 않도록 방지
- 진행상황: 완료
- 진행내용:
  - 최근 후보가 `파이썬 비동기 검색` 또는 `파이썬 비동기.pdf` 문서이고 현재 메시지가 `파이썬 비동기 방법 알려줘`인 경우, 주제는 겹치지만 사용자는 저장된 결과 요약이 아니라 일반 설명을 기대한다.
  - `knowledge_candidate_matches_general_information_request()`를 추가해 document/web 후보는 `방법`, `어떻게`, `가이드`, `설명`, `차이`, `의미` 같은 일반 정보 표지가 있고 `문서`, `파일`, `pdf`, `검색`, `검색결과`, `링크`, `요약`, `다시검색` 같은 자료 참조 표지가 없으면 후보 연결을 거부하도록 했다.
  - `web_result_title_general_information_request_does_not_retry_web_result`와 `document_title_general_information_request_does_not_continue_document` 매트릭스 케이스를 추가했다.
  - 직접 재현으로 `파이썬 비동기 방법 알려줘`는 새 `chat` 요청으로 남고, `파이썬 비동기 요약해줘`, `파이썬 비동기 다시 검색해줘`, `파이썬 비동기.pdf 요약해줘`, `문서 7 보여줘`는 기존 후속 요청으로 유지되는지 확인했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`(`163 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1101 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 저장 항목 조회 표현 과차단 해소

- 작업 이름: `알려줘`/`내용 알려줘` 조회 표현을 저장 항목 후속으로 복원
- 진행상황: 완료
- 진행내용:
  - 일반 정보 질문 차단 규칙이 너무 넓어 `병원 예약 알려줘`, `병원 예약 내용 알려줘`처럼 저장된 할 일을 조회하는 자연스러운 표현까지 새 `chat` 요청으로 보내는 문제를 확인했다.
  - `general_information_request_markers()`에서 단독 `알려줘`/`알려`를 제거하고, `내용`은 저장 항목 조회 보조어로 처리하도록 조정했다.
  - route validation의 `explicit_named_targets_from_text()`도 `내용`, `상세`, `세부`, `정보`, `항목` 같은 조회 보조어를 대상명 끝에서 제거하도록 보강했다.
  - `task_title_plain_show_request_continues_task`, `task_title_content_show_request_continues_task`, `test_validate_route_context_link_keeps_matching_named_target_with_content_suffix`를 추가했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_named_target_with_content_suffix -q`(`166 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1106 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 이름 있는 대상 조회 진단 힌트 세분화

- 작업 이름: 현재 메시지 진단이 저장 항목 조회 가능성을 새 요청으로만 표시하지 않도록 개선
- 진행상황: 완료
- 진행내용:
  - fallback 라우터는 `병원 예약 알려줘`, `병원 예약 내용 알려줘`를 저장 항목 조회로 연결할 수 있지만, `build_current_message_context()`는 `알려줘`를 새 요청 표지로만 보고 `likely_new_request_do_not_link_previous_state`를 모델 라우터에 전달하고 있었다.
  - `is_possible_named_target_lookup()`를 추가해 명시 named target과 단순 `show` 액션이 있고 `방법`, `가이드`, `추천`, `차이` 같은 일반 정보 표지가 없으면 `possible_named_target_lookup_check_candidate_match`로 진단하도록 했다.
  - `병원 예약 방법 알려줘`는 계속 `likely_new_request_do_not_link_previous_state`로 남기고, `병원 예약 알려줘`, `병원 예약 내용 알려줘`는 후보 제목/ID와 대조할 수 있는 조회 후보로 표시한다.
  - `test_build_current_message_context_marks_possible_named_target_lookup`와 `test_build_current_message_context_keeps_general_information_request_as_new_request`를 추가했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_current_message_context_marks_possible_named_target_lookup tests/test_context_builder.py::test_build_current_message_context_keeps_general_information_request_as_new_request tests/test_context_routing_matrix.py::test_context_routing_matrix tests/test_route_validation.py::test_validate_route_context_link_keeps_matching_named_target_with_content_suffix -q`(`168 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1110 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 후속 대상 슬롯 런타임 계약 일치 테스트

- 작업 이름: 새 에이전트 target slot 추가 시 라우터/turn state/내부 로그 계약 불일치 방지
- 진행상황: 완료
- 진행내용:
  - 카탈로그 target slot 목록, `SAFE_INTERNAL_ROUTE_SLOT_KEYS`, `TURN_STATE_TARGET_HINT_SLOT_KEYS`, `INTERNAL_ACTION_TARGET_HINT_KEYS`가 현재는 같은 대상 슬롯 집합을 공유하지만, 이 일치가 직접 테스트로 고정되어 있지 않았다.
  - `test_catalog_target_slot_contract_matches_runtime_context_sets`를 추가해 카탈로그 대상 슬롯 세트가 라우터 안전 merge 슬롯, turn state target hint 슬롯, 내부 action target hint 슬롯과 같은 계약을 유지하는지 검증했다.
  - 새 에이전트가 `event_id`, `ticket_id` 같은 후속 대상 슬롯을 추가할 때 한 곳만 수정해서 다음 턴 후보/내부 로그/라우터 merge 중 하나가 빠지는 회귀를 빠르게 드러내도록 했다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_catalog_target_slot_contract_matches_runtime_context_sets tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_turn_state_hints tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_internal_route_slot_merge tests/test_agent_registry.py::test_agent_catalog_target_slot_outputs_are_available_for_internal_action_target_hints -q`(`4 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1112 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 이름 있는 대상 조회 진단의 fallback 연결 계약 고정

- 작업 이름: `possible_named_target_lookup` 힌트가 새 요청 차단으로 오해되지 않도록 테스트
- 진행상황: 완료
- 진행내용:
  - 현재 메시지 진단이 `possible_named_target_lookup_check_candidate_match`를 반환하더라도, fallback 라우터가 이 힌트를 `likely_new_request_do_not_link_previous_state`처럼 해석하면 저장 항목 조회가 다시 끊길 수 있다.
  - `test_current_message_decision_hint_parses_named_target_lookup_diagnostic`를 추가해 새 진단 힌트가 라우터 fallback에서 파싱되는지 고정했다.
  - `test_router_fallback_uses_named_target_lookup_diagnostic_to_allow_candidate_match`를 추가해 `병원 예약 내용 알려줘`가 `할 일 3 병원 예약` 후보와 매칭되면 `manage_task`, `context_link=continue`, `task_id=3`으로 연결되는지 검증했다.
  - 기존 새 요청 차단 테스트도 함께 실행해 `likely_new_request_do_not_link_previous_state`와 `possible_named_target_lookup_check_candidate_match`가 서로 다른 의미를 유지하는지 확인했다.
  - 관련 검증으로 `python3 -m pytest tests/test_router_agent.py::test_current_message_decision_hint_parses_named_target_lookup_diagnostic tests/test_router_agent.py::test_router_fallback_uses_named_target_lookup_diagnostic_to_allow_candidate_match tests/test_router_agent.py::test_router_fallback_uses_current_message_new_request_diagnostic_to_skip_candidate_link -q`(`3 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1114 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation 로그 요약 단일 계산

- 작업 이름: 실행 전 검증 로그의 요약 생성 일관성 정리
- 진행상황: 완료
- 진행내용:
  - `AssistantBot.log_route_validation_if_changed()`가 `route_validation_summary()`를 변경 여부 확인과 실제 로그 기록에서 각각 호출하고 있어, 동일한 검증 결과 요약을 두 번 생성하고 있었다.
  - 요약 문자열을 `summary` 변수에 한 번만 계산한 뒤 `None` 여부 확인과 `logs.add(reason=summary)`에 재사용하도록 정리했다.
  - `test_runtime_route_validation_log_summary_is_computed_once`를 추가해 봇/CLI 양쪽 `log_route_validation_if_changed()` 안에서 `route_validation_summary()`가 한 번만 호출되고, 기록 reason에는 계산된 `summary` 변수가 사용되는지 소스 레벨로 검증했다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_runtime_route_validation_log_summary_is_computed_once tests/test_bot_helpers.py::test_route_validation_summary_preserves_pending_cross_location_retry_context tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router -q`(`3 passed`)와 `python3 -m pytest tests/test_agent_registry.py::test_runtime_route_validation_log_summary_is_computed_once tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment -q`(`2 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1119 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 사용자별 대화 컨텍스트 조회 계약 고정

- 작업 이름: 공유 채널 맥락 오염 방지를 위한 conversation context 조회 소스 계약 보강
- 진행상황: 완료
- 진행내용:
  - 새 에이전트나 오케스트레이션 코드가 `ConversationStore.recent_messages()`를 읽을 때 `user_id`를 넘기는 계약은 소스 레벨 테스트로 고정되어 있었지만, 같은 맥락 자료인 `latest_summary()`, `latest_user_context_preview()`, `latest_user_message()`, `char_count_since_latest_summary()` 조회 계약은 하나의 안전망으로 묶여 있지 않았다.
  - `test_scope_based_conversation_context_reads_include_user_id`를 추가해 봇, CLI, context builder, 모든 전문 에이전트 코드에서 사용자별 대화 요약/미리보기/최근 메시지/요약 기준 글자 수 조회 시 `user_id` 인자를 빠뜨리면 실패하도록 했다.
  - 이 변경은 공유 채널에서 다른 사용자의 요약, 최근 발화, 다른 위치 미리보기가 현재 사용자의 후속 맥락 판단이나 대화 압축 기준으로 섞이는 회귀를 새 에이전트 추가 단계에서 바로 잡기 위한 안전장치다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_scope_based_conversation_context_reads_include_user_id tests/test_agent_registry.py::test_scope_based_recent_message_reads_include_user_id -q`(`2 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1124 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 도구 결과 artifact 후속 연결 보강

- 작업 이름: 내부 도구 조회 결과가 문서/알림 후속 요청으로 안정적으로 이어지도록 개선
- 진행상황: 완료
- 진행내용:
  - 기존 보강은 `tool_call_trace`가 `facts`에 있을 때 메모/할 일 artifact를 추론하는 흐름 중심으로 검증되어 있었다.
  - 새 에이전트가 trace를 `slots`나 기존 `artifacts` 쪽에 싣더라도 같은 안전한 `result_summary` 후보를 turn state artifact로 추론하도록 `iter_result_tool_call_traces()`를 추가했다.
  - `tool_call_trace` 원문은 여전히 `infer_turn_slots()`로 승격하지 않고, 최종 저장 artifact에서도 private key 제거 규칙을 유지한다.
  - `get_document_detail` 결과 요약이 `slots.tool_call_trace`에 있어도 `document` artifact로 복원되는지, `list_reminders` 결과 요약이 artifact 내부 trace에 있어도 `reminder` artifact로 복원되는지 테스트를 추가했다.
  - `방금 찾은 문서 다시 요약해줘`처럼 기본 heuristic이 `recall`로 잡히고 이전 후보 intent가 `chat`인 경우에도, 후보 artifact kind가 `document`이고 현재 문장이 문서 요약/분석 요청이면 `analyze_document`로 끌어올리도록 fallback 라우터를 보강했다.
  - `tool_result_single_document_artifact_summary_restores_document_id`, `tool_result_single_reminder_artifact_delete_restores_reminder_id` 매트릭스 케이스를 추가해 문서/알림 도구 결과 후속 연결을 고정했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_tool_call_trace_result_summary_infers_document_artifacts_from_slots tests/test_bot_helpers.py::test_tool_call_trace_result_summary_infers_reminder_artifacts_from_artifacts tests/test_bot_helpers.py::test_tool_call_trace_result_summary_infers_turn_artifacts tests/test_bot_helpers.py::test_tool_call_trace_result_summary_infers_task_artifacts_from_tool_name`(`4 passed`), `python3 -m pytest -q tests/test_context_routing_matrix.py -k "tool_result_single or document_artifact or reminder"`(`18 passed, 150 deselected`), `python3 -m pytest -q tests/test_router_agent.py tests/test_context_builder.py`(`194 passed`)를 통과했다.

## 2026-06-07 - 공개 응답 결과 필드 필터 계약 고정

- 작업 이름: `OperationResult` 필드 추가 시 최종 응답 private metadata 필터 누락 방지
- 진행상황: 완료
- 진행내용:
  - 최종 답변 작성 모델에는 `public_operation_result_for_response()`로 정리된 실행 결과만 들어가지만, `OperationResult`에 새 필드가 추가되면 이 변환 함수가 해당 필드를 누락할 수 있는 위험을 확인했다.
  - `test_public_operation_result_for_response_handles_every_result_field`를 추가해 공개 응답 변환 함수가 현재 `OperationResult`의 모든 dataclass 필드를 명시적으로 다루는지 소스 레벨로 검증했다.
  - 이 테스트는 새 에이전트가 새 결과 필드를 추가할 때, 그 필드에 `context_link`, `linked_state_id`, `tool_call_trace` 같은 내부 메타데이터가 담기더라도 최종 응답 프롬프트로 새지 않도록 필터 계약을 함께 갱신하게 만드는 안전장치다.
  - 관련 검증으로 `python3 -m pytest tests/test_response_composer.py::test_public_operation_result_for_response_handles_every_result_field -q`(`1 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1125 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 런타임 에이전트 실행 결과 metadata attach 계약 고정

- 작업 이름: 새 실행 경로가 후속 맥락 metadata를 잃지 않도록 소스 계약 보강
- 진행상황: 완료
- 진행내용:
  - 봇/CLI 런타임에서 `agent_registry.dispatch()`나 `document_analysis_agent.analyze()`를 호출한 결과는 `attach_execution_context_metadata()`를 거쳐야 다음 턴 라우터가 `context_link`, `linked_state_id`, 안전한 `resolved_slots`를 내부 행동 기록과 turn state에서 참고할 수 있다.
  - 기존 테스트는 raw `return await ...` 패턴만 금지하고 있어, 새 함수가 실행 결과를 변수에 받은 뒤 metadata attach 없이 반환하거나 기록하는 회귀를 충분히 막지 못할 수 있었다.
  - `test_runtime_agent_execution_functions_attach_execution_metadata`를 추가해 봇/CLI 함수 안에 런타임 에이전트 실행 호출이 있으면 같은 함수 안에 `attach_execution_context_metadata()` 호출도 있어야 한다고 고정했다.
  - 이 변경은 새 버튼 경로, 새 첨부 처리 경로, 새 CLI 재현 경로를 추가할 때 라우팅은 맞았지만 후속 맥락 기록이 비는 문제를 조기에 잡기 위한 안전장치다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_runtime_agent_execution_functions_attach_execution_metadata -q`(`1 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1128 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 버튼 응답 실행 컨텍스트 재사용 정리

- 작업 이름: 버튼 응답 작성과 내부 행동 기록이 같은 실행 컨텍스트를 보도록 정리
- 진행상황: 완료
- 진행내용:
  - 확인 버튼, URL 후보 선택 버튼, 작업 후보 선택 버튼 경로에서 `execution_context_from_result_metadata()`를 응답 작성용과 내부 행동 기록용으로 각각 다시 호출하고 있었다.
  - 현재 함수는 같은 입력에 대해 같은 값을 만들지만, 향후 컨텍스트 생성 로직이 더 복잡해지면 최종 답변 작성자가 본 실행 컨텍스트와 내부 기록에 남은 실행 컨텍스트가 달라질 수 있다.
  - 세 버튼 핸들러에서 `response_execution_context`를 한 번 계산한 뒤 `ResponseComposer.compose()`와 `record_internal_action_result()`에 같은 객체를 넘기도록 정리했다.
  - `test_button_handlers_reuse_single_response_execution_context`를 추가해 버튼 핸들러가 실행 컨텍스트를 한 번만 만들고 응답 작성/내부 기록 양쪽에서 같은 변수를 쓰는지 소스 레벨로 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py -k "confirmation_button or candidate_selection_button or url_candidate_selection_button or internal_action" -q`(`24 passed, 125 deselected`), `python3 -m pytest tests/test_agent_registry.py::test_runtime_agent_execution_functions_attach_execution_metadata tests/test_agent_registry.py::test_response_composer_calls_include_context_contract tests/test_agent_registry.py::test_runtime_internal_action_result_records_include_execution_context -q`(`3 passed`), `python3 -m pytest tests/test_agent_registry.py::test_button_handlers_reuse_single_response_execution_context -q`(`1 passed`)를 통과했다.

## 2026-06-07 - 긴 도구 trace 내부 맥락 보존 수정

- 작업 이름: 내부 행동 로그가 길어도 `tool_context` 도구명과 핵심 인자를 잃지 않도록 초기 보강
- 진행상황: 완료
- 진행내용:
  - 전체 테스트 중 `test_record_internal_action_result_preserves_compact_tool_trace_context_when_long`가 실패하며, 긴 `tool_call_trace`가 `slots=` 세그먼트 안에서 잘려 `tool_context`는 표시되지만 도구명 `search_memories`가 라우터 컨텍스트에 남지 않는 문제를 확인했다.
  - 이 시점에는 `internal_action_result_reason()`이 안전하게 압축한 trace를 별도 세그먼트로 남기는 방향을 검토했다.
  - 이후 `긴 도구 trace의 tool_context 복원 안정화` 작업에서 최종 계약을 `tool_context=...` segment로 정리하고, target hint 추출까지 함께 고정했다.
  - 이 변경으로 내부 도구 출력 전체나 비밀값은 숨기면서도, 라우터가 다음 턴에서 “방금 어떤 read-only 도구로 어떤 자료를 조회했는지”를 계속 참고할 수 있다.
  - 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_preserves_compact_tool_trace_context_when_long -q`(`1 passed`)와 `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_preserves_compact_tool_trace_context_when_long tests/test_context_builder.py::test_build_router_context_exposes_private_tool_trace_as_internal_tool_context tests/test_agent_registry.py::test_button_handlers_reuse_single_response_execution_context -q`(`3 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1131 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 도구 결과 artifact 과연결 방지 표지 확장

- 작업 이름: 조회된 문서/알림 제목과 겹치는 일반 정보 질문을 새 요청으로 유지
- 진행상황: 완료
- 진행내용:
  - 도구 결과 artifact가 후속 요청 후보로 잘 복원되더라도, 반대로 `계약서 작성 방법 알려줘`, `물 마시기 효과 알려줘`처럼 제목이 겹치는 새 설명 질문을 과거 문서/알림 작업에 붙이면 안 된다.
  - `tool_result_document_artifact_general_question_does_not_continue`, `tool_result_reminder_artifact_general_question_does_not_continue` 매트릭스 케이스를 추가해 도구 결과 artifact가 있어도 일반 정보 질문은 `context_link=none`인 새 `chat` 요청으로 남는지 검증했다.
  - 현재 메시지 진단에서 `물 마시기 효과 알려줘`가 `possible_named_target_lookup_check_candidate_match`로 잘못 표시되는 문제를 확인하고, 일반 정보 질문 표지에 `효과`, `장점`, `단점`, `원리`, `이유`를 추가했다.
  - 라우터의 저장 항목/문서·웹 일반 정보 질문 차단 표지도 같은 목록으로 확장해 모델 라우팅과 fallback 라우팅이 같은 경계를 공유하게 했다.
  - `test_build_current_message_context_marks_document_title_general_question_as_new_request`, `test_build_current_message_context_marks_reminder_title_general_question_as_new_request`를 추가했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_context_builder.py::test_build_current_message_context_marks_document_title_general_question_as_new_request tests/test_context_builder.py::test_build_current_message_context_marks_reminder_title_general_question_as_new_request tests/test_context_builder.py::test_build_current_message_context_marks_possible_named_target_lookup`(`3 passed`), `python3 -m pytest -q tests/test_context_routing_matrix.py -k "tool_result_document_artifact_general_question_does_not_continue or tool_result_reminder_artifact_general_question_does_not_continue or tool_result_single"`(`5 passed, 165 deselected`), `python3 -m pytest -q tests/test_context_builder.py tests/test_router_agent.py`(`196 passed`), `python3 -m pytest -q tests/test_context_routing_matrix.py`(`170 passed`)를 통과했다.

## 2026-06-07 - 내부 로그 전용 trace 계약 고정

- 작업 이름: 새 에이전트 내부 trace가 turn state 슬롯이나 사용자 응답으로 새지 않도록 안전망 추가
- 진행상황: 완료
- 진행내용:
  - 내부 도구 조회 흔적인 `tool_call_trace`는 내부 행동 로그에는 필요하지만, 실제 실행 슬롯이나 일반 fact context로 승격되면 다음 턴 라우터 후보를 오염시킬 수 있다.
  - `test_internal_log_only_context_keys_do_not_become_turn_state_or_fact_slots`를 추가해 내부 로그 전용 키가 `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`, `INTERNAL_RESULT_SLOT_KEYS`, `INTERNAL_ACTION_LOG_CONTEXT_KEYS`에는 포함되고, `INTERNAL_ACTION_CONTEXT_KEYS`, `FACT_CONTEXT_SLOT_KEYS`, `infer_turn_slots()`에는 포함되지 않는 계약을 고정했다.
  - artifact 내부에 있는 `tool_call_trace`는 `result_summary` 후보 추론에는 사용하되, 최종 turn state artifact에는 trace payload가 남지 않도록 `test_turn_state_artifacts_use_tool_trace_summary_but_drop_trace_payload`를 추가했다.
  - `route_safe_values()`가 private key 제거 뒤 빈 dict만 남은 nested payload를 제거하도록 보강해, 내부 trace/debug metadata만 담긴 껍데기가 라우터/응답 컨텍스트에 남지 않게 했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_agent_registry.py::test_internal_log_only_context_keys_do_not_become_turn_state_or_fact_slots tests/test_agent_registry.py::test_registry_treats_tool_call_trace_as_internal_result_metadata tests/test_bot_helpers.py::test_infer_turn_slots_excludes_internal_log_only_tool_trace`(`3 passed`), `python3 -m pytest -q tests/test_bot_helpers.py::test_turn_state_artifacts_use_tool_trace_summary_but_drop_trace_payload tests/test_bot_helpers.py::test_turn_state_artifacts_from_result_removes_private_route_metadata tests/test_bot_helpers.py::test_sanitized_turn_state_slots_removes_private_route_metadata_for_completed_state`(`3 passed`), `python3 -m pytest -q tests/test_response_composer.py`(`35 passed`)를 통과했다.

## 2026-06-07 - 긴 도구 trace의 tool_context 복원 안정화

- 작업 이름: result_summary가 긴 내부 도구 조회도 다음 턴 라우터가 읽을 수 있게 개선
- 진행상황: 완료
- 진행내용:
  - `record_internal_action_result()`가 `tool_call_trace`를 `slots=...` 안에 넣고 220자로 압축하면, `result_summary`가 조금만 길어져도 `ast.literal_eval()` 파싱이 깨져 라우터 컨텍스트의 `tool_context`가 사라지는 문제를 재현했다.
  - `test_record_internal_action_result_preserves_compact_tool_trace_context_when_long`를 추가해 긴 도구 결과 요약에서도 `search_memories`, query, 결과 제목이 라우터 컨텍스트에 남아야 한다는 계약을 고정했다.
  - 내부 행동 로그 생성 시 raw `tool_call_trace`를 `slots`에 섞지 않고, `compact_internal_action_tool_call()`로 안전하게 축약한 `tool_context=...` segment를 별도 기록하도록 했다.
  - `build_internal_action_context()`가 기존 `slots/artifacts.tool_call_trace`뿐 아니라 새 `tool_context` segment도 직접 읽도록 보강했다.
  - `internal_action_target_hints()`가 `tool_context`에서도 query/title 같은 대상 단서를 추출하도록 해, precompacted tool context에서도 `target_hints`가 유지되게 했다.
  - `test_build_router_context_reads_precompacted_tool_context_segment`를 추가해 새 로그 형식을 직접 검증했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_record_internal_action_result_logs_private_tool_trace_for_future_context tests/test_bot_helpers.py::test_record_internal_action_result_preserves_compact_tool_trace_context_when_long tests/test_bot_helpers.py::test_record_internal_action_result_sanitizes_delimiters_inside_values_for_future_context tests/test_bot_helpers.py::test_turn_state_artifacts_use_tool_trace_summary_but_drop_trace_payload`(`4 passed`), `python3 -m pytest -q tests/test_context_builder.py::test_build_router_context_exposes_private_tool_trace_as_internal_tool_context tests/test_context_builder.py::test_build_router_context_reads_precompacted_tool_context_segment tests/test_context_builder.py::test_build_router_context_exposes_tool_trace_result_summary_artifacts_as_turn_state_hints tests/test_context_builder.py::test_build_router_context_adds_internal_action_target_hints_and_guidance`(`4 passed`), `python3 -m pytest -q tests/test_response_composer.py tests/test_agent_registry.py::test_internal_log_only_context_keys_do_not_become_turn_state_or_fact_slots`(`36 passed`)를 통과했다.

## 2026-06-07 - tool_context 사용자 문자열 구분자 정제

- 작업 이름: 도구 query/title 안의 내부 로그 구분자가 segment 파싱을 오염시키지 않도록 방지
- 진행상황: 완료
- 진행내용:
  - `tool_context=...`를 별도 segment로 남기더라도, query나 result title에 ` | route_context=...`, ` | slots=...` 같은 문자열이 있으면 내부 로그가 다시 여러 segment로 쪼개질 수 있음을 확인했다.
  - `test_record_internal_action_result_sanitizes_tool_context_delimiters`를 추가해 도구 query/title 안의 내부 필드명 모양 문자열이 라우터 컨텍스트에서 실제 `route_context`나 `slots` segment로 오해되지 않는지 검증했다.
  - `sanitize_internal_action_tool_text()`를 추가해 tool argument/result item 문자열에서 ` | `를 ` / `로 바꾸고, `route_context=`, `validation_context=`, `tool_context=`, `target_hints=`, `slots=`, `artifacts=`, `context_link=`, `linked_state_id=`, `resolved_slots=`, `pending_original_text=` 같은 내부 필드 표기를 일반 텍스트 형태로 정리한다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_record_internal_action_result_sanitizes_tool_context_delimiters`(`1 passed`), `python3 -m pytest -q tests/test_bot_helpers.py::test_record_internal_action_result_logs_private_tool_trace_for_future_context tests/test_bot_helpers.py::test_record_internal_action_result_preserves_compact_tool_trace_context_when_long tests/test_bot_helpers.py::test_record_internal_action_result_sanitizes_tool_context_delimiters tests/test_bot_helpers.py::test_record_internal_action_result_sanitizes_delimiters_inside_values_for_future_context`(`4 passed`), `python3 -m pytest -q tests/test_context_builder.py::test_build_router_context_exposes_private_tool_trace_as_internal_tool_context tests/test_context_builder.py::test_build_router_context_reads_precompacted_tool_context_segment tests/test_context_builder.py::test_build_router_context_exposes_tool_trace_result_summary_artifacts_as_turn_state_hints`(`3 passed`)를 통과했다.

## 2026-06-07 - validation 경고 해제 판단의 recency 기준 보강

- 작업 이름: 오래된 validation 경고가 최신 정상 실행을 다시 막지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록은 우선순위 정렬로 인해 최신 정상 실행 line이 오래된 route validation 경고 line보다 앞에 출력될 수 있다.
  - 기존 `internal_validation_removed_state_ids()`와 `internal_validation_clarified_state_ids()`는 line 순서대로 set을 갱신해, 최신 정상 실행이 먼저 나오고 오래된 경고가 뒤에 나오면 오래된 경고가 다시 살아나는 문제가 있었다.
  - `test_router_validation_removed_state_is_cleared_by_latest_success_even_if_line_appears_first`, `test_router_validation_clarified_state_is_cleared_by_latest_success_even_if_line_appears_first`를 추가해 해당 재현을 고정했다.
  - validation 경고 해제 판단을 state_id별 최신 이벤트 비교로 변경했다. `recency=latest`가 `older`보다 우선하고, 같은 recency 안에서는 기존 line 순서가 tie-breaker가 된다.
  - `test_router_fallback_reuses_state_when_latest_success_appears_before_older_removed_warning`를 추가해 실제 fallback 라우팅에서도 오래된 자동 연결 제거 경고가 최신 성공 실행을 막지 않는지 검증했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_router_agent.py::test_router_parses_internal_validation_removed_state_ids tests/test_router_agent.py::test_router_validation_removed_state_is_cleared_by_later_successful_route_context tests/test_router_agent.py::test_router_validation_removed_state_is_cleared_by_latest_success_even_if_line_appears_first tests/test_router_agent.py::test_router_validation_removed_state_survives_when_removal_is_latest tests/test_router_agent.py::test_router_parses_internal_validation_clarified_state_ids tests/test_router_agent.py::test_router_validation_clarified_state_is_cleared_by_later_successful_route_context tests/test_router_agent.py::test_router_validation_clarified_state_is_cleared_by_latest_success_even_if_line_appears_first tests/test_router_agent.py::test_router_ignores_unlinked_validation_guidance_for_state_id_sets`(`8 passed`), `python3 -m pytest -q tests/test_router_agent.py::test_router_fallback_does_not_reuse_validation_removed_state_for_implicit_follow_up tests/test_router_agent.py::test_router_fallback_reuses_state_when_later_successful_route_context_clears_removed_warning tests/test_router_agent.py::test_router_fallback_reuses_state_when_latest_success_appears_before_older_removed_warning tests/test_router_agent.py::test_router_fallback_allows_validation_removed_state_when_user_explicitly_names_target tests/test_router_agent.py::test_router_validation_removed_state_is_cleared_by_latest_success_even_if_line_appears_first tests/test_router_agent.py::test_router_validation_clarified_state_is_cleared_by_latest_success_even_if_line_appears_first`(`6 passed`), `python3 -m pytest -q tests/test_router_agent.py`(`131 passed`)를 통과했다.

## 2026-06-07 - tool trace 로그 형식 단일화 정리

- 작업 이름: 내부 도구 trace를 `tool_context` 세그먼트로만 노출하도록 정리
- 진행상황: 완료
- 진행내용:
  - 이전 수정 과정에서 긴 도구 trace 보존을 위해 `tool_call_trace=` 세그먼트와 `tool_context=` 세그먼트가 함께 남을 수 있는 중복 경로를 확인했다.
  - 라우터 컨텍스트에 노출되는 최종 계약은 이미 안전하게 축약된 `tool_context`이므로, 내부 행동 로그 생성에서 별도 `tool_call_trace=` 세그먼트를 추가하지 않도록 정리했다.
  - `build_internal_action_context()`는 기존 `slots/artifacts.tool_call_trace`와 `tool_context` 세그먼트를 모두 읽을 수 있어 기존 로그 호환성은 유지한다.
  - 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_preserves_compact_tool_trace_context_when_long tests/test_context_builder.py::test_build_router_context_reads_precompacted_tool_context_segment tests/test_context_builder.py::test_build_router_context_exposes_private_tool_trace_as_internal_tool_context -q`(`3 passed`)를 통과했다.

## 2026-06-07 - tool_context 단일 계약 후속 정리

- 작업 이름: 사용되지 않는 raw trace helper 제거
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그의 최종 공개 계약을 `tool_context=...` 세그먼트로 단일화한 뒤, 더 이상 호출되지 않는 `safe_internal_action_tool_trace_values()` helper가 남아 있는지 확인했다.
  - raw `tool_call_trace`를 별도 세그먼트로 만들 수 있다는 오해를 줄이기 위해 미사용 helper를 제거했다.
  - `build_internal_action_context()`의 기존 로그 호환 경로는 유지하되, 새 로그 생성 경로는 안전하게 축약된 `tool_context`만 남기는 구조로 정리했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1132 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 후보 자동 실행 방지 공통화

- 작업 이름: 출처 기반 후속 생성 요청도 위치 변경 확인 정책을 따르도록 보강
- 진행상황: 완료
- 진행내용:
  - 기존 라우터 fallback은 대부분의 후속 연결 경로에서 `candidate.is_cross_location`을 확인했지만, `그 메모를 할 일로 만들어줘`처럼 출처 후보를 새 메모/할 일/알림의 본문으로 쓰는 변환 경로는 공통 `context_link_for_candidate_intent()`의 `continue` 결과를 그대로 사용할 수 있었다.
  - 이 경우 다른 위치에서 조회한 메모/문서/작업 후보를 현재 위치에서 바로 변환 실행할 위험이 있으므로, 후보 기반 context link helper가 다른 위치 후보를 만나면 기본적으로 `clarify`를 반환하도록 바꿨다.
  - `test_router_fallback_cross_location_source_reference_creation_requires_confirmation`을 추가해 다른 위치 메모를 할 일로 만들라는 요청이 바로 실행되지 않고 `context_link=clarify`로 남는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_fallback_cross_location_source_reference_creation_requires_confirmation -q`(`1 passed`), `python3 -m pytest tests/test_router_agent.py -q`(`132 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`170 passed`), `python3 -m pytest tests/test_route_validation.py -q`(`162 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1136 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 출처 변환 검증 레이어 고정

- 작업 이름: 라우터가 만든 다른 위치 출처 변환 확인 요청을 실행 전 검증에서도 보존
- 진행상황: 완료
- 진행내용:
  - 라우터 fallback에서 다른 위치 출처 변환을 `context_link=clarify`로 바꾸더라도, 실제 봇 실행 전에는 `validate_route_context_link()`가 한 번 더 route와 linked state를 검증한다.
  - `그 메모 할일로 만들어줘`처럼 출처는 다른 위치 메모이고 목적은 새 할 일 생성인 경우, 검증 레이어가 이를 호환 불가로 제거하지 않고 확인 질문으로 유지해야 한다.
  - `test_validate_route_context_link_clarifies_cross_location_source_conversion`을 추가해 `linked_state_id`는 출처 메모 상태를 보존하고, `resolved_slots`에는 실행 입력인 `task_title`만 남기며, 사용자에게 다른 위치 작업을 여기서 이어갈지 묻는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clarifies_cross_location_source_conversion -q`(`1 passed`), `python3 -m pytest tests/test_route_validation.py -q`(`163 passed`), `python3 -m pytest tests/test_router_agent.py -q`(`132 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`170 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1139 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 출처 변환 승인 복원 고정

- 작업 이름: 확인 질문 승인 후 출처 변환 실행 슬롯 복원 검증
- 진행상황: 완료
- 진행내용:
  - 다른 위치 출처 변환은 첫 턴에서 `clarify`로 멈춘 뒤, 사용자가 `응`이라고 승인하면 저장된 pending context를 사용해 원래 실행 의도를 복원해야 한다.
  - 기존 승인 복원 테스트는 `task_id`, `document_id`, `url` 같은 ID/URL 슬롯 중심이라, `그 메모 할일로 만들어줘`에서 필요한 `task_title` 텍스트 슬롯이 승인 뒤 복원되는지 직접 고정하지 않았다.
  - `test_pending_context_approval_restores_source_conversion_text_slots`를 추가해 pending 상태의 `pending_resolved_slots.task_title`과 `pending_original_text`가 승인 route에 다시 들어가는지 검증했다.
  - 이 계약은 출처 상태는 `linked_state_id`로 유지하고, 실제 실행 입력은 `resolved_slots`로 전달한다는 분리를 승인 흐름까지 이어가기 위한 것이다.
  - 관련 검증으로 `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_restores_source_conversion_text_slots -q`(`1 passed`), `python3 -m pytest tests/test_route_validation.py -q`(`164 passed`), `python3 -m pytest tests/test_router_agent.py -q`(`132 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "continue_context or pending_context or context_link_confirmation" -q`(`11 passed, 140 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1139 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 내부 행동 최신성 라벨의 위치별 독립성 고정

- 작업 이름: 현재 위치와 다른 위치의 최신 내부 행동 후보를 서로 덮어쓰지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 라우터 컨텍스트는 현재 위치 후보와 다른 위치 후보를 함께 제공하므로, 전체 내부 행동 로그 중 하나만 `recency=latest`로 표시하면 다른 위치의 실제 최신 후보가 `older`로 밀릴 수 있다.
  - 이 경우 사용자가 채팅 위치를 바꾼 뒤 `다시해봐`, `이어서 해줘`처럼 말했을 때, 라우터가 다른 위치에서 이어갈 후보를 정확히 식별하지 못하거나 오래된 후보와 섞을 위험이 있다.
  - `test_build_router_context_marks_latest_internal_action_per_location`을 추가해 현재 위치의 최신 로그와 다른 위치의 최신 로그가 각각 `location_priority=current/latest`, `location_priority=cross_location/latest`로 표시되는지 검증했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_context_builder.py::test_build_router_context_marks_latest_internal_action_per_location`(`1 passed`), `python3 -m pytest -q tests/test_context_builder.py::test_build_router_context_marks_latest_internal_action_per_location tests/test_context_builder.py::test_build_router_context_includes_same_user_cross_location_internal_action_logs tests/test_context_builder.py::test_build_router_context_keeps_latest_cross_location_execution_result_when_current_logs_fill_limit tests/test_context_builder.py::test_build_router_context_keeps_actual_internal_action_recency_after_priority_sort`(`4 passed`), `python3 -m pytest -q tests/test_router_agent.py::test_router_validation_removed_state_is_cleared_by_latest_success_even_if_line_appears_first tests/test_router_agent.py::test_router_validation_clarified_state_is_cleared_by_latest_success_even_if_line_appears_first tests/test_router_agent.py::test_router_fallback_reuses_state_when_latest_success_appears_before_older_removed_warning`(`3 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1138 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 위치별 latest 동률 validation 판단 보강

- 작업 이름: 현재 위치와 다른 위치가 모두 latest일 때 오래된 validation 경고가 최신 성공을 덮지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 내부 행동 로그는 현재 위치와 다른 위치의 최신 로그를 각각 `recency=latest`로 표시한다.
  - 이때 같은 linked state에 대해 현재 위치의 최신 성공 실행 로그와 다른 위치의 오래된 route validation 경고가 모두 `latest`로 표시되면, 기존 라우터는 같은 rank 안에서 줄 순서만 보고 뒤에 나온 오래된 경고를 최신 이벤트로 오해할 수 있었다.
  - `latest_internal_validation_events()`의 비교 키에 `created_at`을 추가해, `recency`가 같을 때는 실제 로그 시각이 더 최신인 이벤트가 이기도록 수정했다.
  - `test_router_validation_removed_state_uses_created_at_when_each_location_has_latest`, `test_router_validation_clarified_state_uses_created_at_when_each_location_has_latest`를 추가해 removed/clarified validation 경고 모두에서 같은 문제가 재발하지 않도록 했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_router_agent.py::test_router_validation_removed_state_uses_created_at_when_each_location_has_latest tests/test_router_agent.py::test_router_validation_removed_state_is_cleared_by_latest_success_even_if_line_appears_first tests/test_router_agent.py::test_router_validation_removed_state_survives_when_removal_is_latest tests/test_router_agent.py::test_router_validation_clarified_state_is_cleared_by_latest_success_even_if_line_appears_first`(`4 passed`), `python3 -m pytest tests/test_router_agent.py -q`(`134 passed`), `python3 -m pytest tests/test_context_builder.py -q`(`70 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`171 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1142 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 버튼 승인 출처 변환 슬롯 전달 고정

- 작업 이름: Discord 확인 버튼 승인 경로에서도 텍스트 실행 슬롯을 보존
- 진행상황: 완료
- 진행내용:
  - 라우터와 실행 전 검증에서 다른 위치 출처 변환을 확인 질문으로 멈추고 승인 route를 복원하더라도, 실제 Discord 버튼 승인 경로가 `pending_resolved_slots.task_title`을 에이전트 실행 컨텍스트까지 전달하지 못하면 사용자가 버튼을 눌렀을 때 작업이 어긋날 수 있다.
  - `test_context_confirmation_button_approval_restores_cross_location_source_conversion_slots`를 추가해 다른 위치 메모를 현재 위치에서 할 일로 만들라는 pending 확인을 승인하면 `manage_task` dispatch가 실행되고, 원래 문장과 `task_title`이 그대로 `AgentContext.execution.resolved_slots`에 남는지 검증했다.
  - 이 테스트는 출처 상태(`linked_state_id`)와 실행 입력(`task_title`)의 분리가 Discord 버튼 승인 경로에서도 유지되는지 확인한다.
  - 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_context_confirmation_button_approval_restores_cross_location_source_conversion_slots -q`(`1 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "continue_context or context_confirmation_button or pending_context" -q`(`18 passed, 134 deselected`), `python3 -m pytest tests/test_route_validation.py -q`(`167 passed`), `python3 -m pytest tests/test_router_agent.py -q`(`134 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1147 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 다른 위치 후보의 같은 지명 새 주제 분리

- 작업 이름: 다른 위치 날씨 후보가 같은 지역의 새 일반 요청을 가로채지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 기존 매트릭스에는 현재 위치의 `원주 날씨` 후보 뒤 `원주 맛집 알려줘`가 새 요청으로 처리되는 케이스가 있었지만, 같은 후보가 다른 위치에 있을 때도 확인 질문으로 가로채지 않는지 직접 고정한 케이스는 없었다.
  - 사용자가 채팅 위치를 옮긴 상태에서는 같은 사용자 장기 맥락을 보존하되, 새 주제 요청을 다른 위치 작업으로 잘못 연결하지 않는 것이 핵심이므로 `cross_location_same_location_name_new_non_weather_topic_does_not_ask_to_continue_weather` 매트릭스 테스트를 추가했다.
  - 이 케이스는 다른 채널의 `원주 날씨` 후보가 있어도 현재 위치의 `원주 맛집 알려줘`는 `context_link=none`인 새 일반 요청으로 남아야 한다는 계약을 고정한다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_context_routing_matrix.py -k "same_location_name_new_non_weather_topic"`(`2 passed, 169 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1140 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 확인의 짧은 작업 동사 승인 복원

- 작업 이름: `응 검색해줘`, `응 요약해줘` 같은 자연스러운 승인 답변 처리
- 진행상황: 완료
- 진행내용:
  - 기존 승인 판정은 `검색`, `요약`, `설명`, `알려줘` 같은 단어를 새 요청 marker로 보수적으로 취급해, pending 확인 질문에 대한 `응 검색해줘` 같은 자연스러운 답변도 승인으로 복원하지 못할 수 있었다.
  - `응 OpenAI 검색해줘`처럼 새 query가 명확한 문장은 새 요청으로 남겨야 하지만, `응 검색해줘`처럼 새 대상 없이 원래 pending intent의 실행 동사만 있는 문장은 사용자의 승인 의사에 더 가깝다.
  - pending approval matcher에 intent별 일반 승인 동사 suffix를 추가해, `web_search`의 `검색해줘`, `analyze_document`의 `요약해줘/분석해줘`처럼 새 대상 없는 짧은 답변만 pending 확인 승인으로 복원하도록 했다.
  - `test_pending_context_approval_accepts_generic_web_search_action_without_new_query`, `test_pending_context_approval_rejects_generic_web_search_action_with_new_query`, `test_pending_context_approval_accepts_generic_document_summary_action_without_new_target`를 추가해 승인/새 요청 경계를 고정했다.
  - 맥락 매트릭스에는 `positive_prefix_generic_web_search_restores_pending_search_retry_approval`을 추가해 실제 pending web search retry가 `응 검색해줘`로 복원되는지 검증했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_route_validation.py::test_pending_context_approval_accepts_generic_web_search_action_without_new_query tests/test_route_validation.py::test_pending_context_approval_rejects_generic_web_search_action_with_new_query tests/test_route_validation.py::test_pending_context_approval_accepts_generic_document_summary_action_without_new_target tests/test_context_routing_matrix.py -k "generic_web_search"`(`3 passed, 172 deselected`), `python3 -m pytest -q tests/test_context_routing_matrix.py -k "positive_prefix_generic_web_search"`(`1 passed, 171 deselected`)를 통과했다.
  - Bot 통합 경로에는 `test_assistant_bot_generic_search_approval_restores_pending_web_search`를 추가해 `handle_message()`가 `응 검색해줘`를 pending web search 승인으로 복원하고, 원래 query와 `pending_original_text`를 실행 컨텍스트에 보존한 뒤 pending 상태를 만료하는지 검증했다.
  - 관련 통합 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_assistant_bot_generic_search_approval_restores_pending_web_search`(`1 passed`), `python3 -m pytest -q tests/test_bot_helpers.py -k "chat_approval or generic_search_approval or pending_context_approval"`(`5 passed, 148 deselected`)를 통과했다.
  - 같은 통합 테스트를 확장해, 실행 결과를 내부 행동 로그로 기록했을 때 `route`, `linked_state_id`, 원래 query가 남고 다음 턴 `build_router_context()`에서 `internal_action_context_by_linked_state()`로 복원되는지 확인했다.
  - 추가 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py -k "generic_search_approval or record_internal_action_result_logs_cross_location_retry_approval_context or state_candidate_button_selection"`(`3 passed, 150 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1152 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 문서 요약 승인 통합 검증

- 작업 이름: `응 요약해줘`가 저장 문서 분석으로 이어지는 실제 Bot 경로 고정
- 진행상황: 완료
- 진행내용:
  - 검색 pending 승인과 같은 방식으로, 문서 분석 pending 확인 질문 뒤 `응 요약해줘`가 실제 저장 문서 분석 경로까지 이어지는지 확인했다.
  - 처음에는 turn state만 만들고 실제 문서를 저장하지 않아 `DocumentAnalysisAgent`가 linked document를 찾지 못하고 비전/OCR 잔여 용량 조회로 빠지는 문제를 확인했다.
  - 테스트를 실제 `MemoryStore.save_document()`로 저장한 문서 기반으로 바꿔, pending 상태의 `document_id/document_ids`가 `handle_message()`에서 복원되고 `DocumentAnalysisAgent.analyze()`가 저장 문서 요약을 수행하는지 고정했다.
  - `test_assistant_bot_generic_summary_approval_restores_pending_document_analysis`를 추가해 `응 요약해줘`가 `context_link=continue`, linked document state, 원래 `pending_original_text`를 보존하고, 실행 결과를 내부 행동 로그로 기록한 뒤 다음 턴 라우터 컨텍스트에서 document id를 복원할 수 있는지 검증했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_assistant_bot_generic_summary_approval_restores_pending_document_analysis`(`1 passed`), `python3 -m pytest -q tests/test_bot_helpers.py -k "generic_search_approval or generic_summary_approval or chat_approval"`(`6 passed, 150 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1155 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 조작형 pending 승인 내부 로그 복원 검증

- 작업 이름: `응 완료해줘` 같은 위험 action 승인도 대상 ID를 다음 컨텍스트에 남기는지 확인
- 진행상황: 완료
- 진행내용:
  - 검색/문서처럼 조회형 작업은 내부 로그 복원을 검증했지만, `완료`, `삭제` 같은 조작형 작업은 잘못 연결되면 피해가 크므로 같은 수준의 내부 행동 기록 검증이 필요했다.
  - 기존 `test_assistant_bot_generic_task_approval_restores_pending_task`를 확장해 `응 완료해줘`가 pending task를 승인한 뒤 `route`, `linked_state_id`, `task_id/task_ids`를 내부 행동 로그에 남기고, 다음 턴 `build_router_context()`에서 같은 linked state 기준으로 복원되는지 확인했다.
  - 이 테스트는 새 대상 없는 짧은 승인형 action만 복원하고, `응 장보기 완료해줘`처럼 새 대상이 있는 문장은 기존 route validation 단위 테스트에서 계속 거부한다는 경계를 보완한다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_assistant_bot_generic_task_approval_restores_pending_task`(`1 passed`), `python3 -m pytest -q tests/test_bot_helpers.py -k "generic_task_approval or generic_reminder_approval or generic_search_approval or generic_summary_approval"`(`4 passed, 152 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1155 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - cross-location 조작형 pending 승인 고정

- 작업 이름: 채팅 위치가 바뀐 뒤 `응 완료해줘`가 확인된 작업에만 실행되는지 검증
- 진행상황: 완료
- 진행내용:
  - 기존 조작형 pending 승인 테스트는 같은 위치 기준이었으므로, 사용자가 다른 채팅 위치에서 이어가기 확인을 승인하는 실제 목표 시나리오를 더 직접적으로 검증할 필요가 있었다.
  - `test_assistant_bot_generic_task_approval_restores_pending_task`를 cross-location 구조로 강화했다. 대상 task state는 DM에 있고, pending 확인 상태는 서버 채널에 있으며, 사용자의 `응 완료해줘`는 pending 확인을 거친 뒤에만 DM의 task state를 linked state로 실행한다.
  - 실행 컨텍스트에 source conversation id가 보존되고, 내부 행동 로그와 다음 턴 router context에서 같은 `linked_state_id`와 `task_id/task_ids`를 복원할 수 있는지 확인했다.
  - 새 대상이 있는 `응 장보기 완료해줘`, `응 물 마시기 알림 삭제해줘`는 route validation 단위 테스트에서 계속 pending 승인으로 소비하지 않도록 유지한다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_assistant_bot_generic_task_approval_restores_pending_task`(`1 passed`), `python3 -m pytest -q tests/test_bot_helpers.py -k "generic_task_approval or generic_reminder_approval or chat_approval_allows_cross_location_pending_context"`(`3 passed, 154 deselected`), `python3 -m pytest -q tests/test_route_validation.py -k "generic_task_action or generic_reminder_action"`(`4 passed, 167 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1156 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 응답 작성용 private route metadata 빈 껍데기 제거

- 작업 이름: 사용자-facing 모델 입력에서 내부 route metadata 제거 후 남는 빈 구조 정리
- 진행상황: 완료
- 진행내용:
  - 응답 작성 계층은 `context_link`, `linked_state_id`, `resolved_slots`, `pending_*` 같은 내부 route metadata를 사용자-facing 구조화 결과에서 제거한다.
  - 하지만 private key만 들어 있던 nested dict/list는 제거 뒤 `{}` 또는 `[{}]` 같은 빈 껍데기로 남을 수 있어, 최종 응답 작성 모델 입력에 불필요한 잡음이 생길 수 있었다.
  - `test_response_private_route_filter_drops_empty_nested_containers`를 추가해 facts, slots, items 안의 private-only nested dict/list가 완전히 제거되어야 한다는 계약을 고정했다.
  - `sanitize_private_route_values()`가 private key 제거 뒤 빈 dict/list/tuple을 버리도록 보강했다. 안전한 값이 섞인 구조는 유지하고, 내부 metadata만 담긴 빈 구조만 제거한다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_response_composer.py::test_response_private_route_filter_drops_empty_nested_containers tests/test_response_composer.py`(`37 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1158 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 확인의 작업/알림 동사 승인 복원

- 작업 이름: `응 완료해줘`, `응 삭제해줘` 같은 작업/알림 승인 답변 처리
- 진행상황: 완료
- 진행내용:
  - 기존 generic pending action approval은 문서, 웹검색, URL, 날씨, 기억 조회 중심으로 구성되어 있어 `manage_task`, `manage_reminder`의 짧은 승인 답변을 놓칠 수 있었다.
  - 사용자가 확인 질문에 `응 완료해줘`, `응 삭제해줘`처럼 답하면 새 대상이 없는 한 pending 작업/알림 실행 의도를 승인한 것으로 보는 편이 자연스럽다.
  - `GENERIC_PENDING_ACTION_APPROVAL_SUFFIXES`에 `manage_task`, `manage_reminder`용 짧은 동사 suffix를 추가했다.
  - `test_pending_context_approval_accepts_generic_task_action_without_new_target`, `test_pending_context_approval_rejects_generic_task_action_with_new_target`, `test_pending_context_approval_accepts_generic_reminder_action_without_new_target`, `test_pending_context_approval_rejects_generic_reminder_action_with_new_target`를 추가해 대상 없는 승인과 새 대상 포함 요청의 경계를 고정했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_route_validation.py::test_pending_context_approval_accepts_generic_task_action_without_new_target tests/test_route_validation.py::test_pending_context_approval_rejects_generic_task_action_with_new_target tests/test_route_validation.py::test_pending_context_approval_accepts_generic_reminder_action_without_new_target tests/test_route_validation.py::test_pending_context_approval_rejects_generic_reminder_action_with_new_target`(`4 passed`), `python3 -m pytest tests/test_route_validation.py -q`(`171 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`172 passed`), `python3 -m pytest tests/test_router_agent.py -q`(`134 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1152 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - pending 작업/알림 승인 통합 경로 고정

- 작업 이름: `handle_message()`에서 작업/알림 pending 승인 복원 검증
- 진행상황: 완료
- 진행내용:
  - 라우트 검증 단위 테스트만으로는 `응 완료해줘`, `응 삭제해줘` 같은 답변이 실제 Discord 메시지 처리 경로에서 에이전트 실행 컨텍스트까지 보존되는지 증명하기 어렵다.
  - `FakeGenericTaskApprovalRouter`, `FakeGenericReminderApprovalRouter`를 추가해 라우터가 새 대상 없이 `manage_task`, `manage_reminder`로 판단한 상황을 재현했다.
  - `test_assistant_bot_generic_task_approval_restores_pending_task`, `test_assistant_bot_generic_reminder_approval_restores_pending_reminder`를 추가해 pending 상태의 원래 문장, linked state, `task_id`/`reminder_id` 슬롯이 dispatch 직전 `AgentContext.execution`에 복원되는지 검증했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_assistant_bot_generic_task_approval_restores_pending_task tests/test_bot_helpers.py::test_assistant_bot_generic_reminder_approval_restores_pending_reminder`(`2 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "generic_task_approval or generic_reminder_approval or generic_search_approval or pending_context_approval" -q`(`3 passed, 152 deselected`), `python3 -m pytest tests/test_route_validation.py -q`(`171 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`172 passed`)를 통과했다.
  - 전체 검증 중 기존 문서 요약 pending 승인 통합 테스트가 한 차례 실패했으나, 현재 작업트리 기준 단일 재검증에서 `python3 -m pytest -q tests/test_bot_helpers.py::test_assistant_bot_generic_summary_approval_restores_pending_document_analysis`(`1 passed`)를 통과했고, 문서 분석 특수 경로도 같은 맥락 복원 계약을 유지하는지 확인했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1155 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 새 유틸리티 요청의 pending 확인 오인 방지

- 작업 이름: `그거 말고 지금 몇시야`가 pending 작업 승인으로 소비되지 않도록 통합 경로 고정
- 진행상황: 완료
- 진행내용:
  - 사용자가 후속 작업 확인 질문에 답하지 않은 상태에서 `그거 말고 지금 몇시야`처럼 이전 맥락을 거부하고 새 유틸리티 요청을 하면, 오래된 pending 작업을 승인하지 않고 현재 시간 요청으로 처리해야 한다.
  - `FakeCurrentTimeRouter`를 추가하고 `test_assistant_bot_new_time_request_expires_pending_context_without_approval`를 추가해 `handle_message()` 전체 경로에서 `current_time`이 실행되고, `context_link=none`, `linked_state=None`, 빈 `resolved_slots`로 남는지 검증했다.
  - 같은 테스트에서 기존 pending context state가 만료되고, 내부 로그에 “새 요청 라우팅으로 이전 후속 작업 확인 대기를 모두 만료함” 기록이 남는지 확인했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_assistant_bot_new_time_request_expires_pending_context_without_approval`(`1 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "new_time_request_expires_pending_context or expires_stale_pending_context_on_new_request or generic_task_approval or generic_reminder_approval or generic_summary_approval" -q`(`5 passed, 152 deselected`), `python3 -m pytest tests/test_route_validation.py -q`(`171 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`172 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1156 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 새 유틸리티 요청의 삭제 확인 오인 방지

- 작업 이름: `응 확인 지금 몇시야`가 기억 삭제 승인으로 소비되지 않도록 통합 경로 고정
- 진행상황: 완료
- 진행내용:
  - 기억 삭제 확인 대기는 `handle_message()`에서 라우터보다 먼저 처리되므로, 새 요청 오인 방지 테스트를 pending context와 별도로 가져가야 한다.
  - `test_assistant_bot_new_time_request_expires_pending_memory_delete_without_approval`를 추가해 전체 기억 삭제 확인 대기가 있는 상태에서 `응 확인 지금 몇시야`를 보내면 삭제가 실행되지 않고 `current_time`으로 라우팅되는지 검증했다.
  - 같은 테스트에서 기존 삭제 확인 대기가 새 요청 라우팅으로 만료되고, 저장된 메모는 그대로 남으며, 내부 로그에 `pending_memory_deletions=1`이 기록되는지 확인했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_assistant_bot_new_time_request_expires_pending_memory_delete_without_approval`(`1 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "new_time_request_expires_pending or stale_general_pending or keeps_pending_delete_for_positive_prefixed_new_request or confirmation_helpers" -q`(`5 passed, 153 deselected`), `python3 -m pytest tests/test_route_validation.py -q`(`171 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`172 passed`)를 통과했다.
  - 전체 검증 중 응답 composer의 private route metadata 필터 테스트가 한 차례 실패했으나, 현재 작업트리 기준 단일 재검증에서 `python3 -m pytest -q tests/test_response_composer.py::test_response_private_route_filter_drops_empty_nested_containers`(`1 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1158 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 메모 대기 상태의 새 유틸리티 요청 오저장 방지

- 작업 이름: `지금 몇시야`가 다음 메모 본문으로 저장되지 않도록 Discord/CLI 경로 보강
- 진행상황: 완료
- 진행내용:
  - 메모 대기 상태는 다음 사용자 메시지 1개를 저장하도록 설계되어 있지만, `지금 몇시야`, `도움말 알려줘`, `봇 상태 알려줘`처럼 명백한 유틸리티 요청까지 메모로 저장하면 사용자의 의도와 크게 어긋난다.
  - `is_pending_memory_capture_new_action_request()`를 추가해 현재 시간, 도움말, 상태, 오늘 브리핑, 대화 초기화뿐 아니라 날씨, 웹검색, 할 일, 알림처럼 명시적 새 작업으로 분류되는 요청을 감지하도록 했다.
  - `recall` 휴리스틱은 자연문 메모 본문도 보수적으로 잡을 수 있으므로, `메모 3 보여줘`, `문서 찾아줘`처럼 기억/문서 대상과 조회 action이 함께 있을 때만 새 작업 요청으로 양보하도록 좁혔다.
  - Discord `handle_pending_memory_capture()`와 로컬 CLI `handle_local_pending_memory_capture()`가 이 요청을 만나면 메모 대기 상태를 만료하고 `None`을 반환해 일반 라우팅이 이어지도록 했다.
  - `test_assistant_bot_new_time_request_expires_pending_memory_capture_without_saving`을 추가해 Discord 전체 메시지 경로에서 `지금 몇시야`가 `current_time`으로 실행되고 메모가 저장되지 않는지 검증했다.
  - `test_assistant_bot_new_weather_request_expires_pending_memory_capture_without_saving`을 추가해 Discord 전체 메시지 경로에서 `서울 날씨 알려줘`가 `weather`로 실행되고 메모가 저장되지 않는지 검증했다.
  - `test_cli_pending_memory_capture_yields_to_new_action_request`를 추가해 로컬 CLI도 같은 판단으로 메모 대기 상태를 만료하고 저장하지 않는지 검증했다.
  - `test_pending_memory_capture_yields_to_explicit_new_action_requests`, `test_pending_memory_capture_keeps_plain_memory_content_or_memory_control_text`를 추가해 메모 대기 중 명시적 새 작업 요청은 양보하고, `내일 오전에 병원 예약`, `나는 오전에 집중이 잘 된다` 같은 자연스러운 메모 본문은 계속 저장 후보로 남는지 고정했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_pending_memory_capture_yields_to_explicit_new_action_requests tests/test_bot_helpers.py::test_pending_memory_capture_keeps_plain_memory_content_or_memory_control_text`(`11 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "pending_memory_capture or new_time_request_expires_pending or new_weather_request_expires_pending" -q`(`18 passed, 153 deselected`), `python3 -m pytest tests/test_cli.py -k "pending_memory_capture or stale_confirmations" -q`(`2 passed, 81 deselected`), `python3 -m pytest tests/test_router_heuristics.py -q`(`51 passed`), `python3 -m pytest tests/test_route_validation.py -q`(`179 passed`)를 통과했다.
  - 전체 검증 중 CLI route preview의 pending 검색 승인 복원 테스트가 한 차례 실패했으나, 현재 작업트리 기준 단일 재검증에서 `python3 -m pytest -q tests/test_cli.py::test_preview_model_route_details_restores_generic_pending_search_approval -vv`(`1 passed`)를 통과했다.
  - `python3 -m ruff check assistant_bot/cli.py --fix`로 import 정렬을 정리했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1181 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 모델 라우팅 미리보기의 generic pending 승인 복원

- 작업 이름: `route --model`과 공통 route validation의 짧은 승인 동사 처리 보강
- 진행상황: 완료
- 진행내용:
  - 운영자가 `assistant-admin route --model`로 라우팅을 재현할 때도 Discord 실행 경로와 같은 pending 승인 복원 규칙을 확인할 수 있어야 한다.
  - 기존 공통 검증은 `응 검색해줘` 같은 generic 승인 문장을 지원했지만, 라우터 모델이 이미 `context_link=retry/continue/modify`를 반환한 경우에는 순수한 `응`, `네` 같은 plain approval만 허용해 pending 복원이 끊길 수 있었다.
  - `matching_pending_context_approval_state()`가 자동 연결 route에서도 원래 pending intent와 맞는 generic approval suffix를 승인으로 인정하도록 보강했다.
  - `test_pending_context_approval_accepts_generic_web_search_action_with_model_retry_link`를 추가해 모델이 이미 `web_search/retry`를 낸 경우에도 pending의 `query`, `linked_state_id`, `pending_original_text`가 복원되는지 고정했다.
  - `test_preview_model_route_details_restores_generic_pending_search_approval`를 추가해 CLI 모델 라우팅 미리보기에서도 `응 검색해줘`가 pending 검색 재시도를 정확히 복원하는지 검증했다.
  - 관련 검증으로 `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_accepts_generic_web_search_action_with_model_retry_link tests/test_cli.py::test_preview_model_route_details_restores_generic_pending_search_approval -q`(`2 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_cli.py -q`(`255 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1162 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - generic pending 승인 복원의 intent별 공통 검증 확대

- 작업 이름: 문서/할 일/알림 모델 route에서도 짧은 승인 동사 복원 고정
- 진행상황: 완료
- 진행내용:
  - 직전 보강은 웹검색 재시도 케이스를 중심으로 검증했으나, 같은 코드 경계가 문서 요약, 할 일 완료, 알림 삭제 같은 다른 intent에서도 반복될 수 있었다.
  - `test_pending_context_approval_accepts_generic_action_with_model_context_link`를 parametrized 테스트로 추가했다.
  - 라우터 모델이 이미 `analyze_document/continue`, `manage_task/continue`, `manage_reminder/continue`를 반환한 경우에도 `응 요약해줘`, `응 완료해줘`, `응 삭제해줘`가 pending의 원래 대상 슬롯과 원문을 복원하는지 확인했다.
  - 새 대상이 붙은 요청을 pending 승인으로 소비하지 않는 기존 거부 테스트는 그대로 유지해, 승인 복원과 새 요청 분리를 함께 보호한다.
  - 관련 검증으로 `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_accepts_generic_action_with_model_context_link tests/test_route_validation.py -q`(`178 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "generic_search_approval or generic_summary_approval or generic_task_approval or generic_reminder_approval" -q`(`4 passed, 156 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1166 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 조회형 generic pending 승인 복원 검증 확대

- 작업 이름: 웹 URL, 날씨, 기억 조회/목록 route의 짧은 승인 동사 복원 고정
- 진행상황: 완료
- 진행내용:
  - generic pending approval suffix는 `web_url`, `weather`, `recall`, `list_memory`에도 정의되어 있으므로, 문서/작업/알림뿐 아니라 조회형 intent도 모델 route가 이미 `continue/retry`를 반환한 상황에서 같은 복원 계약을 가져야 한다.
  - `test_pending_context_approval_accepts_generic_action_with_model_context_link`에 `응 읽어줘`, `응 다시 알려줘`, `응 보여줘`, `응 목록 보여줘` 케이스를 추가했다.
  - 각 케이스는 pending 상태의 `url`, `location`, `memory_id`, `memory_scope` 같은 대상 슬롯과 `pending_original_text`가 복원되는지 확인한다.
  - 관련 검증으로 `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_accepts_generic_action_with_model_context_link -q`(`7 passed`), `python3 -m pytest tests/test_route_validation.py -q`(`179 passed`)를 통과했다.
  - 전체 검증 중 메모 대기 상태 본문 판별 테스트가 한 차례 실패했으나, 현재 작업트리 기준 재검증에서 `python3 -m pytest tests/test_bot_helpers.py::test_pending_memory_capture_yields_to_explicit_new_action_requests tests/test_bot_helpers.py::test_pending_memory_capture_keeps_plain_memory_content_or_memory_control_text -q`(`11 passed`)를 통과했고, 이어서 전체 테스트도 정상 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1181 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 후보 선택 버튼 실패 경로의 내부 맥락 보존

- 작업 이름: 잘못된 후보 번호 선택 시 pending 원문과 후보 단서 기록
- 진행상황: 완료
- 진행내용:
  - URL 후보 선택 버튼과 후속 작업 후보 선택 버튼은 성공/취소 경로에서는 실행 컨텍스트와 내부 행동 로그를 남기고 있었지만, 선택 번호가 범위를 벗어난 실패 경로는 어떤 pending 흐름에서 실패했는지 단서가 약했다.
  - `run_selected_url_candidate()`의 잘못된 index 결과에 `context_link=clarify`, `pending_original_text`, `pending_candidate_urls`, `pending_candidate_url_titles`, `resolved_slots.selected_index`, `resolved_slots.candidate_count`를 남기도록 했다.
  - `run_selected_state_candidate()`의 잘못된 index 결과에도 `context_link=clarify`, `pending_original_text`, `pending_candidate_state_ids`, `resolved_slots.selected_index`, `resolved_slots.candidate_count`를 남기도록 했다.
  - `selected_index`와 `candidate_count`는 사용자 기능 슬롯이 아니라 내부 route/debug 값이므로 top-level slot이 아니라 `resolved_slots` 안에만 보존해 agent catalog 계약을 지키도록 했다.
  - `test_url_candidate_button_invalid_index_preserves_pending_context`, `test_state_candidate_button_invalid_index_preserves_pending_context`를 추가해 pending 상태가 만료되지 않고, 응답 작성 execution context와 내부 로그에 원래 요청/후보/선택 번호가 남는지 검증했다.
  - 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_url_candidate_button_invalid_index_preserves_pending_context tests/test_bot_helpers.py::test_state_candidate_button_invalid_index_preserves_pending_context -q`(`2 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "candidate_button or confirmation_button or attachment_save_rejection_preserves_pending_filename_context" -q`(`18 passed, 159 deselected`)를 통과했다.
  - 전체 검증 중 fact context slot 동기화 테스트가 한 차례 실패했으나, 현재 작업트리 기준 단일 재검증에서 `python3 -m pytest tests/test_agent_registry.py::test_registry_fact_context_slot_keys_match_turn_state_inference_keys -q`(`1 passed`)를 통과했고, 전체 테스트 재실행도 정상 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1187 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 메모 대기 취소 표현과 새 요청 혼합 분리

- 작업 이름: `메모 취소 말고 서울 날씨 알려줘`를 취소 응답으로 소비하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 메모 대기 상태에서 `메모 취소 말고 서울 날씨 알려줘`, `메모 그만하고 OpenAI 검색해줘`처럼 취소 표현 뒤에 새 요청이 붙은 문장은 단순 취소가 아니라 새 요청으로 이어져야 한다.
  - `handle_pending_memory_capture()`와 로컬 CLI 메모 대기 처리 순서를 새 작업 요청 감지 후 취소 감지로 바꿨다.
  - `pending_memory_capture_effective_action_text()`를 추가해 `말고`, `대신`, `그리고`, `하고` 뒤의 새 요청 부분을 기준으로 다시 라우팅 판단하도록 했다.
  - `test_pending_memory_capture_yields_to_explicit_new_action_requests`에 취소 표현과 새 요청이 섞인 문장을 추가했다.
  - `test_assistant_bot_cancel_phrase_with_new_weather_request_expires_memory_capture_without_cancel_reply`를 추가해 Discord 전체 경로에서 `메모 취소 말고 서울 날씨 알려줘`가 `weather`로 실행되고 `메모 대기 취소` 응답으로 끝나지 않는지 검증했다.
  - CLI의 `test_cli_pending_memory_capture_yields_to_new_action_request`도 같은 혼합 문장으로 검증하도록 갱신했다.
  - 관련 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_pending_memory_capture_yields_to_explicit_new_action_requests tests/test_bot_helpers.py::test_pending_memory_capture_keeps_plain_memory_content_or_memory_control_text tests/test_bot_helpers.py::test_assistant_bot_cancel_phrase_with_new_weather_request_expires_memory_capture_without_cancel_reply`(`15 passed`), `python3 -m pytest -q tests/test_cli.py::test_cli_pending_memory_capture_yields_to_new_action_request`(`1 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "memory_capture or new_time_request_expires_pending or new_weather_request_expires_pending" -q`(`23 passed, 152 deselected`), `python3 -m pytest tests/test_cli.py -k "pending_memory_capture or stale_confirmations" -q`(`2 passed, 81 deselected`), `python3 -m pytest tests/test_router_heuristics.py -q`(`51 passed`), `python3 -m pytest tests/test_route_validation.py -q`(`179 passed`)를 통과했다.
  - 전체 검증 중 후보 선택 실패 응답의 내부 슬롯(`pending_candidate_*`, `selected_index`, `candidate_count`)이 agent registry의 내부 컨텍스트 키 계약에 빠져 있어 결과 로그가 기록되지 않는 문제를 확인했다.
  - 해당 키를 `FACT_CONTEXT_SLOT_KEYS`, `INTERNAL_RESULT_SLOT_KEYS`, `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`에 맞춰 추가해 내부 행동 로그에는 남기되 사용자 응답에는 노출되지 않도록 정리했다.
  - 추가 검증으로 `python3 -m pytest -q tests/test_agent_registry.py::test_registry_fact_context_slot_keys_match_turn_state_inference_keys tests/test_bot_helpers.py::test_url_candidate_button_invalid_index_preserves_pending_context tests/test_bot_helpers.py::test_state_candidate_button_invalid_index_preserves_pending_context`(`3 passed`), `python3 -m pytest -q tests/test_response_composer.py -k "private_route"`(`12 passed, 24 deselected`), `python3 -m pytest tests/test_agent_registry.py tests/test_response_composer.py -q`(`110 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "candidate_button_invalid_index or candidate_selection_button or url_candidate" -q`(`9 passed, 168 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1187 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 후보 선택 debug key의 private 응답 계약 고정

- 작업 이름: `selected_index`, `candidate_count` 사용자 노출 방지 계약 강화
- 진행상황: 완료
- 진행내용:
  - 후보 선택 실패 경로에서 내부 맥락 복원을 위해 `selected_index`, `candidate_count`를 `resolved_slots`에 남기도록 했으므로, 이 값들이 내부 route/debug metadata로 계속 취급되어야 한다.
  - `test_internal_route_context_keys_are_private_for_response_composer`의 route/debug key 판정에 `selected_index`, `candidate_count`를 명시적으로 포함했다.
  - `test_response_private_route_keys_are_filtered_from_both_result_and_execution_context`가 `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS` 전체를 검사하므로, 두 키가 응답 작성 컨텍스트에서 제거되는 계약도 함께 확인된다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_internal_route_context_keys_are_private_for_response_composer tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context -q`(`2 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_response_composer.py -q`(`110 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1187 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - registry handler의 실행 컨텍스트 참조 계약 강화

- 작업 이름: 새 전문 에이전트 추가 시 `context.execution` 누락 방지
- 진행상황: 완료
- 진행내용:
  - 기존 테스트는 현재 전문 에이전트 메서드 호출 목록을 하드코딩해 `execution_context=context.execution` 전달 여부를 확인했다.
  - 새 intent handler가 추가되면 이 하드코딩 목록을 깜빡할 수 있으므로, `handlers` dict를 AST로 읽어 순수 유틸리티 intent를 제외한 모든 registry handler 함수가 본문에서 `context.execution`을 참조하는지 검사하는 `test_registry_non_utility_handlers_reference_execution_context`를 추가했다.
  - `registry_handler_functions_by_intent()`, `function_references_context_execution()` helper를 추가해 handler dict와 함수 본문을 직접 대조한다.
  - 새 에이전트를 추가할 때 handler가 `context.execution`을 전문 에이전트에 넘기거나 직접 활용하지 않으면 테스트가 실패하므로, 라우터가 고른 linked state/resolved slots가 실행 단계에서 사라지는 회귀를 줄일 수 있다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_registry_non_utility_handlers_reference_execution_context tests/test_agent_registry.py::test_registry_handlers_pass_execution_context_to_context_aware_agents -q`(`2 passed`), `python3 -m pytest tests/test_agent_registry.py -q`(`75 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1191 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 대화 회상형 질문의 작업 맥락 오염 방지

- 작업 이름: `아까 뭐 먹었지`, `방금 뭐라고 했지`를 최근 작업 상태와 분리
- 진행상황: 완료
- 진행내용:
  - `아까`, `방금` 같은 후속 참조 단어가 포함되어 있어도, 사용자가 작업 상태를 이어가려는 것이 아니라 과거 대화 내용을 떠올리는 질문일 수 있다.
  - `asks_unrelated_conversation_recall_request()`를 추가해 명시적 메모/문서/파일/할 일/알림/날씨/웹 대상이 없는 대화 회상형 질문을 작업 후보 자동 연결 대상에서 제외했다.
  - `build_current_message_context()`가 이 신호를 `unrelated_conversation_recall_request=True`와 `decision_hint=likely_new_request_do_not_link_previous_state`로 라우터 프롬프트에 전달하도록 했다.
  - `context_aware_fallback_route()`에도 같은 방어선을 넣어 모델이나 context hint가 흔들려도 fallback이 최근 작업 상태로 강제 연결하지 않도록 했다.
  - `test_context_routing_matrix`에 `아까 뭐 먹었지`, `방금 뭐라고 했지`가 최근 할 일 후보와 연결되지 않는 회귀 케이스를 추가했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`174 passed`), `python3 -m pytest tests/test_context_builder.py -k "current_message_context" -q`(`6 passed, 65 deselected`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`558 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "context or routing or pending" -q`(`107 passed, 70 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1191 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 후보 선택 debug 슬롯의 실행 route_context 분리

- 작업 이름: `selected_index`, `candidate_count`가 다음 턴 실행 슬롯처럼 복원되지 않도록 경계 보강
- 진행상황: 완료
- 진행내용:
  - 후보 선택 버튼 실패 경로에서 `selected_index`, `candidate_count`는 사용자가 누른 번호와 후보 개수를 설명하는 debug 값이지, 다음 턴 전문 에이전트가 실행할 대상 슬롯이 아니다.
  - 기존 구조는 이 값들을 private metadata로 처리하고 라우터 파서도 실행 슬롯으로 복원하지 않았지만, 내부 행동 로그의 `route.resolved_slots`에는 보일 수 있어 라우터 모델이 대상 단서처럼 오해할 여지가 있었다.
  - `INTERNAL_ACTION_ROUTE_DEBUG_KEYS`를 추가하고, `safe_internal_action_route_values()`와 `safe_internal_action_route_values_from_result()`가 `selected_index`, `candidate_count`를 `route.resolved_slots`에서 제외하도록 변경했다.
  - debug 값은 응답 작성 private metadata와 내부 진단 정보로는 남길 수 있지만, `route_context`에는 실제 확인/실행 복원에 필요한 pending 후보 URL/state ID, 원래 요청, ID/URL/query 같은 대상 슬롯만 남긴다.
  - `test_internal_action_route_values_keep_debug_slots_out_of_executable_route_context`, `test_internal_action_route_values_from_result_keep_debug_slots_out_of_executable_route_context`를 추가했다.
  - 후보 선택 실패 테스트의 기대값도 `selected_index`가 로그 route prefix에 섞이지 않는지 확인하도록 조정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_internal_action_route_values_keep_debug_slots_out_of_executable_route_context tests/test_bot_helpers.py::test_internal_action_route_values_from_result_keep_debug_slots_out_of_executable_route_context tests/test_bot_helpers.py::test_url_candidate_button_invalid_index_preserves_pending_context tests/test_bot_helpers.py::test_state_candidate_button_invalid_index_preserves_pending_context -q`(`4 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_route_validation.py tests/test_response_composer.py tests/test_agent_registry.py -q`(`495 passed`), `python3 -m pytest tests/test_bot_helpers.py -q`(`179 passed`)를 통과했다.
  - 현재 작업트리 기준 전체 검증으로 `python3 -m pytest -q`(`1197 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 대화 회상/맥락 차단 표현의 자동 연결 방지 확대

- 작업 이름: `아까 어디였지`, `그거랑 상관없이 점심 추천해줘`를 최근 작업과 분리
- 진행상황: 완료
- 진행내용:
  - 추가 재현에서 `아까 어디였지`, `아까 몇시에 봤지`, `방금 본 영화 추천해줘` 같은 일반 대화/추천 질문이 최근 할 일 후보에 붙는 오판을 확인했다.
  - `asks_unrelated_conversation_recall_request()`의 질문 표지를 `어디`, `언제`, `몇시`, `몇분`, `본`, `봤지`, `먹은`까지 확장해 대화 회상형 질문을 더 넓게 분리했다.
  - `그거랑 상관없이`, `관련없이`, `무시하고`처럼 사용자가 이전 맥락을 명시적으로 끊는 표현을 context rejection 신호와 후보 제외 기준에 추가했다.
  - 후보 제외 기준은 해당 표현 앞부분에 후보 제목이 직접 없더라도 `그거` 같은 대명사 후속 표현이 있으면 이전 후보를 제외하도록 보강했다.
  - `test_context_routing_matrix`에 `아까 어디였지`, `아까 몇시에 봤지`, `방금 본 영화 추천해줘`, `그거랑 상관없이 점심 추천해줘` 회귀 케이스를 추가했다.
  - 직접 재현으로 위 문장들은 `context_link=none`으로 분리되고, `방금 조회한 할 일 완료해줘`는 기존처럼 최근 할 일 후보에 연결되는 것을 확인했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`178 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`562 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "context or routing or pending" -q`(`109 passed, 70 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1197 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 관련 표현과 새 작업 생성 표현의 맥락 경계 고정

- 작업 이름: `관련해서`는 이어가고, `관련해서 새 알림`은 새 요청으로 분리하는 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - 최근 보강으로 `상관없이`, `별개로`, `무시하고` 같은 차단 표현은 최근 작업과 분리되지만, 사용자가 `관련해서`, `이어서`처럼 이전 작업을 실제로 이어가려는 표현까지 끊기면 반대 방향의 맥락 손실이 생길 수 있다.
  - 직접 재현으로 `그거랑 관련해서 보여줘`, `그거 이어서 보여줘`, `그거랑 관련해서 완료했어`는 최근 할 일 후보에 연결되고, `그거랑 관련해서 새 알림 등록해줘`는 새 알림 요청으로 분리되는 것을 확인했다.
  - 이 경계를 `test_context_routing_matrix`에 `related_pronoun_show_continues_current_task`, `related_pronoun_complete_continues_current_task`, `related_pronoun_new_reminder_creation_stays_new_request`로 추가했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`182 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_bot_helpers.py -q`(`745 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1201 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - `별개로/별도로/따로` 맥락 차단 표현 보강

- 작업 이름: 이전 후보와 별개인 새 웹검색/날씨/유틸리티 요청 분리
- 진행상황: 완료
- 진행내용:
  - 추가 샘플링에서 `그거랑 별개로 OpenAI 검색해줘`가 새 웹검색 요청임에도 최근 작업 후보 확인으로 빠지는 오판을 확인했다.
  - `candidate_is_excluded_by_replacement_text()`와 `has_context_rejection_signal()`에 `별개로`, `별도로`, `따로`를 추가했다.
  - 해당 표현 앞에 `그거`, `이거` 같은 대명사 후속 표현이 있고 뒤에는 새 요청이 붙으면, 이전 후보를 제외하고 현재 요청 intent를 유지하도록 했다.
  - `test_context_routing_matrix`에 `그거랑 별개로 OpenAI 검색해줘` 케이스를 추가해 여러 후보가 있어도 `web_search/context_link=none`으로 남는지 고정했다.
  - 직접 재현으로 `그거랑 별개로 OpenAI 검색해줘`, `그거랑 별도로 서울 날씨 알려줘`, `그거 따로 두고 지금 몇시야`는 새 요청으로 분리되고, `마지막 거 완료해줘`는 기존처럼 최근 할 일 후보에 연결되는 것을 확인했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`179 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`563 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "context or routing or pending" -q`(`109 passed, 70 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1198 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 새 항목 생성 표현의 현재 메시지 진단 보강

- 작업 이름: `새 알림`, `새 메모`, `새 할 일`을 명시 새 대상으로 표시
- 진행상황: 완료
- 진행내용:
  - `그거랑 관련해서 새 알림 등록해줘`처럼 이전 작업을 언급하면서도 새 항목을 만들려는 문장은, 라우터 모델이 “이전 작업 후속”과 “새 대상 생성” 신호를 모두 볼 수 있어야 한다.
  - 기존에는 `새 알림`이 `new_request_marker=True`로는 잡혔지만 `explicit_new_target=False`로 남아, 모델 프롬프트의 현재 메시지 진단에서 새 대상성이 덜 분명했다.
  - `has_explicit_new_item_creation_reference()`를 추가해 `새메모`, `새기억`, `새할일`, `새작업`, `새알림`, `새리마인드` 및 영어 `newtask/newreminder` 계열을 명시 새 대상으로 판정하도록 했다.
  - `test_build_current_message_context_keeps_related_follow_up_as_existing_target`, `test_build_current_message_context_marks_related_new_item_creation_as_new_target`, `test_build_current_message_context_marks_plain_new_item_creation_as_new_request`를 추가해 `관련해서 보여줘`는 기존 대상 후속으로, `관련해서 새 알림 등록해줘`와 `새 할 일 추가해줘`는 새 대상 신호로 진단되는지 고정했다.
  - 현재 메시지 진단이 포함된 route validation 로그는 `decision_hint`와 `validation_context`를 함께 보존해야 하므로, 일반 로그의 900자 제한은 유지하되 현재 메시지 진단이 있는 경우에만 압축 예산을 1100자로 사용하도록 조정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_current_message_context_keeps_related_follow_up_as_existing_target tests/test_context_builder.py::test_build_current_message_context_marks_related_new_item_creation_as_new_target tests/test_context_builder.py::test_build_current_message_context_marks_plain_new_item_creation_as_new_request tests/test_context_routing_matrix.py -q`(`185 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py -q`(`571 passed`)를 통과했다.
  - 전체 검증 중 route validation 로그 900자 제한 테스트가 한 차례 실패해, 현재 메시지 진단이 없는 일반 로그는 기존처럼 900자 제한을 유지하도록 재조정했다.
  - 재검증으로 `python3 -m pytest tests/test_cli.py::test_log_route_validation_if_changed_compacts_long_adjustment tests/test_cli.py::test_log_route_validation_if_changed_preserves_parseable_context_with_many_slots tests/test_bot_helpers.py::test_route_validation_summary_records_separate_new_request_diagnostics -q`(`4 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1208 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 새 항목 제목이 기존 후보와 같을 때 자동 연결 차단

- 작업 이름: `새 할 일 병원 예약 추가해줘`가 기존 `병원 예약` 할 일에 붙지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 추가 재현에서 최근 할 일 후보 제목이 `병원 예약`일 때 `새 할 일 병원 예약 추가해줘`가 새 할 일 생성이 아니라 기존 할 일 3의 후속 수정처럼 `continue`될 수 있음을 확인했다.
  - `action_match_is_new_item_creation()`은 action match 경로만 막고 있었고, 제목/target hint가 직접 일치하는 explicit match 경로에서는 새 항목 생성 의도가 후보 override를 막지 못했다.
  - `candidate_match_may_override_base_route()`에 `has_explicit_new_item_creation_reference()` 검사를 추가해, 대명사로 이전 대상을 재료로 쓰는 경우가 아니면 `새 할 일/새 알림/새 메모` 요청이 기존 후보 제목과 같아도 자동 연결하지 않도록 했다.
  - `action_match_is_new_item_creation()`도 대명사 출처 변환은 유지하되, 명시 새 항목 생성 marker가 있으면 후보 제목 일치보다 새 생성 의도를 우선하도록 순서를 정리했다.
  - `test_context_routing_matrix`에 `explicit_new_task_with_same_title_does_not_continue_existing_task`를 추가했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`183 passed`), `python3 -m pytest tests/test_router_agent.py::test_router_does_not_refine_model_intent_without_context_link_for_new_item_creation tests/test_router_agent.py::test_router_refines_model_intent_without_context_link_for_follow_up_candidate tests/test_route_validation.py::test_validate_route_context_link_keeps_reminder_to_task_source_conversion tests/test_context_routing_matrix.py -q`(`186 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_bot_helpers.py -q`(`753 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1210 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 제목 기반 기존 항목 수정 진단 보강

- 작업 이름: `병원 예약 할 일에 ... 추가해줘`를 새 요청이 아니라 후보 대조 수정으로 표시
- 진행상황: 완료
- 진행내용:
  - fallback 라우터는 `병원 예약 할 일에 내일 오전까지라고 추가해줘`를 최근 `병원 예약` 할 일에 잘 연결하지만, 모델 라우터에 들어가는 현재 메시지 진단은 `할 일`과 `추가` 때문에 `likely_new_request_do_not_link_previous_state`로 표시될 수 있었다.
  - `is_possible_named_target_mutation()`을 추가해 명시 새 항목 생성이 아니면서 수정/완료/삭제/복구/미루기/이름변경 계열 action이 있고, 제목/타입 단서가 있는 문장은 `possible_named_target_mutation_check_candidate_match`로 표시하도록 했다.
  - `새 할 일 병원 예약 추가해줘`는 `explicit_new_target=True`, `named_target_mutation=False`로 유지해 새 생성과 기존 항목 수정 경계를 분리했다.
  - `test_build_current_message_context_marks_named_target_mutation_for_candidate_match`, `test_build_current_message_context_keeps_new_task_with_same_title_as_new_request`를 추가하고 기존 새 항목/조회 진단 테스트도 새 필드를 확인하도록 보강했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_current_message_context_marks_named_target_mutation_for_candidate_match tests/test_context_builder.py::test_build_current_message_context_keeps_new_task_with_same_title_as_new_request tests/test_context_builder.py::test_build_current_message_context_marks_plain_new_item_creation_as_new_request tests/test_context_builder.py::test_build_current_message_context_marks_possible_named_target_lookup tests/test_context_routing_matrix.py -q`(`187 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`574 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1212 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 라우터 프롬프트의 제목 기반 조회/수정 진단 해석 보강

- 작업 이름: `possible_named_target_lookup/mutation` decision hint를 모델 지침에 명시
- 진행상황: 완료
- 진행내용:
  - 코드와 fallback은 `possible_named_target_lookup_check_candidate_match`, `possible_named_target_mutation_check_candidate_match`를 구분하지만, 라우터 모델 instructions에는 이 두 decision hint의 해석 규칙이 직접 적혀 있지 않았다.
  - 라우터 프롬프트에 lookup hint는 저장 항목 제목/ID와 조회 의도를 후보와 대조하고, mutation hint는 새 항목 생성이 아닌 기존 항목 수정/삭제/완료/미루기/복구 요청으로 후보의 target_hints, slots, artifacts, actions를 대조하라고 명시했다.
  - `likely_new_request_do_not_link_previous_state`와 명시 새 항목 생성 신호가 있으면 후보 제목과 겹쳐도 기존 후보에 연결하지 말라는 반대 규칙도 함께 추가했다.
  - 예시로 `병원 예약 할 일에 내일 오전까지라고 추가해줘`는 기존 task update 후보에 연결 가능하고, `새 할 일 병원 예약 추가해줘`는 같은 제목 후보가 있어도 `context_link=none`이라는 지침을 추가했다.
  - `test_router_agent_prefers_model_route_over_heuristic`가 새 decision hint 이름과 두 예시를 프롬프트에서 확인하도록 보강했다.
  - 관련 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_agent_prefers_model_route_over_heuristic tests/test_context_builder.py::test_build_current_message_context_marks_named_target_mutation_for_candidate_match tests/test_context_routing_matrix.py -q`(`185 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`574 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1214 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 맥락 차단 표현의 라우터 입력 진단 보강

- 작업 이름: `별개로/상관없이/따로` 뒤 새 요청을 `effective_text`로 전달
- 진행상황: 완료
- 진행내용:
  - fallback 라우터는 `그거랑 별개로 OpenAI 검색해줘`를 새 요청으로 처리하지만, `build_current_message_context()`는 여전히 `mixed_follow_up_and_new_target_check_target_match_before_link`로 진단해 라우터 모델 입력이 덜 선명했다.
  - `replacement_effective_user_text()`가 `상관없이`, `관련없이`, `무시하고`, `별개로`, `별도로`, `따로` 뒤의 요청 본문을 추출하도록 확장했다.
  - `따로 두고 지금 몇시야`처럼 자연스러운 연결 표현에서 `두고`, `놓고` 접두어를 제거해 `effective_text=지금몇시야`로 전달하도록 했다.
  - `test_build_current_message_context_marks_separate_new_request_as_replacement_target`, `test_build_current_message_context_strips_separate_transition_prefix`를 추가해 라우터 프롬프트 진단이 `replacement_target=True`, `decision_hint=likely_new_request_do_not_link_previous_state`를 내는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_builder.py -k "current_message_context or new_target_diagnostics" -q`(`9 passed, 64 deselected`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`182 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`568 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "context or routing or pending" -q`(`109 passed, 70 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1203 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - route validation 로그의 현재 메시지 진단 보존

- 작업 이름: 내부 검증 로그에서 `replacement_target`과 `decision_hint` 보존
- 진행상황: 완료
- 진행내용:
  - `route_validation_summary()`는 현재 메시지 진단을 내부 행동 로그에 남기지만, 긴 진단 문자열을 단순 압축하면 `replacement_target=True` 같은 핵심 신호가 중간에서 잘릴 수 있었다.
  - `compact_current_message_context_for_validation()`을 추가해 `text`, `effective_text`, 주요 signal, `decision_hint`만 선별해서 route validation 로그에 남기도록 했다.
  - 이로써 다음 턴 라우터가 내부 로그를 참고할 때 “왜 후보 연결이 제거되었는지”를 `effective_text`, `replacement_target`, `decision_hint`로 다시 확인할 수 있다.
  - `test_route_validation_summary_records_separate_new_request_diagnostics`를 추가해 `그거랑 별개로 OpenAI 검색해줘`, `그거 따로 두고 지금 몇시야` 로그가 `effective_text`, `replacement_target=True`, `decision_hint=likely_new_request_do_not_link_previous_state`를 보존하고 `validation_context`도 계속 파싱 가능한지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_route_validation_summary_records_separate_new_request_diagnostics tests/test_bot_helpers.py::test_route_validation_summary_preserves_pending_cross_location_retry_context tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment -q`(`4 passed`), `python3 -m pytest tests/test_bot_helpers.py::test_route_validation_summary_records_separate_new_request_diagnostics -q -vv`(`2 passed`), `python3 -m pytest tests/test_bot_helpers.py::test_route_validation_summary_records_separate_new_request_diagnostics tests/test_bot_helpers.py::test_route_validation_summary_preserves_pending_cross_location_retry_context tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment tests/test_context_builder.py -k "validation_context or current_message_context or router_context" -q`(`56 passed, 24 deselected`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`571 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "context or routing or pending or route_validation" -q`(`112 passed, 69 deselected`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1208 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 라우터 전용 진단의 에이전트/응답 노출 방지 계약

- 작업 이름: `current_message_context` 내부 로그가 전문 에이전트와 응답 작성에 새지 않도록 회귀 테스트 고정
- 진행상황: 완료
- 진행내용:
  - route validation 로그에 `current_message_context`, `effective_text`, `replacement_target`, `decision_hint`를 보존하도록 했으므로, 이 정보가 라우터 컨텍스트에는 남되 전문 에이전트와 응답 작성 모델에는 노출되지 않는 경계를 확인했다.
  - `test_execution_context_hides_route_validation_current_message_diagnostics_from_agent_and_response`를 추가해 라우터 컨텍스트에는 새 요청 진단이 남고, `for_agent()`와 `for_response()`에는 해당 내부 판단 토큰과 `validation_context`, `agent=route_validation`, `model=gpt-5.4-mini`가 제거되는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_response_composer.py::test_execution_context_hides_route_validation_current_message_diagnostics_from_agent_and_response tests/test_response_composer.py::test_execution_context_agent_context_hides_raw_route_diagnostics_but_keeps_target_hints tests/test_response_composer.py::test_execution_context_agent_context_hides_current_message_diagnostics_but_router_keeps_them -q`(`3 passed`), `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py -q`(`112 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py -k "internal_action or route_validation or current_message_context or response" -q`(`44 passed, 213 deselected`), `python3 -m pytest tests/test_route_validation.py tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`495 passed`)를 통과했다.
  - 전체 검증 중 `explicit_new_task_with_same_title_does_not_continue_existing_task`가 한 차례 실패했으나, 현재 작업트리 기준 단일 재검증에서 통과했고, 이어 전체 테스트도 정상 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1210 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 에이전트 카탈로그 등록 단계 맥락 계약 강화

- 작업 이름: 새 에이전트의 잘못된 후속 맥락 선언을 등록 시점에 차단
- 진행상황: 완료
- 진행내용:
  - 기존에는 `agent_catalog.json`의 `state_outputs` 형식 검증과 route validation action 어휘 검증이 주로 테스트에 머물러 있어, 개발자가 테스트를 놓치면 잘못된 카탈로그 항목이 런타임까지 들어올 수 있었다.
  - `build_agent_definition()`에 등록 단계 검증을 추가해 중복 예시, 중복 도구, 중복 `state_outputs`, private route/debug 슬롯, 보존 불가능한 `slots.*`, 지원하지 않는 `artifacts.*`, route validation이 처리할 수 없는 `available_actions.*`를 즉시 거부하도록 했다.
  - 이 변경은 새 에이전트가 라우터 프롬프트에는 노출되지만 실제 turn state, 내부 행동 로그, 후속 라우팅 단서에는 남지 않는 불완전한 맥락 계약을 만들지 않기 위한 안전장치다.
  - `test_build_agent_definition_rejects_duplicate_catalog_contract_values`, `test_build_agent_definition_rejects_private_or_unpreserved_state_outputs`를 추가해 잘못된 카탈로그 항목이 등록 단계에서 실패하는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py -q`(`77 passed`)를 통과했다.

## 2026-06-07 - 내부 도구 결과 후보의 후속 맥락 승격

- 작업 이름: tool result summary의 종류+ID를 라우터 target hint와 안전 슬롯으로 복원
- 진행상황: 완료
- 진행내용:
  - 내부 도구 호출 결과 요약에는 `{'kind': 'memory', 'id': 7, 'title': '원주 날씨 기록'}`처럼 후보 종류와 ID가 남을 수 있지만, 기존 내부 target hint 생성은 `memory_id` 같은 타입별 키만 ID 힌트로 읽고 `kind/id` 조합은 제목만 남겼다.
  - 이 상태에서는 다음 턴에 사용자가 “그 메모 보여줘”처럼 이어갈 때 라우터가 제목은 보지만 정확한 `메모 7` ID 힌트를 보지 못해 후보 선택 정확도가 떨어질 수 있었다.
  - `add_internal_action_kind_id_hint()`를 추가해 내부 로그의 `tool_context`와 `tool_call_trace` result summary 항목을 `메모 7`, `문서 9`, `할 일 3`, `알림 4` 같은 타입별 target hint로 승격했다.
  - `parse_internal_action_tool_result_slots()`를 추가해 linked state가 있는 내부 행동 기록에서는 tool result summary의 `memory_id/document_id/task_id/reminder_id/url` 계열 값을 안전 슬롯 후보로 복원하도록 했다.
  - `test_router_parses_tool_result_summary_items_as_safe_slots`, `test_router_merges_tool_result_summary_slots_for_linked_internal_action`을 추가하고, 기존 context builder 테스트 기대값을 `메모 7` 힌트까지 확인하도록 보강했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py -q`(`214 passed`)와 `python3 -m pytest tests/test_response_composer.py -q`(`37 passed`)를 통과했다.

## 2026-06-07 - 내부 target hint 병합 경계 고정

- 작업 이름: ID/URL 없는 내부 힌트가 현재 후보를 오염시키지 않도록 안전 계약 확인
- 진행상황: 완료
- 진행내용:
  - 내부 로그의 `target_hints`만 후보에 병합하면, 실제 실행 가능한 ID/URL/슬롯 없이 제목만 비슷한 과거 내부 기록이 현재 새 요청을 이전 작업으로 끌고 갈 위험이 있음을 확인했다.
  - 기존 `test_router_fallback_does_not_merge_internal_hints_without_executable_slots` 안전 계약을 유지하고, hint-only 병합은 열지 않는 방향으로 결정했다.
  - 대신 `test_router_fallback_enriches_state_candidate_from_tool_result_summary_slots`를 추가해 `tool_context` result summary에 `kind`, `id`, `title`이 있는 경우에는 `memory_id` 같은 안전 슬롯과 `메모 7` target hint가 실제 `parse_state_candidates()` 결과까지 합쳐지는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_fallback_enriches_state_candidate_from_tool_result_summary_slots tests/test_router_agent.py::test_router_fallback_does_not_merge_internal_hints_without_executable_slots tests/test_router_agent.py -q`(`139 passed`)를 통과했다.

## 2026-06-07 - 내부 행동 로그 저장소 사용자 격리 계약 고정

- 작업 이름: `AgentLogStore` 조회 단계에서 다른 사용자 내부 로그가 섞이지 않도록 저장소 테스트 보강
- 진행상황: 완료
- 진행내용:
  - 공유 채널에서는 여러 사용자가 같은 `conversation_id`를 사용할 수 있으므로, 내부 행동 기록 조회가 `user_id`를 제대로 필터링하지 않으면 라우터가 다른 사용자의 실행 결과를 현재 사용자의 맥락으로 오해할 수 있다.
  - 기존 컨텍스트 빌더 테스트는 최종 라우터 컨텍스트에서 다른 사용자 로그가 제외되는지 확인하고 있었지만, 저장소 API 자체의 필터 계약도 직접 고정하는 편이 새 호출부 추가 시 안전하다고 판단했다.
  - `test_agent_log_store_filters_same_channel_logs_by_user_id`를 추가해 같은 공유 `conversation_id` 안의 다른 사용자 로그가 `recent()` 결과에서 제외되는지 확인했다.
  - `test_agent_log_store_allows_legacy_null_user_logs_only_for_user_scoped_conversation_ids`를 추가해 `user_id`가 없는 과거 로그는 `dm:user-1`처럼 사용자 전용 conversation_id에서만 허용되고, `user-1`이 `user-10`에 부분 매칭되거나 공유 채널 legacy 로그가 섞이지 않는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_memory_store.py -q`(`120 passed`)와 `python3 -m pytest tests/test_context_builder.py -k "internal_action or user_log or same_user or other_user or legacy" -q`(`16 passed, 63 deselected`)를 통과했다.

## 2026-06-07 - 실행 전 검증의 새 항목 생성 링크 차단

- 작업 이름: route validation에서 `새 할 일/새 메모/새 알림` 요청이 기존 상태에 붙지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 라우터 프롬프트와 fallback은 명시적 새 항목 생성 표현을 기존 후보와 분리하도록 보강했지만, 실행 전 검증 계층이 같은 경계를 보장하는지 테스트가 부족했다.
  - `unrelated_new_request_mismatch_linked_state()`에 명시적 새 항목 생성 marker 검사를 추가해, `새 할 일 추가해줘`, `새 할 일 병원 예약 추가해줘`처럼 새 항목을 만들려는 문장이 기존 linked state와 슬롯에 연결되어 있으면 실행 직전에 링크를 제거하도록 했다.
  - `그 작업을 새 메모로 저장해줘`처럼 명시적 원본을 재료로 새 항목을 만드는 source conversion 요청은 기존처럼 linked state를 유지한다.
  - `test_validate_route_context_link_clears_explicit_new_task_even_when_title_matches`, `test_validate_route_context_link_clears_explicit_new_task_without_named_title`, `test_validate_route_context_link_keeps_existing_named_task_mutation`, `test_validate_route_context_link_keeps_new_memory_from_explicit_linked_source`를 추가했다.
  - 관련 검증으로 `python3 -m pytest tests/test_route_validation.py -q`(`183 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_context_builder.py -q`(`580 passed`)를 통과했다.

## 2026-06-07 - 자연스러운 새 항목 생성 표현 확장

- 작업 이름: `새로운/새로/신규` 항목 생성 표현을 기존 맥락과 분리
- 진행상황: 완료
- 진행내용:
  - 기존 새 항목 생성 판정은 `새 할 일`, `새 메모`, `새 알림` 중심이라 사용자가 `새로운 할 일`, `새로 할 일`, `신규 메모`처럼 자연스럽게 말하면 기존 후보 제목과 우연히 붙을 수 있었다.
  - `has_explicit_new_item_creation_reference()`에 `새로운*`, `새로*`, `신규*` 계열 메모/기억/할 일/작업/알림/리마인드 표현을 추가했다.
  - 검증 중 `replacement_effective_user_text()`가 `새로운` 안의 `새로`를 전환 접두어로 잘라 `운할일...`처럼 만드는 문제가 확인되어, `새로운`은 전환 접두어 제거 대상에서 제외했다.
  - `unrelated_new_request_mismatch_linked_state()`는 변환된 effective text뿐 아니라 원문 compact 기준으로도 새 항목 생성 marker를 먼저 확인하도록 보강했다.
  - `test_build_current_message_context_marks_natural_new_item_creation_phrases`, `natural_new_task_phrase_with_same_title_does_not_continue_existing_task`, `test_validate_route_context_link_clears_natural_new_item_creation_phrases`를 추가했다.
  - 관련 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_current_message_context_marks_natural_new_item_creation_phrases tests/test_context_routing_matrix.py tests/test_route_validation.py::test_replacement_effective_user_text_handles_natural_replacement_markers tests/test_route_validation.py::test_validate_route_context_link_clears_natural_new_item_creation_phrases -q`(`187 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py -q`(`584 passed`)를 통과했다.

## 2026-06-07 - Discord 실행 컨텍스트 전달 계약 보강

- 작업 이름: `handle_message()`와 내부 행동 기록 래퍼의 실행 컨텍스트 누락 방지 테스트 추가
- 진행상황: 완료
- 진행내용:
  - 기존 소스 레벨 테스트가 에이전트 dispatch, 응답 작성, 내부 행동 기록 호출부의 `ExecutionContext` 전달을 검사하고 있음을 확인했다.
  - 새 호출부가 늘어날 때 Discord 봇 본체의 `record_internal_action_result()` 래퍼에서 실행 컨텍스트가 떨어지면 내부 로그의 `route_context`, `linked_state_id`, `resolved_slots`가 사라질 수 있으므로, 래퍼가 받은 `execution_context`를 모듈 공통 기록 함수에 그대로 전달하는지 테스트를 추가했다.
  - `handle_message()`가 라우팅/검증 이후 생성한 `ExecutionContext`를 `response_execution_context_sink`에 게시하는지 테스트를 추가했다. 이 sink는 최종 응답 작성, turn state 저장, 내부 행동 기록이 라우팅 전 기본 컨텍스트가 아니라 실제 실행 컨텍스트를 보게 하는 연결점이다.
  - 관련 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_runtime_internal_action_result_records_include_execution_context tests/test_agent_registry.py::test_discord_internal_action_result_wrapper_forwards_execution_context tests/test_agent_registry.py::test_discord_handle_message_publishes_route_execution_context_to_response_sink tests/test_agent_registry.py::test_runtime_agent_execution_functions_attach_execution_metadata -q`(`4 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_agent_registry.py -q`(`79 passed`), `python3 -m pytest tests/test_bot_helpers.py -k "execution_context or internal_action or response_execution_context" -q`(`20 passed, 162 deselected`), `python3 -m pytest -q`(`1231 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-07 - 짧은 비작업 반응의 pending 맥락 보존

- 작업 이름: `아`, `음`, `잠깐` 같은 반응이 후속 작업 확인 대기를 지우지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `expire_stale_pending_context_link()`는 `context_link=none`인 새 요청이 들어오면 기존 후속 작업 확인 대기를 만료하는데, 사용자의 짧은 감탄/머뭇거림 메시지도 같은 경로를 탈 수 있었다.
  - 이 경우 사용자가 확인 질문을 받은 뒤 `아`, `음...`, `잠깐`처럼 말했을 뿐인데 pending 확인 상태가 사라져, 다음에 `응 진행해줘` 또는 `다시해봐`라고 했을 때 맥락을 잃을 수 있다.
  - `is_non_action_interjection_text()`를 추가해 명확한 비작업 반응만 구분하고, 승인/거부/새 요청/행동 요청은 보존 대상에서 제외했다.
  - Discord 봇과 로컬 CLI의 stale pending context 만료 함수가 이 헬퍼를 참고하도록 연결했다.
  - `test_non_action_interjection_text_only_matches_clear_fillers`, `test_assistant_bot_keeps_pending_context_for_non_action_interjection`, `test_assistant_bot_handle_message_keeps_pending_context_for_non_action_interjection`, `test_cli_keeps_pending_context_links_for_non_action_interjection`를 추가했다.
  - 직접 만료 helper뿐 아니라 `handle_message()` 전체 경로에서도 `chat/context_link=none`인 `아` 메시지가 기존 pending 확인 상태를 지우지 않는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_route_validation.py::test_non_action_interjection_text_only_matches_clear_fillers tests/test_bot_helpers.py::test_assistant_bot_keeps_pending_context_for_non_action_interjection tests/test_bot_helpers.py::test_assistant_bot_handle_message_keeps_pending_context_for_non_action_interjection tests/test_bot_helpers.py::test_assistant_bot_new_time_request_expires_pending_context_without_approval -q`(`4 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_route_validation.py tests/test_bot_helpers.py -k "pending_context or interjection or context_link or route_validation" tests/test_cli.py -k "pending_context or route_validation" -q`(`218 passed, 235 deselected`)를 통과했다.

## 2026-06-07 - filler가 붙은 pending 승인/거부 인식 보강

- 작업 이름: `아 맞아 진행해줘`, `음 그건 하지마` 같은 혼합 문장 처리
- 진행상황: 완료
- 진행내용:
  - 직전 보강으로 `아`, `음`, `잠깐` 단독 반응은 pending 확인을 보존하지만, 사용자가 `아 맞아 진행해줘`처럼 filler 뒤에 명확한 승인을 붙이면 승인으로 처리되어야 한다.
  - `strip_context_link_confirmation_filler_prefix()`를 추가해 확인 문맥에서만 `아/음/흠/잠깐/잠시/잠만` 접두어를 제거하고, 제거 후 남은 문장이 승인 또는 거부 prefix로 시작할 때만 정규화하도록 했다.
  - 이 정규화는 `is_context_link_approval_text()`, `is_context_link_rejection_text()`, `has_context_link_approval_prefix()`, `strip_context_link_approval_prefix()`에 연결했다.
  - `아침`, `아까`처럼 실제 단어는 filler로 잘리지 않도록, 제거 후 승인/거부 prefix가 없는 경우 원문 compact를 유지한다.
  - `test_pending_context_approval_accepts_filler_prefixed_confirmation`, `test_context_link_approval_accepts_plain_confirmation_but_not_new_request`, `test_context_link_rejection_rejects_plain_cancel_but_not_new_request`, `test_non_action_interjection_text_only_matches_clear_fillers`, `test_assistant_bot_filler_prefixed_chat_approval_restores_pending_context`, `test_assistant_bot_cancels_pending_context_link_and_expires_state`를 보강했다.
  - route validation helper뿐 아니라 Discord `handle_message()` 전체 경로에서도 `아 맞아 진행해줘`가 pending 확인 승인으로 처리되고, 원래 문장, linked state, resolved slots가 복원되는지 고정했다.
  - Discord `handle_message()` 전체 경로에서 `음 그건 하지마`가 pending 확인 취소로 처리되고, 취소 대상의 pending intent/context_link/resolved slots/original text가 구조화 결과에 남는지도 고정했다.
  - 라우팅 매트릭스에 `filler_prefixed_rejection_cancels_pending_context`를 추가해 fallback/route validation 조합에서도 같은 거부 계약을 확인하도록 했다.
  - 관련 검증으로 `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_accepts_filler_prefixed_confirmation tests/test_bot_helpers.py::test_assistant_bot_filler_prefixed_chat_approval_restores_pending_context tests/test_bot_helpers.py::test_assistant_bot_chat_approval_allows_cross_location_pending_context -q`(`3 passed`)를 통과했다.
  - 거부 통합 검증으로 `python3 -m pytest tests/test_route_validation.py::test_context_link_rejection_rejects_plain_cancel_but_not_new_request tests/test_bot_helpers.py::test_assistant_bot_cancels_pending_context_link_and_expires_state -q`(`3 passed`)를 통과했다.
  - 기존 helper 검증으로 `python3 -m pytest tests/test_route_validation.py::test_context_link_rejection_rejects_plain_cancel_but_not_new_request tests/test_route_validation.py::test_non_action_interjection_text_only_matches_clear_fillers tests/test_route_validation.py::test_context_link_approval_accepts_plain_confirmation_but_not_new_request tests/test_route_validation.py::test_pending_context_approval_accepts_filler_prefixed_confirmation -q`(`4 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -k "pending_context or filler or approval or rejection or context_link" -q`(`241 passed, 316 deselected`), `python3 -m pytest -q`(`1237 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`507 passed`)를 통과했다.

## 2026-06-08 - filler 포함 거부+새 요청 분리

- 작업 이름: `음 아니 취소 말고 서울 날씨 알려줘`가 pending 취소로 소비되지 않도록 통합 경계 고정
- 진행상황: 완료
- 진행내용:
  - 기존에는 `아니 취소 말고 서울 날씨 알려줘`가 pending 취소가 아니라 새 날씨 요청으로 처리되는 Discord 통합 테스트가 있었지만, 앞에 `음` 같은 filler가 붙은 변형은 직접 고정되어 있지 않았다.
  - `test_context_link_rejection_rejects_plain_cancel_but_not_new_request`에 `음 아니 취소 말고 목록 보여줘`를 추가해 route validation helper가 filler 뒤 거부+새 요청을 순수 거부로 보지 않는지 확인했다.
  - `test_assistant_bot_routes_negative_prefixed_new_request_instead_of_cancel_pending`를 파라미터화해 `음 아니 취소 말고 서울 날씨 알려줘`도 Discord `handle_message()` 전체 경로에서 weather 새 요청으로 실행되고, 기존 pending context가 만료되는지 고정했다.
  - 관련 검증으로 `python3 -m pytest tests/test_route_validation.py::test_context_link_rejection_rejects_plain_cancel_but_not_new_request tests/test_bot_helpers.py::test_assistant_bot_routes_negative_prefixed_new_request_instead_of_cancel_pending -q`(`3 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -k "new_request or cancel_pending or pending_context or rejection" -q`(`84 passed, 474 deselected`)를 통과했다.

## 2026-06-08 - 일반 확인 대기의 비작업 반응 보존

- 작업 이름: `아`, `잠깐` 같은 반응이 첨부 저장/삭제/웹검색 확인 대기를 지우지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 후속 작업 pending context는 비작업 반응을 보존하도록 보강되어 있었지만, 첨부 저장 확인, 전체 기억 삭제 확인, 웹 검색 확인 같은 일반 pending confirmation은 별도 만료 함수에서 여전히 `context_link=none` 라우팅을 새 요청으로 보고 만료할 수 있었다.
  - Discord 봇과 CLI의 `expire_stale_pending_confirmations()`에 `is_non_action_interjection_text()` 예외를 연결해, `아`, `음`, `잠깐`처럼 명확히 행동 요청이 아닌 메시지는 일반 확인 대기를 유지하도록 했다.
  - 실제 새 요청으로 라우팅된 문장은 기존처럼 일반 확인 대기를 만료하고, 승인/거부/웹검색 확인 intent도 기존 우선순위를 유지한다.
  - `test_assistant_bot_keeps_general_pending_confirmations_for_non_action_interjection`, `test_cli_keeps_general_pending_confirmations_for_non_action_interjection`를 추가해 첨부 저장, 기억 삭제, 웹 검색 확인 대기가 함께 보존되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_keeps_general_pending_confirmations_for_non_action_interjection tests/test_cli.py::test_cli_keeps_general_pending_confirmations_for_non_action_interjection -q`(`2 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_bot_helpers.py -k "pending_confirmation or pending_attachment or web_search_confirmation or memory_deletion or interjection" tests/test_cli.py -k "pending_confirmation or pending_attachment or web_search_confirmation or memory_deletion or interjection" -q`(`22 passed, 251 deselected`)와 `python3 -m pytest tests/test_route_validation.py::test_non_action_interjection_text_only_matches_clear_fillers -q`(`1 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1239 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 내부 컨텍스트 키의 공개 응답 노출 차단

- 작업 이름: `route_context`, `validation_context`, `current_message_context`를 응답 private key로 승격
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록과 라우터 진단에서는 `route_context`, `validation_context`, `current_message_context`가 유용하지만, 에이전트가 실수로 이 키를 `OperationResult.facts/slots/items`에 넣으면 공개 응답 작성 모델 입력에 남을 수 있는 빈틈을 확인했다.
  - `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`에 세 키를 추가해 공개 결과 필터, 실행 컨텍스트 필터, registry 내부 결과 예외가 같은 private key 계약을 공유하도록 했다.
  - `test_response_private_route_keys_are_filtered_from_nested_items`를 보강해 `facts`, `slots`, `items[].facts`, `items[].slots` 안의 세 키와 `decision_hint/effective_text` 값이 `public_operation_result_for_response()` 결과에서 제거되는지 확인했다.
  - 관련 검증으로 `python3 -m pytest tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_nested_items tests/test_agent_registry.py::test_internal_route_context_keys_are_private_for_response_composer tests/test_agent_registry.py::test_internal_log_only_context_keys_do_not_become_turn_state_or_fact_slots -q`(`4 passed`)를 통과했다.
  - 추가 검증으로 `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py -q`(`116 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1241 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - assistant 예시 참조와 승인 표현 분리

- 작업 이름: `네가 예를 들어준 내용 그대로 수정해줘`가 pending 승인으로 소비되지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `네가/너가/니가`처럼 사용자가 봇을 가리키는 표현이 `네` 승인 prefix와 겹쳐, `네가 예를 들어준 내용 그대로 수정해줘` 같은 문장이 `context_link` 승인으로 오인될 수 있는 경계를 확인했다.
  - `starts_with_assistant_self_reference()`를 추가하고 `is_context_link_approval_text()`, `has_context_link_approval_prefix()`, `context_link_approval_suffix()`, `strip_context_link_approval_prefix()`가 이 표현을 승인 prefix로 자르지 않도록 했다.
  - 현재 메시지 진단에 `assistant_self_reference`, `assistant_example_reference` 신호와 `possible_recent_assistant_example_reference_use_recent_conversation` 힌트를 추가해, 라우터가 최근 assistant 예시/설명을 행동 요청의 재료로 참고할 수 있게 했다.
  - `test_context_link_approval_accepts_plain_confirmation_but_not_new_request`, `test_pending_context_approval_does_not_consume_assistant_example_reference`, `test_build_current_message_context_marks_assistant_example_reference_without_confirmation`를 추가/보강했다.
  - 직접 검증으로 `python3 -m pytest tests/test_route_validation.py::test_context_link_approval_accepts_plain_confirmation_but_not_new_request tests/test_route_validation.py::test_pending_context_approval_does_not_consume_assistant_example_reference tests/test_context_builder.py::test_build_current_message_context_marks_assistant_example_reference_without_confirmation -q`(`3 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_context_builder.py -k "current_message_context or focused_context" tests/test_route_validation.py -k "approval or confirmation or assistant_example" -q`(`46 passed, 221 deselected`)와 `python3 -m pytest tests/test_route_validation.py tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`589 passed`)를 통과했다.

## 2026-06-08 - 내부 진단 키의 실행 슬롯 격리 계약 고정

- 작업 이름: `route_context`, `validation_context`, `current_message_context`가 전문 에이전트 실행 슬롯으로 섞이지 않도록 회귀 테스트 보강
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록과 라우터 진단에는 세 키가 필요하지만, 새 에이전트가 추가될 때 이 값들이 safe execution slot이나 catalog target slot으로 편입되면 전문 에이전트가 raw 진단 JSON을 실행 대상처럼 읽을 수 있는 위험을 확인했다.
  - `test_internal_route_diagnostic_keys_do_not_become_execution_targets`를 추가해 세 키가 응답 private key이면서 `SAFE_INTERNAL_ROUTE_SLOT_KEYS`, catalog target slot, turn state target hint, internal action target hint에는 포함되지 않는지 고정했다.
  - `test_execution_context_response_hides_private_route_metadata_from_resolved_slots`를 보강해 세 키와 nested `decision_hint/effective_text`가 agent context와 response context 양쪽의 `resolved_slots` 출력에서 제거되는지 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_internal_route_diagnostic_keys_do_not_become_execution_targets tests/test_response_composer.py::test_execution_context_response_hides_private_route_metadata_from_resolved_slots -q`(`2 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py -q`(`117 passed`)를 통과했다.

## 2026-06-08 - assistant 예시 참조의 fallback 후보 연결 차단

- 작업 이름: `네가 예시로 든 내용 그대로...` 요청이 최근 작업 후보 확인으로 빼앗기지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - route validation은 `네가/너가/니가`를 `네` 승인으로 보지 않도록 고쳤지만, router fallback은 `수정해줘` 같은 action 단어만 보고 최근 작업 후보 여러 개를 `어느 작업을 이어서 처리할까요?` 확인으로 끌어올릴 수 있었다.
  - 라우터 프롬프트에 `possible_recent_assistant_example_reference_use_recent_conversation`의 의미를 명시해, `네가/너가/니가`를 approval로 보지 말고 최근 assistant 예시/설명을 행동 요청의 재료로 쓰도록 했다.
  - `context_aware_fallback_route()`가 이 decision hint를 보고 명시 후보 일치가 없으면 최근 작업 후보 자동 연결과 다중 후보 clarify를 보류하도록 했다.
  - `test_current_message_decision_hint_parses_assistant_example_reference_diagnostic`, `test_router_prompt_explains_assistant_example_reference_not_confirmation`, `test_router_fallback_does_not_treat_assistant_example_reference_as_pending_approval`를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_current_message_decision_hint_parses_assistant_example_reference_diagnostic tests/test_router_agent.py::test_router_prompt_explains_assistant_example_reference_not_confirmation tests/test_router_agent.py::test_router_fallback_does_not_treat_assistant_example_reference_as_pending_approval -q`(`3 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_context_builder.py -k "assistant_example or current_message_context" tests/test_route_validation.py -k "assistant_example or approval" tests/test_router_agent.py -k "assistant_example or current_message_decision" -q`(`8 passed, 399 deselected`)와 `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`592 passed`)를 통과했다.
  - 이번 전체 검증 중 같은 회귀가 다시 드러나 `context_aware_fallback_route()`의 assistant 예시 참조 보류 판단을 pending 후보 선택보다 먼저 적용하도록 순서를 재확인했다.
  - 재검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_fallback_does_not_treat_assistant_example_reference_as_pending_approval -q`(`1 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_response_composer.py tests/test_agent_registry.py -q`(`257 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1246 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 내부 행동 로그 사용자 격리 감시 강화

- 작업 이름: `AgentLogStore` 별칭으로 만든 로그 저장소도 `user_id` 없는 기록 호출을 잡도록 소스 레벨 테스트 보강
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록은 다음 턴 라우터와 에이전트가 참고하는 강한 맥락 신호이므로, 공유 채널에서 다른 사용자의 로그가 섞이지 않으려면 모든 런타임 `AgentLogStore.add()` 호출에 `user_id`가 있어야 한다.
  - 기존 소스 레벨 테스트는 `logs.add()`와 `self.logs.add()` 패턴을 중심으로 잡았지만, 새 에이전트나 오케스트레이션 코드가 `agent_logs = AgentLogStore(...)`, `self.audit_logs = AgentLogStore(...)`처럼 다른 이름을 쓰면 감시망이 약해질 수 있음을 확인했다.
  - `agent_log_store_targets()` 헬퍼를 추가해 파일 안에서 `AgentLogStore(...)`로 생성된 지역 변수와 인스턴스 속성 이름을 추적하고, 그 대상의 `.add()` 호출도 `user_id` 계약 검사에 포함하도록 했다.
  - `test_agent_log_add_detector_follows_agent_log_store_aliases`를 추가해 `agent_logs.add()`, `self.audit_logs.add()`는 탐지하면서 무관한 `self.other.add()`는 탐지하지 않는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_agent_log_add_detector_follows_agent_log_store_aliases tests/test_agent_registry.py::test_runtime_agent_logs_always_include_user_id tests/test_agent_registry.py::test_scope_based_agent_logs_include_user_id -q`(`3 passed`)를 통과했다.

## 2026-06-08 - assistant 예시 참조 표현 범위 확장

- 작업 이름: `방금 네가 예시로 든 내용...`, `아까 너가 말한 예시...` 진단 보강
- 진행상황: 완료
- 진행내용:
  - 직전 보강은 문장이 `네가/너가/니가`로 바로 시작하는 경우를 중심으로 잡았지만, 실제 사용자는 `방금 네가 예시로 든 내용 그대로 수정해줘`, `아까 너가 말한 예시 그대로 해줘`처럼 시간 표현을 앞에 붙일 수 있다.
  - 현재 메시지 진단에서 assistant self reference를 문장 시작뿐 아니라 compact text 내부에서도 찾도록 `has_assistant_self_reference()`를 추가했다.
  - 이 확장으로 `방금/아까`가 앞에 붙어도 `assistant_self_reference=True`, `assistant_example_reference=True`, `decision_hint=possible_recent_assistant_example_reference_use_recent_conversation`으로 라우터에 전달된다.
  - `test_build_current_message_context_marks_assistant_example_reference_without_confirmation`를 보강해 `네가...`, `방금 네가...`, `아까 너가...` 세 변형을 함께 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_current_message_context_marks_assistant_example_reference_without_confirmation tests/test_router_agent.py::test_router_fallback_does_not_treat_assistant_example_reference_as_pending_approval -q`(`2 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_context_builder.py -k "assistant_example or current_message_context or focused_context" tests/test_router_agent.py -k "assistant_example or current_message_decision" tests/test_route_validation.py -k "assistant_example or approval" -q`(`48 passed, 359 deselected`)를 통과했다.

## 2026-06-08 - 최근 대화 원문 참조 표현 확장

- 작업 이름: `방금 한 말`, `아까 얘기했던 거`, `전에 말한거`를 최근 대화 원문 참조로 인식
- 진행상황: 완료
- 진행내용:
  - 기존에는 `방금 말한 거 메모해줘`는 최근 대화 원문을 새 메모/할 일/알림으로 만드는 요청으로 잘 분리했지만, `방금 한 말 메모해줘`, `아까 얘기했던 거 할 일로 추가해줘`, `전에 말한거 할 일로 추가해줘` 같은 자연어 변형은 source creation으로 잡히지 않았다.
  - `RECENT_CONVERSATION_SOURCE_MARKERS`를 공통 routing marker로 추가해 router fallback과 route validation이 같은 source marker 계약을 공유하도록 했다.
  - `방금 저장한`, `아까 등록한`처럼 실제 저장 항목을 가리키는 표현은 기존처럼 source creation에서 제외해, 저장 항목 조회/수정/삭제 흐름과 섞이지 않게 유지했다.
  - `test_router_and_route_validation_share_recent_conversation_source_variants`를 추가해 router와 route validation의 인식 결과가 같은지 고정했다.
  - `test_validate_route_context_link_clears_recent_conversation_source_creation_link`를 파라미터화하고, 라우팅 매트릭스에 `recent_spoken_word_memory_request_does_not_link_previous_memory`를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_route_validation.py::test_router_and_route_validation_share_recent_conversation_source_variants tests/test_route_validation.py::test_validate_route_context_link_clears_recent_conversation_source_creation_link tests/test_context_routing_matrix.py -k "recent_spoken_word_memory_request or recent_said_memory_request or previous_said_task_request" -q`(`3 passed, 187 deselected`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`518 passed`)를 통과했다.

## 2026-06-08 - 최근 대화/저장 항목 marker drift 방지

- 작업 이름: 최근 대화 원문 참조와 저장 항목 참조 marker를 공통 계약으로 관리
- 진행상황: 완료
- 진행내용:
  - `RECENT_CONVERSATION_SOURCE_MARKERS`는 공통화했지만, source creation에서 제외해야 하는 `방금 저장한/아까 등록한` 계열 저장 항목 참조 marker는 router와 route validation에 각각 중복 문자열로 남아 있었다.
  - `RECENT_STORED_ITEM_REFERENCE_MARKERS`를 `routing_markers.py`에 추가하고, router fallback과 route validation의 `asks_to_create_from_recent_conversation_source()`가 같은 제외 marker를 사용하도록 했다.
  - `test_router_and_route_validation_share_recent_conversation_source_variants`가 `RECENT_CONVERSATION_SOURCE_MARKERS`와 `RECENT_STORED_ITEM_REFERENCE_MARKERS`를 직접 순회하도록 보강해, marker 추가 시 한 계층만 바뀌는 drift를 잡도록 했다.
  - 직접 검증으로 `python3 -m pytest tests/test_route_validation.py::test_router_and_route_validation_share_recent_conversation_source_variants tests/test_route_validation.py::test_validate_route_context_link_clears_recent_conversation_source_creation_link tests/test_context_routing_matrix.py -k "recent_spoken_word_memory_request or recent_said_memory_request" -q`(`2 passed, 188 deselected`)를 통과했다.
  - 관련 ruff 검증으로 `python3 -m ruff check tests/test_route_validation.py assistant_bot/routing_markers.py assistant_bot/route_validation.py assistant_bot/agents/router.py`를 통과했다.

## 2026-06-08 - pending 후보 선택의 제외 표현 회귀 고정

- 작업 이름: `첫 번째 말고`, `그거 말고 첫 번째` 같은 후보 선택 답변을 안정적으로 해석
- 진행상황: 완료
- 진행내용:
  - 후보가 여러 개라 확인 질문이 나온 뒤 사용자는 `첫 번째`, `두 번째`처럼만 답하지 않고 `첫 번째 말고`, `그거 말고 첫 번째`처럼 제외 표현과 선택 표현을 함께 쓸 수 있다.
  - `select_pending_candidate()`는 이미 저장된 `pending_candidate_state_ids` 순서를 기준으로 ordinal 선택과 제외 선택을 처리하지만, 실제 대화형 표현을 직접 고정한 회귀 테스트가 부족했다.
  - `test_select_pending_candidate_handles_exclusion_and_ordinal_selection_text`를 추가해 `그거말고첫번째`는 명시 선택으로 첫 후보를 고르고, `첫번째말고`는 첫 후보를 제외해 남은 후보를 고르는지 확인했다.
  - `test_router_fallback_selects_pending_state_candidate_by_exclusion_text`를 추가해 라우터 fallback 전체 경로에서도 `첫 번째 말고`가 pending 원래 요청(`그거 삭제해줘`)과 두 번째 후보의 실행 슬롯(`task_id=22`)으로 복원되는지 고정했다.
  - `test_router_fallback_does_not_consume_pending_selection_for_new_weather_request`를 추가해 `첫 번째 말고 서울 날씨 알려줘`, `서울 날씨 첫 번째 말고 알려줘`처럼 후보 선택 말투와 새 날씨 요청이 섞인 문장은 pending 후보 선택으로 소비하지 않고 새 weather 요청으로 유지하는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_select_pending_candidate_uses_saved_candidate_id_order_for_ordinals tests/test_router_agent.py::test_select_pending_candidate_handles_exclusion_and_ordinal_selection_text -q`(`2 passed`)와 `python3 -m pytest tests/test_router_agent.py::test_router_fallback_selects_pending_state_candidate_by_exclusion_text tests/test_router_agent.py::test_router_fallback_does_not_consume_pending_selection_for_new_weather_request -q`(`3 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_router_agent.py -q`(`142 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1253 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 에이전트 최근 메시지 헬퍼의 marker 계약 반영

- 작업 이름: Memory/Task/Reminder 헬퍼도 공통 최근 대화 원문 marker를 사용하도록 보강
- 진행상황: 완료
- 진행내용:
  - 라우터 fallback과 route validation은 `RECENT_CONVERSATION_SOURCE_MARKERS`를 공유하지만, 실제 Memory/Task/Reminder 에이전트가 쓰는 `asks_to_remember_recent_message()`, `asks_to_create_task_from_recent_message()`, `asks_to_create_reminder_from_recent_message()`는 자체 marker 목록을 갖고 있었다.
  - `agents.common`에 `has_recent_conversation_source_reference()`와 `has_recent_stored_item_reference()`를 추가하고, 세 recent-message 헬퍼가 공통 marker를 보도록 연결했다.
  - `방금 생각난 거`는 이전 대화 원문이 아니라 새로 떠오른 생각이므로, 에이전트 recent-message 헬퍼에서는 `include_unspecified_thought=False`로 제외하고 기존 `asks_to_remember_unspecified_recent_thought()` 흐름과 분리했다.
  - `test_substantive_memory_text_ignores_file_only_instruction`, `test_task_request_helpers`에 `방금 한 말`, `아까 얘기했던 내용`, `전에 말한거` 변형과 `방금 생각난 거` 제외 경계를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_heuristics.py::test_substantive_memory_text_ignores_file_only_instruction tests/test_router_heuristics.py::test_task_request_helpers tests/test_route_validation.py::test_router_and_route_validation_share_recent_conversation_source_variants tests/test_route_validation.py::test_validate_route_context_link_clears_recent_message_reminder_creation_link -q`(`4 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_router_heuristics.py tests/test_memory_store.py -k "recent_message or recent_thought or 방금 or create_task_from_recent" -q`(`3 passed, 168 deselected`)와 `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -k "recent_conversation_source or recent_message_reminder or recent_spoken_word or recent_said or recent_thought" -q`(`14 passed, 550 deselected`)를 통과했다.

## 2026-06-08 - 응답 작성 fallback 컨텍스트의 내부 로그 필터링

- 작업 이름: `execution_context` 없이 `conversation_context`만 전달된 응답 작성 경로도 비공개 라우팅 로그를 정리
- 진행상황: 완료
- 진행내용:
  - 정상 경로의 `ExecutionContext.for_response()`는 내부 행동 기록과 라우터 진단을 응답용으로 정리하지만, 새 호출부가 `execution_context` 없이 raw `conversation_context`만 넘기면 `최근 내부 행동 기록`, `route_context`, `validation_context`, `agent=*:result` 같은 내부 표기가 응답 모델 입력에 남을 수 있는 빈틈을 확인했다.
  - `response_safe_conversation_context()`를 추가해 raw context fallback도 섹션 단위로 정리하도록 했다.
  - `맥락 판별 정책`은 현재 메시지 진단을 제거하고, `최근 내부 행동 기록`은 `비공개 내부 참고`로 바꾸어 `response_safe_internal_action_context()`를 통과시키며, `라우팅 근거`는 공개 가능한 이유만 남긴다.
  - `test_response_composer_sanitizes_raw_conversation_context_without_execution_context`를 추가해 `execution_context`가 없어도 `현재 메시지 맥락 진단`, `decision_hint`, `route_context`, `validation_context`, `linked_state_id`, `resolved_slots`, `agent=route_validation`, `agent=task:result`, model명이 응답 모델 입력에서 제거되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_response_composer.py::test_response_composer_sanitizes_raw_conversation_context_without_execution_context -q`(`1 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_response_composer.py -q`(`38 passed`)를 통과했다.

## 2026-06-08 - 응답 작성 호출부의 실행 컨텍스트 계약 강화

- 작업 이름: `ResponseComposer.compose()` 호출이 실제 `execution_context`를 넘기는지 소스 레벨 검증 보강
- 진행상황: 완료
- 진행내용:
  - 최종 응답 작성자는 구조화 실행 결과뿐 아니라 실제 실행 기준 `ExecutionContext`의 `resolved_slots`, linked state, 안전한 내부 행동 기록을 함께 봐야 한다.
  - 기존 테스트는 `conversation_context`와 `execution_context` 키워드 존재만 확인했지만, 새 호출부가 실수로 `execution_context=None`이나 raw `conversation_context` 변수를 넘겨도 감지하지 못할 수 있었다.
  - `test_response_composer_calls_include_context_contract`를 보강해 `execution_context` 키워드 값이 `None`이 아니고, `conversation_context`/`response_conversation_context` 같은 raw context 변수가 아닌지 확인하도록 했다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_response_composer_calls_include_context_contract -q`(`1 passed`)를 통과했다.

## 2026-06-08 - 내부 검증 로그 state_id 문자열 직렬화 대응

- 작업 이름: `validation_context.linked_state_id`가 문자열로 저장되어도 라우터가 검증 경고를 복원
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록의 `validation_context`는 보통 정수 `linked_state_id`를 담지만, 로그 직렬화/파서 경로가 바뀌면 `'31'`처럼 문자열 ID로 남을 수 있다.
  - 기존 `internal_validation_event_from_line()`은 `before.linked_state_id`가 정수일 때만 제거/확인 경고를 복원해, 문자열 ID 로그에서는 오래된 자동 실행 차단 힌트를 놓칠 수 있었다.
  - `before.linked_state_id`와 `after.linked_state_id`를 `coerce_artifact_id()`로 정규화하도록 바꿔 문자열 숫자도 같은 state id로 처리하게 했다.
  - `test_router_parses_internal_validation_state_id_when_serialized_as_string`를 추가해 문자열 `linked_state_id`가 들어간 `validation_context`에서도 `internal_validation_clarified_state_ids()`가 `{31}`을 반환하는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_parses_internal_validation_removed_state_ids tests/test_router_agent.py::test_router_parses_internal_validation_state_id_when_serialized_as_string tests/test_router_agent.py::test_router_validation_clarified_state_is_cleared_by_latest_success_even_if_line_appears_first tests/test_router_agent.py::test_router_validation_removed_state_is_cleared_by_latest_success_even_if_line_appears_first -q`(`4 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_router_agent.py -q`(`145 passed`)를 통과했다.

## 2026-06-08 - 최근 대화 원문 프롬프트와 에이전트 헬퍼 정렬

- 작업 이름: 라우터 프롬프트와 Memory/Task/Reminder 헬퍼의 최근 대화 원문 해석을 일치
- 진행상황: 완료
- 진행내용:
  - 라우터/검증 계층에서 `방금 한 말`, `아까 얘기했던 내용`, `전에 말한거`를 최근 대화 원문 참조로 확장했지만, 모델 라우터 프롬프트와 실제 에이전트 recent-message 헬퍼가 같은 폭을 갖는지 다시 점검했다.
  - 라우터 프롬프트에 `방금 한 말 메모해줘`, `아까 얘기했던 내용 기억해줘`를 최근 대화 원문 저장/등록 예시로 추가하고, `방금 생각난 거`는 저장할 본문이 없는 새 생각 요청이라고 명시했다.
  - `asks_to_remember_recent_message()`, `asks_to_create_task_from_recent_message()`, `asks_to_create_reminder_from_recent_message()`가 공통 recent conversation marker를 보도록 연결했다.
  - `방금 생각난 거` 계열은 recent-message 헬퍼에서 제외해 `asks_to_remember_unspecified_recent_thought()`와 같은 본문 없음 처리 흐름과 분리했다.
  - `test_router_agent_prefers_model_route_over_heuristic`, `test_substantive_memory_text_ignores_file_only_instruction`, `test_task_request_helpers`를 보강했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_agent_prefers_model_route_over_heuristic tests/test_router_heuristics.py::test_substantive_memory_text_ignores_file_only_instruction tests/test_router_heuristics.py::test_task_request_helpers -q`(`3 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_router_heuristics.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`571 passed`)를 통과했다.

## 2026-06-08 - 내부 검증 로그 context_link 정규화

- 작업 이름: `validation_context`와 `route_context`의 `context_link` 공백/대소문자 차이를 같은 의미로 처리
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록은 라우터와 검증층이 공유하는 핵심 맥락 단서이므로, 로그 직렬화 과정에서 `context_link`가 `' none '` 또는 `' continue '`처럼 남아도 의미가 달라지면 안 된다.
  - `normalize_context_link()`를 추가해 내부 검증 이벤트 복원, 성공 route 경고 해제, 대상 없는 clarify 새 요청 감지에서 같은 정규화 기준을 사용하도록 했다.
  - `test_router_parses_internal_validation_context_link_with_extra_spaces`를 추가해 공백이 섞인 `validation_context`도 자동 연결 제거 경고로 복원되는지 고정했다.
  - `test_router_validation_warning_is_cleared_by_spaced_successful_route_context`를 추가해 공백이 섞인 최신 성공 `route_context`가 오래된 검증 경고를 정상 해제하는지 고정했다.
  - `test_router_parses_internal_validation_state_id_string_with_extra_spaces`를 추가해 `linked_state_id`가 공백 포함 문자열로 직렬화되어도 같은 state id로 복원되는 계약을 회귀 테스트로 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_parses_internal_validation_state_id_string_with_extra_spaces tests/test_router_agent.py::test_router_parses_internal_validation_context_link_with_extra_spaces tests/test_router_agent.py::test_router_validation_warning_is_cleared_by_spaced_successful_route_context -q`(`3 passed`)를 통과했다.

## 2026-06-08 - 내부 행동 로그 linked_state_id 공백 문자열 대응

- 작업 이름: `route_context.linked_state_id`가 `' 44 '`처럼 저장되어도 라우터가 최근 작업 후보를 복원
- 진행상황: 완료
- 진행내용:
  - `validation_context.linked_state_id`는 `coerce_artifact_id()`를 사용해 문자열 숫자를 처리하지만, `internal_action_context_by_linked_state()`가 쓰는 `parse_internal_action_linked_state_id()`는 별도 수동 파싱으로 `linked_state_id=' 44 '` 같은 공백 포함 문자열을 놓칠 수 있었다.
  - 이 경우 내부 행동 기록에는 작업 슬롯/행동/대상 힌트가 있어도 state id를 읽지 못해 다음 턴 라우터가 이전 작업 후보를 잃을 수 있다.
  - `coerce_artifact_id()`가 문자열을 `strip()` 후 숫자로 변환하도록 보강하고, `parse_internal_action_linked_state_id()`도 같은 중앙 정규화 함수를 사용하도록 통일했다.
  - `test_router_parses_internal_route_context_linked_state_id_with_spaces`를 추가해 `route_context={'context_link': ' continue ', 'linked_state_id': ' 44 '}` 형태에서도 state 44의 슬롯, 행동, 대상 힌트가 복원되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_parses_internal_route_context_linked_state_id_with_spaces tests/test_router_agent.py::test_router_parses_structured_internal_route_context_when_reason_route_is_trimmed tests/test_router_agent.py::test_router_parses_internal_validation_context_link_with_extra_spaces tests/test_router_agent.py::test_router_validation_warning_is_cleared_by_spaced_successful_route_context -q`(`4 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_router_agent.py -q`(`148 passed`)와 `python3 -m pytest tests/test_context_builder.py -k "internal_action or validation_context or linked_state" -q`(`12 passed, 68 deselected`)를 통과했다.
  - 정적 검증으로 `python3 -m ruff check assistant_bot/agents/router.py tests/test_router_agent.py`를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1263 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 내부 행동 로그 created_at 포맷 정규화

- 작업 이름: 내부 검증 경고와 최신 성공 로그의 시간 비교가 `T`, `Z`, timezone offset 포맷 차이에 흔들리지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `latest_internal_validation_events()`는 state id별로 최신 검증 이벤트와 최신 성공 실행을 비교해 오래된 자동 연결 제거/확인 경고를 무시한다.
  - 기존 비교는 `created_at` 문자열을 그대로 사용해 `2026-06-05T12:05:00`과 `2026-06-05 12:10:00`처럼 ISO `T` 구분자와 공백 구분자가 섞이면 실제 시간순과 다른 문자열 순서가 나올 수 있었다.
  - `normalize_internal_action_created_at()`을 추가해 비교 전에 ISO `T`, `Z`, timezone offset을 파싱하고, timezone-aware 값은 UTC 기준 naive 문자열로 통일하도록 했다.
  - 파싱할 수 없는 값은 기존처럼 문자열 비교가 가능하도록 최소한 `T`를 공백으로 바꾼 값을 사용한다.
  - `test_router_validation_removed_state_created_at_normalizes_iso_separator`를 추가해 더 이른 `T` 포맷 성공 로그가 더 늦은 공백 포맷 검증 경고를 잘못 지우지 않는지 고정했다.
  - `test_router_validation_clarified_state_created_at_normalizes_timezone_suffix`를 추가해 `Z`와 `+00:00` 포맷이 섞여도 최신 성공 로그가 오래된 clarify 경고를 정상 해제하는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_validation_removed_state_created_at_normalizes_iso_separator tests/test_router_agent.py::test_router_validation_clarified_state_created_at_normalizes_timezone_suffix tests/test_router_agent.py::test_router_validation_removed_state_uses_created_at_when_each_location_has_latest tests/test_router_agent.py::test_router_validation_clarified_state_uses_created_at_when_each_location_has_latest -q`(`4 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_router_agent.py -q`(`151 passed`)와 `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`266 passed`)를 통과했다.
  - 정적 검증으로 `python3 -m ruff check assistant_bot/agents/router.py tests/test_router_agent.py`를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1267 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 상태 후보 최신순 선택 created_at 정규화

- 작업 이름: `방금/최근/마지막` 후보 선택도 `created_at` 포맷 차이에 흔들리지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 내부 검증 로그의 최신성 비교는 `normalize_internal_action_created_at()`을 사용하지만, fallback 라우터의 `prefer_latest_current_location_match()`는 `StateCandidate.created_at` 원문 문자열을 그대로 비교하고 있었다.
  - 이 상태에서는 현재 위치 후보가 여러 개이고 사용자가 `최근거 보여줘`, `방금 그거 다시해줘`처럼 시간 의존 후속 표현을 썼을 때, `2026-06-05T12:05:00` 후보가 실제로 더 늦은 `2026-06-05 12:10:00` 후보보다 최신으로 선택될 수 있었다.
  - `prefer_latest_current_location_match()`가 `normalize_internal_action_created_at(candidate.created_at)`을 기준으로 정렬하도록 바꿔 내부 로그와 상태 후보 최신성 기준을 일치시켰다.
  - `test_prefer_latest_current_location_match_normalizes_created_at_format`를 추가해 `T` 포맷의 더 이른 후보와 공백 포맷의 더 늦은 후보가 함께 있을 때 실제 최신 후보를 고르는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_prefer_latest_current_location_match_normalizes_created_at_format tests/test_router_agent.py::test_router_fallback_reuses_state_when_latest_success_appears_before_older_removed_warning tests/test_router_agent.py::test_router_validation_removed_state_created_at_normalizes_iso_separator -q`(`3 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_router_agent.py -q`(`152 passed`)와 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`186 passed`)를 통과했다.
  - 정적 검증으로 `python3 -m ruff check assistant_bot/agents/router.py tests/test_router_agent.py`를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1270 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 응답 필터의 비공개 라우팅 키 prefix 처리

- 작업 이름: 새 에이전트가 만든 파생 내부 키도 최종 응답 모델 입력에서 제거
- 진행상황: 완료
- 진행내용:
  - 기존 응답 필터는 `route_context`, `validation_context`, `tool_call_trace`처럼 정확히 일치하는 비공개 키를 제거했지만, 새 에이전트가 `route_context_debug`, `validation_context_raw`, `tool_context_raw` 같은 파생 키를 넣으면 응답 모델 입력에 남을 수 있었다.
  - `RESPONSE_PRIVATE_ROUTE_SLOT_KEY_PREFIXES`와 `is_private_route_key()`를 추가해 `pending_*`, `linked_state*`, `route_context*`, `validation_context*`, `current_message_context*`, `tool_call*`, `tool_context*` 계열을 내부 메타데이터로 처리하도록 했다.
  - 구조화 dict 필터(`route_safe_values`, `sanitize_private_route_values`)와 문자열 필터가 같은 prefix 패턴을 사용하도록 정렬했다.
  - 추가로 `linked_`, `link_confidence`, `candidate_`, `selected_` 계열도 prefix 계약에 포함해 `linked_subject_debug`, `link_confidence_raw`, `candidate_count_raw`, `selected_index_reason` 같은 새 에이전트 파생 키가 응답 모델 입력에 남지 않도록 했다.
  - `test_response_private_route_prefix_keys_are_filtered_from_result_and_context`를 추가해 OperationResult의 facts/slots/summary/fallback과 ExecutionContext resolved slots에서 파생 내부 키가 제거되는지 고정했다.
  - `test_response_private_route_prefixes_cover_internal_diagnostic_families`를 추가해 주요 내부 진단 키 계열이 prefix 계약에 포함되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_response_composer.py::test_response_private_route_prefix_keys_are_filtered_from_result_and_context tests/test_response_composer.py::test_response_private_route_prefixes_cover_internal_diagnostic_families tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context -q`(`3 passed`)와 `python3 -m pytest tests/test_response_composer.py -q`(`42 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_internal_route_context_keys_are_private_for_response_composer tests/test_agent_registry.py::test_catalog_target_slot_names_do_not_include_private_route_metadata -q`(`2 passed`)와 `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py -q`(`162 passed`)를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1268 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 에이전트 결과 계약의 내부 키 prefix 허용

- 작업 이름: 새 에이전트가 반환하는 파생 내부 메타데이터 키를 state output 선언 대상으로 오해하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 응답 필터는 `route_context*`, `validation_context*`, `tool_context*` 같은 prefix 계열을 비공개 메타데이터로 처리하지만, `validate_operation_result_contract()`는 exact key 중심이라 새 에이전트가 이런 값을 `slots`에 담으면 미선언 state output으로 거부될 수 있었다.
  - `is_internal_result_slot_key()`를 추가해 에이전트 결과 계약도 응답 필터와 같은 `is_private_route_key()` 기준을 사용하도록 정렬했다.
  - 이 과정에서 helper 위치가 검증 함수 중간에 들어가 available_actions/artifacts 검증이 빠지는 회귀가 드러났고, helper를 함수 밖으로 옮겨 기존 계약 검증을 유지했다.
  - `test_registry_treats_private_route_prefix_keys_as_internal_result_metadata`를 추가해 `route_context_debug`, `validation_context_raw`, `tool_context_raw`, `pending_candidate_state_ids_debug`, `tool_call_trace_extra`가 내부 결과 메타데이터로 허용되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_registry_treats_private_route_prefix_keys_as_internal_result_metadata tests/test_agent_registry.py::test_registry_dispatch_rejects_result_actions_not_declared_in_catalog tests/test_agent_registry.py::test_registry_dispatch_rejects_result_artifacts_not_declared_in_catalog tests/test_agent_registry.py::test_registry_dispatch_rejects_result_artifacts_without_linkable_target -q`(`4 passed`)와 `python3 -m pytest tests/test_agent_registry.py tests/test_response_composer.py -q`(`124 passed`)를 통과했다.

## 2026-06-08 - turn state 저장의 내부 prefix 메타데이터 제거

- 작업 이름: 확인 대기 상태에는 필요한 pending 슬롯만 남기고 내부 파생 키는 저장하지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 응답 필터와 에이전트 결과 계약은 내부 prefix 키를 비공개 메타데이터로 처리하지만, turn state 저장 경로의 `sanitized_turn_state_slots()`는 completed 상태에서 exact private key만 제거하고 있었다.
  - 확인 대기 상태는 `pending_original_text`, `pending_candidate_state_ids` 같은 pending 키를 유지해야 하므로, pending 전용 키는 보존하되 `route_context_debug`, `validation_context_raw`, `tool_context_raw`, `selected_index_debug` 같은 내부 파생 키는 저장하지 않도록 했다.
  - `context_link` 계열도 내부 연결 메타데이터 prefix에 포함해 `context_link_debug` 같은 값이 응답/상태 저장 경로에 남지 않도록 했다.
  - `test_sanitized_turn_state_slots_preserves_pending_keys_but_removes_private_prefix_metadata`를 추가해 pending 확인 상태의 필수 슬롯 보존과 내부 파생 키 제거를 함께 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_sanitized_turn_state_slots_preserves_pending_keys_but_removes_private_prefix_metadata tests/test_bot_helpers.py::test_sanitized_turn_state_slots_removes_private_route_metadata_for_completed_state tests/test_response_composer.py::test_response_private_route_prefixes_cover_internal_diagnostic_families -q`(`3 passed`)와 `python3 -m pytest tests/test_bot_helpers.py tests/test_response_composer.py tests/test_agent_registry.py -q`(`313 passed`)를 통과했다.

## 2026-06-08 - pending turn state 중첩 슬롯 정리

- 작업 이름: 확인 대기 상태의 일반 슬롯/중첩 값에서도 내부 라우팅 메타데이터를 제거
- 진행상황: 완료
- 진행내용:
  - 확인 대기 상태는 `pending_original_text`, `pending_candidate_state_ids`, `pending_resolved_slots` 같은 키를 유지해야 하지만, 그 외 일반 슬롯이나 `pending_resolved_slots` 내부에 `route_context_debug`, `validation_context_raw` 같은 내부 파생 키가 남으면 다음 턴 후보 상태가 오염될 수 있었다.
  - `sanitized_pending_turn_state_slots()`와 `sanitized_pending_turn_state_value()`를 추가해 pending 전용 키는 보존하되, 일반 슬롯과 pending resolved slots의 중첩 값은 `route_safe_values()`로 정리하도록 했다.
  - `pending_original_text`는 사용자의 원문 복원에 필요한 값이므로 그대로 보존하고, 실행용 resolved slots와 대상 보조 값만 내부 키를 제거한다.
  - `test_sanitized_turn_state_slots_preserves_pending_keys_but_removes_private_prefix_metadata`를 확장해 nested `target.route_context`, `target.validation_context_raw`, `pending_resolved_slots.route_context_debug`, 내부 표기가 섞인 `note`가 저장 전 정리되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_sanitized_turn_state_slots_preserves_pending_keys_but_removes_private_prefix_metadata tests/test_bot_helpers.py::test_sanitized_turn_state_slots_removes_private_route_metadata_for_completed_state -q`(`2 passed`)와 `python3 -m pytest tests/test_bot_helpers.py -q`(`189 passed`)를 통과했다.

## 2026-06-08 - state_outputs 비공개 prefix 검증과 pending_query 보존

- 작업 이름: 에이전트 카탈로그의 내부 메타데이터 선언을 prefix 기준으로 막되 공개 pending query는 보존
- 진행상황: 완료
- 진행내용:
  - 런타임 결과 계약과 응답/상태 필터는 `route_context*`, `validation_context*` 같은 prefix를 비공개로 처리하지만, `agent_catalog.json`의 `state_outputs` 검증은 exact key만 막고 있어 `slots.route_context_debug` 같은 선언을 놓칠 수 있었다.
  - `build_agent_definition()`의 private state output 검증을 `is_private_route_key()` 기준으로 맞추고, `test_build_agent_definition_rejects_private_or_unpreserved_state_outputs`에 `slots.route_context_debug`, `artifacts.validation_context_raw` 케이스를 추가했다.
  - 이 과정에서 broad `pending_` prefix가 공개 슬롯 `pending_query`까지 비공개로 오인하는 문제를 발견해, `pending_candidate_`, `pending_context_`, `pending_linked_`, `pending_original_`, `pending_resolved_`처럼 실제 내부 메타데이터 계열로 좁혔다.
  - `test_agent_catalog_state_outputs_do_not_declare_private_route_metadata`가 prefix 기준으로 카탈로그 선언을 감시하도록 바꿨다.
  - `test_response_private_route_prefixes_do_not_hide_public_pending_query`를 추가해 웹 검색 확인용 `pending_query`가 최종 응답 구성 입력에 남는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_build_agent_definition_rejects_private_or_unpreserved_state_outputs tests/test_agent_registry.py::test_agent_catalog_state_outputs_do_not_declare_private_route_metadata tests/test_response_composer.py::test_response_private_route_prefixes_cover_internal_diagnostic_families -q`(`3 passed`), `python3 -m pytest tests/test_response_composer.py::test_response_private_route_prefixes_do_not_hide_public_pending_query tests/test_response_composer.py::test_response_private_route_prefix_keys_are_filtered_from_result_and_context tests/test_agent_registry.py::test_agent_catalog_state_outputs_do_not_declare_private_route_metadata -q`(`3 passed`), `python3 -m pytest tests/test_agent_registry.py tests/test_response_composer.py -q`(`125 passed`)를 통과했다.

## 2026-06-08 - pending_query turn state 보존 회귀 고정

- 작업 이름: 웹 검색 확인 대기의 공개 query 슬롯이 상태 저장 필터에서 제거되지 않도록 테스트 보강
- 진행상황: 완료
- 진행내용:
  - `pending_query`는 내부 pending 메타데이터가 아니라 웹 검색 확인 대기에서 사용자가 승인할 검색어를 나타내는 공개/실행 슬롯이다.
  - 응답 작성 입력에서는 이미 보존되도록 고정했지만, turn state 저장 필터에서도 `pending_query`와 `query_text`가 남고 `route_context_debug`, `reason` 같은 내부 값은 빠지는지 직접 테스트가 부족했다.
  - `test_sanitized_turn_state_slots_preserves_public_pending_query_for_confirmation`를 추가해 검색 확인 상태 저장 시 `pending_query`, `query_text`, 필요한 pending 원문/링크는 보존하고 내부 파생 키와 내부 reason은 제거되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_sanitized_turn_state_slots_preserves_public_pending_query_for_confirmation tests/test_bot_helpers.py::test_sanitized_turn_state_slots_preserves_pending_keys_but_removes_private_prefix_metadata tests/test_response_composer.py::test_response_private_route_prefixes_do_not_hide_public_pending_query -q`(`3 passed`)와 `python3 -m pytest tests/test_bot_helpers.py -q`(`191 passed`)를 통과했다.

## 2026-06-08 - 응답 결과의 내부 reason 슬롯 비공개 처리

- 작업 이름: 확인/라우팅 결과의 내부 `reason` 슬롯이 최종 응답 모델 입력에 노출되지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `build_context_clarification_result()`는 확인 대기 결과의 slots에 `reason=route.reason`을 넣어 내부 판단 근거를 보존하지만, 최종 응답 작성자는 사용자에게 보여줄 질문은 `fallback_text`와 summary/items로 충분히 구성할 수 있다.
  - `reason`을 `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`에 추가해 구조화 결과, resolved slots, raw text 경로에 섞여도 최종 응답 입력에서 제거되도록 했다.
  - `test_response_private_route_keys_hide_internal_reason_slot_but_keep_prompt_text`를 추가해 내부 reason은 제거하면서 `어느 작업을 삭제할까요?` 같은 사용자 확인 문구는 유지되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_response_composer.py::test_response_private_route_keys_hide_internal_reason_slot_but_keep_prompt_text tests/test_response_composer.py::test_response_private_route_keys_are_filtered_from_both_result_and_execution_context tests/test_agent_registry.py::test_registry_treats_private_route_prefix_keys_as_internal_result_metadata -q`(`3 passed`)와 `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py -q`(`127 passed`)를 통과했다.

## 2026-06-08 - 비공개 key 문자열 필터의 단어 경계 보강

- 작업 이름: `reason` 비공개 처리로 `unsupported_reason` 같은 공개 키가 잘못 잘리지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - `reason`을 비공개 key에 추가한 뒤 문자열 필터가 `unsupported_reason=...`의 뒤쪽 `reason=...`을 독립 키처럼 오인할 수 있는 위험을 확인했다.
  - `PRIVATE_ROUTE_TEXT_ASSIGNMENT_PATTERN`을 추가해 비공개 key 할당 표현이 단어 중간에서 시작하지 않을 때만 제거되도록 했다.
  - `models.py`와 `response_composer.py`의 문자열 필터가 같은 정규식 패턴을 사용하도록 통일했다.
  - `test_response_private_route_text_filter_preserves_user_reason_text_and_public_reason_suffixes`를 추가해 `unsupported_reason`, `my_reason` 같은 공개 suffix key와 사용자 텍스트의 `reason=...`이 보존되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_response_composer.py::test_response_private_route_text_filter_preserves_user_reason_text_and_public_reason_suffixes tests/test_response_composer.py::test_response_private_route_keys_hide_internal_reason_slot_but_keep_prompt_text tests/test_response_composer.py::test_response_private_route_metadata_is_filtered_from_nested_string_values -q`(`3 passed`)와 `python3 -m pytest tests/test_response_composer.py -q`(`46 passed`)를 통과했다.

## 2026-06-08 - 사용자 텍스트의 `reason=` 보존

- 작업 이름: `reason`은 구조화 내부 key로만 숨기고 사용자 문자열 내용은 보존
- 진행상황: 완료
- 진행내용:
  - `reason`을 비공개 key로 추가한 뒤 문자열 필터에서도 독립 `reason=...`을 지우면, 사용자가 메모/문서/설정값에 실제로 적은 `reason=테스트 실패` 같은 텍스트까지 손상될 수 있음을 확인했다.
  - `RESPONSE_PRIVATE_ROUTE_TEXT_KEYS`를 추가해 문자열 할당 표현 필터에서는 `reason`을 제외하고, dict key 필터에서는 기존처럼 `reason` key를 제거하도록 분리했다.
  - `test_response_private_route_text_filter_preserves_user_reason_text_and_public_reason_suffixes`로 `unsupported_reason`, `my_reason`, 사용자 `memory_text` 안의 `reason=...`이 보존되는지 고정했다.
  - 기존 `test_response_private_route_keys_hide_internal_reason_slot_but_keep_prompt_text`는 `slots.reason` 같은 구조화 내부 key가 계속 제거되는지 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_response_composer.py::test_response_private_route_keys_hide_internal_reason_slot_but_keep_prompt_text tests/test_response_composer.py::test_response_private_route_text_filter_preserves_user_reason_text_and_public_reason_suffixes tests/test_response_composer.py::test_response_private_route_metadata_is_filtered_from_nested_string_values -q`(`3 passed`)와 `python3 -m pytest tests/test_response_composer.py -q`(`46 passed`)를 통과했다.

## 2026-06-08 - 내부 행동 로그 trimming 시 route_context 보존

- 작업 이름: 긴 내부 행동 로그에서도 `route_context.linked_state_id`가 라우터 컨텍스트에 남도록 보강
- 진행상황: 완료
- 진행내용:
  - 문자열 필터 보강 뒤 전체 테스트에서 긴 내부 행동 로그가 잘릴 때 `route_context`가 사라져 라우터가 `linked_state_id`를 잃는 회귀가 드러났다.
  - 내부 행동 로그 trimming은 tail 보존 방식이므로, 라우터가 가장 중요하게 쓰는 `route_context`를 줄 끝으로 배치해 긴 로그에서도 구조화 연결 정보가 남도록 했다.
  - 실패했던 `test_build_router_context_keeps_parseable_internal_route_context_when_trimmed`, `test_build_router_context_does_not_include_partial_internal_action_line_when_trimmed`로 긴 로그에서도 route context가 parse 가능하게 남는지 재검증했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_router_context_keeps_parseable_internal_route_context_when_trimmed tests/test_context_builder.py::test_build_router_context_does_not_include_partial_internal_action_line_when_trimmed -q`(`2 passed`), `python3 -m pytest tests/test_context_builder.py -q`(`80 passed`), `python3 -m pytest -q`(`1279 passed`)를 통과했다.

## 2026-06-08 - 내부 로그 `route_context` 후방 배치 파서 계약 고정

- 작업 이름: `route_context`가 `link_guidance` 뒤에 있어도 라우터가 연결 슬롯을 복원
- 진행상황: 완료
- 진행내용:
  - 긴 내부 행동 로그에서 route context를 보존하기 위해 `route_context`를 줄 끝으로 옮겼으므로, 라우터 파서가 새 필드 순서에서도 `linked_state_id`, `resolved_slots`, `target_hints`, actions를 모두 복원해야 한다.
  - `test_router_parses_internal_route_context_after_link_guidance`를 추가해 `target_hints -> link_guidance -> route_context` 순서의 내부 행동 로그가 정상 파싱되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_parses_internal_route_context_after_link_guidance tests/test_router_agent.py::test_router_parses_internal_route_context_url_title_slots tests/test_context_builder.py::test_build_router_context_keeps_parseable_internal_route_context_when_trimmed -q`(`3 passed`)와 `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py -q`(`235 passed`)를 통과했다.

## 2026-06-08 - 현재 메시지 진단 하위 키의 응답 비공개 처리

- 작업 이름: `assistant_example_reference`, `decision_hint` 같은 라우팅 진단값이 최종 응답 모델 입력에 새지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `current_message_context` 전체 섹션은 응답용 컨텍스트에서 제거되고 있었지만, raw `conversation_context`가 한 줄 형태로 들어오거나 진단 하위 키가 별도 문자열로 섞이면 `effective_text`, `decision_hint`, `assistant_example_reference`, `confirmation_approval` 같은 내부 판단값이 남을 수 있는 경계를 확인했다.
  - `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`에 현재 메시지 진단 전용 하위 키를 추가해, 구조화 결과, resolved slots, linked state, raw conversation fallback 어디에 섞여도 응답용 경로에서 제거되도록 했다.
  - `text`처럼 실제 메모/문서/도메인 값과 충돌할 수 있는 범용 키는 비공개 키로 추가하지 않고, 라우팅 진단 전용 키만 제한적으로 추가했다.
  - `test_response_composer_sanitizes_inline_current_message_diagnostics_without_sections`를 추가해 섹션 없는 raw context에서도 `current_message_context`, `effective_text`, `assistant_self_reference`, `assistant_example_reference`, `confirmation_*`, `decision_hint`가 최종 응답 모델 입력에 남지 않는지 고정했다.
  - `test_response_private_route_keys_include_current_message_diagnostics`를 추가해 새 진단 키들이 응답 비공개 키 계약에 포함되는지 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_response_composer.py -q`(`40 passed`)를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_internal_route_diagnostic_keys_do_not_become_execution_targets tests/test_agent_registry.py::test_internal_route_context_keys_are_private_for_response_composer tests/test_agent_registry.py::test_catalog_target_slot_names_do_not_include_private_route_metadata tests/test_response_composer.py::test_execution_context_hides_route_validation_current_message_diagnostics_from_agent_and_response -q`(`4 passed`)와 `python3 -m pytest tests/test_context_builder.py::test_build_current_message_context_marks_assistant_example_reference_without_confirmation tests/test_router_agent.py::test_router_prompt_explains_assistant_example_reference_not_confirmation tests/test_router_agent.py::test_router_fallback_does_not_treat_assistant_example_reference_as_pending_approval -q`(`3 passed`)를 통과했다.
  - 정적 검증으로 `python3 -m ruff check assistant_bot/models.py tests/test_response_composer.py`를 통과했다.
  - 전체 검증으로 `python3 -m pytest -q`(`1259 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - pending 확인 상태 최신성 선택 보강

- 작업 이름: 짧은 승인/거부 답변이 오래된 확인 질문에 잘못 붙지 않도록 pending 상태 선택 기준 보강
- 진행상황: 완료
- 진행내용:
  - `latest_pending_context_state()`가 이름과 달리 후보 목록의 첫 번째 pending 상태를 그대로 반환하고 있어, 후보 배열 순서가 바뀌면 `응`, `좋아`, `아니` 같은 짧은 답변이 오래된 확인 질문에 연결될 수 있었다.
  - `pending_context_state_latest_key()`와 `normalize_turn_state_created_at()`을 추가해 pending 확인 상태를 `created_at` 기준으로 먼저 비교하고, 시간이 같거나 애매한 경우 state id로 최신 상태를 고르도록 했다.
  - ISO `T` 포맷, `Z` suffix, timezone offset이 섞여도 최신성 비교가 같은 기준으로 작동하도록 정규화했다.
  - `test_latest_pending_context_state_returns_newest_pending_candidate`를 수정해 후보 순서가 오래된 pending 먼저 들어와도 실제 최신 pending을 선택하는지 고정했다.
  - `test_latest_pending_context_state_normalizes_created_at_before_selecting_latest`를 추가해 `2026-06-05T12:01:00Z` 같은 포맷이 단순 문자열 비교로 최신 처리되지 않도록 회귀 테스트를 넣었다.
  - `test_pending_context_approval_only_uses_latest_pending_candidate`도 후보 순서를 반대로 넣어 최신 pending만 승인 대상으로 쓰는지 확인하도록 보강했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_route_validation.py -k "latest_pending_context_state or pending_context_approval_only_uses_latest_pending_candidate"`(`3 passed`)와 `python3 -m ruff check assistant_bot/route_validation.py tests/test_route_validation.py`를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest -q tests/test_context_routing_matrix.py tests/test_route_validation.py`(`377 passed`)와 `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-08 - pending 후보 선택 매칭 최신순 정렬

- 작업 이름: 같은 pending 원문이 여러 번 남아도 최신 확인 상태를 먼저 처리하도록 후보 선택 매칭 정렬
- 진행상황: 완료
- 진행내용:
  - `latest_pending_context_state()`는 최신 pending을 고르도록 보강했지만, `matching_pending_candidate_selection_states()`와 `matching_resolved_pending_context_states()`는 매칭된 상태 목록을 후보 배열 순서 그대로 반환하고 있었다.
  - 호출부는 매칭 상태를 모두 만료하지만, 내부 로그와 처리 순서가 후보 배열에 의존하면 같은 원문 확인 질문이 중복 생성된 상황에서 오래된 확인 상태가 먼저 처리되는 흐름이 남을 수 있었다.
  - 두 매칭 함수가 `pending_context_state_latest_key()`를 사용해 최신 생성 시각, state id 기준 내림차순으로 결과를 반환하도록 정렬했다.
  - `test_matching_pending_candidate_selection_states_returns_newest_matches_first`를 추가해 같은 `pending_original_text`를 가진 후보 선택 확인 상태가 여러 개일 때 최신 상태가 먼저 반환되는지 고정했다.
  - `test_matching_resolved_pending_context_states_returns_newest_matches_first`를 추가해 명시적 후속 요청 처리 후 pending 확인 상태를 정리할 때도 최신 상태부터 반환되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_route_validation.py -k "matching_pending_candidate_selection_states or matching_resolved_pending_context_states or latest_pending_context_state"`(`6 passed`)와 `python3 -m ruff check assistant_bot/route_validation.py tests/test_route_validation.py`를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest -q tests/test_context_routing_matrix.py tests/test_route_validation.py`(`379 passed`)를 통과했다.

## 2026-06-08 - 연결된 작업 상태의 위치 신호 유지

- 작업 이름: 라우터 승인 뒤 전문 에이전트와 응답 작성자도 linked state가 현재 위치/다른 위치인지 인지하도록 보강
- 진행상황: 완료
- 진행내용:
  - 라우터 입력의 최근 작업 상태 후보에는 `location=현재 위치/다른 위치`, `confirm_policy`, `suggested_question`이 포함되지만, 라우터가 특정 `linked_state`를 선택한 뒤 에이전트/응답 모델에 전달되는 `연결된 이전 작업 상태`에는 `conversation_id`만 있고 위치 라벨이 직접 표시되지 않았다.
  - 이 상태에서는 사용자가 다른 채팅 위치에서 하던 작업을 승인해 이어가는 경우, 전문 에이전트나 응답 작성자가 “위치가 바뀐 작업”이라는 사실을 명확히 참고하기 어려웠다.
  - `ExecutionContext`에 `current_conversation_id`를 추가하고, `build_execution_context()`가 현재 scope의 `conversation_id`를 채우도록 했다.
  - `agent_safe_turn_state_context()`와 `response_safe_turn_state_context()`가 현재 conversation id를 받으면 linked state에 `location=현재 위치` 또는 `location=다른 위치`를 함께 출력하도록 했다.
  - 기존 직접 생성 테스트와 호환되도록 현재 conversation id가 없으면 location 라벨을 생략한다.
  - `test_build_execution_context_links_cross_location_turn_state_for_same_user`를 보강해 다른 위치 linked state가 에이전트/응답 컨텍스트에서 `location=다른 위치`로 보이는지 고정했다.
  - `test_execution_context_marks_linked_state_location_for_agent_and_response`를 추가해 `ExecutionContext` 직렬화 자체도 linked state 위치 라벨을 유지하는지 확인했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_context_builder.py::test_build_execution_context_links_cross_location_turn_state_for_same_user tests/test_response_composer.py::test_execution_context_marks_linked_state_location_for_agent_and_response`(`2 passed`)와 `python3 -m ruff check assistant_bot/models.py assistant_bot/context_builder.py tests/test_context_builder.py tests/test_response_composer.py`를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest -q tests/test_context_builder.py tests/test_response_composer.py tests/test_memory_store.py -k "execution_context or linked_state or response_context or cross_location"`(`41 passed, 204 deselected`)와 `python3 -m pytest -q tests/test_context_routing_matrix.py tests/test_router_agent.py -k "cross_location or linked_state or current_location"`(`40 passed, 298 deselected`)를 통과했다.

## 2026-06-08 - 내부 검증 이벤트의 위치 범위 분리

- 작업 이름: 다른 위치 내부 검증 경고가 현재 위치 후속 연결을 과하게 막지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록은 `location_priority=current_location/cross_location`과 `context_policy`를 포함하지만, `internal_validation_removed_state_ids()`와 `internal_validation_clarified_state_ids()`는 state id만 반환해 검증 이벤트가 어느 위치에서 발생했는지 잃고 있었다.
  - 이 상태에서는 다른 위치에서 “자동 실행하지 말고 확인으로 바꿈” 또는 “자동 연결 제거”가 발생한 기록이 현재 위치의 정상 후속 요청까지 막는 hard signal로 작동할 수 있었다.
  - `latest_internal_validation_events()`가 현재 위치 내부 행동 로그만 자동 연결 차단/확인 필요 이벤트로 반영하도록 `internal_action_line_is_current_location()` 필터를 추가했다.
  - `location_priority=current_location`이 있으면 이를 우선 사용하고, 구형 라인처럼 `location=현재 위치`만 있는 경우도 현재 위치로 인식하도록 했다. 위치 정보가 없는 구형 테스트/로그는 기존 호환을 위해 현재 위치로 취급한다.
  - 다른 위치 내부 로그는 여전히 라우터의 배경 참고, 후보 보강, cross-location 확인 질문 단서로 남지만 현재 위치 후보를 제거하거나 확인으로 강제하는 신호로는 쓰지 않는다.
  - `test_router_validation_removed_state_ignores_newer_cross_location_warning`를 추가해 더 최신의 다른 위치 제거 경고가 현재 위치 성공 연결을 막지 않는지 고정했다.
  - `test_router_validation_removed_state_created_at_normalizes_iso_separator`는 현재 위치끼리의 시간 비교 테스트로 재정렬해 created_at 정규화 보장을 유지했다.
  - `test_router_validation_clarified_state_ignores_newer_cross_location_warning`를 추가해 다른 위치 clarify 경고가 현재 위치 자동 연결을 확인 질문으로 강제하지 않는지 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_router_agent.py -k "internal_validation_removed_state_ids or internal_validation_clarified_state_ids or validation_removed_state or validation_clarified_state"`(`17 passed, 137 deselected`)와 `python3 -m ruff check assistant_bot/agents/router.py tests/test_router_agent.py`를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest -q tests/test_router_agent.py tests/test_context_routing_matrix.py`(`340 passed`)와 `python3 -m pytest -q tests/test_context_builder.py -k "internal_action or cross_location or route_validation"`(`17 passed, 63 deselected`)를 통과했다.

## 2026-06-08 - 내부 로그 hard/soft signal 프롬프트 정렬

- 작업 이름: 모델 라우터도 현재 위치 내부 검증 로그와 다른 위치 배경 로그를 구분하도록 지시 보강
- 진행상황: 완료
- 진행내용:
  - 코드 경로에서는 다른 위치 내부 검증 경고를 현재 위치 자동 연결 차단 신호로 쓰지 않도록 분리했지만, 라우터 프롬프트의 `validation_guidance` 설명은 위치 구분 없이 “자동 연결 제거/확인 필요 이력”으로만 설명하고 있었다.
  - 이 상태에서는 모델 응답 경로가 `location_priority=cross_location` 로그를 현재 위치 후보 차단 근거처럼 오해할 수 있었다.
  - 라우터 프롬프트에 `location_priority=current_location`인 `validation_guidance`만 현재 위치 후보의 hard signal이며, `location_priority=cross_location` 또는 `context_policy=background_only_ask_before_execute_when_follow_up` 로그는 다른 위치 soft signal이라고 명시했다.
  - 다른 위치 soft signal은 현재 위치 작업 상태를 제거하거나 현재 위치 후속 요청을 막는 근거가 아니라, 다른 위치 작업을 여기서 이어갈지 물어볼 때만 배경 단서로 참고하도록 지시했다.
  - 내부 행동 기록 컨텍스트 header에도 같은 원칙을 추가해, 라우터 입력 본문 자체가 `validation_guidance`의 위치별 의미를 설명하도록 했다.
  - `internal_action_validation_guidance()`가 현재 위치 로그에는 `현재 위치 hard signal`, 다른 위치 로그에는 `다른 위치 soft signal, 현재 위치 작업 차단 금지`를 함께 출력하도록 보강했다.
  - `internal_action_link_guidance()`도 다른 위치 내부 기록은 soft signal이며 현재 위치 작업 차단 신호로 쓰지 말라고 명시하도록 했다.
  - 프롬프트 회귀 테스트에 hard/soft signal 문구를 추가했고, context builder 테스트에는 header 정책과 cross-location soft signal 문구를 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_context_builder.py -k "internal_action or validation_guidance"`(`9 passed, 71 deselected`), `python3 -m pytest -q tests/test_router_agent.py -k "prompt or internal_validation or validation_removed_state or validation_clarified_state"`(`21 passed, 133 deselected`), `python3 -m ruff check assistant_bot/context_builder.py assistant_bot/agents/router.py tests/test_context_builder.py tests/test_router_agent.py`를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest -q tests/test_router_agent.py tests/test_context_builder.py tests/test_context_routing_matrix.py`(`420 passed`)를 통과했다.

## 2026-06-08 - 에이전트 state_outputs subject 필수화

- 작업 이름: 새 에이전트가 후속 맥락 후보 대표명 없이 추가되지 않도록 카탈로그 계약 보강
- 진행상황: 완료
- 진행내용:
  - `agent_catalog.json`의 모든 에이전트는 `state_outputs`에 `subject`를 선언하고 있지만, `build_agent_definition()` 자체는 이를 필수 계약으로 강제하지 않았다.
  - 새 에이전트가 `slots.*`나 `available_actions.*`만 선언하고 `subject`를 빠뜨리면, 라우터 후보에는 구조화 값이 남아도 사용자에게 확인할 대표 대상명이 약해져 “어느 작업을 이어갈까요?” 같은 질문과 후속 맥락 판단 품질이 떨어질 수 있다.
  - `build_agent_definition()`에 `subject` 필수 검증을 추가해, 지원 키/private key/action 검증을 통과한 정상 카탈로그 항목이라도 대표명 단서를 빼먹으면 등록 단계에서 실패하도록 했다.
  - 기존 private/unsupported state output 오류는 기존처럼 더 구체적인 오류가 먼저 나오도록 subject 검증은 마지막에 배치했다.
  - `test_catalog_entry_requires_subject_state_output`를 추가해 `state_outputs=["slots.topic"]` 같은 새 에이전트 정의가 거부되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_agent_registry.py -k "state_outputs or subject_state_output or catalog_entry or registry_prompt"`(`9 passed, 74 deselected`)와 `python3 -m ruff check assistant_bot/agent_registry.py tests/test_agent_registry.py`를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest -q tests/test_agent_registry.py tests/test_router_agent.py -k "catalog or registry or prompt or state_outputs"`(`84 passed, 154 deselected`)를 통과했다.

## 2026-06-08 - 메모 도구 호출 결과의 내부 artifact 추론 보강

- 작업 이름: tool calling 기반 메모 조회 결과가 kind를 생략해도 후속 맥락 대상 단서로 복원
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록은 `tool_call_trace.result_summary.items`를 turn state artifact로 추론해 다음 턴 라우터의 `target_hints`로 사용한다.
  - 기존 추론은 `search_tasks`, `list_tasks`, `list_due_tasks`는 task로 보정하지만, `search_memories`, `list_recent_memories` 결과가 `kind` 없이 id/title만 반환하면 memory artifact로 복원하지 못했다.
  - 새 에이전트가 메모 도구를 호출하면서 결과 item에 `kind`를 생략하면 내부 로그에는 tool_context만 남고, “메모 7”, “원주 날씨 기록” 같은 후속 대상 단서가 약해질 수 있었다.
  - `infer_tool_trace_artifact_kind()`가 `search_memories`, `list_recent_memories`, `get_memory_detail`을 memory artifact로 추론하도록 보강했다.
  - `test_tool_call_trace_result_summary_infers_memory_artifacts_from_tool_name`를 추가해 `search_memories` 결과 item에 `kind`가 없어도 `{"kind": "memory", "id": 7, "title": ...}` artifact가 만들어지는지 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py -k "tool_call_trace_result_summary_infers or record_internal_action_result_preserves_compact_tool_trace_context"`(`6 passed, 184 deselected`)와 `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py tests/test_context_builder.py -k "tool_call_trace or internal_action or target_hints"`(`41 passed, 230 deselected`)를 통과했다.

## 2026-06-08 - 컬렉션 목록 조회의 후속 맥락 오연결 방지

- 작업 이름: 메모/문서/파일/알림 목록 요청이 특정 이전 항목에 붙지 않도록 라우팅 검증 보강
- 진행상황: 완료
- 진행내용:
  - 사용자가 `메모 목록 보여줘`, `파일 목록 보여줘`, `알림 리스트 알려줘`처럼 컬렉션 전체 조회를 요청하는 경우, 라우터가 직전 메모/문서/알림 상태를 `continue`로 연결하면 특정 항목 조회처럼 처리될 위험이 있었다.
  - `unrelated_new_request_mismatch_linked_state()`에 컬렉션 목록 조회 판정을 추가해, 명확한 후속 지시가 아닌 목록/리스트 요청은 이전 작업 대상이 아닌 새 컬렉션 조회로 분리하도록 했다.
  - `asks_unrelated_collection_list_request()`를 추가해 메모, 기억, 문서, 파일, 첨부, 할 일, 작업, 알림, 리마인드 계열의 `목록/리스트/list` 요청을 공통으로 감지한다.
  - `has_ambiguous_follow_up_reference()` 검사는 기존처럼 먼저 적용되므로 `그 메모`, `그 문서`처럼 명시적으로 이전 대상을 가리키는 표현은 무조건 새 목록 요청으로 끊지 않는다.
  - `test_validate_route_context_link_clears_collection_list_request_from_specific_state`를 추가해 메모 목록, 파일 목록, 알림 리스트 요청이 각각 특정 이전 상태와 연결되어 들어와도 `context_link=none`으로 정리되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clears_collection_list_request_from_specific_state tests/test_route_validation.py::test_validate_route_context_link_clears_unrelated_utility_request_from_weather_retry tests/test_route_validation.py::test_validate_route_context_link_keeps_weather_detail_follow_up -q`(`5 passed`)와 `python3 -m ruff check assistant_bot/route_validation.py tests/test_route_validation.py`를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest tests/test_route_validation.py -q`(`196 passed`)와 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`186 passed`)를 통과했다.

## 2026-06-08 - 내부 행동 로그 artifact 보존 순서 보강

- 작업 이름: tool_context가 길어도 내부 행동 로그의 구조화 artifact 단서가 잘리지 않도록 순서 조정
- 진행상황: 완료
- 진행내용:
  - 전체 테스트 중 `test_record_internal_action_result_restores_typed_tool_ids_as_target_hints`가 실패해, 내부 행동 로그 컨텍스트에서 `target_hints`는 남지만 `artifacts=...` 구조화 조각이 보이지 않는 상황을 확인했다.
  - 원인은 `tool_context`가 길어 `internal_action_result_reason()`의 900자 압축 예산을 먼저 사용하면서, 뒤에 붙는 `artifacts`가 잘리는 순서였다.
  - 라우터가 내부 행동 기록에서 대상 ID와 종류를 더 안정적으로 참고할 수 있도록 `artifacts`를 `tool_context`보다 먼저 기록하게 조정했다.
  - 이 변경으로 tool calling 결과에서 추론한 `memory_ids`, `document_ids`, `task_ids`가 내부 행동 로그의 구조화 조각과 `target_hints` 양쪽에 남을 수 있게 했다.
  - `artifacts`가 `slots`보다 앞에 올 수 있게 되면서 라우터의 내부 행동 로그 파서가 `artifacts=... | slots=...` 형식을 읽도록 종료 조건에 `slots`를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_record_internal_action_result_restores_typed_tool_ids_as_target_hints tests/test_bot_helpers.py::test_tool_call_trace_result_summary_infers_memory_artifacts_from_tool_name -q`(`2 passed`), `python3 -m pytest tests/test_router_agent.py::test_router_parses_actual_internal_action_result_reason tests/test_router_agent.py::test_router_parses_internal_action_artifacts_as_candidate_slots tests/test_bot_helpers.py::test_record_internal_action_result_restores_typed_tool_ids_as_target_hints -q`(`3 passed`)와 `python3 -m ruff check assistant_bot/agents/router.py assistant_bot/bot.py tests/test_router_agent.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-08 - tool trace 도메인별 ID 필드 보존

- 작업 이름: 도구 결과가 `id` 대신 `memory_id/document_id/task_id/reminder_id`를 써도 내부 맥락 대상 단서로 유지
- 진행상황: 완료
- 진행내용:
  - 새 에이전트나 도구가 결과 item을 반환할 때 범용 `id` 대신 `memory_id`, `document_id`, `task_id`, `reminder_id` 같은 도메인별 ID 필드를 사용할 수 있다.
  - 기존 artifact 추론은 `id` 중심이라 typed ID만 있는 도구 결과에서는 내부 artifact와 `target_hints`가 약해질 수 있었다.
  - `infer_tool_trace_artifact_from_item()`이 도구 종류에 맞는 typed ID와 plural typed ID를 artifact에 복사하도록 보강했다.
  - `infer_tool_trace_artifact_kind()`가 `list_reminders`, `get_reminder_detail` 결과도 reminder artifact로 추론하도록 추가했다.
  - `compact_internal_action_tool_result_item()`도 `memory_ids`, `document_ids`, `task_ids`, `reminder_ids`까지 보존해, 라우터가 압축된 `tool_context`에서도 대상 ID를 직접 확인할 수 있게 했다.
  - `test_tool_call_trace_result_summary_preserves_typed_artifact_ids`를 추가해 typed ID 기반 결과가 memory/document/task/reminder artifact와 내부 artifact 값으로 복원되는지 고정했다.
  - `test_record_internal_action_result_restores_typed_tool_ids_as_target_hints`를 추가해 내부 행동 기록 컨텍스트에 typed ID와 `메모 7`, `문서 8`, `할 일 9`, `알림 10` 같은 사용자 친화 대상 단서가 남는지 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py -k "typed_tool_ids or typed_artifact_ids or tool_call_trace_result_summary_infers"`(`7 passed, 186 deselected`)와 `python3 -m ruff check assistant_bot/bot.py assistant_bot/context_builder.py tests/test_bot_helpers.py`를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py tests/test_context_builder.py -k "tool_call_trace or internal_action or target_hints"`(`43 passed, 230 deselected`)와 `python3 -m compileall assistant_bot tests`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1288 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - agents 패키지 export 누락 보정

- 작업 이름: 봇/CLI 직접 import 경로가 reminder helper 누락으로 깨지지 않도록 보정
- 진행상황: 완료
- 진행내용:
  - 전체 검증 중 CLI 계약 테스트가 helper source를 잘못 읽는 현상을 추적하다가, `assistant_bot.bot` 직접 import 시 `asks_to_delete_reminder`, `extract_reminder_ids`가 `assistant_bot.agents`에서 export되지 않아 ImportError가 나는 문제를 확인했다.
  - 두 helper는 `assistant_bot/agents/common.py`에는 존재하지만 `assistant_bot/agents/__init__.py`에 누락되어 있어, 봇 실행/import 경로가 환경에 따라 깨질 수 있었다.
  - `assistant_bot/agents/__init__.py`에 `asks_to_delete_reminder`, `extract_reminder_ids` export를 추가했다.
  - 알림 삭제 확인 흐름에서 사용하는 `_reminder_deletion_slots`, `reminder_ids_from_execution_context` 경로가 lint 기준으로 정상 인식되도록 import/export 상태를 정리했다.
  - 직접 검증으로 `assistant_bot.cli` import 후 `build_context_clarification_result`, `build_context_cancellation_result`의 source 위치가 `assistant_bot.bot`의 실제 helper로 잡히는지 확인했다.
  - 실패했던 `python3 -m pytest -q tests/test_cli.py::test_cli_clarification_result_records_linked_subject_contract tests/test_cli.py::test_cli_context_cancellation_uses_shared_result_contract`를 재실행해 `2 passed`를 확인했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1288 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 웹검색 후속 참조 marker 계약 정렬

- 작업 이름: 라우터가 아는 후속 참조 표현을 WebSearchAgent 실행 단계도 동일하게 인식하도록 보강
- 진행상황: 완료
- 진행내용:
  - 계획서에는 라우터뿐 아니라 Web Search, Memory 같은 전문 에이전트 내부 helper도 `그거`, `이거`, `위 내용`, `그 메모`, `이 파일` 같은 후속 지시 표현을 같은 의미로 인식해야 한다고 명시되어 있다.
  - `WebSearchAgent.linked_search_text()`는 독자적인 marker 목록을 사용하고 있어 `위 내용 검색해줘`, `그 메모 검색해줘`처럼 라우터가 후속 참조로 볼 수 있는 표현을 실행 단계에서 놓칠 수 있었다.
  - `linked_search_text()`가 `routing_markers.py`의 `GENERIC_REFERENCE_MARKERS`, `explicit_source_reference_markers()`, `RECENT_CONVERSATION_SOURCE_MARKERS`, `RECENT_STORED_ITEM_REFERENCE_MARKERS`를 함께 사용하도록 바꿨다.
  - 이 변경으로 라우터가 linked state를 검증해 넘겼는데 웹검색 에이전트가 현재 사용자 문장을 새 검색어로 오해하는 위험을 줄였다.
  - `test_web_search_agent_uses_resolved_query_from_linked_non_search_state`에 `위 내용 검색해줘`, `그 메모 검색해줘`를 추가했고, artifact title fallback 테스트도 `이 파일 검색해줘`로 후속 파일 참조를 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_web_search_agent.py -k "linked_non_search_state or linked_artifact_title"`(`7 passed, 23 deselected`)와 `python3 -m ruff check assistant_bot/agents/web_search.py tests/test_web_search_agent.py`를 통과했다.
  - 관련 라우팅 검증으로 `python3 -m pytest -q tests/test_context_routing_matrix.py -k "pronoun_web_search or web_result_reference or site_reference or compact_link_reference"`(`6 passed, 180 deselected`)와 `python3 -m pytest -q tests/test_router_agent.py -k "web_search or source_reference or web_result"`(`2 passed, 153 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1291 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 할 일 삭제 확인 슬롯 복원 보강

- 작업 이름: linked task 삭제 요청이 즉시 삭제되지 않고 확인 대기와 승인 실행까지 같은 task id를 유지하도록 보강
- 진행상황: 완료
- 진행내용:
  - ruff 검증 중 `task_ids_from_execution_context`, `_task_deletion_slots`가 정의되지 않은 상태로 사용되는 것을 확인했다.
  - 이 경로는 사용자가 `방금 할 일 삭제해줘`처럼 linked state 기반으로 할 일 삭제를 요청할 때, 실행 컨텍스트의 `task_id/task_ids`를 삭제 확인 대기로 옮겨야 하는 핵심 경로다.
  - `_task_deletion_slots()`를 추가해 삭제 확인/취소/실행 결과에 `task_ids`와 단일 `task_id`를 함께 남기도록 했다.
  - `task_ids_from_execution_context()`를 추가해 route resolved slots, linked state slots, linked task artifacts의 `id/task_id/task_ids`를 모두 읽어 삭제 대상 ID를 복원하도록 했다.
  - `test_assistant_bot_confirms_linked_task_delete_before_deleting`를 추가해 linked task 삭제 요청이 바로 삭제되지 않고 `confirm_required`가 되며, 승인 후에만 삭제되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_assistant_bot_confirms_linked_task_delete_before_deleting tests/test_bot_helpers.py::test_assistant_bot_dispatches_linked_reminder_delete_to_reminder_agent`(`2 passed`)와 `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1291 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - linked subject fallback 라벨 제거

- 작업 이름: linked state subject만 남은 경우에도 `메모 8`, `할 일 3`, `알림 5` 같은 내부 라벨이 새 본문에 섞이지 않도록 정리
- 진행상황: 완료
- 진행내용:
  - 전문 에이전트는 linked state에서 `resolved_slots`나 artifact title을 우선 사용하지만, 이 단서가 없으면 subject/summary를 fallback 본문으로 사용한다.
  - 기존 fallback은 `메모 8 병원 예약`, `할 일 3 병원 예약`, `알림 5 물 마시기` 같은 subject 라벨을 그대로 사용할 수 있어, 사용자가 `그거 기억해줘`, `그 메모 할 일로 추가해줘`라고 했을 때 시스템식 라벨이 새 기억/할 일/알림 본문에 섞일 위험이 있었다.
  - `normalize_linked_subject_text()`를 추가해 메모, 기억, 문서, 파일, 할 일, 작업, 태스크, 알림, 리마인더 라벨과 ID 접두사를 제거하도록 했다.
  - `normalize_context_task_title()`가 linked subject 정리를 먼저 적용하도록 했고, `MemoryAgent.linked_memory_text_from_context()`와 `ReminderAgent.normalize_context_reminder_text()`도 같은 정리 함수를 사용하도록 맞췄다.
  - 기존 `test_task_agent_creates_task_from_linked_memory_reference`와 `test_memory_agent_remembers_linked_task_text`를 더 엄격하게 바꿔, resolved slot/artifact title 없이 subject fallback만 있어도 `병원 예약`만 저장되는지 고정했다.
  - `test_reminder_agent_normalizes_linked_reminder_subject_as_new_reminder_text`로 알림 subject fallback의 라벨 제거도 함께 검증했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_memory_store.py -k "linked_memory_reference or remembers_linked_task or normalizes_linked_reminder_subject"`(`4 passed, 116 deselected`)와 `python3 -m ruff check assistant_bot/agents/common.py assistant_bot/agents/memory.py assistant_bot/agents/task.py assistant_bot/agents/reminder.py tests/test_memory_store.py`를 통과했다.
  - 관련 라우팅 검증으로 `python3 -m pytest -q tests/test_context_routing_matrix.py -k "reference_create or pronoun_create_reminder"`(`12 passed, 174 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1293 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 중첩 private route 문자열 제거 보강

- 작업 이름: 응답 작성 프롬프트에 중첩 `route_context/resolved_slots/validation_context` 찌꺼기가 남지 않도록 sanitizer 보강
- 진행상황: 완료
- 진행내용:
  - `sanitize_private_route_text()`와 실행 컨텍스트 sanitizer는 기존에 정규식 한 번으로 `resolved_slots={...}` 같은 내부 metadata 문자열을 제거했다.
  - 하지만 값이 `resolved_slots={'task_id': 3, 'pending_resolved_slots': {'document_id': 7}}`처럼 중첩 dict를 포함하면 바깥 구조 전체를 지우지 못하고 `}| done`, `'after': {` 같은 찌꺼기가 응답 프롬프트에 남을 수 있었다.
  - `remove_private_route_assignments()`와 balanced value scanner를 추가해 private route/debug assignment 값을 `{}`/`[]` 중첩과 따옴표 escape를 고려해 끝까지 제거하도록 했다.
  - `response_composer.sanitize_private_route_text()`와 `models.sanitize_private_route_segment_text()`, `sanitize_private_route_value_text()`가 같은 scanner를 사용하도록 맞췄다.
  - `test_response_private_route_text_filter_removes_nested_private_assignment_values`를 추가해 `route_context`, `resolved_slots`, `pending_resolved_slots`, `validation_context`, `current_message_context`가 중첩 문자열 안에서도 제거되고 사용자 설명만 남는지 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_response_composer.py -k "nested_private_assignment or private_route_text_filter or private_route_keys_are_filtered"`(`5 passed, 42 deselected`)와 `python3 -m ruff check assistant_bot/models.py assistant_bot/response_composer.py tests/test_response_composer.py`를 통과했다.
  - 관련 범위 검증으로 `python3 -m pytest -q tests/test_response_composer.py tests/test_context_builder.py -k "private_route or response_safe or internal_action or route_reason"`(`32 passed, 95 deselected`)와 `python3 -m pytest -q tests/test_agent_registry.py -k "private_route or response_composer or diagnostic"`(`6 passed, 77 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1294 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - Discord 알림 삭제 확인 대기 적용

- 작업 이름: 실제 봇 경로에서 알림 삭제도 버튼/확인 후 실행하도록 오삭제 방지 보강
- 진행상황: 완료
- 진행내용:
  - `ReminderAgent.delete_reminders()`는 에이전트 단독 호출 시 즉시 삭제를 수행하고 있었고, Discord 봇 통합 경로에서도 `그 알림 삭제해줘`가 라우터 연결 결과에 따라 바로 실행될 수 있었다.
  - 메모/문서 삭제는 이미 확인 대기를 거치므로, 라우터가 후속 맥락을 잘못 연결했을 때 더 위험한 삭제류 행동의 정책이 서로 달라지는 문제가 있었다.
  - `PendingReminderDeletion` 모델과 `pending_reminder_deletions` 테이블, `PendingReminderDeletionStore`를 추가해 알림 삭제 확인 대기를 저장하도록 했다.
  - Discord `AssistantBot` 경로에서 `manage_reminder` 삭제 요청은 바로 에이전트에 dispatch하지 않고, 삭제 대상 알림 ID를 확인한 뒤 `confirm_required` 결과와 승인/거부 버튼을 노출하도록 바꿨다.
  - 승인 버튼 또는 `응` 계열 확인 답변이 들어오면 pending 알림 삭제를 실제 실행하고, 거부/취소 답변이면 삭제하지 않고 대기를 종료한다.
  - stale pending 정리에도 `pending_reminder_deletions`를 포함해, 사용자가 새 요청을 시작하면 오래된 알림 삭제 대기가 뒤늦게 승인되지 않도록 했다.
  - 내부 실행 컨텍스트에 `pending_intent=manage_reminder`, `reminder_id/reminder_ids`, `canceled_target=reminder_deletion`을 남겨 응답 작성자와 내부 행동 로그가 삭제 확인 흐름을 참고할 수 있게 했다.
  - `test_assistant_bot_dispatches_linked_reminder_delete_to_reminder_agent`를 갱신해 Discord 봇 경로에서는 알림 삭제 요청이 먼저 `confirm_required`가 되고, 승인 후에만 실제 삭제되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_dispatches_linked_reminder_delete_to_reminder_agent tests/test_memory_store.py::test_reminder_agent_deletes_reminder_by_id tests/test_memory_store.py::test_reminder_agent_deletes_linked_reminder_without_id_in_text -q`(`3 passed`), `python3 -m pytest tests/test_bot_helpers.py -q`(`193 passed`), `python3 -m pytest tests/test_memory_store.py -q`(`120 passed`)와 `python3 -m ruff check assistant_bot/bot.py assistant_bot/models.py assistant_bot/stores.py assistant_bot/database.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-08 - Discord 할 일 삭제 확인 대기 적용

- 작업 이름: 실제 봇 경로에서 할 일 삭제도 버튼/확인 후 실행하도록 오삭제 방지 보강
- 진행상황: 완료
- 진행내용:
  - `TaskAgent`는 단독 호출 시 `할 일 3 삭제해줘`, `방금 추가한 할 일 삭제해줘` 같은 요청을 즉시 삭제한다.
  - Discord 봇 통합 경로에서도 라우터가 후속 맥락을 잘못 연결하면 특정 할 일이 바로 삭제될 수 있어, 메모/문서/알림 삭제와 확인 정책이 달랐다.
  - `PendingTaskDeletion` 모델과 `pending_task_deletions` 테이블, `PendingTaskDeletionStore`를 추가해 할 일 삭제 확인 대기를 저장하도록 했다.
  - Discord `AssistantBot` 경로에서 `manage_task` 삭제 요청은 바로 task agent에 dispatch하지 않고, 삭제 대상 할 일 ID를 확인한 뒤 `confirm_required` 결과와 승인/거부 버튼을 노출하도록 바꿨다.
  - 승인 버튼 또는 `응` 계열 확인 답변이 들어오면 pending 할 일 삭제를 실제 실행하고, 거부/취소 답변이면 삭제하지 않고 대기를 종료한다.
  - stale pending 정리에도 `pending_task_deletions`를 포함해, 사용자가 새 요청을 시작하면 오래된 할 일 삭제 대기가 뒤늦게 승인되지 않도록 했다.
  - 내부 실행 컨텍스트에 `pending_intent=manage_task`, `task_id/task_ids`, `canceled_target=task_deletion`을 남겨 응답 작성자와 내부 행동 로그가 삭제 확인 흐름을 참고할 수 있게 했다.
  - `test_assistant_bot_confirms_linked_task_delete_before_deleting`을 추가해 Discord 봇 경로에서는 할 일 삭제 요청이 먼저 `confirm_required`가 되고, 승인 후에만 실제 삭제되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_confirms_linked_task_delete_before_deleting tests/test_bot_helpers.py::test_assistant_bot_dispatches_linked_reminder_delete_to_reminder_agent tests/test_memory_store.py::test_task_agent_delete_prefers_linked_task_context_over_latest_item tests/test_memory_store.py::test_task_agent_delete_uses_linked_task_artifact_id_when_slots_missing -q`(`4 passed`), `python3 -m pytest tests/test_bot_helpers.py -q`(`194 passed`), `python3 -m pytest tests/test_memory_store.py -q`(`120 passed`)와 `python3 -m ruff check assistant_bot/bot.py assistant_bot/models.py assistant_bot/stores.py assistant_bot/database.py tests/test_bot_helpers.py`를 통과했다.

## 2026-06-08 - 할 일/알림 삭제 확인 버튼 계약 고정

- 작업 이름: Discord 삭제 확인 대기가 실제 승인/거부 버튼으로 이어지는지 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - 할 일/알림 삭제를 `confirm_required`로 바꾸더라도 `confirmation_action_for()`가 pending store를 인식하지 못하면 사용자는 버튼 없이 채팅으로만 승인해야 한다.
  - 삭제류 위험 행동은 사용자가 실수 없이 승인/거부할 수 있어야 하므로, pending task/reminder deletion 결과에 `ConfirmationView`가 붙는지 테스트로 고정했다.
  - `test_assistant_bot_attaches_buttons_to_task_and_reminder_delete_confirmation`을 추가해 `manage_task` 삭제 확인은 `delete_tasks`, `manage_reminder` 삭제 확인은 `delete_reminders` action으로 연결되고 버튼 라벨이 `승인/거부`인지 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_attaches_buttons_to_task_and_reminder_delete_confirmation tests/test_bot_helpers.py::test_assistant_bot_confirms_linked_task_delete_before_deleting tests/test_bot_helpers.py::test_assistant_bot_dispatches_linked_reminder_delete_to_reminder_agent -q`(`4 passed`)와 `python3 -m ruff check tests/test_bot_helpers.py assistant_bot/bot.py`를 통과했다.

## 2026-06-08 - 삭제 확인 대기 운영 가시성 보강

- 작업 이름: 할 일/알림 삭제 확인 대기가 DB 상태, 사용자 스냅샷, cleanup에 빠지지 않도록 반영
- 진행상황: 완료
- 진행내용:
  - Discord 봇 경로에는 `pending_reminder_deletions`, `pending_task_deletions`가 추가됐지만, CLI 운영 상태와 사용자 스냅샷은 여전히 `pending_memory_deletions`만 표시하고 있었다.
  - 이 상태에서는 실제로 알림/할 일 삭제 확인 대기가 남아 있어도 운영자가 스냅샷에서 놓칠 수 있고, 해결된 대기 row가 cleanup 대상에서 빠져 오래된 내부 상태가 남을 수 있었다.
  - `CORE_TABLE_NAMES`에 `pending_reminder_deletions`, `pending_task_deletions`를 추가해 DB 초기화 점검에서 핵심 테이블 누락을 발견할 수 있게 했다.
  - `collect_database_stats()`와 `format_database_stats()`에 삭제 확인 대기 알림/할 일 카운트를 추가했다.
  - `build_user_snapshot()`과 `format_user_snapshot()`에 사용자별 알림/할 일 삭제 확인 대기 수를 포함해, 운영자가 현재 사용자에게 걸린 대기 작업을 한 줄에서 확인할 수 있게 했다.
  - `cleanup_database()`의 pending 정리 대상에 해결된 기억/알림/할 일 삭제 확인 대기 row를 포함했다. 열린 대기 작업은 삭제하지 않고 resolved 된 오래된 row만 정리한다.
  - `test_build_user_snapshot_combines_memory_tasks_and_conversation_locations`, `test_collect_and_format_database_stats`, `test_cleanup_database_previews_and_deletes_old_operational_rows`를 보강해 새 pending 테이블이 상태/스냅샷/정리 계약에서 빠지지 않도록 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py -q`(`85 passed`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1294 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 내부 행동 기록 최신성 병합 보강

- 작업 이름: 같은 상태 후보에 여러 내부 행동 기록이 섞였을 때 최신 실행 결과가 라우터 단서로 우선되도록 수정
- 진행상황: 완료
- 진행내용:
  - 라우터의 `internal_action_context_by_linked_state()`는 사용자에게 보이지 않는 내부 행동 기록을 읽어 `linked_state_id`별 슬롯, 대상 힌트, 가능한 액션을 보강한다.
  - 기존 구조는 같은 `linked_state_id`의 여러 로그가 들어오면 컨텍스트 라인 순서에 따라 병합되어, 오래된 내부 기록의 `task_id`, 대상명, 액션이 최신 기록보다 먼저 남을 수 있었다.
  - 내부 행동 기록을 먼저 레코드로 모은 뒤 `(recency, created_at, line_index)` 기준 최신순으로 정렬해 병합하도록 바꿨다.
  - 슬롯은 최신 레코드의 값을 우선 유지하고, `target_hints`와 `actions`도 최신 항목부터 중복 없이 이어붙이도록 했다.
  - 이로써 “방금 처리한 대상”을 사용자가 `그거`, `다시해봐`, `방금 것`처럼 이어 말했을 때 오래된 내부 로그가 대상 후보를 빼앗는 위험을 줄였다.
  - `test_router_internal_action_context_prefers_latest_record_for_same_state`를 추가해 같은 state에 오래된 할 일 3 기록과 최신 할 일 8 기록이 함께 있을 때 최신 ID, 제목, 힌트, 액션이 우선되는지 고정했다.
  - 전체 검증 중 드러난 맥락 진단 취약점도 함께 보강했다. `병원 예약 할 일에 내일 오전까지라고 추가해줘`에서 `내일 오전까지라고`는 대상명이 아니라 수정 내용이므로, 명시 대상 추출이 `병원 예약`만 남기도록 정리했다.
  - 따옴표로 감싼 파일명 `"분기 보고서 v2.pdf"`를 읽을 때 내부의 `v2.pdf`를 별도 파일로 중복 추출하지 않도록 파일명 추출 로직도 수정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_router_agent.py -k internal_action_context`(`1 passed, 155 deselected`), `python3 -m pytest -q tests/test_context_builder.py::test_build_current_message_context_marks_named_target_mutation_for_candidate_match tests/test_context_builder.py::test_build_current_message_context_exposes_explicit_ids_and_file_targets tests/test_route_validation.py::test_validate_route_context_link_keeps_existing_named_task_mutation`(`3 passed`), `python3 -m pytest -q tests/test_route_validation.py::test_explicit_text_target_extractors_ignore_pronoun_follow_ups`(`1 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1296 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - route validation 결과의 다음 턴 슬롯 복원 보강

- 작업 이름: 라우팅 검증으로 보정된 결과도 내부 행동 기록에서 parse 가능한 `route_context`로 남기기
- 진행상황: 완료
- 진행내용:
  - 실행 결과 로그는 `route=`를 남겨 다음 턴 라우터가 `linked_state_id`와 `resolved_slots`를 복원할 수 있었지만, `route_validation` 로그는 주로 `validation_context=`만 남겼다.
  - 이 구조는 자동 연결 차단/확인 필요 이벤트를 판단하기에는 충분했지만, 사용자가 확인 질문에 승인해서 라우팅이 복원된 직후의 보정 결과를 다음 턴 후보 슬롯으로 다시 쓰기에는 약했다.
  - `route_validation_summary()`가 after 라우팅 결과를 `route_context={'context_link': ..., 'linked_state_id': ..., 'resolved_slots': ...}` 형태로 함께 기록하도록 바꿨다.
  - `resolved_slots`는 `route_safe_values()`를 거쳐 `pending_original_text` 같은 원문성 슬롯을 실행 대상 슬롯으로 과하게 보존하지 않도록 했다.
  - `context_builder.internal_action_route_context()`가 기존 `route=`뿐 아니라 `route_context=` 세그먼트와 세미콜론 구분 validation 로그 원문도 읽도록 확장했다.
  - 이로써 route validation 로그가 “무엇을 막거나 확인했는지”뿐 아니라 “검증 후 실제로 어떤 state와 슬롯으로 이어졌는지”도 다음 턴 내부 컨텍스트에 구조화해서 제공한다.
  - `test_route_validation_summary_preserves_pending_cross_location_retry_context`를 보강해 validation summary만으로 `internal_action_context_by_linked_state()`가 `state_id=21`, `location=원주` 슬롯을 복원하는지 고정했다.
  - `test_build_router_context_pending_approval_validation_log_is_not_guidance`를 보강해 실제 router context에 `route_context`가 출력되고, 그 컨텍스트를 라우터 파서가 다시 읽는지 확인했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_bot_helpers.py::test_route_validation_summary_preserves_pending_cross_location_retry_context tests/test_context_builder.py::test_build_router_context_pending_approval_validation_log_is_not_guidance`(`2 passed`), `python3 -m pytest -q tests/test_context_builder.py -k "internal_action or route_validation or execution_context"`(`17 passed, 64 deselected`), `python3 -m pytest -q tests/test_bot_helpers.py -k "internal_action_result or route_validation_summary"`(`21 passed, 175 deselected`), `python3 -m pytest -q tests/test_router_agent.py -k "internal_action or validation"`(`41 passed, 115 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1296 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - route validation action/catalog 계약 보강

- 작업 이름: 새 에이전트 추가 시 라우팅 검증 action과 agent catalog 후속 action 선언이 어긋나지 않도록 계약 테스트 추가
- 진행상황: 완료
- 진행내용:
  - 라우팅 검증 계층의 `INTENT_ACTIONS`는 사용자 표현을 해석하고 linked state와 호환되는 후속 행동인지 판단하는 기준이다.
  - `agent_catalog.json`의 `available_actions.*`는 실제 turn state 후보에 남아 라우터가 다음 턴에서 참고하는 후속 행동 목록이다.
  - 기존 테스트는 catalog가 검증 계층이 모르는 action을 선언하지 않는지만 확인했다. 반대로 검증 계층이 허용하는 action이 catalog에 빠져 있는지는 확인하지 않았다.
  - `VALIDATION_ONLY_INTENT_ACTIONS`를 추가해 `continue`, `modify`, `rename`, 삭제/복구 직후 전환 action처럼 사용자 표현 해석 또는 검증 전용으로 쓰지만 state 후보 action으로 노출하지 않아도 되는 action을 명시했다.
  - `test_route_validation_actions_are_declared_in_agent_catalog`를 추가해 `INTENT_ACTIONS` 중 검증 전용으로 명시되지 않은 action은 반드시 catalog의 `available_actions.*`에 선언되도록 했다.
  - `test_validation_only_actions_are_known_intent_actions`를 추가해 검증 전용 action 목록 자체가 `INTENT_ACTIONS`에 없는 값을 품지 않도록 고정했다.
  - 이 계약은 앞으로 새 에이전트/새 후속 행동을 추가할 때 라우터 프롬프트, route validation, turn state 후보 action이 서로 벌어지는 문제를 조기에 잡기 위한 안전장치다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_agent_registry.py::test_route_validation_actions_are_declared_in_agent_catalog tests/test_agent_registry.py::test_validation_only_actions_are_known_intent_actions tests/test_agent_registry.py::test_agent_catalog_action_outputs_match_route_validation_actions`(`3 passed`)와 `python3 -m ruff check assistant_bot/route_validation.py tests/test_agent_registry.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1300 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 최종 응답 내부 메타데이터 재필터링

- 작업 이름: 응답 작성 모델 출력과 보조 item artifact 계약의 마지막 안전망 보강
- 진행상황: 완료
- 진행내용:
  - 응답 작성 프롬프트와 입력 컨텍스트는 내부 행동 기록을 사용자에게 보이지 않도록 정리하지만, 최종 응답 작성 모델이 실수로 `context_link=...`, `linked_state_id=...`, `agent=task:result`, `model=...`, `route_validation` 같은 내부 표지를 답변에 섞어 내보내면 기존 코드는 그 출력 자체를 그대로 반환했다.
  - `sanitize_model_answer_text()`를 추가해 모델이 생성한 최종 답변에도 한 번 더 private route assignment 제거와 내부 agent/model/log 표지 제거를 적용하도록 했다.
  - 이 필터는 실행 결과를 바꾸지 않고 표현 단계의 내부 메타데이터만 제거한다. 제거 후 내용이 비면 기존 안전 fallback 문장으로 대체한다.
  - `test_response_composer_sanitizes_private_metadata_from_model_output`을 추가해 모델 출력에 내부 route/debug 표지가 섞여도 사용자 답변에는 자연스러운 결과 문장만 남는지 고정했다.
  - 전체 검증 중 `manage_task` 결과의 `items`에 보조 문서 항목이 섞인 경우 catalog 계약 검증이 이를 주 도메인 artifact처럼 막는 문제가 드러났다.
  - `OperationResult.artifacts`는 에이전트가 공식적으로 남기는 후속 대상이므로 catalog와 반드시 맞춰 검증하되, `items`에서 추론되는 artifact는 해당 intent의 주 도메인일 때만 catalog 선언을 강제하도록 분리했다.
  - 이로써 할 일 결과 안의 보조 문서 항목처럼 다음 턴 맥락에는 유용하지만 해당 에이전트의 공식 artifact 출력은 아닌 값을 내부 turn state에 보존할 수 있게 했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_response_composer.py::test_response_composer_sanitizes_private_metadata_from_model_output tests/test_response_composer.py::test_response_composer_uses_model_output tests/test_response_composer.py::test_response_composer_sanitizes_private_route_metadata_from_failed_fallback`(`3 passed`), `python3 -m pytest -q tests/test_response_composer.py -k "private_route or sanitize or metadata or model_output or for_response"`(`25 passed, 23 deselected`), `python3 -m pytest -q tests/test_agent_registry.py -k "private_route or internal_route or response"`(`12 passed, 75 deselected`), `python3 -m pytest -q tests/test_bot_helpers.py -k "private_route or sanitized_turn_state"`(`6 passed, 191 deselected`)를 통과했다.
  - 보조 artifact 계약 검증으로 `python3 -m pytest -q tests/test_agent_registry.py::test_registry_dispatch_rejects_item_artifacts_not_declared_in_catalog tests/test_bot_helpers.py::test_assistant_bot_record_turn_state_merges_explicit_and_inferred_artifacts`(`2 passed`)와 `python3 -m ruff check assistant_bot/agent_registry.py tests/test_agent_registry.py tests/test_bot_helpers.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1302 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 현재 메시지 대상 추출 진단 보강

- 작업 이름: 라우터가 새 요청/후속 요청을 구분할 때 현재 메시지의 실제 대상과 행동을 더 선명하게 보도록 보강
- 진행상황: 완료
- 진행내용:
  - 기존 `현재 메시지 맥락 진단`은 `follow_up_reference`, `explicit_new_target` 같은 boolean 신호 위주라, 라우터가 실제로 어떤 ID, 파일명, 지역, URL, 검색어, 이름 대상, 요청 행동을 기준으로 판단해야 하는지 덜 선명했다.
  - `build_current_message_context()`에 `extracted_targets`를 추가해 `requested_actions`, `memory/document/task/reminder ids`, `weather_locations`, `document_filenames`, `urls`, `search_queries`, `named_targets`를 구조화된 문자열로 노출하도록 했다.
  - `explicit_document_filenames_from_text()`가 `문서 7 다시 분석하고 contract.pdf` 같은 자연문에서 앞 문장 전체를 파일명으로 오인하지 않도록, 따옴표로 감싼 파일명과 공백 없는 bare filename을 분리해 추출하도록 고쳤다.
  - `explicit_named_targets_from_text()`가 `병원 예약 할 일에 내일 오전까지라고 추가해줘`처럼 기존 항목에 내용을 덧붙이는 문장에서 대상명을 `병원 예약`으로 분리하도록 보강했다.
  - `parse_state_candidates()`가 내부 행동 기록의 `target_hints`만 있는 경우 이를 상태 후보 target으로 병합하지 않도록 수정했다. 내부 기록 hint만으로 후보가 오염되면 새 파일명 요청이 이전 상태에 잘못 연결될 수 있기 때문이다.
  - `test_build_current_message_context_*`, `test_explicit_text_target_extractors_ignore_pronoun_follow_ups`, `test_router_fallback_does_not_merge_internal_hints_without_executable_slots`를 통해 대상 추출과 내부 hint 병합 조건을 회귀 테스트로 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py -q`(`433 passed`)와 `python3 -m ruff check assistant_bot/context_builder.py assistant_bot/agents/router.py assistant_bot/route_validation.py tests/test_context_builder.py tests/test_router_agent.py tests/test_route_validation.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1296 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - CLI pending 확인 정리 정책 일치

- 작업 이름: 로컬 CLI 경로에서도 알림/할 일 삭제 확인 대기가 새 요청에 맞춰 정리되도록 Discord 정책과 일치
- 진행상황: 완료
- 진행내용:
  - Discord 봇 경로의 `expire_stale_pending_confirmations()`는 새 요청이 들어오면 첨부, 기억 삭제, 알림 삭제, 할 일 삭제, 웹검색 확인 대기를 함께 정리한다.
  - 로컬 CLI 경로는 아직 첨부, 기억 삭제, 웹검색 확인만 정리하고 있어, 같은 대화 상태를 디버깅할 때 알림/할 일 삭제 확인 대기가 남는 편차가 있었다.
  - `assistant_bot/cli.py`에서 `PendingReminderDeletionStore`, `PendingTaskDeletionStore`를 초기화하고 stale pending 정리 함수에 전달하도록 했다.
  - CLI `expire_stale_pending_confirmations()`의 반환값을 `(첨부, 기억 삭제, 알림 삭제, 할 일 삭제, 웹검색 확인)` 5개 카운트로 확장하고, 내부 로그에도 `pending_reminder_deletions`, `pending_task_deletions`를 남기도록 했다.
  - `tests/test_cli.py`의 새 요청/비작업 감탄 테스트를 보강해 새 요청에서는 다섯 종류의 일반 확인 대기가 모두 resolve 되고, `잠깐` 같은 비작업 반응에는 모두 유지되는지 고정했다.
  - 전체 검증 중 `route_validation` 로그의 `route_context`가 `; validation_context=` 앞에 있을 때 내부 행동 파서가 읽지 못하는 회귀가 드러나, `parse_internal_action_route_value()`가 세미콜론 구분자도 종료자로 인식하도록 보정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py -q`(`85 passed`), 실패 회귀 범위인 `python3 -m pytest tests/test_bot_helpers.py::test_route_validation_summary_preserves_pending_cross_location_retry_context tests/test_context_builder.py::test_build_router_context_pending_approval_validation_log_is_not_guidance tests/test_cli.py -q`(`87 passed`)와 관련 ruff 검증을 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1296 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 복수형 artifact kind 추론 보강

- 작업 이름: 에이전트 결과 item이 복수형 대상 키만 제공해도 다음 턴 후보가 명확한 artifact kind를 갖도록 수정
- 진행상황: 완료
- 진행내용:
  - 새 에이전트가 `items`에 `document_ids`, `task_ids`, `reminder_ids`, `urls` 같은 복수형 대상 키만 넣고 `kind`를 빼먹으면, turn_state artifact가 대상 종류 없이 저장될 수 있었다.
  - 이 경우 라우터의 다음 턴 후보에는 ID/URL 자체는 남아도 `memory/document/task/reminder/web_result` 종류가 약해져, “그 문서”, “그 할 일” 같은 후속 요청을 구분하는 단서가 덜 선명해진다.
  - `infer_turn_artifact_from_item()`에서 단일 ID 키뿐 아니라 `memory_ids`, `document_ids`, `task_ids`, `reminder_ids` 복수형 키를 보고 artifact `kind`를 자동 추론하도록 했다.
  - `url` 또는 `urls`만 있는 item은 `web_result` artifact로 추론하도록 해 웹 검색/URL 후보도 같은 방식으로 다음 턴 단서가 남게 했다.
  - `test_item_artifact_kind_is_inferred_from_plural_target_keys`를 추가해 kind가 없는 item에서도 `memory/document/task/reminder/web_result`가 복원되고, 내부 행동 context용 ID/URL 값도 보존되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py tests/test_context_builder.py -q`(`165 passed`)와 `python3 -m ruff check assistant_bot/bot.py tests/test_agent_registry.py tests/test_context_builder.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1297 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - artifact 기반 subject 추론 보강

- 작업 이름: 에이전트가 subject를 비워도 artifact 제목과 ID로 다음 턴 대표명을 복원하도록 수정
- 진행상황: 완료
- 진행내용:
  - turn_state의 `subject`는 라우터가 “그거”, “방금 것”, “그 문서” 같은 후속 요청을 사용자에게 확인하거나 자동 연결할 때 사람이 읽는 대표 대상명으로 쓰인다.
  - 기존 `infer_turn_subject()`는 facts의 단일 ID나 일부 intent별 값 중심이라, 새 에이전트가 subject를 직접 넣지 않고 item/artifact만 반환하면 `할 일 3 병원 예약` 같은 구체적 대표명을 만들지 못할 수 있었다.
  - `infer_turn_subject_from_artifacts()`와 `turn_state_artifact_subject()`를 추가해 `memory/document/task/reminder` artifact의 ID와 제목을 조합하고, `url/web_result` artifact는 제목 또는 URL을 subject로 쓰도록 했다.
  - artifact title 추출은 기존 `append_artifact_title()`과 같은 필드 목록을 쓰는 `first_artifact_title_value()`를 추가해 `title`, `filename`, `task_title`, `reminder_text`, `url_title` 등을 일관되게 읽도록 했다.
  - `test_infer_turn_subject_uses_artifact_title_when_subject_is_missing`를 추가해 subject가 비어 있어도 `할 일 3 병원 예약`, `문서 7 contract.pdf`, `OpenAI`를 복원하는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_infer_turn_subject_uses_artifact_title_when_subject_is_missing tests/test_bot_helpers.py::test_infer_turn_slots_keeps_plural_web_targets_for_context_linking tests/test_agent_registry.py::test_item_artifact_kind_is_inferred_from_plural_target_keys -q`(`3 passed`)와 `python3 -m ruff check assistant_bot/bot.py tests/test_bot_helpers.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1300 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - items 기반 artifact 계약 검증 보강

- 작업 이름: `OperationResult.items`에서 자동 추론되는 artifact도 `agent_catalog` 계약을 통과하도록 강화
- 진행상황: 완료
- 진행내용:
  - 런타임은 `OperationResult.items`에서 `task_ids`, `document_ids`, `urls` 등을 artifact로 추론해 다음 턴 후보와 내부 행동 context에 사용한다.
  - 기존 registry 계약 검증은 `result.artifacts`만 검사하고 items에서 추론되는 artifact는 검사하지 않아, catalog에 `artifacts.*`를 선언하지 않은 에이전트도 후속 target을 context에 남길 수 있었다.
  - `validate_operation_result_contract()`가 `infer_contract_artifacts_from_items()` 결과도 검사하도록 확장했다.
  - `artifact_contract_errors()`로 명시 artifacts와 items 기반 artifacts 검사를 공통화했고, 오류 메시지에 `artifacts #n` 또는 `items #n` 출처를 남기도록 했다.
  - `test_registry_dispatch_rejects_item_artifacts_not_declared_in_catalog`를 추가해 `manage_task`가 `artifacts.task_ids`를 선언하지 않고 task item을 반환하면 registry dispatch 단계에서 실패하도록 고정했다.
  - 기존 turn_state merge 테스트는 task와 document 결과를 함께 허용하는 `daily_briefing` intent로 조정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py -q`(`87 passed`), 관련 focused 테스트(`2 passed`), 관련 ruff 검증을 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1302 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 라우터 맥락 연결 판단 요약 추가

- 작업 이름: 현재 메시지와 최근 작업 후보를 비교한 공통 연결 판단 요약을 라우터 컨텍스트에 추가
- 진행상황: 완료
- 진행내용:
  - 기존 라우터 컨텍스트는 최근 작업 후보와 각 후보의 `link_guidance`를 제공했지만, 현재 메시지와 후보를 비교한 결론은 LLM이 직접 추론해야 했다.
  - `build_context_link_decision_summary()`를 추가해 현재 메시지의 후속 표현, 새 대상 신호, 추출 target을 후보별 `target_hints`와 비교한다.
  - 후보별로 `target_match`, `target_conflict`, `recommended`를 명시해 `do_not_link_new_request`, `can_link_if_action_matches`, `can_link_if_action_supported`, `ask_user_before_execute` 같은 공통 판단 결과를 라우터에 전달한다.
  - 새 지역/파일명/ID/URL/검색어 등 후보와 맞지 않는 새 대상이 있으면 이전 작업으로 연결하지 않도록 `do_not_link_new_request`를 표시한다.
  - 다른 대화 위치의 후보가 후속 요청처럼 보이면 바로 실행하지 않고 `ask_user_before_execute`로 확인 질문을 요구한다.
  - `test_context_link_decision_summary_blocks_new_target_from_previous_state`, `test_context_link_decision_summary_allows_current_location_clear_follow_up`, `test_context_link_decision_summary_requires_confirmation_for_cross_location_follow_up`를 추가했다.
  - `build_router_context` 출력에 `맥락 연결 판단 요약` 섹션이 포함되는지도 기존 최근 작업 상태 테스트에 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py -q`(`84 passed`), 라우팅 관련 묶음 `python3 -m pytest tests/test_context_builder.py tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`622 passed`), 관련 ruff 검증을 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1305 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-08 - 실행/응답 컨텍스트에 라우터 연결 판단 요약 보존

- 작업 이름: 라우터가 본 맥락 연결 판단 요약을 에이전트 실행과 응답 작성 단계까지 전달
- 진행상황: 완료
- 진행내용:
  - 직전 작업에서 `build_router_context()`에는 `맥락 연결 판단 요약`이 추가되었지만, `ExecutionContext`에는 같은 정보가 보존되지 않았다.
  - 이 상태에서는 라우터가 “새 요청으로 처리” 또는 “다른 위치 작업은 확인 필요”라고 판단해도, 실제 에이전트와 응답 작성 단계는 해당 판단 단서를 직접 참고하지 못할 수 있었다.
  - `ExecutionContext`에 `context_link_decision_summary` 필드를 추가하고 `for_router()`, `for_agent()`, `for_response()`에 포함했다.
  - `build_execution_context()`에서도 `build_context_link_decision_summary()`를 호출해 라우터와 동일한 후보 비교 요약을 실행 컨텍스트에 저장하도록 했다.
  - 새 필드는 기존 positional `ExecutionContext(...)` 호출과 충돌하지 않도록 dataclass 끝에 배치했다. 중간에 추가했을 때 라우팅 매트릭스 일부가 깨지는 회귀를 확인했고, 필드 순서를 끝으로 옮겨 복구했다.
  - `test_build_execution_context_preserves_context_link_decision_summary_for_agents_and_response`를 추가해 “서울 날씨 다시해봐”가 이전 “원주 날씨” 후보와 충돌한다는 `recommended=do_not_link_new_request` 단서가 에이전트/응답 컨텍스트까지 남는지 고정했다.
  - 직접 검증으로 focused 테스트(`2 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_response_composer.py -q`(`133 passed`), 봇/라우터/응답 묶음 `python3 -m pytest tests/test_bot_helpers.py tests/test_router_agent.py tests/test_context_builder.py tests/test_response_composer.py -q`(`492 passed`)를 통과했다.
  - 필드 순서 보정 후 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`(`186 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1312 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-08 - 연결 판단 요약을 내부 행동 결과 로그에 기록

- 작업 이름: 에이전트 결과 로그에도 라우터 연결 판단 요약을 남겨 다음 턴 컨텍스트에서 참고하도록 보강
- 진행상황: 완료
- 진행내용:
  - 기존 내부 행동 결과 로그는 `context_link=continue/retry`처럼 실제 연결된 상태가 있을 때 route 정보를 잘 남겼지만, “이전 후보와 연결하지 않기로 한 판단”은 결과 로그에 남지 않았다.
  - `internal_action_result_reason()`이 `ExecutionContext.context_link_decision_summary`를 압축해 `context_decision={...}` 세그먼트로 기록하도록 했다.
  - `context_link=none`이어도 `candidate_state_id`, `target_conflict`, `recommended=do_not_link_new_request` 같은 핵심 판단은 다음 턴 내부 행동 로그에 남는다.
  - `build_internal_action_context()`가 `context_decision` 세그먼트를 파싱하고 내부 행동 기록 라인에 포함하도록 했다.
  - `ExecutionContext.for_agent()`의 내부 행동 안전 컨텍스트가 `context_decision`을 `연결 판단`으로 보여주도록 해, 에이전트가 이전 후보를 왜 이어받지 않았는지 참고할 수 있게 했다.
  - 값이 없는 로그에는 `context_decision=-`를 붙이지 않도록 해 기존 `route_validation` 로그의 `agent=route_validation` 식별자가 잘리지 않는 회귀를 방지했다.
  - `test_internal_action_result_reason_records_context_decision_even_without_link`와 `test_build_router_context_surfaces_internal_context_decision_logs`를 추가했다.
  - 직접 검증으로 focused 테스트(`2 passed`), 내부 행동/라우터 관련 묶음 `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_router_agent.py -q`(`447 passed`)를 통과했다.
  - 전체 검증 중 CLI route validation 로그 trimming 회귀를 발견해 `context_decision`을 값이 있을 때만 출력하도록 보정했고, 실패 케이스 포함 focused 테스트(`3 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1316 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-08 - 라우터 선택 로그에 현재 메시지 진단과 연결 판단 요약 추가

- 작업 이름: 라우터의 모델/휴리스틱 선택 로그도 다음 턴에서 구조적으로 참고 가능하게 보강
- 진행상황: 완료
- 진행내용:
  - 기존 라우터 로그는 `intent`, `context_link`, `linked_state_id`, `reason` 중심이라, 라우터가 어떤 현재 메시지 진단과 후보 비교 요약을 보고 판단했는지 다음 턴에서 복원하기 어려웠다.
  - `route_log_reason()`에 `conversation_context` 인자를 추가하고, 라우터의 모델 라우팅 로그와 휴리스틱 fallback 로그에 전달하도록 했다.
  - `현재 메시지 맥락 진단` 섹션을 `current_message_context=...`로 압축해 라우터 로그에 남긴다.
  - `맥락 연결 판단 요약` 섹션은 `route_log_context_decision()`으로 파싱해 `context_decision={current_message, candidates}` 형태로 저장한다.
  - 후보별로 `state_id`, `location`, `intent`, `subject`, `target_match`, `target_conflict`, `recommended`, `reason`만 짧게 남겨 다음 턴 내부 행동 기록에서 참고할 수 있게 했다.
  - 내부 로그 세그먼트 구분자인 ` | `가 값 안에 들어가면 파싱이 깨질 수 있어 `sanitize_route_log_segment_value()`로 `/` 형태로 치환했다.
  - `test_route_log_reason_records_current_message_and_context_decision`를 추가해 “서울 날씨 다시해봐”가 기존 “원주 날씨” 후보와 충돌해 `do_not_link_new_request`로 기록되는지 고정했다.
  - 직접 검증으로 focused 테스트(`2 passed`), 라우터/컨텍스트/검증 묶음 `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py tests/test_route_validation.py -q`(`441 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1318 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-08 - context_decision을 내부 연결 판단 지침으로 변환

- 작업 이름: 내부 행동 로그의 `context_decision`을 라우터/에이전트가 바로 참고할 수 있는 guidance로 변환
- 진행상황: 완료
- 진행내용:
  - `context_decision`은 후보별 `recommended` 값을 담지만, 기존에는 단순 데이터로만 노출되어 라우터가 hard/soft signal로 해석해야 했다.
  - `internal_action_context_decision_guidance()`를 추가해 `do_not_link_new_request`, `ask_user_before_execute`, `can_link_if_action_matches`, `can_link_if_action_supported`를 자연어 지침으로 변환한다.
  - 현재 위치 로그는 `현재 위치 hard signal`로 표시해 같은 새 대상 신호가 있을 때 이전 후보 재연결을 막도록 했다.
  - 다른 위치 로그는 `다른 위치 soft signal, 현재 위치 작업 차단 금지`로 표시해 다른 채팅 위치의 판단이 현재 위치 작업을 과하게 막지 않게 했다.
  - `build_internal_action_context()`가 값이 있을 때만 `context_decision_guidance=...`를 추가하도록 했다.
  - `ExecutionContext.for_agent()`의 내부 행동 안전 컨텍스트가 이를 `연결 판단 주의`로 보여주도록 했다.
  - `test_build_router_context_surfaces_internal_context_decision_logs`를 확장하고 `test_internal_context_decision_guidance_marks_cross_location_as_soft_signal`를 추가했다.
  - 직접 검증으로 focused 테스트(`2 passed`), 컨텍스트/응답/라우터 묶음 `python3 -m pytest tests/test_context_builder.py tests/test_response_composer.py tests/test_router_agent.py -q`(`292 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1321 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-08 - 메모 대기 상태의 새 요청 가로채기 방지 보강

- 작업 이름: 메모 대기 상태에서도 명확한 새 요청은 라우터 판단을 참고해 원래 에이전트로 넘기도록 수정
- 진행상황: 완료
- 진행내용:
  - `다음 메시지를 메모로 받을게요` 상태가 남아 있을 때, 사용자가 실제 메모 본문이 아니라 `기능 알려줘`, `도와줄 수 있는거 뭐야`, `브리핑 해줘` 같은 새 요청을 보내면 메모 본문으로 저장될 위험이 있었다.
  - 공통 라우팅 휴리스틱의 도움말/기능 문의 표현과 브리핑 요청 표현을 보강했다. 다만 `요약해줘` 같은 문서 후속 요청이 오늘 브리핑으로 오인되지 않도록 `요약`은 `오늘/일일` 맥락이 있을 때만 브리핑으로 분류하게 좁혔다.
  - `AssistantBot.handle_pending_memory_capture()`에 선택적 라우터 보조 판단을 추가했다. 휴리스틱이 새 요청을 못 잡더라도 라우터가 높은 확신으로 `help`, `status`, `current_time`, `weather`, `web_search`, `web_url`, `daily_briefing`, `analyze_document`, `list_memory`, `reset_context` 같은 새 유틸리티/조회 요청을 판단하면 메모 대기를 resolve 하고 원래 라우팅 흐름으로 넘긴다.
  - 반대로 `내일 오전에 병원 예약`처럼 할 일처럼 보일 수 있지만 사용자가 메모 대기 상태에서 보낸 자연어 본문은 라우터만으로 `manage_task`에 넘기지 않도록 했다. 명시적인 새 작업 요청이 아니라면 `다음 한 메시지를 메모로 저장`이라는 사용자 의도를 유지하기 위함이다.
  - `pending_memory_capture_should_yield_to_route()`를 추가해 라우터 보조 판단의 허용 intent, confidence, context_link 조건을 별도로 테스트할 수 있게 했다.
  - `tests/test_bot_helpers.py`에 휴리스틱 보강 케이스와 라우터 보조 판단 통합 테스트를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py -q`(`203 passed`), `python3 -m pytest tests/test_router_heuristics.py tests/test_router_agent.py tests/test_cli.py -q`(`292 passed`)를 통과했다.
  - 브리핑 감지 범위 조정 후 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`186 passed`)로 문서 요약 후속 라우팅 회귀를 확인했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1312 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 자동 맥락 연결 확신도 방어선 보강

- 작업 이름: 라우터의 낮은 확신도 자동 연결은 바로 실행하지 않고 사용자 확인으로 전환
- 진행상황: 완료
- 진행내용:
  - 라우터가 `context_link=continue/retry/modify`와 `linked_state_id`를 반환하면, 상태와 대상이 호환되는 경우 `link_confidence`가 낮아도 자동 실행될 수 있는 위험을 확인했다.
  - `MIN_AUTO_CONTEXT_LINK_CONFIDENCE=0.75` 기준을 추가하고, 일반 자동 연결의 `link_confidence`가 기준보다 낮으면 `context_link=clarify`로 낮춰 사용자 확인을 먼저 받도록 했다.
  - 사용자가 이미 pending 확인 질문에 `응`, `이어 해줘`처럼 승인한 경우에는 별도 확인이 중복되지 않도록 `route_with_pending_context_values()`에서 pending 상태의 `linked_state_id`를 복원할 때 `link_confidence`도 기준 이상으로 보강했다.
  - `test_validate_route_context_link_clarifies_low_confidence_auto_link`로 낮은 확신도 연결이 자동 실행되지 않고 확인 질문으로 전환되는지 고정했다.
  - `test_assistant_bot_clarifies_low_confidence_context_link_before_dispatch`로 실제 봇 처리에서 낮은 확신도 연결이 에이전트 dispatch 전에 멈추고 `needs_input` 결과를 만드는지 확인했다.
  - 전체 검증 중 CLI 내부 행동 컨텍스트에서 긴 실행 결과 로그가 `route_validation` 로그를 밀어내는 경우를 발견했다. 현재 위치의 `route_validation` 우선순위를 실행 결과보다 높여, 자동 연결 차단/확인 필요 신호가 컨텍스트에 남도록 보강했다.
  - 직접 검증으로 `python3 -m pytest tests/test_route_validation.py tests/test_bot_helpers.py -q`(`402 passed`), `python3 -m pytest tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_context_builder.py -q`(`428 passed`), CLI 회귀 테스트와 context builder 묶음(`87 passed`)을 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1316 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - pending 확인 승인 prefix 오인 방지

- 작업 이름: `네이버`, `그래도`, `그래프` 같은 일반 단어를 pending 승인 prefix로 오인하지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - pending 맥락 확인 응답 판별에서 `응`, `네`, `그래`, `좋아` 같은 승인 prefix를 compact 문자열 앞부분만 보고 판단하고 있었다.
  - 그 결과 `네이버 검색해줘`, `그래도 서울 날씨 알려줘`, `그래프 보여줘`, `좋아하지 않아`, `응?` 같은 일반 발화도 `has_context_link_approval_prefix()` 단계에서는 승인 prefix가 있는 것처럼 보일 수 있었다.
  - 대부분의 실행 경로에서는 추가 조건으로 차단되지만, pending 확인 매칭의 안정성을 위해 prefix 뒤 suffix가 흔한 단어 충돌 패턴이면 승인 prefix로 인정하지 않도록 `context_link_approval_prefix_suffix_from_compact()`를 추가했다.
  - filler 제거와 approval suffix 추출도 같은 helper를 사용하도록 통일해, `잠깐만 응 계속해줘`, `음 좋아 이어서 해줘`, `응 완료해줘` 같은 실제 승인 표현은 유지하고 단어 충돌만 차단했다.
  - `test_context_link_approval_prefix_ignores_common_word_prefix_collisions`를 추가해 일반 단어 prefix 충돌이 pending 승인으로 소비되지 않도록 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_route_validation.py -q`(`198 passed`)와 관련 ruff 검증을 통과했다.
  - pending 승인 흐름 회귀 확인으로 `python3 -m pytest tests/test_bot_helpers.py tests/test_context_routing_matrix.py tests/test_cli.py -q`(`476 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1318 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 카탈로그 target slot 보존 계약 강화

- 작업 이름: 에이전트가 선언한 후속 대상 슬롯이 facts/resolved_slots에서 turn state로 보존되는지 계약 테스트 추가
- 진행상황: 완료
- 진행내용:
  - 새 에이전트가 `agent_catalog.json`에 `slots.memory_id`, `slots.task_title`, `slots.location`, `slots.url` 같은 target slot을 선언해도, 실제 결과 저장 경로가 그 값을 turn state 슬롯으로 보존하지 않으면 다음 턴 라우터가 대상을 놓칠 수 있다.
  - 기존 테스트는 target slot이 내부 행동 context, target hints, route slot merge에 포함되는지 확인했지만, `turn_state_slots_from_result()`가 `facts`와 `resolved_slots` 값을 실제 후보 슬롯으로 보존하는지는 카탈로그 전체 기준으로 고정하지 않았다.
  - `test_agent_catalog_target_slot_outputs_are_preserved_from_facts_to_turn_state_slots`를 추가해 에이전트가 target slot을 `facts`에 넣으면 turn state 슬롯으로 살아남는지 확인했다.
  - `test_agent_catalog_target_slot_outputs_are_preserved_from_resolved_slots_to_turn_state_slots`를 추가해 route validation, pending 승인, 버튼 승인 흐름처럼 `resolved_slots`에 target slot이 들어오는 경우도 후보 슬롯으로 복원되는지 확인했다.
  - 이 계약은 `memory/document/task/reminder` ID, 제목/본문, 날씨 location, 웹 query/url/title, 파일명/첨부명 계열을 모두 대상으로 한다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py -q`(`89 passed`)와 관련 ruff 검증을 통과했다.
  - 라우팅 후보/컨텍스트 회귀 확인으로 `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`(`478 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1321 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - context_decision guidance의 fallback 행동 반영

- 작업 이름: 내부 연결 판단 지침을 라우터 휴리스틱 fallback의 후보 재사용 방어선으로 연결
- 진행상황: 완료
- 진행내용:
  - `context_decision_guidance`가 컨텍스트에 노출되는 것에서 끝나지 않고, 모델 실패/불확실 상황의 휴리스틱 fallback에서도 실제 자동 연결 판단에 반영되도록 했다.
  - `internal_context_decision_blocked_state_ids()`와 관련 최신 이벤트 파서를 추가해 현재 위치 내부 로그의 `재연결 금지. 현재 위치 hard signal`을 state 후보 차단 신호로 읽는다.
  - 다른 위치 로그의 `다른 위치 soft signal, 현재 위치 작업 차단 금지`는 현재 위치 후보 차단에 쓰지 않도록 분리했다.
  - 이후 같은 state가 성공적인 `route_context`로 다시 연결되면 이전 차단 신호를 clear 처리해, 오래된 판단이 정상 후속 요청을 영구적으로 막지 않게 했다.
  - 휴리스틱 fallback의 암시적 후보 재사용 필터에 `validation_removed_state_ids`와 `context_decision_blocked_state_ids`를 함께 적용했다. 사용자가 명확히 같은 대상을 다시 말한 경우는 기존 명시 매칭 규칙을 유지한다.
  - `test_router_parses_current_location_context_decision_blocked_state_ids`, `test_router_ignores_cross_location_context_decision_soft_signal`, `test_router_context_decision_block_blocks_implicit_candidate_reuse`, `test_router_context_decision_block_is_cleared_by_later_successful_route_context`를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py -q`(`161 passed`)와 `python3 -m pytest tests/test_context_builder.py tests/test_response_composer.py tests/test_router_agent.py -q`(`297 passed`)를 통과했다.

## 2026-06-08 - context_decision 내부 메타데이터 비공개 계약 보강

- 작업 이름: 라우터 연결 판단 메타데이터가 사용자 응답/turn state로 새지 않도록 private key 등록
- 진행상황: 완료
- 진행내용:
  - `context_decision`, `context_decision_guidance`는 라우터와 내부 행동 로그가 참고해야 하는 비공개 판단 메타데이터이므로 응답 생성과 turn state 대상 슬롯에서 제외되어야 한다.
  - `RESPONSE_PRIVATE_ROUTE_SLOT_KEYS`와 private prefix에 `context_decision` 계열을 추가했다.
  - `INTERNAL_ACTION_LOG_ONLY_CONTEXT_KEYS`에도 같은 키를 추가해, 향후 OperationResult facts에 들어와도 일반 실행 대상 슬롯이나 사용자 응답용 facts로 오해되지 않게 했다.
  - `test_response_private_route_keys_include_current_message_diagnostics`와 `test_internal_log_only_context_keys_do_not_become_turn_state_or_fact_slots`를 보강했다.
  - 직접 검증으로 focused 테스트(`3 passed`)와 `python3 -m pytest tests/test_agent_registry.py tests/test_response_composer.py -q`(`137 passed`)를 통과했다.

## 2026-06-08 - 분리 신호가 있는 새 요청의 후보명 충돌 방지

- 작업 이름: `별개로/상관없이/말고`가 있는 명시 새 요청을 이전 후보 확인 질문으로 바꾸지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - `그거랑 별개로 병원 예약 검색해줘`처럼 이전 작업 제목(`병원 예약`)과 새 검색어가 겹치면 fallback이 `web_search` base route를 버리고 “어느 작업을 이어갈까요?” 확인 질문으로 바꾸는 회귀를 확인했다.
  - `base_intent_is_explicit_new_request()`를 추가해 base route가 `web_search`, `web_url`, `weather`, `current_time`, `daily_briefing`, `help`, `status`, `reset_context` 같은 명시 새 요청이면 분리 신호를 우선 존중하게 했다.
  - 기존에는 분리 신호가 있어도 후보 제목이 명시 매칭되면 base를 보존하지 않았는데, 이제 실행 가능한 새 요청 intent에서는 후보명 충돌보다 현재 사용자 요청을 우선한다.
  - 직접 검증으로 실패 케이스 focused 테스트(`1 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`187 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_context_routing_matrix.py -q`(`546 passed`)를 통과했다.

## 2026-06-08 - 전문 에이전트 resolved_slots 사용 계약 보강

- 작업 이름: 각 전문 에이전트가 자기 intent 카탈로그에 선언한 슬롯만 `ExecutionContext.resolved_slots`에서 읽도록 테스트 고정
- 진행상황: 완료
- 진행내용:
  - 기존에는 `execution_context.resolved_slots`를 동적 키로 읽지 못하게 하고, 전체 안전 슬롯 집합 안에서만 읽도록 검사했다.
  - 한 단계 더 좁혀서 Memory/Document/Task/Reminder/Weather/Web 전문 에이전트가 자신이 처리하는 intent의 `state_outputs`에 선언된 `slots.*`만 읽는지 확인하는 계약 테스트를 추가했다.
  - 이 테스트는 새 에이전트나 새 슬롯이 추가될 때 카탈로그 선언 없이 다른 도메인 슬롯을 읽어 맥락을 잘못 이어가는 회귀를 막기 위한 것이다.
  - 직접 검증으로 focused 테스트(`2 passed`)와 `python3 -m pytest tests/test_agent_registry.py -q`(`90 passed`)를 통과했다.
  - 전체 검증 중 일시적인 테스트 순서성 실패가 한 번 있었으나 동일 실패 케이스 단독 재현은 되지 않았고, 전체 재실행에서 `python3 -m pytest -q`(`1329 passed`)를 통과했다.
  - 최종 검증으로 `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 내부 행동 로그 요청 원문 기록 계약 보강

- 작업 이름: Discord/CLI 진입 경로의 내부 행동 결과 로그가 항상 사용자 요청 텍스트를 함께 기록하도록 AST 계약 추가
- 진행상황: 완료
- 진행내용:
  - 내부 행동 결과 로그에는 `request=...`가 들어가야 다음 턴 컨텍스트에서 “어떤 사용자 요청 때문에 실행된 내부 행동인지”를 구분할 수 있다.
  - 일반 메시지, 버튼 처리, CLI 실행 경로가 `record_internal_action_result(..., user_text=...)`를 호출하는지 AST 기반으로 검사하는 `test_runtime_internal_action_result_logs_include_user_text`를 추가했다.
  - 이 계약은 새 버튼 핸들러나 로컬 실행 경로가 추가될 때 내부 행동 결과만 남고 원 요청이 빠지는 회귀를 막기 위한 것이다.
  - 직접 검증으로 focused 테스트(`1 passed`)와 `python3 -m pytest tests/test_agent_registry.py -q`(`91 passed`)를 통과했다.

## 2026-06-08 - 긴 내부 행동 로그의 요청 원문 보존 보강

- 작업 이름: 내부 행동 컨텍스트 trimming 시 `request`, `route_context`, `target_hints`가 함께 남도록 개선
- 진행상황: 완료
- 진행내용:
  - 내부 행동 결과 로그의 `request=...`는 다음 턴에서 “어떤 사용자 요청으로 이 행동이 실행됐는지”를 판단하는 중요한 단서다.
  - 기존에는 긴 내부 행동 로그가 잘릴 때 `route_context`와 `target_hints`는 tail 쪽에서 살아남을 수 있었지만, `request`는 `reason=...` 내부에만 있어 잘릴 위험이 있었다.
  - `build_internal_action_context()`가 raw reason의 `request` 세그먼트를 별도 `request=...` 필드로 노출하도록 했다.
  - `internal_action_identity_prefix()`가 긴 줄을 head/tail로 자를 때 `request=`도 identity 필드로 보존하도록 했다.
  - `test_build_router_context_keeps_internal_action_request_when_trimmed`를 추가해 긴 로그에서도 요청 원문, route context, target hints가 같이 남는지 고정했다.
  - 직접 검증으로 focused 테스트(`3 passed`)와 `python3 -m pytest tests/test_context_builder.py tests/test_router_agent.py -q`(`250 passed`)를 통과했다.

## 2026-06-08 - request 원문 노출 범위 분리

- 작업 이름: 내부 행동 `request`는 라우터 컨텍스트에 보존하되 에이전트/응답 safe context에는 노출하지 않도록 정리
- 진행상황: 완료
- 진행내용:
  - `request=...`가 별도 내부 행동 필드로 생겼으므로 `reason=` 안에 중복으로 포함하지 않도록 `internal_action_compact_reason()`에서 request를 제외했다.
  - `request`를 응답용 private route key로 등록해 OperationResult facts/slots나 내부 행동 safe context에서 사용자 응답 모델 입력으로 새지 않게 했다.
  - `test_execution_context_filters_private_route_metadata_from_internal_action_segments`에 `request=그거 수정해줘` 필드를 추가해 에이전트/응답 safe context에서 요청 원문이 숨겨지는지 고정했다.
  - 직접 검증으로 focused 테스트(`4 passed`)와 `python3 -m pytest tests/test_context_builder.py tests/test_response_composer.py tests/test_bot_helpers.py -q`(`343 passed`)를 통과했다.

## 2026-06-08 - route validation 현재 메시지 진단 보존 보강

- 작업 이름: validation 로그의 현재 메시지 진단과 요청 원문이 내부 행동 컨텍스트에서 잘리지 않도록 개선
- 진행상황: 완료
- 진행내용:
  - route validation summary에서 `reason`이 길면 `current_message_context`가 `validation_context` 앞에서 잘릴 수 있는 구조를 확인했다.
  - `route_validation_summary()`의 필드 순서를 `route_context -> current_message_context -> reason -> validation_context`로 바꿔, 현재 메시지 진단이 긴 reason보다 먼저 보존되도록 했다.
  - `build_internal_action_context()`가 validation 로그의 `current_message_context=...`를 별도 필드로 노출하도록 했다.
  - route validation 로그에는 별도 `request=...`가 없으므로, `current_message_context`의 `text=` 값을 내부 행동 컨텍스트의 `request=...`로 복원하게 했다.
  - 긴 validation 로그에서도 `current_message_context`와 `decision_hint`가 남는지 CLI 테스트를 보강했고, router context에 `request=아 다시해봐`가 노출되는지 context builder 테스트를 보강했다.
  - 직접 검증으로 focused 테스트(`2 passed`)와 `python3 -m pytest tests/test_cli.py tests/test_context_builder.py tests/test_bot_helpers.py tests/test_router_agent.py -q`(`541 passed`)를 통과했다.

## 2026-06-08 - 긴 내부 행동 기록의 핵심 맥락 보존 보강

- 작업 이름: 라우터 컨텍스트 문자 제한 상황에서도 내부 행동 기록의 정체성과 재연결 슬롯을 함께 유지
- 진행상황: 완료
- 진행내용:
  - 기존 내부 행동 기록은 필수 로그를 행 선택 단계에서는 보존하더라도, 최종 문자 제한에서 긴 한 줄이 뒤쪽만 남도록 잘릴 수 있었다.
  - 그 결과 `route_context`의 `linked_state_id`는 남지만 `agent`, `intent`, `location_priority`가 사라져 라우터가 현재 위치 작업인지, 어떤 에이전트 결과인지 판단하기 어려운 위험을 확인했다.
  - 긴 내부 행동 로그 한 줄을 부분 보존할 때 앞쪽의 `agent`, `intent`, `location_priority`, `executable_actions`, `retryable`와 뒤쪽의 `route_context`를 함께 남기는 head+tail 트리밍을 추가했다.
  - 줄 단위 `link_guidance`는 헤더 정책과 중복되는 긴 문장을 짧게 줄여, 실제 판단에 필요한 target/action/route 슬롯이 문자 제한에서 밀리지 않도록 했다.
  - 내부 행동 `route_context`의 `resolved_slots`는 다음 턴 라우팅에 필요한 안전 슬롯만 남기도록 압축했다. 예를 들어 `task_id`, `document_id`, `location`, `query`, `filename` 계열은 유지하고 `pending_original_text`, 긴 `new_text` 계열은 제외한다.
  - `test_build_router_context_keeps_internal_action_identity_when_long_line_is_trimmed`를 추가해 긴 실행 결과에서도 정체성 필드와 `linked_state_id/resolved_slots`가 함께 유지되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py -q`(`88 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py -q`(`359 passed`), `python3 -m pytest tests/test_bot_helpers.py -q`(`205 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1326 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 새 요청 분리 표현의 라우팅 우선순위 보강

- 작업 이름: `말고/별개로/따로` 뒤의 명시 새 요청이 이전 작업 후보 확인으로 빼앗기지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - `그거랑 별개로 병원 예약 검색해줘`처럼 대명사 후속 표현과 새 요청 분리 표현이 함께 있을 때, 기존 fallback이 여러 작업 후보 사이의 확인 질문으로 멈추는 문제를 재현했다.
  - 명시적 `검색해줘`가 있어도 내부 검색 문맥 판정이 먼저 실행되어 `web_search` 점수가 사라질 수 있어, 명시 웹검색 표현은 저장 기억/메모/할 일 검색 요청이 아닌 경우 웹검색으로 우선 판정하도록 수정했다.
  - 라우터 fallback에서 `replacement_effective_user_text()`를 사용해 `말고/별개로/따로` 뒤의 실제 요청문이 분리되었는지 확인하고, base intent가 이미 `web_search`처럼 구체적이면 여러 후보 확인 질문으로 덮어쓰지 않도록 했다.
  - route validation에서도 분리 표현 뒤의 effective text를 기준으로 새 요청 여부를 판단하도록 보강해, 앞부분의 `그거` 때문에 새 요청 차단 로직이 무력화되지 않게 했다.
  - `test_context_routing_matrix`에 `separate_search_with_matching_task_subject_stays_new_web_search` 케이스를 추가해, 이전 할 일 제목과 검색어가 겹쳐도 새 웹검색으로 유지되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`(`187 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_router_heuristics.py -q`(`410 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py -q`(`293 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1327 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 내부 행동 결과 로그의 사용자 요청 단서 보강

- 작업 이름: 에이전트 실행 결과 로그에 실제 사용자 요청 텍스트를 안전하게 기록
- 진행상황: 완료
- 진행내용:
  - 내부 행동 결과 로그는 `status`, `summary`, `subject`, `slots`, `actions`를 잘 남기고 있었지만, 결과가 어떤 사용자 요청에서 발생했는지 항상 명확하지 않았다.
  - 다음 턴 라우터가 “방금 사용자가 어떤 요청을 했고 어떤 결과가 생겼는지”를 더 안정적으로 참고할 수 있도록 내부 result log에 `request=` 필드를 추가했다.
  - 일반 Discord 메시지, 확인 버튼, URL 후보 선택 버튼, 작업 후보 선택 버튼, CLI 경로에서 실제 사용자 요청 텍스트를 `record_internal_action_result()`에 전달하도록 연결했다.
  - `request=` 값은 기존 내부 로그 sanitizer를 거쳐 `|`, `route_context=`, `slots=` 같은 구조 오염 토큰이 라우터 파서에 영향을 주지 않도록 압축/정리된다.
  - `internal_action_compact_reason()`이 `request` 필드를 보존하도록 수정해, 라우터 컨텍스트에서 결과 요약과 함께 사용자의 직전 요청 단서도 확인할 수 있게 했다.
  - `test_record_internal_action_result_logs_operation_result_for_future_context`를 보강해 `request=그거 완료했어`가 로그와 라우터 컨텍스트에 남는지 확인했다.
  - `test_record_internal_action_result_sanitizes_user_request_for_future_context`를 추가해 사용자 요청 안의 구조 오염 문자열이 내부 컨텍스트 파싱을 깨지 않는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py -q`(`294 passed`)와 `python3 -m pytest tests/test_cli.py tests/test_router_agent.py -q`(`246 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1329 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 최근 답변 source 요청의 이전 항목 오연결 방지

- 작업 이름: `방금 답변`, `네가 답변한 거`, `네가 말한 ...`을 최근 저장 항목이 아닌 최근 대화 원문 source로 분리
- 진행상황: 완료
- 진행내용:
  - `방금 답변 메모해줘`, `네가 방금 답변한 거 메모해줘` 같은 요청이 최근 저장 메모 후보에 연결되어 `memory_id` 기반 후속 작업처럼 처리되는 문제를 확인했다.
  - 사용자의 의도는 이전 저장 항목을 수정/조회하는 것이 아니라 봇의 최근 답변 또는 최근 대화 내용을 새 메모/할 일/알림의 재료로 쓰는 것이므로, 최근 작업 상태 후보와 분리해야 한다.
  - `RECENT_CONVERSATION_SOURCE_MARKERS`에 `방금답변`, `네가답변`, `네가방금답변한`, `네가말한`, `네가한말` 계열을 추가했다.
  - 이 marker는 route validation과 router fallback 양쪽에서 공통으로 사용되므로, 최근 답변 source 요청이 이전 저장 항목 후보에 자동 연결되지 않는다.
  - `test_context_routing_matrix`에 `recent_answer_memory_request_does_not_link_previous_memory`, `assistant_answer_memory_request_does_not_link_previous_memory`, `assistant_said_topic_memory_request_does_not_link_matching_previous_memory`, `recent_answer_task_request_does_not_link_previous_task`를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`(`191 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_router_heuristics.py -q`(`410 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py -q`(`294 passed`), `python3 -m pytest tests/test_agent_registry.py -q`(`91 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1334 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 후보 확인 이후 새 요청 전환 회귀 보강

- 작업 이름: 후보 선택 확인 질문 뒤의 번호/제외 표현이 새 요청을 빼앗지 않는지 테스트 고정
- 진행상황: 완료
- 진행내용:
  - 후보 선택 확인 질문 뒤에 사용자가 `두 번째 말고 서울 날씨 알려줘`, `두 번째 말고 OpenAI 검색해줘`처럼 번호 표현과 새 요청을 함께 말할 수 있는 흐름을 점검했다.
  - 현재 라우터는 이 경우 pending 후보 선택으로 소비하지 않고 `weather` 또는 `web_search` 새 요청으로 유지하고 있음을 확인했다.
  - 이 동작은 사용자가 확인 질문 이후 마음을 바꿔 새 요청으로 전환하는 실제 Discord 대화에서 중요하므로, `test_context_routing_matrix`에 `pending_candidate_ordinal_rejection_new_weather_request_does_not_select_candidate`, `pending_candidate_ordinal_rejection_new_web_search_does_not_select_candidate`를 추가했다.
  - 두 케이스 모두 `context_link=none`, `linked_state_id=None`으로 고정해, 향후 후보 선택 로직이 넓어지더라도 새 요청을 이전 후보에 잘못 연결하지 않도록 했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q`(`193 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py tests/test_router_heuristics.py -q`(`410 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py -q`(`295 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1337 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 모델 라우팅 오판의 명시 새 요청 보정

- 작업 이름: 모델이 기존 작업 intent를 과신해도 현재 메시지의 명시 새 요청 intent를 복원
- 진행상황: 완료
- 진행내용:
  - 모델 라우터가 `그거 말고 OpenAI 검색해줘`를 기존 `manage_task` 후속 요청처럼 강하게 판단하면, route validation이 링크는 제거해도 intent가 잘못 남을 수 있는 위험을 확인했다.
  - `model_route_needs_context_refinement()`에 명시적 heuristic intent 충돌 감지를 추가해, 현재 메시지에서 고신뢰로 잡히는 `web_search`, `weather`, `current_time` 같은 새 요청이 모델 intent와 충돌하면 context-aware fallback을 다시 적용하도록 했다.
  - fallback 결과가 heuristic intent와 일치하고 충분히 신뢰도가 높은 경우에만 `refined_route_corrects_explicit_model_mismatch()`로 모델 응답을 보정한다. 따라서 모델 판단을 무조건 덮어쓰지 않고, 현재 메시지 자체가 강한 근거를 줄 때만 실행된다.
  - route validation에서는 명시 검색어가 있는 요청을 `검색어 mismatch`보다 먼저 `새 웹검색 요청`으로 분류하도록 정리했다. 내부 행동 로그와 다음 턴 컨텍스트가 “이전 검색 실패”가 아니라 “새 검색 전환”으로 읽히게 하기 위한 변경이다.
  - `test_router_refines_wrong_model_task_intent_for_separate_web_search_request`를 추가해 모델이 잘못된 `manage_task/continue`를 반환해도 최종 라우팅이 `web_search/context_link=none`으로 복원되는지 고정했다.
  - `test_validate_route_context_link_clears_wrong_task_link_for_separate_web_search`를 추가해 검증기 단에서도 잘못된 기존 작업 링크가 실행 전 제거되는지 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py -q`(`361 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`193 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1339 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 명시 새 요청 보정 회귀 범위 확장

- 작업 이름: 웹검색 외 명시 요청에서도 모델 intent 오판을 복원하는 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - 이전 보정이 `web_search` 사례에는 테스트로 고정되어 있었지만, 목표는 앞으로 추가될 에이전트까지 포함해 모델 오판을 일반적으로 줄이는 것이다.
  - `model_route_needs_context_refinement()`와 `refined_route_corrects_explicit_model_mismatch()`가 이미 `base_intent_is_explicit_new_request()` 기반으로 동작해, 웹검색뿐 아니라 날씨/현재시간/도움말 같은 명시 요청에도 적용 가능한 구조임을 확인했다.
  - 이 일반성을 회귀 테스트로 고정하기 위해 `test_router_refines_wrong_model_task_intent_for_explicit_new_requests`를 추가했다.
  - 테스트는 모델이 `manage_task/context_link=continue`를 고신뢰로 잘못 반환하더라도 `그거 말고 서울 날씨 알려줘`, `그거 말고 지금 몇시야?`, `그거 말고 네가 뭘 할 수 있는지 알려줘`가 각각 `weather`, `current_time`, `help`로 복원되는지 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_refines_wrong_model_task_intent_for_explicit_new_requests -q`(`3 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`358 passed`), `python3 -m pytest tests/test_route_validation.py tests/test_bot_helpers.py -q`(`405 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1342 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 문서/비전 분석 요청의 이전 작업 오연결 방지 회귀 고정

- 작업 이름: 첨부 문서 분석과 비전 잔여 용량 조회가 기존 작업 intent에 빼앗기지 않도록 테스트 보강
- 진행상황: 완료
- 진행내용:
  - 사용자가 파일을 첨부하고 `그거 말고 이 문서 요약해줘`처럼 말하는 경우, 실제 대상은 이전 작업이 아니라 현재 첨부 파일이다.
  - 모델 라우터가 이 상황을 기존 `manage_task/context_link=continue`로 잘못 판단해도, heuristic+context fallback이 `analyze_document/context_link=none`으로 복원하는지 확인했다.
  - 첨부가 없는 경우에도 `이미지 분석 남은 용량 알려줘`는 이전 작업 후속 요청이 아니라 비전 분석 정책/쿼터 조회 요청이므로 `analyze_document`로 유지되어야 한다.
  - `test_router_refines_wrong_model_task_intent_for_attached_document_analysis_request`와 `test_router_refines_wrong_model_task_intent_for_vision_quota_request`를 추가해 두 흐름을 회귀 테스트로 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_refines_wrong_model_task_intent_for_attached_document_analysis_request tests/test_router_agent.py::test_router_refines_wrong_model_task_intent_for_vision_quota_request -q`(`2 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py -q`(`360 passed`), `python3 -m pytest tests/test_document_analysis_agent.py tests/test_bot_helpers.py -q`(`218 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1345 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 같은 intent 새 항목 생성의 잘못된 링크 제거

- 작업 이름: 모델이 같은 에이전트 intent에 기존 항목 링크를 붙여도 순수 새 항목 생성은 새 요청으로 정리
- 진행상황: 완료
- 진행내용:
  - 기존 보정은 모델 intent가 완전히 틀린 경우를 잘 복원했지만, `새 할 일 추가`, `새 메모 추가`, `새 알림 추가`처럼 intent 자체는 맞고 `context_link=continue`만 잘못 붙은 경우에는 라우터가 모델 응답을 그대로 통과시킬 수 있었다.
  - 실행 전 route validation이 최종 안전망으로 링크를 제거하더라도, 라우터의 내부 로그와 다음 턴 컨텍스트에는 처음부터 더 정확한 판단이 남는 편이 좋다.
  - `model_route_links_explicit_new_item_creation()`을 추가해 모델 응답이 이전 항목 링크를 가진 상태에서 현재 메시지가 순수 새 항목 생성이면 refinement를 실행하도록 했다.
  - `refined_route_clears_explicit_new_item_link()`를 추가해 fallback이 같은 intent를 유지하되 `context_link=none`으로 정리한 결과를 유효한 보정으로 채택하도록 했다.
  - `그 작업을 새 메모로 저장해줘`처럼 기존 작업을 source로 삼아 새 항목을 만드는 요청은 연결이 맞으므로 `has_explicit_source_conversion_request()`인 경우 새 항목 링크 제거 대상에서 제외했다.
  - `test_router_clears_wrong_model_link_for_same_intent_new_item_creation`을 추가해 새 할 일/새 메모/새 알림 생성에서 잘못된 기존 항목 링크가 라우터 단계에서 제거되는지 고정했다.
  - `test_router_keeps_source_conversion_link_even_with_new_item_phrase`를 추가해 source conversion 요청은 `새 메모` 표현이 있어도 기존 작업 링크를 유지하는지 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_clears_wrong_model_link_for_same_intent_new_item_creation tests/test_router_agent.py::test_router_keeps_source_conversion_link_even_with_new_item_phrase -q`(`4 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`193 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py -q`(`370 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_router_heuristics.py -q`(`258 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1350 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 같은 intent 새 대상 요청의 잘못된 링크 제거

- 작업 이름: 모델이 intent는 맞췄지만 이전 대상 링크를 유지한 경우 라우터 단계에서 새 대상으로 분리
- 진행상황: 완료
- 진행내용:
  - 기존 보정은 모델 intent가 틀린 경우와 새 항목 생성 링크 오판을 처리했지만, `weather`, `web_search`, `web_url`처럼 intent는 맞고 대상만 새로 바뀐 경우에는 모델의 `context_link=continue`가 그대로 통과될 수 있었다.
  - 예를 들어 최근 상태가 `원주 날씨`인데 사용자가 `서울 날씨 알려줘`라고 하면 intent는 둘 다 `weather`지만, 대상은 새 지역이므로 이전 상태에 연결하면 안 된다.
  - `model_route_links_explicit_new_target()`을 추가해 모델 응답이 이전 작업 링크를 가진 상태에서 현재 메시지에 새 지역/검색어/URL/파일명/ID 같은 명시 대상이 있으면 refinement를 실행하도록 했다.
  - `refined_route_clears_explicit_new_target_link()`를 추가해 fallback이 같은 intent를 유지하면서 `context_link=none`으로 정리한 결과를 유효한 보정으로 채택하도록 했다.
  - source conversion 요청과 순수 새 항목 생성 요청은 각각 기존 예외/기존 보정에서 처리되도록 분리했다.
  - `test_router_clears_wrong_model_link_for_same_intent_explicit_new_target`를 추가해 `서울 날씨 알려줘`, `OpenAI 최신 모델 검색해줘`, 새 URL 요약 요청이 이전 대상 링크를 제거하는지 고정했다.
  - `test_router_keeps_matching_same_intent_explicit_target_link`를 추가해 명시 대상이 실제 후보와 일치하는 경우에는 연결을 유지하고, retryable 후보는 `retry`로 이어지는 기존 정책도 유지되는지 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_clears_wrong_model_link_for_same_intent_explicit_new_target tests/test_router_agent.py::test_router_keeps_matching_same_intent_explicit_target_link -q`(`4 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`194 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_route_validation.py -q`(`374 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`(`576 passed`), `python3 -m pytest tests/test_weather_agent.py tests/test_web_search_agent.py tests/test_document_analysis_agent.py -q`(`53 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1355 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 모델 cross-location 자동 실행 오판의 라우터 보정

- 작업 이름: 모델이 다른 대화 위치 작업을 `continue`로 바로 실행하려는 경우 확인 질문으로 승격
- 진행상황: 완료
- 진행내용:
  - 같은 사용자라도 대화 위치가 바뀐 경우에는 장기 맥락을 참고하되, 다른 위치에서 하던 작업을 여기서 바로 실행하지 말고 먼저 확인해야 한다.
  - 실행 전 route validation은 이미 cross-location `continue/retry/modify`를 `clarify`로 바꾸고 있었지만, 모델 라우터 로그에는 여전히 바로 실행하려는 `continue` 판단이 남을 수 있었다.
  - `model_route_links_cross_location_candidate()`를 추가해 모델 응답의 `linked_state_id`가 라우터 컨텍스트의 cross-location 후보를 가리키면 refinement를 실행하도록 했다.
  - 이 보정은 기존 `context_aware_fallback_route()`의 cross-location 확인 질문 생성 로직을 재사용하므로, `pending_linked_state_id`, `resolved_slots`, 후보 subject를 보존한 확인 질문으로 전환된다.
  - `test_router_refines_model_cross_location_continue_to_confirmation`을 추가해 모델이 `그거 완료했어`를 다른 위치 할 일 8에 `continue`로 바로 연결해도 최종 라우팅이 `context_link=clarify`로 바뀌는지 고정했다.
  - 기존 cross-location explicit target, source conversion, pending approval, route validation 테스트와 함께 검증해 현재 위치 후보 우선/승인 후 실행 정책이 깨지지 않는지 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_refines_model_cross_location_continue_to_confirmation -q`(`1 passed`), `python3 -m pytest tests/test_router_agent.py::test_router_refines_model_cross_location_continue_to_confirmation tests/test_router_agent.py::test_router_model_refinement_keeps_explicit_cross_location_target_for_confirmation tests/test_router_agent.py::test_router_fallback_explicit_cross_location_id_requires_confirmation tests/test_router_agent.py::test_router_fallback_cross_location_source_reference_creation_requires_confirmation -q`(`4 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`194 passed`), `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clarifies_cross_location_link_before_execution tests/test_route_validation.py::test_validate_route_context_link_standardizes_model_cross_location_clarify_question tests/test_route_validation.py::test_validate_route_context_link_allows_cross_location_link_after_approval -q`(`3 passed`)를 통과했다.
  - 확장 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_bot_helpers.py -q`(`578 passed`), `python3 -m pytest tests/test_cli.py tests/test_context_builder.py -q`(`175 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1357 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 라우팅 검증 로그의 현재 메시지 단서 보존

- 작업 이름: 내부 라우팅 검증 기록에서 현재 사용자 요청과 새 요청 판단 근거가 잘리지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - 라우팅 검증 로그가 길어질 때 `reason`이 앞쪽에 배치되어 `current_message_context`와 `validation_context`가 뒤로 밀릴 수 있는 위험을 확인했다.
  - `route_validation_summary()`의 필드 순서를 조정해 `route_context` 다음에 `current_message_context`가 먼저 남도록 했다. 이제 다음 턴 라우터가 직전 검증의 실제 사용자 문장과 판단 힌트를 더 안정적으로 참고할 수 있다.
  - `build_internal_action_context()`가 라우팅 검증 로그의 `current_message_context`를 별도 필드로 노출하도록 수정했다.
  - 내부 행동 로그에 명시적인 `request=`가 없더라도 `current_message_context`의 `text=`에서 사용자 요청을 복원해, 다음 턴 컨텍스트에 실제 요청 원문 단서가 남도록 했다.
  - `그거 말고 OpenAI 검색해줘`처럼 이전 작업 후보와 분리된 명시 웹검색 요청은 일반 검색어 불일치가 아니라 `새 웹검색 요청`으로 기록하도록 route validation reason을 보강했다.
  - 모델 라우터가 기존 작업 intent를 잘못 고른 경우에도 현재 문장 자체의 명시 새 요청 intent가 강하면 heuristic intent로 복원하는 조건을 넓혔다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py::test_log_route_validation_if_changed_compacts_long_adjustment tests/test_context_builder.py::test_build_router_context_pending_approval_validation_log_is_not_guidance -q`(`2 passed`), `python3 -m pytest tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_task_link_for_separate_web_search tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_search_link_when_new_query_is_only_in_text tests/test_route_validation.py::test_validate_route_context_link_clears_wrong_search_link_from_subject_only_query tests/test_router_agent.py::test_router_refines_wrong_model_task_intent_for_separate_web_search_request -q`(`4 passed`)를 통과했다.
  - 라우팅 관련 회귀 검증으로 `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`554 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1339 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 새 요청 실행 슬롯의 후속 맥락 보존

- 작업 이름: `context_link=none`인 새 요청도 실제 실행 대상 슬롯을 다음 턴 후보와 내부 로그에 남기도록 수정
- 진행상황: 완료
- 진행내용:
  - 기존 `attach_execution_context_metadata()`는 `context_link=none`이면 실행 컨텍스트 메타데이터를 붙이지 않았다.
  - 이 구조에서는 새 요청으로 올바르게 분리된 웹검색/날씨/문서 분석이라도, 에이전트 결과 자체가 `query`, `location`, `document_id` 같은 슬롯을 충분히 남기지 않으면 다음 턴 라우터가 “방금 처리한 대상”을 이어받기 어려울 수 있었다.
  - `safe_internal_action_route_values()`를 수정해 `context_link=none`일 때는 `linked_state_id` 같은 연결 메타데이터는 붙이지 않되, 안전한 `resolved_slots`는 보존하도록 했다.
  - 완료된 turn state 저장 시에는 기존 `turn_state_slots_from_result()`와 `sanitized_turn_state_slots()`가 `resolved_slots`에서 `query`, `location`, `task_id`, `document_id` 같은 실행 대상 슬롯만 승격하고 `pending_original_text`, `context_link`, `linked_state_id` 같은 내부 제어값은 제거한다.
  - `test_attach_execution_context_metadata_keeps_new_request_resolved_slots_for_future_context`를 추가해 새 웹검색 요청의 `query`가 다음 턴 후보 슬롯으로 남고, 내부 연결 메타데이터는 저장되지 않는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_attach_execution_context_metadata_keeps_new_request_resolved_slots_for_future_context tests/test_bot_helpers.py::test_attach_execution_context_metadata_adds_route_slots_for_button_results -q`(`2 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_bot_helpers.py tests/test_context_builder.py tests/test_response_composer.py -q`(`344 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1344 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 새 요청 실행 슬롯의 라우터 후보 힌트 승격 검증

- 작업 이름: 새 요청에서 보존한 실행 슬롯이 다음 턴 라우터 후보의 `slots`와 `target_hints`까지 이어지는지 통합 테스트로 고정
- 진행상황: 완료
- 진행내용:
  - 직전 보강으로 `context_link=none`인 새 요청에도 안전한 `resolved_slots`가 남게 되었지만, 이 값이 실제 다음 턴 라우터 컨텍스트의 후보 힌트까지 노출되는지는 별도 통합 검증이 필요했다.
  - `OperationResult + ExecutionContext`에 새 웹검색 요청의 `query`를 붙이고, 완료 turn state 저장 슬롯으로 정리한 뒤, `build_router_context()`의 `최근 작업 상태 후보`에 `slots={'query': ...}`와 `target_hints`가 남는지 확인하는 테스트를 추가했다.
  - 이 테스트는 새 에이전트를 추가하더라도 실제 실행 대상 슬롯이 `OperationResult`에서 turn state, router context까지 이어져야 한다는 공통 계약을 고정한다.
  - 검증 중 같은 intent의 `새 할 일/새 메모/새 알림` 생성 요청이 모델의 잘못된 기존 항목 링크로 남지 않는 회귀 테스트도 함께 재확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_router_context_promotes_new_request_execution_slots_to_candidate_hints -q`(`1 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py tests/test_router_agent.py -q`(`467 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1350 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 웹검색 query 부분 일치 과연결 방지

- 작업 이름: 이전 웹검색과 일부 단어만 겹치는 새 검색 요청을 기존 검색 retry로 오해하지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 실행 슬롯 보존이 강화되면서, 이전 웹검색의 `query`가 다음 턴 라우터 후보에 더 잘 보이게 되었다.
  - 이 장점이 반대로 `OpenAI` 이전 검색 뒤 `OpenAI 가격 검색해줘` 같은 새 요청을 기존 `OpenAI` 검색 retry로 과하게 연결할 위험을 재현했다.
  - `explicit_web_target_mismatches_candidate()`의 검색어 비교를 수정해, 명시 검색어가 있으면 후보 query와 단순 포함 관계가 아니라 정규화된 query 동등성으로 판단하도록 좁혔다.
  - `검색`, `검색결과` 같은 접미사는 정규화에서 제거해 `OpenAI 검색`과 `OpenAI` 같은 표현 차이는 허용하되, `OpenAI 가격`처럼 추가 대상이 있는 새 query는 기존 `OpenAI` 검색과 분리한다.
  - `test_context_routing_matrix`에 `explicit_web_search_with_longer_query_does_not_retry_shorter_previous_search`를 추가해 부분 문자열만 겹치는 새 웹검색이 `context_link=none`으로 유지되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q -k explicit_web_search_with_longer_query_does_not_retry_shorter_previous_search`(`1 passed`)를 통과했다.
  - 라우팅/검증 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_route_validation.py -q`(`568 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1355 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 날씨 location 부분 일치 과연결 방지

- 작업 이름: 이전 날씨 위치와 일부 글자만 겹치는 새 위치 요청을 기존 날씨 retry로 오해하지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 웹검색 query와 같은 유형의 문제가 날씨 location에도 있는지 확인했다.
  - 이전 후보가 `서울` 날씨일 때 사용자가 `서울역 날씨 알려줘`라고 말하면, 기존 라우터 fallback은 `서울`이 `서울역`에 포함된다는 이유로 이전 날씨 후보의 retry로 연결할 수 있었다.
  - 실행 전 route validation은 최종적으로 링크를 제거하고 있었지만, 라우터 단계의 판단과 내부 로그도 더 정확해야 다음 턴 맥락이 덜 흔들린다.
  - `explicit_weather_target_mismatches_candidate()`를 추가해 명시 날씨 위치가 있으면 후보의 `location` 슬롯/아티팩트 위치와 정규화된 값이 실제로 같은지 확인하도록 했다.
  - `서울역`처럼 더 구체적인 새 위치는 기존 `서울` 후보와 부분 문자열만 겹치더라도 자동 연결하지 않는다.
  - `test_context_routing_matrix`에 `explicit_weather_with_longer_location_does_not_retry_shorter_previous_location`을 추가해 이 흐름을 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q -k 'explicit_weather_with_longer_location_does_not_retry_shorter_previous_location or explicit_web_search_with_longer_query_does_not_retry_shorter_previous_search'`(`2 passed`)를 통과했다.
  - 라우팅/검증 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_route_validation.py -q`(`570 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1357 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 문서 filename 부분 일치 과연결 방지

- 작업 이름: 이전 문서 파일명과 일부만 겹치는 새 파일명 요청을 기존 문서 재분석으로 오해하지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 문서/파일명에서도 웹검색 query, 날씨 location과 같은 부분 일치 과연결 위험이 있는지 확인했다.
  - 이전 후보가 `report.pdf`일 때 사용자가 `report-final.pdf 다시 요약해줘`라고 말하면, 기존 라우터 fallback은 파일명 일부가 겹친다는 이유로 기존 문서 후보의 retry로 연결할 수 있었다.
  - 실행 전 route validation은 최종적으로 링크를 제거했지만, 라우터 단계와 내부 로그에서부터 새 파일명 요청을 기존 문서와 분리하는 것이 더 안정적이다.
  - `explicit_document_target_mismatches_candidate()`를 추가해 명시 파일명이 있으면 후보의 `filename`, `filenames`, `attachment_name`, `attachment_names`와 정규화된 값이 실제로 같은지 확인하도록 했다.
  - `report-final.pdf`처럼 기존 `report.pdf`와 부분 문자열만 겹치는 파일명은 자동 연결하지 않는다.
  - `test_context_routing_matrix`에 `explicit_document_filename_with_longer_name_does_not_retry_shorter_previous_file`을 추가해 이 흐름을 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q -k 'explicit_document_filename_with_longer_name_does_not_retry_shorter_previous_file or explicit_weather_with_longer_location_does_not_retry_shorter_previous_location or explicit_web_search_with_longer_query_does_not_retry_shorter_previous_search'`(`3 passed`)를 통과했다.
  - 라우팅/검증 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_route_validation.py -q`(`571 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1358 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 저장 항목 제목 부분 일치 과연결 방지

- 작업 이름: 할 일/알림 제목 일부가 일반 정보 질문이나 새 항목 생성 요청에 겹쳐도 기존 항목 후속으로 오해하지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 이전 후보가 `병원 예약` 할 일일 때 `병원 예약 준비물 알려줘`가 기존 할 일 조회로 연결되는 문제를 재현했다.
  - 같은 후보에서 `병원 예약 준비물 할 일 추가해줘`도 새 할 일 생성이 아니라 기존 할 일 update/continue처럼 연결될 수 있었다.
  - 이전 알림이 `물 마시기`일 때 `물 마시기 알림음 설정 알려줘`가 기존 알림 후속 조회로 붙는 문제도 확인했다.
  - 일반 정보 질문 marker에 `준비물`, `비용`, `가격`, `설정`을 추가해 저장 항목 제목과 일부가 겹쳐도 일반 정보 요청으로 분리하도록 했다.
  - `explicit_new_item_creation_request_should_not_link_candidate()`를 추가해 대명사나 source conversion 없이 `할 일 추가`, `메모 추가`, `알림 등록`처럼 새 항목 생성 표현이 명확하면 기존 후보에 자동 연결하지 않도록 했다.
  - 단, `병원 예약 할 일에 ... 추가해줘`처럼 기존 항목에 덧붙이는 표현은 `...에` marker로 기존 update 가능성을 보존했다.
  - `알림음`은 단어 안에 `알림`이 들어가지만 저장된 알림 항목을 가리키는 표현이 아니므로 일반 설정 질문으로 분리하는 예외를 추가했다.
  - `test_context_routing_matrix`에 `task_title_general_preparation_question_does_not_continue_task`, `task_title_longer_new_task_creation_does_not_update_existing_task`, `reminder_title_general_setting_question_does_not_continue_reminder`를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q -k 'task_title_general_preparation_question_does_not_continue_task or task_title_longer_new_task_creation_does_not_update_existing_task or reminder_title_general_setting_question_does_not_continue_reminder'`(`3 passed`)를 통과했다.
  - 라우팅/검증 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_route_validation.py -q`(`574 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1362 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 라우팅 검증 결과의 다음 턴 컨텍스트 보강

- 작업 이름: 검증 단계에서 제거된 잘못된 작업 연결이 다음 턴 라우터 컨텍스트에 더 명확히 남도록 수정
- 진행상황: 완료
- 진행내용:
  - 실행 전 라우팅 검증이 `context_link=continue`를 `none`으로 고친 경우에도, 다음 턴 라우터가 왜 연결이 제거되었는지 충분히 참고하지 못할 수 있는 지점을 확인했다.
  - `build_internal_action_context()`가 라우팅 검증 로그의 `current_message_context`를 `internal_action_validation_guidance()`에 함께 넘기도록 수정했다.
  - 검증 전에는 기존 작업에 연결되어 있었지만 검증 후 연결이 제거되었고, 현재 메시지에 `explicit_new_target=True`, `new_request_marker=True`, `replacement_target=True`, `likely_new_request_do_not_link_previous_state` 같은 새 대상/새 요청 신호가 있으면 내부 guidance에 “새 대상/새 요청 때문에 제거됨”이라고 남기도록 했다.
  - 이 guidance는 다음 턴 라우터가 같은 후보를 다시 보더라도, 현재 메시지에 새 대상 신호가 있으면 이전 작업에 재연결하지 않고 새 요청으로 라우팅해야 한다는 기준을 제공한다.
  - `test_build_router_context_guides_removed_link_from_new_target_signal`을 추가해 `서울 날씨 알려줘`처럼 이전 `원주` 날씨 작업과 분리된 새 위치 요청의 검증 결과가 다음 턴 컨텍스트에 명확히 남는지 고정했다.
  - `cross_location_document_filename_with_longer_name_does_not_ask_to_continue_shorter_file`을 추가해, 다른 대화 위치의 `report.pdf` 문서 후보가 있어도 현재 요청의 `report-final.pdf`처럼 일부만 겹치는 새 파일명을 이전 문서 작업 확인 질문으로 바꾸지 않도록 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_router_context_guides_removed_link_from_new_target_signal -q`(`1 passed`)를 통과했다.
  - 파일명 cross-location 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q -k 'cross_location_document_filename_with_longer_name_does_not_ask_to_continue_shorter_file or explicit_document_filename_with_longer_name_does_not_retry_shorter_previous_file'`(`2 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_router_context_guides_removed_link_from_new_target_signal tests/test_context_builder.py::test_build_router_context_guides_unlinked_clarify_cleared_to_new_request tests/test_context_builder.py::test_build_router_context_validation_context_is_parseable_by_router tests/test_context_builder.py::test_build_router_context_pending_approval_validation_log_is_not_guidance -q`(`4 passed`), `python3 -m pytest tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment tests/test_cli.py::test_log_route_validation_if_changed_preserves_parseable_context_with_many_slots -q`(`2 passed`)를 통과했다.
  - 넓은 라우터/컨텍스트 회귀 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`287 passed`), `python3 -m pytest tests/test_router_agent.py tests/test_bot_helpers.py -q`(`383 passed`)를 통과했다.
  - 추가 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_router_agent.py tests/test_route_validation.py -q`(`575 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_bot_helpers.py -q`(`298 passed`)를 통과했다.

## 2026-06-08 - 새 에이전트용 대상 슬롯 계약과 긴 내부 로그 보존 보강

- 작업 이름: 에이전트가 남기는 후속 대상 슬롯 계약을 런타임 상수로 정리하고, 긴 내부 행동 로그에서도 핵심 맥락이 잘리지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 새 에이전트가 추가될 때 `memory_id`, `document_id`, `task_title`, `location`, `query`, `filename`, `url` 같은 후속 대상 슬롯이 라우터 후보, 내부 행동 로그, route slot merge에 모두 같은 의미로 이어져야 한다.
  - 기존에는 이 대상 슬롯 목록이 테스트 안에 별도 상수로만 있어, 실제 런타임 계약이 어느 값까지를 “라우터가 따라갈 수 있는 대상 슬롯”으로 보는지 덜 명확했다.
  - `assistant_bot/agent_registry.py`에 `CONTEXT_TARGET_SLOT_KEYS`를 추가하고, `tests/test_agent_registry.py`의 계약 검증이 이 런타임 상수를 기준으로 동작하도록 정리했다.
  - 긴 내부 행동 로그가 잘릴 때 `current_message_context`의 `named_target_lookup`, `new_request_marker`, `decision_hint` 같은 핵심 플래그가 사라지는 문제를 확인했다.
  - `internal_action_identity_prefix()`가 현재 메시지 진단을 그대로 넣지 않고 핵심 플래그만 짧게 압축해 보존하도록 했다. 빈 `current_message_context=-`는 제거해 기존 identity 필드를 밀어내지 않게 했다.
  - `target_hints`도 긴 내부 로그의 앞쪽 identity 영역에 짧게 보존하고, `| ... | link_guidance`가 끼어도 라우터의 `internal_action_context_by_linked_state()`가 literal target hint 목록을 파싱할 수 있도록 보정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_router_context_keeps_parseable_internal_route_context_when_trimmed tests/test_context_builder.py::test_build_router_context_keeps_internal_action_identity_when_long_line_is_trimmed tests/test_context_builder.py::test_build_router_context_guides_removed_stored_item_link_from_general_question -q`(`3 passed`)를 통과했다.
  - 계약/라우팅 회귀 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`468 passed`), `python3 -m pytest tests/test_agent_registry.py -q`(`91 passed`)를 통과했다.

## 2026-06-08 - 내부 연결 판단 로그의 긴 대상 압축 보강

- 작업 이름: 긴 파일명/URL/검색어 target이 있어도 내부 연결 판단의 핵심 플래그와 후보 판단이 보존되도록 수정
- 진행상황: 완료
- 진행내용:
  - `맥락 연결 판단 요약`은 현재 메시지와 최근 작업 후보를 비교해 `do_not_link_new_request`, `ask_user_before_execute` 같은 권고를 남긴다.
  - 이 요약이 내부 행동 로그의 `context_decision`으로 들어갈 때, 긴 파일명이나 URL, 검색어가 `targets`에 포함되면 단순 길이 제한 때문에 핵심 플래그가 흐려질 수 있는 위험을 확인했다.
  - `safe_internal_action_context_decision_values()`가 현재 메시지 판단을 기록할 때 `follow_up_reference`, `explicit_new_target`, `new_request_marker`는 그대로 보존하고 `targets`만 짧게 압축하도록 `compact_context_decision_current_message()`를 추가했다.
  - 라우터의 `route_log_context_decision()`에도 같은 방식의 `compact_route_context_decision_current_message()`를 추가해, 모델 라우팅 로그와 실행 결과 로그가 같은 형태의 판단 신호를 남기도록 맞췄다.
  - `test_internal_action_context_decision_compacts_long_targets_but_keeps_flags`와 `test_route_log_context_decision_compacts_long_targets_but_keeps_flags`를 추가해 긴 PDF 파일명 target에서도 새 요청 플래그와 후보의 `do_not_link_new_request` 판단이 유지되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_internal_action_result_reason_records_context_decision_even_without_link tests/test_bot_helpers.py::test_internal_action_context_decision_compacts_long_targets_but_keeps_flags -q`(`2 passed`), `python3 -m pytest tests/test_router_agent.py::test_route_log_reason_records_current_message_and_context_decision tests/test_router_agent.py::test_route_log_context_decision_compacts_long_targets_but_keeps_flags -q`(`2 passed`)를 통과했다.
  - 라우팅/검증 회귀 검증으로 `python3 -m pytest tests/test_bot_helpers.py tests/test_router_agent.py tests/test_context_builder.py -q`(`478 passed`), `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`399 passed`)를 통과했다.

## 2026-06-08 - 공통 후속 표현 marker 계약 보강

- 작업 이름: 라우터와 실행 전 검증 계층의 후속 표현 인식 기준이 갈라지지 않도록 공통 marker helper와 계약 테스트 추가
- 진행상황: 완료
- 진행내용:
  - 계획 문서의 “라우터의 후속 표현 marker와 route validation의 후속 표현 marker는 같은 의미권을 유지한다” 요구사항을 현재 코드 기준으로 점검했다.
  - `routing_markers.py`에 `shared_follow_up_reference_markers()`를 추가해 generic reference, 명시 source reference, 최근 reference, 최근 저장 항목 reference marker를 한 번에 제공하도록 했다.
  - `route_validation.FOLLOW_UP_MARKERS`가 이 공통 helper를 포함하도록 수정했다.
  - 라우터의 `has_follow_up_signal()`과 `has_pronoun_follow_up_signal()`도 같은 helper를 참고하도록 해, 새 marker가 추가될 때 한쪽만 인식하는 위험을 줄였다.
  - `test_shared_reference_markers_are_recognized_by_validation_and_router`를 추가해 공통 marker가 라우터와 검증 계층 양쪽에서 후속 표현으로 인식되는지 고정했다.
  - `test_recent_stored_item_reference_markers_are_follow_up_signals`를 추가해 `방금저장한`, `아까등록한` 같은 최근 저장 항목 표현도 양쪽에서 후속 신호로 유지되는지 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_route_validation.py::test_shared_reference_markers_are_recognized_by_validation_and_router tests/test_route_validation.py::test_recent_stored_item_reference_markers_are_follow_up_signals -q`(`2 passed`), `python3 -m pytest tests/test_router_agent.py -q`(`180 passed`)를 통과했다.
  - 넓은 회귀 검증으로 `python3 -m pytest tests/test_route_validation.py tests/test_context_routing_matrix.py tests/test_context_builder.py -q`(`494 passed`), `python3 -m pytest tests/test_bot_helpers.py tests/test_agent_registry.py -q`(`299 passed`)를 통과했다.

## 2026-06-08 - 저장 항목 링크 제거 검증 신호 보존

- 작업 이름: 저장 항목 제목과 겹치는 일반 정보 질문에서 링크 제거 이유가 다음 턴 라우터 컨텍스트에 보존되도록 수정
- 진행상황: 완료
- 진행내용:
  - `병원 예약 준비물 알려줘`처럼 저장된 할 일 제목과 일부가 겹치지만 실제로는 일반 정보 질문인 경우, route validation이 기존 작업 연결을 제거해도 다음 턴 컨텍스트 압축에서 `named_target_lookup=True`가 잘려나갈 수 있는 문제를 확인했다.
  - `compact_current_message_context_for_validation()`이 모든 boolean 신호를 길게 보존하던 방식을 바꿔, 실제로 참인 신호만 남기도록 수정했다.
  - 이로써 `new_request_marker=True`, `named_target_lookup=True`, `named_target_mutation=True` 같은 라우팅 판단 핵심 신호가 내부 행동 기록의 `current_message_context` 안에서 우선 보존된다.
  - `test_build_router_context_guides_removed_stored_item_link_from_general_question`을 추가해 저장 항목 후보와 제목이 겹친 일반 정보 질문도 다음 턴에 기존 항목으로 재연결되지 않도록 검증했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_router_context_guides_removed_stored_item_link_from_general_question -q`(`1 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_router_context_guides_removed_link_from_new_target_signal tests/test_context_builder.py::test_build_router_context_guides_removed_stored_item_link_from_general_question tests/test_cli.py::test_log_route_validation_if_changed_records_adjustment tests/test_cli.py::test_log_route_validation_if_changed_compacts_long_adjustment tests/test_cli.py::test_log_route_validation_if_changed_preserves_parseable_context_with_many_slots -q`(`5 passed`)를 통과했다.
  - 넓은 컨텍스트/라우터 회귀 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_cli.py tests/test_router_agent.py -q`(`353 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1364 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 내부 행동 로그 identity 압축 신호 일관화

- 작업 이름: 긴 내부 행동 로그가 잘릴 때 현재 메시지 진단의 참 신호만 보존하도록 정리
- 진행상황: 완료
- 진행내용:
  - route validation 요약 압축에서는 `False` 신호를 제거했지만, 긴 내부 행동 로그의 identity 영역을 만드는 `internal_action_identity_field()`는 여전히 모든 boolean 신호를 보존하고 있었다.
  - 이 불일치 때문에 내부 로그가 매우 길어질 경우 `new_request_marker=True`, `named_target_lookup=True` 같은 핵심 신호가 낮은 가치의 `False` 신호에 밀릴 수 있는 여지가 있었다.
  - `internal_action_identity_field()`도 참인 신호만 보존하도록 수정해 라우터 컨텍스트 압축 규칙을 일관화했다.
  - `test_internal_action_identity_field_prioritizes_true_current_message_signals`를 추가해 현재 메시지 진단이 짧아질 때 핵심 참 신호와 `decision_hint`는 남고, 거짓 신호는 제거되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py::test_internal_action_identity_field_prioritizes_true_current_message_signals tests/test_context_builder.py::test_build_router_context_keeps_internal_action_identity_when_long_line_is_trimmed tests/test_context_builder.py::test_build_router_context_guides_removed_stored_item_link_from_general_question -q`(`3 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_cli.py tests/test_router_agent.py -q`(`355 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1367 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 긍정 접두사와 맥락 거절이 섞인 새 요청 회귀 고정

- 작업 이름: `응/좋아/네 + 그거 말고 + 새 요청` 문장을 pending 맥락 승인으로 오해하지 않도록 테스트 보강
- 진행상황: 완료
- 진행내용:
  - pending 후속 확인이 있는 상태에서 사용자가 `응 그거 말고 서울 날씨 알려줘`, `좋아 그거 말고 OpenAI 검색해줘`, `네 그거 말고 지금 몇시야`처럼 말하면 앞부분의 긍정 표현 때문에 기존 작업 승인으로 소비될 위험이 있는지 점검했다.
  - 현재 라우터는 해당 문장을 각각 `weather`, `web_search`, `current_time`의 새 요청으로 올바르게 분리하고 있어 코드 수정은 필요하지 않았다.
  - `test_router_fallback_does_not_approve_pending_context_for_positive_rejection_new_request`를 추가해 이 정책을 명시적으로 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_fallback_does_not_approve_pending_context_for_positive_rejection_new_request tests/test_router_agent.py::test_router_fallback_does_not_approve_pending_context_for_positive_prefixed_weather_request tests/test_router_agent.py::test_router_fallback_does_not_cancel_pending_context_for_negative_prefixed_web_request -q`(`5 passed`)를 통과했다.
  - 라우터/검증 회귀 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`581 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1372 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 다른 위치 후보와 새 할 일 생성 분리 회귀 고정

- 작업 이름: 같은 사용자 다른 위치의 기존 할 일 후보가 있어도 명시적 새 할 일 생성 요청은 확인 질문으로 빼앗지 않도록 테스트 보강
- 진행상황: 완료
- 진행내용:
  - 다른 위치에 `병원 예약` 할 일 후보가 남아 있을 때 `병원 예약 준비물 할 일 추가해줘`, `장보기 할 일 추가해줘`, `새 할 일 병원 예약 추가해줘`, `병원 예약 말고 장보기 할 일 추가해줘`가 기존 후보 확인 질문으로 바뀌지 않는지 점검했다.
  - 현재 라우터는 모두 `manage_task`, `context_link=none`으로 새 요청 처리하고 있어 코드 수정은 필요하지 않았다.
  - `test_router_fallback_does_not_clarify_cross_location_for_explicit_new_task_creation`을 추가해 다른 위치 후보보다 현재 메시지의 새 생성 의도가 우선한다는 정책을 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_fallback_does_not_clarify_cross_location_for_explicit_new_task_creation tests/test_router_agent.py::test_router_fallback_explicit_cross_location_id_requires_confirmation tests/test_router_agent.py::test_router_fallback_clarifies_cross_location_pronoun_follow_up -q`(`6 passed`)를 통과했다.
  - 라우터/검증 회귀 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`585 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1376 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 모델 오판 기반 다른 위치 새 생성 링크 제거 회귀 고정

- 작업 이름: 모델이 다른 위치 기존 할 일에 잘못 `continue`를 반환해도 명시적 새 할 일 생성은 새 요청으로 복구되는지 테스트 보강
- 진행상황: 완료
- 진행내용:
  - fallback 라우터는 다른 위치 기존 후보가 있어도 `새 할 일 병원 예약 추가해줘`를 새 요청으로 처리하지만, 실제 운영에서는 라우팅 모델이 기존 후보에 `context_link=continue`를 잘못 붙일 수 있다.
  - 현재 refinement 로직이 이 모델 오판을 `context_link=none`, `linked_state_id=None`, 빈 `resolved_slots`로 복구하는지 확인했다.
  - `test_router_clears_wrong_model_cross_location_link_for_new_task_creation`을 추가해 다른 위치 후보, 명시적 새 할 일 생성, 모델의 잘못된 continue 링크 조합을 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_clears_wrong_model_cross_location_link_for_new_task_creation tests/test_router_agent.py::test_router_clears_wrong_model_link_for_same_intent_new_item_creation tests/test_router_agent.py::test_router_refines_model_cross_location_continue_to_confirmation -q`(`5 passed`)를 통과했다.
  - 라우터/검증 회귀 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`586 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1379 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 모델 clarify 오판 기반 새 생성 확인 질문 제거 회귀 고정

- 작업 이름: 모델이 명시적 새 할 일 생성 요청을 기존 작업 확인 질문으로 잘못 바꿔도 새 요청으로 복구되는지 테스트 보강
- 진행상황: 완료
- 진행내용:
  - 모델이 `새 할 일 병원 예약 추가해줘`를 보고 다른 위치 기존 `병원 예약` 후보에 대해 `context_link=clarify`를 반환하는 경우를 점검했다.
  - 연결 대상이 있는 clarify와 연결 대상이 없는 clarify 모두 현재 refinement 로직이 `context_link=none`, `linked_state_id=None`, 빈 `resolved_slots`, 빈 `clarification_question`으로 복구하는 것을 확인했다.
  - `test_router_clears_wrong_model_clarify_for_new_task_creation`을 추가해 “실행하지 않고 물어보기만 하는 오판”도 사용자 의도와 충돌하면 제거되도록 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py::test_router_clears_wrong_model_clarify_for_new_task_creation tests/test_router_agent.py::test_router_clears_wrong_model_cross_location_link_for_new_task_creation tests/test_router_agent.py::test_router_clears_wrong_model_link_for_same_intent_new_item_creation -q`(`6 passed`)를 통과했다.
  - 라우터/검증 회귀 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`588 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1381 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 현재 메시지 진단 압축 정책 일원화와 알림 상세 facts 보강

- 작업 이름: route validation 요약과 내부 행동 로그 identity가 같은 현재 메시지 신호 압축 helper를 사용하도록 정리
- 진행상황: 완료
- 진행내용:
  - `bot.py`의 `compact_current_message_context_for_validation()`과 `context_builder.py`의 `internal_action_identity_field()`가 같은 boolean 신호 목록과 `True` 신호만 보존하는 규칙을 각각 따로 들고 있는 중복을 확인했다.
  - `context_builder.py`에 `CURRENT_MESSAGE_CONTEXT_SIGNAL_KEYS`와 `compact_current_message_true_signals()`를 추가해 `follow_up_reference`, `new_request_marker`, `named_target_lookup` 같은 핵심 신호 압축 정책을 한 곳에서 관리하도록 했다.
  - route validation 요약 압축과 내부 행동 로그 identity 압축이 모두 이 helper를 사용하게 바꿔, 앞으로 새 신호가 추가될 때 한쪽만 누락되는 위험을 줄였다.
  - 전체 검증 중 단일 알림 상세 결과의 `facts`에 `reminder_ids`가 없어 복수 알림 조회 결과와 후속 맥락 계약이 달라지는 문제를 발견했다.
  - `ReminderAgent.reminder_detail_result()`의 `facts`에 `reminder_ids: [item.id]`를 추가해 단일/복수 알림 조회가 라우터와 응답 작성기에 같은 ID 계약을 제공하도록 보강했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py::test_internal_action_identity_field_prioritizes_true_current_message_signals tests/test_context_builder.py::test_build_router_context_guides_removed_stored_item_link_from_general_question tests/test_context_builder.py::test_build_router_context_guides_removed_link_from_new_target_signal -q`(`3 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_builder.py tests/test_cli.py tests/test_router_agent.py -q`(`365 passed`)와 `python3 -m pytest tests/test_memory_store.py::test_reminder_agent_show_prefers_resolved_ids_over_stale_linked_state tests/test_memory_store.py::test_reminder_agent_show_uses_linked_plural_reminder_ids tests/test_memory_store.py::test_reminder_agent_show_prefers_linked_reminder_context -q`(`3 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1385 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 할 일 결과 ID facts 계약 보강과 resolved_slots 안전 접근 정리

- 작업 이름: 할 일 단일/복수 결과가 facts와 slots 모두에서 같은 ID 계약을 제공하도록 보강
- 진행상황: 완료
- 진행내용:
  - 알림 상세 결과에서 발견한 단수/복수 ID facts 불일치와 같은 패턴이 할 일 에이전트에도 있는지 점검했다.
  - 할 일 생성, 중복 확인, 최근 완료 다시 열기, 최근 삭제 복구, 최근 추가 삭제, 최근/ID 상세 조회 결과에서 slots에는 `task_id/task_ids`가 있지만 facts에는 `task` 또는 `duplicate_task`만 있는 경우를 확인했다.
  - 해당 결과들의 facts에 `task_id`와 `task_ids`를 추가해 내부 행동 로그, subject 추론, 다음 턴 라우팅이 같은 ID 정보를 안정적으로 참고하도록 했다.
  - `resolved_or_linked_artifact_ids()`와 `resolved_or_linked_urls()`가 `execution_context.resolved_slots.get(key)`를 동적 key로 읽어 정적 안전 슬롯 계약 테스트에 걸리는 문제도 확인했다.
  - resolved slots는 `items()`에서 허용된 호출자 slot key만 필터링하도록 바꿔, 동적 `.get()` 사용 없이 read-only 안전 슬롯 계약을 유지했다.
  - `tests/test_memory_store.py`의 할 일 생성/상세/최근 완료 되돌리기/최근 삭제 테스트에 facts ID 검증을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_memory_store.py::test_task_agent_creates_task_from_linked_memory_reference tests/test_memory_store.py::test_task_agent_show_detail_prefers_linked_task_context tests/test_memory_store.py::test_task_agent_show_detail_prefers_resolved_plural_task_context tests/test_memory_store.py::test_task_agent_reopens_latest_completed_task tests/test_memory_store.py::test_task_agent_deletes_latest_added_task -q`(`5 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_specialist_agents_read_only_safe_execution_resolved_slots tests/test_memory_store.py -q`(`125 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1385 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 첨부 문서 저장 결과 ID 계약 보강

- 작업 이름: 첨부 파일을 기억으로 저장한 결과가 문서 ID를 facts, slots, artifacts에 일관되게 남기도록 보강
- 진행상황: 완료
- 진행내용:
  - 첨부 문서 저장 경로에서 `document_id`는 facts에 있었지만 `document_ids`, slots, artifacts가 부족해 다음 턴의 `그 문서 다시 요약해줘`, `그 파일 삭제해줘` 같은 후속 요청 맥락이 덜 안정적일 수 있는 지점을 확인했다.
  - 신규 문서 저장 결과와 중복 문서 확인 결과 모두 `document_id`, `document_ids`, `filename`, `attachment_name`, 문서 artifact, `show/summarize/reanalyze/delete` 액션을 남기도록 보강했다.
  - 여러 첨부 저장 결과를 묶는 bundled result도 저장된 문서 ID를 집계해 facts, slots, subject, artifacts, available_actions에 반영하도록 했다.
  - `remember` intent에서 첨부 문서 저장 결과가 문서 슬롯과 `summarize/reanalyze` 액션을 반환할 수 있으므로 `agent_catalog.json`의 state_outputs 계약도 갱신했다.
  - `test_assistant_bot_keeps_pending_attachment_for_chat_approval`에 facts/slots/artifacts의 문서 ID 계약 검증을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_assistant_bot_keeps_pending_attachment_for_chat_approval tests/test_bot_helpers.py::test_assistant_bot_auto_saves_and_answers_attached_document_request tests/test_document_analysis_agent.py::test_document_analysis_agent_prefers_resolved_document_ids_over_stale_linked_state -q`(`3 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_bot_helpers.py tests/test_document_analysis_agent.py -q`(`222 passed`)와 `python3 -m pytest tests/test_agent_registry.py::test_agent_catalog_declares_literal_operation_result_actions tests/test_agent_registry.py::test_literal_operation_results_follow_catalog_contract tests/test_bot_helpers.py::test_assistant_bot_keeps_pending_attachment_for_chat_approval -q`(`3 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1391 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 실행 에이전트 복수 대상 슬롯 계약 보강

- 작업 이름: 라우터가 넘긴 `resolved_slots.task_ids`를 TaskAgent 실행 단계에서 최신 항목보다 우선한다는 회귀 테스트 추가
- 진행상황: 완료
- 진행내용:
  - 맥락 파악 품질을 높이려면 라우터가 앞선 대화에서 해석한 대상 슬롯을 전문 에이전트가 원문 재해석이나 현재 위치 최신 항목보다 우선해야 한다.
  - 기존 TaskAgent는 단수 `task_id` 기반 조회/수정/삭제 회귀 테스트가 강하게 잡혀 있었고, 내부 `_linked_task_ids()`도 `resolved_slots.task_ids`를 읽고 있었다.
  - 복수 대상 실행 계약을 명시적으로 고정하기 위해 `test_task_agent_show_detail_prefers_resolved_plural_task_context`를 추가했다.
  - 같은 원칙이 변경 작업에서도 유지되는지 확인하기 위해 `test_task_agent_delete_prefers_resolved_plural_task_context_over_latest_item`를 추가했다.
  - 두 테스트는 원문이 `방금 추가한 할 일`처럼 최신 항목을 가리킬 수 있는 상황에서도, `resolved_slots.task_ids`로 전달된 두 항목만 조회/삭제하고 현재 채널 최신 항목은 건드리지 않는지 검증한다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_memory_store.py -k "resolved_plural_task_context"`(`2 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_memory_store.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`523 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1379 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 실행 에이전트 resolved 슬롯 우선순위 보강

- 작업 이름: `resolved_slots`와 linked state가 충돌할 때 실행 에이전트가 resolved 대상만 사용하도록 수정
- 진행상황: 완료
- 진행내용:
  - 라우터가 현재 메시지와 최근 작업 상태를 보고 확정한 `resolved_slots`는 실행 단계의 최종 대상이어야 한다.
  - 기존 helper들은 `resolved_slots`를 먼저 읽은 뒤 linked state의 slots/artifacts도 함께 합쳤기 때문에, 실행 전 검증을 우회하거나 stale 상태가 남는 경우 resolved 대상과 오래된 대상이 같이 실행될 여지가 있었다.
  - TaskAgent, ReminderAgent, MemoryAgent, DocumentAnalysisAgent, WebSearchAgent의 linked target helper를 수정해 `resolved_slots`에 유효한 ID/URL이 있으면 즉시 그 값만 반환하고, linked state는 resolved 값이 없을 때만 fallback으로 사용하도록 했다.
  - ReminderAgent의 ID 변환 로직은 `_coerce_reminder_ids()` helper로 분리해 resolved/fallback 양쪽에서 같은 dedupe 규칙을 쓰도록 정리했다.
  - TaskAgent 조회, Reminder 조회, Memory 회상, DocumentAnalysis 재분석, Web URL 재요약에 각각 stale linked state 충돌 회귀 테스트를 추가하거나 기존 테스트를 강화했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_memory_store.py -k "stale_linked_state or resolved_plural_task_context" tests/test_document_analysis_agent.py -k "stale_linked_state" tests/test_web_search_agent.py -k "stale_linked_state"`(`4 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_memory_store.py tests/test_document_analysis_agent.py tests/test_web_search_agent.py tests/test_route_validation.py -q`(`368 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1385 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - resolved 우선 실행 대상 helper 공통화

- 작업 이름: 새 에이전트가 후속 실행 대상을 읽을 때 같은 resolved 우선 규칙을 재사용하도록 공통 helper 추가
- 진행상황: 완료
- 진행내용:
  - 직전 작업에서 Task/Reminder/Memory/Document/Web 에이전트별로 `resolved_slots`를 linked state보다 우선하도록 보강했지만, 규칙이 각 파일에 흩어져 있어 새 에이전트 추가 시 같은 실수를 반복할 수 있었다.
  - `agents/common.py`에 `coerce_int_values()`, `resolved_or_linked_artifact_ids()`, `coerce_url_values()`, `resolved_or_linked_urls()`를 추가했다.
  - 공통 helper의 계약은 `resolved_slots`에 유효한 ID/URL이 있으면 그 값만 반환하고, linked state slots/artifacts는 resolved 값이 없을 때만 fallback으로 사용하는 것이다.
  - TaskAgent, ReminderAgent, MemoryAgent, DocumentAnalysisAgent, WebSearchAgent의 대상 추출 helper가 공통 helper를 사용하도록 정리했다.
  - 사용처가 없어진 Task/Memory/DocumentAnalysis의 로컬 `_coerce_int_list()`와 Reminder의 `_coerce_reminder_ids()`, WebSearch의 `_coerce_urls()`를 제거했다.
  - `tests/test_agent_common.py`를 추가해 ID 대상과 URL 대상 모두 resolved 우선/fallback 동작을 직접 검증했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_agent_common.py`(`4 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_agent_common.py tests/test_memory_store.py tests/test_document_analysis_agent.py tests/test_web_search_agent.py tests/test_route_validation.py -q`(`372 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1389 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 오케스트레이션 삭제 확인 대상도 resolved 우선 계약 적용

- 작업 이름: Discord 봇의 삭제 확인 전처리에서 task/reminder 대상 ID를 resolved 슬롯 우선으로 복원하도록 수정
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록과 실행 컨텍스트를 점검하면서, 전문 에이전트는 공통 `resolved_or_linked_artifact_ids()` helper를 쓰지만 Discord 봇의 삭제 확인 전처리 helper는 여전히 별도 로직으로 `resolved_slots`와 linked state 값을 합치고 있음을 확인했다.
  - `task_ids_from_execution_context()`와 `reminder_ids_from_execution_context()`를 공통 `resolved_or_linked_artifact_ids()` 사용으로 교체했다.
  - 이로써 `할 일 삭제해줘`, `알림 삭제해줘`가 라우터가 확정한 resolved ID와 오래된 linked state ID를 동시에 삭제 확인 대상으로 삼는 위험을 줄였다.
  - `test_task_ids_from_execution_context_prefers_resolved_slots_over_stale_linked_state`와 `test_reminder_ids_from_execution_context_prefers_resolved_slots_over_stale_linked_state`를 추가해 오케스트레이션 단계에서도 resolved 슬롯이 stale linked state보다 우선하는지 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_agent_common.py tests/test_bot_helpers.py -k "execution_context_prefers_resolved_slots or resolved_or_linked"`(`6 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_bot_helpers.py tests/test_agent_common.py tests/test_route_validation.py -q`(`415 passed`)를 통과했다.
  - 전체 검증 중 `remember`의 문서 저장 응답 action과 카탈로그 선언이 어긋난 것으로 보이는 일시 실패를 확인했으나, 현재 `agent_catalog.json`에는 `available_actions.summarize`와 `available_actions.reanalyze`가 이미 선언되어 있음을 재확인했다.
  - 해당 실패 테스트만 재실행해 `python3 -m pytest -q tests/test_agent_registry.py::test_agent_catalog_declares_literal_operation_result_actions tests/test_agent_registry.py::test_literal_operation_results_follow_catalog_contract`(`2 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1391 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - ID 슬롯 계약 안전성 보강

- 작업 이름: 공통 실행 대상 ID 변환에서 boolean 값을 ID로 오인하지 않도록 수정하고 카탈로그-아티팩트 ID 계약 테스트 추가
- 진행상황: 완료
- 진행내용:
  - `resolved_or_linked_artifact_ids()`가 사용하는 `coerce_int_values()`는 파이썬 특성상 `True`를 `1`, `False`를 `0`으로 변환할 수 있었다.
  - 라우터의 `resolved_slots`는 모델/JSON 경로를 거치므로 잘못된 boolean 값이 들어왔을 때 실제 ID로 실행되는 것을 막아야 한다.
  - `coerce_int_values()`가 boolean 값을 무시하도록 수정했다.
  - `artifact_id_values()` 내부에 숨어 있던 kind별 ID slot key 목록을 `ARTIFACT_ID_SLOT_KEYS_BY_KIND` 상수로 올려 테스트와 새 에이전트 개발자가 같은 계약을 참고할 수 있게 했다.
  - `test_coerce_int_values_ignores_boolean_values`를 추가해 boolean 값이 ID로 변환되지 않는지 고정했다.
  - `test_artifact_id_slot_key_contract_covers_follow_up_target_kinds`와 `test_catalog_id_target_slots_match_artifact_id_slot_contract`를 추가해 memory/document/task/reminder ID slot family가 카탈로그 target slot 계약과 어긋나지 않도록 했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_agent_common.py tests/test_agent_registry.py::test_catalog_id_target_slots_match_artifact_id_slot_contract tests/test_agent_registry.py::test_catalog_target_slot_contract_matches_runtime_context_sets`(`8 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_agent_common.py tests/test_agent_registry.py tests/test_route_validation.py tests/test_bot_helpers.py -q`(`509 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1394 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 응답 작성 내부 키 누출 방지 보강

- 작업 이름: 최종 응답 모델 출력에서 standalone 내부 route/debug 키가 사용자 답변에 남지 않도록 후처리 강화
- 진행상황: 완료
- 진행내용:
  - `ResponseComposer`는 내부 행동 기록을 비공개 참고 정보로 모델 입력에 제공하지만, 모델이 `linked_state_id를 참고했다`, `resolved_slots는 숨기겠다`처럼 내부 키 이름만 자연어에 섞어 말할 수 있는 위험을 점검했다.
  - 기존 후처리는 `context_link=...`, `linked_state_id=...` 같은 할당문과 `route_validation` 단어를 제거했지만, standalone 내부 키 토큰에는 더 약했다.
  - `sanitize_model_answer_text()`가 `RESPONSE_PRIVATE_ROUTE_TEXT_KEY_PATTERN`을 사용해 standalone 내부 route/debug 키 토큰도 제거하도록 보강했다.
  - 한국어 조사 `을/를/이/가/은/는/도/만/까지`가 붙은 내부 키도 제거하도록 처리했다.
  - `test_response_composer_sanitizes_standalone_private_keys_from_model_output`을 추가해 `linked_state_id를`, `resolved_slots는`, `pending_resolved_slots도` 같은 모델 출력이 사용자 답변에 남지 않는지 고정했다.
  - 직접 검증으로 `python3 -m pytest -q tests/test_response_composer.py::test_response_composer_sanitizes_private_metadata_from_model_output tests/test_response_composer.py::test_response_composer_sanitizes_standalone_private_keys_from_model_output`(`2 passed`)를 통과했다.
  - 응답 composer 회귀 검증으로 `python3 -m pytest tests/test_response_composer.py -q`(`49 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_response_composer.py tests/test_agent_registry.py tests/test_bot_helpers.py -q`(`351 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1395 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 웹 검색/URL 후속 맥락 계약 보강

- 작업 이름: 웹 검색 결과와 URL 직접 읽기 결과가 다음 턴 라우팅에 필요한 query, URL, 제목 정보를 안정적으로 남기도록 수정
- 진행상황: 완료
- 진행내용:
  - 웹 검색 성공 결과가 기존에는 `query/queries` 중심으로만 상태를 남겨, 사용자가 `방금 그 링크 열어줘`, `아까 검색 결과 다시 요약해줘`처럼 이어 말할 때 URL/제목 단서가 약할 수 있었다.
  - `web_search` 성공 결과의 facts와 slots에 `query`, `queries`, `url`, `urls`, `url_title`, `url_titles`를 함께 남기도록 보강했다.
  - 검색 결과 artifacts에 상위 URL 묶음 artifact와 개별 URL artifact를 함께 남겨, 라우터와 컨텍스트 빌더가 단수/복수 링크 표현을 모두 안정적으로 참조할 수 있게 했다.
  - `web_url` 직접 읽기 성공/실패 결과도 facts에 단수 `url`과, 제목이 있을 경우 `url_title`을 함께 남기도록 맞췄다.
  - `search_result_urls()`, `search_result_titles()`, `web_search_slots()`, `web_search_artifacts()` helper를 추가해 새 웹 계열 에이전트가 같은 출력 계약을 재사용하기 쉽게 했다.
  - `test_web_search_agent_summarizes_naver_results`와 URL 읽기 실패 테스트에 facts/slots/artifacts 계약 검증을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_web_search_agent.py -q`(`31 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_agent_registry.py -q`(`92 passed`)와 `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py -q`(`293 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1394 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 도구 결과 내부 맥락 단서 보존 보강

- 작업 이름: tool calling 기반 내부 행동 기록에서 URL 제목과 파일명 단서가 라우터 컨텍스트와 turn state에 남도록 수정
- 진행상황: 완료
- 진행내용:
  - 목표 중 “사용자에게 보이지 않는 내부 행동도 컨텍스트에서 참고” 항목을 점검하면서, tool trace 결과 요약이 일부 ID와 제목은 보존하지만 `url_title`, `urls`, `filename`, `filenames`, `attachment_name` 같은 후속 대상 단서가 누락될 수 있음을 확인했다.
  - `compact_internal_action_tool_result_item()`의 허용 키를 확장해 내부 행동 컨텍스트의 `tool_context`에 URL 제목, URL 묶음, 파일명, 첨부명, 사람이 읽기 좋은 시간 단서가 안전하게 남도록 했다.
  - `infer_tool_trace_artifact_from_item()`도 같은 계열의 URL/파일 제목 단서를 artifact로 복원하도록 보강했다.
  - tool trace item에 `memory_id`, `document_id`, `task_id`, `reminder_id`만 있고 공통 `id`가 없는 경우에도 turn state artifact의 `id`를 함께 채우도록 수정했다.
  - 이로써 새 tool calling 기반 에이전트가 검색 결과, 문서 상세, 작업 목록 등을 도구로 가져온 뒤 사용자가 “방금 그 링크”, “그 문서”, “아까 파일”처럼 이어 말할 때 라우터가 더 풍부한 내부 단서를 참고할 수 있다.
  - `test_build_router_context_preserves_tool_trace_url_and_file_titles`를 추가해 도구 결과의 `url_title`과 `filename`이 내부 컨텍스트와 turn state artifact 양쪽에 남는지 검증했다.
  - 기존 `test_tool_call_trace_result_summary_preserves_typed_artifact_ids` 기대값을 새 계약에 맞춰 typed ID와 공통 `id`가 함께 보존되는지 확인하도록 갱신했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_builder.py::test_build_router_context_preserves_tool_trace_url_and_file_titles -q`(`1 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_builder.py -q`(`94 passed`)와 `python3 -m pytest tests/test_bot_helpers.py -k "tool_trace or turn_state_artifacts" -q`(`6 passed, 204 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1396 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 새 에이전트 실행 대상 복원 규칙 문서화

- 작업 이름: 새 에이전트가 실행 대상 ID/URL을 읽을 때 resolved 슬롯을 최종값으로 쓰는 공통 계약을 계획 문서에 고정
- 진행상황: 완료
- 진행내용:
  - 현재 코드와 문서를 다시 점검하면서, `agents/common.py`의 `resolved_or_linked_artifact_ids()`와 `resolved_or_linked_urls()` 구현 및 테스트는 이미 추가되어 있지만, 새 에이전트 개발자가 따라야 할 문서 규칙은 더 직접적인 표현이 필요하다고 판단했다.
  - `plan.md`의 후속 맥락 실행 원칙에 “`ExecutionContext.resolved_slots`는 최종 실행값이고, linked state slots/artifacts는 resolved 값이 없을 때만 fallback”이라는 규칙을 추가했다.
  - ID/URL 대상 추출은 에이전트별 로컬 병합 helper가 아니라 공통 helper를 사용하도록 명시했다.
  - boolean이나 잘못된 값이 실행 ID로 변환되지 않아야 하며, 새 artifact 종류를 추가할 때 `ARTIFACT_ID_SLOT_KEYS_BY_KIND`, `agent_catalog.json`, route validation, 실행 에이전트 테스트를 함께 갱신해야 한다는 계약을 문서에 남겼다.
  - 검증 중 `agent_registry.py`의 `FACT_CONTEXT_SLOT_KEYS`에는 단수 파일명 키가 포함되어 있지만 registry 내부 `INTERNAL_ACTION_CONTEXT_KEYS`에는 빠져 있어 정적 계약 테스트가 실패하는 것을 확인했다.
  - `agent_registry.py`에도 `TURN_STATE_ID_SLOT_KEYS`와 `INTERNAL_ACTION_CONTEXT_KEYS`를 명시하고, `FACT_CONTEXT_SLOT_KEYS`를 두 집합의 조합으로 만들도록 정리해 파일명/첨부명 단서 계약을 일관화했다.
  - `test_registry_context_key_sets_match_runtime_context_key_sets`를 추가해 registry의 내부 행동 컨텍스트 키/turn state ID 키 집합이 실제 런타임 `bot.py` 키 집합과 직접 일치하는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py -q`(`93 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_agent_common.py tests/test_agent_registry.py tests/test_response_composer.py -q`(`148 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1397 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 같은 위치 다중 재시도 후보 확인 회귀 테스트 추가

- 작업 이름: 같은 대화 위치에 재시도 가능한 실패 작업이 여러 개 있을 때 `다시해봐`를 최신 하나로 자동 실행하지 않고 후보 확인으로 전환하는지 고정
- 진행상황: 완료
- 진행내용:
  - 교차 위치에 재시도 후보가 여러 개 있을 때는 이미 확인 질문으로 전환하는 매트릭스가 있었지만, 같은 위치의 다중 후보도 같은 원칙으로 보호되는지 직접 테스트가 필요했다.
  - `multiple_current_location_retry_candidates_asks_which_one` 케이스를 `tests/test_context_routing_matrix.py`에 추가했다.
  - 이 케이스는 같은 DM 안에 실패한 날씨 조회와 실패한 웹검색이 모두 있는 상태에서 사용자가 `다시해봐`라고 말하면, 특정 후보를 임의 실행하지 않고 `pending_candidate_state_ids=[21, 30]`를 가진 `clarify`로 전환되는지 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q -k "multiple_current_location_retry_candidates"`(`1 passed, 200 deselected`)를 통과했다.
  - 라우팅 매트릭스 전체 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`201 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1398 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 긍정 접두어 목록 요청의 pending 오승인 방지 회귀 테스트 추가

- 작업 이름: pending 후속 확인이 열린 상태에서 `응 확인 목록 보여줘`가 오래된 작업 승인으로 소비되지 않도록 라우팅 매트릭스에 고정
- 진행상황: 완료
- 진행내용:
  - 실제 대화에서는 봇의 확인 질문 뒤에 사용자가 `응 확인 목록 보여줘`처럼 긍정 표현과 새 요청을 섞어 말할 수 있다.
  - 이 문장은 `그거 완료했어` 같은 오래된 pending 요청 승인이 아니라 현재 문장의 `list_memory` 새 요청으로 처리되어야 한다.
  - `positive_prefix_memory_list_request_does_not_approve_pending_context` 케이스를 `tests/test_context_routing_matrix.py`에 추가했다.
  - 이 케이스는 pending context가 `manage_task` 완료 요청을 들고 있어도 `응 확인 목록 보여줘`는 `context_link=none`, `linked_state_id=None`, 빈 `resolved_slots`의 `list_memory`로 유지되는지 검증한다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q -k "positive_prefix_memory_list_request"`(`1 passed, 201 deselected`)를 통과했다.
  - 라우팅 매트릭스 전체 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`202 passed`)를 통과했다.

## 2026-06-08 - 웹 URL 제목 기반 링크 선택 슬롯 보존 보강

- 작업 이름: URL 제목으로 웹 결과 링크를 선택한 경우 실행 슬롯에도 `url_title/url_titles`를 보존하도록 수정
- 진행상황: 완료
- 진행내용:
  - 전체 검증 중 `web_result_title_open_uses_matching_url_title` 케이스가 URL은 복원하지만 `url_title/url_titles`를 잃는 문제를 드러냈다.
  - `matched_web_url_artifact_slots()`가 매칭 URL만 반환하고 같은 artifact의 제목 단서를 버리고 있음을 확인했다.
  - `web_url_artifact_title_for_url()` helper를 추가해 URL과 정렬된 `url_title/url_titles`, 단일 URL artifact의 공유 `title/name`을 실행 슬롯으로 함께 복원하도록 했다.
  - 라우터 테스트 기대값도 새 계약에 맞춰, 전체 URL 목록을 여는 경우와 특정 제목으로 URL을 고르는 경우 모두 제목 슬롯을 보존하는지 확인하도록 했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q -k "web_result_title_open_uses_matching_url_title or positive_prefix_memory_list_request"`(`2 passed, 201 deselected`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_router_agent.py -q`(`390 passed`), `python3 -m ruff check assistant_bot/agents/router.py tests/test_context_routing_matrix.py tests/test_router_agent.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1400 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 파일명 슬롯 카탈로그 계약 보강

- 작업 이름: 새 에이전트가 facts에 단수 파일명/첨부명 단서를 남길 때 카탈로그 선언을 강제하도록 수정
- 진행상황: 완료
- 진행내용:
  - 새 에이전트 추가 시 맥락 계약이 자동으로 깨지는지 점검하면서, `filename`, `attachment_name`은 실제 후속 대상 슬롯으로 쓰이지만 `FACT_CONTEXT_SLOT_KEYS`에 빠져 있어 facts에 들어가도 카탈로그 선언 누락을 잡지 못할 수 있음을 확인했다.
  - `agent_registry.py`의 facts 맥락 슬롯 계약에 `filename`, `attachment_name`을 추가했다.
  - 동일한 슬롯 집합이 turn state/internal action context와 일치해야 하므로 `bot.py`의 `INTERNAL_ACTION_CONTEXT_KEYS`에도 단수 파일명/첨부명 키를 추가했다.
  - `test_catalog_target_slot_contract_matches_runtime_context_sets`에 `CATALOG_TARGET_SLOT_NAMES <= FACT_CONTEXT_SLOT_KEYS` 검증을 추가해 target slot으로 쓰는 키가 facts 계약에서도 빠지지 않도록 고정했다.
  - 이로써 새 문서/파일 관련 에이전트가 `facts={"filename": ...}` 또는 `facts={"attachment_name": ...}`를 반환하면서 `agent_catalog.json`에 `slots.filename`, `slots.attachment_name`을 선언하지 않으면 테스트나 런타임 계약 검증에서 잡힌다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py -q`(`92 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_bot_helpers.py -q`(`210 passed`), `python3 -m pytest tests/test_context_builder.py -q`(`94 passed`), `python3 -m pytest tests/test_document_analysis_agent.py tests/test_memory_store.py -q`(`136 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1396 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - URL 제목 후속 대상 동등 비교 보강

- 작업 이름: pending context 승인 검증에서 `url_title`과 `url_titles`를 같은 대상 슬롯으로 비교하도록 수정
- 진행상황: 완료
- 진행내용:
  - route validation을 점검하면서 `url_title/url_titles`는 target slot으로 수집되고 카탈로그에도 선언되어 있지만, pending context 승인 비교의 단수/복수 동등 키 목록에는 빠져 있음을 확인했다.
  - 이 상태에서는 라우터가 한쪽에는 `url_title`, 다른 한쪽에는 `url_titles`를 복원한 경우 같은 링크 제목을 가리켜도 pending context 승인 흐름이 불필요하게 어긋날 수 있었다.
  - `equivalent_pending_slot_key()`에 `url_title <-> url_titles` 동등 관계를 추가했다.
  - `slot_values_equivalent()`의 텍스트 정규화 비교 대상에도 `url_title`, `url_titles`를 추가했다.
  - `test_pending_context_approval_accepts_equivalent_normalized_text_slots`에 URL 제목 단수/복수 양방향 케이스를 추가해 “OpenAI Models”처럼 제목으로 링크를 다시 가리키는 후속 요청이 안정적으로 비교되도록 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_accepts_equivalent_normalized_text_slots -q`(`1 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_route_validation.py -q`(`201 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`200 passed`), `python3 -m pytest tests/test_agent_registry.py::test_catalog_target_slot_contract_matches_runtime_context_sets -q`(`1 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1397 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 검색어 단수/복수 후속 대상 동등 비교 보강

- 작업 이름: pending context 승인 검증에서 `query`와 `queries`를 같은 검색 대상 슬롯으로 비교하도록 수정
- 진행상황: 완료
- 진행내용:
  - URL 제목 단수/복수 보강 이후 같은 계열의 슬롯을 점검하면서, 웹 검색 결과와 카탈로그는 `query`와 `queries`를 함께 쓰지만 pending context 승인 비교에는 `query <-> queries` 동등 관계가 없음을 확인했다.
  - 이 상태에서는 pending 쪽이 `query="OpenAI 모델"`이고 라우터가 다음 턴에서 `queries=["OpenAI 모델"]`로 복원한 경우 같은 검색 대상을 가리켜도 확인 흐름이 어긋날 수 있었다.
  - `equivalent_pending_slot_key()`에 `query <-> queries` 동등 관계를 추가했다.
  - `slot_values_equivalent()`의 텍스트 정규화 비교 대상에도 `queries`를 추가했다.
  - `test_pending_context_approval_accepts_equivalent_normalized_text_slots`에 `query`와 `queries` 양방향 케이스를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_route_validation.py::test_pending_context_approval_accepts_equivalent_normalized_text_slots -q`(`1 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_route_validation.py -q`(`201 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`201 passed`), `python3 -m pytest tests/test_web_search_agent.py -q`(`31 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1398 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 웹 결과 제목 기반 URL 복원 최종 검증

- 작업 이름: 웹 검색 결과 제목으로 링크를 여는 후속 요청에서 선택 URL과 제목 슬롯을 함께 유지하도록 최종 보강
- 진행상황: 완료
- 진행내용:
  - `OpenAI Models 열어줘`처럼 사용자가 직전 웹 검색 결과의 제목을 가리켜 링크 열기를 요청하면 URL은 복원되지만 `url_title/url_titles`가 빠지는 회귀를 라우팅 매트릭스에 고정했다.
  - `resolved_slots_for_base_intent()`의 `web_url` 빠른 경로가 제목 복원 helper를 우회하던 문제를 수정해, 제목으로 URL을 고른 경우 `matched_web_url_artifact_slots()`를 통해 선택 URL과 선택 제목을 함께 반환하도록 했다.
  - 여러 URL을 그대로 여는 fallback에서도 artifact의 `url_titles`를 함께 보존해 다음 턴의 링크 대상 비교와 사용자-facing 응답이 제목 단서를 잃지 않도록 했다.
  - `tests/test_router_agent.py`의 기존 웹 URL fallback 기대값을 새 계약에 맞춰 갱신했고, 전체 URL 목록을 여는 경우에는 제목 목록 전체를, 특정 제목으로 URL을 고르는 경우에는 선택 제목만 보존하도록 명시했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q -k "web_result_title_open_uses_matching_url_title"`(`1 passed, 202 deselected`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`203 passed`), `python3 -m pytest tests/test_route_validation.py -q`(`201 passed`), `python3 -m pytest tests/test_web_search_agent.py -q`(`31 passed`), `python3 -m pytest tests/test_router_agent.py -q -k "artifact_urls_array_for_web_url_slots or artifact_url_title_to_choose_specific_url or keeps_url_titles_aligned"`(`3 passed, 184 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1400 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 짧은 후속 재시도와 교차 위치 분리 검증

- 작업 이름: `아 다시해봐`류의 짧은 후속 표현과 교차 위치 날씨 재시도 정책이 함께 안정적으로 동작하는지 재검증
- 진행상황: 완료
- 진행내용:
  - 목표의 핵심인 “이전 맥락을 잘 잇되, 무관한 새 요청은 엮지 않기” 관점에서 라우터, context builder, route validation 구조를 재확인했다.
  - 현재 구조는 같은 위치의 명확한 후속 표현은 자동 연결하고, 다른 위치 후보는 명확한 후속 표현이어도 먼저 사용자 확인으로 바꾸도록 되어 있음을 확인했다.
  - 내부 행동 기록은 현재 위치 로그와 다른 위치 로그를 구분해, 다른 위치 로그가 현재 위치 요청을 차단하지 않도록 `location_priority=cross_location`과 `context_policy=background_only_ask_before_execute_when_follow_up` 단서를 포함한다.
  - 사용자가 실제로 겪었던 날씨 재시도류 문제와 가까운 회귀군을 좁혀 `python3 -m pytest tests/test_context_routing_matrix.py -q -k "weather_retry or cross_location_new_weather_location or cross_location_weather_retry"`(`8 passed, 195 deselected`)로 검증했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1400 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했다.

## 2026-06-08 - 내부 행동 기록의 문서 파일명 슬롯 보존 보강

- 작업 이름: 문서/파일 후속 요청이 내부 행동 기록에서도 파일명과 첨부명 단서를 잃지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 라우팅 검증층은 `filename/filenames/attachment_name/attachment_names`를 문서 대상 구분의 핵심 슬롯으로 사용하지만, 내부 action artifact summary는 문서 ID와 제목만 구조화해 남기고 파일명/첨부명 슬롯은 별도 보존하지 않는 점을 확인했다.
  - `safe_internal_action_artifact_values()`에서 document artifact의 `filename`, `filenames`, `attachment_name`, `attachment_names`를 각각 `filenames`, `attachment_names`로 보존하도록 했다.
  - `parse_internal_action_artifact_slots()`가 내부 action 기록의 `filenames`, `attachment_names`를 읽고, 단일 값일 때 `filename`, `attachment_name`도 함께 복원하도록 했다.
  - `internal_action_context_by_linked_state()` 통합 테스트를 갱신해 문서 분석 결과 내부 기록에서 `document_id`뿐 아니라 `filename/filenames/attachment_name/attachment_names`까지 라우터 슬롯으로 합쳐지는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py -q -k "artifact_outputs_are_available_for_internal_action_context or artifact_outputs_are_preserved_from_items_to_internal_context or item_artifact_kind_is_inferred"`(`3 passed, 90 deselected`), `python3 -m pytest tests/test_router_agent.py -q -k "internal_action_artifact_slots_cover_known_artifact_outputs"`(`1 passed, 186 deselected`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_agent_registry.py -q`(`93 passed`), `python3 -m pytest tests/test_router_agent.py -q`(`187 passed`), `python3 -m pytest tests/test_context_builder.py -q`(`94 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1400 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 내부 artifact 파일명 기반 문서 후속 라우팅 회귀 테스트 추가

- 작업 이름: 내부 행동 기록의 `artifacts`에만 남은 문서 파일명 단서가 실제 후속 라우팅 연결까지 이어지는지 고정
- 진행상황: 완료
- 진행내용:
  - 이전 보강으로 내부 action artifact summary가 `filenames`, `attachment_names`를 보존하게 되었지만, 실제 `parse_state_candidates()`와 `context_aware_fallback_route()` 경로에서 그 단서가 문서 후속 요청 연결에 쓰이는지 직접 회귀 테스트가 필요했다.
  - `test_router_fallback_enriches_document_filename_slots_from_internal_action_artifacts`를 추가했다.
  - 이 케이스는 현재 작업 상태 후보에는 문서 ID/파일명이 없고, 최근 내부 행동 기록의 `artifacts={'document_ids': [7], 'filenames': ['contract.pdf'], 'attachment_names': ['contract.pdf']}`에만 대상 단서가 있는 상태를 재현한다.
  - 사용자가 `contract.pdf 다시 요약해줘`라고 하면 라우터 후보 슬롯에 `document_id/document_ids/filename/filenames/attachment_name/attachment_names`가 병합되고, `analyze_document`가 `context_link=continue`, `linked_state_id=21`로 이어지는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py -q -k "document_filename_slots_from_internal_action_artifacts"`(`1 passed, 187 deselected`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_router_agent.py -q`(`188 passed`), `python3 -m pytest tests/test_agent_registry.py -q`(`93 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`203 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1401 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 파일명 포함 일반 정보 질문의 문서 후속 과연결 방지

- 작업 이름: `contract.pdf 분석 방법 알려줘` 같은 일반 정보 질문이 최근 문서 분석 실행으로 오판되지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - 내부 행동 기록과 문서 artifact 파일명 단서를 강화한 뒤, 파일명이 현재 메시지와 직접 일치하면 `분석`이라는 단어만으로 최근 문서 분석 상태에 과하게 연결될 수 있는지 점검했다.
  - 실제로 `contract.pdf 분석 방법 알려줘`가 일반적인 방법 질문인데도 `analyze_document`의 `retry/continue` 흐름으로 붙는 문제를 확인했다.
  - `is_document_general_information_request()`를 추가해 문서/파일 마커와 `방법`, `가이드`, `절차`, `요령`, `설정` 같은 일반 정보 질문 마커가 함께 있으면 generic 문서 분석/조회 요청으로 보지 않도록 했다.
  - `document_candidate_matches_general_information_request()`를 추가해 파일명/문서명 매칭만으로 일반 정보 질문이 기존 문서 후보에 연결되지 않도록 했다.
  - `document_filename_analysis_method_request_does_not_continue_document` 매트릭스 케이스를 추가해 `contract.pdf 분석 방법 알려줘`가 최근 `contract.pdf` 문서 후보와 연결되지 않고 `chat`, `context_link=none`으로 남는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q -k "document_filename_analysis_method_request"`(`1 passed, 203 deselected`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q -k "document"`(`28 passed, 176 deselected`), `python3 -m pytest tests/test_router_agent.py -q -k "document or filename or attachment"`(`12 passed, 176 deselected`), `python3 -m pytest tests/test_route_validation.py -q -k "document or filename or attachment"`(`15 passed, 186 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1403 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 할 일/알림 시간 슬롯 내부 라우팅 계약 보강

- 작업 이름: 내부 행동 기록의 기한/알림 시각 단서가 라우터 후보 슬롯과 target hint로 이어지도록 수정
- 진행상황: 완료
- 진행내용:
  - `manage_task`, `manage_reminder` 카탈로그와 에이전트 결과는 `due_at`, `human_due_at`, `remind_at`, `human_remind_at`을 후속 맥락 단서로 선언하고 보존하지만, 라우터의 `SAFE_INTERNAL_ROUTE_SLOT_KEYS`에는 이 시간 슬롯들이 빠져 있음을 확인했다.
  - 이 상태에서는 내부 action result에 사람 읽기 좋은 기한/알림 시각이 남아도 라우터가 내부 기록을 다시 후보 슬롯으로 병합할 때 시간 단서를 버릴 수 있었다.
  - `assistant_bot/agents/router.py`의 안전 병합 슬롯에 `due_at`, `human_due_at`, `remind_at`, `human_remind_at`을 추가했다.
  - `assistant_bot/agent_registry.py`의 `CONTEXT_TARGET_SLOT_KEYS`와 `assistant_bot/context_builder.py`의 `TURN_STATE_TARGET_HINT_SLOT_KEYS`에도 같은 시간 슬롯을 추가해 카탈로그, turn state target hint, 내부 action route merge 계약을 일치시켰다.
  - `test_router_parses_internal_action_result_slots_without_route_resolved_slots`를 갱신해 task 내부 action 기록에서 `due_at/human_due_at`이 보존되는지 확인했다.
  - `test_router_preserves_reminder_time_slots_from_internal_action_result`를 추가해 reminder 내부 action 기록에서 `remind_at/human_remind_at`이 라우터 후보 슬롯으로 살아나는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py -q -k "internal_action_result_slots_without_route_resolved_slots or preserves_reminder_time_slots"`(`2 passed, 187 deselected`)를 통과했다.
  - 관련 계약 검증으로 `python3 -m pytest tests/test_agent_registry.py -q -k "target_slot_outputs_are_visible_in_turn_state_hints or target_slot_outputs_are_preserved_from_facts_to_turn_state_slots or target_slot_outputs_are_preserved_from_resolved_slots_to_turn_state_slots or target_slot_contract"`(`4 passed, 91 deselected`), `python3 -m pytest tests/test_context_builder.py -q -k "target_hints"`(`9 passed, 85 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1406 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 저장된 알림/할 일 시간 회상형 후속 요청 연결 보강

- 작업 이름: `그 알림 몇시에 오기로 했지?`, `그 할 일 기한 언제였지?` 같은 시간 회상 질문을 현재 시간 질문과 분리해 기존 항목으로 연결
- 진행상황: 완료
- 진행내용:
  - 시간 슬롯 계약 보강 이후 실제 라우팅을 재현하면서, `내가 아까 몇시에 알림 보내달라고 했지?`는 알림 후보에 연결되지만 `그 알림 몇시에 오기로 했지?`는 `current_time`으로 빠지고, `그 할 일 기한 언제였지?`와 `병원 예약 언제까지였지?`는 기존 할 일 후보에 연결되지 않는 문제를 확인했다.
  - 라우터에 `route_from_time_recall_candidate()` 경로를 추가해 reminder/task 후보의 시간 회상 질문을 별도로 처리하도록 했다.
  - `reminder_time_recall_request()`, `task_due_time_recall_request()`를 추가해 현재 시간 질문과 저장된 항목의 알림/기한 확인 질문을 분리했다.
  - 선택된 후보가 있으면 `reminder_id` 또는 `task_id`와 함께 `remind_at/human_remind_at`, `due_at/human_due_at`을 resolved slot에 함께 복원하도록 했다.
  - `reminder_pronoun_time_recall_uses_recent_reminder`, `task_pronoun_due_time_recall_uses_recent_task`, `task_title_due_time_recall_uses_matching_task` 매트릭스 케이스를 추가했다.
  - 재현 확인 결과 `그 알림 몇시에 오기로 했지?`는 `manage_reminder`, `그 할 일 기한 언제였지?`와 `병원 예약 언제까지였지?`는 `manage_task`로 이어지고, 각 resolved slot에 사람이 읽기 좋은 시간 단서가 함께 남는 것을 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q -k "time_recall_uses"`(`3 passed, 209 deselected`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`212 passed`), `python3 -m pytest tests/test_router_agent.py -q`(`189 passed`), `python3 -m pytest tests/test_route_validation.py -q -k "current_time or reminder or task"`(`26 passed, 175 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1415 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 목록 후보의 선택 항목 시간 슬롯 복원 보강

- 작업 이름: 할 일/알림 목록에서 특정 항목을 시간 회상 질문으로 좁혔을 때 선택된 artifact의 시간까지 resolved slot에 복원
- 진행상황: 완료
- 진행내용:
  - 단일 할 일/알림 후보의 시간 회상은 보강됐지만, `할 일 목록`, `알림 목록`처럼 여러 artifact가 있는 후보에서는 `오전 회신 언제까지였지?`, `물 마시기 알림 언제였지?`가 항목 ID만 복원하고 `due_at/human_due_at`, `remind_at/human_remind_at`은 빠지는 문제를 재현했다.
  - `time_recall_resolved_slots()`가 후보 전체의 시간값이 유일할 때만 시간 슬롯을 추가하던 방식을 보완했다.
  - `add_matched_candidate_time_slot()`과 `artifact_time_value_for_identifier()`를 추가해, `task_id` 또는 `reminder_id`로 좁혀진 항목과 같은 artifact에 들어 있는 시간 슬롯을 찾아 resolved slot에 함께 복원하도록 했다.
  - `task_list_time_recall_restores_matched_artifact_due_time`과 `reminder_list_time_recall_restores_matched_artifact_remind_time` 매트릭스 케이스를 추가했다.
  - 재현 확인 결과 `오전 회신 언제까지였지?`는 `task_id=3`과 `오늘 오전 9시`, `물 마시기 알림 언제였지?`는 `reminder_id=5`와 `오늘 오전 7시 4분`을 함께 복원하는 것을 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q -k "list_time_recall_restores"`(`2 passed, 212 deselected`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`214 passed`), `python3 -m pytest tests/test_router_agent.py -q`(`189 passed`), `python3 -m pytest tests/test_route_validation.py -q -k "task or reminder or current_time"`(`26 passed, 175 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1417 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 내부 행동 기록 주입/비공개 응답 감사

- 작업 이름: 사용자에게 보이지 않는 내부 행동 기록이 라우터와 에이전트 판단에는 들어가고 사용자 응답에는 원문으로 새지 않는지 감사
- 진행상황: 완료
- 진행내용:
  - 목표의 두 번째 축인 “에이전트가 사용자에게 보이지 않는 내부 행동도 기록해서 컨텍스트에서 참고” 항목을 기준으로 `AgentLogStore`, `build_router_context()`, `ExecutionContext.for_agent()`, `ExecutionContext.for_response()` 경로를 확인했다.
  - 라우터 컨텍스트는 `최근 내부 행동 기록` 섹션에 route validation, result log, tool trace, target hints, validation guidance를 포함한다.
  - 에이전트 컨텍스트는 내부 행동 기록을 대상/상태/주의사항 중심으로 축약하고, `route_context`, `validation_context`, `linked_state_id`, `pending_original_text` 같은 내부 라우팅 원문은 제거한다.
  - 응답 컨텍스트와 응답 composer는 내부 행동 기록을 비공개 참고 정보로만 쓰도록 하고, 모델 출력에 내부 키가 섞여도 후처리에서 제거하는 테스트가 있음을 확인했다.
  - 공유 채널/교차 위치에서는 `user_id` 기준으로 내부 로그를 분리하고, `user_id` 없는 레거시 로그는 사용자 ID가 conversation_id에 포함된 개인 대화에서만 허용하는 계약을 확인했다.
  - 확인한 대표 테스트 증거: `test_build_router_context_includes_recent_internal_action_logs`, `test_build_router_context_excludes_other_user_internal_logs_in_same_channel`, `test_runtime_agent_logs_always_include_user_id`, `test_response_composer_treats_internal_action_context_as_hidden_reference`, `test_execution_context_agent_context_hides_raw_route_diagnostics_but_keeps_target_hints`, `test_execution_context_hides_route_validation_current_message_diagnostics_from_agent_and_response`.
  - 새 결함은 발견하지 못했으나, 목표 완료 판정에는 실제 Discord 환경에서 내부 로그가 다음 턴 라우팅에 반영되는 수동 검증이 아직 필요하다.

## 2026-06-08 - on_message 2턴 맥락 저장/재주입 통합 테스트 추가

- 작업 이름: 실제 Discord 메시지 처리 흐름에서 첫 턴 작업 결과가 다음 턴 라우터 컨텍스트로 들어오는지 고정
- 진행상황: 완료
- 진행내용:
  - 목표 완료 감사에서 가장 중요한 런타임 흐름은 `on_message()`가 작업을 처리한 뒤 대화 메시지, turn state, 내부 행동 로그를 저장하고, 다음 사용자 메시지 라우팅 시 그 기록을 `conversation_context`에 다시 넣는 것이다.
  - `test_on_message_next_turn_router_receives_recorded_state_and_internal_log`를 추가했다.
  - 테스트는 첫 메시지 `병원 예약 할 일 추가해줘`를 처리해 `할 일 3 병원 예약` 결과를 만들고, 두 번째 메시지 `방금 할 일 보여줘`의 라우터 입력 컨텍스트에 최근 대화, 최근 작업 상태 후보, task artifact, 내부 행동 로그, request, target hints가 모두 들어오는지 검증한다.
  - 이로써 단위 helper가 아니라 실제 `AssistantBot.on_message()` 경로에서 저장된 내부 행동 기록과 작업 상태가 다음 턴 맥락 판단 자료로 재주입되는 계약을 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_bot_helpers.py::test_on_message_next_turn_router_receives_recorded_state_and_internal_log -q`(`1 passed`)를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_bot_helpers.py -q`(`211 passed`), `python3 -m pytest tests/test_context_builder.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q`(`498 passed`), `python3 -m ruff check tests/test_bot_helpers.py`를 통과했다.

## 2026-06-08 - 목표 완료 Discord 수동 검증 기준 문서화

- 작업 이름: 맥락 파악 목표를 완료로 볼 실제 Discord 수동 검증 체크리스트 추가
- 진행상황: 완료
- 진행내용:
  - 자동 테스트는 충분히 넓어졌지만, 목표 자체가 “거의 완벽에 가까운 맥락 파악”이므로 실제 Discord 환경에서 어떤 시나리오를 통과해야 완료인지 명확한 판정표가 필요했다.
  - `plan.md`에 `목표 완료 수동 검증 기준` 섹션을 추가했다.
  - 체크리스트는 같은 위치 후속 요청, 새 요청 분리, 다른 위치 맥락 확인, 내부 행동 기록 재사용, pending/버튼 확인, 메모 대기, 파일/이미지 흐름을 포함한다.
  - 하나라도 실패하면 목표 완료가 아니라 추가 수정 대상으로 보고, 수동 검증 결과를 `process.md`에 시나리오, 실제 응답, 판정, 후속 수정 여부와 함께 기록하도록 명시했다.

## 2026-06-08 - 문서 파일명 포함 일반 정보 질문 분리 회귀 검증

- 작업 이름: `contract.pdf 분석 방법 알려줘`를 저장 문서 후속 분석이 아니라 일반 정보 질문으로 분리
- 진행상황: 완료
- 진행내용:
  - 수동 검증 기준 추가 후 맥락 매트릭스를 다시 실행하면서 `document_filename_analysis_method_request_does_not_continue_document` 실패를 확인했다.
  - 이 문장은 파일명과 `분석`이라는 단어가 포함되어 있지만, 핵심 의도는 저장된 문서 분석이 아니라 `분석 방법`에 대한 일반 정보 질문이다.
  - 라우터 fallback의 문서 후보 연결 경로에서 `is_document_general_information_request()`와 `document_candidate_matches_general_information_request()`가 이런 문장을 저장 문서 후보에 붙이지 않도록 하는 계약을 확인하고, 매트릭스 회귀를 재검증했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q -k "document_filename_analysis_method"`(`1 passed, 203 deselected`)를 통과했다.
  - 전체 맥락 매트릭스 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`204 passed`)를 통과했다.
  - 관련 라우터 회귀 검증으로 `python3 -m pytest tests/test_router_agent.py -q -k "general_information or document_filename or document_general"`(`1 passed, 187 deselected`)와 `python3 -m ruff check assistant_bot/agents/router.py tests/test_context_routing_matrix.py`를 통과했다.

## 2026-06-08 - 에이전트 카탈로그와 라우팅 후속 액션 계약 보강

- 작업 이름: 새 에이전트 추가 시 카탈로그와 맥락 라우팅 검증 규칙이 어긋나는 문제를 자동으로 감지
- 진행상황: 완료
- 진행내용:
  - 목표의 핵심인 “앞으로 에이전트를 추가해도 이전 맥락과 새 요청을 안정적으로 구분”하려면 각 에이전트가 남기는 `available_actions`와 라우팅 검증기가 이해하는 후속 액션 계약이 서로 맞아야 한다.
  - 기존 테스트는 대표 intent 몇 개의 `state_outputs`만 손으로 확인했기 때문에, 나중에 새 액션이나 새 에이전트를 추가하면서 `INTENT_ACTIONS`에는 넣고 카탈로그에는 빠뜨리는 실수를 놓칠 수 있었다.
  - `test_agent_catalog_covers_route_validation_follow_up_actions`를 추가해 `INTENT_ACTIONS`의 후속 액션이 카탈로그 `available_actions.*` 또는 `VALIDATION_ONLY_INTENT_ACTIONS`에 반드시 드러나도록 했다.
  - `test_agent_catalog_available_actions_use_known_context_action_vocabulary`를 추가해 카탈로그에 오타나 검증기가 모르는 액션명이 들어가면 실패하도록 했다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_agent_catalog_covers_route_validation_follow_up_actions tests/test_agent_registry.py::test_agent_catalog_available_actions_use_known_context_action_vocabulary -q`(`2 passed`)와 `python3 -m ruff check tests/test_agent_registry.py`를 통과했다.
  - 기존 카탈로그 target slot 테스트가 `due_at`, `human_due_at`, `remind_at`, `human_remind_at` 샘플을 갖고 있지 않아 실패하던 부분도 보완했다. 이로써 할 일/알림 시간 단서가 turn state target hint와 슬롯 보존 경로에서 유지되는지도 함께 검증한다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_agent_registry.py -q`(`95 passed`)와 `python3 -m ruff check tests/test_agent_registry.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1406 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 고빈도 유틸리티/복구/검색확인 intent 맥락 매트릭스 보강

- 작업 이름: 이전 작업 상태 후보가 있어도 명확한 새 유틸리티/복구/검색확인 요청이 빼앗기지 않도록 회귀 고정
- 진행상황: 완료
- 진행내용:
  - 맥락 라우팅 매트릭스가 대부분의 전문 intent를 다루고 있었지만, `help`, `daily_briefing`, `reset_context`, `restore_memory`, `confirm_web_search`는 직접 등장하지 않았다.
  - 이 intent들은 사용자가 새 요청으로 자주 보내는 기능이므로, 최근 할 일이나 문서 후보가 남아 있을 때도 이전 후보에 연결되지 않고 원래 intent로 유지되는지 고정할 필요가 있었다.
  - `help_request_not_stolen_by_previous_task`, `daily_briefing_request_not_stolen_by_previous_task`, `reset_context_request_not_stolen_by_previous_task`, `deleted_memory_list_request_not_stolen_by_previous_task`, `confirm_web_search_request_not_stolen_by_previous_document` 케이스를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py::test_context_routing_matrix -q -k "not_stolen_by_previous or deleted_memory_list_request"`(`5 passed, 204 deselected`)와 `python3 -m ruff check tests/test_context_routing_matrix.py`를 통과했다.
  - 전체 맥락 매트릭스 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`209 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1411 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 카탈로그 intent 맥락 매트릭스 커버리지 계약 추가

- 작업 이름: 새 에이전트 intent 추가 시 맥락 매트릭스 회귀 누락을 자동 감지
- 진행상황: 완료
- 진행내용:
  - 목표의 핵심은 새 에이전트를 추가해도 이전 맥락과 새 요청 분리 정책이 무너지지 않는 것이다.
  - 이를 위해 `agent_catalog.json`에 등록된 실행 가능한 intent가 `tests/test_context_routing_matrix.py`에 최소 한 번은 등장해야 한다는 계약을 추가했다.
  - `test_context_routing_matrix_covers_every_actionable_catalog_intent`와 `context_routing_matrix_intents()` helper를 추가했다.
  - `unsupported`는 보통 capability check 이후 실행 단계에서 만들어지는 결과라, 맥락 후속 라우팅 매트릭스 직접 커버리지 예외로 두었다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py::test_context_routing_matrix_covers_every_actionable_catalog_intent -q`(`1 passed`)와 `python3 -m ruff check tests/test_agent_registry.py`를 통과했다.
  - 관련 회귀 검증으로 `python3 -m pytest tests/test_agent_registry.py -q`(`96 passed`), `python3 -m pytest tests/test_context_routing_matrix.py -q`(`212 passed`), `python3 -m ruff check tests/test_agent_registry.py tests/test_context_routing_matrix.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1415 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - Discord 수동 검증 시트 작성

- 작업 이름: 목표 완료 판정을 위한 실제 Discord 검증 절차를 별도 문서로 정리
- 진행상황: 완료
- 진행내용:
  - 목표 완료 기준은 이미 `plan.md`에 있었지만, 실제 Discord에서 순서대로 실행하고 판정하기에는 체크리스트가 길고 기록 양식이 분리되어 있었다.
  - `discord_manual_verification.md`를 추가해 같은 위치 후속 요청, 새 요청 분리, 다른 위치 맥락, 내부 행동 기록 재사용, pending/버튼 확인, 메모 대기, 파일/이미지, 말투/자연스러움 항목을 순서형 표로 정리했다.
  - 각 항목은 입력, 기대 동작, 판정 칸을 포함해 사용자가 직접 봇을 실행한 뒤 결과를 기록할 수 있게 했다.
  - 실패/보류 항목을 `process.md`에 기록하기 위한 템플릿도 포함했다.
  - `plan.md`의 목표 완료 수동 검증 기준에서 이 검증 시트를 참조하도록 했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1417 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - Discord 수동 검증 시트 문서 계약 테스트 추가

- 작업 이름: 목표 완료 수동 검증 시트가 필수 검증 축을 계속 포함하는지 자동 감지
- 진행상황: 완료
- 진행내용:
  - `discord_manual_verification.md`가 만들어졌지만, 이후 수정 과정에서 필수 시나리오나 `plan.md` 참조가 빠져도 자동으로 감지할 수 없었다.
  - `tests/test_manual_verification_doc.py`를 추가해 수동 검증 시트가 같은 위치 후속 요청, 새 요청 분리, 다른 위치 맥락, 내부 행동 기록 재사용, pending/버튼 확인, 메모 대기, 파일/이미지, 말투/자연스러움 섹션을 모두 포함하는지 확인하게 했다.
  - 고위험 실제 입력인 `방금 할 일 보여줘`, `응 서울 날씨 알려줘`, `방금 찾은 문서 다시 요약해줘`, `다음 내용 메모로 남겨줘`, `PDF 첨부 + 이 문서 요약해봐`, `파일 목록 보여줘`, `SleepGPT` 등이 문서에 남아 있는지도 고정했다.
  - `plan.md`가 `discord_manual_verification.md`를 목표 완료 수동 검증 기준으로 계속 참조하는지도 테스트한다.
  - 직접 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py -q`(`3 passed`)와 `python3 -m ruff check tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1420 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - README 검증 섹션에 Discord 수동 검증 게이트 추가

- 작업 이름: 운영 문서에서 목표 완료 수동 검증 시트와 사전 점검 명령을 바로 찾을 수 있게 정리
- 진행상황: 완료
- 진행내용:
  - `README.md`의 검증 섹션이 오래된 테스트 수와 자동 검증 명령만 안내하고 있어, 목표 완료에 필요한 실제 Discord 수동 검증 게이트가 운영 문서에서 드러나지 않았다.
  - 검증 명령을 `python3 -m pytest -q`, `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`로 정리했다.
  - 자동 검증이 모두 통과해도 맥락 파악 목표 완료는 `discord_manual_verification.md` 기준 실제 Discord 검증을 거쳐야 한다고 명시했다.
  - 실패 또는 보류 항목은 `process.md`에 기록하도록 안내했다.
  - Discord 실행 전 사전 점검 명령으로 `assistant-admin route`, `assistant-admin ask`, `assistant-admin turn-states`, `assistant-admin logs`를 안내했다.
  - `tests/test_manual_verification_doc.py`에 README가 이 수동 검증 게이트와 사전 점검 명령을 계속 언급하는지 확인하는 테스트를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py -q`(`4 passed`)와 `python3 -m ruff check tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1421 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - 라우터 artifact 슬롯 보강 범위 정리

- 작업 이름: 목록/시간/순번 기반 후속 요청에서 실행 슬롯과 답변 근거 슬롯을 안정적으로 분리
- 진행상황: 완료
- 진행내용:
  - 전체 회귀 검증 중 `matched_artifact_slots_for_intent()`가 memory/document/task/reminder 후보에 설명용 슬롯을 지나치게 넓게 붙여 일부 라우팅 기대값과 충돌하는 문제를 확인했다.
  - memory/document는 실행 대상 ID 중심으로 유지하고, task/reminder는 제목, 시간, 순번, 변경 요청처럼 실제 대상 식별과 응답 안전성에 필요한 경우에만 `task_title`, `reminder_text`, `due_at`, `human_due_at`, `remind_at`, `human_remind_at`을 보강하도록 정리했다.
  - 단일 후보 시간 조회는 기존 계약대로 ID와 시간만 반환하고, 목록에서 제목/시간으로 특정한 후보나 순번으로 선택한 변경 요청은 대상명도 보존하도록 매트릭스 계약을 맞췄다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py -q`(`214 passed`)와 `python3 -m ruff check assistant_bot/agents/router.py tests/test_context_routing_matrix.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1421 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - README 자동 검증 결과 수 정합성 보강

- 작업 이름: 운영 문서의 자동 검증 통과 수가 실제 전체 테스트 결과와 어긋나지 않도록 고정
- 진행상황: 완료
- 진행내용:
  - 전체 검증 결과가 `1421 passed`인데 `README.md`의 현재 자동 검증 결과가 `테스트 1420개 통과`로 남아 있어, 목표 완료 전 운영 점검 문서와 실제 검증 결과가 어긋나는 지점을 확인했다.
  - README 숫자 검증 테스트와 CLI 수동 검증 상태 테스트를 포함한 최종 전체 테스트 수가 `1424 passed`가 되었으므로, `README.md`의 자동 검증 결과를 `테스트 1424개 통과`로 갱신했다.
  - `tests/test_manual_verification_doc.py`에 README가 최신 테스트 통과 수를 계속 언급하는지 확인하는 계약을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py -q`(`5 passed`)와 `python3 -m ruff check tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1424 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - Discord 수동 검증 완료 판정표 보강

- 작업 이름: 목표 완료 수동 검증 결과를 섹션별로 판정하고 증거 위치를 남길 수 있게 정리
- 진행상황: 완료
- 진행내용:
  - 골모드 목표 완료는 실제 Discord 수동 검증이 필요하지만, 기존 `discord_manual_verification.md`는 개별 시나리오 판정 칸만 있어 전체 완료 여부를 한눈에 판단하기 어려웠다.
  - `discord_manual_verification.md`에 `완료 판정 요약` 표를 추가해 8개 검증 섹션의 최종 판정과 증거 위치를 기록하도록 했다.
  - 모든 항목이 `통과`여야 목표 완료로 볼 수 있고, `실패` 또는 `보류`가 하나라도 있으면 추가 수정 또는 환경 재검증 대상으로 둔다고 명시했다.
  - 증거 위치에는 Discord 메시지 링크, 스크린샷 파일명, 또는 `process.md` 검증 결과 제목을 남기도록 안내했다.
  - `tests/test_manual_verification_doc.py`에 완료 판정 요약 표와 증거 기록 규칙이 계속 남아 있는지 확인하는 테스트를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py -q`(`5 passed`)와 `python3 -m ruff check tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1422 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - Discord 수동 검증 상태 CLI 추가

- 작업 이름: 수동 검증 시트의 완료 가능 여부를 로컬에서 즉시 확인하는 운영 명령 추가
- 진행상황: 완료
- 진행내용:
  - 실제 Discord 검증은 사용자가 직접 수행해야 하지만, 검증표를 채운 뒤 미기입/실패/보류 항목이 남았는지 수동으로 다시 세는 과정은 실수 가능성이 있었다.
  - `assistant-admin verification-status` 명령을 추가해 `discord_manual_verification.md`의 `완료 판정 요약` 표를 읽고 통과, 실패, 보류, 미기입 섹션 수를 출력하도록 했다.
  - 모든 섹션이 `통과`일 때만 exit code 0과 `판정: 완료 가능`을 반환하고, 미기입/실패/보류가 있으면 exit code 1과 남은 섹션 목록을 출력한다.
  - `discord_manual_verification.md`와 `README.md`에 새 명령 사용법을 연결했다.
  - `tests/test_cli.py`에 미기입/실패/보류가 섞인 시트와 모든 섹션이 통과한 시트의 판정 테스트를 추가했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`를 실행하면 8개 섹션이 모두 미기입이라 `판정: 완료 불가`를 반환하는 것을 확인했다.
  - 직접 검증으로 `python3 -m assistant_bot.cli verification-status --help`, `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q`(`92 passed`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1424 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - Discord 수동 검증 진행 순서 보강

- 작업 이름: 목표 완료 수동 검증을 실제 실행 순서대로 따라갈 수 있게 문서화
- 진행상황: 완료
- 진행내용:
  - 자동 검증은 통과했지만, 실제 Discord 검증을 수행할 때 사전 상태 확인, 8개 섹션 실행, 완료 판정 요약 작성, 상태 명령 실행, 실패 기록의 순서가 한곳에 뚜렷하게 모여 있지 않았다.
  - `discord_manual_verification.md`에 `진행 순서` 섹션을 추가해 Discord에서 봇 직접 실행, `assistant-admin route`, `assistant-admin ask`, `assistant-admin turn-states`, `assistant-admin logs` 사전 확인, 8개 섹션 실행, `완료 판정 요약` 작성, `assistant-admin verification-status` 실행, 실패/보류 항목의 `process.md` 기록 흐름을 정리했다.
  - `README.md`의 검증 섹션에도 같은 순서를 짧게 연결해 사용자가 실제 검증 전에 어떤 절차를 따르면 되는지 바로 확인할 수 있게 했다.
  - `tests/test_manual_verification_doc.py`에 진행 순서 문구와 README 절차 문구가 계속 남아 있는지 확인하는 계약 테스트를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py -q`(`6 passed`)와 `python3 -m ruff check tests/test_manual_verification_doc.py`를 통과했다.
  - 전체 테스트 수가 늘어 `README.md`의 현재 자동 검증 결과를 `테스트 1426개 통과`로 갱신했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1426 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`는 8개 섹션 미기입 때문에 `판정: 완료 불가`를 반환하는 것을 다시 확인했다.

## 2026-06-08 - verification-status 필수 8섹션 완료 조건 보강

- 작업 이름: 일부 섹션만 통과한 검증표를 목표 완료로 오판하지 않도록 방지
- 진행상황: 완료
- 진행내용:
  - `assistant-admin verification-status`가 요약 표에 존재하는 행이 모두 `통과`이면 전체 필수 섹션이 빠져 있어도 완료 가능으로 볼 수 있는 빈틈을 확인했다.
  - 목표 완료 기준은 같은 위치 후속 요청, 새 요청 분리, 다른 위치 맥락, 내부 행동 기록 재사용, Pending/버튼 확인, 메모 대기, 파일/이미지, 말투/자연스러움의 8개 섹션 전체 통과이므로 `REQUIRED_MANUAL_VERIFICATION_SECTIONS`를 추가했다.
  - 요약 표에 필수 섹션 행이 없으면 `(요약 표 행 없음)`으로 미기입 항목에 포함하고, 완료 불가로 판정하도록 바꿨다.
  - `tests/test_cli.py`에 일부 섹션만 통과한 검증표가 완료 불가로 처리되는 회귀 테스트를 추가했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 8개 섹션 전체를 미기입으로 보고 `판정: 완료 불가`를 반환하는 것도 재확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py -q -k "manual_verification or verification_status"`(`3 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1425 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - verification-status 통과 증거 위치 필수화

- 작업 이름: 통과 판정만 있고 증거 위치가 빈 검증표를 목표 완료로 오판하지 않도록 방지
- 진행상황: 완료
- 진행내용:
  - 골모드 완료 감사는 테스트 의도뿐 아니라 실제 Discord 증거가 필요하므로, `완료 판정 요약`에서 `통과`로 표시된 섹션도 증거 위치가 비어 있으면 완료 가능으로 보면 안 된다.
  - `assistant-admin verification-status`가 `통과` 행의 증거 위치를 검사하고, 비어 있으면 `증거 누락` 항목으로 표시하며 exit code 1을 반환하도록 보강했다.
  - `discord_manual_verification.md`에 `통과` 항목도 증거 위치가 비어 있으면 목표 완료 증거로 인정하지 않는다고 명시했다.
  - `README.md`의 수동 검증 절차에도 실패, 보류뿐 아니라 증거 누락을 확인하도록 반영했다.
  - `tests/test_cli.py`에 8개 섹션이 모두 `통과`이지만 한 섹션의 증거 위치가 비어 있으면 완료 불가로 처리하는 회귀 테스트를 추가했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 8개 섹션 전체를 미기입으로 보고 `판정: 완료 불가`, `증거 누락: 0`을 반환하는 것을 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py -q -k "manual_verification or verification_status"`(`4 passed, 85 deselected`), `python3 -m pytest tests/test_manual_verification_doc.py -q`(`6 passed`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1427 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - verification-status 증거 형식 검증 보강

- 작업 이름: 임시 문자열을 수동 검증 완료 증거로 오판하지 않도록 방지
- 진행상황: 완료
- 진행내용:
  - 증거 위치가 비어 있지 않아도 `msg-1`, `완료`, `확인함` 같은 임시 문구가 들어가면 실제 Discord 검증 증거로 보기 어렵다.
  - `assistant-admin verification-status`에 증거 형식 검증을 추가해 `통과` 항목의 증거 위치가 Discord/HTTP 링크, 스크린샷 파일명(`.png`, `.jpg`, `.jpeg`, `.webp`, `.heic`), 또는 `process.md` 참조가 아니면 `증거 형식 오류`로 표시하도록 했다.
  - 출력 요약에 `증거 형식 오류` 개수를 추가하고, 후속 조치 문구에도 미기입/증거 누락/증거 형식 오류를 함께 안내하도록 바꿨다.
  - `discord_manual_verification.md`에 임시 문구는 증거 위치로 인정하지 않는다고 명시했고, `README.md`의 수동 검증 절차에도 증거 형식 오류 확인을 추가했다.
  - `tests/test_cli.py`에 `msg-1` 같은 placeholder 증거를 완료 불가로 처리하는 회귀 테스트를 추가했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 8개 섹션 전체를 미기입으로 보고 `증거 형식 오류: 0`, `판정: 완료 불가`를 반환하는 것을 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py -q -k "manual_verification or verification_status"`(`5 passed, 85 deselected`), `python3 -m pytest tests/test_manual_verification_doc.py -q`(`6 passed`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1428 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - verification-status 증거 누락 완료 방지 확인

- 작업 이름: 통과 판정만 있고 증거 위치가 없는 수동 검증표를 완료로 인정하지 않는지 재확인
- 진행상황: 완료
- 진행내용:
  - 목표 완료는 실제 Discord 응답 증거가 필요하므로, `완료 판정 요약`의 최종 판정이 `통과`여도 증거 위치가 비어 있으면 완료 가능으로 보면 안 된다.
  - 현재 `assistant-admin verification-status`가 `통과` 섹션 중 증거 위치가 없는 항목을 `증거 누락`으로 집계하고, `ok=False`와 `판정: 완료 불가`를 반환하는 것을 코드와 테스트에서 확인했다.
  - `discord_manual_verification.md`에는 `통과` 항목도 증거 위치가 비어 있으면 목표 완료 증거로 인정하지 않는다고 명시되어 있고, `README.md`도 실패, 보류, 증거 누락을 `process.md` 기록 대상으로 안내한다.
  - `tests/test_cli.py`의 `test_collect_manual_verification_status_requires_evidence_for_passed_sections`가 파일/이미지 섹션의 증거 위치가 비어 있으면 `증거 누락: 1`과 완료 불가로 처리되는 계약을 고정한다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`10 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1427 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - verification-status 후속 조치 안내 보강

- 작업 이름: 수동 검증 상태 출력에서 다음 기록 행동을 바로 안내
- 진행상황: 완료
- 진행내용:
  - `assistant-admin verification-status`가 미기입, 증거 누락, 증거 형식 오류, 실패, 보류 항목을 잘 보여주지만, 출력 자체에는 다음에 어떤 문서를 채우거나 어디에 실패 내용을 기록해야 하는지 직접 안내하지 않았다.
  - 완료 불가 판정일 때 출력 마지막에 `discord_manual_verification.md`의 `완료 판정 요약`을 채우고, 실패/보류는 `process.md`에 실제 응답과 후속 수정 필요 여부를 기록하라는 후속 조치 문구를 추가했다.
  - 완료 가능 판정에서는 후속 조치 문구를 출력하지 않아, 실제 모든 검증이 통과했을 때 출력이 불필요하게 장황해지지 않도록 했다.
  - `tests/test_cli.py`에서 미기입, 일부 섹션 누락, 증거 누락, 증거 형식 오류 케이스는 후속 조치 문구를 포함하고, 전체 통과 케이스는 포함하지 않는 계약을 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`11 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1428 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - verification-status 판정값 오류 완료 방지

- 작업 이름: 수동 검증표에 허용되지 않은 판정값이 적혀도 완료로 오판하지 않도록 방지
- 진행상황: 완료
- 진행내용:
  - `완료 판정 요약`의 최종 판정 칸에 `완료`, `확인`, `OK`처럼 `통과`, `실패`, `보류`가 아닌 값을 적으면 완료 판정에서 누락될 수 있는지 확인했다.
  - `assistant-admin verification-status`가 `통과`, `실패`, `보류` 외의 비어 있지 않은 판정값을 `판정값 오류`로 집계하고, 완료 불가로 처리하도록 보강했다.
  - 출력 요약과 후속 조치 문구에도 `판정값 오류`를 포함해, 사용자가 잘못 적은 판정값을 `discord_manual_verification.md`에서 바로 고칠 수 있게 했다.
  - `discord_manual_verification.md`에는 최종 판정에 `통과`, `실패`, `보류` 중 하나만 적고, `완료`, `확인`, `OK` 같은 값은 판정값 오류로 본다고 명시했다.
  - `README.md`에도 실패, 보류, 판정값 오류, 증거 누락, 증거 형식 오류가 있으면 `process.md`에 기록해야 한다고 정리했다.
  - `tests/test_cli.py`에 잘못된 판정값 `완료`가 들어간 검증표를 완료 불가로 처리하는 회귀 테스트를 추가했고, `tests/test_manual_verification_doc.py`에 문서 문구 계약을 보강했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`12 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 8개 섹션과 38개 세부 시나리오 미기입 때문에 `판정: 완료 불가`를 반환하고, `판정값 오류: 0`을 함께 표시하는 것을 확인했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1429 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - Discord 수동 검증 세부 시나리오 수 문서 계약 추가

- 작업 이름: 목표 완료 수동 검증이 8개 섹션과 38개 세부 시나리오 전체를 요구한다는 점을 문서와 테스트로 고정
- 진행상황: 완료
- 진행내용:
  - `assistant-admin verification-status`는 현재 `discord_manual_verification.md`에서 8개 섹션과 38개 세부 시나리오를 읽어 모두 채워야 완료 가능으로 판단한다.
  - `discord_manual_verification.md`에 각 섹션 안의 총 38개 세부 시나리오 판정도 모두 `통과`여야 한다고 명시했다.
  - 진행 순서도 `8개 섹션의 총 38개 세부 시나리오`를 순서대로 실행하는 표현으로 바꿨다.
  - `README.md`의 검증 안내에도 `8개 섹션과 총 38개 세부 시나리오 실행`을 명시했다.
  - `tests/test_manual_verification_doc.py`가 `parse_manual_verification_scenario_rows()`로 실제 수동 검증 시트에서 세부 시나리오 38개가 파싱되는지 확인하도록 했다.
  - 직접 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py -q`(`7 passed`)와 `python3 -m ruff check tests/test_manual_verification_doc.py`를 통과했다.

## 2026-06-08 - verification-status 세부 시나리오 판정 검증 보강

- 작업 이름: 수동 검증 요약표뿐 아니라 각 세부 시나리오 판정까지 완료 조건으로 검사
- 진행상황: 완료
- 진행내용:
  - `assistant-admin verification-status`가 `discord_manual_verification.md`의 8개 섹션 아래 세부 시나리오 표를 파싱하도록 보강했다.
  - 각 필수 섹션에 세부 시나리오 행이 있는지 확인하고, 모든 세부 시나리오의 판정이 `통과`, `실패`, `보류` 중 하나인지 검사하도록 했다.
  - 세부 시나리오 미기입, 판정값 오류, 실패, 보류를 각각 별도 항목으로 출력해 요약표만 채워도 목표 완료로 오판하지 않게 했다.
  - `discord_manual_verification.md`와 `README.md`에는 `verification-status`가 완료 요약과 세부 시나리오의 미기입, 판정값 오류, 실패, 보류, 증거 누락, 증거 형식 오류를 함께 확인한다고 정리했다.
  - `tests/test_cli.py`에 요약표만 통과하고 세부 시나리오 표가 없는 경우, 세부 시나리오에 미기입/실패/보류/잘못된 판정값이 섞인 경우를 완료 불가로 처리하는 회귀 테스트를 추가했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 8개 요약 섹션 미기입과 38개 세부 시나리오 미기입을 보고 `판정: 완료 불가`를 반환하는 것을 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py -q -k "manual_verification or verification_status"`(`8 passed, 85 deselected`), `python3 -m pytest tests/test_manual_verification_doc.py -q`(`7 passed`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1432 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - Discord 수동 검증 전 맥락 회귀 점검

- 작업 이름: 실제 Discord 검증 전에 라우터, 실행 전 검증, 응답 작성 자동 회귀망 재확인
- 진행상황: 완료
- 진행내용:
  - 목표 완료는 아직 실제 Discord 수동 검증 38개 시나리오가 필요하므로, 코드 레벨에서 먼저 맥락 유지 관련 고위험 테스트 묶음을 다시 실행했다.
  - `python3 -m assistant_bot.cli verification-status`를 실행해 현재 수동 검증 시트가 8개 요약 섹션 미기입과 38개 세부 시나리오 미기입 때문에 `판정: 완료 불가`를 반환하는 것을 재확인했다.
  - `tests/test_context_routing_matrix.py`는 같은 위치 후속 요청, 새 요청 분리, 다른 위치 확인, pending 승인/거부, 메모/문서/날씨/웹검색 후속 처리 매트릭스를 포함하며 `214 passed`로 통과했다.
  - `tests/test_route_validation.py`는 실행 전 링크 검증, 불명확한 후속 요청, 명시적 새 요청, cross-location clarify, pending 후보 선택 안전장치를 포함하며 `201 passed`로 통과했다.
  - `tests/test_router_agent.py`는 라우터 fallback, 모델 라우팅 보정, 내부 행동 기록 파싱, pending/context 후보 해석을 포함하며 `189 passed`로 통과했다.
  - `tests/test_response_composer.py tests/test_bot_helpers.py`는 최종 응답 작성과 Discord 오케스트레이션 helper의 private metadata 비노출, 작업 상태 저장 보조 로직을 포함하며 `260 passed`로 통과했다.
  - 이번 점검에서 새 코드 결함은 발견하지 못했으며, 남은 완료 조건은 실제 Discord 환경에서 `discord_manual_verification.md`의 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1432 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 8개 섹션과 38개 세부 시나리오 미기입 때문에 `판정: 완료 불가`를 반환하는 것을 확인했다.

## 2026-06-08 - assistant 예시 참조 메모 수정 pending 오승인 방지 테스트 추가

- 작업 이름: 봇이 든 예시를 그대로 사용하라는 메모 수정 요청을 다른 pending 승인으로 오해하지 않게 고정
- 진행상황: 완료
- 진행내용:
  - 실제 대화에서 사용자가 `네가 예를 들어준 내용 그대로 수정해줘`처럼 말했을 때, 이전 pending 확인이 열려 있으면 이 문장이 승인 답변처럼 소비될 위험이 있다.
  - `tests/test_context_routing_matrix.py`에 열린 할 일 삭제 pending이 있는 상태에서 같은 문장이 들어와도 `update_memory`, `context_link=none`으로 남고 pending 작업의 `linked_state_id`를 승인하지 않는 회귀 테스트를 추가했다.
  - 기존 `MemoryAgent`의 assistant 예시 기반 수정 테스트와 라우터의 assistant example diagnostic 테스트에 더해, 라우팅 매트릭스 레벨에서도 실제 실패 유형을 고정했다.
  - 직접 검증으로 새 케이스 단독 실행(`1 passed, 214 deselected`), 관련 묶음 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_route_validation.py tests/test_router_agent.py tests/test_memory_store.py -q`(`729 passed`), 문서/매트릭스 검증 `222 passed`, 관련 Ruff 검사를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1433 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `README.md`의 현재 자동 검증 결과와 문서 계약 테스트의 테스트 수를 `1433개 통과`로 갱신했다.

## 2026-06-08 - verification-status 섹션/시나리오 불일치 감지

- 작업 이름: 섹션 요약은 통과인데 세부 시나리오가 통과가 아닌 검증표를 명확히 표시
- 진행상황: 완료
- 진행내용:
  - `완료 판정 요약`의 섹션 최종 판정이 `통과`인데 해당 섹션의 세부 시나리오가 미기입, 실패, 보류, 판정값 오류인 경우 완료 불가로 처리되지만, 사용자가 어떤 섹션 요약을 다시 고쳐야 하는지 출력에서 바로 보기는 어려웠다.
  - `assistant-admin verification-status`가 이런 상태를 `섹션/시나리오 불일치`로 별도 집계하고 출력하도록 보강했다.
  - 완료 조건에도 `섹션/시나리오 불일치`가 없어야 한다는 조건을 포함했다.
  - `discord_manual_verification.md`와 `README.md`에 섹션/시나리오 불일치가 완료 불가 사유이며 `process.md` 기록 대상이라고 명시했다.
  - `tests/test_cli.py`의 세부 시나리오 실패/보류/미기입/판정값 오류 케이스가 섹션/시나리오 불일치를 출력하는지 확인하도록 보강했고, `tests/test_manual_verification_doc.py`에도 문서 문구 계약을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`15 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1432 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 `섹션/시나리오 불일치: 0`을 포함해 출력하고, 8개 섹션과 38개 세부 시나리오 미기입 때문에 `판정: 완료 불가`를 반환하는 것을 확인했다.

## 2026-06-08 - 자동 검증 결과 1433개 통과 재확인

- 작업 이름: assistant 예시 참조 pending 오승인 방지 테스트 추가 이후 최종 자동 검증 수 정리
- 진행상황: 완료
- 진행내용:
  - `assistant 예시 참조 메모 수정 pending 오승인 방지 테스트`가 추가되면서 전체 테스트 수가 1433개로 늘었다.
  - `README.md`와 `tests/test_manual_verification_doc.py`의 현재 자동 검증 결과 문구를 `테스트 1433개 통과`로 맞췄다.
  - 최종 검증으로 `python3 -m pytest -q`(`1433 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 `discord_manual_verification.md`의 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-status 섹션/시나리오 불일치 양방향 감지

- 작업 이름: 세부 시나리오는 통과인데 섹션 요약이 실패/보류로 남은 검증표도 불일치로 표시
- 진행상황: 완료
- 진행내용:
  - 기존 섹션/시나리오 불일치 검사는 섹션 요약이 `통과`인데 세부 시나리오가 통과가 아닌 경우를 중심으로 잡았다.
  - 실제 검증 중에는 반대로 세부 시나리오는 모두 통과했지만 섹션 요약이 실패/보류로 남아 있는 경우도 발생할 수 있으므로, 이 경우도 `섹션/시나리오 불일치`로 집계하도록 보강했다.
  - `discord_manual_verification.md`에는 요약 통과/세부 미통과와 세부 전체 통과/요약 실패 또는 보류가 모두 불일치에 해당한다고 명시했다.
  - `tests/test_cli.py`에 섹션 요약은 실패지만 세부 시나리오는 통과인 검증표를 완료 불가와 섹션/시나리오 불일치로 처리하는 회귀 테스트를 추가했다.
  - `tests/test_manual_verification_doc.py`에는 양방향 불일치 설명 문구가 계속 남아 있는지 확인하는 계약을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`16 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1434 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 `섹션/시나리오 불일치: 0`을 포함해 출력하고, 8개 섹션과 38개 세부 시나리오 미기입 때문에 `판정: 완료 불가`를 반환하는 것을 확인했다.

## 2026-06-08 - verification-status 수동 검증 진행률 출력

- 작업 이름: 수동 검증표 작성 진행률을 CLI 출력에서 바로 확인
- 진행상황: 완료
- 진행내용:
  - `assistant-admin verification-status`가 미기입 항목은 보여주지만, 8개 섹션과 38개 세부 시나리오 중 판정 칸을 얼마나 채웠는지 한눈에 보기 어려웠다.
  - 상태 수집 결과에 섹션 판정 입력 수와 시나리오 판정 입력 수를 추가하고, 출력에 `섹션 진행률`과 `시나리오 진행률`을 표시하도록 했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `섹션 진행률: 0/8`, `시나리오 진행률: 0/38`이 출력되는 것을 확인했다.
  - 완료 가능 샘플은 `섹션 진행률: 8/8`, `시나리오 진행률: 8/8`을 출력하도록 테스트로 고정했다.
  - `discord_manual_verification.md`에는 출력의 진행률 항목을 보면 판정 칸을 얼마나 채웠는지 확인할 수 있다고 안내했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`16 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - `inspect.getsource()` 기반 CLI 계약 테스트의 간헐적 실패를 안정화한 뒤 관련 범위 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py tests/test_cli.py -q -k "manual_verification or verification_status or readme_mentions or cli_clarification_result or cli_context_cancellation or cli_response_composer"`(`20 passed, 82 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1435 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 `섹션 진행률: 0/8`, `시나리오 진행률: 0/38`을 표시하고 `판정: 완료 불가`를 반환하는 것을 확인했다.

## 2026-06-08 - verification-status 필수 시나리오 부족 게이트 재확인

- 작업 이름: 축소된 수동 검증표가 완료 가능으로 통과하지 못하도록 하는 게이트 확인
- 진행상황: 완료
- 진행내용:
  - 현재 `assistant-admin verification-status`는 `REQUIRED_MANUAL_VERIFICATION_SCENARIOS = 38`을 기준으로, 세부 시나리오가 1개 이상 38개 미만이면 `필수 시나리오 부족`으로 완료 불가 처리한다.
  - `tests/test_cli.py`에는 8개 축소 시나리오만 모두 통과한 검증표가 `필수 시나리오 부족: 1`, `세부 시나리오 8/38개`로 완료 불가 처리되는 회귀 테스트가 있다.
  - `discord_manual_verification.md`, `README.md`, `tests/test_manual_verification_doc.py`에도 필수 시나리오 부족 항목이 수동 검증 게이트의 확인 대상으로 남아 있는 것을 확인했다.
  - 현재 비어 있는 실제 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 세부 시나리오 38개를 정상 파싱하고 `필수 시나리오 부족: 0`, `섹션 진행률: 0/8`, `시나리오 진행률: 0/38`, `판정: 완료 불가`를 출력하는 것을 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`17 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 전체 CLI 검증으로 `python3 -m pytest tests/test_cli.py -q`(`96 passed`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1436 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.

## 2026-06-08 - verification-status 진행률 퍼센트 표시

- 작업 이름: 수동 검증표 작성 진행률을 숫자와 퍼센트로 함께 표시
- 진행상황: 완료
- 진행내용:
  - 기존 `verification-status`는 `섹션 진행률: 0/8`, `시나리오 진행률: 0/38`처럼 채운 개수만 보여주어 전체 진행 감각을 한눈에 보기는 아쉬웠다.
  - `format_manual_verification_progress()`를 추가해 진행률을 `0/38 (0%)`, `38/38 (100%)` 형태로 출력하도록 했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `섹션 진행률: 0/8 (0%)`, `시나리오 진행률: 0/38 (0%)`가 출력되는 것을 확인했다.
  - 완료 가능 샘플과 축소 시나리오 샘플 테스트의 진행률 기대값을 퍼센트 포함 형식으로 갱신했다.
  - `discord_manual_verification.md`에는 진행률을 숫자와 퍼센트로 확인할 수 있다고 안내했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`18 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1437 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 `섹션 진행률: 0/8 (0%)`, `시나리오 진행률: 0/38 (0%)`와 함께 `판정: 완료 불가`를 반환하는 것을 확인했다.

## 2026-06-08 - verification-status 후속 조치 문구 전체 게이트 반영

- 작업 이름: 완료 불가 출력의 후속 조치 안내에 모든 수동 검증 게이트 항목 포함
- 진행상황: 완료
- 진행내용:
  - `verification-status` 출력은 필수 시나리오 부족, 시나리오 순서 오류, 섹션/시나리오 불일치까지 표시하지만, 후속 조치 문구는 미기입/판정값 오류/증거 오류 중심으로만 안내하고 있었다.
  - 후속 조치 문구에 `필수 시나리오 부족`, `시나리오 순서 오류`, `섹션·시나리오 불일치`를 포함해, 출력에 드러난 모든 게이트 항목이 어떤 문서를 수정해야 하는지 한 문장에서 안내되도록 했다.
  - 실패/보류는 계속 `process.md`에 실제 응답과 후속 수정 필요 여부를 기록하도록 안내한다.
  - 현재 비어 있는 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 새 후속 조치 문구를 출력하는 것을 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`19 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.

## 2026-06-08 - CLI 소스 계약 테스트 안정화

- 작업 이름: `run_local_text_interaction` 소스 계약 테스트의 간헐적 실패 방지
- 진행상황: 완료
- 진행내용:
  - 전체 테스트 중 `inspect.getsource(cli_module.run_local_text_interaction)`가 간헐적으로 함수 전체가 아니라 `load_cli_config` 내부 설정 줄 하나를 반환해, 실제 코드 문제가 아닌 테스트 소스 추출 문제로 3개 계약 테스트가 실패하는 상황을 확인했다.
  - `tests/test_cli.py`에 `cli_function_source()` helper를 추가해 `assistant_bot/cli.py` 파일 텍스트에서 함수 범위를 직접 잘라 읽도록 했다.
  - `test_cli_clarification_result_records_linked_subject_contract`, `test_cli_context_cancellation_uses_shared_result_contract`, `test_cli_response_composer_uses_post_execution_router_context`가 이 helper를 사용하도록 바꿨다.
  - 직접 검증으로 해당 3개 테스트(`3 passed`), 관련 범위 테스트 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions or cli_clarification_result or cli_context_cancellation or cli_response_composer"`(`20 passed, 82 deselected`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 요약이 `통과`인데 해당 섹션의 세부 시나리오 행이 아예 없는 경우도 `섹션/시나리오 불일치`로 잡도록 보강했다.
  - 검증 시트 파일을 찾지 못하는 경우에도 `scenario_rows`, `scenario_summary_mismatch` 등 출력 포맷에 필요한 키를 모두 반환하도록 정리했다.
  - `tests/test_cli.py`에서 요약 8개가 통과인데 세부 시나리오 표가 없는 경우 `섹션/시나리오 불일치: 8`로 처리되는지 확인하도록 기대값을 보강했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1434 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 `discord_manual_verification.md`의 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-status 필수 38개 시나리오 수 완료 조건 추가

- 작업 이름: 축소된 수동 검증표를 완료 가능으로 오판하지 않도록 필수 시나리오 개수 검증
- 진행상황: 완료
- 진행내용:
  - `discord_manual_verification.md`는 목표 완료 기준으로 8개 섹션과 총 38개 세부 시나리오를 요구하지만, 기존 `verification-status` 완료 가능 테스트는 섹션별 1개씩 총 8개 세부 시나리오만 있어도 통과 가능한 축소 표를 사용하고 있었다.
  - `assistant_bot/cli.py`에 `REQUIRED_MANUAL_VERIFICATION_SCENARIOS = 38`을 추가하고, 세부 시나리오 행이 1개 이상 38개 미만이면 `필수 시나리오 부족`으로 완료 불가 처리하도록 보강했다.
  - `tests/test_cli.py`의 완료 가능 샘플을 실제 검증표와 같은 4/5/5/5/5/5/5/4 분포의 38개 시나리오로 확장했다.
  - 축소 표 8개가 모두 `통과`여도 `필수 시나리오 부족: 1`, `세부 시나리오 8/38개`로 완료 불가가 되는 회귀 테스트를 추가했다.
  - `discord_manual_verification.md`, `README.md`, `tests/test_manual_verification_doc.py`에 `필수 시나리오 부족` 항목을 수동 검증 게이트의 확인 대상으로 추가했다.
  - 현재 비어 있는 실제 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 세부 시나리오 38개를 정상 파싱하고 `필수 시나리오 부족: 0`, 미기입 8/38 때문에 `판정: 완료 불가`를 반환하는 것을 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`17 passed, 85 deselected`), 이후 갱신된 집중 검증 `tests/test_manual_verification_doc.py`(`7 passed`)와 `tests/test_cli.py -k "manual_verification or verification_status"`(`10 passed, 85 deselected`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1435 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-status 섹션별 시나리오 분포 검증 추가

- 작업 이름: 총 38개는 맞지만 특정 검증 축이 빠진 수동 검증표를 완료로 보지 않게 고정
- 진행상황: 완료
- 진행내용:
  - 총 세부 시나리오 수가 38개여도 특정 섹션의 시나리오가 부족하고 다른 섹션에 과하게 들어가면 목표 검증 축이 빠질 수 있다.
  - `assistant_bot/cli.py`에 `REQUIRED_MANUAL_VERIFICATION_SCENARIO_COUNTS`를 추가해 섹션별 기대 분포를 `4/5/5/5/5/5/5/4`로 고정했다.
  - `verification-status`가 실제 시나리오 행의 섹션별 개수를 세고, 기대 개수와 다르면 `필수 시나리오 부족` 항목으로 표시하도록 보강했다.
  - `tests/test_manual_verification_doc.py`는 실제 `discord_manual_verification.md`에서 파싱한 시나리오 분포가 `REQUIRED_MANUAL_VERIFICATION_SCENARIO_COUNTS`와 정확히 일치하는지 확인한다.
  - `tests/test_cli.py`에는 총 38개지만 1번 섹션은 3/4개, 2번 섹션은 6/5개인 검증표를 완료 불가로 처리하는 회귀 테스트를 추가했다.
  - 현재 실제 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 세부 시나리오 38개와 섹션별 분포를 정상으로 보고 `필수 시나리오 부족: 0`, 미기입 8/38 때문에 `판정: 완료 불가`를 반환하는 것을 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`18 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1436 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-status 시나리오 순서 오류 검증 추가

- 작업 이름: 세부 시나리오 순서가 중복되거나 누락된 검증표를 완료로 보지 않게 고정
- 진행상황: 완료
- 진행내용:
  - 섹션별 시나리오 개수는 맞아도 `순서` 값이 중복되거나 빠지면 실제 수동 검증표가 어떤 항목을 검증했는지 추적하기 어려워진다.
  - `assistant_bot/cli.py`가 각 섹션의 시나리오 순서를 `1..N` 기대 목록과 비교하고, 다르면 `시나리오 순서 오류`로 출력하도록 보강했다.
  - `tests/test_cli.py`에는 개수와 분포는 맞지만 1번 섹션 순서가 `1, 2, 2, 4`인 검증표를 완료 불가로 처리하는 회귀 테스트를 추가했다.
  - 기존 축소표/분포 오류 테스트도 `시나리오 순서 오류` 항목을 함께 확인하도록 보강했다.
  - `discord_manual_verification.md`, `README.md`, `tests/test_manual_verification_doc.py`에 `시나리오 순서 오류` 항목을 수동 검증 게이트의 확인 대상으로 추가했다.
  - 현재 실제 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 `시나리오 순서 오류: 0`, `필수 시나리오 부족: 0`을 출력하고, 판정 미기입 8/38 때문에 `판정: 완료 불가`를 반환하는 것을 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`19 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1437 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-status 파일 없음 출력 계약 보강

- 작업 이름: 수동 검증 시트 경로가 잘못된 경우에도 새 완료 게이트 출력 구조 유지
- 진행상황: 완료
- 진행내용:
  - `verification-status` 후속 조치 문구가 새 게이트인 필수 시나리오 부족, 시나리오 순서 오류, 섹션/시나리오 불일치를 모두 안내하는지 확인했다.
  - `tests/test_cli.py`에 검증 시트 파일이 없는 경우를 추가해, `필수 시나리오 부족`, `시나리오 순서 오류`, `섹션/시나리오 불일치` 출력 키가 빠지지 않고 후속 조치 문구도 최신 형태로 유지되는지 고정했다.
  - `README.md`와 `tests/test_manual_verification_doc.py`의 현재 자동 검증 결과를 `테스트 1438개 통과`로 갱신했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`20 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1438 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-status 다음 미기입 시나리오 안내

- 작업 이름: 수동 검증 중 다음에 확인할 세부 시나리오를 바로 안내
- 진행상황: 완료
- 진행내용:
  - 목표 완료 판단은 실제 Discord 수동 검증표의 38개 세부 시나리오를 모두 채워야 하는데, 기존 `verification-status` 출력은 미기입 목록 전체만 보여줘 다음 진행 항목을 바로 찾기 어려웠다.
  - `assistant_bot/cli.py`의 `format_manual_verification_status()`가 완료 불가 상태에서 세부 시나리오 미기입 항목이 있으면 첫 번째 항목을 `다음 미기입 시나리오`로 출력하도록 보강했다.
  - `discord_manual_verification.md`에 `다음 미기입 시나리오`를 보고 바로 이어서 검증하라는 운영 기준을 추가했다.
  - `tests/test_cli.py`와 `tests/test_manual_verification_doc.py`에 새 출력/문서 계약을 추가했다.
  - 현재 실제 수동 검증 시트 기준으로 `python3 -m assistant_bot.cli verification-status`가 `다음 미기입 시나리오: 1. 같은 위치 후속 요청 / 1`을 출력하는 것을 확인했다. 검증표가 비어 있으므로 종료 코드 1과 `판정: 완료 불가`는 정상이다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`20 passed, 85 deselected`)와 `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1438 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-preflight 맥락 연결 사전검증 보강

- 작업 이름: Discord 수동 검증 전 같은 위치/다른 위치/새 요청 분리 정책을 로컬에서 먼저 확인
- 진행상황: 완료
- 진행내용:
  - 기존 `verification-preflight`는 핵심 문장 intent 중심이라, 목표의 핵심인 맥락 연결 정책(`continue`, `clarify`, `none`)을 충분히 사전 검증하지 못했다.
  - `assistant_bot/cli.py`의 예행 케이스에 같은 위치 최근 할 일 후보가 있을 때 `방금 할 일 보여줘`를 `manage_task + context_link=continue`로 처리하는 케이스를 추가했다.
  - 최근 원주 날씨 실패 후보가 있어도 `서울 날씨 알려줘`는 새 지역 요청이므로 `weather + context_link=none`으로 분리되는지 확인하도록 seed 상태를 추가했다.
  - 다른 위치에 할 일 후보가 있을 때 `그거 보여줘`는 바로 실행하지 않고 `manage_task + context_link=clarify`로 확인 질문 경로를 타는지 확인하는 케이스를 추가했다.
  - 예행 검증용 상태는 실제 운영 DB에 쓰지 않고 케이스별 임시 SQLite DB에 심은 뒤 `-wal`, `-shm` 파일까지 정리하도록 했다.
  - seed 상태도 `OperationResult`와 `turn_state_artifacts_from_result()`를 거치게 해 실제 런타임 turn state 정제 규칙과 맞췄다.
  - `discord_manual_verification.md`, `README.md`, `tests/test_manual_verification_doc.py`에 예행 점검이 19개 핵심 문장과 같은 위치 `continue`, 실패 작업 재시도 `retry`, 다른 위치 `clarify`, 무관한 새 요청 `none` 분리를 함께 확인한다는 운영 기준을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "preflight or manual_verification or readme_mentions"`(`22 passed, 85 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`19개 통과`), `python3 -m ruff check .`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1440 passed`), `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `python3 -m assistant_bot.cli verification-status`는 실제 Discord 검증표 8개 섹션/38개 시나리오가 아직 미기입이라 `판정: 완료 불가`를 반환했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-preflight 실패 진단 출력 보강

- 작업 이름: 로컬 예행 실패 시 라우팅 reason과 연결 상태 후보를 바로 확인
- 진행상황: 완료
- 진행내용:
  - `verification-preflight`가 실패하면 기존에는 실제 intent/context_link만 보여줘, 왜 이전 맥락을 잘못 이어받았는지 또는 왜 새 요청을 분리하지 못했는지 바로 판단하기 어려웠다.
  - `assistant_bot/cli.py`의 예행 결과 row에 라우터 reason, 실제 linked_state_id, 연결된 subject, 후보 개수를 함께 저장하도록 보강했다.
  - 출력은 평소에는 짧게 유지하고, 실패 케이스에서만 `reason`과 `linked_state` 진단 줄을 추가하도록 했다.
  - `tests/test_cli.py`에 실패 출력이 `reason: ...`, `linked_state: ... · subject: ... · candidates: ...`를 포함하는지 확인하는 계약 테스트를 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py -q -k "manual_verification_preflight"`(`2 passed, 98 deselected`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py`, `python3 -m assistant_bot.cli verification-preflight`(`19개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1440 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-status 다음 시나리오 상세 안내

- 작업 이름: 수동 검증 중 다음 미기입 시나리오의 입력과 기대 동작을 바로 표시
- 진행상황: 완료
- 진행내용:
  - 기존 `verification-status`는 다음 미기입 시나리오 라벨만 보여줘, 실제로 어떤 메시지를 Discord에 보내야 하는지 확인하려면 `discord_manual_verification.md`를 다시 열어야 했다.
  - `parse_manual_verification_scenario_rows()`가 세부 시나리오 표의 `입력`, `기대 동작`, 그리고 다른 위치 맥락 표의 `입력 위치`까지 파싱하도록 보강했다.
  - `format_manual_verification_status()`가 완료 불가 상태에서 첫 미기입 시나리오의 `입력`과 `기대 동작`을 함께 출력하도록 했다.
  - `discord_manual_verification.md`에 `다음 미기입 시나리오`, `입력`, `기대 동작`을 보고 바로 이어서 검증할 수 있다는 운영 기준을 추가했다.
  - `tests/test_cli.py`와 `tests/test_manual_verification_doc.py`에 다음 시나리오 상세 출력과 실제 검증표의 입력/기대 동작 파싱 계약을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py tests/test_cli.py -q -k "manual_verification or verification_status or preflight or readme_mentions"`(`22 passed, 85 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`19개 통과`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1440 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 현재 `python3 -m assistant_bot.cli verification-status`는 `다음 미기입 시나리오: 1. 같은 위치 후속 요청 / 1`, `입력: 병원 예약 할 일 추가해줘`, `기대 동작: 새 할 일이 등록된다.`를 출력하고, 실제 Discord 검증표가 아직 비어 있어 `판정: 완료 불가`를 반환한다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-record 수동 검증 기록 CLI 추가

- 작업 이름: Discord 수동 검증 결과를 Markdown 표에 안전하게 기록
- 진행상황: 완료
- 진행내용:
  - 수동 검증 중 `discord_manual_verification.md`를 직접 편집하면 판정값 오타나 표 형식 깨짐이 생길 수 있어, CLI로 세부 시나리오와 섹션 요약을 기록하는 경로를 추가했다.
  - `assistant-admin verification-record --section 1 --step 1 --status 통과`는 해당 세부 시나리오의 판정 칸만 갱신한다.
  - `assistant-admin verification-record --section 1 --status 통과 --evidence "https://discord.com/channels/..."`는 완료 판정 요약의 최종 판정과 증거 위치를 갱신한다.
  - 섹션은 `1` 같은 번호, 전체 섹션명, 제목만 입력해도 해석되며, 판정은 `통과`, `실패`, `보류`만 허용한다.
  - 잘못된 섹션이나 없는 순서는 `ValueError`로 실패하게 해 검증표가 조용히 잘못 수정되지 않도록 했다.
  - `discord_manual_verification.md`와 `README.md`에 `verification-record` 사용 흐름을 추가하고, `tests/test_manual_verification_doc.py`가 해당 운영 기준을 확인하도록 갱신했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "record_manual_verification or manual_verification_doc or readme_mentions"`(`9 passed, 100 deselected`), `python3 -m assistant_bot.cli verification-record --help`, `python3 -m assistant_bot.cli verification-preflight`(`20개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1442 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `python3 -m assistant_bot.cli verification-status`는 실제 Discord 검증표 8개 섹션/38개 시나리오가 아직 미기입이라 `판정: 완료 불가`를 반환했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-record 다음 미기입 바로 기록 옵션 추가

- 작업 이름: `verification-status`가 안내한 다음 세부 시나리오를 `--next`로 바로 기록
- 진행상황: 완료
- 진행내용:
  - 수동 검증 중 `verification-status`가 다음 미기입 시나리오를 알려줘도, 기록할 때 다시 `--section`, `--step`을 옮겨 적어야 해서 작은 오타 가능성이 남아 있었다.
  - `assistant-admin verification-record --next --status 통과`를 추가해 검증표에서 첫 번째 미기입 세부 시나리오를 자동으로 찾아 판정 칸을 기록하도록 했다.
  - `--next`는 세부 시나리오 기록 전용이며, `--section` 또는 `--step`과 함께 쓰면 실패하게 해 기록 대상이 모호해지지 않도록 했다.
  - `--next` 기록 결과에는 해당 시나리오의 입력과 기대 동작도 함께 출력되도록 했다.
  - `discord_manual_verification.md`, `README.md`, `tests/test_manual_verification_doc.py`에 `--next` 사용 흐름을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "record_manual_verification or manual_verification_doc or readme_mentions"`(`10 passed, 100 deselected`), `python3 -m assistant_bot.cli verification-record --help`, `python3 -m assistant_bot.cli verification-preflight`(`21개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1443 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `python3 -m assistant_bot.cli verification-status`는 실제 Discord 검증표 8개 섹션/38개 시나리오가 아직 미기입이라 `판정: 완료 불가`를 반환했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-status 다음 기록 명령 안내

- 작업 이름: 다음 미기입 시나리오 출력에 바로 실행할 기록 명령 표시
- 진행상황: 완료
- 진행내용:
  - `verification-status`가 다음 미기입 시나리오의 입력과 기대 동작을 알려주지만, 사용자가 검증 결과에 맞는 `verification-record --next` 명령을 다시 떠올려야 하는 마찰이 남아 있었다.
  - 완료 불가 출력에서 다음 미기입 세부 시나리오가 있으면 `기록 명령` 섹션을 추가해 `통과`, `실패`, `보류`별 `assistant-admin verification-record --next --status ...` 명령을 바로 보여주도록 했다.
  - `discord_manual_verification.md`와 `tests/test_manual_verification_doc.py`에 `기록 명령` 안내가 유지되도록 문서 계약을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification or verification_status or readme_mentions"`(`25 passed, 85 deselected`), `python3 -m assistant_bot.cli verification-status`, `python3 -m assistant_bot.cli verification-preflight`(`22개 통과`)를 확인했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1443 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `python3 -m assistant_bot.cli verification-status`는 실제 Discord 검증표 8개 섹션/38개 시나리오가 아직 미기입이라 `판정: 완료 불가`를 반환했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-preflight 재시도 slot 보존 검증

- 작업 이름: 실패한 날씨 조회 뒤 `다시해봐`가 원래 지역을 유지해 재시도되는지 로컬 예행으로 고정
- 진행상황: 완료
- 진행내용:
  - 이전 Discord 테스트에서 날씨 조회 실패 뒤 `다시해봐`가 원래 지역을 이어받지 못하고 지역을 다시 묻는 문제가 있었다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 원주 날씨 실패 상태를 seed한 뒤 `다시해봐`를 보내는 케이스를 추가했다.
  - 새 케이스는 `intent=weather`, `context_link=retry`, `resolved_slots.location=원주`를 모두 만족해야 통과하도록 했다.
  - `collect_manual_verification_preflight()`가 케이스별 `expected_resolved_slots`를 검사하고, 실패 시 실제/기대 slot을 함께 출력하도록 보강했다.
  - `README.md`, `discord_manual_verification.md`, `tests/test_manual_verification_doc.py`의 로컬 예행 문장 수를 19개로 갱신하고, 실패 작업 재시도의 `retry` 분리 기준을 문서화했다.
  - `tests/test_cli.py`는 `다시해봐` 성공 출력과 slot mismatch 실패 진단 출력을 함께 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification_preflight or manual_verification_doc or readme_mentions"`(`9 passed, 98 deselected`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`, `python3 -m assistant_bot.cli verification-preflight`(`19개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1440 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-preflight 교차 위치 재시도 확인 검증

- 작업 이름: 다른 위치의 실패 작업에 대한 `다시해봐`가 바로 실행되지 않고 확인 질문으로 가는지 고정
- 진행상황: 완료
- 진행내용:
  - 같은 위치 실패 작업은 `retry`로 이어져야 하지만, 다른 위치의 실패 작업을 현재 위치에서 `다시해봐`라고 하면 위치가 바뀌었으므로 바로 실행하지 않고 확인해야 한다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 다른 위치 원주 날씨 실패 상태를 seed한 뒤 현재 위치에서 `다시해봐`를 보내는 케이스를 추가했다.
  - 새 케이스는 `intent=weather`, `context_link=clarify`, `resolved_slots.location=원주`를 모두 만족해야 통과한다.
  - `README.md`, `discord_manual_verification.md`, `tests/test_manual_verification_doc.py`의 로컬 예행 문장 수를 20개로 갱신하고, 다른 위치 후속/재시도 요청은 `clarify`로 분리한다는 기준을 문서화했다.
  - `tests/test_cli.py`는 같은 `다시해봐`라도 같은 위치 실패 작업은 `retry`, 다른 위치 실패 작업은 `clarify`로 나뉘는 성공 출력을 함께 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification_preflight or manual_verification_doc or readme_mentions"`(`9 passed, 98 deselected`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`, `python3 -m assistant_bot.cli verification-preflight`(`20개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1442 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-preflight 같은 위치 다중 재시도 후보 확인 검증

- 작업 이름: 같은 위치에 재시도 가능한 실패 후보가 여러 개일 때 `다시해봐`가 특정 후보를 임의 실행하지 않도록 고정
- 진행상황: 완료
- 진행내용:
  - 같은 위치 실패 작업이 하나면 `다시해봐`를 `retry`로 이어가야 하지만, 실패한 날씨 조회와 웹검색처럼 재시도 후보가 여러 개면 어느 작업을 재시도할지 먼저 물어야 한다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 같은 위치의 원주 날씨 실패와 OpenAI 모델 웹검색 실패 상태를 함께 seed한 뒤 `다시해봐`를 보내는 케이스를 추가했다.
  - 새 케이스는 `intent=chat`, `context_link=clarify`, `pending_candidate_state_ids`, `pending_original_text=다시해봐`를 만족해야 통과한다.
  - 예행 중 실제로 `pending_candidate_state_ids`가 `[2, 1, 2, 1]`처럼 중복되는 문제를 발견했고, `route_validation.safe_unlinked_clarify_slots()`와 `bot.pending_candidate_state_ids_from_slots()`에서 순서 유지 dedupe를 적용했다.
  - `README.md`, `discord_manual_verification.md`, `tests/test_manual_verification_doc.py`의 로컬 예행 문장 수를 21개로 갱신하고, 같은 위치 다중 재시도 후보는 `clarify`로 분리한다는 기준을 문서화했다.
  - `tests/test_cli.py`는 같은 `다시해봐`라도 단일 실패 후보는 `weather + retry`, 다중 실패 후보는 `chat + clarify`로 나뉘는 성공 출력을 함께 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification_preflight or manual_verification_doc or readme_mentions"`(`9 passed, 101 deselected`), `python3 -m ruff check assistant_bot/cli.py assistant_bot/bot.py assistant_bot/route_validation.py tests/test_cli.py tests/test_manual_verification_doc.py`, `python3 -m assistant_bot.cli verification-preflight`(`21개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1443 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-preflight 다중 후보 선택 복원 검증

- 작업 이름: 다중 재시도 후보 확인 뒤 `첫 번째` 선택이 선택된 작업의 원래 재시도 의도를 복원하는지 고정
- 진행상황: 완료
- 진행내용:
  - 다중 후보 상황에서 `다시해봐`를 `chat + clarify`로 멈추는 것만으로는 충분하지 않고, 사용자의 `첫 번째` 같은 선택 답변이 선택된 후보의 원래 작업으로 복원되어야 실제 대화가 이어진다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 날씨 실패, 웹검색 실패, 재시도 후보 선택 대기 상태를 seed한 뒤 `첫 번째`를 보내는 케이스를 추가했다.
  - 새 케이스는 pending 후보 순서상 첫 번째인 웹검색 후보를 선택해 `intent=web_search`, `context_link=retry`, `resolved_slots.query=OpenAI 모델`, `pending_original_text=다시해봐`를 만족해야 통과한다.
  - `README.md`, `discord_manual_verification.md`, `tests/test_manual_verification_doc.py`의 로컬 예행 문장 수를 22개로 갱신하고, 후보 선택 답변은 원래 작업으로 복원해야 한다는 기준을 문서화했다.
  - `tests/test_cli.py`는 `첫 번째`가 `web_search + retry`로 복원되는 성공 출력을 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification_preflight or manual_verification_doc or readme_mentions"`(`9 passed, 101 deselected`), `python3 -m ruff check assistant_bot/cli.py assistant_bot/bot.py assistant_bot/route_validation.py tests/test_cli.py tests/test_manual_verification_doc.py`, `python3 -m assistant_bot.cli verification-preflight`(`22개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1443 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-preflight `응` 새 요청 pending 오인 방지 강화

- 작업 이름: pending 확인 대기 상태가 있어도 `응 서울 날씨 알려줘`를 오래된 승인으로 소비하지 않도록 예행 강화
- 진행상황: 완료
- 진행내용:
  - 기존 `응 서울 날씨 알려줘` 예행은 단순 문장만 검증해, 실제 pending 확인 대기 상태가 있는 상황에서 오래된 `원주` 재시도 승인으로 오해하지 않는지 충분히 검증하지 못했다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`의 `2.3` 케이스에 원주 날씨 실패 상태와 원주 재시도 확인 대기 상태를 seed했다.
  - 새 검사는 `intent=weather`, `context_link=none`을 기대하면서, `resolved_slots.location=원주` 또는 `pending_original_text=다시해봐`가 묻어나오면 실패하도록 `forbidden_resolved_slots`를 추가했다.
  - `collect_manual_verification_preflight()`가 금지 slot을 검사하고, 실패 시 `forbidden_slots`를 출력하도록 보강했다.
  - `README.md`, `discord_manual_verification.md`, `tests/test_manual_verification_doc.py`에 `응`으로 시작하는 새 요청은 pending 승인으로 오인하지 않는다는 기준을 문서화했다.
  - `tests/test_cli.py`는 실패 진단 출력에 금지 slot 목록이 포함되는지 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification_preflight or manual_verification_doc or readme_mentions"`(`9 passed, 101 deselected`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`, `python3 -m assistant_bot.cli verification-preflight`(`22개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1443 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-preflight `응` 목록 조회 pending 오인 방지 강화

- 작업 이름: pending 확인 대기 상태가 있어도 `응 확인 목록 보여줘`를 오래된 승인으로 소비하지 않도록 예행 강화
- 진행상황: 완료
- 진행내용:
  - 기존 `응 서울 날씨 알려줘` 예행은 새 날씨 요청 분리를 확인하지만, 실제 대화에서 자주 나올 수 있는 목록 조회 계열 새 요청까지 pending 승인으로 오인하지 않는지는 별도로 고정할 필요가 있었다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 `2.4` 케이스를 추가해 원주 날씨 실패 상태와 원주 재시도 확인 대기 상태가 있는 상황에서 `응 확인 목록 보여줘`를 보낸다.
  - 새 검사는 `intent=list_memory`, `context_link=none`을 기대하면서, 오래된 pending의 `resolved_slots.location=원주` 또는 `pending_original_text=다시해봐`가 묻어나오면 실패하도록 금지 slot을 둔다.
  - `README.md`, `discord_manual_verification.md`, `tests/test_manual_verification_doc.py`의 로컬 예행 문장 수를 23개로 갱신하고, 수동 검증 고위험 문구에도 `응 확인 목록 보여줘`를 추가했다.
  - `tests/test_cli.py`는 `응 확인 목록 보여줘`가 `list_memory + none`으로 분리되는 성공 출력을 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification_preflight or manual_verification_doc or readme_mentions"`(`9 passed, 101 deselected`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`, `python3 -m assistant_bot.cli verification-preflight`(`23개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1443 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-preflight 부정어 새 요청 pending 거부 오인 방지 강화

- 작업 이름: pending 확인 대기 상태가 있어도 `아니 취소 말고 상태 알려줘`를 오래된 거부로 소비하지 않도록 예행 강화
- 진행상황: 완료
- 진행내용:
  - 실제 대화에서는 사용자가 `아니 취소 말고 ...`처럼 부정어로 시작하지만 뒤에 명시적인 새 요청을 붙이는 경우가 있다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 `5.5` 케이스를 추가해 `아니 취소 말고 상태 알려줘`가 `intent=status`, `context_link=none`으로 분리되는지 확인하도록 했다.
  - `is_negative_confirmation()` 회귀 테스트에도 같은 문장을 추가해 pending 확인 처리기가 이 문장을 거부/취소 신호로 오인하지 않도록 고정했다.
  - 기존에 `2.6` 케이스가 이미 있어 이번 추가 후 실제 로컬 예행은 26개가 되었고, `README.md`, `discord_manual_verification.md`, `tests/test_manual_verification_doc.py`의 로컬 예행 문장 수를 26개로 갱신했다.
  - 부정어로 시작하는 새 요청은 pending 거부로 오인하지 않는다는 기준을 문서화했다.
  - `tests/test_cli.py`는 `아니 취소 말고 상태 알려줘`가 `status + none`으로 분리되는 성공 출력을 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py tests/test_bot_helpers.py -q -k "manual_verification_preflight or manual_verification_doc or readme_mentions or confirmation_helpers"`(`10 passed, 311 deselected`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py tests/test_bot_helpers.py`, `python3 -m assistant_bot.cli verification-preflight`(`26개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1443 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 파일/메모 목록 범위 슬롯 보존 강화

- 작업 이름: `파일 목록 보여줘`와 `메모 목록 보여줘`가 라우터 단계부터 서로 다른 범위로 남도록 개선
- 진행상황: 완료
- 진행내용:
  - 기존에는 두 문장이 모두 `list_memory`로 라우팅되지만 `resolved_slots`가 비어 있어, 내부 행동 기록과 후속 맥락에서 파일 목록을 봤는지 메모 목록을 봤는지 구분 근거가 약했다.
  - `memory_list_kind()`를 공통 라우팅 유틸로 옮기고, 휴리스틱 라우터가 `파일 목록 보여줘`는 `memory_kind=document`, `메모 목록 보여줘`는 `memory_kind=memory`를 `resolved_slots`에 담도록 했다.
  - 실행 전 링크 검증은 `context_link=none`의 위험한 대상 슬롯은 계속 제거하되, `list_memory`의 안전한 범위 슬롯인 `memory_kind`는 보존하도록 했다.
  - `verification-preflight`의 `7.3`, `7.4` 케이스에 `expected_resolved_slots`를 추가해 파일/메모 목록 범위가 다시 빈 슬롯으로 퇴행하지 않게 했다.
  - 이 과정에서 `4.1` 내부 행동 기록 재사용 예행이 실패해, route validation이 제거한 후보도 대명사 매칭만으로 다시 살아나는 문제를 확인했다.
  - `filter_validation_removed_implicit_candidates()`를 조정해 내부 검증 이력으로 제거된 후보는 명시 대상 재지목이 있을 때만 다시 후보로 살리고, `그거 완료했어` 같은 대명사만으로는 재연결하지 않도록 했다.
  - `README.md`와 `discord_manual_verification.md`에 로컬 예행이 파일/메모 목록 범위의 `memory_kind` 슬롯 분리와 내부 검증 이력의 자동 연결 차단도 확인한다는 기준을 남겼다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_heuristics.py tests/test_route_validation.py tests/test_cli.py tests/test_router_agent.py tests/test_manual_verification_doc.py -q -k "list_memory_resolves_requested_kind or preserves_safe_list_memory_kind or manual_verification_preflight or validation or manual_verification_doc or readme_mentions"`(`239 passed, 314 deselected`), `python3 -m ruff check assistant_bot/agents/common.py assistant_bot/agents/memory.py assistant_bot/agents/__init__.py assistant_bot/agents/router.py assistant_bot/route_validation.py tests/test_router_heuristics.py tests/test_route_validation.py tests/test_cli.py tests/test_manual_verification_doc.py`, `python3 -m assistant_bot.cli verification-preflight`(`27개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1446 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`를 통과했고, EOF 공백 정리 후 `git diff --check`와 관련 집중 테스트(`4 passed, 353 deselected`)를 재통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 파일/메모 목록 범위 슬롯 실행 반영 강화

- 작업 이름: 라우터의 `memory_kind` 슬롯을 MemoryAgent 실행에서 우선 사용하도록 연결
- 진행상황: 완료
- 진행내용:
  - 라우터가 `memory_kind=document|memory`를 만들더라도 MemoryAgent가 다시 텍스트만 파싱하면, 라우터 판단과 실제 실행 사이에 어긋남이 생길 수 있다.
  - `MemoryAgent.list_memories()`가 `execution_context.resolved_slots.memory_kind`를 우선 사용하고, 슬롯이 없거나 유효하지 않을 때만 기존 텍스트 기반 `memory_list_kind()`를 fallback으로 쓰도록 했다.
  - `memory_kind`를 공개 후속 맥락 슬롯으로 인정하기 위해 `agent_catalog.json`의 `list_memory` state_outputs, `assistant_bot/agent_registry.py`의 컨텍스트 슬롯, `assistant_bot/agents/router.py`의 안전 내부 route 슬롯에 추가했다.
  - `tests/test_memory_store.py`에 문장 자체는 일반 `기억 목록 보여줘`여도 실행 컨텍스트가 `memory_kind=document`이면 파일/문서만 조회하는 회귀 테스트를 추가했다.
  - 관련 집중 검증으로 `python3 -m pytest tests/test_memory_store.py -q -k "kind_filter or memory_kind or list_memories_prefers"`(`1 passed, 124 deselected`), `python3 -m pytest tests/test_agent_registry.py -q -k "safe_execution_resolved_slots or declared_execution_resolved_slots or supported_context_contract_keys or SAFE_INTERNAL_ROUTE_SLOT_KEYS or CATALOG_TARGET_SLOT_NAMES"`(`4 passed, 92 deselected`), `python3 -m pytest tests/test_router_heuristics.py tests/test_route_validation.py tests/test_cli.py -q -k "list_memory_resolves_requested_kind or preserves_safe_list_memory_kind or manual_verification_preflight"`(`4 passed, 353 deselected`)를 통과했다.
  - 이후 `memory_kind`가 `resolved_slots`에서 턴 상태 슬롯으로 평탄화되어 다음 턴의 후속 맥락 힌트에도 남도록 `assistant_bot/bot.py`, `assistant_bot/models.py`, `tests/test_agent_registry.py`의 슬롯 계약을 함께 보강했다.
  - 재검증으로 `python3 -m pytest tests/test_agent_registry.py -q -k "target_slot_outputs_are_visible or target_slot_outputs_are_preserved or registry_fact_context_slot_keys or registry_context_key_sets or catalog_target_slot_contract or slot_outputs_are_available"`(`11 passed, 85 deselected`), `python3 -m ruff check assistant_bot/bot.py tests/test_agent_registry.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1447 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `python3 -m assistant_bot.cli verification-preflight`(`27개 통과`), `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-record 다음 검증 항목 즉시 안내

- 작업 이름: 수동 검증 기록 직후 다음 미기입 시나리오 안내
- 진행상황: 완료
- 진행내용:
  - `verification-record --next --status ...`로 판정을 기록한 뒤 다음 항목을 알기 위해 다시 `verification-status`를 실행해야 하는 마찰이 남아 있었다.
  - `record_manual_verification()`이 검증표를 갱신한 뒤 최신 상태를 다시 읽어 `next_missing_scenario`를 결과에 포함하도록 변경했다.
  - `format_manual_verification_record_result()`가 기록 완료 출력에 다음 미기입 시나리오, 입력, 기대 동작을 함께 표시하도록 보강했다.
  - `discord_manual_verification.md`와 `README.md`에 기록 직후 다음 항목으로 바로 이어가는 운영 흐름을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "record_manual_verification or manual_verification_doc or readme_mentions"`(`10 passed, 100 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`22개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1443 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `python3 -m assistant_bot.cli verification-status`는 실제 수동 검증표가 비어 있어 종료 코드 1과 `판정: 완료 불가`를 반환하지만, 다음 미기입 시나리오와 `verification-record --next` 기록 명령을 정상 출력한다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 유사 단어 일반 질문의 이전 작업 오연결 방지

- 작업 이름: 기존 작업 대상과 비슷한 단어가 들어간 일반 질문을 후속 작업 확인으로 오인하지 않도록 수정
- 진행상황: 완료
- 진행내용:
  - `병원 예약` 할 일 상태가 남아 있을 때 `병원 예약 방법 알려줘`가 일반 질문/검색 새 요청이 아니라 후속 작업 후보 확인(`clarify`)으로 빠지는 문제를 로컬 예행에서 재현했다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`의 `1.4` 케이스에 실제 할 일 상태를 seed하고, `context_link=none`과 `task_id` 미전파를 기대하도록 강화했다.
  - fallback 라우터의 다중 후보 확인 질문 조건을 조정해, 후보가 여러 개라도 현재 메시지에 `다시해봐`, `그거`, `방금` 같은 후속 신호가 없으면 기본 라우팅을 보존하도록 했다.
  - `README.md`와 `discord_manual_verification.md`에 기존 작업과 비슷한 단어가 들어간 일반 질문도 새 요청으로 분리하는 예행 기준을 명시했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py tests/test_router_agent.py tests/test_context_routing_matrix.py tests/test_route_validation.py -q -k "manual_verification_preflight or manual_verification_doc or readme_mentions or context or new_request or clarify or fallback"`(`561 passed, 154 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`23개 통과`), `python3 -m ruff check .`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1443 passed`), `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 완료형 후속 요청 로컬 예행 추가

- 작업 이름: `그거 완료했어`가 최근 할 일 후보에 안정적으로 연결되는지 verification-preflight로 고정
- 진행상황: 완료
- 진행내용:
  - 수동 검증표에는 같은 위치 후속 요청 1.3으로 `그거 완료했어`가 있지만, Discord 실행 전 로컬 예행에는 조회형 후속인 `방금 할 일 보여줘`만 있었다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 최근 할 일 3 상태를 seed한 뒤 `그거 완료했어`를 보내는 1.3 케이스를 추가했다.
  - 새 케이스는 `intent=manage_task`, `context_link=continue`, `resolved_slots.task_id=3`을 만족해야 통과한다.
  - 전체 문서 계약이 부정어 새 요청 오인 방지도 요구하고 있어, `아니 취소 말고 서울 날씨 알려줘`가 오래된 pending 거부로 소비되지 않고 `weather + none`으로 분리되는 2.6 케이스도 추가했다.
  - `assistant-admin verification-preflight` 기준 로컬 예행 문장 수를 26개로 늘리고, README, 수동 검증 문서, 문서 테스트의 개수 표현을 갱신했다.
  - 직접 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py tests/test_cli.py -q -k "manual_verification_doc or readme_mentions or manual_verification_preflight"`(`9 passed, 101 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`26개 통과`), `python3 -m ruff check .`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1443 passed`), `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 내부 추적 키 최종 답변 비노출 회귀 테스트 추가

- 작업 이름: 모델 출력에 내부 행동 추적 키가 섞여도 사용자 답변에서 제거되는지 고정
- 진행상황: 완료
- 진행내용:
  - 수동 검증표의 내부 행동 기록 재사용 축은 내부 기록을 참고하되 `linked_state_id`, `validation_context`, `pending_original_text`, `tool_call_trace`, `route_validation`, `*:result` 같은 내부 키를 사용자에게 노출하지 않는 것을 요구한다.
  - 기존 응답 작성자 테스트는 `linked_state_id`, `route_validation`, `*:result`, `validation_context` 등을 넓게 확인했지만, 모델 출력에 `tool_call_trace`가 직접 섞이는 경우를 별도 케이스로 고정하지는 않았다.
  - `tests/test_response_composer.py`에 `test_response_composer_sanitizes_internal_trace_keys_from_model_output`을 추가해 `tool_call_trace`, `route_context`, `validation_context`, `linked_state_id`, `context_link`, `task:result`, `route_validation`이 최종 답변에서 제거되는지 확인했다.
  - 직접 검증으로 `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_bot_helpers.py -q -k "internal_action or internal_trace or route_validation or private_route or hidden_reference or internal"`(`81 passed, 274 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`26개 통과`), `python3 -m ruff check .`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1444 passed`), `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 내부 검증 이력 기반 자동 연결 차단 preflight 추가

- 작업 이름: 내부 행동 기록이 라우터 예행에서 실제 자동 연결 차단 신호로 쓰이는지 고정
- 진행상황: 완료
- 진행내용:
  - 기존 `verification-preflight`는 최근 작업 상태 후보만 seed할 수 있어, 사용자에게 보이지 않는 `agent_logs` 기반 내부 행동 기록이 라우터 컨텍스트에 들어가는 흐름을 직접 예행하지 못했다.
  - `prepare_preflight_case_database()`에 `seed_logs`를 추가해 preflight 전용 SQLite에 `agent_logs`를 심을 수 있게 했다.
  - preflight 판정에 `forbidden_linked_state_ids`를 추가해 내부 검증 이력이 특정 state 자동 연결을 막는지 검사할 수 있게 했다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 4.1 내부 행동 기록 재사용 케이스를 추가했다. 이 케이스는 할 일 3 상태와 `route_validation` 로그를 함께 seed한 뒤 `그거 완료했어`가 `linked_state_id=1` 또는 `task_id=3`으로 자동 연결되지 않아야 통과한다.
  - README, 수동 검증 문서, 문서 테스트의 로컬 예행 수를 27개로 갱신하고, 내부 검증 이력의 자동 연결 차단을 예행 기준에 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py tests/test_context_builder.py tests/test_router_agent.py -q -k "manual_verification_preflight or manual_verification_doc or readme_mentions or internal_validation or internal_action or validation_guidance"`(`48 passed, 345 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`27개 통과`), `python3 -m ruff check .`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1446 passed`), `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `git diff --check` 중 발견된 `assistant_bot/agents/memory.py` EOF 여분 빈 줄도 함께 정리했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 검증 상태 출력과 memory_kind 슬롯 계약 보강

- 작업 이름: 수동 검증 게이트 오판 방지와 파일/메모 목록 범위 슬롯 보존 정합성 보강
- 진행상황: 완료
- 진행내용:
  - `verification-status` 출력 상단에 로컬 예행 기준 `27개`와 Discord 완료 기준 `8섹션 / 38개 세부 시나리오`를 함께 표시하도록 했다.
  - 이로써 `verification-preflight` 통과가 목표 완료가 아니라 실제 Discord 수동 검증 전 사전 점검이라는 점이 상태 출력에서도 바로 드러난다.
  - `tests/test_cli.py`에 새 출력 계약을 추가해 수동 검증 상태 출력이 로컬 예행 기준과 Discord 완료 기준을 계속 보여주도록 고정했다.
  - 전체 테스트 중 `memory_kind` 슬롯이 라우터/카탈로그에는 추가됐지만 런타임 턴 상태 보존 목록에는 빠져 있는 계약 불일치를 발견했다.
  - `assistant_bot/bot.py`와 `assistant_bot/models.py`의 안전한 턴 상태 슬롯 목록에 `memory_kind`를 포함해, `파일 목록 보여줘`와 `메모 목록 보여줘`의 범위 판단이 다음 턴 상태에서도 유실되지 않도록 했다.
  - `tests/test_agent_registry.py`의 목표 슬롯 샘플에도 `memory_kind`를 추가해 facts와 `resolved_slots`에서 턴 상태 슬롯으로 보존되는지 확인하게 했다.
  - `README.md`의 현재 자동 검증 결과를 최신 전체 테스트 수 `1447개 통과`로 갱신했다.
  - 직접 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py tests/test_cli.py tests/test_agent_registry.py -q -k "readme_mentions or manual_verification_status or target_slot_outputs or context_key_sets or target_slot_contract"`(`22 passed, 184 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`27개 통과`), `python3 -m assistant_bot.cli verification-status`를 확인했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1447 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `verification-status`는 실제 Discord 수동 검증표가 아직 비어 있어 `판정: 완료 불가`를 반환하며, 다음 미기입 시나리오 `1. 같은 위치 후속 요청 / 1`을 안내한다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 수동 검증 섹션 요약 기록 안내 보강

- 작업 이름: 세부 시나리오 통과 후 완료 판정 요약 누락을 바로 안내
- 진행상황: 완료
- 진행내용:
  - 실제 Discord 수동 검증 중 한 섹션의 세부 시나리오를 모두 `통과`로 채운 뒤 `완료 판정 요약`의 최종 판정이나 증거 위치를 빠뜨릴 수 있는 운영상 빈틈을 확인했다.
  - `collect_manual_verification_status()`가 섹션별 세부 시나리오가 모두 통과했지만 요약 판정 또는 증거 위치가 부족한 섹션을 `summary_record_needed`로 계산하도록 했다.
  - `verification-status` 출력에 `요약 기록 필요` 개수와 첫 번째 대상 섹션, `assistant-admin verification-record --section ... --status 통과 --evidence "증거 위치"` 명령을 표시하도록 했다.
  - `tests/test_cli.py`에 세부 시나리오 1섹션이 모두 통과했지만 요약이 비어 있을 때 요약 기록 명령을 안내하는 회귀 테스트를 추가했다.
  - `discord_manual_verification.md`와 `README.md`에 `요약 기록 필요` 안내를 따라 섹션 요약 판정과 증거를 채우는 흐름을 문서화했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification_status or summary_record or manual_verification_doc or readme_mentions"`(`21 passed, 90 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`29개 통과`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1448 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 수동 검증 통과 요약 증거 필수화

- 작업 이름: 섹션 요약을 통과로 기록할 때 유효한 증거 위치를 강제
- 진행상황: 완료
- 진행내용:
  - `verification-status`가 나중에 증거 누락을 잡아주더라도, `verification-record --section 1 --status 통과`처럼 섹션 요약 통과 판정만 먼저 기록하면 수동 검증표가 중간에 불완전해질 수 있는 지점을 확인했다.
  - `record_manual_verification()`에 `validate_manual_verification_summary_evidence()`를 추가해 섹션 요약을 `통과`로 기록할 때 기존 증거 또는 새 `--evidence`가 유효해야만 기록되도록 했다.
  - 유효 증거는 기존 `verification-status` 기준과 동일하게 Discord 메시지 링크, HTTP 링크, 스크린샷 파일명, 또는 `process.md` 참조로 판단한다.
  - `tests/test_cli.py`에 섹션 요약 통과 기록 시 증거가 없거나 `msg-1` 같은 placeholder면 거절하고, 기존 유효 증거가 있으면 재기록을 허용하는 회귀 테스트를 추가했다.
  - `discord_manual_verification.md`와 `README.md`에 섹션 요약 `통과` 기록에는 유효한 증거 위치가 필요하다는 운영 기준을 추가했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "record_manual_verification or manual_verification_doc or readme_mentions"`(`11 passed, 101 deselected`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1449 passed`), `python3 -m assistant_bot.cli verification-preflight`(`30개 통과`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `README.md`와 문서 계약 테스트의 자동 검증 결과를 `테스트 1449개 통과`로 갱신했다.
  - 현재 `verification-status`는 로컬 예행 기준 `30개`, Discord 완료 기준 `8섹션 / 38개 세부 시나리오`, 실제 수동 검증표 미기입으로 `판정: 완료 불가`를 출력한다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - verification-record 요약 기록 필요 후속 안내

- 작업 이름: 마지막 세부 시나리오 기록 직후 섹션 요약 기록 명령까지 안내
- 진행상황: 완료
- 진행내용:
  - `verification-record --next`로 마지막 미기입 세부 시나리오를 기록한 직후에는 다음 미기입 시나리오가 없어도 `완료 판정 요약`과 증거 위치가 아직 남아 있을 수 있다.
  - 기존 기록 완료 출력은 `다음 미기입 시나리오: 없음`만 보여줄 수 있어, 사용자가 `verification-status`를 다시 실행하기 전까지 섹션 요약 기록 필요를 놓칠 수 있는 흐름을 확인했다.
  - `attach_next_manual_verification_scenario()`가 최신 `summary_record_needed`도 결과에 포함하도록 했다.
  - `format_manual_verification_record_result()`가 다음 미기입 시나리오와 별개로 남은 `요약 기록 필요` 섹션과 `assistant-admin verification-record --section ... --status 통과 --evidence "증거 위치"` 명령을 함께 출력하도록 했다.
  - `tests/test_cli.py`에 마지막 세부 시나리오를 통과로 기록한 직후 다음 미기입 시나리오는 없지만 섹션 요약 기록 필요가 안내되는 회귀 테스트를 추가했다.
  - `discord_manual_verification.md`와 `README.md`에 `verification-record`가 기록 직후 다음 미기입 시나리오뿐 아니라 남은 `요약 기록 필요` 항목도 안내한다고 문서화했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "record_manual_verification or manual_verification_doc or readme_mentions"`(`12 passed, 101 deselected`), `python3 -m ruff check assistant_bot/cli.py tests/test_cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1450 passed`), `python3 -m assistant_bot.cli verification-preflight`(`31개 통과`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `README.md`와 문서 계약 테스트의 자동 검증 결과를 `테스트 1450개 통과`로 갱신했다.
  - 현재 `verification-status`는 로컬 예행 기준 `31개`, Discord 완료 기준 `8섹션 / 38개 세부 시나리오`, 실제 수동 검증표 미기입으로 `판정: 완료 불가`를 출력한다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - pending 승인 접두어형 새 검색 요청 매트릭스 보강

- 작업 이름: `네이버 검색해줘`가 오래된 pending 승인으로 소비되지 않는지 컨텍스트 매트릭스로 고정
- 진행상황: 완료
- 진행내용:
  - `verification-preflight`에는 `네이버 검색해줘`가 pending 승인으로 오인되지 않는 케이스가 있었지만, 더 넓은 `tests/test_context_routing_matrix.py`에는 같은 위험 축이 직접 고정되어 있지 않았다.
  - `naver_search_request_not_consumed_as_pending_approval` 매트릭스 케이스를 추가했다.
  - 이 케이스는 할 일 삭제 확인 pending 상태가 있는 상황에서 `네이버 검색해줘`가 `web_search`, `context_link=none`, `linked_state_id=None`으로 분리되어야 통과한다.
  - 이 보강은 `네`, `응` 같은 승인 접두어로 보일 수 있는 문자열이 실제 새 요청일 때 오래된 pending으로 소비되지 않도록 새 에이전트 추가 이후에도 회귀를 잡기 위한 것이다.
  - 직접 검증으로 `python3 -m pytest tests/test_context_routing_matrix.py tests/test_cli.py -q -k "naver_search_request_not_consumed_as_pending_approval or manual_verification_preflight"`(`3 passed, 320 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`31개 통과`), `python3 -m ruff check tests/test_context_routing_matrix.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1452 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `README.md`와 문서 계약 테스트의 자동 검증 결과를 `테스트 1452개 통과`로 갱신했다.
  - 현재 `verification-status`는 로컬 예행 기준 `31개`, Discord 완료 기준 `8섹션 / 38개 세부 시나리오`, 실제 수동 검증표 미기입으로 `판정: 완료 불가`를 출력한다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 다른 위치 새 요청 분리 preflight 보강

- 작업 이름: 다른 위치 작업 후보가 있어도 명확한 새 할 일/검색 요청은 현재 요청으로 분리되는지 로컬 예행에 추가
- 진행상황: 완료
- 진행내용:
  - 수동 검증표의 `3. 다른 위치 맥락`에는 다른 위치의 작업 후보가 있어도 `새 할 일 병원 예약 추가해줘`, `OpenAI 검색해줘`처럼 명확한 새 요청은 바로 실행되어야 한다는 항목이 있었다.
  - 기존 `verification-preflight`는 다른 위치 후속/재시도 요청의 `clarify`만 확인해, 반대로 새 요청을 과하게 이전 위치 맥락에 연결하지 않는지에 대한 자동 예행 근거가 약했다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 `3.4 새 할 일 병원 예약 추가해줘`, `3.5 OpenAI 검색해줘`를 추가했다.
  - 두 케이스 모두 다른 위치의 `장보기` 할 일 상태를 seed하고, 현재 메시지는 `context_link=none`이며 이전 `task_id=7`을 `resolved_slots`로 가져오지 않아야 통과한다.
  - `README.md`, `discord_manual_verification.md`, `tests/test_manual_verification_doc.py`의 로컬 예행 기준을 핵심 문장 `29개`로 갱신하고, 다른 위치 후보가 있어도 명확한 새 할 일/검색 요청은 `none`으로 분리한다는 기준을 문서화했다.
  - 직접 검증으로 `python3 -m pytest tests/test_manual_verification_doc.py tests/test_cli.py -q -k "readme_mentions or manual_verification_preflight or verification_status"`(`17 passed, 94 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`29개 통과`)를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1448 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `ruff`에 `README.md`를 직접 넘긴 별도 실수성 명령은 Markdown을 Python으로 파싱해 실패했지만, 프로젝트 표준 lint 명령인 `python3 -m ruff check .`는 정상 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 후보 선택 순서 복원 preflight 보강

- 작업 이름: 다중 재시도 후보에서 `두 번째` 선택도 원래 작업으로 정확히 복원되는지 로컬 예행에 추가
- 진행상황: 완료
- 진행내용:
  - 기존 `verification-preflight`는 다중 재시도 후보 선택에서 `첫 번째`만 확인해, 사용자가 `두 번째`를 고른 경우 후보 순서와 원래 작업 슬롯이 정확히 복원되는지 자동 근거가 약했다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 `2.multi_retry_select_second` 케이스를 추가했다.
  - 이 케이스는 실패한 웹 검색과 실패한 원주 날씨 조회 후보가 함께 있는 상태에서 `두 번째`를 보내면 `intent=weather`, `context_link=retry`, `resolved_slots.location=원주`, `pending_original_text=다시해봐`로 복원되어야 통과한다.
  - `README.md`, `discord_manual_verification.md`, `tests/test_manual_verification_doc.py`의 로컬 예행 기준을 핵심 문장 `30개`로 갱신하고, `첫 번째`, `두 번째` 같은 후보 선택 답변이 선택한 순서에 맞는 원래 작업을 복원한다는 기준을 문서화했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification_preflight or readme_mentions or manual_verification_doc or verification_status"`(`23 passed, 89 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`30개 통과`), `python3 -m ruff check assistant_bot/cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1449 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 승인 접두어 오인 방지 preflight 보강

- 작업 이름: `네이버 검색해줘`처럼 승인처럼 시작하지만 실제 새 요청인 문장을 pending 승인으로 오인하지 않도록 로컬 예행에 추가
- 진행상황: 완료
- 진행내용:
  - pending 확인 상태가 남아 있을 때 `네이버 검색해줘`가 `네` 승인 접두어처럼 보일 수 있어, 오래된 pending 작업 승인으로 소비되면 사용자가 명확히 요청한 새 검색을 놓치게 된다.
  - `MANUAL_VERIFICATION_PREFLIGHT_CASES`에 `2.4b 네이버 검색해줘` 케이스를 추가했다.
  - 이 케이스는 원주 날씨 재시도 pending 상태가 있어도 현재 메시지가 `web_search` 또는 `confirm_web_search`, `context_link=none`으로 분리되고, `location=원주`나 `pending_original_text=다시해봐`를 가져오지 않아야 통과한다.
  - `README.md`, `discord_manual_verification.md`, `tests/test_manual_verification_doc.py`의 로컬 예행 기준을 핵심 문장 `31개`로 갱신하고, `네이버`처럼 승인 접두어로 보일 수 있는 새 요청도 pending 승인으로 오인하지 않는다는 기준을 문서화했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py tests/test_manual_verification_doc.py -q -k "manual_verification_preflight or readme_mentions or manual_verification_doc or verification_status"`(`23 passed, 90 deselected`), `python3 -m assistant_bot.cli verification-preflight`(`31개 통과`), `python3 -m ruff check assistant_bot/cli.py tests/test_manual_verification_doc.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1450 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 후보 선택 대기 원문 매칭 회귀 테스트 추가

- 작업 이름: 후보 선택 처리 후 pending 대기 만료가 원래 사용자 문장과 일치할 때만 일어나도록 고정
- 진행상황: 완료
- 진행내용:
  - 다중 후보 선택 대기는 사용자가 `첫 번째`, `두 번째`처럼 짧게 답하는 구조라, 오래된 후보 선택 대기가 남아 있으면 엉뚱한 pending 상태를 닫아버릴 위험이 있다.
  - 기존 테스트는 선택된 pending 하나만 만료하고 다른 pending은 남긴다는 점을 확인했지만, `pending_original_text`가 빠진 route가 후보 대기를 만료하지 않는다는 직접 회귀 테스트는 없었다.
  - `tests/test_cli.py`에 `test_cli_does_not_expire_pending_candidate_without_original_text_match`를 추가해 `pending_original_text`가 없는 선택 복원 route는 pending 후보 선택 대기를 만료하지 않도록 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_cli.py -q -k "expires_selected_pending_candidate or original_text_match"`(`2 passed, 105 deselected`), `python3 -m ruff check tests/test_cli.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1451 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `README.md`와 문서 계약 테스트의 자동 검증 결과를 `테스트 1451개 통과`로 갱신했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 내부 행동 route 슬롯 memory_kind 보존

- 작업 이름: 내부 행동 기록의 route_context에서도 파일/메모 목록 범위 슬롯을 잃지 않도록 보강
- 진행상황: 완료
- 진행내용:
  - `memory_kind`는 라우터, 실행 컨텍스트, 턴 상태 슬롯에서는 안전 슬롯으로 보존되지만, 내부 행동 로그의 `route_context.resolved_slots`를 다시 파싱할 때 쓰는 허용 목록에는 빠져 있었다.
  - 이 상태에서는 `파일 목록 보여줘`, `메모 목록 보여줘` 같은 범위 판단이 내부 행동 기록으로 재참조될 때 `document|memory` 구분 단서가 사라질 수 있다.
  - `assistant_bot/context_builder.py`의 `INTERNAL_ACTION_ROUTE_SLOT_KEYS`에 `memory_kind`를 추가했다.
  - `tests/test_router_agent.py`에 `test_router_parses_internal_action_route_context_preserves_memory_kind`를 추가해 내부 route context 파싱에서 `memory_kind=document`는 보존하고 `pending_original_text` 같은 내부 원문 슬롯은 계속 제거되는지 고정했다.
  - 직접 검증으로 `python3 -m pytest tests/test_router_agent.py tests/test_context_builder.py -q -k "memory_kind or internal_action_route_context or internal_action_context"`(`3 passed, 281 deselected`), `python3 -m ruff check assistant_bot/context_builder.py tests/test_router_agent.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1453 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `README.md`와 문서 계약 테스트의 자동 검증 결과를 `테스트 1453개 통과`로 갱신했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - pending 내부 키 최종 답변 비노출 회귀 테스트 보강

- 작업 이름: pending 후보/취소 내부 키가 모델 출력에 섞여도 사용자 답변에서 제거되는지 고정
- 진행상황: 완료
- 진행내용:
  - 맥락 선택, 후보 선택, pending 취소 기능이 늘어나면서 `pending_candidate_state_ids`, `pending_candidate_urls`, `pending_candidate_url_titles`, `pending_context_link`, `cancelled_pending_linked_state_id` 같은 내부 키가 최종 답변에 섞일 위험이 생겼다.
  - 사용자는 내부 라우팅 상태를 볼 필요가 없으므로, 이런 값이 모델 출력에 들어와도 자연스러운 사용자 답변만 남아야 한다.
  - `tests/test_response_composer.py`에 `test_response_composer_sanitizes_pending_internal_keys_from_model_output`을 추가했다.
  - 이 테스트는 모델이 pending 내부 키와 값을 그대로 출력해도 최종 응답이 `취소했어요.`처럼 짧은 자연어로 정리되는지 확인한다.
  - 직접 검증으로 `python3 -m pytest tests/test_response_composer.py tests/test_context_builder.py tests/test_bot_helpers.py -q -k "pending_internal_keys or internal_trace or private_metadata or internal_action or hidden_reference or route_validation"`(`47 passed, 309 deselected`), `python3 -m ruff check tests/test_response_composer.py assistant_bot/response_composer.py assistant_bot/models.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1454 passed`), `python3 -m assistant_bot.cli verification-preflight`(`31개 통과`), `python3 -m ruff check .`를 통과했다.
  - 문서 갱신 후 재검증으로 `python3 -m pytest tests/test_manual_verification_doc.py tests/test_response_composer.py -q -k "readme_mentions or pending_internal_keys"`(`2 passed, 56 deselected`), `python3 -m compileall assistant_bot tests`, `git diff --check`, `python3 -m ruff check .`를 통과했다.
  - `python3 -m assistant_bot.cli verification-status`는 로컬 예행 기준 `31개`, Discord 완료 기준 `8섹션 / 38개 세부 시나리오`, 진행률 `0/38`, `판정: 완료 불가`를 출력했다.
  - `README.md`와 문서 계약 테스트의 자동 검증 결과를 `테스트 1454개 통과`로 갱신했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.

## 2026-06-08 - 내부 route 슬롯 계약 테스트 강화

- 작업 이름: 카탈로그 목표 슬롯과 내부 action route 슬롯 허용 목록을 동일 계약으로 고정
- 진행상황: 완료
- 진행내용:
  - `memory_kind` 누락처럼 특정 슬롯이 라우터/실행/턴 상태에는 보존되지만 내부 action route context 재파싱에서는 사라지는 문제가 다시 생길 수 있어, 허용 목록 간 계약을 더 강하게 묶었다.
  - `CONTEXT_TARGET_SLOT_KEYS`, `SAFE_INTERNAL_ROUTE_SLOT_KEYS`, `TURN_STATE_TARGET_HINT_SLOT_KEYS`, `INTERNAL_ACTION_ROUTE_SLOT_KEYS`가 같은 목표 슬롯 집합을 공유하도록 `tests/test_agent_registry.py`의 계약 테스트를 보강했다.
  - 계약 테스트를 추가하며 `INTERNAL_ACTION_ROUTE_SLOT_KEYS`에서 빠져 있던 `due_at`, `human_due_at`, `remind_at`, `human_remind_at`도 함께 보존 목록에 추가했다.
  - 이 보강으로 할 일/알림의 시간 관련 후속 맥락도 내부 행동 기록 route_context에서 유실되지 않는다.
  - 직접 검증으로 `python3 -m pytest tests/test_agent_registry.py tests/test_router_agent.py tests/test_context_builder.py -q -k "catalog_target_slot_contract or memory_kind or internal_action_route_context"`(`3 passed, 377 deselected`), `python3 -m ruff check assistant_bot/context_builder.py tests/test_agent_registry.py tests/test_router_agent.py`를 통과했다.
  - 최종 전체 검증으로 `python3 -m pytest -q`(`1454 passed`), `python3 -m ruff check .`, `python3 -m compileall assistant_bot tests`, `git diff --check`를 통과했다.
  - `README.md`와 문서 계약 테스트의 자동 검증 결과를 `테스트 1454개 통과`로 갱신했다.
  - 아직 목표 완료 조건은 실제 Discord 환경에서 38개 세부 시나리오를 실행하고 판정/증거를 채우는 것이다.
