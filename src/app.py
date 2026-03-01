import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

from src.main_window import MainWindow
from src.utils.theme_detector import ThemeDetector


class MarkdownEditorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self._configure_app()
        self.window = MainWindow(self)

    def _configure_app(self):
        self.app.setApplicationName("Markdown Editor")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("MarkdownEditor")

        # Enable high DPI scaling
        self.app.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        # Set app style
        self.app.setStyle("Fusion")

        # Apply dark palette if system is in dark mode
        if ThemeDetector.is_dark_mode():
            self.apply_dark_palette()

    def apply_dark_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(212, 212, 212))
        palette.setColor(QPalette.Base, QColor(37, 37, 38))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, QColor(50, 50, 50))
        palette.setColor(QPalette.ToolTipText, QColor(212, 212, 212))
        palette.setColor(QPalette.Text, QColor(212, 212, 212))
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, QColor(212, 212, 212))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, QColor(86, 156, 214))
        palette.setColor(QPalette.Highlight, QColor(38, 79, 120))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        self.app.setPalette(palette)

    def apply_light_palette(self):
        self.app.setPalette(self.app.style().standardPalette())

    def run(self) -> int:
        self.window.show()
        return self.app.exec()


def create_app() -> MarkdownEditorApp:
    return MarkdownEditorApp()
