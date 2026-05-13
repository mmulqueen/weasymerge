from pathlib import Path

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
