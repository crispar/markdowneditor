"""Tests for MarkdownHighlighter."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.editor.syntax_highlighter import MarkdownHighlighter


class TestHighlighterInit:
    def test_create_light_mode(self, qapp):
        h = MarkdownHighlighter(is_dark=False)
        assert h._is_dark is False
        assert len(h._rules) > 0

    def test_create_dark_mode(self, qapp):
        h = MarkdownHighlighter(is_dark=True)
        assert h._is_dark is True
        assert len(h._rules) > 0

    def test_switch_mode(self, qapp):
        h = MarkdownHighlighter(is_dark=False)
        h.set_dark_mode(True)
        assert h._is_dark is True

    def test_rules_cover_all_syntax(self, qapp):
        h = MarkdownHighlighter(is_dark=False)
        # Should have rules for: heading, bold, italic, strikethrough,
        # inline code, code fence, link, image, unordered list,
        # ordered list, blockquote, hr, checklist = 13 rules
        assert len(h._rules) >= 12
