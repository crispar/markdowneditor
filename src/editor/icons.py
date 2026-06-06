"""Vector toolbar icons drawn at runtime with QPainter.

Why not SVG/PNG files? The PyInstaller spec excludes the Qt SVG image plugin
(to keep the bundle small), so QIcon could not load .svg assets in the frozen
app. Drawing the icons with QPainter keeps them self-contained, crisp at any
size, and recolourable to match the current light/dark theme.
"""
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QPen, QFont, QPolygonF
)

# Logical canvas size the drawing routines are authored against.
_S = 32.0


def _text(p: QPainter, color: QColor, label: str, *, scale: float,
          bold=False, italic=False, strike=False):
    font = QFont("Segoe UI")
    font.setPixelSize(int(_S * scale))
    font.setBold(bold)
    font.setItalic(italic)
    font.setStrikeOut(strike)
    p.setFont(font)
    p.setPen(color)
    p.drawText(QRectF(0, 0, _S, _S), Qt.AlignCenter, label)


def _stroke(p: QPainter, color: QColor, width=2.4):
    pen = QPen(color)
    pen.setWidthF(width)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)


def _lines(p: QPainter, color: QColor, x0, x1, ys, width=2.4):
    _stroke(p, color, width)
    for y in ys:
        p.drawLine(QPointF(x0, y), QPointF(x1, y))


# ----- individual icon painters (canvas is 32x32) -----

def _bold(p, c):       _text(p, c, "B", scale=0.66, bold=True)
def _italic(p, c):     _text(p, c, "I", scale=0.66, italic=True)
def _strike(p, c):     _text(p, c, "S", scale=0.62, strike=True)
def _h1(p, c):         _text(p, c, "H1", scale=0.42, bold=True)
def _h2(p, c):         _text(p, c, "H2", scale=0.42, bold=True)
def _h3(p, c):         _text(p, c, "H3", scale=0.42, bold=True)


def _code(p, c):
    _stroke(p, c)
    p.drawPolyline(QPolygonF([QPointF(13, 10), QPointF(7, 16), QPointF(13, 22)]))
    p.drawPolyline(QPolygonF([QPointF(19, 10), QPointF(25, 16), QPointF(19, 22)]))


def _code_block(p, c):
    _stroke(p, c)
    p.drawRoundedRect(QRectF(5, 7, 22, 18), 3, 3)
    _lines(p, c, 9, 18, [13, 17, 21], width=1.8)


def _quote(p, c):
    # left accent bar + two text lines
    p.setPen(Qt.NoPen)
    p.setBrush(c)
    p.drawRoundedRect(QRectF(7, 9, 3.2, 14), 1.5, 1.5)
    _lines(p, c, 14, 25, [13, 19], width=2.0)


def _bullet_list(p, c):
    p.setPen(Qt.NoPen)
    p.setBrush(c)
    for y in (10, 16, 22):
        p.drawEllipse(QPointF(9, y), 1.7, 1.7)
    _lines(p, c, 14, 26, [10, 16, 22], width=2.0)


def _numbered_list(p, c):
    _lines(p, c, 14, 26, [10, 16, 22], width=2.0)
    f = QFont("Segoe UI")
    f.setPixelSize(8)
    f.setBold(True)
    p.setFont(f)
    p.setPen(c)
    for i, y in enumerate((10, 16, 22), start=1):
        p.drawText(QRectF(4, y - 6, 8, 12), Qt.AlignCenter, str(i))


def _checklist(p, c):
    _stroke(p, c, 2.0)
    p.drawRoundedRect(QRectF(6, 12, 9, 9), 2, 2)
    p.drawPolyline(QPolygonF([QPointF(8, 16.5), QPointF(10, 19), QPointF(13.5, 13.5)]))
    _lines(p, c, 18, 26, [16.5], width=2.0)


def _link(p, c):
    _stroke(p, c, 2.2)
    p.save()
    p.translate(16, 16)
    p.rotate(-45)
    p.drawRoundedRect(QRectF(-11, -4.5, 12, 9), 4.5, 4.5)
    p.drawRoundedRect(QRectF(-1, -4.5, 12, 9), 4.5, 4.5)
    p.restore()


def _image(p, c):
    _stroke(p, c, 2.0)
    p.drawRoundedRect(QRectF(5, 7, 22, 18), 3, 3)
    p.setBrush(c)
    p.drawEllipse(QPointF(12, 13), 2.2, 2.2)
    p.setBrush(Qt.NoBrush)
    # "mountain" baseline
    p.drawPolyline(QPolygonF([
        QPointF(7, 23), QPointF(13, 17), QPointF(17, 21),
        QPointF(21, 15), QPointF(25, 23),
    ]))


def _table(p, c):
    _stroke(p, c, 2.0)
    p.drawRoundedRect(QRectF(5, 7, 22, 18), 2, 2)
    p.drawLine(QPointF(5, 13), QPointF(27, 13))   # header divider
    p.drawLine(QPointF(16, 7), QPointF(16, 25))   # column divider
    p.drawLine(QPointF(5, 19), QPointF(27, 19))   # row divider


def _hr(p, c):
    _stroke(p, c, 2.6)
    p.drawLine(QPointF(6, 16), QPointF(26, 16))


_PAINTERS = {
    "bold": _bold, "italic": _italic, "strikethrough": _strike,
    "h1": _h1, "h2": _h2, "h3": _h3,
    "code": _code, "code_block": _code_block, "quote": _quote,
    "bullet_list": _bullet_list, "numbered_list": _numbered_list,
    "checklist": _checklist, "link": _link, "image": _image,
    "table": _table, "hr": _hr,
}


def make_icon(name: str, color: str = "#333333", size: int = 32) -> QIcon:
    """Return a QIcon for the given logical name, tinted with *color*."""
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.TextAntialiasing, True)
    p.scale(size / _S, size / _S)
    painter_fn = _PAINTERS.get(name)
    if painter_fn:
        painter_fn(p, QColor(color))
    p.end()
    return QIcon(pm)


def icon_names():
    return list(_PAINTERS.keys())


def make_app_pixmap(size: int = 256, bg: str = "#0a66c2", fg: str = "#ffffff") -> QPixmap:
    """A Markdown-style app icon: rounded badge with a white 'M' and down-arrow."""
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing, True)
    s = float(size)

    p.setPen(Qt.NoPen)
    p.setBrush(QColor(bg))
    p.drawRoundedRect(QRectF(s * 0.06, s * 0.16, s * 0.88, s * 0.68), s * 0.13, s * 0.13)

    pen = QPen(QColor(fg))
    pen.setWidthF(s * 0.075)
    pen.setJoinStyle(Qt.RoundJoin)
    pen.setCapStyle(Qt.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)

    # "M"
    p.drawPolyline(QPolygonF([
        QPointF(s * 0.17, s * 0.66), QPointF(s * 0.17, s * 0.34),
        QPointF(s * 0.31, s * 0.52), QPointF(s * 0.45, s * 0.34),
        QPointF(s * 0.45, s * 0.66),
    ]))
    # down arrow
    p.drawLine(QPointF(s * 0.64, s * 0.34), QPointF(s * 0.64, s * 0.63))
    p.drawPolyline(QPolygonF([
        QPointF(s * 0.55, s * 0.52), QPointF(s * 0.64, s * 0.64), QPointF(s * 0.73, s * 0.52),
    ]))
    p.end()
    return pm


def make_app_icon(size: int = 256) -> QIcon:
    return QIcon(make_app_pixmap(size))
