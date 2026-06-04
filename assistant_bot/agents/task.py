from __future__ import annotations

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope
from assistant_bot.stores import AgentLogStore, ConversationStore, TaskStore

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


