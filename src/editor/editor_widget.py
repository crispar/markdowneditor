import re
import shutil
from typing import Tuple
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPlainTextEdit, QFileDialog, QMessageBox, QInputDialog
)
from PySide6.QtCore import Signal, QTimer, QEvent, QUrl, QMimeData
from PySide6.QtGui import (
    QTextCursor, QKeyEvent, QFont, QColor, QTextCharFormat,
    QKeySequence, QShortcut, QDragEnterEvent, QDropEvent
)
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt

from src.editor.toolbar import EditorToolbar
from src.editor.find_replace import FindReplaceWidget
from src.editor.syntax_highlighter import MarkdownHighlighter
from src.utils.image_handler import ImageHandler


class EditorWidget(QWidget):
    text_changed = Signal(str)
    image_download_status = Signal(str)  # status message for statusbar

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_handler = ImageHandler()
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(self._emit_text_changed)
        self._zoom_level = 0  # relative to base size 12

        self._setup_ui()
        self._connect_signals()

        # Install event filter on editor to catch Ctrl+V and Enter
        self.editor.installEventFilter(self)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        self.toolbar = EditorToolbar(self)
        layout.addWidget(self.toolbar)

        # Find/Replace bar
        self.find_replace = None  # lazy init after editor

        # Editor
        self.editor = QPlainTextEdit(self)
        self.editor.setPlaceholderText("Write your Markdown here...")
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.Monospace)
        self.editor.setFont(font)
        self.editor.setTabStopDistance(40)

        # Enable drag and drop
        self.editor.setAcceptDrops(True)

        layout.addWidget(self.editor)

        # Find/Replace widget (below editor)
        self.find_replace = FindReplaceWidget(self.editor, self)
        layout.addWidget(self.find_replace)

        # Syntax highlighter
        self.highlighter = MarkdownHighlighter(self.editor.document())

        # Current line highlight
        self.editor.cursorPositionChanged.connect(self._highlight_current_line)
        self._highlight_current_line()

    def _connect_signals(self):
        # Editor text changes
        self.editor.textChanged.connect(self._on_text_changed)

        # Toolbar signals
        self.toolbar.bold_clicked.connect(lambda: self._toggle_wrap("**", "**"))
        self.toolbar.italic_clicked.connect(lambda: self._toggle_wrap("*", "*"))
        self.toolbar.heading1_clicked.connect(lambda: self._toggle_heading("# "))
        self.toolbar.heading2_clicked.connect(lambda: self._toggle_heading("## "))
        self.toolbar.heading3_clicked.connect(lambda: self._toggle_heading("### "))
        self.toolbar.code_clicked.connect(lambda: self._toggle_wrap("`", "`"))
        self.toolbar.code_block_clicked.connect(self._insert_code_block)
        self.toolbar.quote_clicked.connect(lambda: self._prefix_lines("> "))
        self.toolbar.bullet_list_clicked.connect(lambda: self._prefix_lines("- "))
        self.toolbar.numbered_list_clicked.connect(lambda: self._prefix_lines("1. "))
        self.toolbar.link_clicked.connect(self._insert_link)
        self.toolbar.image_clicked.connect(self._insert_image_dialog)
        self.toolbar.horizontal_rule_clicked.connect(lambda: self._insert_text("\n---\n"))
        self.toolbar.strikethrough_clicked.connect(lambda: self._toggle_wrap("~~", "~~"))
        self.toolbar.checklist_clicked.connect(lambda: self._prefix_lines("- [ ] "))
        self.toolbar.table_clicked.connect(self._insert_table)

        # Find/Replace shortcuts
        find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        find_shortcut.activated.connect(self._show_find)
        replace_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        replace_shortcut.activated.connect(self._show_replace)

    def _show_find(self):
        if self.find_replace:
            self.find_replace.show_find()

    def _show_replace(self):
        if self.find_replace:
            self.find_replace.show_replace()

    def _on_text_changed(self):
        self._debounce_timer.start()

    def _emit_text_changed(self):
        self.text_changed.emit(self.editor.toPlainText())

    def _highlight_current_line(self):
        selections = []
        if not self.editor.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#e8f0fe")  # will be updated by theme
            if hasattr(self, '_current_line_color'):
                line_color = self._current_line_color
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextCharFormat.FullWidthSelection, True)
            selection.cursor = self.editor.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)
        self.editor.setExtraSelections(selections)

    def set_current_line_color(self, color: QColor):
        self._current_line_color = color
        self._highlight_current_line()

    def eventFilter(self, obj, event: QEvent) -> bool:
        """Intercept key events from the editor widget"""
        if obj == self.editor and event.type() == QEvent.KeyPress:
            # Ctrl+V paste handling
            if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                if self._handle_paste():
                    return True
            # Enter key auto-indent
            if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() == Qt.NoModifier:
                if self._handle_enter():
                    return True
        # Drag and drop on editor
        if obj == self.editor:
            if event.type() == QEvent.DragEnter:
                return self._handle_drag_enter(event)
            if event.type() == QEvent.Drop:
                return self._handle_drop(event)
        return super().eventFilter(obj, event)

    def _handle_enter(self) -> bool:
        """Auto-indent for lists, quotes, etc."""
        cursor = self.editor.textCursor()
        block_text = cursor.block().text()

        # Patterns for auto-continuation
        patterns = [
            (re.compile(r'^(\s*)([-*+])\s+\[[ xX]\]\s(.*)$'), 'checklist'),  # checklist
            (re.compile(r'^(\s*)([-*+])\s(.*)$'), 'unordered'),
            (re.compile(r'^(\s*)(\d+)\.\s(.*)$'), 'ordered'),
            (re.compile(r'^(\s*)(>)\s(.*)$'), 'quote'),
        ]

        for pattern, list_type in patterns:
            match = pattern.match(block_text)
            if match:
                indent = match.group(1)
                content = match.group(3)

                # If current item is empty, remove the prefix instead
                if not content.strip():
                    cursor.movePosition(QTextCursor.StartOfBlock)
                    cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                    cursor.removeSelectedText()
                    self.editor.setTextCursor(cursor)
                    return True

                # Insert new line with continuation
                if list_type == 'checklist':
                    marker = match.group(2)
                    cursor.insertText(f"\n{indent}{marker} [ ] ")
                elif list_type == 'unordered':
                    marker = match.group(2)
                    cursor.insertText(f"\n{indent}{marker} ")
                elif list_type == 'ordered':
                    num = int(match.group(2)) + 1
                    cursor.insertText(f"\n{indent}{num}. ")
                elif list_type == 'quote':
                    cursor.insertText(f"\n{indent}> ")
                self.editor.setTextCursor(cursor)
                return True

        return False

    def _handle_drag_enter(self, event) -> bool:
        mime = event.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                path = url.toLocalFile().lower()
                if any(path.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.md', '.markdown')):
                    event.acceptProposedAction()
                    return True
        return False

    def _handle_drop(self, event) -> bool:
        mime = event.mimeData()
        if not mime.hasUrls():
            return False

        for url in mime.urls():
            file_path = url.toLocalFile()
            lower_path = file_path.lower()

            if any(lower_path.endswith(ext) for ext in ('.md', '.markdown')):
                # Signal parent to open the file
                main_window = self.window()
                if hasattr(main_window, '_open_dropped_file'):
                    main_window._open_dropped_file(file_path)
                event.acceptProposedAction()
                return True

            if any(lower_path.endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                self.image_handler.ensure_images_dir()
                src = Path(file_path)
                filename = src.name
                dest_path = self.image_handler.images_dir / filename

                if dest_path.exists():
                    import uuid
                    name, ext = filename.rsplit('.', 1)
                    filename = f"{name}_{uuid.uuid4().hex[:8]}.{ext}"
                    dest_path = self.image_handler.images_dir / filename

                shutil.copy2(file_path, dest_path)
                relative_path = f"images/{filename}"
                md_syntax = self.image_handler.get_markdown_image_syntax(relative_path)
                self._insert_text(md_syntax)
                event.acceptProposedAction()
                return True

        return False

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
                self.image_download_status.emit("Downloading image...")
                self._insert_text("![Downloading image...]")
                cursor = self.editor.textCursor()
                start_pos = cursor.position() - len("![Downloading image...]")

                image_path = self.image_handler.save_image_from_url(text)

                cursor.setPosition(start_pos)
                cursor.setPosition(cursor.position() + len("![Downloading image...]"),
                                   QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                self.editor.setTextCursor(cursor)

                if image_path:
                    md_syntax = self.image_handler.get_markdown_image_syntax(image_path)
                    self._insert_text(md_syntax)
                    self.image_download_status.emit("Image inserted")
                    return True
                else:
                    md_syntax = f"![image]({text})"
                    self._insert_text(md_syntax)
                    self.image_download_status.emit("Image download failed, URL inserted")
                    return True

        return False

    def _toggle_wrap(self, prefix: str, suffix: str):
        """Wrap/unwrap selection with prefix/suffix (toggle)."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()

        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            text = cursor.selectedText()

            # Check if already wrapped
            if text.startswith(prefix) and text.endswith(suffix) and len(text) > len(prefix) + len(suffix):
                # Unwrap
                unwrapped = text[len(prefix):-len(suffix)]
                cursor.insertText(unwrapped)
            else:
                # Check if the surrounding text has the wrapping
                doc = self.editor.document()
                full_text = doc.toPlainText()
                before_start = max(0, start - len(prefix))
                after_end = min(len(full_text), end + len(suffix))

                if (full_text[before_start:start] == prefix and
                        full_text[end:after_end] == suffix):
                    # Remove surrounding wrapping
                    cursor.setPosition(before_start)
                    cursor.setPosition(after_end, QTextCursor.KeepAnchor)
                    cursor.insertText(full_text[before_start + len(prefix):after_end - len(suffix)])
                else:
                    # Wrap
                    new_text = f"{prefix}{text}{suffix}"
                    cursor.insertText(new_text)
        else:
            pos = cursor.position()
            cursor.insertText(f"{prefix}{suffix}")
            cursor.setPosition(pos + len(prefix))
            self.editor.setTextCursor(cursor)

        cursor.endEditBlock()

    def _toggle_heading(self, prefix: str):
        """Toggle or switch heading level."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        line_text = cursor.selectedText()

        # Check if line already has a heading prefix
        heading_match = re.match(r'^(#{1,6})\s+', line_text)
        if heading_match:
            existing_prefix = heading_match.group(0)
            if existing_prefix == prefix:
                # Same level: remove heading (toggle off)
                cursor.insertText(line_text[len(existing_prefix):])
            else:
                # Different level: replace
                cursor.insertText(prefix + line_text[len(existing_prefix):])
        else:
            # No heading: add
            cursor.insertText(prefix + line_text)

        cursor.endEditBlock()

    def _prefix_lines(self, prefix: str):
        """Apply prefix to all selected lines (or current line)."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()

        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()

            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.StartOfBlock)
            start_block = cursor.blockNumber()

            cursor.setPosition(end)
            if cursor.atBlockStart() and end > start:
                cursor.movePosition(QTextCursor.Left)
            end_block = cursor.blockNumber()

            # Apply prefix to each line
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.StartOfBlock)

            for i in range(end_block - start_block + 1):
                cursor.movePosition(QTextCursor.StartOfBlock)
                cursor.insertText(prefix)
                if i < end_block - start_block:
                    cursor.movePosition(QTextCursor.Down)
        else:
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.insertText(prefix)

        cursor.endEditBlock()

    def _insert_text(self, text: str):
        cursor = self.editor.textCursor()
        cursor.insertText(text)

    def _insert_code_block(self):
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()

        # Ask for language
        lang, ok = QInputDialog.getItem(
            self, "Code Block Language",
            "Select language:",
            ["", "python", "javascript", "typescript", "java", "c", "cpp",
             "csharp", "go", "rust", "html", "css", "sql", "bash", "json",
             "yaml", "xml", "markdown"],
            0, True
        )
        if not ok:
            return

        cursor.beginEditBlock()
        if selected_text:
            new_text = f"```{lang}\n{selected_text}\n```"
            cursor.insertText(new_text)
        else:
            pos = cursor.position()
            cursor.insertText(f"```{lang}\n\n```")
            cursor.setPosition(pos + 4 + len(lang))
            self.editor.setTextCursor(cursor)
        cursor.endEditBlock()

    def _insert_link(self):
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()

        cursor.beginEditBlock()
        if selected_text:
            new_text = f"[{selected_text}](url)"
            cursor.insertText(new_text)
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 3)
            self.editor.setTextCursor(cursor)
        else:
            pos = cursor.position()
            cursor.insertText("[text](url)")
            cursor.setPosition(pos + 1)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 4)
            self.editor.setTextCursor(cursor)
        cursor.endEditBlock()

    def _insert_table(self):
        cursor = self.editor.textCursor()
        table_text = (
            "\n| Header 1 | Header 2 | Header 3 |\n"
            "| -------- | -------- | -------- |\n"
            "| Cell 1   | Cell 2   | Cell 3   |\n"
            "| Cell 4   | Cell 5   | Cell 6   |\n"
        )
        cursor.beginEditBlock()
        cursor.insertText(table_text)
        cursor.endEditBlock()

    def _insert_image_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All Files (*)"
        )

        if file_path:
            self.image_handler.ensure_images_dir()
            filename = Path(file_path).name
            dest_path = self.image_handler.images_dir / filename

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

    def get_word_count(self) -> int:
        text = self.editor.toPlainText().strip()
        if not text:
            return 0
        return len(text.split())

    def zoom_in(self):
        self._zoom_level += 1
        self._apply_zoom()

    def zoom_out(self):
        if self._zoom_level > -5:
            self._zoom_level -= 1
            self._apply_zoom()

    def zoom_reset(self):
        self._zoom_level = 0
        self._apply_zoom()

    def _apply_zoom(self):
        base_size = self._base_font_size()
        size = max(8, base_size + self._zoom_level)
        font = self.editor.font()
        font.setPointSize(size)
        self.editor.setFont(font)

    def _base_font_size(self):
        font = self.editor.font()
        ps = font.pointSize()
        if ps > 0:
            return ps - self._zoom_level
        return 12

    def go_to_line(self, line_number: int):
        block = self.editor.document().findBlockByLineNumber(line_number - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            self.editor.setTextCursor(cursor)
            self.editor.centerCursor()
            self.editor.setFocus()
