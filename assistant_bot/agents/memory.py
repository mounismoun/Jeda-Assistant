from __future__ import annotations

from assistant_bot.agent_toolkits import build_memory_read_tools
from assistant_bot.config import Config
from assistant_bot.model_selector import choose_model
from assistant_bot.models import ConversationScope
from assistant_bot.openai_service import OpenAIService
from assistant_bot.stores import AgentLogStore, ConversationStore, MemoryStore

from .common import (
    asks_to_delete_all_memories,
    asks_to_delete_latest_memory,
    asks_to_list_deleted_memories,
    asks_to_remember_recent_message,
    asks_to_search_memories,
    asks_to_show_latest_memory,
    asks_to_update_latest_memory,
    compact_preview,
    extract_delete_ids,
    extract_delete_query,
    extract_memory_search_query,
    extract_memory_text,
    extract_recall_ids,
    extract_restore_ids,
    extract_update_ids,
    extract_update_query,
    extract_update_text,
    format_detail,
)


class MemoryAgent:
    def __init__(
        self,
        *,
        config: Config,
        openai: OpenAIService,
        memories: MemoryStore,
        logs: AgentLogStore,
        conversations: ConversationStore | None = None,
    ) -> None:
        self.config = config
        self.openai = openai
        self.memories = memories
        self.logs = logs
        self.conversations = conversations

    async def remember_text(self, *, text: str, scope: ConversationScope, message_id: str) -> str:
        memory_text = extract_memory_text(text)
        if asks_to_remember_recent_message(text):
            if self.conversations is None:
                return "직전 대화를 확인할 수 없어요. 기억할 내용을 직접 적어 주세요."
            latest = self.conversations.latest_user_message(
                conversation_id=scope.conversation_id,
                user_id=scope.user_id,
            )
            if latest is None:
                return "직전에 저장할 만한 사용자 메시지가 없어요. 기억할 내용을 직접 적어 주세요."
            recent_text = str(latest["content"]).strip()
            if not recent_text or asks_to_remember_recent_message(recent_text):
                return "직전에 저장할 만한 내용을 찾지 못했어요. 기억할 내용을 직접 적어 주세요."
            memory_text = recent_text
        duplicate = self.memories.find_duplicate_text_memory(scope=scope, text=memory_text)
        if duplicate is not None:
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="memory",
                intent="remember",
                difficulty="easy",
                model=self.config.easy_model,
                reason="동일한 텍스트 기억 중복 저장 방지",
            )
            return (
                f"이미 같은 내용을 기억하고 있어요. 기존 메모 ID는 `{duplicate.id}`이고, "
                f"저장 위치는 {duplicate.source_location}입니다."
            )
        memory_id = await self.memories.save_text_memory(
            scope=scope,
            text=memory_text,
            source_message_id=message_id,
        )
        choice = choose_model(self.config, text)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="remember",
            difficulty=choice.difficulty,
            model=choice.model,
            reason=choice.reason,
        )
        return f"기억해둘게요. 저장 ID는 `{memory_id}`입니다."

    async def recall(self, *, text: str, scope: ConversationScope) -> str:
        if asks_to_show_latest_memory(text):
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="memory",
                intent="recall",
                difficulty="easy",
                model=self.config.easy_model,
                reason="최근 저장 항목 상세 조회",
            )
            return self.recall_latest_item(scope=scope)

        exact_memory_ids, exact_document_ids = extract_recall_ids(text)
        if exact_memory_ids or exact_document_ids:
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="memory",
                intent="recall",
                difficulty="easy",
                model=self.config.easy_model,
                reason="ID 기반 상세 조회",
            )
            return self.recall_by_ids(
                scope=scope,
                memory_ids=exact_memory_ids,
                document_ids=exact_document_ids,
            )

        choice = choose_model(
            self.config,
            text,
            context_chars=len(text),
            result_count=0,
        )
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="recall",
            difficulty=choice.difficulty,
            model=choice.model,
            reason=choice.reason,
        )

        instructions = """
너는 사용자의 저장된 기억과 문서에 근거해 답하는 개인 비서다.
답하기 전에 반드시 제공된 read-only 도구로 저장된 기억이나 문서를 조회한다.
도구 결과에 없는 내용은 추측이라고 분리해서 말하거나, 모른다고 말한다.
답변 마지막에는 참고한 파일명이나 기억 제목을 짧게 적는다.
"""
        return await self.openai.tool_response(
            model=choice.model,
            instructions=instructions,
            input_text=f"질문:\n{text}",
            tools=build_memory_read_tools(config=self.config, memories=self.memories, scope=scope),
            temperature=0.2,
        )

    def recall_latest_item(self, *, scope: ConversationScope) -> str:
        items = self.memories.recent_items(scope=scope, limit=1)
        if not items:
            return "아직 저장된 기억이 없어요. `이거 기억해줘: ...`처럼 말하면 장기 기억에 저장합니다."
        item = items[0]
        if item.kind == "memory":
            return self.recall_by_ids(scope=scope, memory_ids=[item.id], document_ids=[])
        return self.recall_by_ids(scope=scope, memory_ids=[], document_ids=[item.id])

    def recall_by_ids(
        self,
        *,
        scope: ConversationScope,
        memory_ids: list[int],
        document_ids: list[int],
    ) -> str:
        lines: list[str] = []
        missing: list[str] = []

        for memory_id in memory_ids:
            detail = self.memories.get_memory_detail(scope=scope, memory_id=memory_id)
            if detail is None:
                missing.append(f"메모 `{memory_id}`")
                continue
            lines.append(
                format_detail(
                    detail.title,
                    detail.text,
                    f"메모 `{detail.id}`",
                    detail.created_at,
                    detail.source_location,
                )
            )

        for document_id in document_ids:
            detail = self.memories.get_document_detail(scope=scope, document_id=document_id)
            if detail is None:
                missing.append(f"문서 `{document_id}`")
                continue
            label = f"문서 `{detail.id}` · {detail.chunk_count} chunks"
            lines.append(format_detail(detail.title, detail.text, label, detail.created_at, detail.source_location))

        if missing:
            lines.append("찾지 못한 항목: " + ", ".join(missing))
        if not lines:
            return "해당 ID의 기억이나 문서를 찾지 못했어요. `지금 뭘 기억하고 있어?`로 목록을 먼저 확인해 주세요."
        return "\n\n".join(lines)

    async def delete(self, *, text: str, scope: ConversationScope) -> str:
        if asks_to_delete_all_memories(text):
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="memory",
                intent="delete_memory",
                difficulty="easy",
                model=self.config.easy_model,
                reason="사용자 전체 장기 기억 삭제 확인 필요",
            )
            return "전체 기억 삭제는 확인이 필요해요. 다시 `내 기억 전부 삭제해줘`라고 말하면 확인 절차를 시작합니다."

        if asks_to_delete_latest_memory(text):
            deleted_item = self.memories.delete_latest_item(scope=scope)
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="memory",
                intent="delete_memory",
                difficulty="easy",
                model=self.config.easy_model,
                reason="최근 저장 항목 삭제",
            )
            if deleted_item is None:
                return "삭제할 최근 저장 기억이 없어요."
            label = "메모" if deleted_item.kind == "memory" else "문서"
            return f"가장 최근에 저장한 {label} `{deleted_item.id}` · {deleted_item.title}을 삭제 처리했어요."

        query = extract_delete_query(text)
        exact_memory_ids, exact_document_ids = extract_delete_ids(text)
        deleted_count = self.memories.delete_memory_ids(scope=scope, memory_ids=exact_memory_ids)
        deleted_count += self.memories.delete_document_ids(scope=scope, document_ids=exact_document_ids)

        if deleted_count == 0:
            deleted_count = self.memories.delete_by_query(scope=scope, query=query)

        if deleted_count == 0 and query:
            candidates = await self.memories.search(
                scope=scope,
                query=query,
                limit=5,
            )
            memory_ids = [result.id for result in candidates if result.kind == "memory" and result.score >= 0.28]
            document_ids = [result.id for result in candidates if result.kind == "document" and result.score >= 0.28]
            deleted_count = self.memories.delete_memory_ids(scope=scope, memory_ids=memory_ids)
            deleted_count += self.memories.delete_document_ids(scope=scope, document_ids=document_ids)

        choice = choose_model(self.config, text)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="delete_memory",
            difficulty=choice.difficulty,
            model=choice.model,
            reason=choice.reason,
        )
        if deleted_count == 0:
            return "삭제할 기억을 찾지 못했어요. 더 구체적인 키워드로 말해주면 다시 찾아볼게요."
        return f"관련 기억 {deleted_count}개를 삭제 처리했어요."

    def restore(self, *, text: str, scope: ConversationScope) -> str:
        if asks_to_list_deleted_memories(text):
            return self.list_deleted_memories(scope=scope)

        memory_ids, document_ids = extract_restore_ids(text)
        if memory_ids or document_ids:
            restored_count = self.memories.restore_memory_ids(scope=scope, memory_ids=memory_ids)
            restored_count += self.memories.restore_document_ids(scope=scope, document_ids=document_ids)
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="memory",
                intent="restore_memory",
                difficulty="easy",
                model=self.config.easy_model,
                reason="ID 기반 삭제 항목 복구",
            )
            if restored_count == 0:
                return "해당 ID의 삭제된 기억을 찾지 못했어요. `삭제한 기억 목록 보여줘`로 먼저 확인해 주세요."
            return f"삭제된 기억 {restored_count}개를 복구했어요."

        restored_item = self.memories.restore_latest_deleted_item(scope=scope)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="restore_memory",
            difficulty="easy",
            model=self.config.easy_model,
            reason="최근 삭제 항목 복구",
        )
        if restored_item is None:
            return "복구할 삭제된 기억이 없어요."
        label = "메모" if restored_item.kind == "memory" else "문서"
        return f"가장 최근에 삭제한 {label} `{restored_item.id}` · {restored_item.title}을 복구했어요."

    def list_deleted_memories(self, *, scope: ConversationScope) -> str:
        items = self.memories.deleted_items(scope=scope, limit=10)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="restore_memory",
            difficulty="easy",
            model=self.config.easy_model,
            reason="삭제된 기억 목록 조회",
        )
        if not items:
            return "삭제된 기억이 없어요."
        lines = ["최근 삭제된 기억:"]
        for item in items:
            label = "메모" if item.kind == "memory" else "문서"
            lines.append(
                f"- {label} `{item.id}` · {item.title} · {item.detail} · "
                f"저장 위치: {item.source_location} · 삭제 시각: {item.created_at}"
            )
        lines.append("복구하려면 `메모 3 복구해줘` 또는 `문서 2 복구해줘`처럼 말해 주세요.")
        return "\n".join(lines)

    async def list_memories(self, *, text: str, scope: ConversationScope) -> str:
        query = extract_memory_search_query(text)
        if asks_to_search_memories(text):
            return await self.search_memories(query=query, scope=scope)

        stats = self.memories.stats(scope=scope)
        items = self.memories.recent_items(scope=scope, limit=10)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="list_memory",
            difficulty="easy",
            model=self.config.easy_model,
            reason="저장된 기억 목록 조회",
        )

        if not items:
            return "아직 저장된 기억이 없어요. “이거 기억해줘: ...”처럼 말하면 장기 기억에 저장합니다."

        lines = [
            (
                f"현재 텍스트 기억 {stats['memories']}개, 문서 {stats['documents']}개"
                f"({stats['chunks']} chunks)를 기억하고 있어요."
            ),
            "최근 기억:",
        ]
        for item in items:
            label = "메모" if item.kind == "memory" else "문서"
            lines.append(f"- {label} `{item.id}` · {item.title} · {item.detail} · 저장 위치: {item.source_location}")
        return "\n".join(lines)

    async def search_memories(self, *, query: str, scope: ConversationScope) -> str:
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="list_memory",
            difficulty="easy",
            model=self.config.easy_model,
            reason="저장된 기억 검색 목록 조회",
        )
        if not query:
            return "찾을 기억 키워드를 알려주세요. 예: `운동 관련 기억 찾아줘`"

        results = await self.memories.search(scope=scope, query=query, limit=8)
        useful_results = [result for result in results if result.score >= 0.18]
        if not useful_results:
            return f"`{query}`와 관련된 저장 기억을 찾지 못했어요."

        lines = [f"`{query}` 관련 저장 기억 {len(useful_results)}개:"]
        for result in useful_results:
            label = "메모" if result.kind == "memory" else "문서"
            preview = compact_preview(result.text, limit=110)
            lines.append(
                f"- {label} `{result.id}` · {result.title} · 관련도 {result.score:.2f} · "
                f"저장 위치: {result.source_location}\n"
                f"  {preview}"
            )
        lines.append("자세히 보려면 `메모 3 보여줘` 또는 `문서 2 보여줘`처럼 말해 주세요.")
        return "\n".join(lines)

    async def update(self, *, text: str, scope: ConversationScope) -> str:
        memory_ids, document_ids = extract_update_ids(text)
        replacement = extract_update_text(text)
        choice = choose_model(self.config, text)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="update_memory",
            difficulty=choice.difficulty,
            model=choice.model,
            reason=choice.reason,
        )

        if document_ids:
            return (
                "문서 내용 수정은 아직 직접 지원하지 않아요. "
                "새 문서를 다시 기억시킨 뒤 기존 문서를 삭제해 주세요."
            )

        if not replacement:
            return "어떤 내용으로 수정할지 모르겠어요. 예: `메모 3을 나는 오전 운동을 선호한다로 수정해줘`"

        if asks_to_update_latest_memory(text):
            items = self.memories.recent_items(scope=scope, limit=1)
            if not items:
                return "수정할 최근 저장 기억이 없어요."
            latest_item = items[0]
            if latest_item.kind != "memory":
                return (
                    "최근 저장 항목은 문서라서 직접 수정할 수 없어요. "
                    "새 문서를 다시 기억시킨 뒤 기존 문서를 삭제해 주세요."
                )
            await self.memories.update_text_memory(scope=scope, memory_id=latest_item.id, text=replacement)
            return f"가장 최근에 저장한 메모 `{latest_item.id}`를 수정했어요."

        if memory_ids:
            updated = 0
            missing: list[str] = []
            for memory_id in memory_ids:
                if await self.memories.update_text_memory(scope=scope, memory_id=memory_id, text=replacement):
                    updated += 1
                else:
                    missing.append(f"메모 `{memory_id}`")
            lines = []
            if updated:
                lines.append(f"메모 {updated}개를 수정했어요.")
            if missing:
                lines.append("찾지 못한 항목: " + ", ".join(missing))
            return "\n".join(lines) if lines else "수정할 메모를 찾지 못했어요."

        query = extract_update_query(text)
        if not query:
            return "수정할 메모를 특정하지 못했어요. `지금 뭘 기억하고 있어?`로 ID를 확인한 뒤 수정해 주세요."

        candidates = await self.memories.search(scope=scope, query=query, limit=3)
        memory_candidates = [result for result in candidates if result.kind == "memory" and result.score >= 0.32]
        if len(memory_candidates) != 1:
            return (
                "수정할 메모를 확실히 고르지 못했어요. "
                "`지금 뭘 기억하고 있어?`로 ID를 확인한 뒤 `메모 3을 ...로 수정해줘`처럼 말해 주세요."
            )

        memory_id = memory_candidates[0].id
        await self.memories.update_text_memory(scope=scope, memory_id=memory_id, text=replacement)
        return f"가장 관련 있어 보이는 메모 `{memory_id}`를 수정했어요."

