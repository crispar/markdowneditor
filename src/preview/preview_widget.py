import sys
import shutil
import tempfile
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QUrl, Qt, QTimer

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
        self.base_path = Path.cwd()
        self.colors = Theme.get_current()
        self._is_initialized = False
        self._pending_text = None
        self.web_view = None
        self.converter = None

        self._setup_ui_placeholder()

        # Defer heavy initialization
        QTimer.singleShot(10, self._init_webview)

    def _setup_ui_placeholder(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.loading_label = QLabel("Initializing preview...", self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.loading_label)

    def _init_webview(self):
        from PySide6.QtWebEngineWidgets import QWebEngineView

        # Initialize converter
        self.converter = MarkdownConverter()

        # Create temp directory for mermaid rendering
        self.temp_dir = Path(tempfile.mkdtemp())
        self.temp_html = self.temp_dir / "preview.html"

        # Copy mermaid.js to temp directory
        self._setup_mermaid()

        # Replace placeholder with WebEngineView
        self.web_view = QWebEngineView(self)
        self.web_view.setContextMenuPolicy(Qt.NoContextMenu)

        self.layout.removeWidget(self.loading_label)
        self.loading_label.deleteLater()
        self.layout.addWidget(self.web_view)

        self._is_initialized = True

        # Process any pending update
        if self._pending_text is not None:
            self.update_preview(self._pending_text)
            self._pending_text = None
        else:
            self.update_preview("")

    def _setup_mermaid(self):
        """Copy mermaid.js to temp directory for local loading"""
        mermaid_src = get_resource_path("resources/js/mermaid.min.js")
        self.mermaid_js_path = self.temp_dir / "mermaid.min.js"
        if mermaid_src.exists():
            shutil.copy(mermaid_src, self.mermaid_js_path)

    def update_preview(self, markdown_text: str):
        if not self._is_initialized:
            self._pending_text = markdown_text
            return

        html_content = self.converter.convert(markdown_text)
        has_mermaid = 'class="mermaid"' in html_content
        full_html = self._wrap_html(html_content, include_mermaid=has_mermaid)

        if has_mermaid:
            # Save to temp file and load via file URL (allows external scripts)
            with open(self.temp_html, 'w', encoding='utf-8') as f:
                f.write(full_html)
            self.web_view.setUrl(QUrl.fromLocalFile(str(self.temp_html)))
        else:
            # Use setHtml for faster rendering when no mermaid
            base_url = QUrl.fromLocalFile(str(self.base_path) + "/")
            self.web_view.setHtml(full_html, base_url)

    def _wrap_html(self, content: str, include_mermaid: bool = False) -> str:
        css = Theme.get_preview_css(self.colors)
        highlight_css = MarkdownConverter.get_code_highlight_css()
        is_dark = self.colors.background == "#1e1e1e"
        mermaid_theme = "dark" if is_dark else "default"

        # Only include mermaid.js when needed (local file)
        if include_mermaid and self.mermaid_js_path.exists():
            mermaid_head = f'<script src="mermaid.min.js"></script>'
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
