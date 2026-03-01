"""FileManager — handles file I/O, dirty state, and recent files.

Separated from MainWindow to follow Single Responsibility Principle.
No UI dependencies — pure Python + QSettings for persistence.
"""
from pathlib import Path

from src.constants import MAX_RECENT_FILES


class FileManager:
    def __init__(self, settings):
        self.settings = settings
        self.current_file = None
        self.base_path = Path.cwd()
        self._dirty = False
        self._saved_text = ""
        self.recent_files = self._load_recent_files()

    @property
    def is_dirty(self):
        return self._dirty

    def get_initial_dir(self):
        if self.current_file:
            return str(self.current_file.parent)
        last_dir = self.settings.value("last_directory", "")
        if last_dir and Path(last_dir).exists():
            return last_dir
        return ""

    def load_file(self, file_path):
        """Load file content. Returns content string. Raises OSError on failure."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.current_file = Path(file_path)
        self.base_path = self.current_file.parent
        self._dirty = False
        self._saved_text = content
        self.add_recent_file(file_path)
        self.settings.setValue("last_directory", str(self.current_file.parent))
        return content

    def write_file(self, path, content):
        """Write content to file. Raises OSError on failure."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def mark_dirty(self, current_text):
        """Mark as dirty if text differs from saved. Returns True if state changed."""
        if not self._dirty and current_text != self._saved_text:
            self._dirty = True
            return True
        return False

    def mark_saved(self, text):
        """Clear dirty flag after save."""
        self._dirty = False
        self._saved_text = text

    def new_file(self):
        """Reset state for a new file."""
        self.current_file = None
        self._dirty = False
        self._saved_text = ""

    def get_title(self):
        """Get window title string based on current state."""
        title = "Markdown Editor"
        if self.current_file:
            title = f"{self.current_file.name} - {title}"
        if self._dirty:
            title = f"* {title}"
        return title

    # ===== Recent Files =====

    def _load_recent_files(self):
        files = self.settings.value("recent_files", [])
        if files is None:
            return []
        return [f for f in files if Path(f).exists()]

    def save_recent_files(self):
        self.settings.setValue("recent_files", self.recent_files)

    def add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:MAX_RECENT_FILES]
        self.save_recent_files()

    def clear_recent_files(self):
        self.recent_files = []
        self.save_recent_files()
