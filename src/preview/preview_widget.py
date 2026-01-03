from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

from src.utils.markdown_converter import MarkdownConverter
from src.styles.theme import Theme, ThemeColors


class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.converter = MarkdownConverter()
        self.base_path = Path.cwd()
        self.colors = Theme.get_current()

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView(self)
        self.web_view.setContextMenuPolicy(Qt.NoContextMenu)
        layout.addWidget(self.web_view)

        # Initial empty content
        self.update_preview("")

    def update_preview(self, markdown_text: str):
        html_content = self.converter.convert(markdown_text)
        full_html = self._wrap_html(html_content)

        # Set base URL for local image loading
        base_url = QUrl.fromLocalFile(str(self.base_path) + "/")
        self.web_view.setHtml(full_html, base_url)

    def _wrap_html(self, content: str) -> str:
        css = Theme.get_preview_css(self.colors)
        highlight_css = MarkdownConverter.get_code_highlight_css()

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        {css}
        {highlight_css}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

    def set_base_path(self, path: str):
        self.base_path = Path(path)

    def set_theme(self, colors: ThemeColors):
        self.colors = colors

    def get_html(self) -> str:
        return self.web_view.page().toHtml(lambda html: html)

    def get_full_html(self, markdown_text: str) -> str:
        html_content = self.converter.convert(markdown_text)
        return self._wrap_html(html_content)
