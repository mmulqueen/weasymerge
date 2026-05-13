import subprocess
import sys
from pathlib import Path
from typing import Any

from pypdf import PdfReader


def pdf_text(path: Path | str) -> str:
    return "\n".join(page.extract_text() for page in PdfReader(str(path)).pages)


def run_weasymerge(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "weasymerge", *args],
        capture_output=True,
        text=True,
        check=False,
        **kwargs,
    )
