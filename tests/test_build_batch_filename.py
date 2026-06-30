import pytest

from weasymerge import Batch, build_batch_filename


def _batch(rows: list[dict[str, str]], from_row_number: int, total: int) -> Batch:
    return Batch(
        rows=rows,
        from_row_number=from_row_number,
        to_row_number=from_row_number + len(rows) - 1,
        total_rows=total,
    )


@pytest.mark.parametrize(
    ("template", "batch", "expected"),
    [
        (
            "out/{batch.from_row_number}-{batch.to_row_number}.pdf",
            _batch([{}, {}, {}], 1, 10),
            "out/1-3.pdf",
        ),
        (
            "page-{batch.total_rows}.pdf",
            _batch([{}], 1, 42),
            "page-42.pdf",
        ),
        (
            "out/{batch.rows[0][Name]}.pdf",
            _batch([{"Name": "Renée"}], 1, 1),
            "out/Renee.pdf",
        ),
        (
            "labels-{batch.from_row_number}-{batch.to_row_number}-of-{batch.total_rows}.pdf",
            _batch([{}, {}], 25, 100),
            "labels-25-26-of-100.pdf",
        ),
    ],
    ids=["range", "total", "first-row-field-sanitised", "combined"],
)
def test_build_batch_filename(template: str, batch: Batch, expected: str) -> None:
    assert build_batch_filename(template, batch) == expected


def test_unsafe_chars_in_row_field_sanitised() -> None:
    batch = _batch([{"Name": "a/b:c"}], 1, 1)
    assert build_batch_filename("out/{batch.rows[0][Name]}.pdf", batch) == "out/abc.pdf"


def test_missing_field_raises() -> None:
    batch = _batch([{"Name": "Alice"}], 1, 1)
    with pytest.raises(KeyError):
        build_batch_filename("out/{batch.rows[0][Missing]}.pdf", batch)
