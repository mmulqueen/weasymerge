WeasyMerge is a tool for doing mail merges and other bulk
document generation without having to write your own glue code.
You get the power of [WeasyPrint](https://weasyprint.org/)'s best-in-class PDF 
generation with the ease of writing a [Jinja2](https://jinja.palletsprojects.com/) template
with some HTML/CSS and providing a CSV file of data to merge.

WeasyMerge can generate individual PDFs or batch rows together 
into one or more PDFs. 

## Installation

WeasyMerge is a command-line tool, so the easiest way to install it is with
[pipx](https://pipx.pypa.io/) or [uv](https://docs.astral.sh/uv/):

```bash
pipx install weasymerge
```

```bash
uv tool install weasymerge
```

You can also install it into an existing environment with pip:

```bash
pip install weasymerge
```

WeasyMerge relies on WeasyPrint, which needs some system libraries — see its
[installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).
On Windows this is much smoother under [WSL](https://learn.microsoft.com/windows/wsl/).

## Usage

```bash
weasymerge --data guests.csv --template invite.html.j2 --output "pdfs/Invite {row_number} {row[Name]}.pdf"
```

`pipx run` and `uvx` run WeasyMerge on demand, fetching it if it isn't already
available, so you can invoke it without installing it first:

```bash
pipx run weasymerge --data guests.csv --template invite.html.j2 --output "pdfs/Invite {row_number} {row[Name]}.pdf"
```

```bash
uvx weasymerge --data guests.csv --template invite.html.j2 --output "pdfs/Invite {row_number} {row[Name]}.pdf"
```

The first row of the CSV file is assumed to be the
header row and the header is used as the key for the row 
dictionary.

HTML escaping is on by default in the Jinja2 template.

The row number for the first data row is 1.

WeasyMerge provides "safe" row data to the output filename 
template (ASCII letters, digits, space, underscore, hyphen, 
and dot). Non-ASCII letters are converted to their closest
ASCII equivalent.

## Batch mode (multiple rows per document)

Pass `--rows-per-document=N` to render N rows into a single document,
or `--rows-per-document=all` to render every row into one document.
Use this for label sheets, ID cards, or any layout where the
template needs to see more than one row at a time.

```bash
weasymerge --data seeds.csv --template labels.html.j2 \
  --output "labels-{batch.from_row_number}-{batch.to_row_number}.pdf" \
  --rows-per-document=all
```

In batch mode the template receives a `batch` object instead of
`row` and `row_number`:

- `batch.rows` — list of row dicts in this batch
- `batch.numbered_rows` — list of `(row_number, row)` pairs
- `batch.from_row_number`, `batch.to_row_number` — 1-indexed inclusive range
- `batch.total_rows` — total rows in the source data

The same fields are available in the `--output` template (e.g.
`{batch.from_row_number}`, `{batch.rows[0][Plant]}`). Page breaks
within a single document are the template's responsibility — use
CSS `page-break-after: always` or `break-after: page`.

See `examples/labels/` for a 70×37mm, 24-per-A4 label sheet.

## Barcodes and QR codes

WeasyMerge comes with barcode and QR code Jinja2 filters, powered by
[pyStrich](https://www.method-b.uk/pyStrich/).

Each filter turns a value into a `data:` URL you can drop straight into an
`<img>` tag in your template:

```html
<img src="{{ row['TicketID'] | qrcode_svg_dataurl }}" alt="Ticket QR code">
```

The available filters are:

- `qrcode_svg_dataurl`
- `datamatrix_svg_dataurl`
- `aztec_svg_dataurl`
- `pdf417_svg_dataurl`
- `code128_svg_dataurl`
- `ean13_svg_dataurl`
- `code39_svg_dataurl`

See `examples/tickets/` for A6 event tickets with a QR code and a Code128
barcode.

