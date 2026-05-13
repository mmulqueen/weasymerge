import pytest

from weasymerge import path_safe


@pytest.mark.parametrize(
    "value",
    [
        "Hello World",
        "file_name-1.0",
        "ABCdef 123",
        "a.b.c",
        "trailing ",
        " leading",
    ],
)
def test_allowed_characters_pass_through(value):
    assert path_safe(value) == value


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("a/b", "ab"),
        ("a\\b", "ab"),
        ("name:1", "name1"),
        ('a"b', "ab"),
        ("a*b?c", "abc"),
        ("a<b>c|d", "abcd"),
        ("a\nb\tc", "abc"),
        ("a;b,c", "abc"),
    ],
)
def test_disallowed_characters_stripped(value, expected):
    assert path_safe(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("café", "cafe"),
        ("naïve", "naive"),
        ("Zoë", "Zoe"),
        ("Renée Müller", "Renee Muller"),
        ("ÀÉÎÕÜ", "AEIOU"),
    ],
)
def test_unicode_normalised_to_ascii(value, expected):
    assert path_safe(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "🙂",
        "日本語",
        "→",
    ],
)
def test_non_normalisable_dropped(value):
    assert path_safe(value) == ""


def test_empty_string():
    assert path_safe("") == ""


def test_path_traversal_neutralised():
    assert path_safe("../etc/passwd") == "..etcpasswd"
