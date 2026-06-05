from __future__ import annotations

from assistant_bot.agent_toolkits import build_memory_read_tools
from assistant_bot.config import Config
from assistant_bot.model_selector import choose_model
from assistant_bot.models import ConversationScope
from assistant_bot.openai_service import OpenAIService
from assistant_bot.operation_result import OperationResult
from assistant_bot.persona import ASSISTANT_PERSONA
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
    has_substantive_memory_text,
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

    async def remember_text(self, *, text: str, scope: ConversationScope, message_id: str) -> OperationResult:
        memory_text = extract_memory_text(text)
        if asks_to_remember_recent_message(text):
            if self.conversations is None:
                return self._result(
                    "직전 대화를 확인할 수 없어요. 기억할 내용을 직접 적어 주세요.",
                    status="needs_input",
                    summary="직전 대화 확인 불가",
                    next_actions=("기억할 내용을 직접 물어본다",),
                )
            latest = self.conversations.latest_user_message(
                conversation_id=scope.conversation_id,
                user_id=scope.user_id,
            )
            if latest is None:
                return self._result(
                    "직전에 저장할 만한 사용자 메시지가 없어요. 기억할 내용을 직접 적어 주세요.",
                    status="needs_input",
                    summary="직전 저장 대상 메시지 없음",
                    next_actions=("기억할 내용을 직접 물어본다",),
                )
            recent_text = str(latest["content"]).strip()
            if not recent_text or asks_to_remember_recent_message(recent_text):
                return self._result(
                    "직전에 저장할 만한 내용을 찾지 못했어요. 기억할 내용을 직접 적어 주세요.",
                    status="needs_input",
                    summary="직전 메시지에서 기억할 내용 추출 실패",
                    next_actions=("기억할 내용을 직접 물어본다",),
                )
            memory_text = recent_text
        elif not has_substantive_memory_text(text):
            return self._result(
                "메모할 내용을 알려주세요. 예: `메모: 나는 오전에 집중이 잘 된다`",
                status="needs_input",
                summary="저장할 메모 내용 필요",
                next_actions=("메모할 실제 내용을 물어본다",),
            )
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
            fallback = (
                f"이미 같은 내용을 기억하고 있어요. 기존 메모 ID는 `{duplicate.id}`이고, "
                f"저장 위치는 {duplicate.source_location}입니다."
            )
            return self._result(
                fallback,
                status="success",
                summary="중복 텍스트 기억 확인",
                facts={"duplicate_memory": self._stored_item(duplicate)},
                preserve_values=(str(duplicate.id), duplicate.source_location),
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
        return self._result(
            f"기억해둘게요. 저장 ID는 `{memory_id}`입니다.",
            status="success",
            summary="텍스트 기억 저장 완료",
            facts={"memory_id": memory_id, "text": memory_text},
            preserve_values=(str(memory_id),),
        )

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

        instructions = f"""
{ASSISTANT_PERSONA}

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

    def recall_latest_item(self, *, scope: ConversationScope) -> OperationResult:
        items = self.memories.recent_items(scope=scope, limit=1)
        if not items:
            return self._result(
                "아직 저장된 기억이 없어요. `이거 기억해줘: ...`처럼 말하면 장기 기억에 저장합니다.",
                status="not_found",
                summary="최근 저장된 기억 없음",
                next_actions=("새 기억을 저장할 수 있음을 짧게 안내한다",),
            )
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
    ) -> OperationResult:
        lines: list[str] = []
        missing: list[str] = []
        found_items: list[dict[str, object]] = []

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
            found_items.append(
                {
                    "kind": "memory",
                    "id": detail.id,
                    "title": detail.title,
                    "created_at": detail.created_at,
                    "source_location": detail.source_location,
                }
            )

        for document_id in document_ids:
            detail = self.memories.get_document_detail(scope=scope, document_id=document_id)
            if detail is None:
                missing.append(f"문서 `{document_id}`")
                continue
            label = f"문서 `{detail.id}` · {detail.chunk_count} chunks"
            lines.append(format_detail(detail.title, detail.text, label, detail.created_at, detail.source_location))
            found_items.append(
                {
                    "kind": "document",
                    "id": detail.id,
                    "title": detail.title,
                    "created_at": detail.created_at,
                    "source_location": detail.source_location,
                    "chunk_count": detail.chunk_count,
                }
            )

        if missing:
            lines.append("찾지 못한 항목: " + ", ".join(missing))
        if not lines:
            return self._result(
                "해당 ID의 기억이나 문서를 찾지 못했어요. `지금 뭘 기억하고 있어?`로 목록을 먼저 확인해 주세요.",
                status="not_found",
                summary="ID 기반 기억 상세 조회 결과 없음",
                facts={"memory_ids": memory_ids, "document_ids": document_ids},
                preserve_values=tuple(str(value) for value in memory_ids + document_ids),
            )
        return self._result(
            "\n\n".join(lines),
            status="success",
            summary="ID 기반 기억 상세 조회",
            facts={"memory_ids": memory_ids, "document_ids": document_ids, "missing": missing},
            items=tuple(found_items),
            warnings=tuple(missing),
            preserve_values=tuple(str(value) for value in memory_ids + document_ids),
        )

    async def delete(self, *, text: str, scope: ConversationScope) -> OperationResult:
        if asks_to_delete_all_memories(text):
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="memory",
                intent="delete_memory",
                difficulty="easy",
                model=self.config.easy_model,
                reason="사용자 전체 장기 기억 삭제 확인 필요",
            )
            return self._result(
                "전체 기억 삭제는 확인이 필요해요. 다시 `내 기억 전부 삭제해줘`라고 말하면 확인 절차를 시작합니다.",
                status="confirm_required",
                summary="전체 기억 삭제 확인 필요",
                next_actions=("전체 기억 삭제 확인 절차를 안내한다",),
            )

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
                return self._result(
                    "삭제할 최근 저장 기억이 없어요.",
                    status="not_found",
                    summary="삭제할 최근 저장 기억 없음",
                )
            label = "메모" if deleted_item.kind == "memory" else "문서"
            fallback = f"가장 최근에 저장한 {label} `{deleted_item.id}` · {deleted_item.title}을 삭제 처리했어요."
            return self._result(
                fallback,
                status="success",
                summary="최근 저장 기억 삭제 완료",
                facts={"deleted_item": self._stored_item(deleted_item), "label": label},
                preserve_values=(str(deleted_item.id), deleted_item.title),
            )

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
            return self._result(
                "삭제할 기억을 찾지 못했어요. 더 구체적인 키워드로 말해주면 다시 찾아볼게요.",
                status="not_found",
                summary="삭제 대상 기억 없음",
                facts={"query": query, "memory_ids": exact_memory_ids, "document_ids": exact_document_ids},
                preserve_values=tuple(str(value) for value in exact_memory_ids + exact_document_ids),
                next_actions=("더 구체적인 키워드를 물어본다",),
            )
        return self._result(
            f"관련 기억 {deleted_count}개를 삭제 처리했어요.",
            status="success",
            summary="관련 기억 삭제 완료",
            facts={
                "deleted_count": deleted_count,
                "query": query,
                "memory_ids": exact_memory_ids,
                "document_ids": exact_document_ids,
            },
            preserve_values=(str(deleted_count),)
            + tuple(str(value) for value in exact_memory_ids + exact_document_ids),
        )

    def restore(self, *, text: str, scope: ConversationScope) -> OperationResult:
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
                return self._result(
                    "해당 ID의 삭제된 기억을 찾지 못했어요. `삭제한 기억 목록 보여줘`로 먼저 확인해 주세요.",
                    status="not_found",
                    summary="ID 기반 복구 대상 없음",
                    facts={"memory_ids": memory_ids, "document_ids": document_ids},
                    preserve_values=tuple(str(value) for value in memory_ids + document_ids),
                )
            return self._result(
                f"삭제된 기억 {restored_count}개를 복구했어요.",
                status="success",
                summary="ID 기반 삭제 기억 복구 완료",
                facts={"restored_count": restored_count, "memory_ids": memory_ids, "document_ids": document_ids},
                preserve_values=(str(restored_count),)
                + tuple(str(value) for value in memory_ids + document_ids),
            )

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
            return self._result(
                "복구할 삭제된 기억이 없어요.",
                status="not_found",
                summary="최근 복구 대상 삭제 기억 없음",
            )
        label = "메모" if restored_item.kind == "memory" else "문서"
        fallback = f"가장 최근에 삭제한 {label} `{restored_item.id}` · {restored_item.title}을 복구했어요."
        return self._result(
            fallback,
            status="success",
            summary="최근 삭제 기억 복구 완료",
            facts={"restored_item": self._stored_item(restored_item), "label": label},
            preserve_values=(str(restored_item.id), restored_item.title),
        )

    def list_deleted_memories(self, *, scope: ConversationScope) -> OperationResult:
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
            return self._result(
                "삭제된 기억이 없어요.",
                status="success",
                summary="삭제된 기억 없음",
            )
        lines = ["최근 삭제된 기억:"]
        for item in items:
            label = "메모" if item.kind == "memory" else "문서"
            lines.append(
                f"- {label} `{item.id}` · {item.title} · {item.detail} · "
                f"저장 위치: {item.source_location} · 삭제 시각: {item.created_at}"
            )
        lines.append("복구하려면 `메모 3 복구해줘` 또는 `문서 2 복구해줘`처럼 말해 주세요.")
        return self._result(
            "\n".join(lines),
            status="success",
            summary="삭제된 기억 목록 조회",
            facts={"deleted_count": len(items)},
            items=tuple(self._stored_item(item) for item in items),
            preserve_values=tuple(str(item.id) for item in items),
            next_actions=("복구가 필요하면 ID로 요청할 수 있음을 짧게 안내한다",),
        )

    async def list_memories(self, *, text: str, scope: ConversationScope) -> OperationResult:
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
            return self._result(
                "아직 저장된 기억이 없어요. “이거 기억해줘: ...”처럼 말하면 장기 기억에 저장합니다.",
                status="success",
                summary="저장된 기억 없음",
                facts=stats,
                next_actions=("새 기억을 저장할 수 있음을 짧게 안내한다",),
            )

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
        return self._result(
            "\n".join(lines),
            status="success",
            summary="저장된 기억 목록 조회",
            facts=stats,
            items=tuple(self._stored_item(item) for item in items),
            preserve_values=tuple(str(item.id) for item in items),
        )

    async def search_memories(self, *, query: str, scope: ConversationScope) -> OperationResult:
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="list_memory",
            difficulty="easy",
            model=self.config.easy_model,
            reason="저장된 기억 검색 목록 조회",
        )
        if not query:
            return self._result(
                "찾을 기억 키워드를 알려주세요. 예: `운동 관련 기억 찾아줘`",
                status="needs_input",
                summary="기억 검색 키워드 필요",
                next_actions=("찾을 기억 키워드를 물어본다",),
            )

        results = await self.memories.search(scope=scope, query=query, limit=8)
        useful_results = [result for result in results if result.score >= 0.18]
        if not useful_results:
            return self._result(
                f"`{query}`와 관련된 저장 기억을 찾지 못했어요.",
                status="not_found",
                summary="검색 조건에 맞는 저장 기억 없음",
                facts={"query": query},
                preserve_values=(query,),
            )

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
        return self._result(
            "\n".join(lines),
            status="success",
            summary="저장 기억 검색 결과 조회",
            facts={"query": query, "result_count": len(useful_results)},
            items=tuple(
                {
                    "kind": result.kind,
                    "id": result.id,
                    "title": result.title,
                    "score": result.score,
                    "source_location": result.source_location,
                    "preview": compact_preview(result.text, limit=110),
                }
                for result in useful_results
            ),
            preserve_values=(query,) + tuple(str(result.id) for result in useful_results),
            next_actions=("상세 조회가 필요하면 ID로 요청할 수 있음을 짧게 안내한다",),
        )

    async def update(self, *, text: str, scope: ConversationScope) -> OperationResult:
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
            fallback = (
                "문서 내용 수정은 아직 직접 지원하지 않아요. "
                "새 문서를 다시 기억시킨 뒤 기존 문서를 삭제해 주세요."
            )
            return self._result(
                fallback,
                status="unsupported",
                summary="문서 내용 직접 수정 미지원",
                facts={"document_ids": document_ids},
                preserve_values=tuple(str(document_id) for document_id in document_ids),
                next_actions=("새 문서를 다시 기억시키고 기존 문서를 삭제하는 대안을 안내한다",),
            )

        if not replacement:
            return self._result(
                "어떤 내용으로 수정할지 모르겠어요. 예: `메모 3을 나는 오전 운동을 선호한다로 수정해줘`",
                status="needs_input",
                summary="수정할 새 내용 필요",
                next_actions=("수정할 내용을 물어본다",),
            )

        if asks_to_update_latest_memory(text):
            items = self.memories.recent_items(scope=scope, limit=1)
            if not items:
                return self._result(
                    "수정할 최근 저장 기억이 없어요.",
                    status="not_found",
                    summary="수정할 최근 저장 기억 없음",
                )
            latest_item = items[0]
            if latest_item.kind != "memory":
                fallback = (
                    "최근 저장 항목은 문서라서 직접 수정할 수 없어요. "
                    "새 문서를 다시 기억시킨 뒤 기존 문서를 삭제해 주세요."
                )
                return self._result(
                    fallback,
                    status="unsupported",
                    summary="최근 저장 항목이 문서라 직접 수정 불가",
                    facts={"latest_item": self._stored_item(latest_item)},
                    preserve_values=(str(latest_item.id), latest_item.title),
                    next_actions=("새 문서를 다시 기억시키고 기존 문서를 삭제하는 대안을 안내한다",),
                )
            await self.memories.update_text_memory(scope=scope, memory_id=latest_item.id, text=replacement)
            return self._result(
                f"가장 최근에 저장한 메모 `{latest_item.id}`를 수정했어요.",
                status="success",
                summary="최근 저장 메모 수정 완료",
                facts={"memory_id": latest_item.id, "replacement": replacement},
                preserve_values=(str(latest_item.id),),
            )

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
            if not lines:
                return self._result(
                    "수정할 메모를 찾지 못했어요.",
                    status="not_found",
                    summary="수정할 메모 없음",
                    facts={"memory_ids": memory_ids},
                    preserve_values=tuple(str(memory_id) for memory_id in memory_ids),
                )
            return self._result(
                "\n".join(lines),
                status="success" if updated else "not_found",
                summary="ID 기반 메모 수정 처리",
                facts={"updated_count": updated, "memory_ids": memory_ids, "missing": missing},
                warnings=tuple(missing),
                preserve_values=tuple(str(memory_id) for memory_id in memory_ids),
            )

        query = extract_update_query(text)
        if not query:
            return self._result(
                "수정할 메모를 특정하지 못했어요. `지금 뭘 기억하고 있어?`로 ID를 확인한 뒤 수정해 주세요.",
                status="needs_input",
                summary="수정 대상 메모 특정 실패",
                next_actions=("기억 목록에서 ID를 확인해 수정하도록 안내한다",),
            )

        candidates = await self.memories.search(scope=scope, query=query, limit=3)
        memory_candidates = [result for result in candidates if result.kind == "memory" and result.score >= 0.32]
        if len(memory_candidates) != 1:
            fallback = (
                "수정할 메모를 확실히 고르지 못했어요. "
                "`지금 뭘 기억하고 있어?`로 ID를 확인한 뒤 `메모 3을 ...로 수정해줘`처럼 말해 주세요."
            )
            return self._result(
                fallback,
                status="needs_input",
                summary="검색 기반 수정 대상이 모호함",
                facts={"query": query, "candidate_count": len(memory_candidates)},
                preserve_values=(query,),
                next_actions=("기억 목록에서 ID를 확인해 수정하도록 안내한다",),
            )

        memory_id = memory_candidates[0].id
        await self.memories.update_text_memory(scope=scope, memory_id=memory_id, text=replacement)
        return self._result(
            f"가장 관련 있어 보이는 메모 `{memory_id}`를 수정했어요.",
            status="success",
            summary="검색 기반 메모 수정 완료",
            facts={"memory_id": memory_id, "query": query, "replacement": replacement},
            preserve_values=(str(memory_id), query),
        )

    def _result(
        self,
        fallback_text: str,
        *,
        status: str = "success",
        summary: str,
        facts: dict[str, object] | None = None,
        items: tuple[dict[str, object], ...] = (),
        warnings: tuple[str, ...] = (),
        next_actions: tuple[str, ...] = (),
        preserve_values: tuple[str, ...] = (),
    ) -> OperationResult:
        return OperationResult(
            agent="memory",
            intent="memory",
            status=status,
            summary=summary,
            facts=facts or {},
            items=items,
            warnings=warnings,
            next_actions=next_actions,
            preserve_values=preserve_values,
            fallback_text=fallback_text,
        )

    def _stored_item(self, item) -> dict[str, object]:
        return {
            "kind": item.kind,
            "id": item.id,
            "title": item.title,
            "detail": getattr(item, "detail", ""),
            "source_location": item.source_location,
            "created_at": getattr(item, "created_at", None),
        }
