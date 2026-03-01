import os
import re
import uuid
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QMimeData
from PySide6.QtGui import QImage


class ImageHandler:
    # Supported image extensions
    IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')

    # URL pattern for images
    IMAGE_URL_PATTERN = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+\.(?:png|jpg|jpeg|gif|bmp|webp)(?:\?[^\s]*)?',
        re.IGNORECASE
    )

    # Generic URL pattern (for URLs without extension like Google's)
    GENERIC_URL_PATTERN = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+',
        re.IGNORECASE
    )

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.images_dir = self.base_path / "images"

    def ensure_images_dir(self) -> Path:
        self.images_dir.mkdir(parents=True, exist_ok=True)
        return self.images_dir

    def save_image_from_clipboard(self, mime_data: QMimeData) -> Optional[str]:
        if not mime_data.hasImage():
            return None

        image = QImage(mime_data.imageData())
        if image.isNull():
            return None

        self.ensure_images_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        filename = f"image_{timestamp}_{unique_id}.png"
        filepath = self.images_dir / filename

        if image.save(str(filepath), "PNG"):
            return f"images/{filename}"
        return None

    # Image magic bytes signatures
    IMAGE_SIGNATURES = {
        b'\x89PNG\r\n\x1a\n': '.png',
        b'\xff\xd8\xff': '.jpg',
        b'GIF87a': '.gif',
        b'GIF89a': '.gif',
        b'RIFF': '.webp',  # WebP starts with RIFF
        b'BM': '.bmp',
    }

    def save_image_from_url(self, url: str) -> Optional[str]:
        try:
            self.ensure_images_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]

            # Download with headers to avoid 403
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': url,
                }
            )

            with urllib.request.urlopen(request, timeout=15) as response:
                data = response.read()

                # Check for image by magic bytes
                ext = self._detect_image_type(data)
                if ext is None:
                    # Not a valid image
                    return None

                filename = f"image_{timestamp}_{unique_id}{ext}"
                filepath = self.images_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(data)

            return f"images/{filename}"

        except Exception as e:
            self.last_error = f"Failed to download image: {e}"
            return None

    def _detect_image_type(self, data: bytes) -> Optional[str]:
        """Detect image type from magic bytes"""
        if len(data) < 12:
            return None

        for signature, ext in self.IMAGE_SIGNATURES.items():
            if data.startswith(signature):
                # Special check for WebP (RIFF....WEBP)
                if signature == b'RIFF' and data[8:12] != b'WEBP':
                    continue
                return ext

        return None

    def _get_extension_from_url(self, url: str) -> str:
        # Remove query parameters
        clean_url = url.split('?')[0]

        for ext in self.IMAGE_EXTENSIONS:
            if clean_url.lower().endswith(ext):
                return ext

        return '.png'  # Default

    def is_image_url(self, text: str) -> bool:
        text = text.strip()

        # Check if it's an image URL with extension
        if self.IMAGE_URL_PATTERN.match(text):
            return True

        # Check for common image hosting patterns
        image_hosts = [
            'googleusercontent.com',
            'imgur.com',
            'i.imgur.com',
            'cdn.discordapp.com',
            'media.discordapp.net',
            'pbs.twimg.com',
            'images.unsplash.com',
        ]

        for host in image_hosts:
            if host in text and self.GENERIC_URL_PATTERN.match(text):
                return True

        return False

    def get_markdown_image_syntax(self, image_path: str, alt_text: str = "image") -> str:
        return f"![{alt_text}]({image_path})"

    def resolve_image_path(self, relative_path: str) -> Path:
        return self.base_path / relative_path

    def set_base_path(self, path: str):
        self.base_path = Path(path)
        self.images_dir = self.base_path / "images"
