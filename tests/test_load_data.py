from io import StringIO

import pytest

from weasymerge import load_data


@pytest.mark.parametrize(
    ("csv_text", "expected"),
    [
        (
            "Name,Email\nAlice,a@example.com\nBob,b@example.com\n",
            [
                {"Name": "Alice", "Email": "a@example.com"},
                {"Name": "Bob", "Email": "b@example.com"},
            ],
        ),
        ("Name,Email\n", []),
        ("", []),
        ("Name\n  Alice  \n", [{"Name": "  Alice  "}]),
        (
            'Name,Note\nAlice,"hello, world"\n',
            [{"Name": "Alice", "Note": "hello, world"}],
        ),
    ],
    ids=[
        "multiple-rows",
        "header-only",
        "empty",
        "whitespace-preserved",
        "quoted-commas",
    ],
)
def test_load_data(csv_text: str, expected: list[dict[str, str]]) -> None:
    assert list(load_data(StringIO(csv_text))) == expected
