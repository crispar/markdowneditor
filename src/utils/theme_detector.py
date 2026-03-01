import sys
from enum import Enum


class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"


class ThemeDetector:
    @staticmethod
    def get_system_theme() -> ThemeMode:
        if sys.platform == "win32":
            return ThemeDetector._get_windows_theme()
        return ThemeMode.LIGHT

    @staticmethod
    def _get_windows_theme() -> ThemeMode:
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return ThemeMode.LIGHT if value == 1 else ThemeMode.DARK
        except (FileNotFoundError, OSError, ImportError):
            return ThemeMode.LIGHT

    @staticmethod
    def is_dark_mode() -> bool:
        return ThemeDetector.get_system_theme() == ThemeMode.DARK
