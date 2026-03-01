"""Tests for Theme system."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.styles.theme import Theme, ThemeColors


class TestThemeColors:
    def test_light_colors_have_all_fields(self):
        c = Theme.LIGHT
        assert c.background
        assert c.foreground
        assert c.editor_bg
        assert c.editor_fg
        assert c.border
        assert c.toolbar_bg
        assert c.button_hover
        assert c.selection
        assert c.accent
        assert c.current_line

    def test_dark_colors_have_all_fields(self):
        c = Theme.DARK
        assert c.background
        assert c.foreground
        assert c.editor_bg
        assert c.editor_fg
        assert c.border
        assert c.toolbar_bg
        assert c.button_hover
        assert c.selection
        assert c.accent
        assert c.current_line

    def test_light_and_dark_are_different(self):
        assert Theme.LIGHT.background != Theme.DARK.background
        assert Theme.LIGHT.editor_bg != Theme.DARK.editor_bg


class TestThemeMode:
    def teardown_method(self):
        Theme.set_mode("system")  # reset after each test

    def test_set_dark_mode(self):
        Theme.set_mode("dark")
        assert Theme.is_dark() is True
        assert Theme.get_current() == Theme.DARK

    def test_set_light_mode(self):
        Theme.set_mode("light")
        assert Theme.is_dark() is False
        assert Theme.get_current() == Theme.LIGHT

    def test_set_system_mode(self):
        Theme.set_mode("system")
        # Should return either LIGHT or DARK, not crash
        colors = Theme.get_current()
        assert colors in (Theme.LIGHT, Theme.DARK)

    def test_mode_reset(self):
        Theme.set_mode("dark")
        assert Theme.is_dark() is True
        Theme.set_mode("system")
        # No crash


class TestStylesheetGeneration:
    def test_stylesheet_contains_widget_selectors(self):
        css = Theme.get_stylesheet(Theme.LIGHT)
        assert "QMainWindow" in css
        assert "QPlainTextEdit" in css
        assert "QToolBar" in css
        assert "QToolButton" in css
        assert "QMenuBar" in css
        assert "QMenu" in css
        assert "QStatusBar" in css
        assert "QLabel" in css
        assert "QLineEdit" in css  # new: for FindReplace
        assert "QPushButton" in css  # new: for FindReplace
        assert "QTreeWidget" in css  # new: for Outline

    def test_stylesheet_uses_theme_colors(self):
        colors = Theme.LIGHT
        css = Theme.get_stylesheet(colors)
        assert colors.background in css
        assert colors.foreground in css
        assert colors.editor_bg in css

    def test_preview_css_not_empty(self):
        css = Theme.get_preview_css(Theme.LIGHT)
        assert len(css) > 0
        assert "body" in css
        assert "h1" in css

    def test_preview_css_adapts_highlight_to_theme(self):
        light_css = Theme.get_preview_css(Theme.LIGHT)
        dark_css = Theme.get_preview_css(Theme.DARK)
        # Light theme should have light highlight bg, dark should have dark
        assert "#f6f8fa" in light_css  # light highlight bg
        assert "#272822" in dark_css   # dark highlight bg
