import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self._is_dark = is_dark
        self._build_rules()

    def set_dark_mode(self, is_dark):
        self._is_dark = is_dark
        self._build_rules()
        self.rehighlight()

    def _build_rules(self):
        self._rules = []

        if self._is_dark:
            heading_color = "#569cd6"
            bold_color = "#ce9178"
            italic_color = "#b5cea8"
            code_color = "#d7ba7d"
            link_color = "#4ec9b0"
            image_color = "#c586c0"
            list_color = "#d4d4d4"
            quote_color = "#608b4e"
            hr_color = "#808080"
            strikethrough_color = "#808080"
        else:
            heading_color = "#0000ff"
            bold_color = "#a31515"
            italic_color = "#098658"
            code_color = "#795e26"
            link_color = "#0066cc"
            image_color = "#af00db"
            list_color = "#1a1a1a"
            quote_color = "#008000"
            hr_color = "#808080"
            strikethrough_color = "#808080"

        # Heading (# ... ######)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(heading_color))
        fmt.setFontWeight(QFont.Bold)
        self._rules.append((re.compile(r'^#{1,6}\s+.*$', re.MULTILINE), fmt))

        # Bold **text** or __text__
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(bold_color))
        fmt.setFontWeight(QFont.Bold)
        self._rules.append((re.compile(r'\*\*[^*]+\*\*|__[^_]+__'), fmt))

        # Italic *text* or _text_
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(italic_color))
        fmt.setFontItalic(True)
        self._rules.append((re.compile(r'(?<!\*)\*(?!\*)[^*]+\*(?!\*)|(?<!_)_(?!_)[^_]+_(?!_)'), fmt))

        # Strikethrough ~~text~~
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(strikethrough_color))
        fmt.setFontStrikeOut(True)
        self._rules.append((re.compile(r'~~[^~]+~~'), fmt))

        # Inline code `text`
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(code_color))
        fmt.setFontFamily("Consolas")
        self._rules.append((re.compile(r'`[^`\n]+`'), fmt))

        # Code block fences ```
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(code_color))
        self._rules.append((re.compile(r'^```.*$', re.MULTILINE), fmt))

        # Link [text](url)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(link_color))
        self._rules.append((re.compile(r'\[([^\]]*)\]\([^)]*\)'), fmt))

        # Image ![alt](url)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(image_color))
        self._rules.append((re.compile(r'!\[([^\]]*)\]\([^)]*\)'), fmt))

        # Unordered list markers
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(list_color))
        fmt.setFontWeight(QFont.Bold)
        self._rules.append((re.compile(r'^\s*[-*+]\s', re.MULTILINE), fmt))

        # Ordered list markers
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(list_color))
        fmt.setFontWeight(QFont.Bold)
        self._rules.append((re.compile(r'^\s*\d+\.\s', re.MULTILINE), fmt))

        # Blockquote
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(quote_color))
        self._rules.append((re.compile(r'^>\s.*$', re.MULTILINE), fmt))

        # Horizontal rule
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(hr_color))
        self._rules.append((re.compile(r'^[-*_]{3,}\s*$', re.MULTILINE), fmt))

        # Checklist
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(link_color))
        self._rules.append((re.compile(r'^\s*-\s+\[[ xX]\]\s', re.MULTILINE), fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)
