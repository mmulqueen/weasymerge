from pathlib import Path
from typing import NamedTuple

import pytest
from conftest import run_weasymerge

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


class Example(NamedTuple):
    name: str  # directory under examples/
    args: list[str]  # weasymerge args; --output is appended by the test
    output: str  # --output pattern, rendered into tmp_path


EXAMPLES = [
    Example(
        "invites",
        ["--data", "guests.csv", "--template", "invite.html.j2"],
        "{row_number}.pdf",
    ),
    Example(
        "labels",
        [
            "--data", "seeds.csv",
            "--template", "labels.html.j2",
            "--rows-per-document=all",
        ],
        "labels-{batch.from_row_number}-{batch.to_row_number}.pdf",
    ),
    Example(
        "tickets",
        ["--data", "attendees.csv", "--template", "ticket.html.j2"],
        "ticket-{row[TicketID]}.pdf",
    ),
]


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: e.name)
def test_example_runs_end_to_end(example: Example, tmp_path: Path) -> None:
    result = run_weasymerge(
        [*example.args, "--output", str(tmp_path / example.output)],
        cwd=EXAMPLES_DIR / example.name,
    )
    assert result.returncode == 0, result.stderr

    pdfs = list(tmp_path.glob("*.pdf"))
    assert pdfs, f"example {example.name} produced no PDFs"
    for pdf in pdfs:
        assert pdf.stat().st_size > 0