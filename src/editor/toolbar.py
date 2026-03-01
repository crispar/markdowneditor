from PySide6.QtWidgets import QToolBar, QToolButton
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QKeySequence


class EditorToolbar(QToolBar):
    bold_clicked = Signal()
    italic_clicked = Signal()
    strikethrough_clicked = Signal()
    heading1_clicked = Signal()
    heading2_clicked = Signal()
    heading3_clicked = Signal()
    code_clicked = Signal()
    code_block_clicked = Signal()
    quote_clicked = Signal()
    bullet_list_clicked = Signal()
    numbered_list_clicked = Signal()
    checklist_clicked = Signal()
    link_clicked = Signal()
    image_clicked = Signal()
    table_clicked = Signal()
    horizontal_rule_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self._setup_actions()

    def _setup_actions(self):
        # Bold
        bold_action = QAction("B", self)
        bold_action.setToolTip("Bold (Ctrl+B)")
        bold_action.setShortcut(QKeySequence("Ctrl+B"))
        bold_action.triggered.connect(self.bold_clicked.emit)
        self._add_button(bold_action, bold=True)

        # Italic
        italic_action = QAction("I", self)
        italic_action.setToolTip("Italic (Ctrl+I)")
        italic_action.setShortcut(QKeySequence("Ctrl+I"))
        italic_action.triggered.connect(self.italic_clicked.emit)
        self._add_button(italic_action, italic=True)

        # Strikethrough
        strikethrough_action = QAction("S", self)
        strikethrough_action.setToolTip("Strikethrough (Ctrl+Shift+X)")
        strikethrough_action.setShortcut(QKeySequence("Ctrl+Shift+X"))
        strikethrough_action.triggered.connect(self.strikethrough_clicked.emit)
        self._add_button(strikethrough_action, strikethrough=True)

        self.addSeparator()

        # Headings
        h1_action = QAction("H1", self)
        h1_action.setToolTip("Heading 1 (Ctrl+1)")
        h1_action.setShortcut(QKeySequence("Ctrl+1"))
        h1_action.triggered.connect(self.heading1_clicked.emit)
        self._add_button(h1_action)

        h2_action = QAction("H2", self)
        h2_action.setToolTip("Heading 2 (Ctrl+2)")
        h2_action.setShortcut(QKeySequence("Ctrl+2"))
        h2_action.triggered.connect(self.heading2_clicked.emit)
        self._add_button(h2_action)

        h3_action = QAction("H3", self)
        h3_action.setToolTip("Heading 3 (Ctrl+3)")
        h3_action.setShortcut(QKeySequence("Ctrl+3"))
        h3_action.triggered.connect(self.heading3_clicked.emit)
        self._add_button(h3_action)

        self.addSeparator()

        # Code
        code_action = QAction("</>", self)
        code_action.setToolTip("Inline Code (Ctrl+`)")
        code_action.setShortcut(QKeySequence("Ctrl+`"))
        code_action.triggered.connect(self.code_clicked.emit)
        self._add_button(code_action)

        code_block_action = QAction("{ }", self)
        code_block_action.setToolTip("Code Block (Ctrl+Shift+K)")
        code_block_action.setShortcut(QKeySequence("Ctrl+Shift+K"))
        code_block_action.triggered.connect(self.code_block_clicked.emit)
        self._add_button(code_block_action)

        self.addSeparator()

        # Quote
        quote_action = QAction('"', self)
        quote_action.setToolTip("Quote (Ctrl+Shift+Q)")
        quote_action.setShortcut(QKeySequence("Ctrl+Shift+Q"))
        quote_action.triggered.connect(self.quote_clicked.emit)
        self._add_button(quote_action)

        self.addSeparator()

        # Lists
        bullet_action = QAction("*", self)
        bullet_action.setToolTip("Bullet List (Ctrl+Shift+U)")
        bullet_action.setShortcut(QKeySequence("Ctrl+Shift+U"))
        bullet_action.triggered.connect(self.bullet_list_clicked.emit)
        self._add_button(bullet_action)

        numbered_action = QAction("1.", self)
        numbered_action.setToolTip("Numbered List (Ctrl+Shift+L)")
        numbered_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
        numbered_action.triggered.connect(self.numbered_list_clicked.emit)
        self._add_button(numbered_action)

        # Checklist
        checklist_action = QAction("[]", self)
        checklist_action.setToolTip("Checklist (Ctrl+Shift+T)")
        checklist_action.setShortcut(QKeySequence("Ctrl+Shift+T"))
        checklist_action.triggered.connect(self.checklist_clicked.emit)
        self._add_button(checklist_action)

        self.addSeparator()

        # Link
        link_action = QAction("@", self)
        link_action.setToolTip("Insert Link (Ctrl+K)")
        link_action.setShortcut(QKeySequence("Ctrl+K"))
        link_action.triggered.connect(self.link_clicked.emit)
        self._add_button(link_action)

        # Image
        image_action = QAction("[img]", self)
        image_action.setToolTip("Insert Image (Ctrl+Shift+I)")
        image_action.setShortcut(QKeySequence("Ctrl+Shift+I"))
        image_action.triggered.connect(self.image_clicked.emit)
        self._add_button(image_action)

        # Table
        table_action = QAction("[T]", self)
        table_action.setToolTip("Insert Table")
        table_action.triggered.connect(self.table_clicked.emit)
        self._add_button(table_action)

        self.addSeparator()

        # Horizontal Rule
        hr_action = QAction("--", self)
        hr_action.setToolTip("Horizontal Rule (Ctrl+Shift+H)")
        hr_action.setShortcut(QKeySequence("Ctrl+Shift+H"))
        hr_action.triggered.connect(self.horizontal_rule_clicked.emit)
        self._add_button(hr_action)

    def _add_button(self, action: QAction, bold: bool = False, italic: bool = False, strikethrough: bool = False):
        button = QToolButton(self)
        button.setDefaultAction(action)
        styles = []
        if bold:
            styles.append("font-weight: bold;")
        if italic:
            styles.append("font-style: italic;")
        if strikethrough:
            styles.append("text-decoration: line-through;")
        if styles:
            button.setStyleSheet(" ".join(styles))
        self.addWidget(button)
