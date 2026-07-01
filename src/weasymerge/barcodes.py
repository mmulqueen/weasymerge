from collections.abc import Callable

# Encoders are imported lazily inside each filter so that importing this module
# (and starting the CLI for a plain mail merge) doesn't pull in pyStrich.


# Each filter returns a data: URL string. It's left unescaped only by Jinja2's
# autoescaping — svg_dataurl() percent-encodes its output, so there are no HTML
# special characters to escape, and if that ever regresses autoescaping still
# keeps the template safe.
def datamatrix_svg_dataurl(value: object) -> str:
    from pystrich.datamatrix import DataMatrixData, DataMatrixEncoder

    data = DataMatrixData(str(value), auto_encoding=True)
    return DataMatrixEncoder(data).svg_dataurl()


def qrcode_svg_dataurl(value: object) -> str:
    from pystrich.qrcode import QRCodeEncoder

    return QRCodeEncoder(str(value)).svg_dataurl()


def aztec_svg_dataurl(value: object) -> str:
    from pystrich.aztec import AztecEncoder

    return AztecEncoder(str(value)).svg_dataurl()


def pdf417_svg_dataurl(value: object) -> str:
    from pystrich.pdf417 import PDF417Encoder

    return PDF417Encoder(str(value)).svg_dataurl()


def code128_svg_dataurl(value: object) -> str:
    from pystrich.code128 import Code128Data, Code128Encoder

    return Code128Encoder(Code128Data(str(value), auto_encoding=True)).svg_dataurl()


def ean13_svg_dataurl(value: object) -> str:
    from pystrich.ean13 import EAN13Encoder

    return EAN13Encoder(str(value)).svg_dataurl()


def code39_svg_dataurl(value: object) -> str:
    from pystrich.code39 import Code39Encoder

    return Code39Encoder(str(value)).svg_dataurl()


BARCODE_FILTERS: dict[str, Callable[[object], str]] = {
    "datamatrix_svg_dataurl": datamatrix_svg_dataurl,
    "qrcode_svg_dataurl": qrcode_svg_dataurl,
    "aztec_svg_dataurl": aztec_svg_dataurl,
    "pdf417_svg_dataurl": pdf417_svg_dataurl,
    "code128_svg_dataurl": code128_svg_dataurl,
    "ean13_svg_dataurl": ean13_svg_dataurl,
    "code39_svg_dataurl": code39_svg_dataurl,
}
