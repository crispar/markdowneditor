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

    def save_image_from_url(self, url: str) -> Optional[str]:
        try:
            self.ensure_images_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]

            # Determine extension from URL or default to png
            ext = self._get_extension_from_url(url)
            filename = f"image_{timestamp}_{unique_id}{ext}"
            filepath = self.images_dir / filename

            # Download image with headers to avoid 403
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            with urllib.request.urlopen(request, timeout=10) as response:
                content_type = response.headers.get('Content-Type', '')

                # Verify it's an image
                if not content_type.startswith('image/'):
                    return None

                # Adjust extension based on content type
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'

                filename = f"image_{timestamp}_{unique_id}{ext}"
                filepath = self.images_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(response.read())

            return f"images/{filename}"

        except Exception as e:
            print(f"Failed to download image: {e}")
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
