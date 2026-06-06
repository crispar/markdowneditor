"""QPlainTextEdit subclass that adds a line-number gutter.

This is the canonical Qt "Code Editor" pattern (a sibling widget painted in the
editor's left viewport margin). It is a drop-in replacement for QPlainTextEdit:
the existing event filter, current-line highlight and facade methods on
EditorWidget keep working unchanged.
"""
from PySide6.QtWidgets import QPlainTextEdit, QWidget
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QColor, QPainter


class _LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._editor.paint_line_numbers(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._line_area = _LineNumberArea(self)
        self._num_color = QColor("#9aa0a6")
        self._area_bg = QColor("#f0f2f4")

        self.blockCountChanged.connect(self._update_margin)
        self.updateRequest.connect(self._on_update_request)
        self.cursorPositionChanged.connect(self._line_area.update)
        self._update_margin()

    # ----- width / geometry -----
    def line_number_area_width(self) -> int:
        digits = max(2, len(str(max(1, self.blockCount()))))
        return 14 + self.fontMetrics().horizontalAdvance('9') * digits

    def _update_margin(self, *_):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _on_update_request(self, rect, dy):
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_margin()

    def _reposition_area(self):
        cr = self.contentsRect()
        self._line_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_area()

    def setFont(self, font):
        super().setFont(font)
        self._update_margin()
        self._reposition_area()
        self._line_area.update()

    # ----- theming -----
    def set_line_number_colors(self, text_color, bg_color):
        self._num_color = QColor(text_color)
        self._area_bg = QColor(bg_color)
        self._line_area.update()

    # ----- painting -----
    def paint_line_numbers(self, event):
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), self._area_bg)
        painter.setFont(self.font())

        dim = QColor(self._num_color)
        dim.setAlpha(130)
        line_h = self.fontMetrics().height()
        width = self._line_area.width() - 8
        current = self.textCursor().blockNumber()

        block = self.firstVisibleBlock()
        block_num = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(self._num_color if block_num == current else dim)
                painter.drawText(0, int(top), width, line_h,
                                 Qt.AlignRight | Qt.AlignVCenter, str(block_num + 1))
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_num += 1
        painter.end()
