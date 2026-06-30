import os
import string
import sys
import unicodedata
from argparse import ArgumentParser, ArgumentTypeError, FileType
from csv import DictReader
from dataclasses import dataclass
from typing import TextIO

from jinja2 import Environment, FileSystemLoader, Template
from weasyprint import HTML


@dataclass(frozen=True)
class Batch:
    rows: list[dict[str, str]]
    from_row_number: int
    to_row_number: int
    total_rows: int

    @property
    def numbered_rows(self) -> list[tuple[int, dict[str, str]]]:
        """Row pairs ``(row_number, row)`` starting at ``from_row_number``."""
        return list(enumerate(self.rows, start=self.from_row_number))


def load_data(data_file: TextIO) -> DictReader[str]:
    return DictReader(data_file)


def load_template(template_path: str) -> Template:
    dir_path = os.path.dirname(template_path)
    env = Environment(loader=FileSystemLoader(dir_path), autoescape=True)
    return env.get_template(os.path.basename(template_path))


def merge(template: Template, row: dict[str, str], row_number: int) -> str:
    """Render the template with the row data; row_number is 1-indexed."""
    return template.render(row=row, row_number=row_number)


def merge_batch(template: Template, batch: Batch) -> str:
    return template.render(batch=batch)


def generate_pdf(html: str, output_path: str) -> None:
    HTML(string=html).write_pdf(output_path)


PATH_SAFE_CHARS = set(string.ascii_letters + string.digits + " -_.")


def path_safe(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    )
    return "".join(c for c in ascii_value if c in PATH_SAFE_CHARS)


def _sanitise_row(row: dict[str, str]) -> dict[str, str]:
    return {k: path_safe(v) for k, v in row.items()}


def build_filename(
    output_path_template: str, row: dict[str, str], row_number: int
) -> str:
    return output_path_template.format(row=_sanitise_row(row), row_number=row_number)


def build_batch_filename(output_path_template: str, batch: Batch) -> str:
    safe_batch = Batch(
        rows=[_sanitise_row(r) for r in batch.rows],
        from_row_number=batch.from_row_number,
        to_row_number=batch.to_row_number,
        total_rows=batch.total_rows,
    )
    return output_path_template.format(batch=safe_batch)


def _parse_rows_per_document(value: str) -> int | str:
    if value == "all":
        return value
    try:
        n = int(value)
    except ValueError:
        raise ArgumentTypeError("must be a positive integer or 'all'") from None
    if n < 1:
        raise ArgumentTypeError("must be a positive integer or 'all'")
    return n


def main() -> None:
    parser = ArgumentParser(description="WeasyMerge")
    parser.add_argument(
        "--data", help="The data file (CSV)", type=FileType("r"), default=sys.stdin
    )
    parser.add_argument(
        "--template",
        help="The template file (HTML/CSS/Jinja2)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--output",
        help="The output file (PDF), with optional placeholders",
        required=True,
    )
    parser.add_argument(
        "--rows-per-document",
        type=_parse_rows_per_document,
        default=None,
        help=(
            "Batch N rows into each document (or 'all' for one document). "
            "Omit for the default one-document-per-row mode."
        ),
    )
    args = parser.parse_args()

    template = load_template(args.template)

    if args.rows_per_document is None:
        for i, row in enumerate(load_data(args.data), start=1):
            html = merge(template, row, i)
            generate_pdf(html, build_filename(args.output, row, i))
    else:
        rows = list(load_data(args.data))
        total = len(rows)
        n = total if args.rows_per_document == "all" else args.rows_per_document
        for start in range(0, total, max(n, 1)):
            chunk = rows[start : start + n]
            batch = Batch(
                rows=chunk,
                from_row_number=start + 1,
                to_row_number=start + len(chunk),
                total_rows=total,
            )
            html = merge_batch(template, batch)
            generate_pdf(html, build_batch_filename(args.output, batch))


if __name__ == "__main__":
    main()
