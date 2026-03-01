"""Tests for ImageHandler — image handling logic."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.image_handler import ImageHandler


class TestImageHandler:
    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.handler = ImageHandler(self.tmp_dir)

    # === Path management ===

    def test_default_base_path(self):
        h = ImageHandler()
        assert h.base_path == Path.cwd()

    def test_custom_base_path(self):
        h = ImageHandler("/some/path")
        assert h.base_path == Path("/some/path")

    def test_set_base_path(self):
        self.handler.set_base_path("/new/path")
        assert self.handler.base_path == Path("/new/path")
        assert self.handler.images_dir == Path("/new/path/images")

    def test_ensure_images_dir(self):
        result = self.handler.ensure_images_dir()
        assert result.exists()
        assert result == self.handler.images_dir

    # === URL detection ===

    def test_is_image_url_png(self):
        assert self.handler.is_image_url("https://example.com/image.png")

    def test_is_image_url_jpg(self):
        assert self.handler.is_image_url("https://example.com/photo.jpg")

    def test_is_image_url_jpeg(self):
        assert self.handler.is_image_url("https://example.com/photo.jpeg")

    def test_is_image_url_gif(self):
        assert self.handler.is_image_url("https://example.com/anim.gif")

    def test_is_image_url_webp(self):
        assert self.handler.is_image_url("https://example.com/photo.webp")

    def test_is_image_url_with_query(self):
        assert self.handler.is_image_url("https://example.com/image.png?w=800")

    def test_is_image_url_case_insensitive(self):
        assert self.handler.is_image_url("https://example.com/IMAGE.PNG")

    def test_is_image_url_imgur(self):
        assert self.handler.is_image_url("https://i.imgur.com/abc123")

    def test_is_image_url_discord(self):
        assert self.handler.is_image_url("https://cdn.discordapp.com/attachments/123/456")

    def test_not_image_url_plain_text(self):
        assert not self.handler.is_image_url("hello world")

    def test_not_image_url_non_image_ext(self):
        assert not self.handler.is_image_url("https://example.com/file.pdf")

    def test_not_image_url_empty(self):
        assert not self.handler.is_image_url("")

    # === Markdown syntax generation ===

    def test_markdown_image_syntax(self):
        result = self.handler.get_markdown_image_syntax("images/test.png")
        assert result == "![image](images/test.png)"

    def test_markdown_image_syntax_custom_alt(self):
        result = self.handler.get_markdown_image_syntax("img.png", "my photo")
        assert result == "![my photo](img.png)"

    # === Image type detection ===

    def test_detect_png(self):
        data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        assert self.handler._detect_image_type(data) == '.png'

    def test_detect_jpg(self):
        data = b'\xff\xd8\xff' + b'\x00' * 100
        assert self.handler._detect_image_type(data) == '.jpg'

    def test_detect_gif87(self):
        data = b'GIF87a' + b'\x00' * 100
        assert self.handler._detect_image_type(data) == '.gif'

    def test_detect_gif89(self):
        data = b'GIF89a' + b'\x00' * 100
        assert self.handler._detect_image_type(data) == '.gif'

    def test_detect_bmp(self):
        data = b'BM' + b'\x00' * 100
        assert self.handler._detect_image_type(data) == '.bmp'

    def test_detect_webp(self):
        data = b'RIFF' + b'\x00' * 4 + b'WEBP' + b'\x00' * 100
        assert self.handler._detect_image_type(data) == '.webp'

    def test_detect_unknown(self):
        data = b'\x00\x01\x02\x03' + b'\x00' * 100
        assert self.handler._detect_image_type(data) is None

    def test_detect_too_short(self):
        data = b'\x89PNG'
        assert self.handler._detect_image_type(data) is None

    def test_detect_riff_not_webp(self):
        """RIFF without WEBP marker should not match."""
        data = b'RIFF' + b'\x00' * 4 + b'WAVE' + b'\x00' * 100
        assert self.handler._detect_image_type(data) is None

    # === Path resolution ===

    def test_resolve_image_path(self):
        result = self.handler.resolve_image_path("images/test.png")
        expected = self.handler.base_path / "images/test.png"
        assert result == expected
