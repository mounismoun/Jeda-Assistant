import pytest

from assistant_bot.agent_registry import (
    AgentContext,
    AgentDefinition,
    AgentRegistry,
    build_agent_definition,
    load_agent_catalog,
)
from assistant_bot.models import ConversationScope


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_agent_catalog_contains_router_metadata() -> None:
    catalog = load_agent_catalog("agent_catalog.json")
    intents = {entry["intent"] for entry in catalog}

    assert "chat" in intents
    assert "current_time" in intents
    assert "manage_task" in intents
    assert "manage_reminder" in intents
    assert "unsupported" in intents
    assert all(entry["examples"] for entry in catalog)


def test_registry_prompt_block_uses_catalog_examples() -> None:
    catalog = load_agent_catalog("agent_catalog.json")
    handlers = {entry["intent"]: lambda context: context.text for entry in catalog}
    registry = AgentRegistry()
    for entry in catalog:
        registry.register(build_agent_definition(entry, handlers))

    prompt_block = registry.routing_prompt_block()

    assert "- manage_task: Task Agent" in prompt_block
    assert "- manage_reminder: Reminder Agent" in prompt_block
    assert "- current_time: Utility Agent" in prompt_block
    assert "지금 몇시야?" in prompt_block
    assert "30분 뒤 물 마시라고 알려줘" in prompt_block
    assert "삭제한 기억 목록 보여줘" in prompt_block
    assert "사용 가능 도구: search_memories" in prompt_block


@pytest.mark.anyio
async def test_registry_dispatch_falls_back_to_chat() -> None:
    scope = ConversationScope(
        conversation_id="dm:1",
        channel_id="dm",
        user_id="1",
        guild_id=None,
    )
    registry = AgentRegistry()
    registry.register(
        AgentDefinition(
            intent="chat",
            name="Conversation Agent",
            purpose="일반 대화",
            description="일반 대화를 처리한다.",
            examples=("안녕",),
            tool_names=(),
            handler=lambda context: f"chat:{context.text}",
        )
    )

    answer = await registry.dispatch(
        "unknown",
        AgentContext(
            text="안녕",
            scope=scope,
            message_id="1",
            author_name="tester",
            location_label="DM",
        ),
    )

    assert answer == "chat:안녕"


def test_catalog_entry_requires_matching_handler() -> None:
    with pytest.raises(ValueError, match="handler"):
        build_agent_definition(
            {
                "intent": "calendar",
                "name": "Calendar Agent",
                "purpose": "일정 관리",
                "description": "일정을 처리한다.",
                "examples": ["내일 미팅 잡아줘"],
            },
            handlers={},
        )
