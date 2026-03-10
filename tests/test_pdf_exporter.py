"""Tests for PDFExporter HTML preparation logic with mocked QWebEngineView."""
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = str(Path(__file__).parent.parent)


_MOCK_PREAMBLE = r"""
import sys
sys.path.insert(0, {root!r})

import types

fake_web = types.ModuleType("PySide6.QtWebEngineWidgets")

class FakeWebView:
    def __init__(self, *a, **kw):
        pass
    def setFixedSize(self, *a, **kw):
        pass
    def loadFinished(self, *a, **kw):
        pass

fake_web.QWebEngineView = FakeWebView
sys.modules["PySide6.QtWebEngineWidgets"] = fake_web
"""


def _run_test_script(script: str) -> subprocess.CompletedProcess:
    full_script = _MOCK_PREAMBLE.format(root=PROJECT_ROOT) + script
    return subprocess.run(
        [sys.executable, "-c", full_script],
        capture_output=True,
        text=True,
        timeout=15,
        cwd=PROJECT_ROOT,
    )


class TestPDFExporter:
    def test_prepare_html_includes_mermaid_script_when_present(self):
        r = _run_test_script(
            """
from src.export.pdf_exporter import PDFExporter

exp = PDFExporter()
html, wait = exp._prepare_html(""" + '"""```mermaid\ngraph TD\nA-->B\n```"""' + """)

assert wait is True
assert 'mermaid.min.js' in html
assert 'window.__pdfMermaidReady' in html
print('OK')
"""
        )
        assert "OK" in r.stdout, r.stderr

    def test_prepare_html_skips_mermaid_script_when_absent(self):
        r = _run_test_script(
            """
from src.export.pdf_exporter import PDFExporter

exp = PDFExporter()
html, wait = exp._prepare_html('# Title')

assert wait is False
assert 'mermaid.min.js' not in html
assert 'window.__pdfMermaidReady = true' in html
print('OK')
"""
        )
        assert "OK" in r.stdout, r.stderr

    def test_prepare_html_handles_missing_mermaid_asset(self):
        r = _run_test_script(
            """
from pathlib import Path
from src.export.pdf_exporter import PDFExporter

exp = PDFExporter()
exp._get_resource_path = lambda rel: Path('not_found_mermaid.min.js')
html, wait = exp._prepare_html(""" + '"""```mermaid\ngraph TD\nA-->B\n```"""' + """)

assert wait is False
assert 'mermaid.min.js' not in html
assert 'window.__pdfMermaidReady = true' in html
print('OK')
"""
        )
        assert "OK" in r.stdout, r.stderr
