import markdown
from pygments.formatters import HtmlFormatter


class MarkdownConverter:
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
        self.md.reset()
        return self.md.convert(text)

    @staticmethod
    def get_code_highlight_css() -> str:
        formatter = HtmlFormatter(style='monokai')
        return formatter.get_style_defs('.highlight')
