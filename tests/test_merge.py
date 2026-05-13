import pytest
from jinja2 import Environment

from weasymerge import merge


@pytest.mark.parametrize(
    ("source", "row", "row_number", "expected"),
    [
        ("{{ row.Name }} <{{ row.Email }}>", {"Name": "Alice", "Email": "a@x"}, 1, "Alice <a@x>"),
        ("{{ row['Name'] }}", {"Name": "Alice"}, 1, "Alice"),
        ("#{{ row_number }}", {}, 42, "#42"),
    ],
    ids=["attribute-access", "subscript-access", "row-number"],
)
def test_merge_exposes_row_and_row_number(source, row, row_number, expected):
    template = Environment(autoescape=False).from_string(source)
    assert merge(template, row, row_number) == expected
