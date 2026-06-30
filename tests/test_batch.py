from weasymerge import Batch


def test_numbered_rows_starts_at_from_row_number() -> None:
    batch = Batch(
        rows=[{"Name": "Alice"}, {"Name": "Bob"}, {"Name": "Carol"}],
        from_row_number=5,
        to_row_number=7,
        total_rows=10,
    )
    assert batch.numbered_rows == [
        (5, {"Name": "Alice"}),
        (6, {"Name": "Bob"}),
        (7, {"Name": "Carol"}),
    ]


def test_numbered_rows_empty_when_no_rows() -> None:
    batch = Batch(rows=[], from_row_number=1, to_row_number=0, total_rows=0)
    assert batch.numbered_rows == []
