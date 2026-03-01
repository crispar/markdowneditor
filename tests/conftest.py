"""Shared fixtures for all tests."""
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication

# Single QApplication instance for all tests
_app = None


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance once for the entire test session."""
    global _app
    if _app is None:
        _app = QApplication.instance() or QApplication([])
    return _app


@pytest.fixture(scope="session")
def main_window(qapp):
    """Create a single MainWindow for the entire test session.
    QWebEngineView crashes with multiple instances in test environments.
    Tests must not rely on fresh state - reset what they need."""
    from src.main_window import MainWindow
    window = MainWindow()
    yield window
    window.close()


@pytest.fixture
def editor_widget(qapp):
    """Create an isolated EditorWidget."""
    from src.editor.editor_widget import EditorWidget
    widget = EditorWidget()
    yield widget


@pytest.fixture
def preview_widget(qapp):
    """Create an isolated PreviewWidget."""
    from src.preview.preview_widget import PreviewWidget
    widget = PreviewWidget()
    yield widget
