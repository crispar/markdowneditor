from typing import Tuple
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPlainTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QTextCursor, QKeyEvent, QFont
from PySide6.QtCore import Qt

from src.editor.toolbar import EditorToolbar
from src.utils.image_handler import ImageHandler


class EditorWidget(QWidget):
    text_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_handler = ImageHandler()
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(self._emit_text_changed)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        self.toolbar = EditorToolbar(self)
        layout.addWidget(self.toolbar)

        # Editor
        self.editor = QPlainTextEdit(self)
        self.editor.setPlaceholderText("Write your Markdown here...")
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.Monospace)
        self.editor.setFont(font)
        self.editor.setTabStopDistance(40)
        layout.addWidget(self.editor)

    def _connect_signals(self):
        # Editor text changes
        self.editor.textChanged.connect(self._on_text_changed)

        # Toolbar signals
        self.toolbar.bold_clicked.connect(lambda: self._wrap_selection("**", "**"))
        self.toolbar.italic_clicked.connect(lambda: self._wrap_selection("*", "*"))
        self.toolbar.heading1_clicked.connect(lambda: self._prefix_line("# "))
        self.toolbar.heading2_clicked.connect(lambda: self._prefix_line("## "))
        self.toolbar.heading3_clicked.connect(lambda: self._prefix_line("### "))
        self.toolbar.code_clicked.connect(lambda: self._wrap_selection("`", "`"))
        self.toolbar.code_block_clicked.connect(self._insert_code_block)
        self.toolbar.quote_clicked.connect(lambda: self._prefix_line("> "))
        self.toolbar.bullet_list_clicked.connect(lambda: self._prefix_line("- "))
        self.toolbar.numbered_list_clicked.connect(lambda: self._prefix_line("1. "))
        self.toolbar.link_clicked.connect(self._insert_link)
        self.toolbar.image_clicked.connect(self._insert_image_dialog)
        self.toolbar.horizontal_rule_clicked.connect(lambda: self._insert_text("\n---\n"))

    def _on_text_changed(self):
        self._debounce_timer.start()

    def _emit_text_changed(self):
        self.text_changed.emit(self.editor.toPlainText())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            if self._handle_paste():
                return
        super().keyPressEvent(event)

    def _handle_paste(self) -> bool:
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        # 1. Check for actual image data in clipboard
        if mime_data.hasImage():
            image_path = self.image_handler.save_image_from_clipboard(mime_data)
            if image_path:
                md_syntax = self.image_handler.get_markdown_image_syntax(image_path)
                self._insert_text(md_syntax)
                return True

        # 2. Check for image URL in clipboard text
        if mime_data.hasText():
            text = mime_data.text().strip()
            if self.image_handler.is_image_url(text):
                # Show downloading status
                self._insert_text("![Downloading image...]")
                cursor = self.editor.textCursor()
                start_pos = cursor.position() - len("![Downloading image...]")

                # Download the image
                image_path = self.image_handler.save_image_from_url(text)

                # Remove the placeholder
                cursor.setPosition(start_pos)
                cursor.setPosition(cursor.position() + len("![Downloading image...]"),
                                   QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                self.editor.setTextCursor(cursor)

                if image_path:
                    md_syntax = self.image_handler.get_markdown_image_syntax(image_path)
                    self._insert_text(md_syntax)
                    return True
                else:
                    # If download failed, paste the URL as-is with image syntax
                    md_syntax = f"![image]({text})"
                    self._insert_text(md_syntax)
                    return True

        return False

    def _wrap_selection(self, prefix: str, suffix: str):
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            new_text = f"{prefix}{selected_text}{suffix}"
            cursor.insertText(new_text)
        else:
            pos = cursor.position()
            cursor.insertText(f"{prefix}{suffix}")
            cursor.setPosition(pos + len(prefix))
            self.editor.setTextCursor(cursor)

    def _prefix_line(self, prefix: str):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.insertText(prefix)

    def _insert_text(self, text: str):
        cursor = self.editor.textCursor()
        cursor.insertText(text)

    def _insert_code_block(self):
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            new_text = f"```\n{selected_text}\n```"
            cursor.insertText(new_text)
        else:
            pos = cursor.position()
            cursor.insertText("```\n\n```")
            cursor.setPosition(pos + 4)
            self.editor.setTextCursor(cursor)

    def _insert_link(self):
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            new_text = f"[{selected_text}](url)"
            cursor.insertText(new_text)
            # Select "url" for easy replacement
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 3)
            self.editor.setTextCursor(cursor)
        else:
            pos = cursor.position()
            cursor.insertText("[text](url)")
            cursor.setPosition(pos + 1)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 4)
            self.editor.setTextCursor(cursor)

    def _insert_image_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All Files (*)"
        )

        if file_path:
            # Copy to images folder and get relative path
            import shutil
            from pathlib import Path

            self.image_handler.ensure_images_dir()
            filename = Path(file_path).name
            dest_path = self.image_handler.images_dir / filename

            # Handle duplicate filenames
            if dest_path.exists():
                import uuid
                name, ext = filename.rsplit('.', 1)
                filename = f"{name}_{uuid.uuid4().hex[:8]}.{ext}"
                dest_path = self.image_handler.images_dir / filename

            shutil.copy2(file_path, dest_path)
            relative_path = f"images/{filename}"
            md_syntax = self.image_handler.get_markdown_image_syntax(relative_path)
            self._insert_text(md_syntax)

    def get_text(self) -> str:
        return self.editor.toPlainText()

    def set_text(self, text: str):
        self.editor.setPlainText(text)

    def set_base_path(self, path: str):
        self.image_handler.set_base_path(path)

    def get_cursor_position(self) -> Tuple[int, int]:
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        return line, col

    def get_character_count(self) -> int:
        return len(self.editor.toPlainText())
