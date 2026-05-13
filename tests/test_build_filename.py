import pytest

from weasymerge import build_filename


@pytest.mark.parametrize(
    ("template", "row", "row_number", "expected"),
    [
        ("out/{row_number}.pdf", {}, 7, "out/7.pdf"),
        ("out/{row[Name]}.pdf", {"Name": "Alice"}, 1, "out/Alice.pdf"),
        (
            "pdfs/Invite {row_number} {row[Name]}.pdf",
            {"Name": "Alice"},
            3,
            "pdfs/Invite 3 Alice.pdf",
        ),
        ("out/{row[Name]}.pdf", {"Name": "a/b:c"}, 1, "out/abc.pdf"),
        ("out/{row[Name]}.pdf", {"Name": "Renée"}, 1, "out/Renee.pdf"),
    ],
)
def test_build_filename(template, row, row_number, expected):
    assert build_filename(template, row, row_number) == expected


def test_missing_field_raises():
    with pytest.raises(KeyError):
        build_filename("out/{row[Missing]}.pdf", {"Name": "Alice"}, 1)
