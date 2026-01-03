from dataclasses import dataclass
from src.utils.theme_detector import ThemeDetector, ThemeMode


@dataclass
class ThemeColors:
    background: str
    foreground: str
    editor_bg: str
    editor_fg: str
    border: str
    toolbar_bg: str
    button_hover: str
    selection: str
    accent: str


class Theme:
    LIGHT = ThemeColors(
        background="#ffffff",
        foreground="#1a1a1a",
        editor_bg="#fafafa",
        editor_fg="#24292e",
        border="#e1e4e8",
        toolbar_bg="#f6f8fa",
        button_hover="#e1e4e8",
        selection="#0366d6",
        accent="#0066cc",
    )

    DARK = ThemeColors(
        background="#1e1e1e",
        foreground="#d4d4d4",
        editor_bg="#252526",
        editor_fg="#d4d4d4",
        border="#3c3c3c",
        toolbar_bg="#2d2d2d",
        button_hover="#3c3c3c",
        selection="#264f78",
        accent="#569cd6",
    )

    @staticmethod
    def get_current() -> ThemeColors:
        if ThemeDetector.is_dark_mode():
            return Theme.DARK
        return Theme.LIGHT

    @staticmethod
    def get_stylesheet(colors: ThemeColors) -> str:
        return f"""
        QMainWindow {{
            background-color: {colors.background};
        }}
        QSplitter::handle {{
            background-color: {colors.border};
            width: 2px;
        }}
        QPlainTextEdit {{
            background-color: {colors.editor_bg};
            color: {colors.editor_fg};
            border: 1px solid {colors.border};
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 14px;
            padding: 8px;
            selection-background-color: {colors.selection};
        }}
        QToolBar {{
            background-color: {colors.toolbar_bg};
            border: none;
            border-bottom: 1px solid {colors.border};
            spacing: 4px;
            padding: 4px;
        }}
        QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 6px;
            color: {colors.foreground};
            font-size: 14px;
            min-width: 28px;
            min-height: 28px;
        }}
        QToolButton:hover {{
            background-color: {colors.button_hover};
            border: 1px solid {colors.border};
        }}
        QToolButton:pressed {{
            background-color: {colors.selection};
        }}
        QMenuBar {{
            background-color: {colors.toolbar_bg};
            color: {colors.foreground};
            border-bottom: 1px solid {colors.border};
        }}
        QMenuBar::item:selected {{
            background-color: {colors.button_hover};
        }}
        QMenu {{
            background-color: {colors.background};
            color: {colors.foreground};
            border: 1px solid {colors.border};
        }}
        QMenu::item:selected {{
            background-color: {colors.selection};
        }}
        QStatusBar {{
            background-color: {colors.toolbar_bg};
            color: {colors.foreground};
            border-top: 1px solid {colors.border};
        }}
        QLabel {{
            color: {colors.foreground};
        }}
        """

    @staticmethod
    def get_preview_css(colors: ThemeColors) -> str:
        return f"""
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Malgun Gothic', 'Segoe UI', Helvetica, Arial, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            color: {colors.foreground};
            background-color: {colors.background};
            padding: 20px;
            margin: 0;
            max-width: 100%;
            word-wrap: break-word;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
            color: {colors.foreground};
        }}
        h1 {{ font-size: 2em; border-bottom: 1px solid {colors.border}; padding-bottom: 0.3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid {colors.border}; padding-bottom: 0.3em; }}
        h3 {{ font-size: 1.25em; }}
        h4 {{ font-size: 1em; }}
        p {{ margin-top: 0; margin-bottom: 16px; }}
        a {{ color: {colors.accent}; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        code {{
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 0.9em;
            background-color: {colors.toolbar_bg};
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }}
        pre {{
            background-color: {colors.editor_bg};
            border: 1px solid {colors.border};
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
            font-size: 0.9em;
            line-height: 1.45;
        }}
        .highlight {{
            background: #272822;
            color: #f8f8f2;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
        }}
        .highlight pre {{
            margin: 0;
            padding: 0;
            background: transparent;
            border: none;
        }}
        .highlight code {{
            color: #f8f8f2;
        }}
        blockquote {{
            margin: 0;
            padding: 0 1em;
            color: {colors.foreground};
            border-left: 4px solid {colors.accent};
            opacity: 0.8;
        }}
        ul, ol {{
            padding-left: 2em;
            margin-top: 0;
            margin-bottom: 16px;
        }}
        li {{ margin-bottom: 4px; }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }}
        th, td {{
            border: 1px solid {colors.border};
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: {colors.toolbar_bg};
            font-weight: 600;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        hr {{
            border: none;
            border-top: 1px solid {colors.border};
            margin: 24px 0;
        }}
        """
