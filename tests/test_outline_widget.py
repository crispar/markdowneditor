"""Tests for OutlineWidget."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from PySide6.QtCore import Qt
from src.outline_widget import OutlineWidget


class TestOutlineWidget:
    @pytest.fixture
    def outline(self, qapp):
        w = OutlineWidget()
        yield w

    def test_empty_text(self, outline):
        outline.update_outline("")
        assert outline.tree.topLevelItemCount() == 0

    def test_single_heading(self, outline):
        outline.update_outline("# Title")
        assert outline.tree.topLevelItemCount() == 1
        assert outline.tree.topLevelItem(0).text(0) == "Title"

    def test_multiple_headings(self, outline):
        text = "# H1\n## H2\n### H3"
        outline.update_outline(text)
        assert outline.tree.topLevelItemCount() == 1  # H1 is top level
        h1 = outline.tree.topLevelItem(0)
        assert h1.childCount() == 1  # H2 under H1
        h2 = h1.child(0)
        assert h2.childCount() == 1  # H3 under H2

    def test_sibling_headings(self, outline):
        text = "# First\n# Second\n# Third"
        outline.update_outline(text)
        assert outline.tree.topLevelItemCount() == 3

    def test_heading_text(self, outline):
        outline.update_outline("## My Section")
        assert outline.tree.topLevelItemCount() == 1
        assert outline.tree.topLevelItem(0).text(0) == "My Section"

    def test_line_number_stored(self, outline):
        text = "# Title\n\nSome text\n\n## Section"
        outline.update_outline(text)
        h1 = outline.tree.topLevelItem(0)
        assert h1.data(0, Qt.UserRole) == 1  # line 1
        h2 = h1.child(0)
        assert h2.data(0, Qt.UserRole) == 5  # line 5

    def test_non_heading_lines_ignored(self, outline):
        text = "regular text\n**bold**\n- list item"
        outline.update_outline(text)
        assert outline.tree.topLevelItemCount() == 0

    def test_mixed_content(self, outline):
        text = "intro\n# Main\nparagraph\n## Sub\nmore text"
        outline.update_outline(text)
        assert outline.tree.topLevelItemCount() == 1
        assert outline.tree.topLevelItem(0).text(0) == "Main"

    def test_update_clears_previous(self, outline):
        outline.update_outline("# First")
        assert outline.tree.topLevelItemCount() == 1
        outline.update_outline("# New")
        assert outline.tree.topLevelItemCount() == 1
        assert outline.tree.topLevelItem(0).text(0) == "New"

    def test_deep_nesting(self, outline):
        text = "# L1\n## L2\n### L3\n#### L4\n##### L5\n###### L6"
        outline.update_outline(text)
        assert outline.tree.topLevelItemCount() == 1
        item = outline.tree.topLevelItem(0)
        for _ in range(5):
            assert item.childCount() == 1
            item = item.child(0)
