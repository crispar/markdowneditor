import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QMessageBox,
    QStatusBar, QLabel, QWidget, QHBoxLayout, QMenu,
    QFontDialog, QDockWidget
)
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QAction, QKeySequence, QColor, QFont, QTextCursor, QActionGroup

from src.editor import EditorWidget
from src.preview import PreviewWidget
from src.export import PDFExporter
from src.styles.theme import Theme, ThemeColors
from src.outline_widget import OutlineWidget
from src.file_manager import FileManager
from src.constants import AUTOSAVE_INTERVAL


class MainWindow(QMainWindow):
    def __init__(self, app_instance=None):
        super().__init__()
        self.app_instance = app_instance
        self.settings = QSettings("MarkdownEditor", "MarkdownEditor")
        self.file_manager = FileManager(self.settings)

        self._setup_ui()
        self._setup_menubar()
        self._setup_statusbar()
        self._setup_outline()
        self._apply_theme()
        self._connect_signals()
        self._setup_autosave()
        self._restore_state()

    # --- Property shims for backward compatibility (tests access these directly) ---
    @property
    def current_file(self):
        return self.file_manager.current_file

    @current_file.setter
    def current_file(self, value):
        self.file_manager.current_file = value

    @property
    def base_path(self):
        return self.file_manager.base_path

    @base_path.setter
    def base_path(self, value):
        self.file_manager.base_path = value

    @property
    def _dirty(self):
        return self.file_manager._dirty

    @_dirty.setter
    def _dirty(self, value):
        self.file_manager._dirty = value

    @property
    def _saved_text(self):
        return self.file_manager._saved_text

    @_saved_text.setter
    def _saved_text(self, value):
        self.file_manager._saved_text = value

    @property
    def recent_files(self):
        return self.file_manager.recent_files

    @recent_files.setter
    def recent_files(self, value):
        self.file_manager.recent_files = value

    def _setup_ui(self):
        self.setWindowTitle("Markdown Editor")
        self.setMinimumSize(800, 500)
        self.resize(1400, 800)

        # Main splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(5)

        # Editor and Preview
        self.editor = EditorWidget(self)
        self.preview = PreviewWidget(self)

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        self.splitter.setSizes([700, 700])

        self.setCentralWidget(self.splitter)

    def _setup_outline(self):
        self.outline = OutlineWidget(self)
        self.outline_dock = QDockWidget("Outline", self)
        self.outline_dock.setWidget(self.outline)
        self.outline_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.outline_dock)
        self.outline_dock.hide()

        self.outline.heading_clicked.connect(self.editor.go_to_line)

    def _setup_menubar(self):
        menubar = self.menuBar()

        # ===== File menu =====
        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        self.recent_menu = QMenu("Recent Files", self)
        file_menu.addMenu(self.recent_menu)
        self._update_recent_menu()

        file_menu.addSeparator()

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

        export_html_action = QAction("Export to HTML...", self)
        export_html_action.triggered.connect(self._export_html)
        file_menu.addAction(export_html_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ===== Edit menu =====
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.editor.select_all)
        edit_menu.addAction(select_all_action)

        edit_menu.addSeparator()

        find_action = QAction("Find...", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.editor.show_find)
        edit_menu.addAction(find_action)

        replace_action = QAction("Replace...", self)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        replace_action.triggered.connect(self.editor.show_replace)
        edit_menu.addAction(replace_action)

        # ===== Format menu =====
        format_menu = menubar.addMenu("Format")

        bold_action = QAction("Bold", self)
        bold_action.setShortcut(QKeySequence("Ctrl+B"))
        bold_action.triggered.connect(self.editor.toolbar.bold_clicked.emit)
        format_menu.addAction(bold_action)

        italic_action = QAction("Italic", self)
        italic_action.setShortcut(QKeySequence("Ctrl+I"))
        italic_action.triggered.connect(self.editor.toolbar.italic_clicked.emit)
        format_menu.addAction(italic_action)

        strikethrough_action = QAction("Strikethrough", self)
        strikethrough_action.setShortcut(QKeySequence("Ctrl+Shift+X"))
        strikethrough_action.triggered.connect(self.editor.toolbar.strikethrough_clicked.emit)
        format_menu.addAction(strikethrough_action)

        format_menu.addSeparator()

        h1_action = QAction("Heading 1", self)
        h1_action.triggered.connect(self.editor.toolbar.heading1_clicked.emit)
        format_menu.addAction(h1_action)

        h2_action = QAction("Heading 2", self)
        h2_action.triggered.connect(self.editor.toolbar.heading2_clicked.emit)
        format_menu.addAction(h2_action)

        h3_action = QAction("Heading 3", self)
        h3_action.triggered.connect(self.editor.toolbar.heading3_clicked.emit)
        format_menu.addAction(h3_action)

        format_menu.addSeparator()

        code_action = QAction("Inline Code", self)
        code_action.triggered.connect(self.editor.toolbar.code_clicked.emit)
        format_menu.addAction(code_action)

        code_block_action = QAction("Code Block", self)
        code_block_action.triggered.connect(self.editor.toolbar.code_block_clicked.emit)
        format_menu.addAction(code_block_action)

        format_menu.addSeparator()

        quote_action = QAction("Blockquote", self)
        quote_action.triggered.connect(self.editor.toolbar.quote_clicked.emit)
        format_menu.addAction(quote_action)

        bullet_action = QAction("Bullet List", self)
        bullet_action.triggered.connect(self.editor.toolbar.bullet_list_clicked.emit)
        format_menu.addAction(bullet_action)

        numbered_action = QAction("Numbered List", self)
        numbered_action.triggered.connect(self.editor.toolbar.numbered_list_clicked.emit)
        format_menu.addAction(numbered_action)

        checklist_action = QAction("Checklist", self)
        checklist_action.triggered.connect(self.editor.toolbar.checklist_clicked.emit)
        format_menu.addAction(checklist_action)

        format_menu.addSeparator()

        table_action = QAction("Insert Table", self)
        table_action.triggered.connect(self.editor.toolbar.table_clicked.emit)
        format_menu.addAction(table_action)

        link_action = QAction("Insert Link", self)
        link_action.triggered.connect(self.editor.toolbar.link_clicked.emit)
        format_menu.addAction(link_action)

        image_action = QAction("Insert Image", self)
        image_action.triggered.connect(self.editor.toolbar.image_clicked.emit)
        format_menu.addAction(image_action)

        hr_action = QAction("Horizontal Rule", self)
        hr_action.triggered.connect(self.editor.toolbar.horizontal_rule_clicked.emit)
        format_menu.addAction(hr_action)

        # ===== View menu =====
        view_menu = menubar.addMenu("View")

        # Layout submenu
        layout_group = QActionGroup(self)
        layout_group.setExclusive(True)

        self.split_view_action = QAction("Split View", self)
        self.split_view_action.setShortcut(QKeySequence("Ctrl+Shift+3"))
        self.split_view_action.setCheckable(True)
        self.split_view_action.setChecked(True)
        self.split_view_action.triggered.connect(lambda: self._set_layout("split"))
        layout_group.addAction(self.split_view_action)
        view_menu.addAction(self.split_view_action)

        self.editor_only_action = QAction("Editor Only", self)
        self.editor_only_action.setShortcut(QKeySequence("Ctrl+Shift+1"))
        self.editor_only_action.setCheckable(True)
        self.editor_only_action.triggered.connect(lambda: self._set_layout("editor"))
        layout_group.addAction(self.editor_only_action)
        view_menu.addAction(self.editor_only_action)

        self.preview_only_action = QAction("Preview Only", self)
        self.preview_only_action.setShortcut(QKeySequence("Ctrl+Shift+2"))
        self.preview_only_action.setCheckable(True)
        self.preview_only_action.triggered.connect(lambda: self._set_layout("preview"))
        layout_group.addAction(self.preview_only_action)
        view_menu.addAction(self.preview_only_action)

        view_menu.addSeparator()

        # Outline toggle
        self.toggle_outline_action = QAction("Show Outline", self)
        self.toggle_outline_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self.toggle_outline_action.setCheckable(True)
        self.toggle_outline_action.triggered.connect(self._toggle_outline)
        view_menu.addAction(self.toggle_outline_action)

        view_menu.addSeparator()

        # Theme submenu
        theme_menu = QMenu("Theme", self)
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)

        self.light_theme_action = QAction("Light", self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.triggered.connect(lambda: self._switch_theme("light"))
        theme_group.addAction(self.light_theme_action)
        theme_menu.addAction(self.light_theme_action)

        self.dark_theme_action = QAction("Dark", self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(lambda: self._switch_theme("dark"))
        theme_group.addAction(self.dark_theme_action)
        theme_menu.addAction(self.dark_theme_action)

        self.system_theme_action = QAction("System", self)
        self.system_theme_action.setCheckable(True)
        self.system_theme_action.setChecked(True)
        self.system_theme_action.triggered.connect(lambda: self._switch_theme("system"))
        theme_group.addAction(self.system_theme_action)
        theme_menu.addAction(self.system_theme_action)

        view_menu.addMenu(theme_menu)

        view_menu.addSeparator()

        # Zoom
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence("Ctrl+="))
        zoom_in_action.triggered.connect(self._zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_action.triggered.connect(self._zoom_out)
        view_menu.addAction(zoom_out_action)

        zoom_reset_action = QAction("Reset Zoom", self)
        zoom_reset_action.setShortcut(QKeySequence("Ctrl+0"))
        zoom_reset_action.triggered.connect(self._zoom_reset)
        view_menu.addAction(zoom_reset_action)

        view_menu.addSeparator()

        # Font settings
        font_action = QAction("Font Settings...", self)
        font_action.triggered.connect(self._change_font)
        view_menu.addAction(font_action)

        view_menu.addSeparator()

        # Fullscreen
        self.fullscreen_action = QAction("Fullscreen", self)
        self.fullscreen_action.setShortcut(QKeySequence("F11"))
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(self.fullscreen_action)

        # ===== Help menu =====
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(20)

        self.char_count_label = QLabel("Characters: 0")
        self.word_count_label = QLabel("Words: 0")
        self.cursor_pos_label = QLabel("Ln 1, Col 1")

        status_layout.addWidget(self.char_count_label)
        status_layout.addWidget(self.word_count_label)
        status_layout.addWidget(self.cursor_pos_label)

        self.statusbar.addPermanentWidget(status_widget)

    def _apply_theme(self):
        colors = Theme.get_current()
        self.setStyleSheet(Theme.get_stylesheet(colors))
        self.preview.set_theme(colors)

        # Update editor current line highlight color
        self.editor.set_current_line_color(QColor(colors.current_line))

        # Update syntax highlighter theme
        is_dark = Theme.is_dark()
        self.editor.set_dark_mode(is_dark)

        # Update theme check marks
        if hasattr(self, 'light_theme_action'):
            saved = self.settings.value("theme_mode", "system")
            self.light_theme_action.setChecked(saved == "light")
            self.dark_theme_action.setChecked(saved == "dark")
            self.system_theme_action.setChecked(saved == "system")

    def _connect_signals(self):
        # Update preview on text change
        self.editor.text_changed.connect(self.preview.update_preview)

        # Update status bar
        self.editor.connect_text_changed(self._update_char_count)
        self.editor.connect_text_changed(self._update_word_count)
        self.editor.connect_cursor_changed(self._update_cursor_pos)

        # Dirty flag
        self.editor.connect_text_changed(self._mark_dirty)

        # Scroll sync
        self.editor.connect_scroll_changed(self._sync_scroll)

        # Outline update
        self.editor.text_changed.connect(self.outline.update_outline)

        # Image download status
        self.editor.image_download_status.connect(
            lambda msg: self.statusbar.showMessage(msg, 3000)
        )

        # Initial preview
        QTimer.singleShot(100, lambda: self.preview.update_preview(""))

    def _setup_autosave(self):
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(AUTOSAVE_INTERVAL)
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start()

    def _autosave(self):
        if self.file_manager.is_dirty and self.current_file:
            self._write_file(self.current_file)
            self.file_manager.mark_saved(self.editor.get_text())
            self._update_title()
            self.statusbar.showMessage("Auto-saved", 2000)

    def _mark_dirty(self):
        current_text = self.editor.get_text()
        if self.file_manager.mark_dirty(current_text):
            self._update_title()

    def _sync_scroll(self):
        ratio = self.editor.get_scroll_ratio()
        if ratio > 0.0:
            self.preview.scroll_to_ratio(ratio)

    # ===== Status bar updates =====

    def _update_char_count(self):
        count = self.editor.get_character_count()
        self.char_count_label.setText(f"Characters: {count}")

    def _update_word_count(self):
        count = self.editor.get_word_count()
        self.word_count_label.setText(f"Words: {count}")

    def _update_cursor_pos(self):
        line, col = self.editor.get_cursor_position()
        self.cursor_pos_label.setText(f"Ln {line}, Col {col}")

    # ===== File operations =====

    def _get_initial_dir(self) -> str:
        return self.file_manager.get_initial_dir()

    def _new_file(self):
        if self._check_unsaved_changes():
            self.editor.set_text("")
            self.file_manager.new_file()
            self._update_title()

    def _open_file(self):
        if not self._check_unsaved_changes():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            self._get_initial_dir(),
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )

        if file_path:
            self._load_file(file_path)

    def _load_file(self, file_path: str):
        try:
            content = self.file_manager.load_file(file_path)
            self.editor.set_text(content)
            self.editor.set_base_path(str(self.base_path))
            self.preview.set_base_path(str(self.base_path))
            self._update_title()
            self._update_recent_menu()
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def _open_dropped_file(self, file_path: str):
        if not self._check_unsaved_changes():
            return
        self._load_file(file_path)

    def _save_file(self):
        if self.current_file:
            self._write_file(self.current_file)
            self.file_manager.mark_saved(self.editor.get_text())
            self._update_title()
        else:
            self._save_file_as()

    def _save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File",
            self._get_initial_dir(),
            "Markdown Files (*.md);;All Files (*)"
        )

        if file_path:
            if not file_path.endswith('.md'):
                file_path += '.md'
            self._write_file(Path(file_path))
            self.file_manager.current_file = Path(file_path)
            self.file_manager.base_path = self.file_manager.current_file.parent
            self.editor.set_base_path(str(self.base_path))
            self.preview.set_base_path(str(self.base_path))
            self.file_manager.mark_saved(self.editor.get_text())
            self._update_title()
            self.settings.setValue("last_directory", str(self.current_file.parent))

    def _write_file(self, path):
        try:
            self.file_manager.write_file(path, self.editor.get_text())
            self.statusbar.showMessage("File saved", 3000)
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    # ===== Export =====

    def _export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to PDF",
            self._get_initial_dir(),
            "PDF Files (*.pdf)"
        )

        if file_path:
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'

            # Show progress
            self.statusbar.showMessage("Exporting PDF...")

            try:
                exporter = PDFExporter(str(self.base_path), parent=self)
                exporter.export(self.editor.get_text(), file_path)

                self.statusbar.clearMessage()
                reply = QMessageBox.information(
                    self, "Success",
                    f"PDF exported to:\n{file_path}\n\nOpen the file?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.Yes:
                    self._open_exported_file(file_path)
            except Exception as e:
                self.statusbar.clearMessage()
                QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{str(e)}")

    def _export_html(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to HTML",
            self._get_initial_dir(),
            "HTML Files (*.html)"
        )

        if file_path:
            if not file_path.endswith('.html'):
                file_path += '.html'

            try:
                html_content = self.preview.get_full_html(self.editor.get_text())
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                reply = QMessageBox.information(
                    self, "Success",
                    f"HTML exported to:\n{file_path}\n\nOpen the file?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.Yes:
                    self._open_exported_file(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export HTML:\n{str(e)}")

    def _open_exported_file(self, file_path: str):
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path])
            else:
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            self.statusbar.showMessage(f"Could not open file: {e}", 5000)

    # ===== Title =====

    def _update_title(self):
        self.setWindowTitle(self.file_manager.get_title())

    def _check_unsaved_changes(self) -> bool:
        if self._dirty:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True

    # ===== View actions =====

    def _set_layout(self, mode: str):
        self._layout_mode = mode
        if mode == "editor":
            self.splitter.setSizes([1, 0])
            self.preview.update_preview(self.editor.get_text())
        elif mode == "preview":
            self.splitter.setSizes([0, 1])
            self.preview.update_preview(self.editor.get_text())
        else:  # split
            self.splitter.setSizes([1, 1])

    def _toggle_outline(self, checked):
        if checked:
            self.outline_dock.show()
            self.outline.update_outline(self.editor.get_text())
        else:
            self.outline_dock.hide()

    def _switch_theme(self, mode: str):
        Theme.set_mode(mode)
        self.settings.setValue("theme_mode", mode)
        self._apply_theme()

        if self.app_instance:
            if Theme.is_dark():
                self.app_instance.apply_dark_palette()
            else:
                self.app_instance.apply_light_palette()

        # Refresh preview
        self.preview.update_preview(self.editor.get_text())

    def _zoom_in(self):
        self.editor.zoom_in()
        self.preview.zoom_in()

    def _zoom_out(self):
        self.editor.zoom_out()
        self.preview.zoom_out()

    def _zoom_reset(self):
        self.editor.zoom_reset()
        self.preview.zoom_reset()

    def _change_font(self):
        current_font = self.editor.get_font()
        font, ok = QFontDialog.getFont(current_font, self, "Select Editor Font")
        if ok:
            self.editor.set_font(font)
            self.settings.setValue("editor_font_family", font.family())
            self.settings.setValue("editor_font_size", font.pointSize())

    def _toggle_fullscreen(self, checked):
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    # ===== About =====

    def _show_about(self):
        QMessageBox.about(
            self,
            "About Markdown Editor",
            "Markdown Editor v1.1\n\n"
            "A modern Markdown editor with live preview.\n\n"
            "Features:\n"
            "- Real-time preview with scroll sync\n"
            "- Syntax highlighting\n"
            "- Find & Replace (Ctrl+F / Ctrl+H)\n"
            "- Image paste & drag-and-drop\n"
            "- PDF & HTML export\n"
            "- Dark/Light theme\n"
            "- Outline panel\n"
            "- Auto-save"
        )

    # ===== Window state =====

    def closeEvent(self, event):
        if self._check_unsaved_changes():
            self._save_state()
            event.accept()
        else:
            event.ignore()

    def _save_state(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
        self.settings.setValue("splitter_sizes", self.splitter.sizes())

    def _restore_state(self):
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        state = self.settings.value("window_state")
        if state:
            self.restoreState(state)

        splitter_sizes = self.settings.value("splitter_sizes")
        if splitter_sizes:
            self.splitter.setSizes([int(s) for s in splitter_sizes])

        # Restore theme
        saved_theme = self.settings.value("theme_mode", "system")
        if saved_theme != "system":
            Theme.set_mode(saved_theme)

        # Restore font
        font_family = self.settings.value("editor_font_family")
        font_size = self.settings.value("editor_font_size")
        if font_family:
            font = self.editor.get_font()
            font.setFamily(font_family)
            if font_size:
                font.setPointSize(int(font_size))
            self.editor.set_font(font)

    # ===== Recent Files Management =====

    def _add_recent_file(self, file_path: str):
        self.file_manager.add_recent_file(file_path)
        self._update_recent_menu()

    def _update_recent_menu(self):
        self.recent_menu.clear()
        if not self.recent_files:
            no_recent = QAction("(No recent files)", self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
        else:
            for i, file_path in enumerate(self.recent_files):
                action = QAction(f"&{i+1}. {Path(file_path).name}", self)
                action.setToolTip(file_path)
                action.triggered.connect(lambda checked, fp=file_path: self._open_recent_file(fp))
                self.recent_menu.addAction(action)

            self.recent_menu.addSeparator()
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self._clear_recent_files)
            self.recent_menu.addAction(clear_action)

    def _open_recent_file(self, file_path: str):
        if not self._check_unsaved_changes():
            return

        if not Path(file_path).exists():
            QMessageBox.warning(self, "File Not Found", f"File no longer exists:\n{file_path}")
            self.file_manager.recent_files.remove(file_path)
            self.file_manager.save_recent_files()
            self._update_recent_menu()
            return

        self._load_file(file_path)

    def _clear_recent_files(self):
        self.file_manager.clear_recent_files()
        self._update_recent_menu()
