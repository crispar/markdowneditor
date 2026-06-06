"""Tests for the runtime-drawn toolbar / app icons."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.editor.icons import make_icon, make_app_icon, icon_names


class TestIcons:
    def test_all_named_icons_render_non_null(self, qapp):
        for name in icon_names():
            icon = make_icon(name, "#333333", 32)
            assert not icon.isNull(), f"icon '{name}' is null"
            pm = icon.pixmap(32, 32)
            assert pm.width() == 32 and pm.height() == 32

    def test_icon_count_matches_toolbar(self, qapp):
        # 16 formatting actions are expected on the toolbar
        assert len(icon_names()) == 16

    def test_unknown_icon_is_transparent_not_crash(self, qapp):
        icon = make_icon("does_not_exist", "#000000", 32)
        assert not icon.isNull()  # blank pixmap, but a valid icon

    def test_app_icon_renders(self, qapp):
        icon = make_app_icon(128)
        assert not icon.isNull()
        assert icon.pixmap(128, 128).width() == 128
