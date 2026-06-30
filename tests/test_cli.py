from pathlib import Path

import pytest
from conftest import pdf_text, run_weasymerge


def test_help_exits_cleanly() -> None:
    result = run_weasymerge(["--help"])
    assert result.returncode == 0
    assert "WeasyMerge" in result.stdout


def test_end_to_end_writes_a_pdf_per_row(tmp_path: Path) -> None:
    template = tmp_path / "tpl.html.j2"
    template.write_text("<p>Hello {{ row.Name }} (#{{ row_number }})</p>")
    csv = tmp_path / "data.csv"
    csv.write_text("Name\nAlice\nBob\n")
    out_pattern = str(tmp_path / "{row_number}-{row[Name]}.pdf")

    result = run_weasymerge(
        ["--data", str(csv), "--template", str(template), "--output", out_pattern]
    )
    assert result.returncode == 0, result.stderr

    alice = tmp_path / "1-Alice.pdf"
    bob = tmp_path / "2-Bob.pdf"
    assert alice.exists() and alice.stat().st_size > 0
    assert bob.exists() and bob.stat().st_size > 0

    alice_text = pdf_text(alice)
    assert "Alice" in alice_text
    assert "#1" in alice_text
    assert "Bob" in pdf_text(bob)


def test_data_can_come_from_stdin(tmp_path: Path) -> None:
    template = tmp_path / "tpl.html.j2"
    template.write_text("<p>{{ row.Name }}</p>")
    out_pattern = str(tmp_path / "{row_number}.pdf")

    result = run_weasymerge(
        ["--template", str(template), "--output", out_pattern],
        input="Name\nCharlie\n",
    )
    assert result.returncode == 0, result.stderr

    out = tmp_path / "1.pdf"
    assert out.exists()
    assert "Charlie" in pdf_text(out)


def test_unsafe_characters_in_row_are_stripped_from_filename(tmp_path: Path) -> None:
    template = tmp_path / "tpl.html.j2"
    template.write_text("<p>{{ row.Name }}</p>")
    csv = tmp_path / "data.csv"
    csv.write_text("Name\na/b:c\n")
    out_pattern = str(tmp_path / "{row[Name]}.pdf")

    result = run_weasymerge(
        ["--data", str(csv), "--template", str(template), "--output", out_pattern]
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "abc.pdf").exists()


def test_html_in_row_values_is_escaped_in_pdf(tmp_path: Path) -> None:
    template = tmp_path / "tpl.html.j2"
    template.write_text("<p>{{ row.Name }}</p>")
    csv = tmp_path / "data.csv"
    # The literal text "<b>" should appear in the PDF, not be rendered as bold.
    csv.write_text("Name\n<b>raw</b>\n")
    out_pattern = str(tmp_path / "{row_number}.pdf")

    result = run_weasymerge(
        ["--data", str(csv), "--template", str(template), "--output", out_pattern]
    )
    assert result.returncode == 0, result.stderr

    text = pdf_text(tmp_path / "1.pdf")
    assert "<b>raw</b>" in text


def test_rows_per_document_batches_into_n_per_pdf(tmp_path: Path) -> None:
    template = tmp_path / "tpl.html.j2"
    template.write_text(
        "<html><body>"
        "{% for row in batch.rows %}<p>{{ row.Name }}</p>{% endfor %}"
        "<footer>{{ batch.from_row_number }}-{{ batch.to_row_number }}"
        " of {{ batch.total_rows }}</footer>"
        "</body></html>"
    )
    csv = tmp_path / "data.csv"
    csv.write_text("Name\nAlice\nBob\nCarol\nDave\nEve\n")
    out_pattern = str(tmp_path / "{batch.from_row_number}-{batch.to_row_number}.pdf")

    result = run_weasymerge(
        [
            "--data",
            str(csv),
            "--template",
            str(template),
            "--output",
            out_pattern,
            "--rows-per-document=2",
        ]
    )
    assert result.returncode == 0, result.stderr

    p1 = tmp_path / "1-2.pdf"
    p2 = tmp_path / "3-4.pdf"
    p3 = tmp_path / "5-5.pdf"
    assert p1.exists() and p2.exists() and p3.exists()

    text1 = pdf_text(p1)
    assert "Alice" in text1 and "Bob" in text1
    assert "1-2 of 5" in text1
    assert "5-5 of 5" in pdf_text(p3)


def test_rows_per_document_all_makes_single_pdf(tmp_path: Path) -> None:
    template = tmp_path / "tpl.html.j2"
    template.write_text("{% for row in batch.rows %}<p>{{ row.Name }}</p>{% endfor %}")
    csv = tmp_path / "data.csv"
    csv.write_text("Name\nAlice\nBob\nCarol\n")
    out = tmp_path / "all.pdf"

    result = run_weasymerge(
        [
            "--data",
            str(csv),
            "--template",
            str(template),
            "--output",
            str(out),
            "--rows-per-document=all",
        ]
    )
    assert result.returncode == 0, result.stderr

    text = pdf_text(out)
    assert "Alice" in text and "Bob" in text and "Carol" in text


@pytest.mark.parametrize("value", ["0", "-1", "abc", "1.5"])
def test_rows_per_document_invalid_value(tmp_path: Path, value: str) -> None:
    template = tmp_path / "tpl.html.j2"
    template.write_text("x")
    csv = tmp_path / "data.csv"
    csv.write_text("Name\nAlice\n")

    result = run_weasymerge(
        [
            "--data",
            str(csv),
            "--template",
            str(template),
            "--output",
            str(tmp_path / "out.pdf"),
            f"--rows-per-document={value}",
        ]
    )
    assert result.returncode != 0
