import re
import markdown
from pygments.formatters import HtmlFormatter


class MarkdownConverter:
    # Pattern to match mermaid code blocks
    MERMAID_PATTERN = re.compile(
        r'```mermaid\s*\n(.*?)```',
        re.DOTALL
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

    _highlight_css_cache = None

    @classmethod
    def get_code_highlight_css(cls) -> str:
        if cls._highlight_css_cache is None:
            formatter = HtmlFormatter(style='monokai')
            cls._highlight_css_cache = formatter.get_style_defs('.highlight')
        return cls._highlight_css_cache
