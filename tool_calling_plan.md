# Tool Calling 선택 도입 계획

## 목적

현재 봇은 OpenAI Responses API로 텍스트 응답과 라우팅 JSON을 생성하지만, function/tool calling은 사용하지 않는다. 실제 기억 검색, 할 일 추가, 할 일 완료, 삭제 같은 작업은 Python 코드가 직접 분기해 실행한다.

이 계획의 목적은 모든 기능을 무리하게 tool calling으로 바꾸는 것이 아니라, **tool calling을 사용하는 편이 실제로 효율이 좋은 영역**을 선별해 도입하는 것이다.

## 기본 판단 기준

tool calling은 다음 조건에서 효율이 좋다.

- 모델이 여러 저장소 조회 중 어떤 조회가 필요한지 판단해야 한다.
- 한 번의 검색으로 부족해 여러 번 검색하거나 상세 조회가 필요하다.
- 사용자의 자연어가 애매해서 구조화된 action으로 정리해야 한다.
- 답변 생성 전에 앱 내부 데이터나 기능 실행 결과가 필요하다.
- 새 에이전트가 외부 시스템, 로컬 저장소, API, 파일, 캘린더, 업무 도구 같은 기능과 연결된다.

tool calling을 쓰지 않는 편이 좋은 경우도 명확히 구분한다.

- 이미 Python 규칙으로 정확하고 빠르게 처리되는 요청
- 도움말, 상태 확인, 단순 목록 조회처럼 결정적 응답이 충분한 요청
- 전체 삭제, 대량 삭제, 복구 같은 destructive 작업
- 리마인더 발송 루프처럼 모델 판단이 필요 없는 스케줄러 작업
- 사용자의 명시적 확인이 필요한 안전 민감 흐름

## 앞으로의 에이전트 개발 원칙

앞으로 추가되는 모든 전문 에이전트는 설계 단계에서 다음 항목을 반드시 검토한다.

- 이 에이전트가 tool calling을 사용할 필요가 있는가?
- 사용할 tool은 read-only인가, mutation인가?
- mutation tool은 어떤 intent와 확인 조건에서만 허용할 것인가?
- tool 호출 실패 시 기존 deterministic 처리로 fallback할 수 있는가?
- tool 실행 결과를 최종 답변에 어떻게 반영할 것인가?
- tool 호출 로그와 테스트를 어떻게 남길 것인가?

이 원칙은 `plan.md`의 장기 설계 기준으로도 기록한다.

## 도입 범위

### 1차 도입 대상

1차 도입은 `MemoryAgent`, `TaskAgent`, `ConversationAgent` 중심으로 제한한다.

### Conversation Agent

일반 대화 중 저장된 기억, 문서, 할 일을 섞어 답해야 할 때 read-only tool을 제공한다.

후보 tool:

- `search_memory(query, limit)`
- `get_memory_detail(memory_id)`
- `get_document_detail(document_id)`
- `list_tasks(status, due_filter, limit)`
- `search_tasks(query, limit)`

예시 사용자 요청:

```text
전에 저장한 회의록이랑 오늘 할 일 기준으로 지금 뭘 먼저 해야 할지 정리해줘.
```

이 경우 모델은 기억 검색과 할 일 조회 tool을 호출한 뒤 결과를 종합해 답변한다.

### Memory Agent

단순 recall은 기존 embedding 검색을 유지한다. 다만 검색이 여러 번 필요하거나 특정 문서 상세 조회가 필요한 질문은 tool calling 후보로 둔다.

후보 tool:

- `search_memory(query, limit)`
- `get_memory_detail(memory_id)`
- `get_document_detail(document_id)`

삭제, 수정, 전체 삭제는 tool calling에서 제외한다.

### Task Agent

현재 규칙 기반 파서가 처리하지 못하는 애매한 자연어는 tool calling fallback을 통해 구조화된 작업으로 해석한다.

후보 tool:

- `add_task(title, due_at, priority)`
- `list_tasks(status, due_filter, limit)`
- `search_tasks(query, limit)`
- `postpone_task(task_id, due_at)`
- `complete_task(task_id)`

단, mutation tool은 라우터가 `manage_task`로 확정한 뒤에만 노출한다.

## 제외 범위

다음 항목은 1차 tool calling 도입에서 제외한다.

- 전체 기억 삭제
- 메모/문서 삭제
- 삭제 항목 복구
- 첨부 파일 저장 확인
- 리마인더 발송 루프
- OpenAI built-in web search
- OpenAI built-in file search
- remote MCP
- 런타임 동적 플러그인 시스템

## OpenAIService 확장 계획

`OpenAIService`에 tool calling 전용 메서드를 추가한다.

예상 인터페이스:

```python
async def tool_response(
    self,
    *,
    model: str,
    instructions: str,
    input_text: str,
    tools: list[dict[str, object]],
    executor: ToolExecutor,
    tool_choice: str | dict[str, object] = "auto",
    parallel_tool_calls: bool = False,
    max_tool_rounds: int = 3,
) -> str:
    ...
```

동작 방식:

1. 모델에 `tools`를 포함해 Responses API 요청을 보낸다.
2. 응답에 `function_call`이 있으면 tool 이름과 arguments를 파싱한다.
3. 앱 내부 executor가 실제 Python 함수를 실행한다.
4. `function_call_output`을 input에 추가해 모델에 다시 보낸다.
5. 최종 텍스트 응답 또는 추가 tool call을 처리한다.
6. `max_tool_rounds`를 넘으면 안전한 오류 메시지를 반환한다.

기본 정책:

- JSON schema 기반 function tool을 사용한다.
- schema는 가능한 `strict: true`로 둔다.
- mutation tool은 `parallel_tool_calls=False`로 둔다.
- tool name이 allowlist에 없으면 실행하지 않는다.
- arguments 파싱 실패 시 tool 실행 없이 오류 결과를 모델에 전달한다.

## Tool 권한 정책

에이전트별 tool allowlist를 둔다.

```text
ConversationAgent:
  read-only memory/task tools만 허용

MemoryAgent.recall:
  read-only memory/document tools만 허용

TaskAgent:
  task read/write tools 허용
  단, manage_task intent 확정 후에만 mutation tool 허용

UtilityAgent:
  tool calling 미사용

RouterAgent:
  tool calling 미사용
```

삭제, 전체 삭제, 복구 같은 위험 작업은 tool allowlist에 넣지 않는다.

## 데이터 흐름

기본 흐름:

```text
사용자 메시지
RouterAgent가 intent 판단
대상 에이전트 실행
에이전트가 필요 시 tool_response 호출
모델이 function_call 요청
앱이 allowlist 확인 후 tool 실행
tool output을 모델에 전달
모델이 최종 답변 생성
Discord/CLI로 응답
```

기존 deterministic 처리가 가능한 요청은 이 흐름을 타지 않는다.

```text
사용자 메시지
RouterAgent가 intent 판단
기존 Python 파서와 store 호출로 바로 처리
Discord/CLI로 응답
```

## 테스트 계획

### OpenAIService 테스트

- 단일 function call을 실행하고 최종 답변을 반환한다.
- 여러 function call을 순차 처리한다.
- 알 수 없는 tool name은 실행하지 않는다.
- 잘못된 JSON arguments를 안전하게 처리한다.
- `max_tool_rounds`를 넘으면 실패 메시지를 반환한다.
- retry 설정은 기존 OpenAI 호출 정책을 따른다.

### 권한 테스트

- `ConversationAgent`에는 mutation tool이 전달되지 않는다.
- `MemoryAgent.recall`에는 삭제/수정 tool이 전달되지 않는다.
- `TaskAgent` mutation tool은 `manage_task` intent 안에서만 사용된다.
- destructive memory tool은 1차 도입 tool 목록에 없다.

### 기능 테스트

- 복합 질문에서 memory/task read-only tool 결과를 종합해 답한다.
- 단순 `오늘 할 일 뭐야?`는 기존 deterministic 경로로 처리된다.
- 단순 `30분 뒤 물 마시라고 알려줘`는 기존 task parser 경로로 처리된다.
- parser가 실패한 애매한 task 요청만 tool calling fallback을 사용한다.

### 전체 검증

구현 후 다음 명령이 통과해야 한다.

```bash
python3 -m pytest
python3 -m ruff check .
python3 -m compileall assistant_bot tests
```

## 에이전트 모듈화 계획과의 관계

이 계획은 `agent_modularization_plan.md`와 별개의 작업으로 진행 가능하다. 다만 장기적으로는 두 계획을 합쳐 다음 구조로 발전시키는 것이 좋다.

```python
AgentDefinition(
    intent="manage_task",
    name="Task Agent",
    purpose="할 일 관리",
    description="할 일 추가, 조회, 완료, 미루기, 삭제를 처리한다.",
    examples=(...),
    handler=task_agent.handle,
    tools=(task_read_tools, task_mutation_tools),
)
```

즉, 에이전트 카탈로그에 라우팅 설명뿐 아니라 사용 가능한 tool 목록도 함께 등록한다.

## 적용 순서

1. `plan.md`에 앞으로 모든 신규 에이전트는 tool calling 적용 여부를 개발 단계에서 검토한다는 원칙을 기록한다.
2. `OpenAIService.tool_response`와 tool executor 구조를 구현한다.
3. read-only memory/task tool schema와 executor를 만든다.
4. `ConversationAgent`의 복합 질문에 read-only tool calling을 먼저 적용한다.
5. `MemoryAgent.recall`에 선택적 read-only tool calling을 적용한다.
6. `TaskAgent`에는 parser 실패 fallback부터 제한적으로 적용한다.
7. mutation tool은 충분한 테스트 후 task intent 안에서만 허용한다.
8. 문서와 테스트를 갱신한다.

## 결정된 기본값

- tool calling은 선택 도입한다.
- 첫 대상은 Memory, Task, Conversation 계열이다.
- Router, Utility, 리마인더 루프에는 적용하지 않는다.
- destructive 작업에는 적용하지 않는다.
- mutation tool은 명시적 intent와 allowlist가 있을 때만 허용한다.
- built-in web search, file search, remote MCP는 1차 범위에서 제외한다.
