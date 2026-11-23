"""Run the evaluated image-binding variant in a temporary source tree."""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Verify the candidate without connecting to Discord")
    args = parser.parse_args()
    trial = Path(__file__).resolve().parent
    root = trial.parents[3]
    with TemporaryDirectory(prefix="jeda-image-trial-") as folder:
        work = Path(folder)
        shutil.copytree(root / "assistant_bot", work / "assistant_bot", ignore=shutil.ignore_patterns("__pycache__"))
        subprocess.run(
            ["git", "apply", "--include=assistant_bot/*", str(trial / "candidate.patch")], cwd=work, check=True
        )
        sys.path.insert(0, str(work))
        from assistant_bot import main as bot
        from assistant_bot.visual_evidence import photo_checks

        assert Path(bot.__file__).resolve().is_relative_to(work)
        if args.check:
            print("Candidate ready:", photo_checks.__name__)
            return
        os.chdir(root)
        load_dotenv(root / ".env")
        bot.main()


if __name__ == "__main__":
    main()
