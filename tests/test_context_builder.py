from __future__ import annotations

from assistant_bot.context_builder import build_execution_context, build_focused_context, build_router_context
from assistant_bot.database import AppDatabase
from assistant_bot.models import ConversationScope, RoutingResult
from assistant_bot.stores import ConversationStore
from tests.test_web_search_agent import make_config


def test_build_router_context_includes_summary_and_recent_messages() -> None:
    database = AppDatabase(":memory:")
    conversations = ConversationStore(database.connection)
    scope = make_scope()
    conversations.add_summary(scope.conversation_id, "사용자는 대한민국 대통령에 대해 물었다.")
    conversations.add_message(
        conversation_id=scope.conversation_id,
        role="user",
        user_id=scope.user_id,
        content="지금 한국 대통령 누구야",
    )
    conversations.add_message(
        conversation_id=scope.conversation_id,
        role="assistant",
        user_id="bot",
        content="검색 결과 기준 현재 대한민국 대통령은 이재명입니다.",
    )

    context = build_router_context(config=make_config(), conversations=conversations, scope=scope)

    assert "이전 요약:" in context
    assert "사용자는 대한민국 대통령에 대해 물었다." in context
    assert "최근 대화:" in context
    assert "대한민국 대통령은 이재명" in context


def test_build_execution_context_focuses_follow_up_question() -> None:
    database = AppDatabase(":memory:")
    conversations = ConversationStore(database.connection)
    scope = make_scope()
    conversations.add_summary(scope.conversation_id, "한국 대통령 관련 질의가 이어지고 있다.")
    conversations.add_message(
        conversation_id=scope.conversation_id,
        role="user",
        user_id=scope.user_id,
        content="지금 한국 대통령 누구야",
    )
    conversations.add_message(
        conversation_id=scope.conversation_id,
        role="assistant",
        user_id="bot",
        content="검색 결과 기준 현재 대한민국 대통령은 이재명입니다.",
    )
    route = RoutingResult(
        intent="web_search",
        confidence=0.95,
        reason="직전 대통령 질문의 후속 질문",
        search_need_score=75,
        search_decision="required",
        search_reason="현재 공직자 임기 확인",
    )

    execution = build_execution_context(
        config=make_config(),
        conversations=conversations,
        scope=scope,
        user_text="임기가 언제까지지?",
        route=route,
    )

    assert "대한민국 대통령은 이재명" in execution.focused_context
    assert execution.route_reason == "직전 대통령 질문의 후속 질문"
    assert execution.route_search_need_score == 75
    assert "한국 대통령 관련 질의" in execution.for_agent()


def test_execution_context_includes_same_user_other_location_context() -> None:
    database = AppDatabase(":memory:")
    conversations = ConversationStore(database.connection)
    scope = ConversationScope(
        conversation_id="channel:10:user:user-1",
        channel_id="10",
        user_id="user-1",
        guild_id="guild-1",
    )
    conversations.add_message(
        conversation_id="dm:user-1",
        role="user",
        user_id="user-1",
        content="DM에서 대통령 임기 이야기를 했다.",
    )
    conversations.add_summary("dm:user-1", "현재 대통령은 이재명이라는 확인이 있었다.")
    conversations.add_message(
        conversation_id=scope.conversation_id,
        role="user",
        user_id="user-1",
        content="여기는 서버 대화다.",
    )
    conversations.add_message(
        conversation_id="dm:user-2",
        role="user",
        user_id="user-2",
        content="다른 사용자 대화",
    )

    execution = build_execution_context(
        config=make_config(),
        conversations=conversations,
        scope=scope,
        user_text="임기가 언제까지지?",
    )

    assert "같은 사용자 다른 위치 최근 맥락" in execution.for_agent()
    assert "DM" in execution.cross_location_context
    assert "현재 대통령은 이재명" in execution.cross_location_context
    assert "여기는 서버 대화" not in execution.cross_location_context
    assert "다른 사용자 대화" not in execution.cross_location_context


def test_build_focused_context_respects_max_chars() -> None:
    focused = build_focused_context(
        user_text="임기가 언제까지지?",
        latest_summary="",
        recent_context="\n".join(f"user: 오래된 대화 {index}" for index in range(20)),
        max_chars=40,
    )

    assert len(focused) <= 40


def make_scope() -> ConversationScope:
    return ConversationScope(
        conversation_id="dm:user-1",
        channel_id="dm",
        user_id="user-1",
        guild_id=None,
    )
