import os
import string
import sys
from argparse import ArgumentParser, FileType
from csv import DictReader
from typing import TextIO

import unicodedata
from jinja2 import Template, Environment, FileSystemLoader
from weasyprint import HTML


def load_data(data_file: TextIO):
    return DictReader(data_file)


def load_template(template_path):
    dir_path = os.path.dirname(template_path)
    env = Environment(loader=FileSystemLoader(dir_path), autoescape=True)
    return env.get_template(os.path.basename(template_path))


def merge(template: Template, row: dict[str, str], row_number: int):
    """
    Renders the template and outputs the resulting HTML.
    :param template: Jinja2 template
    :param row: Row data
    :param row_number: Row number, 1st data row is 1.
    :return: HTML string
    """
    return template.render(row=row, row_number=row_number)


def generate_pdf(html: str, output_path: str):
    HTML(string=html).write_pdf(output_path)


PATH_SAFE_CHARS = set(string.ascii_letters + string.digits + " -_.")


def path_safe(value: str):
    # Normalise to nearest ASCII characters
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    # Only allow safe characters
    return "".join(c for c in value.decode() if c in PATH_SAFE_CHARS)


def build_filename(output_path_template: str, row: dict[str, str], row_number: int) -> str:
    safe_row = {k: path_safe(v) for k, v in row.items()}
    return output_path_template.format(row=safe_row, row_number=row_number)


def main():
    parser = ArgumentParser(description="WeasyMerge")
    parser.add_argument("--data", help="The data file (CSV)", type=FileType("r"), default=sys.stdin)
    parser.add_argument("--template", help="The template file (HTML/CSS/Jinja2)", type=str)
    parser.add_argument("--output", help="The output file (PDF), with optional placeholders")
    args = parser.parse_args()

    data = load_data(args.data)
    template = load_template(args.template)

    for i, row in enumerate(data, start=1):
        html = merge(template, row, i)
        output_path = build_filename(args.output, row, i)
        generate_pdf(html, output_path)


if __name__ == "__main__":
    main()
