import sys
import shutil
import tempfile
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt

from src.utils.markdown_converter import MarkdownConverter
from src.styles.theme import Theme, ThemeColors


def get_resource_path(relative_path: str) -> Path:
    """Get path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS) / relative_path
    # Running in development
    return Path(__file__).parent.parent.parent / relative_path


class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.converter = MarkdownConverter()
        self.base_path = Path.cwd()
        self.colors = Theme.get_current()

        # Create temp directory for mermaid rendering
        self.temp_dir = Path(tempfile.mkdtemp())
        self.temp_html = self.temp_dir / "preview.html"

        # Copy mermaid.js to temp directory
        self._setup_mermaid()

        self._setup_ui()

    def _setup_mermaid(self):
        """Copy mermaid.js to temp directory for local loading"""
        mermaid_src = get_resource_path("resources/js/mermaid.min.js")
        self.mermaid_js_path = self.temp_dir / "mermaid.min.js"
        if mermaid_src.exists():
            shutil.copy(mermaid_src, self.mermaid_js_path)

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
        has_mermaid = 'class="mermaid"' in html_content
        full_html = self._wrap_html(html_content, include_mermaid=has_mermaid)

        # Always use setHtml for faster rendering and to avoid disk I/O
        # Base URL is set to user's file path so relative images work
        base_url = QUrl.fromLocalFile(str(self.base_path) + "/")
        self.web_view.setHtml(full_html, base_url)

    def _wrap_html(self, content: str, include_mermaid: bool = False) -> str:
        css = Theme.get_preview_css(self.colors)
        highlight_css = MarkdownConverter.get_code_highlight_css()
        is_dark = self.colors.background == "#1e1e1e"
        mermaid_theme = "dark" if is_dark else "default"

        # Only include mermaid.js when needed (local file)
        if include_mermaid and self.mermaid_js_path.exists():
            # Use absolute path for mermaid script to allow loading from different base URL
            script_url = QUrl.fromLocalFile(str(self.mermaid_js_path)).toString()
            mermaid_head = f'<script src="{script_url}"></script>'
            mermaid_init = f"""
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: '{mermaid_theme}'
        }});
    </script>"""
        else:
            mermaid_head = ""
            mermaid_init = ""

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {mermaid_head}
    <style>
        {css}
        {highlight_css}
        .mermaid {{
            text-align: center;
            margin: 1em 0;
        }}
    </style>
</head>
<body>
    {content}
    {mermaid_init}
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
        has_mermaid = 'class="mermaid"' in html_content
        return self._wrap_html(html_content, include_mermaid=has_mermaid)
