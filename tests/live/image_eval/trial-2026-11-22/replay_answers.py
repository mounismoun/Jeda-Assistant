"""Replay old, fixed tool evidence through each arm's real final-answer path, without a new search."""

import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

PROBES = [
    ("helmet-identity", "B", ["게임", "스킨 이름"]),
    ("dog", "B", ["품종", "공개 사진 대조 근거"]),
    ("new-18", "A", ["캐릭터 이름", "공식 그림 대조 근거"]),
    ("frog-hint", "B", ["캐릭터 이름"]),
]


async def main(args):
    sys.path.insert(0, str((args.work / args.arm).resolve()))
    from assistant_bot.metrics import request_context
    from assistant_bot.openai_service import Models, Settings
    from assistant_bot.runtime import Engine, Output, Request
    from assistant_bot.stores import JedaStore, Scope

    previous = Path(".pytest_cache/paired_identity")
    questions = {c["label"]: c["prompt"] for c in json.loads((previous / "inputs.json").read_text(encoding="utf8"))}
    rows = {}
    for f in (previous / "final").glob("*.jsonl"):
        for line in f.read_text(encoding="utf8").splitlines():
            r = json.loads(line)
            rows[r["case"], f.stem.split("-")[-1]] = r

    async def run(case, old_arm, items):
        with TemporaryDirectory() as tmp:
            store = JedaStore(Path(tmp) / "trial.db")
            cfg = Settings.load()
            models = Models(cfg, metrics_db=store.db)
            engine = Engine(cfg, store, models)
            scope = Scope("eval", case, "tester")
            fixed = rows[case, old_arm]["evidence"]
            req = Request(case, questions[case], [])
            evidence = {f"{case}:{i}": tool for i, tool in enumerate(fixed)}
            plan = dict(
                role="reasoning",
                effort="medium",
                preferences=[],
                partial=False,
                unsupported="",
                initial="확인 중",
                review={"action": "answer", "coverage": []},
                identify_image=True,
                answer_items=items,
                language="ko",
                calls=[dict(name=t["tool"]) for t in fixed],
            )
            with store.db:
                store.db.execute(
                    "INSERT INTO jobs(id,scope,epoch,state,request,evidence) VALUES(?,?,1,'running',?,?)",
                    (case, scope.key, json.dumps(dict(asdict(req), plan=plan)), json.dumps(evidence)),
                )
            try:
                with request_context(case):
                    ans, _ = await engine.generate(scope, engine.job(case), Output(None, None, None))
                return dict(
                    case=case,
                    arm=args.arm,
                    answer=ans,
                    calls=[
                        dict(r)
                        for r in store.db.execute(
                            "SELECT purpose,status,input_tokens,output_tokens FROM model_calls ORDER BY id"
                        )
                    ],
                )
            finally:
                await engine.shutdown()
                await models.client.close()
                store.close()

    outputs = await asyncio.gather(*(run(*p) for p in PROBES))
    (args.work / ("replay-" + args.arm + ".json")).write_text(
        json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("work", type=Path)
    parser.add_argument("arm", choices=["A", "B"])
    asyncio.run(main(parser.parse_args()))
