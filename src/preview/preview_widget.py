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
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent.parent.parent / relative_path


class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.converter = MarkdownConverter()
        self.base_path = Path.cwd()
        self.colors = Theme.get_current()
        self._scroll_position = 0
        self._pending_html = None

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

        # Inject scroll preservation script into HTML
        scroll_script = """
    <script>
        // Save scroll position before content updates
        var __savedScrollY = 0;
        try { __savedScrollY = window.__lastScrollY || 0; } catch(e) {}
        window.addEventListener('load', function() {
            if (__savedScrollY > 0) {
                window.scrollTo(0, __savedScrollY);
            }
        });
        window.addEventListener('scroll', function() {
            window.__lastScrollY = window.scrollY;
        });
    </script>"""

        full_html = self._wrap_html(html_content, include_mermaid=has_mermaid,
                                     extra_scripts=scroll_script)

        if has_mermaid:
            with open(self.temp_html, 'w', encoding='utf-8') as f:
                f.write(full_html)
            self.web_view.setUrl(QUrl.fromLocalFile(str(self.temp_html)))
        else:
            base_url = QUrl.fromLocalFile(str(self.base_path) + "/")
            self.web_view.setHtml(full_html, base_url)

    def scroll_to_ratio(self, ratio: float):
        """Scroll preview to a given ratio (0.0 to 1.0)."""
        js = f"""
        (function() {{
            var maxScroll = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            window.scrollTo(0, maxScroll * {ratio});
        }})();
        """
        self.web_view.page().runJavaScript(js, 0)

    def _wrap_html(self, content: str, include_mermaid: bool = False, extra_scripts: str = "") -> str:
        css = Theme.get_preview_css(self.colors)
        highlight_css = MarkdownConverter.get_code_highlight_css()
        is_dark = self.colors.background == "#1e1e1e"
        mermaid_theme = "dark" if is_dark else "default"

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
    {extra_scripts}
</body>
</html>
"""

    def set_base_path(self, path: str):
        self.base_path = Path(path)

    def set_theme(self, colors: ThemeColors):
        self.colors = colors

    def get_full_html(self, markdown_text: str) -> str:
        html_content = self.converter.convert(markdown_text)
        has_mermaid = 'class="mermaid"' in html_content
        return self._wrap_html(html_content, include_mermaid=has_mermaid)

    def zoom_in(self):
        self.web_view.setZoomFactor(self.web_view.zoomFactor() + 0.1)

    def zoom_out(self):
        factor = self.web_view.zoomFactor()
        if factor > 0.3:
            self.web_view.setZoomFactor(factor - 0.1)

    def zoom_reset(self):
        self.web_view.setZoomFactor(1.0)
