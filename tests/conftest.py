import subprocess
import sys

from pypdf import PdfReader


def pdf_text(path) -> str:
    return "\n".join(page.extract_text() for page in PdfReader(str(path)).pages)


def run_weasymerge(args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "weasymerge", *args],
        capture_output=True,
        text=True,
        check=False,
        **kwargs,
    )
