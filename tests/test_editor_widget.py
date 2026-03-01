"""Tests for EditorWidget — editing features requiring Qt."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from PySide6.QtGui import QTextCursor


class TestEditorBasicOperations:
    """Test basic editor operations (existing functionality)."""

    def test_set_and_get_text(self, editor_widget):
        editor_widget.set_text("hello world")
        assert editor_widget.get_text() == "hello world"

    def test_empty_text(self, editor_widget):
        editor_widget.set_text("")
        assert editor_widget.get_text() == ""

    def test_character_count(self, editor_widget):
        editor_widget.set_text("hello")
        assert editor_widget.get_character_count() == 5

    def test_character_count_empty(self, editor_widget):
        editor_widget.set_text("")
        assert editor_widget.get_character_count() == 0

    def test_cursor_position_initial(self, editor_widget):
        editor_widget.set_text("hello")
        line, col = editor_widget.get_cursor_position()
        assert line >= 1
        assert col >= 1

    def test_cursor_position_multiline(self, editor_widget):
        editor_widget.set_text("line1\nline2\nline3")
        cursor = editor_widget.editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        editor_widget.editor.setTextCursor(cursor)
        line, col = editor_widget.get_cursor_position()
        assert line == 3

    def test_set_base_path(self, editor_widget):
        editor_widget.set_base_path("/tmp/test")
        assert editor_widget.image_handler.base_path == Path("/tmp/test")


class TestWordCount:
    """Test new word count feature."""

    def test_word_count_basic(self, editor_widget):
        editor_widget.set_text("one two three")
        assert editor_widget.get_word_count() == 3

    def test_word_count_empty(self, editor_widget):
        editor_widget.set_text("")
        assert editor_widget.get_word_count() == 0

    def test_word_count_whitespace_only(self, editor_widget):
        editor_widget.set_text("   \n\n   ")
        assert editor_widget.get_word_count() == 0

    def test_word_count_multiline(self, editor_widget):
        editor_widget.set_text("hello\nworld\nfoo bar")
        assert editor_widget.get_word_count() == 4

    def test_word_count_korean(self, editor_widget):
        editor_widget.set_text("hello world")
        assert editor_widget.get_word_count() == 2


class TestFormatToggle:
    """Test format wrapping and toggling (new feature)."""

    def _select_all(self, editor_widget):
        cursor = editor_widget.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        editor_widget.editor.setTextCursor(cursor)

    def _select_range(self, editor_widget, start, end):
        cursor = editor_widget.editor.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        editor_widget.editor.setTextCursor(cursor)

    def test_bold_wrap(self, editor_widget):
        editor_widget.set_text("hello")
        self._select_all(editor_widget)
        editor_widget._toggle_wrap("**", "**")
        assert editor_widget.get_text() == "**hello**"

    def test_bold_unwrap(self, editor_widget):
        editor_widget.set_text("**hello**")
        self._select_all(editor_widget)
        editor_widget._toggle_wrap("**", "**")
        assert editor_widget.get_text() == "hello"

    def test_italic_wrap(self, editor_widget):
        editor_widget.set_text("hello")
        self._select_all(editor_widget)
        editor_widget._toggle_wrap("*", "*")
        assert editor_widget.get_text() == "*hello*"

    def test_italic_unwrap(self, editor_widget):
        editor_widget.set_text("*hello*")
        self._select_all(editor_widget)
        editor_widget._toggle_wrap("*", "*")
        assert editor_widget.get_text() == "hello"

    def test_code_wrap(self, editor_widget):
        editor_widget.set_text("code")
        self._select_all(editor_widget)
        editor_widget._toggle_wrap("`", "`")
        assert editor_widget.get_text() == "`code`"

    def test_strikethrough_wrap(self, editor_widget):
        editor_widget.set_text("deleted")
        self._select_all(editor_widget)
        editor_widget._toggle_wrap("~~", "~~")
        assert editor_widget.get_text() == "~~deleted~~"

    def test_no_selection_inserts_markers(self, editor_widget):
        editor_widget.set_text("")
        editor_widget._toggle_wrap("**", "**")
        assert editor_widget.get_text() == "****"


class TestHeadingToggle:
    """Test heading toggle/switch (new feature)."""

    def _move_to_start(self, editor_widget):
        cursor = editor_widget.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor_widget.editor.setTextCursor(cursor)

    def test_add_heading(self, editor_widget):
        editor_widget.set_text("Hello")
        self._move_to_start(editor_widget)
        editor_widget._toggle_heading("# ")
        assert editor_widget.get_text() == "# Hello"

    def test_remove_same_heading(self, editor_widget):
        editor_widget.set_text("# Hello")
        self._move_to_start(editor_widget)
        editor_widget._toggle_heading("# ")
        assert editor_widget.get_text() == "Hello"

    def test_switch_heading_level(self, editor_widget):
        editor_widget.set_text("# Hello")
        self._move_to_start(editor_widget)
        editor_widget._toggle_heading("## ")
        assert editor_widget.get_text() == "## Hello"

    def test_switch_h2_to_h3(self, editor_widget):
        editor_widget.set_text("## Hello")
        self._move_to_start(editor_widget)
        editor_widget._toggle_heading("### ")
        assert editor_widget.get_text() == "### Hello"


class TestMultiLinePrefix:
    """Test multi-line prefix application (new feature)."""

    def _select_all(self, editor_widget):
        cursor = editor_widget.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        editor_widget.editor.setTextCursor(cursor)

    def test_bullet_list_multiline(self, editor_widget):
        editor_widget.set_text("a\nb\nc")
        self._select_all(editor_widget)
        editor_widget._prefix_lines("- ")
        assert editor_widget.get_text() == "- a\n- b\n- c"

    def test_quote_multiline(self, editor_widget):
        editor_widget.set_text("line1\nline2")
        self._select_all(editor_widget)
        editor_widget._prefix_lines("> ")
        assert editor_widget.get_text() == "> line1\n> line2"

    def test_single_line(self, editor_widget):
        editor_widget.set_text("hello")
        # No selection, just cursor on line
        cursor = editor_widget.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor_widget.editor.setTextCursor(cursor)
        editor_widget._prefix_lines("- ")
        assert editor_widget.get_text() == "- hello"

    def test_numbered_list(self, editor_widget):
        editor_widget.set_text("a\nb")
        self._select_all(editor_widget)
        editor_widget._prefix_lines("1. ")
        assert editor_widget.get_text() == "1. a\n1. b"

    def test_checklist(self, editor_widget):
        editor_widget.set_text("task1\ntask2")
        self._select_all(editor_widget)
        editor_widget._prefix_lines("- [ ] ")
        assert editor_widget.get_text() == "- [ ] task1\n- [ ] task2"


class TestTableInsert:
    """Test table template insertion (new feature)."""

    def test_insert_table(self, editor_widget):
        editor_widget.set_text("")
        editor_widget._insert_table()
        text = editor_widget.get_text()
        assert "Header 1" in text
        assert "Header 2" in text
        assert "Header 3" in text
        assert "---" in text
        assert "Cell 1" in text


class TestZoom:
    """Test zoom functionality (new feature)."""

    def test_zoom_in(self, editor_widget):
        initial = editor_widget._zoom_level
        editor_widget.zoom_in()
        assert editor_widget._zoom_level == initial + 1

    def test_zoom_out(self, editor_widget):
        editor_widget.zoom_in()
        editor_widget.zoom_in()
        editor_widget.zoom_out()
        assert editor_widget._zoom_level == 1

    def test_zoom_reset(self, editor_widget):
        editor_widget.zoom_in()
        editor_widget.zoom_in()
        editor_widget.zoom_reset()
        assert editor_widget._zoom_level == 0

    def test_zoom_out_limit(self, editor_widget):
        for _ in range(20):
            editor_widget.zoom_out()
        assert editor_widget._zoom_level >= -5


class TestGoToLine:
    """Test go to line functionality (new feature for outline)."""

    def test_go_to_line(self, editor_widget):
        editor_widget.set_text("line1\nline2\nline3\nline4\nline5")
        editor_widget.go_to_line(3)
        line, _ = editor_widget.get_cursor_position()
        assert line == 3

    def test_go_to_first_line(self, editor_widget):
        editor_widget.set_text("first\nsecond")
        editor_widget.go_to_line(1)
        line, _ = editor_widget.get_cursor_position()
        assert line == 1
