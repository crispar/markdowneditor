"""Tests for MarkdownConverter — core rendering logic (no Qt needed)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.markdown_converter import MarkdownConverter


class TestMarkdownConverter:
    def setup_method(self):
        self.converter = MarkdownConverter()

    # === Basic markdown rendering (existing functionality) ===

    def test_heading(self):
        html = self.converter.convert("# Hello")
        assert "<h1" in html
        assert "Hello" in html

    def test_heading_levels(self):
        for i in range(1, 7):
            html = self.converter.convert(f"{'#' * i} Level {i}")
            assert f"<h{i}" in html

    def test_bold(self):
        html = self.converter.convert("**bold text**")
        assert "<strong>" in html
        assert "bold text" in html

    def test_italic(self):
        html = self.converter.convert("*italic text*")
        assert "<em>" in html
        assert "italic text" in html

    def test_inline_code(self):
        html = self.converter.convert("`code`")
        assert "<code>" in html
        assert "code" in html

    def test_fenced_code_block(self):
        md = "```python\nprint('hello')\n```"
        html = self.converter.convert(md)
        assert "print" in html

    def test_link(self):
        html = self.converter.convert("[link](http://example.com)")
        assert "<a" in html
        assert "http://example.com" in html

    def test_image(self):
        html = self.converter.convert("![alt](image.png)")
        assert "<img" in html
        assert "image.png" in html

    def test_unordered_list(self):
        md = "- item 1\n- item 2"
        html = self.converter.convert(md)
        assert "<li>" in html
        assert "item 1" in html

    def test_ordered_list(self):
        md = "1. first\n2. second"
        html = self.converter.convert(md)
        assert "<ol>" in html
        assert "first" in html

    def test_blockquote(self):
        html = self.converter.convert("> quoted text")
        assert "<blockquote>" in html

    def test_horizontal_rule(self):
        html = self.converter.convert("---")
        assert "<hr" in html

    def test_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = self.converter.convert(md)
        assert "<table>" in html
        assert "<th>" in html
        assert "<td>" in html

    def test_line_break(self):
        md = "line1\nline2"
        html = self.converter.convert(md)
        assert "<br" in html  # nl2br extension

    def test_empty_input(self):
        html = self.converter.convert("")
        assert html == ""

    # === Mermaid support ===

    def test_mermaid_block_converted_to_div(self):
        md = "```mermaid\ngraph TD;\nA-->B;\n```"
        html = self.converter.convert(md)
        assert 'class="mermaid"' in html
        assert "A-->B" in html

    def test_mermaid_block_not_in_code_tag(self):
        md = "```mermaid\ngraph TD;\n```"
        html = self.converter.convert(md)
        assert "<div" in html

    def test_no_mermaid_when_absent(self):
        html = self.converter.convert("# Title")
        assert "mermaid" not in html

    # === Code highlight CSS ===

    def test_highlight_css_not_empty(self):
        css = MarkdownConverter.get_code_highlight_css()
        assert len(css) > 0
        assert ".highlight" in css

    def test_highlight_css_cached(self):
        css1 = MarkdownConverter.get_code_highlight_css()
        css2 = MarkdownConverter.get_code_highlight_css()
        assert css1 is css2  # same object = cached

    # === Converter reset between calls ===

    def test_converter_reset(self):
        """Ensure converter state resets between calls."""
        self.converter.convert("# First")
        html = self.converter.convert("## Second")
        assert "<h2" in html
        # Should not contain h1 from previous call
        assert "<h1" not in html
