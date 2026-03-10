import re

import markdown
from pygments.formatters import HtmlFormatter


class MarkdownConverter:
    # Pattern to match mermaid code blocks
    MERMAID_PATTERN = re.compile(
        r'```mermaid\s*\n(.*?)```',
        re.DOTALL
    )
    FLOW_BRACKET_LABEL_PATTERN = re.compile(r'(?<!\[)\[([^\[\]\n]+)\](?!\])')
    QUADRANT_AXIS_PATTERN = re.compile(
        r'^(\s*)(x-axis|y-axis|quadrant-[1-4])(\s+)(.*)$',
        re.IGNORECASE,
    )
    QUADRANT_POINT_PATTERN = re.compile(
        r'^(\s*)(.+?)(\s*:\s*\[\s*(?:1|0(?:\.\d+)?)\s*,\s*(?:1|0(?:\.\d+)?)\s*\].*)$'
    )

    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'fenced_code',
                'codehilite',
                'tables',
                'toc',
                'nl2br',
                'sane_lists',
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'linenums': False,
                    'guess_lang': True,
                }
            }
        )

    def convert(self, text: str) -> str:
        # Extract mermaid blocks before markdown processing
        mermaid_blocks = []

        def mermaid_placeholder(match):
            content = match.group(1).strip()
            content = self._normalize_mermaid(content)
            placeholder = f"MERMAID_PLACEHOLDER_{len(mermaid_blocks)}"
            mermaid_blocks.append(content)
            return placeholder

        # Replace mermaid blocks with placeholders
        text = self.MERMAID_PATTERN.sub(mermaid_placeholder, text)

        # Convert markdown
        self.md.reset()
        html = self.md.convert(text)

        # Restore mermaid blocks as div elements
        for i, content in enumerate(mermaid_blocks):
            placeholder = f"MERMAID_PLACEHOLDER_{i}"
            mermaid_div = f'<div class="mermaid">\n{content}\n</div>'
            html = html.replace(f"<p>{placeholder}</p>", mermaid_div)
            html = html.replace(placeholder, mermaid_div)

        return html

    def _normalize_mermaid(self, content: str) -> str:
        """Normalize Mermaid source for the bundled Mermaid parser."""
        content = self._strip_invisible_chars(content)

        if content.startswith("erDiagram"):
            return content

        if content.startswith("flowchart") or content.startswith("graph"):
            return self._normalize_flowchart(content)

        if content.startswith("quadrantChart"):
            return self._normalize_quadrant_chart(content)

        return content

    def _strip_invisible_chars(self, content: str) -> str:
        # Normalize newline first.
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        # Remove BOM/zero-width chars and normalize nbsp.
        return (
            content
            .replace("\ufeff", "")
            .replace("\u200b", "")
            .replace("\u200c", "")
            .replace("\u200d", "")
            .replace("\u00a0", " ")
        )

    def _normalize_flowchart(self, content: str) -> str:
        def replace_label(match):
            label = match.group(1)
            stripped = label.strip()

            # Keep already-quoted labels unchanged.
            if stripped.startswith('"') and stripped.endswith('"'):
                return f"[{label}]"

            # Mermaid flowchart parser can choke on parentheses in [] labels.
            if "(" in label or ")" in label:
                escaped = label.replace('"', r'\"')
                return f'["{escaped}"]'

            return f"[{label}]"

        normalized_lines = []
        for line in content.splitlines():
            if '[' in line and ']' in line:
                line = self.FLOW_BRACKET_LABEL_PATTERN.sub(replace_label, line)
            normalized_lines.append(line)

        return "\n".join(normalized_lines)

    def _normalize_quadrant_chart(self, content: str) -> str:
        normalized_lines = []

        for line in content.splitlines():
            axis_match = self.QUADRANT_AXIS_PATTERN.match(line)
            if axis_match:
                indent, keyword, spacer, value = axis_match.groups()
                value = self._quote_quadrant_axis_value(value.strip())
                normalized_lines.append(f"{indent}{keyword}{spacer}{value}")
                continue

            point_match = self.QUADRANT_POINT_PATTERN.match(line)
            if point_match:
                indent, label, tail = point_match.groups()
                label = label.strip()
                if label and not self._is_quoted(label) and self._has_non_ascii(label):
                    label = self._quote_text(label)
                normalized_lines.append(f"{indent}{label}{tail}")
                continue

            normalized_lines.append(line)

        return "\n".join(normalized_lines)

    def _quote_quadrant_axis_value(self, value: str) -> str:
        if not value:
            return value

        if "-->" in value:
            left, right = value.split("-->", 1)
            left = self._maybe_quote_quadrant_text(left.strip())
            right = self._maybe_quote_quadrant_text(right.strip())
            return f"{left} --> {right}"

        return self._maybe_quote_quadrant_text(value.strip())

    def _maybe_quote_quadrant_text(self, text: str) -> str:
        if not text or self._is_quoted(text):
            return text
        if self._has_non_ascii(text):
            return self._quote_text(text)
        return text

    @staticmethod
    def _is_quoted(text: str) -> bool:
        return len(text) >= 2 and text[0] == '"' and text[-1] == '"'

    @staticmethod
    def _has_non_ascii(text: str) -> bool:
        return any(ord(ch) > 127 for ch in text)

    @staticmethod
    def _quote_text(text: str) -> str:
        escaped = text.replace('"', r'\"')
        return f'"{escaped}"'

    _highlight_css_cache = None

    @classmethod
    def get_code_highlight_css(cls) -> str:
        if cls._highlight_css_cache is None:
            formatter = HtmlFormatter(style='monokai')
            cls._highlight_css_cache = formatter.get_style_defs('.highlight')
        return cls._highlight_css_cache
