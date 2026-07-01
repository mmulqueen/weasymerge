from pathlib import Path

import pytest

from weasymerge import load_template
from weasymerge.barcodes import BARCODE_FILTERS

# Symbology -> a value it can encode.
SAMPLE_VALUES = {
    "datamatrix_svg_dataurl": "TKT-12345",
    "qrcode_svg_dataurl": "TKT-12345",
    "aztec_svg_dataurl": "TKT-12345",
    "pdf417_svg_dataurl": "TKT-12345",
    "code128_svg_dataurl": "TKT-12345",
    "ean13_svg_dataurl": "5901234123457",
    "code39_svg_dataurl": "TKT12345",
}


def test_every_filter_has_a_sample() -> None:
    assert set(SAMPLE_VALUES) == set(BARCODE_FILTERS)


@pytest.mark.parametrize("filter_name", sorted(BARCODE_FILTERS))
def test_filter_produces_svg_data_url(filter_name: str) -> None:
    result = BARCODE_FILTERS[filter_name](SAMPLE_VALUES[filter_name])
    assert result.startswith("data:image/svg+xml,")


@pytest.mark.parametrize("filter_name", sorted(BARCODE_FILTERS))
def test_filter_usable_in_img_src(filter_name: str, tmp_path: Path) -> None:
    tpl = tmp_path / "label.html.j2"
    tpl.write_text(f'<img src="{{{{ row.Code | {filter_name} }}}}">')

    rendered = load_template(str(tpl)).render(row={"Code": SAMPLE_VALUES[filter_name]})

    # The filter returns a plain string, but the data URL is fully
    # percent-encoded, so autoescaping passes it through unchanged.
    assert '<img src="data:image/svg+xml,' in rendered
