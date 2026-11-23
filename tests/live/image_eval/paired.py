"""Run one isolated paired suite with sealed inputs. No Discord connection."""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from PIL import Image, ImageChops, ImageStat


def parse(path):
    return json.loads(path.read_text(encoding="utf8"))


def count_photos(urls, seen):
    representatives = []
    unknown = 0
    for url in dict.fromkeys(urls):
        thumb = seen.get(url)
        if thumb is None:
            unknown += 1
            continue
        background = Image.new("RGB", thumb.size, "white")
        background.paste(thumb, mask=thumb.getchannel("A"))
        sample = background.resize((24, 24), Image.Resampling.LANCZOS)
        ratio = thumb.width / thumb.height
        if not any(
            abs(ratio / other_ratio - 1) < 0.025 and max(ImageStat.Stat(ImageChops.difference(sample, other)).rms) < 3
            for other_ratio, other in representatives
        ):
            representatives.append((ratio, sample))
    return len(representatives) + unknown


async def worker(opts, group):
    sys.path.insert(0, str((opts.work / opts.arm).resolve()))
    from assistant_bot.jeda_server import no_typing
    from assistant_bot.openai_service import Models, Settings
    from assistant_bot.runtime import Engine, Output, Request
    from assistant_bot.stores import JedaStore, Scope
    from assistant_bot.visual_evidence import thumbnail
    from assistant_bot.web_agent import Reader

    get = Reader.get
    seen = {}

    async def metered(reader, url, **kwargs):
        actual, media, data = await get(reader, url, **kwargs)
        if kwargs.get("image") and actual not in seen:
            try:
                seen[actual] = await asyncio.to_thread(thumbnail, data)
            except (OSError, ValueError, Image.DecompressionBombError):
                seen[actual] = None
        return actual, media, data

    Reader.get = metered
    with TemporaryDirectory() as tmp:
        cfg = Settings.load()
        store = JedaStore(Path(tmp) / "test.sqlite")
        models = Models(cfg, metrics_db=store.db)
        engine = Engine(cfg, store, models)
        files = {}
        scope = Scope("local", str(opts.group), "tester")
        output = opts.out / f"{opts.group}-{opts.arm}.jsonl"
        with output.open("x", encoding="utf8") as f:
            for c in group:
                key = uuid4().hex
                atts, responses = [], []
                if c["path"]:
                    p = Path(c["path"])
                    fid = uuid4().hex
                    files[fid] = p
                    atts.append(
                        dict(
                            id=fid,
                            name="image" + p.suffix,
                            size=p.stat().st_size,
                            guild=scope.guild,
                            channel=scope.channel,
                            message=key,
                        )
                    )

                async def send(kind, text, tag, *, recorded=responses):
                    recorded.append([kind, text])
                    return uuid4().hex

                async def load(ref):
                    return files[ref["id"]].read_bytes()

                start = time.monotonic()
                err = None
                try:
                    await engine.submit(scope, Request(key, c["prompt"], atts), Output(send, load, no_typing))
                except Exception as exc:
                    err = type(exc).__name__
                elapsed = time.monotonic() - start
                job = engine.job(key)
                evidence = list(json.loads(job["evidence"]).values()) if job else []
                photos = [
                    e["url"]
                    for t in evidence
                    for r in t.get("records", [])
                    for e in r.get("comparison", {}).get("candidates", [])
                ]
                metrics = [
                    dict(r)
                    for r in store.db.execute(
                        "SELECT model,purpose,status,seconds,input_tokens,output_tokens "
                        "FROM model_calls WHERE job=? ORDER BY id",
                        (key,),
                    )
                ]
                row = dict(
                    case=c["label"],
                    state=job["state"] if job else "failed",
                    error=err,
                    responses=responses,
                    seconds=elapsed,
                    metrics=metrics,
                    evidence=evidence,
                    unique_photos=count_photos(photos, seen),
                )
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
        await engine.shutdown()
        await models.client.close()
        store.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("work", type=Path)
    p.add_argument("manifest", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--arm", choices=["A", "B"])
    p.add_argument("--group", type=int)
    p.add_argument("--jobs", type=int, default=4)
    args = p.parse_args()
    cases = parse(args.manifest)
    if args.arm:
        asyncio.run(worker(args, [c for c in cases if c["channel"] == args.group]))
        return
    args.out.mkdir()
    groups = list(dict.fromkeys(c["channel"] for c in cases))

    def pair(item):
        i, g = item
        for arm in "AB" if i % 2 == 0 else "BA":
            subprocess.run(
                [
                    sys.executable,
                    __file__,
                    str(args.work),
                    str(args.manifest),
                    str(args.out),
                    "--arm",
                    arm,
                    "--group",
                    str(g),
                ],
                check=True,
                env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
            )
        print("paired", g, flush=True)

    with ThreadPoolExecutor(args.jobs) as pool:
        list(pool.map(pair, enumerate(groups)))


if __name__ == "__main__":
    main()
