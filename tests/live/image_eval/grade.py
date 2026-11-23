"""Mask the trial arm for adjudication, then apply the predeclared release gate."""

import argparse
import hashlib
import json
import statistics
from pathlib import Path


def read_rows(folder):
    for path in sorted(folder.glob("*.jsonl")):
        for line in path.read_text(encoding="utf8").splitlines():
            yield path.stem.split("-")[-1], json.loads(line)


def display_id(case, arm):
    return hashlib.sha256(("paired-v1/" + case + "/" + arm).encode()).hexdigest()[:9]


def packet(row):
    sources, photos, search, observations = [], [], [], []
    for tool in row["evidence"]:
        if tool["tool"] == "file":
            observations.append(tool["text"])
        for record in tool.get("records", []):
            if record["kind"] == "page":
                sources.append(dict(url=record["url"], title=record.get("title", "")))
            if record.get("comparison"):
                photos.append(record["comparison"])
            if record["kind"] == "hosted_search":
                search.extend(
                    p.get("text", "")
                    for msg in json.loads(record["text"])
                    if msg["type"] == "message"
                    for p in msg.get("content", [])
                )
    return dict(
        answer=next((text for kind, text in row["responses"] if kind == "final"), ""),
        state=row["state"],
        observations=observations,
        search=search,
        pages=sources,
        photos=photos,
    )


def summarize(rows, judgments):
    totals = {}
    for arm in ("A", "B"):
        group = [r for v, r in rows if v == arm]
        judged = [(r, judgments[display_id(r["case"], arm)]) for r in group]
        metrics = [m for r in group for m in r["metrics"]]
        totals[arm] = dict(
            old=sum(j["full"] for r, j in judged if not r["case"].startswith("new-")),
            blind=sum(j["full"] for r, j in judged if r["case"].startswith("new-")),
            calls=len(metrics),
            failed_calls=sum(m["status"] != "ok" for m in metrics),
            input_tokens=sum(m["input_tokens"] or 0 for m in metrics),
            output_tokens=sum(m["output_tokens"] or 0 for m in metrics),
            unknown_usage=sum(m["input_tokens"] is None for m in metrics),
            p95_seconds=round(statistics.quantiles([r["seconds"] for r in group], n=20, method="inclusive")[18], 1),
            photos=sum(r["unique_photos"] for r in group),
            unfounded=sum(j["unsupported"] for _, j in judged),
            false_photo=sum(j["false_photo"] for _, j in judged),
        )
    a, b = totals["A"], totals["B"]
    gain = b["blind"] - a["blind"]
    accepted = (
        b["old"] >= a["old"]
        and b["unfounded"] <= a["unfounded"]
        and b["false_photo"] == 0
        and ((gain >= 2 and b["calls"] <= a["calls"]) or (gain >= 3 and b["calls"] * 100 <= a["calls"] * 115))
    )
    return dict(totals=totals, adopt_B=accepted)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path, help="Raw JSONL directory or archived results.json")
    p.add_argument("--judgments", type=Path)
    args = p.parse_args()
    if args.input.is_file():
        archive = json.loads(args.input.read_text(encoding="utf8"))
        rows, judgments = [], {}
        for key, case in archive["cases"].items():
            for arm, run in case["runs"].items():
                rows.append(
                    (
                        arm,
                        dict(
                            case=key,
                            metrics=run["model_calls"],
                            seconds=run["seconds"],
                            unique_photos=run["unique_photos"],
                        ),
                    )
                )
                judgments[display_id(key, arm)] = run["judgment"]
    else:
        rows = list(read_rows(args.input))
        judgments = None
    if args.judgments:
        judgments = json.loads(args.judgments.read_text(encoding="utf8"))
    if judgments is not None:
        a_keys, b_keys = ({r["case"] for a, r in rows if a == arm} for arm in "AB")
        if len(rows) != 82 or a_keys != b_keys or len(a_keys) != 41 or sum(k.startswith("new-") for k in a_keys) != 24:
            raise ValueError("Expected 41 distinct requests per arm")
        print(json.dumps(summarize(rows, judgments), indent=2))
    else:
        items = {display_id(r["case"], arm): dict(case=r["case"], **packet(r)) for arm, r in rows}
        print(json.dumps(dict(sorted(items.items())), ensure_ascii=False))


if __name__ == "__main__":
    main()
