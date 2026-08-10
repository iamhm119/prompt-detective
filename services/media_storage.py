"""
Media storage utilities: persist uploaded files and generate thumbnails.
"""
from __future__ import annotations
from pathlib import Path
import os
import shutil
import time
import cv2
from typing import Optional

BASE_UPLOAD_DIR = Path("user_uploads")
BASE_THUMB_DIR = Path("thumbnails")


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def get_user_dir(user_id: int) -> Path:
    """Return persistent directory for a user's uploads."""
    user_dir = BASE_UPLOAD_DIR / str(user_id)
    _ensure_dir(user_dir)
    return user_dir


def safe_filename(filename: str) -> str:
    """Create a safe filename preserving extension with a timestamp suffix to avoid collisions."""
    name = Path(filename).stem
    ext = Path(filename).suffix
    # Basic cleanup
    name = "".join(c for c in name if c.isalnum() or c in ("-", "_")) or "file"
    ts = time.strftime("%Y%m%d_%H%M%S")
    return f"{name}_{ts}{ext}"


def save_uploaded_file(user_id: int, filename: str, data: bytes) -> str:
    """Persist an uploaded file under user_uploads/<user_id>/ and return absolute path (str)."""
    user_dir = get_user_dir(user_id)
    out_name = safe_filename(filename)
    out_path = user_dir / out_name
    with open(out_path, "wb") as f:
        f.write(data)
    return str(out_path)


def generate_image_thumbnail(image_path: str, max_width: int = 512) -> Optional[str]:
    """Create a JPEG thumbnail for an image and return its path. Returns None if failed."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        h, w = img.shape[:2]
        if w > max_width:
            scale = max_width / float(w)
            new_size = (max_width, int(h * scale))
            img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
        # Ensure thumbnail dir exists
        _ensure_dir(BASE_THUMB_DIR)
        base = Path(image_path).stem
        thumb_path = BASE_THUMB_DIR / f"{base}_thumb.jpg"
        cv2.imwrite(str(thumb_path), img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        return str(thumb_path)
    except Exception:
        return None


def generate_video_thumbnail(video_path: str, max_width: int = 512) -> Optional[str]:
    """Capture the first frame of a video and save as thumbnail JPEG; return path or None."""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        ok, frame = cap.read()
        cap.release()
        if not ok or frame is None:
            return None
        h, w = frame.shape[:2]
        if w > max_width:
            scale = max_width / float(w)
            frame = cv2.resize(frame, (max_width, int(h * scale)), interpolation=cv2.INTER_AREA)
        _ensure_dir(BASE_THUMB_DIR)
        base = Path(video_path).stem
        thumb_path = BASE_THUMB_DIR / f"{base}_thumb.jpg"
        cv2.imwrite(str(thumb_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        return str(thumb_path)
    except Exception:
        return None
