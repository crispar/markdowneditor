from PySide6.QtWidgets import QToolBar, QToolButton
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QAction, QKeySequence

from src.editor.icons import make_icon


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

    ICON_SIZE = 20

    # (icon_name, text, tooltip, shortcut, signal_attr); None == separator.
    # NOTE: Ctrl+B / Ctrl+I / Ctrl+Shift+X carry no shortcut here because the
    # Format menu owns them (avoids an "ambiguous shortcut overload"). The
    # remaining shortcuts live only on the toolbar, so they are kept here.
    _LAYOUT = [
        ("bold", "Bold", "Bold (Ctrl+B)", None, "bold_clicked"),
        ("italic", "Italic", "Italic (Ctrl+I)", None, "italic_clicked"),
        ("strikethrough", "Strikethrough", "Strikethrough (Ctrl+Shift+X)", None, "strikethrough_clicked"),
        None,
        ("h1", "Heading 1", "Heading 1 (Ctrl+1)", "Ctrl+1", "heading1_clicked"),
        ("h2", "Heading 2", "Heading 2 (Ctrl+2)", "Ctrl+2", "heading2_clicked"),
        ("h3", "Heading 3", "Heading 3 (Ctrl+3)", "Ctrl+3", "heading3_clicked"),
        None,
        ("code", "Inline Code", "Inline Code (Ctrl+`)", "Ctrl+`", "code_clicked"),
        ("code_block", "Code Block", "Code Block (Ctrl+Shift+K)", "Ctrl+Shift+K", "code_block_clicked"),
        None,
        ("quote", "Quote", "Quote (Ctrl+Shift+Q)", "Ctrl+Shift+Q", "quote_clicked"),
        None,
        ("bullet_list", "Bullet List", "Bullet List (Ctrl+Shift+U)", "Ctrl+Shift+U", "bullet_list_clicked"),
        ("numbered_list", "Numbered List", "Numbered List (Ctrl+Shift+L)", "Ctrl+Shift+L", "numbered_list_clicked"),
        ("checklist", "Checklist", "Checklist (Ctrl+Shift+T)", "Ctrl+Shift+T", "checklist_clicked"),
        None,
        ("link", "Insert Link", "Insert Link (Ctrl+K)", "Ctrl+K", "link_clicked"),
        ("image", "Insert Image", "Insert Image (Ctrl+Shift+I)", "Ctrl+Shift+I", "image_clicked"),
        ("table", "Insert Table", "Insert Table", None, "table_clicked"),
        None,
        ("hr", "Horizontal Rule", "Horizontal Rule (Ctrl+Shift+H)", "Ctrl+Shift+H", "horizontal_rule_clicked"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        self._icon_color = "#333333"
        self._icon_actions = []  # list of (QAction, icon_name)
        self._setup_actions()

    def _setup_actions(self):
        for spec in self._LAYOUT:
            if spec is None:
                self.addSeparator()
                continue
            icon_name, text, tooltip, shortcut, signal_attr = spec
            action = QAction(text, self)
            action.setToolTip(tooltip)
            action.setIcon(make_icon(icon_name, self._icon_color, 32))
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(getattr(self, signal_attr).emit)
            self._icon_actions.append((action, icon_name))

            button = QToolButton(self)
            button.setDefaultAction(action)
            button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            button.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
            button.setAutoRaise(True)
            self.addWidget(button)

    def set_icon_color(self, color: str):
        """Recolour all toolbar icons (called when the theme changes)."""
        if color == self._icon_color:
            return
        self._icon_color = color
        for action, icon_name in self._icon_actions:
            action.setIcon(make_icon(icon_name, color, 32))
