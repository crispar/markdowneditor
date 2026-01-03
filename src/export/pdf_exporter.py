from pathlib import Path
from PySide6.QtCore import QObject, Signal, QMarginsF, QUrl, QEventLoop
from PySide6.QtGui import QPageLayout, QPageSize
from PySide6.QtWebEngineWidgets import QWebEngineView

from src.utils.markdown_converter import MarkdownConverter
from src.styles.theme import Theme


class PDFExportError(Exception):
    pass


class PDFExporter(QObject):
    export_finished = Signal(bool, str)  # success, message

    def __init__(self, base_path: str = None, parent=None):
        super().__init__(parent)
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.converter = MarkdownConverter()
        self._web_view = None
        self._output_path = None
        self._event_loop = None

    def export(self, markdown_text: str, output_path: str) -> bool:
        self._output_path = output_path

        # Create hidden web view for rendering
        self._web_view = QWebEngineView()
        self._web_view.setFixedSize(800, 600)

        # Prepare HTML content
        html_content = self._prepare_html(markdown_text)
        base_url = QUrl.fromLocalFile(str(self.base_path) + "/")

        # Connect load finished signal
        self._web_view.loadFinished.connect(self._on_load_finished)

        # Load HTML
        self._web_view.setHtml(html_content, base_url)

        # Wait for export to complete using event loop
        self._event_loop = QEventLoop()
        self._export_success = False
        self._export_error = None

        self._event_loop.exec()

        # Cleanup
        self._web_view.deleteLater()
        self._web_view = None

        if not self._export_success:
            raise PDFExportError(self._export_error or "PDF export failed")

        return True

    def _on_load_finished(self, ok: bool):
        if not ok:
            self._export_error = "Failed to render HTML content"
            self._export_success = False
            if self._event_loop:
                self._event_loop.quit()
            return

        # Setup page layout for A4
        page_layout = QPageLayout(
            QPageSize(QPageSize.A4),
            QPageLayout.Portrait,
            QMarginsF(15, 15, 15, 15)  # margins in mm
        )

        # Export to PDF
        self._web_view.page().printToPdf(
            self._output_path,
            page_layout
        )

        # Connect to PDF printing finished
        self._web_view.page().pdfPrintingFinished.connect(self._on_pdf_finished)

    def _on_pdf_finished(self, file_path: str, success: bool):
        self._export_success = success
        if not success:
            self._export_error = "Failed to write PDF file"
        if self._event_loop:
            self._event_loop.quit()

    def _prepare_html(self, markdown_text: str) -> str:
        html_content = self.converter.convert(markdown_text)
        css = self._get_pdf_css()
        highlight_css = MarkdownConverter.get_code_highlight_css()

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {css}
        {highlight_css}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

    def _get_pdf_css(self) -> str:
        colors = Theme.LIGHT

        return f"""
@media print {{
    body {{
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}
}}

body {{
    font-family: 'Malgun Gothic', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: {colors.foreground};
    background-color: white;
    padding: 0;
    margin: 0;
}}

h1, h2, h3, h4, h5, h6 {{
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
    page-break-after: avoid;
}}

h1 {{
    font-size: 24pt;
    border-bottom: 1px solid {colors.border};
    padding-bottom: 8px;
}}

h2 {{
    font-size: 18pt;
    border-bottom: 1px solid {colors.border};
    padding-bottom: 6px;
}}

h3 {{ font-size: 14pt; }}
h4 {{ font-size: 12pt; }}

p {{
    margin-top: 0;
    margin-bottom: 16px;
}}

a {{
    color: {colors.accent};
    text-decoration: none;
}}

code {{
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.9em;
    background-color: #f6f8fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
}}

pre {{
    background-color: #f6f8fa;
    border: 1px solid {colors.border};
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    page-break-inside: avoid;
}}

pre code {{
    background-color: transparent;
    padding: 0;
    font-size: 9pt;
    line-height: 1.45;
}}

blockquote {{
    margin: 0 0 16px 0;
    padding: 0 1em;
    color: #6a737d;
    border-left: 4px solid {colors.accent};
}}

ul, ol {{
    padding-left: 2em;
    margin-top: 0;
    margin-bottom: 16px;
}}

li {{
    margin-bottom: 4px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
    page-break-inside: avoid;
}}

th, td {{
    border: 1px solid {colors.border};
    padding: 8px 12px;
    text-align: left;
}}

th {{
    background-color: #f6f8fa;
    font-weight: 600;
}}

img {{
    max-width: 100%;
    height: auto;
    page-break-inside: avoid;
}}

hr {{
    border: none;
    border-top: 1px solid {colors.border};
    margin: 24px 0;
}}
"""

    def set_base_path(self, path: str):
        self.base_path = Path(path)
