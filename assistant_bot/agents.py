from __future__ import annotations

import json
import re
from datetime import datetime, timedelta

from assistant_bot.config import Config
from assistant_bot.model_selector import choose_model
from assistant_bot.models import ConversationScope, RoutingResult, TaskItem
from assistant_bot.openai_service import OpenAIService
from assistant_bot.stores import AgentLogStore, ConversationStore, MemoryStore, TaskStore, normalize_task_priority
from assistant_bot.time_utils import now_in_timezone, resolve_timezone, today_string


class RouterAgent:
    def __init__(self, config: Config, openai: OpenAIService, logs: AgentLogStore) -> None:
        self.config = config
        self.openai = openai
        self.logs = logs

    async def route(
        self,
        *,
        text: str,
        has_attachments: bool,
        scope: ConversationScope,
    ) -> RoutingResult:
        heuristic = heuristic_route(text, has_attachments)
        if heuristic.confidence >= 0.92:
            self.logs.add(
                conversation_id=scope.conversation_id,
                agent="router",
                intent=heuristic.intent,
                model=self.config.router_model,
                reason=f"휴리스틱 라우팅: {heuristic.reason}",
            )
            return heuristic

        instructions = """
너는 Discord 대화형 비서의 라우터다.
사용자 메시지를 아래 intent 중 하나로만 분류한다.
- chat: 일반 대화, 도움 요청, 저장된 기억이 필요 없는 질문
- help: 사용법, 할 수 있는 일, 예시를 묻는 요청
- status: 봇 상태, 설정 모델, 저장소 상태, 현재 동작 상태를 묻는 요청
- cancel_pending: 직전 첨부 저장 확인이나 대기 중인 저장 요청을 취소하는 요청
- remember: 사용자가 무언가를 기억/저장하라고 명시적으로 요청
- recall: 저장된 기억이나 문서에 근거해 답해야 하는 질문
- list_memory: 저장된 기억 목록, 상태, 개수, 무엇을 기억하는지 묻는 요청
- update_memory: 저장된 텍스트 메모를 수정하거나 바꾸라는 요청
- delete_memory: 저장된 기억이나 문서를 삭제/잊으라고 요청
- restore_memory: 삭제한 기억이나 문서를 복구하거나, 삭제한 기억 목록을 보려는 요청
- reset_context: 현재 대화의 최근 메시지와 압축 요약을 초기화하라는 요청. 장기 기억 삭제가 아님
- manage_task: 할 일 추가, 조회, 완료, 삭제 요청
- daily_briefing: 오늘 브리핑, 오늘 할 일과 최근 기억 요약 요청
- unsupported: 처리할 수 없는 요청

JSON만 반환한다. 형식: {"intent":"chat","confidence":0.0,"reason":"짧은 이유"}
"""
        output = await self.openai.text_response(
            model=self.config.router_model,
            instructions=instructions,
            input_text=f"첨부 파일 있음: {has_attachments}\n메시지: {text}",
            temperature=0,
        )
        route = parse_routing_result(output)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="router",
            intent=route.intent,
            model=self.config.router_model,
            reason=route.reason,
        )
        return route


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

        results = await self.memories.search(
            scope=scope,
            query=text,
            limit=self.config.retrieval_limit,
        )
        useful_results = [result for result in results if result.score >= 0.18]
        context = format_memory_context(useful_results)
        choice = choose_model(
            self.config,
            text,
            context_chars=len(context),
            result_count=len(useful_results),
        )
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="memory",
            intent="recall",
            difficulty=choice.difficulty,
            model=choice.model,
            reason=choice.reason,
        )

        if not useful_results:
            return (
                "저장된 기억과 문서에서는 답을 찾지 못했어요. "
                "필요한 내용을 기억해두라고 알려주면 다음부터 근거로 사용할 수 있습니다."
            )

        instructions = """
너는 사용자의 저장된 기억과 문서에 근거해 답하는 개인 비서다.
반드시 제공된 근거를 우선한다.
근거에 없는 내용은 추측이라고 분리해서 말하거나, 모른다고 말한다.
답변 마지막에는 참고한 파일명이나 기억 제목을 짧게 적는다.
"""
        return await self.openai.text_response(
            model=choice.model,
            instructions=instructions,
            input_text=f"질문:\n{text}\n\n저장된 근거:\n{context}",
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


class UtilityAgent:
    def __init__(
        self,
        *,
        config: Config,
        memories: MemoryStore,
        tasks: TaskStore,
        logs: AgentLogStore,
        conversations: ConversationStore | None = None,
    ) -> None:
        self.config = config
        self.memories = memories
        self.tasks = tasks
        self.logs = logs
        self.conversations = conversations

    def help(self, *, scope: ConversationScope) -> str:
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="utility",
            intent="help",
            difficulty="easy",
            model=self.config.easy_model,
            reason="도움말 조회",
        )
        return "\n".join(
            [
                "제가 지금 도와드릴 수 있는 일은 이렇습니다.",
                "- `이거 기억해줘: ...`로 메모를 장기 기억에 저장",
                "- `.txt`, `.md`, `.pdf`를 첨부하고 `이 파일 기억해줘`로 문서 저장",
                "- 첨부만 보낸 뒤 제 확인 메시지에 `응, 기억해줘`라고 답장해서 저장",
                "- `전에 저장한 회의 문서 기준으로 정리해줘`처럼 기억 기반 질문",
                "- `지금 뭘 기억하고 있어?`로 기억 목록 확인",
                "- `메모 3 보여줘`, `문서 2 보여줘`로 저장 항목 상세 확인",
                "- `메모 3을 새 내용으로 수정해줘`로 텍스트 메모 수정",
                "- `운동 관련 기억 삭제해줘`, `메모 3 삭제해줘`, `문서 2 삭제해줘`로 삭제",
                "- `방금 저장한 거 지워줘`로 가장 최근 저장 항목 삭제",
                "- `방금 지운 거 복구해줘`로 가장 최근 삭제 항목 복구",
                "- `대화 맥락 초기화해줘`로 현재 대화 기록과 요약 초기화",
                "- `오늘 브리핑 해줘`로 오늘까지 할 일과 최근 기억 확인",
                "- `할 일 추가: 금요일까지 제안서 초안 작성`으로 개인 할 일 저장",
                "- `할 일 목록 보여줘`, `할 일 3 완료했어`로 작업 관리",
                "- `내 기억 전부 삭제해줘`로 사용자 기준 장기 기억 전체 삭제",
                "",
                "같은 사용자의 장기 기억은 DM, 서버, 스레드 어디서든 이어집니다.",
                "저는 멘션, 제 메시지에 대한 답글, DM에서만 반응합니다.",
            ]
        )

    def status(
        self,
        *,
        scope: ConversationScope,
        pending_count: int,
        pending_deletion_count: int,
        location_label: str,
    ) -> str:
        stats = self.memories.stats(scope=scope)
        task_stats = self.tasks.stats(scope=scope)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="utility",
            intent="status",
            difficulty="easy",
            model=self.config.easy_model,
            reason="상태 조회",
        )
        return "\n".join(
            [
                "현재 상태입니다.",
                f"- 현재 대화 위치: {location_label}",
                f"- 기억: 메모 {stats['memories']}개, 문서 {stats['documents']}개, chunk {stats['chunks']}개",
                f"- 할 일: 열린 작업 {task_stats['open']}개, 완료 {task_stats['completed']}개",
                f"- 저장 확인 대기 첨부: {pending_count}개",
                f"- 삭제 확인 대기 기억: {pending_deletion_count}개",
                f"- 라우터 모델: `{self.config.router_model}`",
                (
                    "- 답변 모델: "
                    f"easy `{self.config.easy_model}`, "
                    f"medium `{self.config.medium_model}`, "
                    f"hard `{self.config.hard_model}`"
                ),
                f"- embedding 모델: `{self.config.embedding_model}`",
            ]
        )

    def daily_briefing(self, *, scope: ConversationScope, location_label: str) -> str:
        today = today_string(self.config.timezone)
        memory_stats = self.memories.stats(scope=scope)
        task_stats = self.tasks.stats(scope=scope)
        due_tasks = self.tasks.list_due(scope=scope, due_before=today, limit=8)
        recent_memories = self.memories.recent_items(scope=scope, limit=5)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="utility",
            intent="daily_briefing",
            difficulty="easy",
            model=self.config.easy_model,
            reason="일일 브리핑 조회",
        )

        lines = [
            f"오늘 브리핑입니다. 현재 위치: {location_label}",
            f"- 열린 할 일: {task_stats['open']}개 · 완료한 할 일: {task_stats['completed']}개",
        ]
        if due_tasks:
            lines.append("오늘까지 처리할 할 일:")
            for task in due_tasks:
                due_text = "오늘까지" if task.due_at == today else f"{task.due_at}까지"
                lines.append(
                    f"- 할 일 `{task.id}` · {task.title} · 우선순위: {format_task_priority(task.priority)} · {due_text}"
                )
        else:
            lines.append("오늘까지 처리해야 하는 열린 할 일은 없어요.")

        lines.append(
            f"저장 기억: 메모 {memory_stats['memories']}개, 문서 {memory_stats['documents']}개"
            f"({memory_stats['chunks']} chunks)"
        )
        if recent_memories:
            lines.append("최근 기억:")
            for item in recent_memories[:3]:
                label = "메모" if item.kind == "memory" else "문서"
                lines.append(f"- {label} `{item.id}` · {item.title} · 저장 위치: {item.source_location}")
        else:
            lines.append("최근 기억은 아직 없어요.")

        if self.conversations is not None:
            recent_conversations = self.conversations.recent_conversations_for_user(user_id=scope.user_id, limit=3)
            if recent_conversations:
                lines.append("최근 대화 위치:")
                for conversation in recent_conversations:
                    preview = compact_preview(str(conversation["latest_content"]), limit=72)
                    lines.append(
                        f"- {format_conversation_location(str(conversation['conversation_id']))} · "
                        f"사용자 메시지 {conversation['user_message_count']}개 · "
                        f"최근: {conversation['latest_user_message_at']}\n"
                        f"  {preview}"
                    )
            else:
                lines.append("최근 대화 기록은 아직 없어요.")

        lines.append("바로 볼 수 있는 명령: `오늘 할 일 뭐야?`, `최근 대화에서 할 일 뽑아줘`")
        return "\n".join(lines)

    def reset_context(self, *, scope: ConversationScope, conversations: ConversationStore) -> str:
        counts = conversations.clear_conversation(scope.conversation_id)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="utility",
            intent="reset_context",
            difficulty="easy",
            model=self.config.easy_model,
            reason="현재 대화 맥락 초기화",
        )
        if counts["messages"] == 0 and counts["summaries"] == 0:
            return "초기화할 이전 대화 맥락이 없어요. 장기 기억은 그대로 유지됩니다."
        return (
            "현재 대화 맥락을 초기화했어요. "
            f"이전 메시지 {counts['messages']}개와 요약 {counts['summaries']}개를 지웠고, "
            "장기 기억은 그대로 유지됩니다."
        )


class TaskAgent:
    def __init__(
        self,
        *,
        config: Config,
        tasks: TaskStore,
        conversations: ConversationStore,
        logs: AgentLogStore,
    ) -> None:
        self.config = config
        self.tasks = tasks
        self.conversations = conversations
        self.logs = logs

    def handle(self, *, text: str, scope: ConversationScope, message_id: str | None = None) -> str:
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="task",
            intent="manage_task",
            difficulty="easy",
            model=self.config.easy_model,
            reason="할 일 관리 요청",
        )

        if asks_to_extract_tasks(text):
            return self.extract_tasks_from_conversation(text=text, scope=scope, message_id=message_id)

        if asks_to_list_deleted_tasks(text):
            return self.list_deleted_tasks(scope=scope)

        if asks_to_list_due_tasks(text):
            return self.list_due_tasks(text=text, scope=scope)

        if asks_to_search_tasks(text):
            return self.search_tasks(text=text, scope=scope)

        if asks_to_show_task_detail(text):
            return self.show_task_detail(text=text, scope=scope)

        if asks_to_list_tasks(text):
            return self.list_tasks(text=text, scope=scope)

        task_ids = extract_task_ids(text)
        if asks_to_clear_task_due(text):
            if asks_to_reference_latest_added_task(text):
                latest_task = self.tasks.latest(scope=scope)
                if latest_task is None or latest_task.status != "open":
                    return "기한을 없앨 최근 열린 할 일이 없어요."
                task_ids = [latest_task.id]
            else:
                task_ids, resolution_error = self.resolve_task_ids_from_text(
                    text=text,
                    scope=scope,
                    explicit_ids=task_ids,
                    target_status="open",
                    action_label="기한을 없앨",
                    example="`할 일 3 기한 없애줘`",
                )
                if resolution_error:
                    return resolution_error
            cleared = self.tasks.clear_due(scope=scope, task_ids=task_ids)
            if cleared == 0:
                return "기한을 없앨 열린 할 일을 찾지 못했어요. `할 일 목록 보여줘`로 ID를 확인해 주세요."
            return f"할 일 {cleared}개에서 기한과 리마인더 예약을 제거했어요."

        if asks_to_postpone_task(text):
            due_at = extract_due_at(text, timezone_name=self.config.timezone)
            if due_at is None:
                return "언제로 미룰지 알려주세요. 예: `할 일 3 내일 다시 알려줘`"
            if asks_to_reference_latest_added_task(text):
                latest_task = self.tasks.latest(scope=scope)
                if latest_task is None or latest_task.status != "open":
                    return "미룰 최근 열린 할 일이 없어요."
                task_ids = [latest_task.id]
            elif asks_to_snooze_latest_reminded_task(text):
                latest_task = self.tasks.latest_reminded_open(scope=scope)
                if latest_task is None:
                    return "다시 알려줄 최근 리마인더가 없어요. `할 일 3 30분 뒤 다시 알려줘`처럼 ID를 알려주세요."
                task_ids = [latest_task.id]
            else:
                task_ids, resolution_error = self.resolve_task_ids_from_text(
                    text=text,
                    scope=scope,
                    explicit_ids=task_ids,
                    target_status="open",
                    action_label="미룰",
                    example="`할 일 3 내일 다시 알려줘`",
                )
                if resolution_error:
                    return resolution_error
            postponed = self.tasks.postpone(scope=scope, task_ids=task_ids, due_at=due_at)
            if postponed == 0:
                return "미룰 열린 할 일을 찾지 못했어요. `할 일 목록 보여줘`로 ID를 확인해 주세요."
            return f"할 일 {postponed}개를 `{due_at}`로 미뤘어요. 리마인더도 다시 예약했습니다."

        if asks_to_rename_task(text):
            title = extract_task_rename_title(text)
            if not title:
                return "새 할 일 제목을 알려주세요. 예: `할 일 3을 고객 미팅 준비로 바꿔줘`"
            if asks_to_reference_latest_added_task(text):
                latest_task = self.tasks.latest(scope=scope)
                if latest_task is None or latest_task.status != "open":
                    return "제목을 바꿀 최근 열린 할 일이 없어요."
                task_ids = [latest_task.id]
            elif not task_ids:
                return "수정할 할 일 ID를 알려주세요. 예: `할 일 3을 고객 미팅 준비로 바꿔줘`"
            renamed = self.tasks.rename(scope=scope, task_ids=task_ids, title=title)
            if renamed == 0:
                return "수정할 열린 할 일을 찾지 못했어요. `할 일 목록 보여줘`로 ID를 확인해 주세요."
            return f"할 일 {renamed}개 제목을 `{title}`로 바꿨어요."

        if asks_to_set_task_priority(text):
            priority = extract_task_priority(text)
            if priority is None:
                return "우선순위를 높음, 보통, 낮음 중 하나로 알려주세요. 예: `할 일 3 우선순위 높음`"
            if asks_to_reference_latest_added_task(text):
                latest_task = self.tasks.latest(scope=scope)
                if latest_task is None or latest_task.status != "open":
                    return "우선순위를 바꿀 최근 열린 할 일이 없어요."
                task_ids = [latest_task.id]
            else:
                task_ids, resolution_error = self.resolve_task_ids_from_text(
                    text=text,
                    scope=scope,
                    explicit_ids=task_ids,
                    target_status="open",
                    action_label="우선순위를 바꿀",
                    example="`할 일 3 중요하게 표시해줘`",
                )
                if resolution_error:
                    return resolution_error
            changed = self.tasks.set_priority(scope=scope, task_ids=task_ids, priority=priority)
            if changed == 0:
                return "우선순위를 바꿀 열린 할 일을 찾지 못했어요. `할 일 목록 보여줘`로 ID를 확인해 주세요."
            return f"할 일 {changed}개 우선순위를 `{format_task_priority(priority)}`으로 바꿨어요."

        if asks_to_reopen_task(text):
            if asks_to_reopen_latest_completed_task(text):
                reopened_task = self.tasks.reopen_latest_completed(scope=scope)
                if reopened_task is None:
                    return "다시 열 최근 완료 할 일이 없어요."
                return f"가장 최근에 완료한 할 일 `{reopened_task.id}` · {reopened_task.title}을 다시 열었어요."
            task_ids, resolution_error = self.resolve_task_ids_from_text(
                text=text,
                scope=scope,
                explicit_ids=task_ids,
                target_status="completed",
                action_label="다시 열",
                example="`할 일 3 다시 열어줘`",
            )
            if resolution_error:
                return resolution_error
            reopened = self.tasks.reopen(scope=scope, task_ids=task_ids)
            if reopened == 0:
                return "다시 열 완료된 할 일을 찾지 못했어요. `할 일 목록 보여줘`로 ID를 확인해 주세요."
            return f"할 일 {reopened}개를 다시 열었어요."

        if asks_to_restore_task(text):
            if task_ids:
                restored = self.tasks.restore(scope=scope, task_ids=task_ids)
                if restored == 0:
                    return "복구할 삭제된 할 일을 찾지 못했어요. `삭제한 할 일 목록 보여줘`로 ID를 확인해 주세요."
                return f"삭제한 할 일 {restored}개를 복구했어요."
            restored_task = self.tasks.restore_latest_deleted(scope=scope)
            if restored_task is None:
                return "복구할 삭제된 할 일이 없어요."
            return f"가장 최근에 삭제한 할 일 `{restored_task.id}` · {restored_task.title}을 복구했어요."

        if asks_to_complete_task(text):
            if asks_to_complete_task_batch(text):
                return self.complete_task_batch(text=text, scope=scope)
            task_ids, resolution_error = self.resolve_task_ids_from_text(
                text=text,
                scope=scope,
                explicit_ids=task_ids,
                target_status="open",
                action_label="완료할",
                example="`할 일 3 완료했어`",
            )
            if resolution_error:
                return resolution_error
            completed = self.tasks.complete(scope=scope, task_ids=task_ids)
            if completed == 0:
                return "완료할 열린 할 일을 찾지 못했어요. `할 일 목록 보여줘`로 ID를 확인해 주세요."
            return f"할 일 {completed}개를 완료 처리했어요."

        if asks_to_delete_task(text):
            if asks_to_delete_latest_task(text):
                item = self.tasks.latest(scope=scope)
                if item is None:
                    return "삭제할 최근 할 일이 없어요."
                deleted = self.tasks.delete(scope=scope, task_ids=[item.id])
                if deleted == 0:
                    return "삭제할 최근 할 일을 찾지 못했어요."
                return (
                    f"가장 최근에 추가한 할 일 `{item.id}` · {item.title}을 삭제했어요. "
                    f"실수라면 `할 일 {item.id} 복구해줘`라고 말해 주세요."
                )
            task_ids, resolution_error = self.resolve_task_ids_from_text(
                text=text,
                scope=scope,
                explicit_ids=task_ids,
                target_status="open",
                action_label="삭제할",
                example="`할 일 3 삭제해줘`",
            )
            if resolution_error:
                return resolution_error
            deleted = self.tasks.delete(scope=scope, task_ids=task_ids)
            if deleted == 0:
                return "삭제할 할 일을 찾지 못했어요. `할 일 목록 보여줘`로 ID를 확인해 주세요."
            return f"할 일 {deleted}개를 삭제했어요."

        if asks_to_create_task_from_recent_message(text):
            return self.create_task_from_recent_message(text=text, scope=scope, message_id=message_id)

        title, due_at = extract_task_creation(text, timezone_name=self.config.timezone)
        if not title:
            return "추가할 할 일을 잘 모르겠어요. 예: `할 일 추가: 금요일까지 제안서 초안 작성`"
        priority = extract_task_priority(text) or "normal"
        duplicate = self.tasks.find_open_duplicate(scope=scope, title=title)
        if duplicate is not None:
            due_text = f" · 기한: {duplicate.due_at}" if duplicate.due_at else ""
            priority_text = f" · 우선순위: {format_task_priority(duplicate.priority)}"
            return (
                f"이미 같은 열린 할 일이 있어요. 기존 할 일 ID는 `{duplicate.id}`입니다."
                f"{priority_text}{due_text}"
            )
        task_id = self.tasks.add(
            scope=scope,
            title=title,
            priority=priority,
            due_at=due_at,
            source_message_id=message_id,
        )
        due_text = f" · 기한: {due_at}" if due_at else ""
        priority_text = f" · 우선순위: {format_task_priority(priority)}"
        return f"할 일 `{task_id}`로 추가했어요.{priority_text}{due_text}"

    def list_tasks(self, *, text: str, scope: ConversationScope) -> str:
        status = extract_task_list_status(text)
        stats = self.tasks.stats(scope=scope)
        items = self.tasks.list_recent(user_id=scope.user_id, status=status, limit=10)
        if not items:
            empty_labels = {
                "open": "열린 할 일이 없어요.",
                "completed": "완료한 할 일이 없어요.",
                "all": "표시할 할 일이 없어요.",
            }
            return empty_labels[status]
        heading_labels = {
            "open": f"열린 할 일 {stats['open']}개:",
            "completed": f"완료한 할 일 {stats['completed']}개:",
            "all": f"할 일 전체 {len(items)}개:",
        }
        lines = [heading_labels[status]]
        for item in items:
            due_text = f" · 기한: {item.due_at}" if item.due_at else ""
            completed_text = f" · 완료: {item.completed_at}" if item.completed_at else ""
            priority_text = f" · 우선순위: {format_task_priority(item.priority)}"
            lines.append(
                f"- 할 일 `{item.id}` · {item.title} · 상태: {item.status}{priority_text}{due_text}{completed_text} · "
                f"저장 위치: {item.source_location}"
            )
        if status == "completed":
            lines.append("다시 열려면 `할 일 3 다시 열어줘`라고 말해 주세요.")
        else:
            lines.append(
                "완료하면 `할 일 3 완료했어`, 미루려면 `할 일 3 내일 다시 알려줘`, "
                "지우려면 `할 일 3 삭제해줘`라고 말해 주세요."
            )
        return "\n".join(lines)

    def complete_task_batch(self, *, text: str, scope: ConversationScope) -> str:
        if has_task_due_filter_marker(text):
            due_filter = extract_task_due_filter(text, self.config.timezone)
            if due_filter["undated"]:
                items = self.tasks.list_recent(user_id=scope.user_id, status="open", undated=True, limit=1000)
            else:
                items = self.tasks.list_recent(
                    user_id=scope.user_id,
                    status="open",
                    due_after=due_filter["due_after"],
                    due_before=due_filter["due_before"],
                    limit=1000,
                )
            label = str(due_filter["heading"])
        else:
            items = self.tasks.list_recent(user_id=scope.user_id, status="open", limit=1000)
            label = "열린 할 일"

        if not items:
            return f"완료 처리할 {label}이 없어요."

        completed = self.tasks.complete(scope=scope, task_ids=[item.id for item in items])
        lines = [f"{label} {completed}개를 완료 처리했어요."]
        for item in items[:5]:
            due_text = f" · 기한: {item.due_at}" if item.due_at else ""
            lines.append(f"- 할 일 `{item.id}` · {item.title}{due_text}")
        if len(items) > 5:
            lines.append(f"...외 {len(items) - 5}개")
        lines.append("실수라면 `할 일 3 다시 열어줘`처럼 되돌릴 수 있어요.")
        return "\n".join(lines)

    def resolve_task_ids_from_text(
        self,
        *,
        text: str,
        scope: ConversationScope,
        explicit_ids: list[int],
        target_status: str,
        action_label: str,
        example: str,
    ) -> tuple[list[int], str | None]:
        if explicit_ids:
            return explicit_ids, None
        query = extract_task_action_query(text)
        if not query:
            return [], f"{action_label} 할 일 ID를 알려주세요. 예: {example}"
        candidates = [
            item for item in self.tasks.search(scope=scope, keyword=query, limit=6) if item.status == target_status
        ]
        if not candidates:
            return [], f"`{query}`로 {action_label} 할 일을 찾지 못했어요. `할 일 목록 보여줘`로 ID를 확인해 주세요."
        if len(candidates) == 1:
            return [candidates[0].id], None
        lines = [f"`{query}`와 관련된 할 일이 여러 개 있어요. {action_label} 항목의 ID를 알려주세요:"]
        for item in candidates[:5]:
            due_text = f" · 기한: {item.due_at}" if item.due_at else ""
            lines.append(f"- 할 일 `{item.id}` · {item.title} · 상태: {item.status}{due_text}")
        return [], "\n".join(lines)

    def list_deleted_tasks(self, *, scope: ConversationScope) -> str:
        items = self.tasks.list_deleted(scope=scope, limit=10)
        if not items:
            return "삭제한 할 일이 없어요."
        lines = [f"삭제한 할 일 {len(items)}개:"]
        for item in items:
            due_text = f" · 기한: {item.due_at}" if item.due_at else ""
            deleted_text = f" · 삭제: {item.deleted_at}" if item.deleted_at else ""
            lines.append(
                f"- 할 일 `{item.id}` · {item.title} · 상태: {item.status} · "
                f"우선순위: {format_task_priority(item.priority)}{due_text}{deleted_text} · "
                f"저장 위치: {item.source_location}"
            )
        lines.append("복구하려면 `할 일 3 복구해줘`라고 말해 주세요.")
        return "\n".join(lines)

    def search_tasks(self, *, text: str, scope: ConversationScope) -> str:
        query = extract_task_search_query(text)
        if not query:
            return "찾을 할 일 키워드를 알려주세요. 예: `제안서 할 일 찾아줘`"
        items = self.tasks.search(scope=scope, keyword=query, limit=10)
        if not items:
            return f"`{query}`와 관련된 할 일을 찾지 못했어요."
        lines = [f"`{query}` 할 일 검색 결과 {len(items)}개:"]
        for item in items:
            due_text = f" · 기한: {item.due_at}" if item.due_at else ""
            completed_text = f" · 완료: {item.completed_at}" if item.completed_at else ""
            lines.append(
                f"- 할 일 `{item.id}` · {item.title} · 상태: {item.status} · "
                f"우선순위: {format_task_priority(item.priority)}{due_text}{completed_text} · "
                f"저장 위치: {item.source_location}"
            )
        return "\n".join(lines)

    def show_task_detail(self, *, text: str, scope: ConversationScope) -> str:
        if asks_to_show_latest_task_detail(text):
            item = self.tasks.latest(scope=scope)
            if item is None:
                return "아직 저장된 할 일이 없어요. `할 일 추가: ...`처럼 말하면 저장할 수 있습니다."
            return format_task_detail(item)

        task_ids = extract_task_ids(text)
        if not task_ids:
            return "확인할 할 일 ID를 알려주세요. 예: `할 일 3 보여줘`"
        lines: list[str] = []
        missing: list[int] = []
        for task_id in task_ids[:5]:
            item = self.tasks.get(scope=scope, task_id=task_id)
            if item is None:
                missing.append(task_id)
                continue
            lines.append(format_task_detail(item))
        if missing:
            lines.append(f"찾지 못한 할 일 ID: {', '.join(str(task_id) for task_id in missing)}")
        return "\n\n".join(lines) if lines else "해당 할 일을 찾지 못했어요."

    def list_due_tasks(self, *, text: str, scope: ConversationScope) -> str:
        due_filter = extract_task_due_filter(text, self.config.timezone)
        if due_filter["undated"]:
            items = self.tasks.list_recent(user_id=scope.user_id, status="open", undated=True, limit=10)
        else:
            items = self.tasks.list_recent(
                user_id=scope.user_id,
                status="open",
                due_after=due_filter["due_after"],
                due_before=due_filter["due_before"],
                limit=10,
            )
        if not items:
            return f"{due_filter['empty_label']} 열린 할 일이 없어요."
        lines = [f"{due_filter['heading']} {len(items)}개:"]
        for item in items:
            due_label = "기한 없음" if item.due_at is None else f"{item.due_at}까지"
            lines.append(
                f"- 할 일 `{item.id}` · {item.title} · 우선순위: {format_task_priority(item.priority)} · "
                f"{due_label} · 저장 위치: {item.source_location}"
            )
        lines.append("완료하면 `할 일 3 완료했어`, 미루려면 `할 일 3 내일 다시 알려줘`라고 말해 주세요.")
        return "\n".join(lines)

    def extract_tasks_from_conversation(
        self,
        *,
        text: str,
        scope: ConversationScope,
        message_id: str | None = None,
    ) -> str:
        recent = self.conversations.recent_messages(scope.conversation_id, limit=40)
        candidates = extract_task_candidates_from_messages(recent)
        if not candidates:
            return "최근 대화에서 바로 할 일로 볼 만한 문장을 찾지 못했어요."

        if asks_to_save_extracted_tasks(text):
            saved: list[str] = []
            skipped: list[str] = []
            for title, due_at in candidates[:10]:
                duplicate = self.tasks.find_open_duplicate(scope=scope, title=title)
                if duplicate is not None:
                    skipped.append(f"`{duplicate.id}` · {duplicate.title}")
                    continue
                priority = extract_task_priority(title) or "normal"
                task_id = self.tasks.add(
                    scope=scope,
                    title=title,
                    priority=priority,
                    due_at=due_at,
                    source_message_id=message_id,
                )
                due_text = f" · 기한: {due_at}" if due_at else ""
                saved.append(f"`{task_id}` · {title} · 우선순위: {format_task_priority(priority)}{due_text}")
            lines: list[str] = []
            if saved:
                lines.append(f"최근 대화에서 할 일 {len(saved)}개를 추가했어요:")
                lines.extend(f"- {item}" for item in saved)
            if skipped:
                lines.append("이미 열린 할 일로 있어서 건너뛴 항목:")
                lines.extend(f"- {item}" for item in skipped)
            return "\n".join(lines) if lines else "추가할 새 할 일이 없어요."

        lines = [f"최근 대화에서 할 일 후보 {len(candidates[:10])}개를 찾았어요:"]
        for index, (title, due_at) in enumerate(candidates[:10], start=1):
            due_text = f" · 기한: {due_at}" if due_at else ""
            priority = extract_task_priority(title) or "normal"
            lines.append(f"{index}. {title} · 우선순위: {format_task_priority(priority)}{due_text}")
        lines.append("저장하려면 `최근 대화에서 할 일 뽑아서 추가해줘`라고 말해 주세요.")
        return "\n".join(lines)

    def create_task_from_recent_message(
        self,
        *,
        text: str,
        scope: ConversationScope,
        message_id: str | None = None,
    ) -> str:
        latest = self.conversations.latest_user_message(conversation_id=scope.conversation_id, user_id=scope.user_id)
        if latest is None:
            return "바로 전에 말한 내용을 찾지 못했어요. `할 일 추가: ...`처럼 제목을 알려주세요."

        previous_text = str(latest["content"]).strip()
        if not previous_text:
            return "바로 전에 말한 내용이 비어 있어서 할 일로 만들 수 없어요."

        title, due_at = extract_task_creation(previous_text, timezone_name=self.config.timezone)
        title = normalize_context_task_title(title or previous_text)
        if not title:
            return "바로 전에 말한 내용에서 할 일 제목을 만들기 어려워요. `할 일 추가: ...`처럼 알려주세요."

        priority = extract_task_priority(text) or extract_task_priority(previous_text) or "normal"
        duplicate = self.tasks.find_open_duplicate(scope=scope, title=title)
        if duplicate is not None:
            due_text = f" · 기한: {duplicate.due_at}" if duplicate.due_at else ""
            return f"이미 같은 열린 할 일이 있어요. 기존 할 일 ID는 `{duplicate.id}`입니다.{due_text}"

        task_id = self.tasks.add(
            scope=scope,
            title=title,
            priority=priority,
            due_at=due_at,
            source_message_id=message_id,
        )
        due_text = f" · 기한: {due_at}" if due_at else ""
        return f"바로 전에 말한 내용을 할 일 `{task_id}`로 추가했어요. · {title}{due_text}"


class ConversationAgent:
    def __init__(
        self,
        *,
        config: Config,
        openai: OpenAIService,
        conversations: ConversationStore,
        memories: MemoryStore,
        logs: AgentLogStore,
    ) -> None:
        self.config = config
        self.openai = openai
        self.conversations = conversations
        self.memories = memories
        self.logs = logs

    async def chat(
        self,
        *,
        text: str,
        scope: ConversationScope,
        author_name: str,
        location_label: str,
    ) -> str:
        recent = self.conversations.recent_messages(scope.conversation_id)
        summary = self.conversations.latest_summary(scope.conversation_id)
        related_memories = await self.memories.search(
            scope=scope,
            query=text,
            limit=min(4, self.config.retrieval_limit),
        )
        useful_memories = [result for result in related_memories if result.score >= 0.24]
        memory_context = format_memory_context(useful_memories)
        conversation_context = format_conversation_context(recent)
        context = "\n\n".join(
            part
            for part in [
                f"이전 요약:\n{summary}" if summary else "",
                f"최근 대화:\n{conversation_context}" if conversation_context else "",
                f"관련 장기 기억:\n{memory_context}" if memory_context else "",
            ]
            if part
        )
        choice = choose_model(
            self.config,
            text,
            context_chars=len(context),
            result_count=len(useful_memories),
        )
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="conversation",
            intent="chat",
            difficulty=choice.difficulty,
            model=choice.model,
            reason=choice.reason,
        )

        instructions = """
너는 Discord에서 대화하는 개인 비서다.
말투는 자연스럽고 간결하게 유지한다.
사용자가 명시적으로 기억해달라고 하지 않은 정보는 장기 기억으로 저장했다고 말하지 않는다.
저장된 기억을 사용할 때는 자연스럽게 반영하되, 확실하지 않은 내용은 단정하지 않는다.
"""
        answer = await self.openai.text_response(
            model=choice.model,
            instructions=instructions,
            input_text=(
                f"사용자 이름: {author_name}\n\n"
                f"현재 대화 위치: {location_label}\n"
                "저장된 기억은 같은 사용자 기준으로 DM과 서버 어디서든 이어진다. "
                "다만 답변할 때는 현재 대화 위치가 바뀌었음을 고려한다.\n\n"
                f"컨텍스트:\n{context}\n\n"
                f"사용자 메시지:\n{text}"
            ),
            temperature=0.4,
        )

        recent_chars = self.conversations.recent_char_count(scope.conversation_id)
        if recent_chars >= self.config.context_compression_chars:
            await self.compress_context(scope.conversation_id)

        return answer

    async def compress_context(self, conversation_id: str) -> None:
        recent = self.conversations.recent_messages(conversation_id, limit=80)
        context = format_conversation_context(recent)
        if not context:
            return
        summary = await self.openai.text_response(
            model=self.config.easy_model,
            instructions="대화의 핵심 맥락, 사용자 선호, 미해결 작업만 짧게 한글로 요약한다.",
            input_text=context,
            temperature=0.1,
        )
        self.conversations.add_summary(conversation_id, summary)


def heuristic_route(text: str, has_attachments: bool) -> RoutingResult:
    normalized = text.strip().lower()
    help_markers = ["도움말", "사용법", "뭘 할 수", "무엇을 할 수", "help", "how to use"]
    status_markers = ["상태", "정상", "status", "health", "설정", "모델 뭐", "어떤 모델"]
    cancel_markers = ["취소", "저장하지마", "저장하지 마", "기억하지마", "기억하지 마", "cancel", "never mind"]
    reset_context_markers = [
        "대화 맥락 초기화",
        "대화맥락초기화",
        "대화 초기화",
        "맥락 초기화",
        "컨텍스트 초기화",
        "대화 기록 초기화",
        "reset context",
        "clear context",
    ]
    remember_markers = ["기억해", "저장해", "기억해줘", "저장해줘", "remember", "save this"]
    update_markers = ["수정해", "고쳐", "바꿔", "업데이트", "update", "change"]
    delete_markers = ["삭제해", "지워", "잊어", "forget", "delete"]
    restore_markers = ["복구", "되돌려", "되살려", "restore", "undo delete"]
    list_markers = ["목록", "리스트", "뭘 기억", "무엇을 기억", "기억 상태", "저장 상태", "list memories"]
    recall_markers = ["기억", "저장한", "전에", "문서", "파일", "회의록", "recall"]

    if asks_for_daily_briefing(text):
        return RoutingResult("daily_briefing", 0.96, "오늘 브리핑 요청 감지")
    if is_task_request(text):
        return RoutingResult("manage_task", 0.95, "할 일 관리 요청 감지")
    if any(marker in normalized for marker in help_markers):
        return RoutingResult("help", 0.96, "도움말 요청 감지")
    if any(marker in normalized for marker in status_markers):
        return RoutingResult("status", 0.94, "상태 조회 요청 감지")
    if any(marker in normalized for marker in cancel_markers):
        return RoutingResult("cancel_pending", 0.95, "대기 작업 취소 의도 감지")
    if any(marker in normalized for marker in reset_context_markers):
        return RoutingResult("reset_context", 0.95, "현재 대화 맥락 초기화 요청 감지")
    if any(marker in normalized for marker in update_markers):
        return RoutingResult("update_memory", 0.95, "기억 수정 의도 표현 감지")
    if asks_to_list_deleted_memories(text):
        return RoutingResult("restore_memory", 0.95, "삭제 기억 목록 조회 의도 감지")
    if any(marker in normalized for marker in restore_markers):
        return RoutingResult("restore_memory", 0.95, "삭제 기억 복구 의도 표현 감지")
    if any(marker in normalized for marker in delete_markers):
        return RoutingResult("delete_memory", 0.95, "삭제 의도 표현 감지")
    if any(marker in normalized for marker in remember_markers):
        return RoutingResult("remember", 0.96, "명시적 기억 요청 감지")
    if asks_to_show_latest_memory(text):
        return RoutingResult("recall", 0.95, "최근 저장 기억 상세 조회 요청 감지")
    if asks_to_search_memories(text):
        return RoutingResult("list_memory", 0.95, "저장 기억 검색 요청 감지")
    if any(marker in normalized for marker in list_markers):
        return RoutingResult("list_memory", 0.95, "기억 목록 조회 의도 감지")
    if has_attachments and not normalized:
        return RoutingResult("chat", 0.95, "첨부만 있어 저장 확인 필요")
    if any(marker in normalized for marker in recall_markers):
        return RoutingResult("recall", 0.78, "저장 정보 회상 가능성 감지")
    return RoutingResult("chat", 0.7, "일반 대화로 판단")


def parse_routing_result(output: str) -> RoutingResult:
    try:
        match = re.search(r"\{.*\}", output, flags=re.DOTALL)
        data = json.loads(match.group(0) if match else output)
        intent = data.get("intent", "chat")
        if intent not in {
            "chat",
            "help",
            "status",
            "cancel_pending",
            "remember",
            "recall",
            "list_memory",
            "update_memory",
            "delete_memory",
            "restore_memory",
            "reset_context",
            "manage_task",
            "daily_briefing",
            "unsupported",
        }:
            intent = "chat"
        return RoutingResult(
            intent=intent,
            confidence=float(data.get("confidence", 0.5)),
            reason=str(data.get("reason", "라우터 응답")),
        )
    except Exception:
        return RoutingResult("chat", 0.3, "라우터 JSON 파싱 실패")


def extract_memory_text(text: str) -> str:
    cleaned = re.sub(
        r"(이거|이 내용|내용|메모)?\s*(기억해줘|기억해|저장해줘|저장해|remember|save this)[:：]?",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    return cleaned or text.strip()


def asks_to_remember_recent_message(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    pronoun_pattern = (
        r"^\s*(?:그거|그것|이거|이것|that|it)\s*(?:도|을|를)?\s*"
        r"(?:기억해줘|기억해|저장해줘|저장해|remember|save)\s*\.?\s*$"
    )
    if re.search(pronoun_pattern, normalized, flags=re.IGNORECASE):
        return True
    recent_markers = ["방금", "직전", "위에", "아까", "latest", "last", "previous"]
    content_markers = ["말한", "얘기한", "내용", "메시지", "대화", "that", "it"]
    remember_markers = ["기억", "저장", "remember", "save"]
    return (
        any(marker in normalized or marker in compact for marker in recent_markers)
        and any(marker in normalized or marker in compact for marker in content_markers)
        and any(marker in normalized or marker in compact for marker in remember_markers)
    )


def asks_to_show_latest_memory(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    latest_markers = ["방금", "최근", "마지막", "직전", "latest", "last"]
    memory_markers = ["저장", "기억", "메모", "문서", "파일", "memory", "document", "doc"]
    show_markers = ["보여", "확인", "뭐", "무엇", "알려", "show", "what"]
    return (
        any(marker in normalized or marker in compact for marker in latest_markers)
        and any(marker in normalized or marker in compact for marker in memory_markers)
        and any(marker in normalized or marker in compact for marker in show_markers)
    )


def has_substantive_memory_text(text: str) -> bool:
    if asks_to_remember_recent_message(text):
        return False
    cleaned = extract_memory_text(text)
    instruction_words = [
        "이 파일",
        "파일",
        "첨부",
        "문서",
        "내용",
        "this file",
        "attachment",
        "document",
    ]
    normalized = cleaned.strip().lower()
    return bool(normalized) and normalized not in instruction_words and len(normalized) >= 4


def extract_delete_query(text: str) -> str:
    cleaned = re.sub(
        r"(기억|메모|문서|파일)?\s*(삭제해줘|삭제해|지워줘|지워|잊어줘|잊어|forget|delete)[:：]?",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    return cleaned or text.strip()


def asks_to_delete_all_memories(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text.casefold())
    delete_markers = ["삭제", "지워", "잊어", "forget", "delete"]
    all_markers = ["전부", "전체", "모두", "다", "모든", "all"]
    memory_markers = ["기억", "메모", "문서", "파일", "memory", "memories", "document"]
    return (
        any(marker in normalized for marker in delete_markers)
        and any(marker in normalized for marker in all_markers)
        and any(marker in normalized for marker in memory_markers)
    )


def asks_to_delete_latest_memory(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text.casefold())
    latest_markers = ["방금", "최근", "마지막", "직전", "latest", "last"]
    delete_markers = ["삭제", "지워", "잊어", "forget", "delete", "remove"]
    return any(marker in normalized for marker in latest_markers) and any(
        marker in normalized for marker in delete_markers
    )


def asks_to_update_latest_memory(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    latest_markers = ["방금", "최근", "마지막", "직전", "latest", "last"]
    memory_markers = ["저장", "기억", "메모", "memory"]
    update_markers = ["수정", "고쳐", "바꿔", "변경", "업데이트", "update", "change"]
    return (
        any(marker in normalized or marker in compact for marker in latest_markers)
        and any(marker in normalized or marker in compact for marker in memory_markers)
        and any(marker in normalized or marker in compact for marker in update_markers)
    )


def asks_to_list_deleted_memories(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text.casefold())
    deleted_markers = ["삭제한", "지운", "잊은", "deleted", "trash"]
    list_markers = ["목록", "리스트", "보여", "뭐", "무엇", "list", "show"]
    return any(marker in normalized for marker in deleted_markers) and any(
        marker in normalized for marker in list_markers
    )


def asks_to_search_memories(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    memory_markers = ["기억", "메모", "문서", "파일", "memory", "memories", "document", "doc"]
    search_markers = ["검색", "찾아", "찾아줘", "관련", "search", "find"]
    return any(marker in normalized or marker in compact for marker in memory_markers) and any(
        marker in normalized or marker in compact for marker in search_markers
    )


def extract_memory_search_query(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(
        r"(?:기억|메모|문서|파일|memory|memories|document|doc)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:관련|검색해줘|검색해|검색|찾아줘|찾아|보여줘|보여|알려줘|알려|search|find|show)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" :：,，")
    return cleaned


def extract_delete_ids(text: str) -> tuple[list[int], list[int]]:
    memory_ids = [int(match) for match in re.findall(r"(?:메모|기억|memory)\s*#?(\d+)", text, re.I)]
    document_ids = [int(match) for match in re.findall(r"(?:문서|파일|document|doc)\s*#?(\d+)", text, re.I)]
    return memory_ids, document_ids


def extract_restore_ids(text: str) -> tuple[list[int], list[int]]:
    memory_ids = [int(match) for match in re.findall(r"(?:메모|기억|memory)\s*#?(\d+)", text, re.I)]
    document_ids = [int(match) for match in re.findall(r"(?:문서|파일|document|doc)\s*#?(\d+)", text, re.I)]
    return memory_ids, document_ids


def extract_update_ids(text: str) -> tuple[list[int], list[int]]:
    memory_ids = [int(match) for match in re.findall(r"(?:메모|기억|memory)\s*#?(\d+)", text, re.I)]
    document_ids = [int(match) for match in re.findall(r"(?:문서|파일|document|doc)\s*#?(\d+)", text, re.I)]
    return memory_ids, document_ids


def extract_update_text(text: str) -> str:
    patterns = [
        r"(?:메모|기억|memory)\s*#?\d+\s*(?:을|를)?\s*(?P<value>.+?)\s*(?:로|으로)\s*(?:수정해줘|수정해|바꿔줘|바꿔|고쳐줘|고쳐|업데이트해줘|업데이트해|update|change)\.?$",
        r"(?:방금|최근|마지막|직전).+?(?:저장한\s*)?(?:메모|기억|memory)\s*(?:을|를)?\s*(?P<value>.+?)\s*(?:로|으로)\s*(?:수정해줘|수정해|바꿔줘|바꿔|고쳐줘|고쳐|변경해줘|변경해|업데이트해줘|업데이트해|update|change)\.?$",
        r".+?(?:을|를)\s*(?P<value>.+?)\s*(?:로|으로)\s*(?:수정해줘|수정해|바꿔줘|바꿔|고쳐줘|고쳐|업데이트해줘|업데이트해)\.?$",
        r"(?:수정|변경|업데이트)\s*(?:내용)?\s*[:：]\s*(?P<value>.+)$",
        r"(?:to|as)\s+['\"]?(?P<value>.+?)['\"]?\s*(?:update|change)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.strip(), flags=re.IGNORECASE)
        if match:
            return match.group("value").strip(" '\"")
    return ""


def extract_update_query(text: str) -> str:
    cleaned = re.sub(
        r"(?:수정해줘|수정해|바꿔줘|바꿔|고쳐줘|고쳐|업데이트해줘|업데이트해|update|change)",
        "",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(?:로|으로)\s*$", "", cleaned.strip())
    replacement = extract_update_text(text)
    if replacement:
        cleaned = cleaned.replace(replacement, "")
    return cleaned.strip()


def extract_recall_ids(text: str) -> tuple[list[int], list[int]]:
    if any(marker in text.lower() for marker in ["삭제", "지워", "delete", "forget"]):
        return [], []
    memory_ids = [int(match) for match in re.findall(r"(?:메모|기억|memory)\s*#?(\d+)", text, re.I)]
    document_ids = [int(match) for match in re.findall(r"(?:문서|파일|document|doc)\s*#?(\d+)", text, re.I)]
    return memory_ids, document_ids


def is_task_request(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    task_markers = ["할 일", "할일", "태스크", "task", "todo", "to-do", "체크리스트"]
    reminder_markers = ["리마인드", "remind", "나중에 알려", "다시 알려", "챙겨"]
    if any(marker in normalized for marker in task_markers) or any(marker in compact for marker in ["할일"]):
        return True
    if asks_to_create_reminder(text):
        return True
    return any(marker in normalized for marker in reminder_markers)


def asks_to_create_reminder(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    notify_markers = ["알려줘", "알려 줘", "말해줘", "말해 줘", "챙겨줘", "챙겨 줘", "remind me"]
    return extract_due_at(text) is not None and any(
        marker in normalized or marker in compact for marker in notify_markers
    )


def asks_for_daily_briefing(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    briefing_markers = ["브리핑", "요약", "briefing", "brief", "daily"]
    today_markers = ["오늘", "일일", "daily", "today"]
    return any(marker in normalized or marker in compact for marker in briefing_markers) and any(
        marker in normalized or marker in compact for marker in today_markers
    )


def asks_to_list_tasks(text: str) -> bool:
    normalized = text.casefold()
    list_markers = ["목록", "리스트", "보여", "뭐", "무엇", "남은", "조회", "list", "show"]
    return is_task_request(text) and any(marker in normalized for marker in list_markers)


def extract_task_list_status(text: str) -> str:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    completed_markers = ["완료한", "완료된", "끝낸", "처리한", "completed", "done", "finished"]
    all_markers = ["전체", "모든", "전부", "all"]
    open_markers = ["열린", "남은", "미완료", "open", "remaining"]
    if any(marker in normalized or marker in compact for marker in completed_markers):
        return "completed"
    if any(marker in normalized or marker in compact for marker in all_markers):
        return "all"
    if any(marker in normalized or marker in compact for marker in open_markers):
        return "open"
    return "open"


def asks_to_search_tasks(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    search_markers = ["검색", "찾아", "찾아줘", "관련", "search", "find"]
    return is_task_request(text) and any(marker in normalized or marker in compact for marker in search_markers)


def asks_to_show_task_detail(text: str) -> bool:
    normalized = text.casefold()
    detail_markers = ["상세", "자세", "보여", "확인", "정보", "detail", "show"]
    return is_task_request(text) and (
        asks_to_show_latest_task_detail(text)
        or (bool(extract_task_ids(text)) and any(marker in normalized for marker in detail_markers))
    )


def asks_to_show_latest_task_detail(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    show_markers = ["보여", "확인", "뭐", "무엇", "show", "what"]
    return (
        asks_to_reference_latest_added_task(text)
        and not asks_to_postpone_task(text)
        and not asks_to_delete_task(text)
        and any(marker in normalized or marker in compact for marker in show_markers)
    )


def asks_to_list_deleted_tasks(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    deleted_markers = ["삭제한", "삭제된", "지운", "deleted", "trash"]
    list_markers = ["목록", "리스트", "보여", "뭐", "무엇", "조회", "list", "show"]
    return is_task_request(text) and any(
        marker in normalized or marker in compact for marker in deleted_markers
    ) and any(marker in normalized or marker in compact for marker in list_markers)


def asks_to_list_due_tasks(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    if asks_to_create_reminder(text):
        return False
    if any(marker in normalized or marker in compact for marker in ["추가", "등록", "만들어", "add", "create"]):
        return False
    postpone_markers = ["미뤄", "미루", "연기", "다시 알려", "나중에 알려", "snooze", "postpone", "remind later"]
    if any(marker in normalized or marker in compact for marker in postpone_markers):
        return False
    list_markers = ["뭐", "무엇", "목록", "리스트", "보여", "조회", "알려", "list", "show"]
    due_markers = [
        "오늘",
        "내일",
        "이번 주",
        "이번주",
        "기한",
        "마감",
        "급한",
        "늦은",
        "지난",
        "없는",
        "overdue",
        "due",
        "today",
        "tomorrow",
        "week",
        "undated",
    ]
    return (
        is_task_request(text)
        and any(marker in normalized or marker in compact for marker in due_markers)
        and any(marker in normalized or marker in compact for marker in list_markers)
    )


def asks_to_extract_tasks(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    extraction_action_markers = ["뽑아", "추출", "extract"]
    conversation_markers = ["최근 대화", "최근대화", "대화에서", "from conversation"]
    return is_task_request(text) and (
        any(marker in normalized or marker in compact for marker in extraction_action_markers)
        or any(marker in normalized or marker in compact for marker in conversation_markers)
    )


def extract_task_due_filter(text: str, timezone_name: str | None) -> dict[str, str | bool | None]:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    now = now_in_timezone(timezone_name)
    today = now.strftime("%Y-%m-%d")

    if any(marker in normalized or marker in compact for marker in ["기한 없는", "마감 없는", "undated", "no due"]):
        return {
            "heading": "기한 없는 할 일",
            "empty_label": "기한 없는",
            "due_after": None,
            "due_before": None,
            "undated": True,
        }

    if any(marker in normalized or marker in compact for marker in ["늦은", "지난", "overdue"]):
        yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        return {
            "heading": "기한이 지난 할 일",
            "empty_label": "기한이 지난",
            "due_after": None,
            "due_before": yesterday,
            "undated": False,
        }

    if any(marker in normalized or marker in compact for marker in ["내일", "tomorrow"]):
        tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        return {
            "heading": "내일 처리할 할 일",
            "empty_label": "내일 처리할",
            "due_after": tomorrow,
            "due_before": tomorrow,
            "undated": False,
        }

    if any(marker in normalized or marker in compact for marker in ["이번 주", "이번주", "this week", "week"]):
        days_until_sunday = 6 - now.weekday()
        sunday = (now + timedelta(days=days_until_sunday)).strftime("%Y-%m-%d")
        return {
            "heading": "이번 주 처리할 할 일",
            "empty_label": "이번 주 처리할",
            "due_after": today,
            "due_before": sunday,
            "undated": False,
        }

    return {
        "heading": "오늘까지 처리할 할 일",
        "empty_label": "오늘까지 처리해야 하는",
        "due_after": None,
        "due_before": today,
        "undated": False,
    }


def asks_to_save_extracted_tasks(text: str) -> bool:
    normalized = text.casefold()
    save_markers = ["추가", "등록", "저장", "만들어", "add", "save", "create"]
    return any(marker in normalized for marker in save_markers)


def asks_to_complete_task(text: str) -> bool:
    normalized = text.casefold()
    complete_markers = [
        "완료",
        "끝냈",
        "끝났",
        "처리했",
        "끝남",
        "다 했",
        "다했",
        "done",
        "finish",
        "finished",
        "complete",
    ]
    return is_task_request(text) and any(marker in normalized for marker in complete_markers)


def asks_to_complete_task_batch(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    batch_markers = ["다", "모두", "전체", "전부", "모든", "all"]
    return asks_to_complete_task(text) and any(marker in normalized or marker in compact for marker in batch_markers)


def has_task_due_filter_marker(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    due_markers = [
        "오늘",
        "내일",
        "이번 주",
        "이번주",
        "기한 없는",
        "마감 없는",
        "늦은",
        "지난",
        "overdue",
        "today",
        "tomorrow",
        "week",
        "undated",
    ]
    return any(marker in normalized or marker in compact for marker in due_markers)


def asks_to_reopen_task(text: str) -> bool:
    normalized = text.casefold()
    reopen_markers = ["다시 열", "완료 취소", "되돌려", "미완료", "reopen", "undo complete"]
    return is_task_request(text) and any(marker in normalized for marker in reopen_markers)


def asks_to_reopen_latest_completed_task(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    latest_markers = ["방금", "최근", "마지막", "직전", "latest", "last"]
    completed_markers = ["완료", "끝낸", "끝낸거", "끝낸 것", "done", "completed"]
    return asks_to_reopen_task(text) and any(
        marker in normalized or marker in compact for marker in latest_markers
    ) and any(marker in normalized or marker in compact for marker in completed_markers)


def asks_to_restore_task(text: str) -> bool:
    normalized = text.casefold()
    restore_markers = ["복구", "삭제 취소", "지운 거 취소", "restore", "undo delete"]
    return is_task_request(text) and any(marker in normalized for marker in restore_markers)


def asks_to_postpone_task(text: str) -> bool:
    normalized = text.casefold()
    postpone_markers = ["미뤄", "미루", "연기", "다시 알려", "나중에 알려", "snooze", "postpone", "remind later"]
    return is_task_request(text) and any(marker in normalized for marker in postpone_markers)


def asks_to_snooze_latest_reminded_task(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    snooze_markers = ["다시 알려", "나중에 알려", "snooze", "remind later"]
    id_markers = extract_task_ids(text)
    return (
        asks_to_postpone_task(text)
        and not id_markers
        and not asks_to_reference_latest_added_task(text)
        and not extract_task_action_query(text)
        and any(marker in normalized or marker in compact for marker in snooze_markers)
    )


def asks_to_clear_task_due(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    due_markers = ["기한", "마감", "리마인더", "리마인드", "due", "deadline", "reminder"]
    clear_markers = ["없애", "지워", "삭제", "빼", "제거", "취소", "clear", "remove"]
    return is_task_request(text) and any(
        marker in normalized or marker in compact for marker in due_markers
    ) and any(marker in normalized or marker in compact for marker in clear_markers)


def asks_to_rename_task(text: str) -> bool:
    normalized = text.casefold()
    rename_markers = ["수정", "변경", "바꿔", "이름", "제목", "rename", "change"]
    return is_task_request(text) and any(marker in normalized for marker in rename_markers)


def asks_to_set_task_priority(text: str) -> bool:
    normalized = text.casefold()
    priority_markers = ["우선순위", "중요", "긴급", "높음", "낮음", "priority", "important", "urgent"]
    return is_task_request(text) and any(marker in normalized for marker in priority_markers)


def asks_to_delete_task(text: str) -> bool:
    normalized = text.casefold()
    delete_markers = ["삭제", "지워", "취소", "delete", "remove"]
    return is_task_request(text) and any(marker in normalized for marker in delete_markers)


def asks_to_delete_latest_task(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    delete_markers = ["삭제", "지워", "취소", "delete", "remove"]
    return asks_to_reference_latest_added_task(text) and any(
        marker in normalized or marker in compact for marker in delete_markers
    )


def asks_to_reference_latest_added_task(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    latest_markers = ["방금", "최근", "마지막", "직전", "latest", "last"]
    create_markers = ["추가", "등록", "만든", "만들", "저장", "add", "created"]
    return (
        is_task_request(text)
        and any(marker in normalized or marker in compact for marker in latest_markers)
        and any(marker in normalized or marker in compact for marker in create_markers)
    )


def asks_to_create_task_from_recent_message(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    reference_markers = [
        "그거",
        "그것",
        "이거",
        "이것",
        "방금 말한",
        "방금말한",
        "방금 얘기한",
        "방금얘기한",
        "직전에 말한",
        "직전말한",
        "위 내용",
        "위내용",
        "this",
        "that",
    ]
    create_markers = ["추가", "등록", "만들", "저장", "add", "create", "save"]
    return is_task_request(text) and any(
        marker in normalized or marker in compact for marker in reference_markers
    ) and any(marker in normalized or marker in compact for marker in create_markers)


def extract_task_search_query(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(
        r"(?:할\s*일|할일|태스크|task|todo|to-do)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:검색해줘|검색해|검색|찾아줘|찾아|관련|조회해줘|조회해|search|find)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(?:중|에서|관련된|관련한|관련)\s*", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" '\"`.,:：")
    return cleaned


def extract_task_action_query(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"(?:할\s*일|할일|태스크|task|todo|to-do)", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\d{4}-\d{1,2}-\d{1,2}(?:까지|에|까지는)?", " ", cleaned)
    cleaned = re.sub(r"\d{1,2}\s*월\s*\d{1,2}\s*일(?:까지|에|까지는)?", " ", cleaned)
    cleaned = re.sub(r"\d+\s*(?:일|주)\s*(?:뒤|후)(?:까지|에|까지는)?", " ", cleaned)
    cleaned = re.sub(r"\d+\s*(?:분|시간)\s*(?:뒤|후)(?:까지|에|까지는)?", " ", cleaned)
    cleaned = remove_due_time_text(cleaned)
    cleaned = re.sub(r"#?\d+", " ", cleaned)
    cleaned = re.sub(
        r"(?:오늘|내일|모레|이번 주|이번주|다음 주|다음주|"
        r"월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:까지|에|까지는)?",
        " ",
        cleaned,
    )
    cleaned = re.sub(
        r"(?:완료했어|완료해줘|완료|끝냈어|끝냈|처리했어|처리했|끝남|done|finish|finished|complete)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:삭제해줘|삭제해|삭제|지워줘|지워|취소|delete|remove)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:미뤄줘|미뤄|미루|연기|다시 알려줘|다시 알려|나중에 알려줘|나중에 알려|"
        r"snooze|postpone|remind later)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:다시 열어줘|다시 열|완료 취소|되돌려|미완료|reopen|undo complete)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:우선순위\s*)?(?:높음|높게|중요|긴급|보통|낮음|낮게|나중|천천히|"
        r"high|urgent|important|normal|low|priority)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" '\"`.,:：")
    return cleaned


def extract_task_ids(text: str) -> list[int]:
    ids = [
        int(match)
        for match in re.findall(r"(?:할\s*일|태스크|task|todo)\s*#?(\d+)(?!\s*(?:일|주|시|분))", text, re.I)
    ]
    if ids:
        return ids
    if (
        asks_to_complete_task(text)
        or asks_to_reopen_task(text)
        or asks_to_postpone_task(text)
        or asks_to_clear_task_due(text)
        or asks_to_rename_task(text)
        or asks_to_set_task_priority(text)
        or asks_to_restore_task(text)
        or asks_to_delete_task(text)
    ):
        return [int(match) for match in re.findall(r"(?<!\d)#?(\d+)(?!\d|\s*(?:일|주|시|분))", text)]
    return []


def extract_task_rename_title(text: str) -> str:
    patterns = [
        r"(?:할\s*일|태스크|task|todo)\s*#?\d+\s*(?:을|를)?\s*(?P<title>.+?)\s*(?:로|으로)\s*(?:수정해줘|수정해|바꿔줘|바꿔|변경해줘|변경해|rename|change)\.?$",
        r"(?:할\s*일|태스크|task|todo)\s*#?\d+\s*(?:제목|이름)\s*(?:을|를)?\s*(?P<title>.+?)\s*(?:로|으로)?\s*(?:해줘|바꿔줘|변경해줘|수정해줘)?\.?$",
        r"(?:방금|최근|마지막|직전).+?(?:할\s*일|할일|태스크|task|todo).+?(?:을|를)?\s*(?P<title>.+?)\s*(?:로|으로)\s*(?:수정해줘|수정해|바꿔줘|바꿔|변경해줘|변경해|rename|change)\.?$",
        r"(?:방금|최근|마지막|직전).+?(?:할\s*일|할일|태스크|task|todo).+?(?:제목|이름)\s*(?:을|를)?\s*(?P<title>.+?)\s*(?:로|으로)?\s*(?:해줘|바꿔줘|변경해줘|수정해줘)?\.?$",
        r"(?:rename|change)\s+(?:task|todo)\s*#?\d+\s+(?:to|as)\s+(?P<title>.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.strip(), flags=re.IGNORECASE)
        if match:
            return match.group("title").strip(" '\"`.,")
    return ""


def extract_task_priority(text: str) -> str | None:
    normalized = text.casefold()
    if any(marker in normalized for marker in ["긴급", "중요", "높음", "높게", "high", "urgent", "important"]):
        return "high"
    if any(marker in normalized for marker in ["낮음", "낮게", "나중", "천천히", "low"]):
        return "low"
    if any(marker in normalized for marker in ["보통", "normal", "medium"]):
        return "normal"
    return None


def format_task_priority(priority: str) -> str:
    normalized = normalize_task_priority(priority)
    labels = {
        "high": "높음",
        "normal": "보통",
        "low": "낮음",
    }
    return labels[normalized]


def format_task_detail(item: TaskItem) -> str:
    due_text = item.due_at or "-"
    completed_text = item.completed_at or "-"
    reminder_text = item.reminder_sent_at or "-"
    deleted_text = item.deleted_at or "-"
    channel_text = item.channel_id or "-"
    message_text = item.source_message_id or "-"
    return "\n".join(
        [
            f"할 일 `{item.id}` · {item.title}",
            f"- 상태: {item.status}",
            f"- 우선순위: {format_task_priority(item.priority)}",
            f"- 기한: {due_text}",
            f"- 저장 위치: {item.source_location}",
            f"- 대화 ID: {item.conversation_id}",
            f"- 채널 ID: {channel_text}",
            f"- 원본 메시지 ID: {message_text}",
            f"- 생성: {item.created_at}",
            f"- 완료: {completed_text}",
            f"- 리마인드 발송: {reminder_text}",
            f"- 삭제: {deleted_text}",
        ]
    )


def extract_task_creation(
    text: str,
    *,
    timezone_name: str | None = None,
    now: datetime | None = None,
) -> tuple[str, str | None]:
    due_at = extract_due_at(text, timezone_name=timezone_name, now=now)
    cleaned = text.strip()
    cleaned = re.sub(
        r"^(?:할\s*일|할일|태스크|task|todo|to-do)\s*(?:추가|등록|만들어줘|만들어|add|create)?\s*[:：-]?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:을|를)?\s*(?:할\s*일|할일|태스크|task|todo|to-do)(?:로)?\s*(?:추가|등록|만들어줘|만들어|add|create)\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"(?:리마인드|remind|remind me|알려줘|알려 줘|말해줘|말해 줘|챙겨줘|챙겨 줘|챙겨)\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(?:하라고|라고)\s*$", "", cleaned)
    cleaned = re.sub(
        r"(?:우선순위\s*)?(?:높음|높게|중요|긴급|보통|낮음|낮게|나중|천천히|high|urgent|important|normal|low)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\d{4}-\d{1,2}-\d{1,2}(?:까지|에|까지는)?", "", cleaned)
    weekday_pattern = (
        r"(?:오늘|내일|모레|이번 주|이번주|다음 주|다음주|"
        r"월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:까지|에|까지는)?"
    )
    cleaned = re.sub(weekday_pattern, "", cleaned)
    cleaned = re.sub(r"\d{1,2}\s*월\s*\d{1,2}\s*일(?:까지|에|까지는)?", "", cleaned)
    cleaned = re.sub(r"\d+\s*(?:일|주)\s*(?:뒤|후)(?:까지|에|까지는)?", "", cleaned)
    cleaned = re.sub(r"\d+\s*(?:분|시간)\s*(?:뒤|후)(?:까지|에|까지는)?", "", cleaned)
    cleaned = remove_due_time_text(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" :：-.,")
    return cleaned, due_at


def normalize_context_task_title(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(
        r"(?:해야겠다|해야겠어|해야 해|해야함|해야 함|해야돼|해야 돼|해야됨|해야 됨|할게|할 것|할거야)\s*$",
        "",
        cleaned,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" '\"`.,:：-")
    return cleaned


def extract_due_at(text: str, *, timezone_name: str | None = None, now: datetime | None = None) -> str | None:
    relative_due_at = extract_relative_due_at(text, timezone_name=timezone_name, now=now)
    if relative_due_at:
        return relative_due_at
    due_date = extract_due_date(text, timezone_name=timezone_name, now=now)
    due_time = extract_due_time(text)
    if due_date and due_time and len(due_date) == 10:
        return f"{due_date} {due_time}"
    return due_date


def extract_relative_due_at(text: str, *, timezone_name: str | None = None, now: datetime | None = None) -> str | None:
    normalized = text.strip()
    current = now.astimezone(resolve_timezone(timezone_name)) if now else now_in_timezone(timezone_name)
    minute_match = re.search(r"(\d+)\s*분\s*(?:뒤|후)", normalized)
    if minute_match:
        minutes = int(minute_match.group(1))
        return (current + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M")
    hour_match = re.search(r"(\d+)\s*시간\s*(?:뒤|후)", normalized)
    if hour_match:
        hours = int(hour_match.group(1))
        return (current + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")
    return None


def extract_due_date(text: str, *, timezone_name: str | None = None, now: datetime | None = None) -> str | None:
    normalized = text.strip()
    now = now.astimezone(resolve_timezone(timezone_name)) if now else now_in_timezone(timezone_name)
    iso_match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", normalized)
    if iso_match:
        year, month, day = (int(part) for part in iso_match.groups())
        return f"{year:04d}-{month:02d}-{day:02d}"

    month_day_match = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", normalized)
    if month_day_match:
        month, day = (int(part) for part in month_day_match.groups())
        year = now.year
        candidate = datetime(year, month, day, tzinfo=now.tzinfo)
        if candidate.date() < now.date():
            year += 1
        return f"{year:04d}-{month:02d}-{day:02d}"

    compact = re.sub(r"\s+", "", normalized)
    relative_days = {
        "오늘": 0,
        "내일": 1,
        "모레": 2,
    }
    for marker, days in relative_days.items():
        if marker in compact:
            return (now + timedelta(days=days)).strftime("%Y-%m-%d")

    relative_day_match = re.search(r"(\d+)\s*일\s*(?:뒤|후)", normalized)
    if relative_day_match:
        days = int(relative_day_match.group(1))
        return (now + timedelta(days=days)).strftime("%Y-%m-%d")

    relative_week_match = re.search(r"(\d+)\s*주\s*(?:뒤|후)", normalized)
    if relative_week_match:
        weeks = int(relative_week_match.group(1))
        return (now + timedelta(days=weeks * 7)).strftime("%Y-%m-%d")

    weekday_offsets = {
        "월요일": 0,
        "화요일": 1,
        "수요일": 2,
        "목요일": 3,
        "금요일": 4,
        "토요일": 5,
        "일요일": 6,
    }
    for marker, weekday in weekday_offsets.items():
        if f"다음주{marker}" in compact:
            days = 7 - now.weekday() + weekday
            return (now + timedelta(days=days)).strftime("%Y-%m-%d")
        if f"이번주{marker}" in compact:
            days = weekday - now.weekday()
            if days < 0:
                days += 7
            return (now + timedelta(days=days)).strftime("%Y-%m-%d")

    if "다음주" in compact:
        return (now + timedelta(days=7)).strftime("%Y-%m-%d")

    for marker, weekday in weekday_offsets.items():
        if marker in compact:
            days = (weekday - now.weekday()) % 7
            if days == 0:
                days = 7
            return (now + timedelta(days=days)).strftime("%Y-%m-%d")

    due_time = extract_due_time(normalized)
    if due_time:
        hour, minute = (int(part) for part in due_time.split(":"))
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate.strftime("%Y-%m-%d")

    return None


def extract_due_time(text: str) -> str | None:
    normalized = text.strip()
    meridiem_match = re.search(
        r"(오전|오후|아침|저녁|밤)\s*(\d{1,2})\s*시(?:\s*(\d{1,2})\s*분?)?",
        normalized,
    )
    if meridiem_match:
        marker, hour_text, minute_text = meridiem_match.groups()
        hour = int(hour_text)
        minute = int(minute_text or "0")
        if marker in {"오후", "저녁", "밤"} and hour < 12:
            hour += 12
        if marker in {"오전", "아침"} and hour == 12:
            hour = 0
        return normalize_hour_minute(hour, minute)

    colon_match = re.search(r"\b(\d{1,2}):(\d{2})\b", normalized)
    if colon_match:
        hour, minute = (int(part) for part in colon_match.groups())
        return normalize_hour_minute(hour, minute)

    hour_match = re.search(r"(?<!\d)(\d{1,2})\s*시(?:\s*(\d{1,2})\s*분?)?", normalized)
    if hour_match:
        hour = int(hour_match.group(1))
        minute = int(hour_match.group(2) or "0")
        return normalize_hour_minute(hour, minute)

    english_match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", normalized, re.IGNORECASE)
    if english_match:
        hour = int(english_match.group(1))
        minute = int(english_match.group(2) or "0")
        marker = english_match.group(3).casefold()
        if marker == "pm" and hour < 12:
            hour += 12
        if marker == "am" and hour == 12:
            hour = 0
        return normalize_hour_minute(hour, minute)

    return None


def normalize_hour_minute(hour: int, minute: int) -> str | None:
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return f"{hour:02d}:{minute:02d}"


def remove_due_time_text(text: str) -> str:
    cleaned = re.sub(
        r"(오전|오후|아침|저녁|밤)\s*\d{1,2}\s*시(?:\s*\d{1,2}\s*분?)?(?:까지|에|까지는)?",
        "",
        text,
    )
    cleaned = re.sub(r"\b\d{1,2}:\d{2}\b(?:까지|에|까지는)?", "", cleaned)
    cleaned = re.sub(r"(?<!\d)\d{1,2}\s*시(?:\s*\d{1,2}\s*분?)?(?:까지|에|까지는)?", "", cleaned)
    cleaned = re.sub(r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm)\b(?:까지|에|까지는)?", "", cleaned, flags=re.IGNORECASE)
    return cleaned


def extract_task_candidates_from_messages(rows: list) -> list[tuple[str, str | None]]:
    candidates: list[tuple[str, str | None]] = []
    seen: set[str] = set()
    for row in rows:
        if row["role"] == "assistant":
            continue
        for sentence in split_task_candidate_sentences(str(row["content"])):
            title = normalize_task_candidate(sentence)
            if not title:
                continue
            key = re.sub(r"\s+", " ", title.casefold()).strip()
            if key in seen:
                continue
            seen.add(key)
            candidates.append((title, extract_due_at(sentence)))
    return candidates


def split_task_candidate_sentences(text: str) -> list[str]:
    pieces = re.split(r"[\n.!?。]+", text)
    return [piece.strip(" -•\t") for piece in pieces if piece.strip(" -•\t")]


def normalize_task_candidate(sentence: str) -> str:
    cleaned = re.sub(r"^@\S+\s*", "", sentence.strip())
    lowered = cleaned.casefold()
    task_markers = [
        "해야",
        "할게",
        "하자",
        "해주세요",
        "해줘",
        "필요",
        "챙겨",
        "작성",
        "검토",
        "공유",
        "확인",
        "todo",
        "follow up",
    ]
    if not any(marker in lowered for marker in task_markers):
        return ""
    cleaned = re.sub(
        r"^(?:내가|제가|우리가|우리|너가|네가|봇이|assistant가)\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"(?:해야\s*해|해야\s*합니다|할게요|할게|하자|해주세요|해줘)\s*$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" :：-.,")
    if len(cleaned) < 4:
        return ""
    return cleaned[:120]


def compact_preview(text: str, *, limit: int = 96) -> str:
    compact = " ".join(text.split())
    if not compact:
        return "(내용 없음)"
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def format_conversation_location(conversation_id: str) -> str:
    if conversation_id.startswith("dm:"):
        return "DM"
    if conversation_id.startswith("thread:"):
        parts = conversation_id.split(":")
        return f"스레드 `{parts[1]}`" if len(parts) > 1 and parts[1] else "스레드"
    if conversation_id.startswith("channel:"):
        parts = conversation_id.split(":")
        return f"채널 `{parts[1]}`" if len(parts) > 1 and parts[1] else "채널"
    if conversation_id.startswith("local:"):
        return "로컬 CLI"
    if conversation_id.startswith("admin:"):
        return "관리 CLI"
    return f"`{conversation_id}`"


def format_detail(
    title: str,
    text: str,
    label: str,
    created_at: str,
    source_location: str,
    max_chars: int = 1400,
) -> str:
    body = text.strip()
    suffix = ""
    if len(body) > max_chars:
        body = body[:max_chars].rstrip()
        suffix = "\n...내용이 길어 앞부분만 보여줬어요. 구체적으로 질문하면 해당 내용 기준으로 답할게요."
    return f"{label}\n- 제목: {title}\n- 저장 위치: {source_location}\n- 저장 시각: {created_at}\n\n{body}{suffix}"


def format_memory_context(results: list) -> str:
    lines = []
    for index, result in enumerate(results, start=1):
        lines.append(
            f"[{index}] 종류: {result.kind}, 제목: {result.title}, 점수: {result.score:.3f}\n{result.text}"
        )
    return "\n\n".join(lines)


def format_conversation_context(rows: list) -> str:
    return "\n".join(f"{row['role']}: {row['content']}" for row in rows)
