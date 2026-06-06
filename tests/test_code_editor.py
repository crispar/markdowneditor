"""Tests for the CodeEditor line-number gutter."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.editor.code_editor import CodeEditor


class TestCodeEditor:
    @pytest.fixture
    def ed(self, qapp):
        w = CodeEditor()
        yield w

    def test_gutter_reserves_left_margin(self, ed):
        # The line-number area must occupy the left viewport margin.
        assert ed.viewportMargins().left() > 0

    def test_width_grows_with_line_count(self, ed):
        narrow = ed.line_number_area_width()
        ed.setPlainText("\n".join(str(i) for i in range(1000)))
        wide = ed.line_number_area_width()
        assert wide > narrow

    def test_set_colors_does_not_crash(self, ed):
        ed.set_line_number_colors("#ffffff", "#000000")
        ed.setPlainText("a\nb\nc")
        # force a repaint of the gutter
        ed._line_area.repaint()
