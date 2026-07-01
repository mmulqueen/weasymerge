import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def pystrich_required(func: Callable[P, R]) -> Callable[P, R]:
    """Turn a missing optional pyStrich dependency into a clear error.

    The wrapped filter imports its encoder from pyStrich locally; if pyStrich
    isn't installed the import raises, and we re-raise with install guidance
    instead of letting templates fail with a cryptic ``ModuleNotFoundError``.
    Transparent: it preserves the wrapped function's signature and return type.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Barcode filters require pyStrich. "
                "Install it with: pip install weasymerge[barcodes]"
            ) from exc

    return wrapper


# Each filter returns a data: URL string. It's left unescaped only by Jinja2's
# autoescaping — svg_dataurl() percent-encodes its output, so there are no HTML
# special characters to escape, and if that ever regresses autoescaping still
# keeps the template safe.
@pystrich_required
def datamatrix_svg_dataurl(value: object) -> str:
    from pystrich.datamatrix import DataMatrixData, DataMatrixEncoder

    data = DataMatrixData(str(value), auto_encoding=True)
    return DataMatrixEncoder(data).svg_dataurl()


@pystrich_required
def qrcode_svg_dataurl(value: object) -> str:
    from pystrich.qrcode import QRCodeEncoder

    return QRCodeEncoder(str(value)).svg_dataurl()


@pystrich_required
def aztec_svg_dataurl(value: object) -> str:
    from pystrich.aztec import AztecEncoder

    return AztecEncoder(str(value)).svg_dataurl()


@pystrich_required
def pdf417_svg_dataurl(value: object) -> str:
    from pystrich.pdf417 import PDF417Encoder

    return PDF417Encoder(str(value)).svg_dataurl()


@pystrich_required
def code128_svg_dataurl(value: object) -> str:
    from pystrich.code128 import Code128Data, Code128Encoder

    return Code128Encoder(Code128Data(str(value), auto_encoding=True)).svg_dataurl()


@pystrich_required
def ean13_svg_dataurl(value: object) -> str:
    from pystrich.ean13 import EAN13Encoder

    return EAN13Encoder(str(value)).svg_dataurl()


@pystrich_required
def code39_svg_dataurl(value: object) -> str:
    from pystrich.code39 import Code39Encoder

    return Code39Encoder(str(value)).svg_dataurl()


# Always registered so a missing barcodes extra fails with the clear message
# above rather than a cryptic "no filter named ..." error.
BARCODE_FILTERS: dict[str, Callable[[object], str]] = {
    "datamatrix_svg_dataurl": datamatrix_svg_dataurl,
    "qrcode_svg_dataurl": qrcode_svg_dataurl,
    "aztec_svg_dataurl": aztec_svg_dataurl,
    "pdf417_svg_dataurl": pdf417_svg_dataurl,
    "code128_svg_dataurl": code128_svg_dataurl,
    "ean13_svg_dataurl": ean13_svg_dataurl,
    "code39_svg_dataurl": code39_svg_dataurl,
}
