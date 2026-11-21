"""같은 대화 범위의 작업과 실제 판독·조회 결과를 후속 요청에 연결한다."""

import json
import re

from assistant_bot.openai_service import chunks, cited_urls


def excerpt(text, limit):
    return next(chunks(text or "", limit), "")


def work_index(store, scope, session, reply_id):
    args = (scope.key, session["epoch"])
    # Keep execution anchors for the entire history window and for tasks named in its summary.
    summary_ids = re.findall(r"(?<![0-9a-f])(?:[0-9]{15,22}|[0-9a-f]{32})(?![0-9a-f])", session["summary"])
    rows = store.db.execute(
        """SELECT j.* FROM jobs j WHERE j.scope=? AND j.epoch=? AND (
           j.id IN (SELECT id FROM jobs WHERE scope=? AND epoch=? ORDER BY rowid DESC LIMIT 8)
           OR j.id IN (SELECT msg FROM raw_messages WHERE scope=? AND epoch=? AND role='user' AND seq>?)
           OR j.id IN (SELECT value FROM json_each(?))) ORDER BY j.rowid DESC""",
        (*args, *args, *args, session["summarized"], json.dumps(summary_ids)),
    ).fetchall()
    linked = None
    if reply_id:
        linked = store.db.execute(
            """SELECT j.* FROM jobs j WHERE scope=? AND epoch=? AND (
                id=? OR EXISTS (SELECT 1 FROM json_each(sent) WHERE value->>'msg'=?)
                OR EXISTS (SELECT 1 FROM receipts WHERE msg=? AND job=j.id)
                OR EXISTS (SELECT 1 FROM json_each(updates) u WHERE u.value->>'id' IN
                    (?,(SELECT job FROM receipts WHERE msg=?)))) LIMIT 1""",
            (*args, reply_id, reply_id, reply_id, reply_id, reply_id),
        ).fetchone()
    jobs = {row["id"]: row for row in rows}
    if linked:
        jobs[linked["id"]] = linked
    return [work_item(row, reply=bool(linked and linked["id"] == row["id"])) for row in jobs.values()]


def work_item(row, *, reply=False, detailed=False):
    request = json.loads(row["request"])
    steps = [request, *json.loads(row["updates"])]
    plan = steps[-1].get("plan", {})
    removed = {key for step in steps for key in step.get("plan", {}).get("replaces", [])}
    evidence = json.loads(row["evidence"])
    tools, files = [], {}
    for step in steps:
        for ref in step.get("attachments", []) + (step.get("reply") or {}).get("attachments", []):
            files[ref["id"]] = ref
        for i, call in enumerate(step.get("plan", {}).get("calls", [])):
            key = f"{step['id']}:{i}"
            result = evidence.get(key, {})
            if key in removed and not result.get("changed"):
                continue
            item = {k: v for k, v in call.items() if v and k != "pdf_mode"}
            item["query"] = excerpt(call.get("question") or call.get("query"), 90)
            item["status"] = result.get("status", "unconfirmed")
            for k in ("source", "opened", "urls", "feeds", "unread"):
                if result.get(k):
                    v = result[k]
                    item[k] = v[:4] if isinstance(v, list) and not detailed else v
            if detailed or item["status"] in {"failed", "partial"}:
                item["text"] = excerpt(result.get("text"), 900 if detailed else 120)
            if detailed and result.get("records"):
                item["records"] = result["records"]
            tools.append(item)
    # Resolve unique names only on numbered lines of the answer actually delivered.
    displayed = {}
    if len(files) > 1:
        for number, label in re.findall(r"^\s*(\d+)[.)]\s+(.+)$", row["answer"], re.M):
            matches = [f for f in files.values() if f["name"] in label]
            if len(matches) == 1:
                displayed[number] = matches[0]["id"]
    return {
        "id": row["id"],
        **({"displayed_file_numbers": displayed} if displayed else {}),
        "request_urls": sorted({url for s in steps for url in cited_urls(s.get("text", ""))}),
        "source_jobs": (plan.get("followup") or {}).get("sources", []),
        "replied_to": reply,
        "state": row["state"],
        "request": excerpt(request.get("text"), 120),
        "intent": excerpt((plan.get("followup") or {}).get("intent") or steps[-1].get("text"), 180),
        "files": list(files.values()) if detailed else [{"id": k, "name": v["name"]} for k, v in files.items()],
        "tools": tools,
        "execution": "recorded" if tools else ("not_attempted" if "calls" in plan and not evidence else "unknown"),
        **(
            {
                "previous_answer": excerpt(row["answer"], 1000),
            }
            if detailed
            else {}
        ),
    }


def selected_work(store, scope, epoch, ids):
    items = []
    pending = list(dict.fromkeys(ids))
    for key in pending:
        row = store.db.execute(
            "SELECT * FROM jobs WHERE id=? AND scope=? AND epoch=?", (key, scope.key, epoch)
        ).fetchone()
        if row:
            item = work_item(row, detailed=True)
            items.append(item)
            if not item["tools"] and len(pending) < 12:
                pending.extend(i for i in item["source_jobs"] if i not in pending)
    return items


def followup_issue(plan, ctx):
    follow = plan.get("followup")
    if not follow:
        return ""
    action = follow["action"]
    if action == "clarify":
        return "" if plan["question"].strip() else "후보를 구분하는 질문이 필요합니다."
    if action in {"direct", "reuse"} and (plan["calls"] or plan.get("read_reply_files")):
        return "선택한 직접 답변·근거 재사용과 새 도구 호출 계획이 충돌합니다."
    if action in {"web", "file", "web_file"} and (not follow["intent"].strip() or plan["question"]):
        return "새 조회의 대상과 최종 요청을 확정하거나 필요한 정보를 질문하세요."
    if action in {"file", "web_file"}:
        refs = ctx["current"]["attachments"] + (ctx["current"]["reply"] or {}).get("attachments", [])
        ids = {r["id"] for r in [*refs, *ctx["recent_files"]]}
        for job in ctx["work"]:
            if job["id"] in follow["sources"]:
                ids.update(f["id"] for f in job["files"])
        ids.update(str(r["id"]) for r in ctx["memory_index"] if r["kind"] == "document")
        file_calls = [c for c in [*plan["calls"], *plan.get("read_reply_files", [])] if c.get("name", "file") == "file"]
        number = follow.get("displayed_file_number", 0)
        if number:
            ordered_ids = {
                job.get("displayed_file_numbers", {}).get(str(number))
                for job in ctx["work"]
                if job["id"] in follow["sources"]
            } - {None}
            if ordered_ids and {c["target"] for c in file_calls} != ordered_ids:
                return f"표시된 목록의 {number}번 ID는 {sorted(ordered_ids)}입니다. 대상 파일을 대조하세요."
        if not file_calls or any(c["target"] not in ids for c in file_calls):
            return "확인할 파일의 실제 ID와 요청한 범위를 file 호출에 지정하세요."
    return ""
