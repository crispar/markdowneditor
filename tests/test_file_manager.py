"""Tests for FileManager — pure Python, no Qt UI dependencies."""
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.file_manager import FileManager


class TestFileManager:
    def setup_method(self):
        self.settings = MagicMock()
        self.settings.value = MagicMock(return_value=[])
        self.fm = FileManager(self.settings)

    def test_initial_state(self):
        assert self.fm.current_file is None
        assert self.fm._dirty is False
        assert self.fm._saved_text == ""
        assert self.fm.recent_files == []

    def test_mark_dirty(self):
        assert self.fm.mark_dirty("changed") is True
        assert self.fm._dirty is True

    def test_mark_dirty_no_change(self):
        assert self.fm.mark_dirty("") is False  # matches _saved_text=""
        assert self.fm._dirty is False

    def test_mark_dirty_already_dirty(self):
        self.fm._dirty = True
        assert self.fm.mark_dirty("any") is False  # already dirty

    def test_mark_saved(self):
        self.fm._dirty = True
        self.fm.mark_saved("saved text")
        assert self.fm._dirty is False
        assert self.fm._saved_text == "saved text"

    def test_new_file(self):
        self.fm.current_file = Path("/some/file.md")
        self.fm._dirty = True
        self.fm._saved_text = "content"
        self.fm.new_file()
        assert self.fm.current_file is None
        assert self.fm._dirty is False
        assert self.fm._saved_text == ""

    def test_get_title_no_file(self):
        assert self.fm.get_title() == "Markdown Editor"

    def test_get_title_with_file(self):
        self.fm.current_file = Path("/path/to/doc.md")
        assert self.fm.get_title() == "doc.md - Markdown Editor"

    def test_get_title_dirty(self):
        self.fm._dirty = True
        assert self.fm.get_title() == "* Markdown Editor"

    def test_get_title_dirty_with_file(self):
        self.fm.current_file = Path("/path/to/doc.md")
        self.fm._dirty = True
        assert self.fm.get_title() == "* doc.md - Markdown Editor"

    def test_write_and_load_file(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode='w') as f:
            test_path = f.name
        try:
            self.fm.write_file(Path(test_path), "# Hello")
            content = self.fm.load_file(test_path)
            assert content == "# Hello"
            assert self.fm.current_file == Path(test_path)
            assert self.fm._dirty is False
            assert self.fm._saved_text == "# Hello"
        finally:
            Path(test_path).unlink()

    def test_add_recent_file(self):
        self.fm.add_recent_file("/a.md")
        assert "/a.md" in self.fm.recent_files

    def test_add_recent_file_deduplicates(self):
        self.fm.add_recent_file("/a.md")
        self.fm.add_recent_file("/b.md")
        self.fm.add_recent_file("/a.md")
        assert self.fm.recent_files == ["/a.md", "/b.md"]

    def test_clear_recent_files(self):
        self.fm.add_recent_file("/a.md")
        self.fm.clear_recent_files()
        assert self.fm.recent_files == []

    def test_get_initial_dir_with_file(self):
        self.fm.current_file = Path("/path/to/doc.md")
        assert self.fm.get_initial_dir() == str(Path("/path/to"))

    def test_get_initial_dir_no_file(self):
        self.settings.value = MagicMock(return_value="")
        assert self.fm.get_initial_dir() == ""

    def test_is_dirty_property(self):
        assert self.fm.is_dirty is False
        self.fm._dirty = True
        assert self.fm.is_dirty is True
