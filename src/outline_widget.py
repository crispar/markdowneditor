import re
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Signal, Qt


class OutlineWidget(QWidget):
    heading_clicked = Signal(int)  # line number

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("  Outline")
        title.setStyleSheet("font-weight: bold; padding: 6px 0;")
        layout.addWidget(title)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)

    def update_outline(self, text: str):
        self.tree.clear()
        if not text.strip():
            return

        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        # Stack to track parent items for nesting
        stack = []  # (level, item)

        for line_num, line in enumerate(text.split('\n'), 1):
            match = heading_pattern.match(line)
            if not match:
                continue

            level = len(match.group(1))
            title = match.group(2).strip()

            item = QTreeWidgetItem()
            item.setText(0, title)
            item.setData(0, Qt.UserRole, line_num)

            # Find the right parent
            while stack and stack[-1][0] >= level:
                stack.pop()

            if stack:
                stack[-1][1].addChild(item)
            else:
                self.tree.addTopLevelItem(item)

            stack.append((level, item))

        self.tree.expandAll()

    def _on_item_clicked(self, item, column):
        line_num = item.data(0, Qt.UserRole)
        if line_num is not None:
            self.heading_clicked.emit(line_num)
