"""Tests for FindReplaceWidget."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from PySide6.QtWidgets import QPlainTextEdit
from src.editor.find_replace import FindReplaceWidget


class TestFindReplace:
    @pytest.fixture
    def setup(self, qapp):
        editor = QPlainTextEdit()
        editor.setPlainText("hello world hello foo hello")
        widget = FindReplaceWidget(editor)
        return editor, widget

    def test_show_find(self, setup):
        _, widget = setup
        widget.show_find()
        assert widget.replace_row_widget.isHidden()

    def test_show_replace(self, setup):
        _, widget = setup
        widget.show_replace()
        assert widget.replace_row_widget.isVisible()

    def test_count_matches(self, setup):
        _, widget = setup
        widget._count_matches("hello")
        assert "3" in widget.match_label.text()

    def test_count_matches_case_insensitive(self, setup):
        editor, widget = setup
        editor.setPlainText("Hello hello HELLO")
        widget.case_check.setChecked(False)
        widget._count_matches("hello")
        assert "3" in widget.match_label.text()

    def test_count_matches_case_sensitive(self, setup):
        editor, widget = setup
        editor.setPlainText("Hello hello HELLO")
        widget.case_check.setChecked(True)
        widget._count_matches("hello")
        assert "1" in widget.match_label.text()

    def test_find_next(self, setup):
        editor, widget = setup
        widget.find_input.setText("hello")
        widget.find_next()
        cursor = editor.textCursor()
        assert cursor.hasSelection()
        assert cursor.selectedText() == "hello"

    def test_replace_all(self, setup):
        editor, widget = setup
        widget.find_input.setText("hello")
        widget.replace_input.setText("HI")
        widget.replace_all()
        assert "hello" not in editor.toPlainText()
        assert editor.toPlainText().count("HI") == 3

    def test_close_find(self, setup):
        _, widget = setup
        widget.show_find()
        widget.close_find()
        assert widget.isHidden()

    def test_empty_find(self, setup):
        _, widget = setup
        widget.find_input.setText("")
        widget.find_next()  # should not crash
        widget.replace_all()  # should not crash
