import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.main_window import MainWindow
from src.utils.theme_detector import ThemeDetector
from src.styles.theme import Theme


class MarkdownEditorApp:
    APP_NAME = "Markdown Editor"
    APP_VERSION = "1.1.0"

    def __init__(self):
        self.app = QApplication(sys.argv)
        self._configure_app()
        self.window = MainWindow(self)

    def _configure_app(self):
        self.app.setApplicationName(self.APP_NAME)
        self.app.setApplicationVersion(self.APP_VERSION)
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
        self.app.setPalette(Theme.create_qpalette("dark"))

    def apply_light_palette(self):
        self.app.setPalette(self.app.style().standardPalette())

    def run(self) -> int:
        self.window.show()
        return self.app.exec()


def create_app() -> MarkdownEditorApp:
    return MarkdownEditorApp()
