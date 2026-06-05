from __future__ import annotations

from datetime import timedelta

import pytest

from assistant_bot.agents import ConversationAgent, MemoryAgent, ReminderAgent, TaskAgent
from assistant_bot.config import Config
from assistant_bot.database import AppDatabase
from assistant_bot.models import ConversationScope
from assistant_bot.operation_result import OperationResult
from assistant_bot.stores import (
    AgentLogStore,
    ConversationStore,
    MemoryStore,
    PendingAttachmentStore,
    PendingMemoryDeletionStore,
    ReminderStore,
    TaskStore,
    document_content_hash,
)
from assistant_bot.time_utils import now_in_timezone


class FakeOpenAI:
    def __init__(self) -> None:
        self.tool_calls: list[dict[str, object]] = []

    async def embedding(self, text: str) -> list[float]:
        lowered = text.lower()
        return [
            1.0 if "운동" in lowered or "workout" in lowered else 0.0,
            1.0 if "회의" in lowered or "meeting" in lowered else 0.0,
            1.0,
        ]

    async def tool_response(self, **kwargs) -> str:
        self.tool_calls.append(kwargs)
        return "도구 기반 회상 답변"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_conversation_store_clears_current_conversation_only() -> None:
    database = AppDatabase(":memory:")
    store = ConversationStore(database.connection)

    store.add_message(conversation_id="dm:user-1", role="user", user_id="user-1", content="이전 대화")
    store.add_message(conversation_id="dm:user-2", role="user", user_id="user-2", content="다른 대화")
    store.add_summary("dm:user-1", "요약")
    store.add_summary("dm:user-2", "다른 요약")

    counts = store.clear_conversation("dm:user-1")

    assert counts == {"messages": 1, "summaries": 1}
    assert store.recent_messages("dm:user-1") == []
    assert store.latest_summary("dm:user-1") is None
    assert len(store.recent_messages("dm:user-2")) == 1
    assert store.latest_summary("dm:user-2") == "다른 요약"


def test_task_store_adds_lists_completes_and_deletes_for_same_user() -> None:
    database = AppDatabase(":memory:")
    store = TaskStore(database.connection)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    other_scope = ConversationScope(
        conversation_id="dm:user-2",
        channel_id="dm",
        user_id="user-2",
        guild_id=None,
    )

    task_id = store.add(scope=scope, title="제안서 초안 작성", due_at="2026-06-10", source_message_id="m1")
    other_task_id = store.add(scope=other_scope, title="다른 사용자 작업")

    assert task_id == 1
    assert other_task_id == 2
    assert store.stats(scope=scope) == {"open": 1, "completed": 0}
    items = store.list_open(scope=scope)
    assert len(items) == 1
    assert items[0].title == "제안서 초안 작성"
    assert items[0].due_at == "2026-06-10"

    assert store.complete(scope=scope, task_ids=[task_id]) == 1
    assert store.stats(scope=scope) == {"open": 0, "completed": 1}
    assert store.stats(scope=other_scope) == {"open": 1, "completed": 0}

    assert store.delete(scope=scope, task_ids=[task_id]) == 1
    assert store.list_recent(user_id="user-1", status="all") == []
    assert len(store.list_open(scope=other_scope)) == 1

    deleted_items = store.list_deleted(scope=scope)
    assert len(deleted_items) == 1
    assert deleted_items[0].id == task_id
    assert deleted_items[0].deleted_at is not None

    assert store.restore(scope=scope, task_ids=[task_id]) == 1
    restored_items = store.list_recent(user_id="user-1", status="all")
    assert len(restored_items) == 1
    assert restored_items[0].status == "completed"
    assert restored_items[0].deleted_at is None
    assert store.list_deleted(scope=scope) == []


def test_task_store_restores_latest_deleted_task() -> None:
    database = AppDatabase(":memory:")
    store = TaskStore(database.connection)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    first_id = store.add(scope=scope, title="먼저 지운 할 일")
    second_id = store.add(scope=scope, title="나중에 지운 할 일")
    assert store.delete(scope=scope, task_ids=[first_id]) == 1
    assert store.delete(scope=scope, task_ids=[second_id]) == 1

    restored = store.restore_latest_deleted(scope=scope)

    assert restored is not None
    assert restored.id == second_id
    assert [item.id for item in store.list_deleted(scope=scope)] == [first_id]


def test_task_agent_does_not_save_duplicate_open_task() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    first_response = agent.handle(text="할 일 추가: 2026-06-10까지 제안서 초안 작성", scope=scope)
    duplicate_response = agent.handle(text="할 일 추가: 제안서 초안 작성", scope=scope)

    assert isinstance(first_response, OperationResult)
    assert isinstance(duplicate_response, OperationResult)
    assert first_response.facts["task_id"] == 1
    assert first_response.facts["title"] == "제안서 초안 작성"
    assert duplicate_response.facts["duplicate_task"]["task_id"] == 1
    assert "할 일 `1`로 추가했어요" in first_response
    assert "이미 같은 열린 할 일이 있어요" in duplicate_response
    assert "기존 할 일 ID는 `1`" in duplicate_response
    assert len(tasks.list_open(scope=scope)) == 1


def test_reminder_agent_creates_reminder_from_natural_request() -> None:
    database = AppDatabase(":memory:")
    reminders = ReminderStore(database.connection)
    logs = AgentLogStore(database.connection)
    agent = ReminderAgent(config=make_test_config(), reminders=reminders, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    response = agent.handle(text="내일 오전 9시에 물 마시라고 알려줘", scope=scope)

    items = reminders.due_for_delivery(as_of="2999-01-01", user_id=scope.user_id)
    assert "알림 `1`로 등록했어요" in response
    assert len(items) == 1
    assert items[0].text == "물 마시"
    assert items[0].remind_at.endswith("09:00")


def test_reminder_agent_creates_reminder_from_relative_time_request() -> None:
    database = AppDatabase(":memory:")
    reminders = ReminderStore(database.connection)
    logs = AgentLogStore(database.connection)
    agent = ReminderAgent(config=make_test_config(), reminders=reminders, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    response = agent.handle(text="30분 뒤 물 마시라고 알려줘", scope=scope)

    items = reminders.due_for_delivery(as_of="2999-01-01", user_id=scope.user_id)
    assert "알림 `1`로 등록했어요" in response
    assert len(items) == 1
    assert items[0].text == "물 마시"
    assert len(items[0].remind_at) == len("2026-06-05 09:00")


def test_reminder_agent_lists_pending_reminders() -> None:
    database = AppDatabase(":memory:")
    reminders = ReminderStore(database.connection)
    logs = AgentLogStore(database.connection)
    agent = ReminderAgent(config=make_test_config(), reminders=reminders, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    reminders.add(scope=scope, text="물 마시기", remind_at="2026-06-05 07:04")

    response = agent.handle(text="현재 등록되어 있는 알림 목록", scope=scope)

    assert "현재 등록된 미발송 알림 1개" in response
    assert "2026-06-05 07:04" in response
    assert "물 마시기" in response


def test_reminder_agent_shows_latest_reminder_time() -> None:
    database = AppDatabase(":memory:")
    reminders = ReminderStore(database.connection)
    logs = AgentLogStore(database.connection)
    agent = ReminderAgent(config=make_test_config(), reminders=reminders, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    reminders.add(scope=scope, text="알림", remind_at="2026-06-05 07:04")

    response = agent.handle(text="내가 아까 몇시에 알림 보내달라고 했지?", scope=scope)

    assert "가장 최근 등록한 알림" in response
    assert "2026-06-05 07:04" in response


def test_task_agent_creates_task_from_recent_user_message() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    conversations.add_message(
        conversation_id=scope.conversation_id,
        role="user",
        user_id=scope.user_id,
        content="내일까지 제안서 초안 작성해야겠다",
    )

    response = agent.handle(text="그거 할 일로 추가해줘", scope=scope)

    items = tasks.list_recent(user_id=scope.user_id, status="open")
    assert "바로 전에 말한 내용을 할 일 `1`로 추가했어요" in response
    assert len(items) == 1
    assert items[0].title == "제안서 초안 작성"
    assert items[0].due_at is not None


def test_task_agent_postpones_task_with_explicit_id() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    task_id = tasks.add(scope=scope, title="물 마시기", due_at="2026-06-05 09:00")
    tasks.mark_reminded(task_id)

    response = agent.handle(text=f"할 일 {task_id} 30분 뒤 다시 알려줘", scope=scope)

    item = tasks.get(scope=scope, task_id=task_id)
    assert item is not None
    assert "할 일 1개를" in response
    assert item.due_at is not None
    assert len(item.due_at) == len("2026-06-05 09:30")
    assert item.reminder_sent_at is None


def test_task_agent_searches_tasks_by_keyword() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    tasks.add(scope=scope, title="제안서 초안 작성", priority="high", due_at="2026-06-10")
    tasks.add(scope=scope, title="장보기")

    response = agent.handle(text="제안서 관련 할 일 찾아줘", scope=scope)

    assert "`제안서` 할 일 검색 결과 1개" in response
    assert "할 일 `1` · 제안서 초안 작성" in response
    assert "우선순위: 높음" in response
    assert "장보기" not in response


def test_task_agent_shows_task_detail() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm-channel",
        user_id="user-1",
        guild_id=None,
    )
    task_id = tasks.add(
        scope=scope,
        title="제안서 초안 작성",
        priority="high",
        due_at="2026-06-10",
        source_message_id="message-1",
    )

    response = agent.handle(text=f"할 일 {task_id} 자세히 보여줘", scope=scope)

    assert f"할 일 `{task_id}` · 제안서 초안 작성" in response
    assert "- 상태: open" in response
    assert "- 우선순위: 높음" in response
    assert "- 기한: 2026-06-10" in response
    assert "- 대화 ID: dm:user-1" in response
    assert "- 채널 ID: dm-channel" in response
    assert "- 원본 메시지 ID: message-1" in response


def test_task_agent_shows_latest_task_detail() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm-channel",
        user_id="user-1",
        guild_id=None,
    )
    first_id = tasks.add(scope=scope, title="먼저 추가한 할 일")
    second_id = tasks.add(
        scope=scope,
        title="방금 추가한 할 일",
        priority="high",
        due_at="2026-06-10 09:00",
        source_message_id="message-2",
    )

    response = agent.handle(text="방금 추가한 할 일 보여줘", scope=scope)

    assert f"할 일 `{second_id}` · 방금 추가한 할 일" in response
    assert f"할 일 `{first_id}`" not in response
    assert "- 우선순위: 높음" in response
    assert "- 기한: 2026-06-10 09:00" in response
    assert "- 원본 메시지 ID: message-2" in response


def test_task_agent_lists_completed_and_all_tasks() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    open_id = tasks.add(scope=scope, title="제안서 초안 작성")
    completed_id = tasks.add(scope=scope, title="회의록 정리")
    assert tasks.complete(scope=scope, task_ids=[completed_id]) == 1

    completed_response = agent.handle(text="완료한 할 일 보여줘", scope=scope)
    all_response = agent.handle(text="전체 할 일 목록 보여줘", scope=scope)

    assert isinstance(completed_response, OperationResult)
    assert isinstance(all_response, OperationResult)
    assert completed_response.summary == "할 일 목록 조회"
    assert all_response.summary == "할 일 목록 조회"
    assert completed_response.items[0]["task_id"] == completed_id
    assert "완료한 할 일 1개" in completed_response
    assert f"할 일 `{completed_id}` · 회의록 정리" in completed_response
    assert f"할 일 `{open_id}` · 제안서 초안 작성" not in completed_response
    assert "다시 열려면" in completed_response
    assert "할 일 전체 2개" in all_response
    assert f"할 일 `{open_id}` · 제안서 초안 작성" in all_response
    assert f"할 일 `{completed_id}` · 회의록 정리" in all_response


def test_task_agent_lists_tomorrow_week_and_undated_tasks() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    now = now_in_timezone("Asia/Seoul")
    today = now.strftime("%Y-%m-%d")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    sunday = (now + timedelta(days=6 - now.weekday())).strftime("%Y-%m-%d")
    after_week = (now + timedelta(days=8)).strftime("%Y-%m-%d")
    tasks.add(scope=scope, title="오늘 작업", due_at=today)
    tasks.add(scope=scope, title="내일 오전 작업", due_at=f"{tomorrow} 09:00")
    tasks.add(scope=scope, title="이번 주 작업", due_at=sunday)
    tasks.add(scope=scope, title="다음 주 작업", due_at=after_week)
    tasks.add(scope=scope, title="기한 없는 작업")

    tomorrow_response = agent.handle(text="내일 할 일 뭐야?", scope=scope)
    week_response = agent.handle(text="이번 주 할 일 보여줘", scope=scope)
    undated_response = agent.handle(text="기한 없는 할 일 보여줘", scope=scope)

    assert "내일 처리할 할 일" in tomorrow_response
    assert "내일 오전 작업" in tomorrow_response
    assert "오늘 작업" not in tomorrow_response
    assert "다음 주 작업" not in tomorrow_response
    assert "이번 주 처리할 할 일" in week_response
    assert "오늘 작업" in week_response
    assert "이번 주 작업" in week_response
    assert "다음 주 작업" not in week_response
    assert "기한 없는 할 일" in undated_response
    assert "기한 없는 작업" in undated_response
    assert "오늘 작업" not in undated_response


def test_task_agent_completes_today_tasks_in_batch() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    today = now_in_timezone("Asia/Seoul").strftime("%Y-%m-%d")
    tomorrow = (now_in_timezone("Asia/Seoul") + timedelta(days=1)).strftime("%Y-%m-%d")
    today_id = tasks.add(scope=scope, title="오늘 작업", due_at=today)
    morning_id = tasks.add(scope=scope, title="오늘 오전 작업", due_at=f"{today} 09:00")
    tomorrow_id = tasks.add(scope=scope, title="내일 작업", due_at=tomorrow)
    undated_id = tasks.add(scope=scope, title="기한 없는 작업")

    response = agent.handle(text="오늘 할 일 다 했어", scope=scope)

    today_task = tasks.get(scope=scope, task_id=today_id)
    morning_task = tasks.get(scope=scope, task_id=morning_id)
    tomorrow_task = tasks.get(scope=scope, task_id=tomorrow_id)
    undated_task = tasks.get(scope=scope, task_id=undated_id)
    assert "오늘까지 처리할 할 일 2개를 완료 처리했어요" in response
    assert today_task is not None
    assert morning_task is not None
    assert tomorrow_task is not None
    assert undated_task is not None
    assert today_task.status == "completed"
    assert morning_task.status == "completed"
    assert tomorrow_task.status == "open"
    assert undated_task.status == "open"


def test_task_agent_completes_all_open_tasks_in_batch() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    first_id = tasks.add(scope=scope, title="첫 번째 작업")
    second_id = tasks.add(scope=scope, title="두 번째 작업")

    response = agent.handle(text="모든 할 일 완료했어", scope=scope)

    first_task = tasks.get(scope=scope, task_id=first_id)
    second_task = tasks.get(scope=scope, task_id=second_id)
    assert "열린 할 일 2개를 완료 처리했어요" in response
    assert first_task is not None
    assert second_task is not None
    assert first_task.status == "completed"
    assert second_task.status == "completed"


def test_task_agent_completes_single_task_by_keyword() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    task_id = tasks.add(scope=scope, title="제안서 초안 작성")
    tasks.add(scope=scope, title="장보기")

    response = agent.handle(text="제안서 할 일 완료했어", scope=scope)

    assert "할 일 1개를 완료 처리했어요" in response
    completed = tasks.get(scope=scope, task_id=task_id)
    assert completed is not None
    assert completed.status == "completed"


def test_task_agent_reopens_latest_completed_task() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    first_id = tasks.add(scope=scope, title="먼저 완료한 작업")
    second_id = tasks.add(scope=scope, title="방금 완료한 작업")
    assert tasks.complete(scope=scope, task_ids=[first_id]) == 1
    assert tasks.complete(scope=scope, task_ids=[second_id]) == 1

    response = agent.handle(text="방금 완료한 할 일 되돌려줘", scope=scope)

    first_task = tasks.get(scope=scope, task_id=first_id)
    second_task = tasks.get(scope=scope, task_id=second_id)
    assert f"할 일 `{second_id}` · 방금 완료한 작업" in response
    assert first_task is not None
    assert second_task is not None
    assert first_task.status == "completed"
    assert second_task.status == "open"


def test_task_agent_asks_for_id_when_keyword_matches_multiple_tasks() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    tasks.add(scope=scope, title="제안서 초안 작성")
    tasks.add(scope=scope, title="제안서 검토")

    response = agent.handle(text="제안서 할 일 완료했어", scope=scope)

    assert "관련된 할 일이 여러 개 있어요" in response
    assert "할 일 `1` · 제안서 초안 작성" in response
    assert "할 일 `2` · 제안서 검토" in response
    assert all(item.status == "open" for item in tasks.list_open(scope=scope))


def test_task_agent_postpones_and_deletes_single_task_by_keyword() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    proposal_id = tasks.add(scope=scope, title="제안서 초안 작성")
    cleanup_id = tasks.add(scope=scope, title="회의록 정리")

    postpone_response = agent.handle(text="제안서 할 일 내일 오전 9시 다시 알려줘", scope=scope)
    delete_response = agent.handle(text="회의록 할 일 삭제해줘", scope=scope)

    proposal = tasks.get(scope=scope, task_id=proposal_id)
    deleted_cleanup = tasks.get(scope=scope, task_id=cleanup_id, include_deleted=True)
    assert "할 일 1개를" in postpone_response
    assert proposal is not None
    assert proposal.due_at is not None
    assert proposal.due_at.endswith("09:00")
    assert "할 일 1개를 삭제했어요" in delete_response
    assert deleted_cleanup is not None
    assert deleted_cleanup.deleted_at is not None


def test_task_agent_deletes_latest_added_task() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    first_id = tasks.add(scope=scope, title="먼저 추가한 할 일")
    second_id = tasks.add(scope=scope, title="방금 추가한 할 일")

    response = agent.handle(text="방금 추가한 할 일 삭제해줘", scope=scope)

    first_task = tasks.get(scope=scope, task_id=first_id)
    second_task = tasks.get(scope=scope, task_id=second_id, include_deleted=True)
    assert f"할 일 `{second_id}` · 방금 추가한 할 일" in response
    assert "복구해줘" in response
    assert first_task is not None
    assert first_task.deleted_at is None
    assert second_task is not None
    assert second_task.deleted_at is not None


def test_task_agent_postpones_latest_added_task() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    first_id = tasks.add(scope=scope, title="먼저 추가한 할 일")
    second_id = tasks.add(scope=scope, title="방금 추가한 할 일")

    response = agent.handle(text="방금 추가한 할 일 내일 오전 9시 다시 알려줘", scope=scope)

    first_task = tasks.get(scope=scope, task_id=first_id)
    second_task = tasks.get(scope=scope, task_id=second_id)
    assert "할 일 1개를" in response
    assert first_task is not None
    assert first_task.due_at is None
    assert second_task is not None
    assert second_task.due_at is not None
    assert second_task.due_at.endswith("09:00")


def test_task_agent_clears_task_due_by_id() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    task_id = tasks.add(scope=scope, title="기한 있는 할 일", due_at="2026-06-10 09:00")

    response = agent.handle(text=f"할 일 {task_id} 기한 없애줘", scope=scope)

    item = tasks.get(scope=scope, task_id=task_id)
    assert "기한과 리마인더 예약을 제거했어요" in response
    assert item is not None
    assert item.due_at is None
    assert item.reminder_sent_at is None


def test_task_agent_clears_latest_added_task_due() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    first_id = tasks.add(scope=scope, title="먼저 추가한 할 일", due_at="2026-06-09")
    second_id = tasks.add(scope=scope, title="방금 추가한 할 일", due_at="2026-06-10")

    response = agent.handle(text="방금 추가한 할 일 리마인더 제거해줘", scope=scope)

    first_task = tasks.get(scope=scope, task_id=first_id)
    second_task = tasks.get(scope=scope, task_id=second_id)
    assert "기한과 리마인더 예약을 제거했어요" in response
    assert first_task is not None
    assert first_task.due_at == "2026-06-09"
    assert second_task is not None
    assert second_task.due_at is None


def test_task_agent_sets_latest_added_task_priority() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    first_id = tasks.add(scope=scope, title="먼저 추가한 할 일")
    second_id = tasks.add(scope=scope, title="방금 추가한 할 일")

    response = agent.handle(text="방금 추가한 할 일 중요하게 표시해줘", scope=scope)

    first_task = tasks.get(scope=scope, task_id=first_id)
    second_task = tasks.get(scope=scope, task_id=second_id)
    assert "우선순위를 `높음`으로 바꿨어요" in response
    assert first_task is not None
    assert first_task.priority == "normal"
    assert second_task is not None
    assert second_task.priority == "high"


def test_task_agent_renames_latest_added_task() -> None:
    database = AppDatabase(":memory:")
    tasks = TaskStore(database.connection)
    logs = AgentLogStore(database.connection)
    conversations = ConversationStore(database.connection)
    agent = TaskAgent(config=make_test_config(), tasks=tasks, conversations=conversations, logs=logs)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    first_id = tasks.add(scope=scope, title="먼저 추가한 할 일")
    second_id = tasks.add(scope=scope, title="방금 추가한 할 일")

    response = agent.handle(text="방금 추가한 할 일을 고객 미팅 준비로 바꿔줘", scope=scope)

    first_task = tasks.get(scope=scope, task_id=first_id)
    second_task = tasks.get(scope=scope, task_id=second_id)
    assert "고객 미팅 준비" in response
    assert first_task is not None
    assert first_task.title == "먼저 추가한 할 일"
    assert second_task is not None
    assert second_task.title == "고객 미팅 준비"


def test_task_store_lists_due_reminders_once() -> None:
    database = AppDatabase(":memory:")
    store = TaskStore(database.connection)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm-channel",
        user_id="user-1",
        guild_id=None,
    )

    due_id = store.add(scope=scope, title="오늘 처리할 일", due_at="2026-06-04")
    urgent_id = store.add(scope=scope, title="중요한 오늘 일", priority="high", due_at="2026-06-04")
    store.add(scope=scope, title="나중에 할 일", due_at="2026-06-10")
    store.add(scope=scope, title="기한 없는 일")

    due_tasks = store.due_for_reminder(today="2026-06-04")

    assert [task.id for task in due_tasks] == [urgent_id, due_id]
    assert due_tasks[0].priority == "high"
    assert due_tasks[1].channel_id == "dm-channel"
    assert due_tasks[1].reminder_sent_at is None
    assert [task.id for task in store.list_due(scope=scope, due_before="2026-06-04")] == [urgent_id, due_id]

    store.mark_reminded(due_id)

    assert [task.id for task in store.due_for_reminder(today="2026-06-04")] == [urgent_id]
    store.mark_reminded(urgent_id)
    assert store.due_for_reminder(today="2026-06-04") == []

    assert store.postpone(scope=scope, task_ids=[due_id], due_at="2026-06-05") == 1
    postponed_tasks = store.due_for_reminder(today="2026-06-05")

    assert [task.id for task in postponed_tasks] == [due_id]
    assert postponed_tasks[0].due_at == "2026-06-05"
    assert postponed_tasks[0].reminder_sent_at is None

    assert store.rename(scope=scope, task_ids=[due_id], title="새 제목") == 1
    assert store.set_priority(scope=scope, task_ids=[due_id], priority="high") == 1
    renamed_tasks = store.list_open(scope=scope)
    assert renamed_tasks[0].title in {"새 제목", "중요한 오늘 일"}
    assert renamed_tasks[0].priority == "high"

    assert store.complete(scope=scope, task_ids=[due_id]) == 1
    assert store.reopen(scope=scope, task_ids=[due_id]) == 1
    reopened = [task for task in store.list_open(scope=scope) if task.id == due_id]
    assert len(reopened) == 1
    assert reopened[0].completed_at is None


def test_task_store_handles_time_specific_due_values() -> None:
    database = AppDatabase(":memory:")
    store = TaskStore(database.connection)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm-channel",
        user_id="user-1",
        guild_id=None,
    )

    morning_id = store.add(scope=scope, title="오전 회신", due_at="2026-06-05 09:00")
    evening_id = store.add(scope=scope, title="저녁 정리", due_at="2026-06-05 18:30")
    tomorrow_id = store.add(scope=scope, title="내일 작업", due_at="2026-06-06 09:00")

    assert [task.id for task in store.due_for_reminder(today="2026-06-05 08:59")] == []
    assert [task.id for task in store.due_for_reminder(today="2026-06-05 09:00")] == [morning_id]
    assert [task.id for task in store.list_due(scope=scope, due_before="2026-06-05")] == [morning_id, evening_id]
    assert tomorrow_id not in [task.id for task in store.list_due(scope=scope, due_before="2026-06-05")]


def test_task_store_finds_latest_reminded_open_task() -> None:
    database = AppDatabase(":memory:")
    store = TaskStore(database.connection)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm-channel",
        user_id="user-1",
        guild_id=None,
    )
    first_id = store.add(scope=scope, title="먼저 알림 받은 일", due_at="2026-06-05 09:00")
    second_id = store.add(scope=scope, title="나중에 알림 받은 일", due_at="2026-06-05 10:00")

    assert store.latest_reminded_open(scope=scope) is None

    store.mark_reminded(first_id)
    store.mark_reminded(second_id)
    latest = store.latest_reminded_open(scope=scope)

    assert latest is not None
    assert latest.id == second_id
    assert store.complete(scope=scope, task_ids=[second_id]) == 1
    latest_after_completion = store.latest_reminded_open(scope=scope)
    assert latest_after_completion is not None
    assert latest_after_completion.id == first_id


@pytest.mark.anyio
async def test_memory_store_lists_stats_and_deletes() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    scope = ConversationScope(
        conversation_id="dm:1",
        channel_id="1",
        user_id="user-1",
        guild_id=None,
    )

    memory_id = await store.save_text_memory(
        scope=scope,
        text="운동은 월수금 저녁에 한다",
        source_message_id="m1",
    )
    document_id, chunk_count = await store.save_document(
        scope=scope,
        filename="meeting.md",
        content_type="text/markdown",
        text="회의에서는 배포 일정을 금요일로 정했다.",
        source_message_id="m2",
    )

    assert memory_id == 1
    assert document_id == 1
    assert chunk_count == 1
    assert store.stats(scope=scope) == {"memories": 1, "documents": 1, "chunks": 1}
    assert len(store.recent_items(scope=scope)) == 2
    memory_detail = store.get_memory_detail(scope=scope, memory_id=memory_id)
    assert memory_detail is not None
    assert memory_detail.title.startswith("운동은")
    assert memory_detail.text == "운동은 월수금 저녁에 한다"
    assert memory_detail.source_location == "DM"

    document_detail = store.get_document_detail(scope=scope, document_id=document_id)
    assert document_detail is not None
    assert document_detail.title == "meeting.md"
    assert document_detail.chunk_count == 1
    assert "배포 일정" in document_detail.text
    assert document_detail.source_location == "DM"
    document_row = database.connection.execute(
        "SELECT content_hash FROM documents WHERE id = ?",
        (document_id,),
    ).fetchone()
    assert document_row["content_hash"] == document_content_hash("회의에서는 배포 일정을 금요일로 정했다.")

    results = await store.search(scope=scope, query="운동 일정", limit=3)
    assert results[0].kind == "memory"

    assert await store.update_text_memory(
        scope=scope,
        memory_id=memory_id,
        text="회의는 월요일 오전에 한다",
    )
    updated_detail = store.get_memory_detail(scope=scope, memory_id=memory_id)
    assert updated_detail is not None
    assert updated_detail.text == "회의는 월요일 오전에 한다"
    assert updated_detail.title.startswith("회의는")

    assert store.delete_memory_ids(scope=scope, memory_ids=[memory_id]) == 1
    assert store.stats(scope=scope) == {"memories": 0, "documents": 1, "chunks": 1}
    assert store.delete_document_ids(scope=scope, document_ids=[document_id]) == 1
    assert store.stats(scope=scope) == {"memories": 0, "documents": 0, "chunks": 0}


@pytest.mark.anyio
async def test_memory_store_keeps_same_user_memory_across_locations() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    dm_scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    guild_scope = ConversationScope(
        conversation_id="channel:10:user:user-1",
        channel_id="10",
        user_id="user-1",
        guild_id="guild-1",
    )

    dm_memory_id = await store.save_text_memory(
        scope=dm_scope,
        text="DM에서 저장한 개인 선호",
        source_message_id="dm-message",
    )
    guild_memory_id = await store.save_text_memory(
        scope=guild_scope,
        text="서버에서 저장한 작업 메모",
        source_message_id="guild-message",
    )

    assert store.stats(scope=dm_scope)["memories"] == 2
    assert store.stats(scope=guild_scope)["memories"] == 2

    guild_items = store.recent_items(scope=guild_scope)
    locations = {item.id: item.source_location for item in guild_items}
    assert locations[dm_memory_id] == "DM"
    assert locations[guild_memory_id] == "서버"

    assert store.get_memory_detail(scope=guild_scope, memory_id=dm_memory_id) is not None


@pytest.mark.anyio
async def test_memory_store_finds_duplicate_text_for_same_user() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    other_scope = ConversationScope(
        conversation_id="dm:user-2",
        channel_id="dm",
        user_id="user-2",
        guild_id=None,
    )

    memory_id = await store.save_text_memory(
        scope=scope,
        text="나는 오전에 집중이 잘 된다",
        source_message_id="m1",
    )

    duplicate = store.find_duplicate_text_memory(scope=scope, text="  나는   오전에 집중이 잘 된다  ")

    assert duplicate is not None
    assert duplicate.id == memory_id
    assert store.find_duplicate_text_memory(scope=other_scope, text="나는 오전에 집중이 잘 된다") is None


@pytest.mark.anyio
async def test_memory_store_finds_duplicate_document_for_same_user() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    other_scope = ConversationScope(
        conversation_id="dm:user-2",
        channel_id="dm",
        user_id="user-2",
        guild_id=None,
    )

    document_id, _ = await store.save_document(
        scope=scope,
        filename="meeting.md",
        content_type="text/markdown",
        text="회의 안건\n\n- 배포 일정\n- 담당자",
        source_message_id="m1",
    )

    duplicate = store.find_duplicate_document(
        scope=scope,
        text=" 회의 안건 \n\n - 배포 일정\n- 담당자 ",
    )

    assert duplicate is not None
    assert duplicate.id == document_id
    assert duplicate.title == "meeting.md"
    assert store.find_duplicate_document(scope=other_scope, text="회의 안건\n- 배포 일정\n- 담당자") is None


@pytest.mark.anyio
async def test_memory_store_deletes_all_for_user_without_touching_other_users() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    other_scope = ConversationScope(
        conversation_id="dm:user-2",
        channel_id="dm",
        user_id="user-2",
        guild_id=None,
    )

    await store.save_text_memory(scope=scope, text="사용자 1 메모", source_message_id="m1")
    await store.save_document(
        scope=scope,
        filename="user-1.md",
        content_type="text/markdown",
        text="사용자 1 문서",
        source_message_id="m2",
    )
    await store.save_text_memory(scope=other_scope, text="사용자 2 메모", source_message_id="m3")

    assert store.delete_all_for_user(scope=scope) == 2
    assert store.stats(scope=scope) == {"memories": 0, "documents": 0, "chunks": 0}
    assert store.stats(scope=other_scope)["memories"] == 1


@pytest.mark.anyio
async def test_memory_store_deletes_latest_item_for_user() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    other_scope = ConversationScope(
        conversation_id="dm:user-2",
        channel_id="dm",
        user_id="user-2",
        guild_id=None,
    )

    memory_id = await store.save_text_memory(scope=scope, text="먼저 저장한 메모", source_message_id="m1")
    document_id, _ = await store.save_document(
        scope=scope,
        filename="latest.md",
        content_type="text/markdown",
        text="나중에 저장한 문서",
        source_message_id="m2",
    )
    await store.save_text_memory(scope=other_scope, text="다른 사용자 메모", source_message_id="m3")
    database.connection.execute(
        "UPDATE user_memories SET created_at = '2026-06-04 10:00:00' WHERE id = ?",
        (memory_id,),
    )
    database.connection.execute(
        "UPDATE documents SET created_at = '2026-06-04 10:05:00' WHERE id = ?",
        (document_id,),
    )
    database.connection.commit()

    deleted = store.delete_latest_item(scope=scope)

    assert deleted is not None
    assert deleted.kind == "document"
    assert deleted.id == document_id
    assert store.stats(scope=scope) == {"memories": 1, "documents": 0, "chunks": 0}
    assert store.stats(scope=other_scope)["memories"] == 1

    second_deleted = store.delete_latest_item(scope=scope)

    assert second_deleted is not None
    assert second_deleted.kind == "memory"
    assert second_deleted.id == memory_id
    assert store.delete_latest_item(scope=scope) is None


@pytest.mark.anyio
async def test_memory_store_restores_latest_deleted_item_for_user() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    other_scope = ConversationScope(
        conversation_id="dm:user-2",
        channel_id="dm",
        user_id="user-2",
        guild_id=None,
    )

    memory_id = await store.save_text_memory(scope=scope, text="복구할 메모", source_message_id="m1")
    document_id, _ = await store.save_document(
        scope=scope,
        filename="restore.md",
        content_type="text/markdown",
        text="복구할 문서",
        source_message_id="m2",
    )
    other_memory_id = await store.save_text_memory(scope=other_scope, text="다른 사용자 메모", source_message_id="m3")
    store.delete_memory_ids(scope=scope, memory_ids=[memory_id])
    store.delete_document_ids(scope=scope, document_ids=[document_id])
    store.delete_memory_ids(scope=other_scope, memory_ids=[other_memory_id])
    database.connection.execute(
        "UPDATE user_memories SET deleted_at = '2026-06-04 10:00:00' WHERE id = ?",
        (memory_id,),
    )
    database.connection.execute(
        "UPDATE documents SET deleted_at = '2026-06-04 10:05:00' WHERE id = ?",
        (document_id,),
    )
    database.connection.execute(
        "UPDATE user_memories SET deleted_at = '2026-06-04 10:10:00' WHERE id = ?",
        (other_memory_id,),
    )
    database.connection.commit()

    restored = store.restore_latest_deleted_item(scope=scope)

    assert restored is not None
    assert restored.kind == "document"
    assert restored.id == document_id
    assert store.stats(scope=scope) == {"memories": 0, "documents": 1, "chunks": 1}
    assert store.stats(scope=other_scope) == {"memories": 0, "documents": 0, "chunks": 0}

    second_restored = store.restore_latest_deleted_item(scope=scope)

    assert second_restored is not None
    assert second_restored.kind == "memory"
    assert second_restored.id == memory_id
    assert store.restore_latest_deleted_item(scope=scope) is None
    assert store.stats(scope=scope) == {"memories": 1, "documents": 1, "chunks": 1}


@pytest.mark.anyio
async def test_memory_store_lists_deleted_items_and_restores_by_ids() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    memory_id = await store.save_text_memory(scope=scope, text="삭제된 메모", source_message_id="m1")
    document_id, _ = await store.save_document(
        scope=scope,
        filename="deleted.md",
        content_type="text/markdown",
        text="삭제된 문서",
        source_message_id="m2",
    )
    store.delete_memory_ids(scope=scope, memory_ids=[memory_id])
    store.delete_document_ids(scope=scope, document_ids=[document_id])

    deleted_items = store.deleted_items(scope=scope)

    assert {item.kind for item in deleted_items} == {"memory", "document"}
    assert store.restore_memory_ids(scope=scope, memory_ids=[memory_id]) == 1
    assert store.restore_document_ids(scope=scope, document_ids=[document_id]) == 1
    assert store.stats(scope=scope) == {"memories": 1, "documents": 1, "chunks": 1}
    assert store.deleted_items(scope=scope) == []


@pytest.mark.anyio
async def test_memory_agent_does_not_save_duplicate_text_memory() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    first = await agent.remember_text(text="이거 기억해줘: 나는 오전에 집중이 잘 된다", scope=scope, message_id="m1")
    second = await agent.remember_text(text="기억해줘: 나는 오전에 집중이 잘 된다", scope=scope, message_id="m2")

    assert isinstance(first, OperationResult)
    assert isinstance(second, OperationResult)
    assert first.facts["memory_id"] == 1
    assert second.facts["duplicate_memory"]["id"] == 1
    assert "저장 ID는 `1`" in first
    assert "이미 같은 내용을 기억하고 있어요" in second
    assert "기존 메모 ID는 `1`" in second
    assert store.stats(scope=scope)["memories"] == 1


@pytest.mark.anyio
async def test_memory_agent_does_not_save_memory_setup_phrase() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    response = await agent.remember_text(text="메모 하나 할게", scope=scope, message_id="m1")

    assert isinstance(response, OperationResult)
    assert response.status == "needs_input"
    assert "메모할 내용을 알려주세요" in response
    assert store.stats(scope=scope)["memories"] == 0


@pytest.mark.anyio
async def test_memory_agent_remembers_previous_user_message() -> None:
    database = AppDatabase(":memory:")
    conversations = ConversationStore(database.connection)
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
        conversations=conversations,
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    conversations.add_message(
        conversation_id=scope.conversation_id,
        role="user",
        user_id=scope.user_id,
        content="나는 오전보다 저녁 운동을 선호한다",
    )

    response = await agent.remember_text(text="방금 말한 거 기억해줘", scope=scope, message_id="m2")

    assert "저장 ID는 `1`" in response
    detail = store.get_memory_detail(scope=scope, memory_id=1)
    assert detail is not None
    assert detail.text == "나는 오전보다 저녁 운동을 선호한다"


@pytest.mark.anyio
async def test_memory_agent_remembers_previous_user_message_from_pronoun_reference() -> None:
    database = AppDatabase(":memory:")
    conversations = ConversationStore(database.connection)
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
        conversations=conversations,
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    conversations.add_message(
        conversation_id=scope.conversation_id,
        role="user",
        user_id=scope.user_id,
        content="나는 회의 전 10분 준비 시간을 선호한다",
    )

    response = await agent.remember_text(text="그거 기억해줘", scope=scope, message_id="m2")

    assert "저장 ID는 `1`" in response
    detail = store.get_memory_detail(scope=scope, memory_id=1)
    assert detail is not None
    assert detail.text == "나는 회의 전 10분 준비 시간을 선호한다"


@pytest.mark.anyio
async def test_memory_agent_requires_previous_message_for_recent_reference() -> None:
    database = AppDatabase(":memory:")
    conversations = ConversationStore(database.connection)
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
        conversations=conversations,
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    response = await agent.remember_text(text="방금 말한 거 기억해줘", scope=scope, message_id="m1")

    assert "직전에 저장할 만한 사용자 메시지가 없어요" in response
    assert store.stats(scope=scope)["memories"] == 0


@pytest.mark.anyio
async def test_memory_agent_searches_saved_memories_as_list() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    memory_id = await store.save_text_memory(scope=scope, text="운동은 월수금 저녁에 한다", source_message_id="m1")
    await store.save_document(
        scope=scope,
        filename="meeting.md",
        content_type="text/markdown",
        text="회의에서는 배포 일정을 금요일로 정했다.",
        source_message_id="m2",
    )

    response = await agent.list_memories(text="운동 관련 기억 찾아줘", scope=scope)

    assert isinstance(response, OperationResult)
    assert response.summary == "저장 기억 검색 결과 조회"
    assert response.items[0]["id"] == memory_id
    assert "`운동` 관련 저장 기억" in response
    assert f"메모 `{memory_id}`" in response
    assert "자세히 보려면" in response


@pytest.mark.anyio
async def test_memory_agent_recalls_latest_saved_item() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    first_id = await store.save_text_memory(scope=scope, text="먼저 저장한 메모", source_message_id="m1")
    second_id = await store.save_text_memory(scope=scope, text="방금 저장한 메모", source_message_id="m2")

    response = await agent.recall(text="방금 저장한 거 보여줘", scope=scope)

    assert f"메모 `{second_id}`" in response
    assert "방금 저장한 메모" in response
    assert f"메모 `{first_id}`" not in response


@pytest.mark.anyio
async def test_memory_agent_general_recall_uses_read_only_tools() -> None:
    database = AppDatabase(":memory:")
    openai = FakeOpenAI()
    store = MemoryStore(database.connection, openai)  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=openai,  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    await store.save_text_memory(scope=scope, text="운동은 월수금 저녁에 한다", source_message_id="m1")

    response = await agent.recall(text="운동 관련 기억 기준으로 알려줘", scope=scope)

    assert response == "도구 기반 회상 답변"
    assert openai.tool_calls
    tool_names = {tool.name for tool in openai.tool_calls[0]["tools"]}
    assert {"search_memories", "get_memory_detail", "get_document_detail"}.issubset(tool_names)


@pytest.mark.anyio
async def test_conversation_agent_includes_current_time_context() -> None:
    database = AppDatabase(":memory:")
    openai = FakeOpenAI()
    memories = MemoryStore(database.connection, openai)  # type: ignore[arg-type]
    conversations = ConversationStore(database.connection)
    tasks = TaskStore(database.connection)
    agent = ConversationAgent(
        config=make_test_config(),
        openai=openai,  # type: ignore[arg-type]
        conversations=conversations,
        memories=memories,
        tasks=tasks,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    response = await agent.chat(
        text="지금 몇시야?",
        scope=scope,
        author_name="사용자",
        location_label="DM",
    )

    assert response == "도구 기반 회상 답변"
    assert openai.tool_calls
    input_text = str(openai.tool_calls[0]["input_text"])
    assert "현재 날짜와 시간" in input_text
    assert "Asia/Seoul" in input_text


@pytest.mark.anyio
async def test_memory_agent_recalls_latest_saved_document() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    await store.save_text_memory(scope=scope, text="먼저 저장한 메모", source_message_id="m1")
    document_id, _ = await store.save_document(
        scope=scope,
        filename="latest.md",
        content_type="text/markdown",
        text="방금 저장한 문서 본문",
        source_message_id="m2",
    )

    response = await agent.recall(text="마지막 저장한 문서 보여줘", scope=scope)

    assert f"문서 `{document_id}`" in response
    assert "방금 저장한 문서 본문" in response


@pytest.mark.anyio
async def test_memory_agent_updates_latest_saved_memory() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    first_id = await store.save_text_memory(scope=scope, text="먼저 저장한 메모", source_message_id="m1")
    second_id = await store.save_text_memory(scope=scope, text="오타가 있는 메모", source_message_id="m2")

    response = await agent.update(text="방금 저장한 메모를 나는 저녁 운동을 선호한다로 바꿔줘", scope=scope)

    first_detail = store.get_memory_detail(scope=scope, memory_id=first_id)
    second_detail = store.get_memory_detail(scope=scope, memory_id=second_id)
    assert f"메모 `{second_id}`를 수정했어요" in response
    assert first_detail is not None
    assert first_detail.text == "먼저 저장한 메모"
    assert second_detail is not None
    assert second_detail.text == "나는 저녁 운동을 선호한다"


@pytest.mark.anyio
async def test_memory_agent_does_not_update_latest_saved_document() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    await store.save_text_memory(scope=scope, text="먼저 저장한 메모", source_message_id="m1")
    await store.save_document(
        scope=scope,
        filename="latest.md",
        content_type="text/markdown",
        text="최근 저장 문서",
        source_message_id="m2",
    )

    response = await agent.update(text="방금 저장한 메모를 새 내용으로 바꿔줘", scope=scope)

    assert "최근 저장 항목은 문서" in response
    assert store.stats(scope=scope)["documents"] == 1


@pytest.mark.anyio
async def test_memory_agent_deletes_latest_saved_item() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    memory_id = await store.save_text_memory(scope=scope, text="실수로 저장한 메모", source_message_id="m1")

    response = await agent.delete(text="방금 저장한 거 지워줘", scope=scope)

    assert isinstance(response, OperationResult)
    assert response.summary == "최근 저장 기억 삭제 완료"
    assert response.facts["deleted_item"]["id"] == memory_id
    assert f"메모 `{memory_id}`" in response
    assert store.stats(scope=scope)["memories"] == 0


@pytest.mark.anyio
async def test_memory_agent_restores_latest_deleted_item() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    memory_id = await store.save_text_memory(scope=scope, text="복구할 메모", source_message_id="m1")
    store.delete_memory_ids(scope=scope, memory_ids=[memory_id])

    response = agent.restore(text="방금 지운 거 복구해줘", scope=scope)

    assert isinstance(response, OperationResult)
    assert response.summary == "최근 삭제 기억 복구 완료"
    assert response.facts["restored_item"]["id"] == memory_id
    assert f"메모 `{memory_id}`" in response
    assert store.stats(scope=scope)["memories"] == 1


@pytest.mark.anyio
async def test_memory_agent_lists_deleted_items_and_restores_by_id() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
    memory_id = await store.save_text_memory(scope=scope, text="삭제된 메모", source_message_id="m1")
    store.delete_memory_ids(scope=scope, memory_ids=[memory_id])

    list_response = agent.restore(text="삭제한 기억 목록 보여줘", scope=scope)
    restore_response = agent.restore(text=f"메모 {memory_id} 복구해줘", scope=scope)

    assert "최근 삭제된 기억" in list_response
    assert f"메모 `{memory_id}`" in list_response
    assert "삭제된 기억 1개를 복구했어요" in restore_response
    assert store.stats(scope=scope)["memories"] == 1


@pytest.mark.anyio
async def test_memory_agent_requires_confirmation_for_all_user_memory_deletion() -> None:
    database = AppDatabase(":memory:")
    store = MemoryStore(database.connection, FakeOpenAI())  # type: ignore[arg-type]
    agent = MemoryAgent(
        config=make_test_config(),
        openai=FakeOpenAI(),  # type: ignore[arg-type]
        memories=store,
        logs=AgentLogStore(database.connection),
    )
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    await store.save_text_memory(scope=scope, text="삭제할 메모", source_message_id="m1")
    await store.save_document(
        scope=scope,
        filename="delete.md",
        content_type="text/markdown",
        text="삭제할 문서",
        source_message_id="m2",
    )

    response = await agent.delete(text="내 기억 전부 삭제해줘", scope=scope)

    assert "확인이 필요" in response
    assert store.stats(scope=scope) == {"memories": 1, "documents": 1, "chunks": 1}


def test_pending_attachment_store_tracks_latest_unresolved_request() -> None:
    database = AppDatabase(":memory:")
    store = PendingAttachmentStore(database.connection)
    scope = ConversationScope(
        conversation_id="channel:1:user:user-1",
        channel_id="1",
        user_id="user-1",
        guild_id="guild-1",
    )

    first_id = store.add(scope=scope, message_id="100", filenames=["first.md"])
    second_id = store.add(scope=scope, message_id="101", filenames=["second.pdf"])

    latest = store.latest(scope=scope)
    assert latest is not None
    assert latest.id == second_id
    assert latest.message_id == "101"
    assert latest.filenames == ["second.pdf"]
    assert store.unresolved_count(scope=scope) == 2

    store.resolve(second_id)
    latest = store.latest(scope=scope)
    assert latest is not None
    assert latest.id == first_id
    assert latest.message_id == "100"
    assert store.unresolved_count(scope=scope) == 1

    resolved = store.resolve_latest(scope=scope)
    assert resolved is not None
    assert resolved.id == first_id
    assert store.latest(scope=scope) is None
    assert store.unresolved_count(scope=scope) == 0


def test_pending_attachment_store_expires_old_requests() -> None:
    database = AppDatabase(":memory:")
    store = PendingAttachmentStore(database.connection)
    scope = ConversationScope(
        conversation_id="channel:1:user:user-1",
        channel_id="1",
        user_id="user-1",
        guild_id="guild-1",
    )

    request_id = store.add(scope=scope, message_id="100", filenames=["old.md"])
    database.connection.execute(
        """
        UPDATE pending_attachment_requests
        SET created_at = '2000-01-01 00:00:00'
        WHERE id = ?
        """,
        (request_id,),
    )
    database.connection.commit()

    assert store.latest(scope=scope, ttl_minutes=10) is None
    assert store.unresolved_count(scope=scope, ttl_minutes=10) == 0


def test_pending_memory_deletion_store_tracks_confirmation_requests() -> None:
    database = AppDatabase(":memory:")
    store = PendingMemoryDeletionStore(database.connection)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    first_id = store.add(scope=scope, message_id="100", memory_count=2, document_count=1)
    second_id = store.add(scope=scope, message_id="101", memory_count=3, document_count=0)

    latest = store.latest(scope=scope)

    assert latest is not None
    assert latest.id == second_id
    assert latest.memory_count == 3
    assert latest.document_count == 0
    assert store.unresolved_count(scope=scope) == 2

    resolved = store.resolve_latest(scope=scope)

    assert resolved is not None
    assert resolved.id == second_id
    assert store.latest(scope=scope).id == first_id  # type: ignore[union-attr]
    assert store.unresolved_count(scope=scope) == 1


def test_pending_memory_deletion_store_expires_old_requests() -> None:
    database = AppDatabase(":memory:")
    store = PendingMemoryDeletionStore(database.connection)
    scope = ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )

    request_id = store.add(scope=scope, message_id="100", memory_count=2, document_count=1)
    database.connection.execute(
        """
        UPDATE pending_memory_deletions
        SET created_at = '2000-01-01 00:00:00'
        WHERE id = ?
        """,
        (request_id,),
    )
    database.connection.commit()

    assert store.latest(scope=scope, ttl_minutes=10) is None
    assert store.unresolved_count(scope=scope, ttl_minutes=10) == 0


def make_test_config() -> Config:
    return Config(
        discord_token="discord-token",
        discord_client_id="client-id",
        openai_api_key="openai-key",
        router_model="gpt-5.4-mini",
        easy_model="gpt-5.4-mini",
        medium_model="gpt-5.4",
        hard_model="gpt-5.5",
        embedding_model="text-embedding-3-small",
        database_path=":memory:",
        max_attachment_bytes=1024,
        context_compression_chars=20000,
        retrieval_limit=8,
        openai_timeout_seconds=30,
        openai_max_retries=2,
        pending_confirmation_ttl_minutes=10,
        task_reminder_interval_minutes=60,
        task_reminder_batch_size=20,
        timezone="Asia/Seoul",
        log_level="INFO",
        log_file=None,
    )
