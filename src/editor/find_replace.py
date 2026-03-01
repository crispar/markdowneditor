import re
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QCheckBox, QLabel
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeySequence, QShortcut, QTextDocument


class FindReplaceWidget(QWidget):
    closed = Signal()

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self._setup_ui()
        self._connect_signals()
        self.hide()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(4)

        # Find row
        find_row = QHBoxLayout()
        find_row.setSpacing(4)

        find_label = QLabel("Find:")
        find_label.setFixedWidth(55)
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Search...")
        self.case_check = QCheckBox("Aa")
        self.case_check.setToolTip("Match Case")
        self.find_prev_btn = QPushButton("<")
        self.find_prev_btn.setToolTip("Previous (Shift+Enter)")
        self.find_prev_btn.setFixedWidth(30)
        self.find_next_btn = QPushButton(">")
        self.find_next_btn.setToolTip("Next (Enter)")
        self.find_next_btn.setFixedWidth(30)
        self.match_label = QLabel("")
        self.match_label.setFixedWidth(60)
        self.close_btn = QPushButton("X")
        self.close_btn.setToolTip("Close (Esc)")
        self.close_btn.setFixedWidth(24)

        find_row.addWidget(find_label)
        find_row.addWidget(self.find_input)
        find_row.addWidget(self.case_check)
        find_row.addWidget(self.find_prev_btn)
        find_row.addWidget(self.find_next_btn)
        find_row.addWidget(self.match_label)
        find_row.addWidget(self.close_btn)
        main_layout.addLayout(find_row)

        # Replace row
        self.replace_row_widget = QWidget()
        replace_row = QHBoxLayout(self.replace_row_widget)
        replace_row.setContentsMargins(0, 0, 0, 0)
        replace_row.setSpacing(4)

        replace_label = QLabel("Replace:")
        replace_label.setFixedWidth(55)
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace with...")
        self.replace_btn = QPushButton("Replace")
        self.replace_btn.setFixedWidth(60)
        self.replace_all_btn = QPushButton("All")
        self.replace_all_btn.setFixedWidth(40)

        replace_row.addWidget(replace_label)
        replace_row.addWidget(self.replace_input)
        replace_row.addWidget(self.replace_btn)
        replace_row.addWidget(self.replace_all_btn)

        main_layout.addWidget(self.replace_row_widget)
        self.replace_row_widget.hide()

    def _connect_signals(self):
        self.find_input.textChanged.connect(self._on_find_text_changed)
        self.find_input.returnPressed.connect(self.find_next)
        self.find_next_btn.clicked.connect(self.find_next)
        self.find_prev_btn.clicked.connect(self.find_previous)
        self.replace_btn.clicked.connect(self.replace)
        self.replace_all_btn.clicked.connect(self.replace_all)
        self.close_btn.clicked.connect(self.close_find)
        self.case_check.toggled.connect(lambda: self._on_find_text_changed(self.find_input.text()))

    def show_find(self):
        self.replace_row_widget.hide()
        self.show()
        self.find_input.setFocus()
        self.find_input.selectAll()

    def show_replace(self):
        self.replace_row_widget.show()
        self.show()
        self.find_input.setFocus()
        self.find_input.selectAll()

    def close_find(self):
        self.hide()
        self.editor.setFocus()
        self.closed.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_find()
        elif event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
            self.find_previous()
        else:
            super().keyPressEvent(event)

    def _get_find_flags(self):
        flags = QTextDocument.FindFlags()
        if self.case_check.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        return flags

    def _on_find_text_changed(self, text):
        if not text:
            self.match_label.setText("")
            return
        self._count_matches(text)
        # Find from current position
        if not self.editor.find(text, self._get_find_flags()):
            # Wrap around from start
            from PySide6.QtGui import QTextCursor
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.editor.setTextCursor(cursor)
            self.editor.find(text, self._get_find_flags())

    def _count_matches(self, text):
        content = self.editor.toPlainText()
        if self.case_check.isChecked():
            count = content.count(text)
        else:
            count = content.lower().count(text.lower())
        self.match_label.setText(f"{count} found")

    def find_next(self):
        text = self.find_input.text()
        if not text:
            return
        if not self.editor.find(text, self._get_find_flags()):
            # Wrap around
            cursor = self.editor.textCursor()
            cursor.movePosition(cursor.Start)
            self.editor.setTextCursor(cursor)
            self.editor.find(text, self._get_find_flags())

    def find_previous(self):
        text = self.find_input.text()
        if not text:
            return
        flags = self._get_find_flags() | QTextDocument.FindBackward
        if not self.editor.find(text, flags):
            # Wrap around
            cursor = self.editor.textCursor()
            cursor.movePosition(cursor.End)
            self.editor.setTextCursor(cursor)
            self.editor.find(text, flags)

    def replace(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection() and self._matches_current(cursor):
            cursor.insertText(self.replace_input.text())
        self.find_next()

    def replace_all(self):
        text = self.find_input.text()
        if not text:
            return
        replacement = self.replace_input.text()
        content = self.editor.toPlainText()
        if self.case_check.isChecked():
            new_content = content.replace(text, replacement)
        else:
            new_content = re.sub(re.escape(text), replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            self.editor.selectAll()
            self.editor.textCursor().insertText(new_content)
        self._count_matches(self.find_input.text())

    def _matches_current(self, cursor):
        selected = cursor.selectedText()
        find_text = self.find_input.text()
        if self.case_check.isChecked():
            return selected == find_text
        return selected.lower() == find_text.lower()
