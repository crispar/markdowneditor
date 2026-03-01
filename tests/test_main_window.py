"""Tests for MainWindow — run via subprocess with QWebEngineView mocked.

QWebEngineView in PySide6 6.2.4 crashes in headless environments.
These tests mock QWebEngineView before importing MainWindow.
"""
import sys
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = str(Path(__file__).parent.parent)

# Preamble that mocks QWebEngineView before any import touches it
_MOCK_PREAMBLE = r"""
import sys
sys.path.insert(0, {root!r})

# Mock QWebEngineView BEFORE any import can load it
from unittest.mock import MagicMock
import types

# Create a fake QWebEngineWidgets module
fake_web = types.ModuleType("PySide6.QtWebEngineWidgets")

from PySide6.QtWidgets import QWidget
class FakeWebView(QWidget):
    '''Lightweight stand-in for QWebEngineView.'''
    def setHtml(self, *a, **kw): pass
    def setUrl(self, *a, **kw): pass
    def page(self):
        m = MagicMock()
        m.runJavaScript = lambda *a, **kw: None
        m.toHtml = lambda cb: cb("<html></html>")
        return m
    def url(self):
        from PySide6.QtCore import QUrl
        return QUrl()

fake_web.QWebEngineView = FakeWebView
sys.modules["PySide6.QtWebEngineWidgets"] = fake_web

from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])
from src.main_window import MainWindow
w = MainWindow()
# Reset state
w.editor.set_text("")
w.current_file = None
w._dirty = False
w._saved_text = ""
w._update_title()
"""


def _run_test_script(script: str) -> subprocess.CompletedProcess:
    """Run a test script in a fresh Python process with QWebEngineView mocked."""
    full_script = _MOCK_PREAMBLE.format(root=PROJECT_ROOT) + script
    result = subprocess.run(
        [sys.executable, "-c", full_script],
        capture_output=True, text=True, timeout=15,
        cwd=PROJECT_ROOT
    )
    return result


class TestDirtyFlag:
    def test_initially_clean(self):
        r = _run_test_script('assert w._dirty is False; print("OK")')
        assert "OK" in r.stdout, r.stderr

    def test_dirty_after_edit(self):
        r = _run_test_script("""
w.editor.editor.setPlainText("test")
assert w._dirty is True, f"Expected dirty, got {w._dirty}"
print("OK")
""")
        assert "OK" in r.stdout, r.stderr

    def test_title_has_asterisk_when_dirty(self):
        r = _run_test_script("""
w.editor.editor.setPlainText("test")
assert "*" in w.windowTitle(), f"No * in title: {w.windowTitle()}"
print("OK")
""")
        assert "OK" in r.stdout, r.stderr

    def test_title_no_asterisk_when_clean(self):
        r = _run_test_script("""
assert "*" not in w.windowTitle(), f"Unexpected * in title: {w.windowTitle()}"
print("OK")
""")
        assert "OK" in r.stdout, r.stderr

    def test_dirty_false_when_text_matches_saved(self):
        r = _run_test_script("""
w._saved_text = "same"
w._dirty = False
w.editor.editor.setPlainText("same")
assert w._dirty is False, f"Should not be dirty when text matches saved"
print("OK")
""")
        assert "OK" in r.stdout, r.stderr

    def test_check_unsaved_returns_true_when_clean(self):
        r = _run_test_script("""
w._dirty = False
assert w._check_unsaved_changes() is True
print("OK")
""")
        assert "OK" in r.stdout, r.stderr


class TestFileSaveLoad:
    def test_save_and_load(self):
        r = _run_test_script("""
import tempfile
from pathlib import Path
with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode='w') as f:
    test_path = f.name
w.editor.set_text("# Test Content\\n\\nHello world!")
w._write_file(Path(test_path))
with open(test_path, 'r', encoding='utf-8') as f:
    content = f.read()
assert content == "# Test Content\\n\\nHello world!", f"Content mismatch: {content!r}"
Path(test_path).unlink()
print("OK")
""")
        assert "OK" in r.stdout, r.stderr

    def test_save_clears_dirty(self):
        r = _run_test_script("""
import tempfile
from pathlib import Path
with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode='w') as f:
    test_path = f.name
w.editor.editor.setPlainText("test")
assert w._dirty is True
w.current_file = Path(test_path)
w._save_file()
assert w._dirty is False, f"Expected clean after save, got dirty"
Path(test_path).unlink()
print("OK")
""")
        assert "OK" in r.stdout, r.stderr

    def test_load_file(self):
        r = _run_test_script("""
import tempfile
from pathlib import Path
with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode='w', encoding='utf-8') as f:
    f.write("# Loaded Content")
    test_path = f.name
w._load_file(test_path)
assert w.editor.get_text() == "# Loaded Content"
assert w.current_file == Path(test_path)
assert w._dirty is False
Path(test_path).unlink()
print("OK")
""")
        assert "OK" in r.stdout, r.stderr


class TestRecentFiles:
    def test_add_recent_file(self):
        r = _run_test_script("""
import tempfile
from pathlib import Path
with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
    test_path = f.name
w._add_recent_file(test_path)
assert test_path in w.recent_files
Path(test_path).unlink()
print("OK")
""")
        assert "OK" in r.stdout, r.stderr

    def test_clear_recent_files(self):
        r = _run_test_script("""
w.recent_files = ["file1.md", "file2.md"]
w._clear_recent_files()
assert w.recent_files == []
print("OK")
""")
        assert "OK" in r.stdout, r.stderr


class TestLayoutModes:
    def test_editor_only(self):
        r = _run_test_script("""
w._set_layout("editor")
sizes = w.splitter.sizes()
assert sizes[1] == 0, f"Preview not collapsed: {sizes}"
print("OK")
""")
        assert "OK" in r.stdout, r.stderr

    def test_preview_only(self):
        r = _run_test_script("""
w._set_layout("preview")
sizes = w.splitter.sizes()
assert sizes[0] == 0, f"Editor not collapsed: {sizes}"
print("OK")
""")
        assert "OK" in r.stdout, r.stderr

    def test_split_view(self):
        r = _run_test_script("""
w._set_layout("editor")
w._set_layout("split")
sizes = w.splitter.sizes()
assert all(s > 0 for s in sizes), f"Not both visible: {sizes}"
print("OK")
""")
        assert "OK" in r.stdout, r.stderr


class TestThemeSwitching:
    def test_dark_theme(self):
        r = _run_test_script("""
w._switch_theme("dark")
assert w.editor.highlighter._is_dark is True
print("OK")
""")
        assert "OK" in r.stdout, r.stderr

    def test_light_theme(self):
        r = _run_test_script("""
w._switch_theme("light")
assert w.editor.highlighter._is_dark is False
print("OK")
""")
        assert "OK" in r.stdout, r.stderr


class TestMenus:
    def test_all_menus_exist(self):
        r = _run_test_script("""
titles = [a.text() for a in w.menuBar().actions()]
for menu in ["File", "Edit", "Format", "View", "Help"]:
    assert menu in titles, f"Missing menu: {menu}. Got: {titles}"
print("OK")
""")
        assert "OK" in r.stdout, r.stderr


class TestAutosave:
    def test_autosave_timer_active(self):
        r = _run_test_script("""
assert w._autosave_timer.isActive()
print("OK")
""")
        assert "OK" in r.stdout, r.stderr


class TestMinimumSize:
    def test_min_size(self):
        r = _run_test_script("""
assert w.minimumWidth() == 800, f"Min width: {w.minimumWidth()}"
assert w.minimumHeight() == 500, f"Min height: {w.minimumHeight()}"
print("OK")
""")
        assert "OK" in r.stdout, r.stderr


class TestWordCount:
    def test_word_count_in_statusbar(self):
        r = _run_test_script("""
w.editor.editor.setPlainText("one two three four")
count = w.editor.get_word_count()
assert count == 4, f"Expected 4, got {count}"
print("OK")
""")
        assert "OK" in r.stdout, r.stderr


class TestOutline:
    def test_outline_panel(self):
        r = _run_test_script("""
w.outline.update_outline("# Title\\n## Sub")
assert w.outline.tree.topLevelItemCount() == 1
h1 = w.outline.tree.topLevelItem(0)
assert h1.text(0) == "Title"
assert h1.childCount() == 1
print("OK")
""")
        assert "OK" in r.stdout, r.stderr
