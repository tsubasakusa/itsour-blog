from PIL import Image
from pathlib import Path
import uuid

UPLOAD_BASE = Path("uploads")
ORIGINAL_DIR = UPLOAD_BASE / "original"
MEDIUM_DIR = UPLOAD_BASE / "medium"
THUMBNAIL_DIR = UPLOAD_BASE / "thumbnail"

for d in [ORIGINAL_DIR, MEDIUM_DIR, THUMBNAIL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

MEDIUM_WIDTH = 800
THUMBNAIL_WIDTH = 300
JPEG_QUALITY = 85


def process_image(file_path: str, filename: str) -> dict:
    """Process uploaded image: generate original (compressed), medium, and thumbnail versions.

    Returns dict with original_path, medium_path, thumbnail_path, width, height, file_size.
    """
    img = Image.open(file_path)
    width, height = img.size

    # Generate a unique prefix
    prefix = uuid.uuid4().hex[:8]
    safe_name = f"{prefix}_{filename}"

    # Convert RGBA to RGB for JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Save original (compressed)
    original_path = ORIGINAL_DIR / safe_name
    img.save(str(original_path), quality=JPEG_QUALITY, optimize=True)
    file_size = original_path.stat().st_size

    # Medium (800px wide)
    medium_path = MEDIUM_DIR / safe_name
    if width > MEDIUM_WIDTH:
        ratio = MEDIUM_WIDTH / width
        medium_size = (MEDIUM_WIDTH, int(height * ratio))
        medium_img = img.resize(medium_size, Image.LANCZOS)
        medium_img.save(str(medium_path), quality=JPEG_QUALITY, optimize=True)
    else:
        img.save(str(medium_path), quality=JPEG_QUALITY, optimize=True)

    # Thumbnail (300px wide)
    thumbnail_path = THUMBNAIL_DIR / safe_name
    if width > THUMBNAIL_WIDTH:
        ratio = THUMBNAIL_WIDTH / width
        thumb_size = (THUMBNAIL_WIDTH, int(height * ratio))
        thumb_img = img.resize(thumb_size, Image.LANCZOS)
        thumb_img.save(str(thumbnail_path), quality=JPEG_QUALITY, optimize=True)
    else:
        img.save(str(thumbnail_path), quality=JPEG_QUALITY, optimize=True)

    return {
        "original_path": str(original_path),
        "medium_path": str(medium_path),
        "thumbnail_path": str(thumbnail_path),
        "width": width,
        "height": height,
        "file_size": file_size,
        "safe_name": safe_name,
    }


def delete_image_files(image) -> None:
    """Delete all size variants of an image from disk."""
    for path_str in [image.filepath, image.medium_path, image.thumbnail_path]:
        if path_str:
            p = Path(path_str)
            if p.exists():
                p.unlink()
