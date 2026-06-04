from __future__ import annotations

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope
from assistant_bot.operation_result import OperationResult
from assistant_bot.stores import AgentLogStore, ConversationStore, TaskStore
from assistant_bot.time_utils import humanize_datetime_text

from .common import (
    asks_to_clear_task_due,
    asks_to_complete_task,
    asks_to_complete_task_batch,
    asks_to_create_task_from_recent_message,
    asks_to_delete_latest_task,
    asks_to_delete_task,
    asks_to_extract_tasks,
    asks_to_list_deleted_tasks,
    asks_to_list_due_tasks,
    asks_to_list_tasks,
    asks_to_postpone_task,
    asks_to_reference_latest_added_task,
    asks_to_rename_task,
    asks_to_reopen_latest_completed_task,
    asks_to_reopen_task,
    asks_to_restore_task,
    asks_to_save_extracted_tasks,
    asks_to_search_tasks,
    asks_to_set_task_priority,
    asks_to_show_latest_task_detail,
    asks_to_show_task_detail,
    asks_to_snooze_latest_reminded_task,
    extract_due_at,
    extract_task_action_query,
    extract_task_candidates_from_messages,
    extract_task_creation,
    extract_task_due_filter,
    extract_task_ids,
    extract_task_list_status,
    extract_task_priority,
    extract_task_rename_title,
    extract_task_search_query,
    format_task_detail,
    format_task_priority,
    has_task_due_filter_marker,
    normalize_context_task_title,
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

    def handle(self, *, text: str, scope: ConversationScope, message_id: str | None = None) -> OperationResult | str:
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
            return self._result(
                "추가할 할 일을 잘 모르겠어요. 예: `할 일 추가: 금요일까지 제안서 초안 작성`",
                status="needs_input",
                summary="할 일 제목이 필요함",
                next_actions=("추가할 할 일 제목을 물어본다",),
            )
        priority = extract_task_priority(text) or "normal"
        duplicate = self.tasks.find_open_duplicate(scope=scope, title=title)
        if duplicate is not None:
            due_text = f" · 기한: {duplicate.due_at}" if duplicate.due_at else ""
            priority_text = f" · 우선순위: {format_task_priority(duplicate.priority)}"
            fallback = (
                f"이미 같은 열린 할 일이 있어요. 기존 할 일 ID는 `{duplicate.id}`입니다."
                f"{priority_text}{due_text}"
            )
            return self._result(
                fallback,
                status="success",
                summary="중복 열린 할 일 확인",
                facts={"duplicate_task": self._task_item(duplicate)},
                preserve_values=(str(duplicate.id), duplicate.title),
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
        return self._result(
            f"할 일 `{task_id}`로 추가했어요.{priority_text}{due_text}",
            status="success",
            summary="할 일 추가 완료",
            facts={
                "task_id": task_id,
                "title": title,
                "priority": priority,
                "priority_label": format_task_priority(priority),
                "due_at": due_at,
                "human_due_at": humanize_datetime_text(due_at, self.config.timezone) if due_at else None,
            },
            preserve_values=tuple(value for value in (str(task_id), title, due_at) if value),
        )

    def list_tasks(self, *, text: str, scope: ConversationScope) -> OperationResult:
        status = extract_task_list_status(text)
        stats = self.tasks.stats(scope=scope)
        items = self.tasks.list_recent(user_id=scope.user_id, status=status, limit=10)
        if not items:
            empty_labels = {
                "open": "열린 할 일이 없어요.",
                "completed": "완료한 할 일이 없어요.",
                "all": "표시할 할 일이 없어요.",
            }
            return self._result(
                empty_labels[status],
                status="success",
                summary="조건에 맞는 할 일 없음",
                facts={"list_status": status, "open_count": stats["open"], "completed_count": stats["completed"]},
            )
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
        return self._result(
            "\n".join(lines),
            status="success",
            summary="할 일 목록 조회",
            facts={"list_status": status, "open_count": stats["open"], "completed_count": stats["completed"]},
            items=tuple(self._task_item(item) for item in items),
            preserve_values=tuple(str(item.id) for item in items),
            next_actions=("완료, 미루기, 삭제 같은 후속 작업을 필요할 때만 짧게 안내한다",),
        )

    def complete_task_batch(self, *, text: str, scope: ConversationScope) -> OperationResult:
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
            return self._result(
                f"완료 처리할 {label}이 없어요.",
                status="not_found",
                summary="완료 처리할 할 일 없음",
                facts={"label": label},
            )

        completed = self.tasks.complete(scope=scope, task_ids=[item.id for item in items])
        lines = [f"{label} {completed}개를 완료 처리했어요."]
        for item in items[:5]:
            due_text = f" · 기한: {item.due_at}" if item.due_at else ""
            lines.append(f"- 할 일 `{item.id}` · {item.title}{due_text}")
        if len(items) > 5:
            lines.append(f"...외 {len(items) - 5}개")
        lines.append("실수라면 `할 일 3 다시 열어줘`처럼 되돌릴 수 있어요.")
        return self._result(
            "\n".join(lines),
            status="success",
            summary="할 일 일괄 완료 처리",
            facts={"label": label, "completed_count": completed, "total_matched": len(items)},
            items=tuple(self._task_item(item) for item in items[:5]),
            preserve_values=tuple(str(item.id) for item in items[:5]),
            next_actions=("실수한 경우 다시 열 수 있음을 짧게 안내한다",),
        )

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

    def list_deleted_tasks(self, *, scope: ConversationScope) -> OperationResult:
        items = self.tasks.list_deleted(scope=scope, limit=10)
        if not items:
            return self._result(
                "삭제한 할 일이 없어요.",
                status="success",
                summary="삭제한 할 일 없음",
            )
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
        return self._result(
            "\n".join(lines),
            status="success",
            summary="삭제한 할 일 목록 조회",
            facts={"deleted_count": len(items)},
            items=tuple(self._task_item(item) for item in items),
            preserve_values=tuple(str(item.id) for item in items),
            next_actions=("복구가 필요하면 ID로 요청할 수 있음을 짧게 안내한다",),
        )

    def search_tasks(self, *, text: str, scope: ConversationScope) -> OperationResult:
        query = extract_task_search_query(text)
        if not query:
            return self._result(
                "찾을 할 일 키워드를 알려주세요. 예: `제안서 할 일 찾아줘`",
                status="needs_input",
                summary="할 일 검색 키워드 필요",
                next_actions=("검색할 키워드를 물어본다",),
            )
        items = self.tasks.search(scope=scope, keyword=query, limit=10)
        if not items:
            return self._result(
                f"`{query}`와 관련된 할 일을 찾지 못했어요.",
                status="not_found",
                summary="검색 조건에 맞는 할 일 없음",
                facts={"query": query},
                preserve_values=(query,),
            )
        lines = [f"`{query}` 할 일 검색 결과 {len(items)}개:"]
        for item in items:
            due_text = f" · 기한: {item.due_at}" if item.due_at else ""
            completed_text = f" · 완료: {item.completed_at}" if item.completed_at else ""
            lines.append(
                f"- 할 일 `{item.id}` · {item.title} · 상태: {item.status} · "
                f"우선순위: {format_task_priority(item.priority)}{due_text}{completed_text} · "
                f"저장 위치: {item.source_location}"
            )
        return self._result(
            "\n".join(lines),
            status="success",
            summary="할 일 검색 결과 조회",
            facts={"query": query, "result_count": len(items)},
            items=tuple(self._task_item(item) for item in items),
            preserve_values=(query,) + tuple(str(item.id) for item in items),
        )

    def show_task_detail(self, *, text: str, scope: ConversationScope) -> OperationResult:
        if asks_to_show_latest_task_detail(text):
            item = self.tasks.latest(scope=scope)
            if item is None:
                return self._result(
                    "아직 저장된 할 일이 없어요. `할 일 추가: ...`처럼 말하면 저장할 수 있습니다.",
                    status="not_found",
                    summary="최근 저장된 할 일 없음",
                    next_actions=("새 할 일을 추가할 수 있음을 짧게 안내한다",),
                )
            return self._result(
                format_task_detail(item),
                status="success",
                summary="최근 할 일 상세 조회",
                facts={"task": self._task_item(item)},
                preserve_values=(str(item.id), item.title),
            )

        task_ids = extract_task_ids(text)
        if not task_ids:
            return self._result(
                "확인할 할 일 ID를 알려주세요. 예: `할 일 3 보여줘`",
                status="needs_input",
                summary="상세 조회할 할 일 ID 필요",
                next_actions=("확인할 할 일 ID를 물어본다",),
            )
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
        if not lines:
            return self._result(
                "해당 할 일을 찾지 못했어요.",
                status="not_found",
                summary="요청한 할 일 상세 없음",
                facts={"requested_task_ids": task_ids[:5]},
                preserve_values=tuple(str(task_id) for task_id in task_ids[:5]),
            )
        found_items = [
            self.tasks.get(scope=scope, task_id=task_id)
            for task_id in task_ids[:5]
            if self.tasks.get(scope=scope, task_id=task_id) is not None
        ]
        return self._result(
            "\n\n".join(lines),
            status="success",
            summary="할 일 상세 조회",
            facts={"requested_task_ids": task_ids[:5], "missing_task_ids": missing},
            items=tuple(self._task_item(item) for item in found_items if item is not None),
            preserve_values=tuple(str(task_id) for task_id in task_ids[:5]),
        )

    def list_due_tasks(self, *, text: str, scope: ConversationScope) -> OperationResult:
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
            return self._result(
                f"{due_filter['empty_label']} 열린 할 일이 없어요.",
                status="success",
                summary="기한 조건에 맞는 열린 할 일 없음",
                facts={"due_filter": due_filter},
            )
        lines = [f"{due_filter['heading']} {len(items)}개:"]
        for item in items:
            due_label = "기한 없음" if item.due_at is None else f"{item.due_at}까지"
            lines.append(
                f"- 할 일 `{item.id}` · {item.title} · 우선순위: {format_task_priority(item.priority)} · "
                f"{due_label} · 저장 위치: {item.source_location}"
            )
        lines.append("완료하면 `할 일 3 완료했어`, 미루려면 `할 일 3 내일 다시 알려줘`라고 말해 주세요.")
        return self._result(
            "\n".join(lines),
            status="success",
            summary="기한 기준 할 일 목록 조회",
            facts={"due_filter": due_filter, "result_count": len(items)},
            items=tuple(self._task_item(item) for item in items),
            preserve_values=tuple(str(item.id) for item in items),
            next_actions=("완료하거나 미룰 수 있음을 필요할 때만 짧게 안내한다",),
        )

    def extract_tasks_from_conversation(
        self,
        *,
        text: str,
        scope: ConversationScope,
        message_id: str | None = None,
    ) -> OperationResult:
        recent = self.conversations.recent_messages(scope.conversation_id, limit=40)
        candidates = extract_task_candidates_from_messages(recent)
        if not candidates:
            return self._result(
                "최근 대화에서 바로 할 일로 볼 만한 문장을 찾지 못했어요.",
                status="not_found",
                summary="최근 대화에서 할 일 후보 없음",
            )

        if asks_to_save_extracted_tasks(text):
            saved: list[dict[str, object]] = []
            skipped: list[dict[str, object]] = []
            for title, due_at in candidates[:10]:
                duplicate = self.tasks.find_open_duplicate(scope=scope, title=title)
                if duplicate is not None:
                    skipped.append(self._task_item(duplicate))
                    continue
                priority = extract_task_priority(title) or "normal"
                task_id = self.tasks.add(
                    scope=scope,
                    title=title,
                    priority=priority,
                    due_at=due_at,
                    source_message_id=message_id,
                )
                saved.append(
                    {
                        "task_id": task_id,
                        "title": title,
                        "priority": priority,
                        "priority_label": format_task_priority(priority),
                        "due_at": due_at,
                        "human_due_at": humanize_datetime_text(due_at, self.config.timezone) if due_at else None,
                    }
                )
            lines: list[str] = []
            if saved:
                lines.append(f"최근 대화에서 할 일 {len(saved)}개를 추가했어요:")
                for item in saved:
                    due_text = f" · 기한: {item['due_at']}" if item["due_at"] else ""
                    lines.append(
                        f"- `{item['task_id']}` · {item['title']} · "
                        f"우선순위: {item['priority_label']}{due_text}"
                    )
            if skipped:
                lines.append("이미 열린 할 일로 있어서 건너뛴 항목:")
                lines.extend(f"- `{item['task_id']}` · {item['title']}" for item in skipped)
            if not lines:
                return self._result(
                    "추가할 새 할 일이 없어요.",
                    status="not_found",
                    summary="최근 대화에서 새로 추가할 할 일 없음",
                )
            return self._result(
                "\n".join(lines),
                status="success",
                summary="최근 대화에서 할 일 추출 후 추가",
                facts={"saved_count": len(saved), "skipped_duplicate_count": len(skipped)},
                items=tuple(saved),
                warnings=tuple(f"중복으로 건너뜀: {item['task_id']} · {item['title']}" for item in skipped),
                preserve_values=tuple(str(item["task_id"]) for item in saved + skipped),
            )

        lines = [f"최근 대화에서 할 일 후보 {len(candidates[:10])}개를 찾았어요:"]
        candidate_items: list[dict[str, object]] = []
        for index, (title, due_at) in enumerate(candidates[:10], start=1):
            due_text = f" · 기한: {due_at}" if due_at else ""
            priority = extract_task_priority(title) or "normal"
            lines.append(f"{index}. {title} · 우선순위: {format_task_priority(priority)}{due_text}")
            candidate_items.append(
                {
                    "index": index,
                    "title": title,
                    "priority": priority,
                    "priority_label": format_task_priority(priority),
                    "due_at": due_at,
                    "human_due_at": humanize_datetime_text(due_at, self.config.timezone) if due_at else None,
                }
            )
        lines.append("저장하려면 `최근 대화에서 할 일 뽑아서 추가해줘`라고 말해 주세요.")
        return self._result(
            "\n".join(lines),
            status="success",
            summary="최근 대화에서 할 일 후보 추출",
            facts={"candidate_count": len(candidate_items)},
            items=tuple(candidate_items),
            next_actions=("저장하려면 추가 요청을 할 수 있음을 짧게 안내한다",),
        )

    def create_task_from_recent_message(
        self,
        *,
        text: str,
        scope: ConversationScope,
        message_id: str | None = None,
    ) -> OperationResult:
        latest = self.conversations.latest_user_message(conversation_id=scope.conversation_id, user_id=scope.user_id)
        if latest is None:
            return self._result(
                "바로 전에 말한 내용을 찾지 못했어요. `할 일 추가: ...`처럼 제목을 알려주세요.",
                status="not_found",
                summary="직전 사용자 메시지 없음",
                next_actions=("할 일 제목을 직접 알려달라고 안내한다",),
            )

        previous_text = str(latest["content"]).strip()
        if not previous_text:
            return self._result(
                "바로 전에 말한 내용이 비어 있어서 할 일로 만들 수 없어요.",
                status="not_found",
                summary="직전 사용자 메시지가 비어 있음",
            )

        title, due_at = extract_task_creation(previous_text, timezone_name=self.config.timezone)
        title = normalize_context_task_title(title or previous_text)
        if not title:
            return self._result(
                "바로 전에 말한 내용에서 할 일 제목을 만들기 어려워요. `할 일 추가: ...`처럼 알려주세요.",
                status="needs_input",
                summary="직전 메시지에서 할 일 제목 추출 실패",
                next_actions=("할 일 제목을 직접 물어본다",),
            )

        priority = extract_task_priority(text) or extract_task_priority(previous_text) or "normal"
        duplicate = self.tasks.find_open_duplicate(scope=scope, title=title)
        if duplicate is not None:
            due_text = f" · 기한: {duplicate.due_at}" if duplicate.due_at else ""
            return self._result(
                f"이미 같은 열린 할 일이 있어요. 기존 할 일 ID는 `{duplicate.id}`입니다.{due_text}",
                status="success",
                summary="직전 메시지 기반 할 일 중복 확인",
                facts={"duplicate_task": self._task_item(duplicate)},
                preserve_values=(str(duplicate.id), duplicate.title),
            )

        task_id = self.tasks.add(
            scope=scope,
            title=title,
            priority=priority,
            due_at=due_at,
            source_message_id=message_id,
        )
        due_text = f" · 기한: {due_at}" if due_at else ""
        return self._result(
            f"바로 전에 말한 내용을 할 일 `{task_id}`로 추가했어요. · {title}{due_text}",
            status="success",
            summary="직전 메시지 기반 할 일 추가 완료",
            facts={
                "task_id": task_id,
                "title": title,
                "priority": priority,
                "priority_label": format_task_priority(priority),
                "due_at": due_at,
                "human_due_at": humanize_datetime_text(due_at, self.config.timezone) if due_at else None,
            },
            preserve_values=tuple(value for value in (str(task_id), title, due_at) if value),
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
            agent="task",
            intent="manage_task",
            status=status,
            summary=summary,
            facts=facts or {},
            items=items,
            warnings=warnings,
            next_actions=next_actions,
            preserve_values=preserve_values,
            fallback_text=fallback_text,
        )

    def _task_item(self, item) -> dict[str, object]:
        return {
            "task_id": item.id,
            "title": item.title,
            "status": item.status,
            "priority": item.priority,
            "priority_label": format_task_priority(item.priority),
            "due_at": item.due_at,
            "human_due_at": humanize_datetime_text(item.due_at, self.config.timezone) if item.due_at else None,
            "completed_at": item.completed_at,
            "source_location": item.source_location,
        }
