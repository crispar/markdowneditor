from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QMessageBox,
    QStatusBar, QLabel, QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence

from src.editor import EditorWidget
from src.preview import PreviewWidget
from src.export import PDFExporter
from src.styles.theme import Theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.base_path = Path.cwd()

        self._setup_ui()
        self._setup_menubar()
        self._setup_statusbar()
        self._apply_theme()
        self._connect_signals()

    def _setup_ui(self):
        self.setWindowTitle("Markdown Editor")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)

        # Main splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(2)

        # Editor and Preview
        self.editor = EditorWidget(self)
        self.preview = PreviewWidget(self)

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        self.splitter.setSizes([700, 700])

        self.setCentralWidget(self.splitter)

    def _setup_menubar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_pdf_action = QAction("Export to PDF...", self)
        export_pdf_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        export_pdf_action.triggered.connect(self._export_pdf)
        file_menu.addAction(export_pdf_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.editor.editor.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.editor.editor.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.editor.editor.paste)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.editor.editor.selectAll)
        edit_menu.addAction(select_all_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Status widgets
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(20)

        self.char_count_label = QLabel("Characters: 0")
        self.cursor_pos_label = QLabel("Ln 1, Col 1")

        status_layout.addWidget(self.char_count_label)
        status_layout.addWidget(self.cursor_pos_label)

        self.statusbar.addPermanentWidget(status_widget)

    def _apply_theme(self):
        colors = Theme.get_current()
        self.setStyleSheet(Theme.get_stylesheet(colors))
        self.preview.set_theme(colors)

    def _connect_signals(self):
        # Update preview on text change
        self.editor.text_changed.connect(self.preview.update_preview)

        # Update status bar
        self.editor.editor.textChanged.connect(self._update_char_count)
        self.editor.editor.cursorPositionChanged.connect(self._update_cursor_pos)

        # Initial preview
        QTimer.singleShot(100, lambda: self.preview.update_preview(""))

    def _update_char_count(self):
        count = self.editor.get_character_count()
        self.char_count_label.setText(f"Characters: {count}")

    def _update_cursor_pos(self):
        line, col = self.editor.get_cursor_position()
        self.cursor_pos_label.setText(f"Ln {line}, Col {col}")

    def _new_file(self):
        if self._check_unsaved_changes():
            self.editor.set_text("")
            self.current_file = None
            self._update_title()

    def _open_file(self):
        if not self._check_unsaved_changes():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.set_text(content)
                self.current_file = Path(file_path)
                self.base_path = self.current_file.parent
                self.editor.set_base_path(str(self.base_path))
                self.preview.set_base_path(str(self.base_path))
                self._update_title()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def _save_file(self):
        if self.current_file:
            self._write_file(self.current_file)
        else:
            self._save_file_as()

    def _save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File",
            "",
            "Markdown Files (*.md);;All Files (*)"
        )

        if file_path:
            if not file_path.endswith('.md'):
                file_path += '.md'
            self._write_file(Path(file_path))
            self.current_file = Path(file_path)
            self.base_path = self.current_file.parent
            self.editor.set_base_path(str(self.base_path))
            self.preview.set_base_path(str(self.base_path))
            self._update_title()

    def _write_file(self, path: Path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.get_text())
            self.statusbar.showMessage("File saved", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def _export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if file_path:
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'

            try:
                exporter = PDFExporter(str(self.base_path), parent=self)
                exporter.export(self.editor.get_text(), file_path)
                self.statusbar.showMessage("PDF exported successfully", 3000)
                QMessageBox.information(self, "Success", f"PDF exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{str(e)}")

    def _update_title(self):
        title = "Markdown Editor"
        if self.current_file:
            title = f"{self.current_file.name} - {title}"
        self.setWindowTitle(title)

    def _check_unsaved_changes(self) -> bool:
        # Simple check - could be enhanced with dirty flag
        if self.editor.get_text().strip():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True

    def _show_about(self):
        QMessageBox.about(
            self,
            "About Markdown Editor",
            "Markdown Editor\n\n"
            "A simple Markdown editor with live preview and PDF export.\n\n"
            "Features:\n"
            "- Real-time Markdown preview\n"
            "- Image paste support (Ctrl+V)\n"
            "- PDF export with Korean font support\n"
            "- Dark/Light theme support"
        )

    def closeEvent(self, event):
        if self._check_unsaved_changes():
            event.accept()
        else:
            event.ignore()
