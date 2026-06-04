# 에이전트 카탈로그 기반 라우팅 및 모듈화 계획

## 목적

초기 구현은 `RouterAgent`, `MemoryAgent`, `TaskAgent`, `ConversationAgent`, `UtilityAgent`처럼 에이전트 책임이 클래스 단위로 분리되어 있었지만, 대부분의 코드가 `assistant_bot/agents.py`에 모여 있었고 라우팅 intent 설명과 실행 분기가 `agents.py`, `bot.py`, `cli.py`, `models.py`에 수동으로 흩어져 있었다.

이 계획의 목적은 새 에이전트를 추가할 때 다음 흐름에 가깝게 만드는 것이다.

```text
새 에이전트 구현
`agent_catalog.json`에 목적, 설명, 예시 등록
Python registry에서 핸들러 연결
라우터가 에이전트 목록을 참고
등록된 핸들러가 실행
```

즉, 에이전트가 늘어나도 중앙 분기문을 계속 키우지 않고, “에이전트 목록”을 시스템의 중심으로 삼는다.

## 기대값

- 새 에이전트 추가 시 수정해야 하는 위치를 줄인다.
- 라우터 모델이 각 에이전트의 목적과 예시를 일관되게 참고하도록 한다.
- Discord 실행 경로와 로컬 CLI 실행 경로가 같은 dispatch 정책을 쓰도록 한다.
- 등록 누락, intent 불일치, 핸들러 누락을 테스트로 잡을 수 있게 한다.
- 향후 일정, 리서치, 코딩, 문서 작성 같은 전문 에이전트를 추가하기 쉬운 구조를 만든다.

## 현재 구조

현재 에이전트 클래스는 `assistant_bot/agents/` 패키지 안에 파일 단위로 분리되어 있다.

- `RouterAgent`: 사용자 메시지를 intent로 분류한다.
- `MemoryAgent`: 기억 저장, 조회, 수정, 삭제, 복구를 처리한다.
- `TaskAgent`: 할 일 추가, 조회, 완료, 미루기, 삭제, 리마인더 관련 요청을 처리한다.
- `ConversationAgent`: 일반 대화와 기억 기반 답변을 처리한다.
- `UtilityAgent`: 도움말, 상태 확인, 오늘 브리핑, 대화 맥락 초기화를 처리한다.

현재 실행 연결은 다음 위치로 정리되어 있다.

- `assistant_bot/models.py`: `RouteIntent` 타입 정의
- `agent_catalog.json`: 라우터가 참고하는 에이전트 목적, 설명, 예시
- `assistant_bot/agent_registry.py`: JSON 카탈로그 로딩, 핸들러 바인딩, 공통 dispatch
- `assistant_bot/agents/`: 라우터, 기억, 할 일, 대화, 유틸리티 에이전트와 공통 휴리스틱
- `assistant_bot/bot.py`: Discord orchestration과 registry dispatch 연결
- `assistant_bot/cli.py`: 로컬 `assistant-admin ask`의 registry dispatch 연결

## 목표 구조

### 1. 에이전트 파일 단위 모듈화

`assistant_bot/agents/` 패키지를 만들고 에이전트별 파일로 분리한다.

```text
assistant_bot/agents/
  __init__.py
  router.py
  memory.py
  task.py
  conversation.py
  utility.py
  common.py
```

역할은 다음과 같이 둔다.

- `router.py`: 라우터 에이전트와 라우팅 결과 파싱
- `memory.py`: 기억 에이전트
- `task.py`: 할 일 에이전트
- `conversation.py`: 대화 에이전트
- `utility.py`: 유틸리티 에이전트
- `common.py`: 휴리스틱 라우팅, 자연어 판별, 텍스트 추출 헬퍼

기존 import 호환성을 유지하기 위해 `assistant_bot/agents/__init__.py`에서 주요 클래스와 함수를 re-export한다.

### 2. 에이전트 정의 객체 추가

새 모듈 `assistant_bot/agent_registry.py`를 추가한다.

핵심 데이터 구조는 다음과 같이 둔다.

```python
@dataclass(frozen=True)
class AgentDefinition:
    intent: str
    name: str
    purpose: str
    description: str
    examples: tuple[str, ...]
    handler: Callable[..., Awaitable[str] | str]
```

각 필드의 의미는 다음과 같다.

- `intent`: 라우터가 반환하는 intent 값
- `name`: 사람이 읽는 에이전트 이름
- `purpose`: 한 줄 목적
- `description`: 라우터가 참고할 상세 설명
- `examples`: 해당 에이전트로 보내야 하는 대표 사용자 발화
- `handler`: 실제 실행 함수

`intent`, `name`, `purpose`, `description`, `examples`는 `agent_catalog.json`에서 읽고, `handler`는 Python registry factory에서 연결한다.

### 3. 에이전트 레지스트리 추가

`AgentRegistry`는 등록된 에이전트를 보관하고 라우터와 실행부에 필요한 인터페이스를 제공한다.

필수 메서드는 다음과 같이 둔다.

```python
class AgentRegistry:
    def register(self, definition: AgentDefinition) -> None: ...
    def get(self, intent: str) -> AgentDefinition | None: ...
    def intents(self) -> list[str]: ...
    def routing_prompt_block(self) -> str: ...
    async def dispatch(self, intent: str, context: AgentContext) -> str: ...
```

`routing_prompt_block()`은 라우터 프롬프트에 들어갈 에이전트 목록을 만든다.

예시:

```text
- manage_task: Task Agent
  목적: 개인 할 일 추가, 조회, 완료, 미루기, 삭제, 리마인더 처리
  예시: "오늘 할 일 뭐야?", "30분 뒤 물 마시라고 알려줘"
```

### 4. 실행 컨텍스트 추가

에이전트 핸들러에 필요한 값을 하나로 묶기 위해 `AgentContext`를 추가한다.

```python
@dataclass
class AgentContext:
    text: str
    scope: ConversationScope
    message_id: str | None
    author_name: str
    location_label: str
    has_attachments: bool
```

Discord 전용 객체인 `discord.Message`는 일반 에이전트 dispatch에 직접 넘기지 않는다. 첨부 다운로드, 원본 메시지 fetch, 전체 삭제 확인 같은 Discord orchestration 흐름은 `AssistantBot`에 남긴다.

### 5. 라우터 프롬프트를 카탈로그 기반으로 변경

`RouterAgent` 프롬프트의 intent 목록은 `AgentRegistry.routing_prompt_block()` 결과를 사용한다. 이 prompt block은 `agent_catalog.json`의 목적, 설명, 예시를 기반으로 생성한다.

라우터는 여전히 다음 형식을 반환한다.

```json
{"intent":"manage_task","confidence":0.95,"reason":"할 일 관리 요청 감지"}
```

라우터 모델은 기존 정책대로 `gpt-5.4-mini`를 사용한다.

### 6. Discord와 CLI 실행 분기 통합

`AssistantBot.handle_message`와 `assistant-admin ask`는 현재 유사한 intent 분기를 각각 가지고 있다. 공통 registry dispatch를 사용하도록 변경한다.

다만 다음 흐름은 registry 밖에 남긴다.

- 첨부 파일 저장 요청
- 첨부만 보낸 뒤 확인 대기
- 전체 기억 삭제 확인 대기
- pending 작업 취소
- 지원하지 않는 첨부 안내
- 리마인더 루프

일반 intent는 registry가 실행한다.

예시:

```python
definition = registry.get(route.intent)
if definition is not None:
    return await registry.dispatch(route.intent, context)
```

## 새 에이전트 추가 절차

예를 들어 `CalendarAgent`를 추가한다면 절차는 다음과 같다.

1. `assistant_bot/agents/calendar.py`에 `CalendarAgent`를 구현한다.
2. 필요하면 `RouteIntent`에 `calendar`를 추가한다.
3. `agent_catalog.json`에 `calendar`의 `intent`, `name`, `purpose`, `description`, `examples`를 추가한다.
4. registry 구성 함수의 handler map에 `calendar_agent.handle`을 연결한다.
5. 라우팅 테스트와 dispatch 테스트를 추가한다.

카탈로그 등록 예시는 다음과 같다.

```json
{
  "intent": "calendar",
  "name": "Calendar Agent",
  "purpose": "일정 조회와 일정 등록을 처리한다.",
  "description": "사용자가 약속, 일정, 미팅 시간, 캘린더를 관리하려는 요청을 처리한다.",
  "examples": ["내일 오후 3시에 미팅 일정 잡아줘", "이번 주 일정 보여줘"]
}
```

이 등록 후 라우터는 `calendar` 설명과 예시를 프롬프트에서 참고한다. 실제 실행은 registry의 handler map에 연결된 `CalendarAgent` 핸들러가 담당한다.

## 테스트 계획

### 구조 테스트

- registry에 중복 intent가 없는지 확인한다.
- registry에 등록된 모든 intent가 핸들러를 가지고 있는지 확인한다.
- `RouteIntent`에 정의된 일반 intent가 registry 또는 orchestration 전용 목록에 포함되어 있는지 확인한다.
- `routing_prompt_block()`에 각 에이전트의 intent, 목적, 설명, 예시가 포함되는지 확인한다.

### 라우팅 테스트

- `그거 기억해줘`는 `remember`로 라우팅된다.
- `오늘 할 일 뭐야?`는 `manage_task`로 라우팅된다.
- `오늘 브리핑 해줘`는 `daily_briefing`으로 라우팅된다.
- 새 에이전트 예시를 등록하면 라우터 프롬프트에 해당 예시가 포함된다.

### dispatch 테스트

- `remember`, `recall`, `list_memory`, `update_memory`, `delete_memory`, `restore_memory`가 `MemoryAgent`로 연결된다.
- `manage_task`가 `TaskAgent`로 연결된다.
- `help`, `status`, `daily_briefing`, `reset_context`가 `UtilityAgent`로 연결된다.
- `chat`이 `ConversationAgent`로 연결된다.
- Discord 경로와 `assistant-admin ask` 경로가 같은 registry dispatch를 사용한다.

### 전체 검증

구현 후 다음 명령을 통과해야 한다.

```bash
python3 -m pytest
python3 -m ruff check .
python3 -m compileall assistant_bot tests
```

## 적용 순서

1. `assistant_bot/agents/` 패키지를 만들고 기존 `agents.py`를 에이전트별 파일로 분리한다.
2. 기존 import가 깨지지 않도록 `agents/__init__.py`에서 re-export한다.
3. `AgentDefinition`, `AgentContext`, `AgentRegistry`를 추가한다.
4. 현재 에이전트들을 registry에 등록하는 factory 함수를 만든다.
5. `RouterAgent`가 registry의 prompt block을 사용하도록 바꾼다.
6. `AssistantBot.handle_message`의 일반 intent 분기를 registry dispatch로 대체한다.
7. `assistant-admin ask`의 일반 intent 분기를 같은 registry dispatch로 대체한다.
8. 구조 테스트, 라우팅 테스트, dispatch 테스트를 추가한다.
9. README와 plan 문서에 에이전트 추가 절차를 반영한다.

## 제외 범위

- 런타임 플러그인용 외부 YAML/JSON 시스템은 이번 단계에서 제외한다.
- 런타임 동적 import 기반 플러그인 로딩은 제외한다.
- `RouteIntent` 타입 자동 생성은 제외한다.
- 기존 사용자-facing 기능 변경은 제외한다.

## 결정된 기본값

- 에이전트 목록 메타데이터는 `agent_catalog.json`으로 관리한다.
- 실제 handler 바인딩은 Python 코드 기반 registry로 관리한다.
- `RouteIntent`는 타입 안정성을 위해 당분간 수동으로 유지한다.
- Discord 특수 흐름은 `AssistantBot` orchestration에 남긴다.
- 라우터 모델은 계속 `gpt-5.4-mini`를 사용한다.
- 이 작업은 기능 추가가 아니라 확장성 리팩터링으로 진행한다.

## 적용 상태

- `assistant_bot/agents.py`를 `assistant_bot/agents/` 패키지로 분리했다.
- `agent_catalog.json`을 추가해 에이전트 목적, 설명, 예시를 JSON 설정으로 관리한다.
- `assistant_bot/agent_registry.py`에서 JSON 카탈로그를 로딩하고 handler를 연결한다.
- Discord 봇과 로컬 CLI의 일반 intent 실행 경로를 `AgentRegistry.dispatch()`로 통합했다.
- `tests/test_agent_registry.py`를 추가해 JSON 카탈로그, prompt block, fallback dispatch, handler 누락 검증을 테스트한다.
