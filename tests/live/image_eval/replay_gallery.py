"""Replay a frozen public gallery against the original private inputs, in either order."""

import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile


class FixedImages:
    def __init__(self, pixels):
        self.pixels = pixels

    async def get(self, url, *, image):
        return url, "image/png", self.pixels[url]


async def replay(args):
    sys.path.insert(0, str(args.source.resolve()))
    from assistant_bot.openai_service import Models, Settings
    from assistant_bot.visual_evidence import compare_page

    inputs = {c["label"]: c for c in json.loads(args.manifest.read_text(encoding="utf8"))}
    settings = Settings.load()
    models = Models(settings)
    try:
        with ZipFile(args.gallery) as archive:
            for case in json.loads(archive.read("cases.json")):
                original = inputs[case["input"]]
                pixels = {url: archive.read(key) for url, key in case["pixels"].items()}
                if any(hashlib.sha256(data).hexdigest() != case["pixels"][url] for url, data in pixels.items()):
                    raise ValueError("Gallery image hash mismatch")

                async def load_original(path=Path(original["path"])):
                    return path.read_bytes()

                for reverse in (False, True):
                    page = dict(case["page"])
                    if reverse:
                        page["images"] = list(reversed(page["images"]))
                    result = await compare_page(
                        models, settings, FixedImages(pixels), page, original["prompt"], load_original, lambda: False
                    )
                    choices = [e["url"].split("?")[0] for e in result["candidates"]]
                    selected = choices[result["match"] - 1] if result["match"] else ""
                    print(
                        json.dumps(
                            dict(
                                case=case["key"],
                                reverse=reverse,
                                correct=selected == case["gold"],
                                present=case["gold"] in choices,
                                comparison=result,
                            ),
                            ensure_ascii=False,
                        )
                    )
    finally:
        await models.client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Directory containing the frozen assistant_bot package")
    parser.add_argument("manifest", type=Path, help="Runner manifest with authorized local image paths")
    parser.add_argument("gallery", type=Path)
    asyncio.run(replay(parser.parse_args()))
