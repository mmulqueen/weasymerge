from pathlib import Path

import pytest
from conftest import run_weasymerge

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def _discover_csv_examples():
    if not EXAMPLES_DIR.is_dir():
        return
    for example in sorted(EXAMPLES_DIR.iterdir()):
        if not example.is_dir():
            continue
        csvs = list(example.glob("*.csv"))
        templates = list(example.glob("*.j2"))
        if len(csvs) == 1 and len(templates) == 1:
            yield pytest.param(example, csvs[0], templates[0], id=example.name)


@pytest.mark.parametrize(("example", "csv", "template"), list(_discover_csv_examples()))
def test_example_runs_end_to_end(example, csv, template, tmp_path):
    out_pattern = str(tmp_path / "{row_number}.pdf")
    result = run_weasymerge(
        ["--data", str(csv), "--template", str(template), "--output", out_pattern]
    )
    assert result.returncode == 0, result.stderr

    pdfs = list(tmp_path.glob("*.pdf"))
    assert pdfs, f"example {example.name} produced no PDFs"
    for pdf in pdfs:
        assert pdf.stat().st_size > 0
