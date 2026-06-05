# Discord 대화형 범용 비서

Discord에서 멘션, 답글, DM으로 대화하는 개인 비서다. 사용자가 명시적으로 요청한 메모와 파일만 장기 기억에 저장하고, 질문이 들어오면 관련 기억을 검색해 답한다.

## 주요 기능

- 슬래시 명령어 없이 자연어 대화로 동작
- 멘션, 봇 메시지 답글, DM에서만 응답
- 명시적 요청이 있을 때만 장기 기억 저장
- 같은 사용자의 장기 기억은 DM, 서버, 스레드 어디서든 유지
- 답변과 상태 확인에서 현재 대화 위치 인지
- 텍스트 메모, `.txt`, `.md`, `.pdf`, `.docx`, `.xlsx`, `.csv` 첨부 저장
- 이미지, 스캔 PDF, 중요 시각 자료가 포함된 혼합 PDF를 `gpt-5.4-mini` 비전 OCR로 분석
- 비전 OCR은 이미지 detail `auto`, 1회 10MB, 사용자별 하루 50MB 제한
- UTF-8이 아니거나 의미 있는 텍스트가 없는 첨부 저장 방지
- 동일한 텍스트 메모 중복 저장 방지
- 동일한 문서 내용 중복 저장 방지
- SQLite 기반 로컬 기억 저장소
- embedding 기반 의미 검색
- 자연어 기억 목록 조회와 상태 확인
- 자연어 도움말과 봇 상태 확인
- 오늘 브리핑으로 오늘까지 할 일, 최근 기억, 최근 대화 위치 확인
- 현재 대화 맥락 초기화
- 자연어 기반 사용자별 할 일 추가, 중복 방지, 상세 조회, 전체/오늘 목록 조회, 최근 대화 추출, 제목/우선순위 수정, 완료, 완료 취소, 미루기, 삭제
- 할 일과 분리된 사용자 알림 요청 등록 및 DM 발송
- ID 기반 메모/문서 상세 조회
- ID 또는 관련 키워드 기반 텍스트 메모 수정
- ID, 키워드, 의미 검색 기반 기억 삭제
- 가장 최근에 저장한 기억 삭제
- 삭제한 기억 목록 조회와 ID 기반 복구
- 가장 최근에 삭제한 기억 복구
- 확인 후 사용자 기준 장기 기억 전체 삭제
- 첨부만 보낸 뒤 봇 확인 메시지에 답장해 저장하는 흐름
- 첨부 저장 확인 대기 상태 취소
- 지원하지 않는 첨부 파일 안내
- `방금 말한 거 기억해줘`, `그거 기억해줘`처럼 직전 발화를 장기 기억으로 저장
- `Router Agent`, `Conversation Agent`, `Memory Agent`, `Task Agent`, `Reminder Agent`, `Utility Agent` 구조
- 봇이 할 수 있는 일과 할 수 없는 일을 `assistant_bot/capabilities.py` 기준으로 일관되게 판단
- 에이전트 목적, 설명, 예시는 `agent_catalog.json`에서 관리
- `Conversation Agent`와 `Memory Agent` 일반 회상은 필요할 때 read-only tool calling으로 기억/할 일 조회
- 라우터는 `gpt-5.4-mini` 고정 사용
- 전문 에이전트는 난이도와 사용자 선호에 따라 모델 선택

## 설치

```bash
python3 -m pip install -e '.[dev]'
```

## 환경 변수

`.env.example`을 참고해 `.env` 파일을 만든다. 실제 값은 저장소에 커밋하지 않는다.

필수 값:

```bash
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
```

OpenAI 호출은 기본적으로 30초 timeout과 2회 재시도를 사용한다. 필요하면 `.env`에서 `OPENAI_TIMEOUT_SECONDS`, `OPENAI_MAX_RETRIES`를 조정한다.

할 일 날짜 계산은 기본적으로 `Asia/Seoul` 기준이다. 필요하면 `.env`에서 `ASSISTANT_TIMEZONE`을 IANA 타임존 이름으로 조정한다.

알림 발송 루프는 기본적으로 1분 단위 설정을 사용하되 실제 확인은 최대 15초 간격으로 수행하고, 설정 타임존 기준으로 예약 시각이 지난 항목을 사용자 DM으로 한 번 알려준다. 서버 채널에서 요청한 알림도 채널 멘션이 아니라 DM으로 발송한다. 필요하면 `.env`에서 `TASK_REMINDER_INTERVAL_MINUTES`, `TASK_REMINDER_BATCH_SIZE`를 조정한다.

로그는 기본적으로 콘솔에 출력된다. 필요하면 `.env`에서 `LOG_LEVEL`로 로그 레벨을 조정하고, `LOG_FILE`을 지정해 파일에도 기록한다.

Discord 서버에서 봇이 메시지를 읽으려면 Developer Portal에서 Message Content Intent를 활성화해야 한다.

## 실행

```bash
assistant-bot
```

또는:

```bash
python3 -m assistant_bot.main
```

## 운영 도구

환경 변수와 기본 설정을 점검한다. 실제 비밀값은 출력하지 않는다. 예시 토큰, 숫자 설정, 타임존, SQLite 저장 경로도 함께 확인한다.

```bash
assistant-admin doctor
```

OpenAI 텍스트 응답 모델과 embedding 모델 연결을 점검한다. 실제 비밀값은 출력하지 않는다.

```bash
assistant-admin openai-check
```

Discord 봇 초대 URL을 생성한다. `DISCORD_CLIENT_ID`가 필요하다.

```bash
assistant-admin invite
```

SQLite 저장소를 생성하고 핵심 테이블 준비 상태를 확인한다.

```bash
assistant-admin init-db
```

SQLite 저장소의 기억, 문서, 할 일, 대화, 대기 첨부, 로그 개수를 확인한다.

```bash
assistant-admin stats
```

사용자별 저장 데이터 현황을 확인한다. 메모, 문서, 할 일, 삭제 항목 수를 함께 보여준다.

```bash
assistant-admin users
assistant-admin users --limit 50
```

최근 저장된 메모와 문서를 목록으로 확인한다.

```bash
assistant-admin memories --limit 20
assistant-admin memories --user-id 123456789
assistant-admin memories --kind document
```

삭제된 메모와 문서를 목록으로 확인한다.

```bash
assistant-admin deleted --limit 20
assistant-admin deleted --user-id 123456789
assistant-admin deleted --kind document
```

삭제된 메모와 문서를 ID로 복구한다.

```bash
assistant-admin undelete --user-id 123456789 --memory-id 3
assistant-admin undelete --user-id 123456789 --document-id 2
```

저장된 메모, 문서, 할 일을 JSON으로 내보낸다. embedding 벡터는 포함하지 않는다.

```bash
assistant-admin export --output assistant-data.json
assistant-admin export --user-id 123456789 --output user-data.json
```

저장된 메모, 문서, 할 일을 키워드로 검색한다. OpenAI API 호출 없이 로컬 SQLite에서 검색한다.

```bash
assistant-admin search 운동
assistant-admin search 운동 --user-id 123456789
```

Discord에 올리지 않고 로컬 파일을 바로 사용자 장기 기억 문서로 저장한다. `.txt`, `.md`, `.pdf`, `.docx`, `.xlsx`, `.csv`를 지원한다.

```bash
assistant-admin ingest ./meeting.md --user-id 123456789
assistant-admin ingest ./notes.md ./plan.pdf --user-id 123456789
```

첨부 파일 분석은 별도 문서 분석 에이전트가 처리한다. 텍스트만 있는 문서는 로컬에서 추출해 분석하므로 비전 OCR 한도에서 차감하지 않는다. 이미지, 스캔 PDF, 중요 시각 자료가 포함된 혼합 PDF는 `gpt-5.4-mini`와 이미지 detail `auto`로 분석하며, 1회 10MB, 사용자별 하루 50MB 제한을 적용한다. 혼합 PDF는 먼저 페이지 이미지를 비전으로 선별하고, 차트/표/그래프/도식처럼 중요한 페이지에 대해서만 이미지 분석을 추가한다.

OpenAI 호출 없이 휴리스틱 fallback 기준 intent를 빠르게 확인한다. 실제 봇은 라우팅 모델을 먼저 사용하므로,
최종 판단은 `assistant-admin ask`나 Discord 실행 경로에서 확인한다.

```bash
assistant-admin route "이거 기억해줘: 나는 오전에 집중이 잘 돼"
assistant-admin route "이 파일 기억해줘" --attachments
```

Discord를 켜기 전에 로컬에서 실제 에이전트, OpenAI, SQLite 흐름으로 텍스트 대화를 실행한다.

```bash
assistant-admin ask "이거 기억해줘: 나는 오전에 집중이 잘 돼" --user-id local-test
assistant-admin ask "내가 오전 집중을 선호한다고 기억하고 있어?" --user-id local-test
```

오늘까지 할 일과 최근 기억을 한 번에 확인한다.

```bash
assistant-admin briefing --user-id 123456789
```

사용자별 기억, 할 일, 대기 작업, 최근 대화 위치를 한 번에 점검한다.

```bash
assistant-admin snapshot --user-id 123456789
assistant-admin snapshot --user-id 123456789 --limit 10
```

저장된 대화 컨텍스트 현황을 확인한다.

```bash
assistant-admin conversations
assistant-admin conversations --limit 50
```

특정 대화 컨텍스트의 메시지와 요약을 초기화한다. 장기 기억과 저장 문서는 유지한다.

```bash
assistant-admin clear-conversation --conversation-id dm:123456789
```

사용자별 할 일을 조회하거나 관리한다. Discord 없이도 열린 작업을 추가, 완료, 삭제하고 삭제한 항목을 복구할 수 있다.

```bash
assistant-admin tasks --user-id 123456789
assistant-admin tasks --user-id 123456789 --due-after 2026-06-05 --due-before 2026-06-05
assistant-admin tasks --user-id 123456789 --due-before 2026-06-10
assistant-admin tasks --user-id 123456789 --undated
assistant-admin tasks --user-id 123456789 --add "제안서 초안 작성" --priority high --due 2026-06-10
assistant-admin tasks --user-id 123456789 --show 3
assistant-admin tasks --user-id 123456789 --rename 3 --title "고객 미팅 준비"
assistant-admin tasks --user-id 123456789 --set-priority 3 --priority low
assistant-admin tasks --user-id 123456789 --reopen 3
assistant-admin tasks --user-id 123456789 --postpone 3 --due 2026-06-12
assistant-admin tasks --user-id 123456789 --complete 3 --status all
assistant-admin tasks --user-id 123456789 --delete 4
assistant-admin tasks --user-id 123456789 --deleted
assistant-admin tasks --user-id 123456789 --restore 4 --status all
```

예약 시각이 지났지만 아직 발송되지 않은 사용자 알림 대상을 미리 확인한다.

```bash
assistant-admin reminders
assistant-admin reminders --user-id 123456789
assistant-admin reminders --as-of "2026-06-10 09:30"
```

최근 에이전트 라우팅과 모델 선택 로그를 조회한다.

```bash
assistant-admin logs --limit 20
assistant-admin logs --agent router
assistant-admin logs --conversation-id dm:123456789
```

오래된 대화 기록, 운영 로그, 해결된 첨부 대기 요청, 삭제된 기억/문서/할 일을 정리한다. `--force`가 없으면 삭제하지 않고 대상 개수만 미리 보여준다.

```bash
assistant-admin cleanup --days 30
assistant-admin cleanup --days 90 --target logs
assistant-admin cleanup --days 90 --target deleted
assistant-admin cleanup --days 30 --target conversations --force
```

SQLite 저장소 전체를 백업한다. embedding과 로그를 포함한 전체 테이블을 보존한다.

```bash
assistant-admin backup --output backup.sqlite
```

SQLite 백업 파일로 저장소를 복구한다. 현재 저장소는 복구 전에 자동으로 안전 백업된다.

```bash
assistant-admin restore --input backup.sqlite --force
```

## 사용 예시

텍스트 기억:

```text
@봇 이거 기억해줘: 나는 오전에 집중이 잘 돼.
```

파일 기억:

```text
@봇 이 파일 기억해줘.
```

첨부만 먼저 보낸 경우:

```text
사용자: @봇 [meeting.pdf 첨부]
봇: 첨부를 확인했어요. 기억해두길 원하면 이 메시지에 “응, 기억해줘”라고 답장해 주세요.
사용자: 응, 기억해줘
```

첨부 저장 취소:

```text
사용자: 취소해
```

질문:

```text
@봇 전에 저장한 회의 문서 기준으로 다음 할 일 정리해줘.
```

기억 목록:

```text
@봇 지금 뭘 기억하고 있어?
```

상세 조회:

```text
@봇 메모 3 보여줘.
@봇 문서 2 보여줘.
```

기억 수정:

```text
@봇 메모 3을 나는 저녁 운동을 선호한다로 수정해줘.
@봇 운동 관련 기억을 나는 저녁 운동을 선호한다로 바꿔줘.
```

도움말:

```text
@봇 도움말 보여줘.
```

상태 확인:

```text
@봇 상태 확인해줘.
```

상태 응답에는 현재 대화 위치, 전체 기억 수, 열린 할 일 수가 함께 표시된다.

오늘 브리핑:

```text
@봇 오늘 브리핑 해줘.
```

브리핑은 오늘까지 처리해야 하는 열린 할 일, 열린/완료 할 일 수, 최근 저장 기억을 함께 보여준다.

대화 맥락 초기화:

```text
@봇 대화 맥락 초기화해줘.
```

이 기능은 현재 DM, 채널, 스레드의 최근 대화 기록과 요약만 초기화하며 장기 기억은 유지한다.

할 일 관리:

```text
@봇 할 일 추가: 금요일까지 제안서 초안 작성.
@봇 할 일 추가: 3일 뒤까지 제안서 초안 작성.
@봇 할 일 추가: 내일 오전 9시까지 제안서 초안 작성.
@봇 할 일 추가: 다음 주 금요일까지 회의자료 정리.
사용자: 제안서 초안 작성해야겠다.
사용자: @봇 그거 할 일로 추가해줘.
@봇 할 일 목록 보여줘.
@봇 완료한 할 일 보여줘.
@봇 전체 할 일 목록 보여줘.
@봇 오늘 할 일 뭐야?
@봇 내일 할 일 뭐야?
@봇 이번 주 할 일 보여줘.
@봇 기한 없는 할 일 보여줘.
@봇 최근 대화에서 할 일 뽑아줘.
@봇 최근 대화에서 할 일 뽑아서 추가해줘.
@봇 할 일 3을 고객 미팅 준비로 바꿔줘.
@봇 할 일 3 중요하게 표시해줘.
@봇 할 일 3 내일 다시 알려줘.
@봇 할 일 3 완료했어.
@봇 제안서 할 일 완료했어.
@봇 회의자료 할 일 3일 뒤 다시 알려줘.
@봇 제안서 할 일 내일 오후 3시 다시 알려줘.
@봇 할 일 3 다시 열어줘.
@봇 할 일 4 삭제해줘.
```

알림 예약:

```text
@봇 내일 오전 9시에 물 마시라고 알려줘.
@봇 30분 뒤 스트레칭하라고 알려줘.
@봇 2시간 후 다시 알려줘.
@봇 현재 등록되어 있는 알림 목록.
@봇 내가 아까 몇시에 알림 보내달라고 했지?
```

기한 표현은 `오늘`, `내일`, `모레`, `30분 뒤`, `2시간 후`, `3일 뒤`, `2주 후`, `이번 주 금요일`, `다음 주 금요일`, `2026-06-10`, `6월 10일`, `오전 9시`, `18:30`, `오후 3시`처럼 말할 수 있다.

할 일은 사용자 기준으로 저장되므로 같은 사용자가 DM, 서버, 스레드 어디에서 말해도 같은 목록을 볼 수 있다.
완료, 삭제, 미루기, 우선순위 변경은 ID 없이도 키워드가 하나의 열린 할 일로 명확히 좁혀지면 처리한다. 여러 개가 맞으면 ID를 다시 물어본다.
할 일의 기한은 마감/정렬 기준이고, `30분 뒤 물 마시라고 알려줘` 같은 알림 요청은 할 일 목록이 아니라 알림 전용 저장소에 등록된다.
알림은 요청 위치가 DM, 서버, 스레드 어디든 시간이 되면 사용자 DM으로 발송된다.
할 일을 미루려면 `할 일 3 내일 다시 알려줘`처럼 대상 할 일을 명시한다.
`오늘 할 일 뭐야?`, `내일 할 일 뭐야?`, `이번 주 할 일 보여줘`, `기한 없는 할 일 보여줘`처럼 목록 범위를 바꿔 볼 수 있다.
`최근 대화에서 할 일 뽑아줘`는 후보만 보여주고, `최근 대화에서 할 일 뽑아서 추가해줘`라고 말해야 실제 할 일로 저장한다.
직전에 말한 내용을 바로 할 일로 만들고 싶으면 `그거 할 일로 추가해줘`처럼 말할 수 있다.
추출되거나 급히 저장된 할 일 제목은 `할 일 3을 ...로 바꿔줘`처럼 나중에 고칠 수 있다.
할 일 우선순위는 높음, 보통, 낮음으로 관리되며 목록, 브리핑, 리마인더에서 높은 우선순위가 먼저 보인다.
실수로 완료 처리한 할 일은 `할 일 3 다시 열어줘`로 열린 상태로 되돌릴 수 있다.

기억 삭제:

```text
@봇 운동 관련 기억 삭제해줘.
```

ID로 삭제:

```text
@봇 메모 3 삭제해줘.
@봇 문서 2 삭제해줘.
```

최근 저장 항목 삭제:

```text
@봇 방금 저장한 거 지워줘.
```

직전 발화 기억:

```text
사용자: 나는 회의 전 10분 준비 시간을 선호한다.
사용자: @봇 그거 기억해줘.
```

이 흐름은 `그거` 자체가 아니라 바로 전 사용자 발화를 저장한다.

최근 삭제 항목 복구:

```text
@봇 삭제한 기억 목록 보여줘.
@봇 메모 3 복구해줘.
@봇 방금 지운 거 복구해줘.
```

전체 삭제:

```text
@봇 내 기억 전부 삭제해줘.
봇: 정말 사용자 기준 저장 기억 전체를 삭제할까요?
사용자: 응, 전부 삭제해.
```

전체 삭제 확인과 첨부 저장 확인은 기본 10분 안에 답장해야 하며, `.env`에서 `PENDING_CONFIRMATION_TTL_MINUTES`로 조정할 수 있다.
`응`, `ok` 같은 짧은 긍정만으로는 전체 삭제가 실행되지 않고, `응, 전부 삭제해`처럼 전체 범위와 삭제 의사가 함께 들어간 답장이 필요하다.

첨부 파일만 보내면 봇은 자동 저장하지 않고, 기억할지 확인한다.

## 검증

```bash
python3 -m pytest
python3 -m ruff check .
```

현재 자동 검증 결과:

- 테스트 163개 통과
- Ruff lint 통과
- `python3 -m compileall assistant_bot tests` 통과
- `assistant-admin doctor`, `assistant-admin invite`, `assistant-admin stats`, `assistant-admin export`, `assistant-admin search`, `assistant-admin backup` 실행 확인
- `assistant-admin export --help` 실행 확인
- `assistant-admin users --help` 실행 확인
- `assistant-admin memories --help` 실행 확인
- `assistant-admin deleted --help` 실행 확인
- `assistant-admin undelete --help` 실행 확인
- `assistant-admin ingest --help` 실행 확인
- `assistant-admin route` 실행 확인
- `assistant-admin ask --help` 실행 확인
- `assistant-admin snapshot --help` 실행 확인
- `assistant-admin conversations --help` 실행 확인
- `assistant-admin clear-conversation --help` 실행 확인
- `assistant-admin tasks --help` 실행 확인
- `assistant-admin reminders --help` 실행 확인
- `assistant-admin tasks` 추가, 조회, 오늘까지 필터, 제목/우선순위 수정, 미루기, 완료, 다시 열기, 삭제 항목 조회, 복구 실행 확인
- `assistant-admin route "최근 대화에서 할 일 뽑아서 추가해줘"` 실행 확인
- `assistant-admin briefing --help` 실행 확인
- `assistant-admin briefing` 실행 확인
- 발송 대기 알림 대상 조회와 전송 표시 동작 확인
- `assistant-admin cleanup --help` 실행 확인
- `assistant-admin openai-check --help` 실행 확인
- `assistant-admin logs --help` 실행 확인
- `assistant-admin restore --help` 실행 확인
