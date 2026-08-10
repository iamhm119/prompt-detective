"""Hybrid file storage service supporting both cloud and local backends."""

import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Optional

from fastapi import UploadFile

from ..core.config import settings
from .cloud_storage import upload_file_to_cloud

SERVICE_DIR = Path(__file__).resolve().parent
APP_DIR = SERVICE_DIR.parent
BACKEND_ROOT = APP_DIR.parent


def _resolve_upload_directory() -> Path:
    """Return absolute path to the upload directory, creating it if needed."""

    upload_dir = Path(settings.UPLOAD_DIR)
    if not upload_dir.is_absolute():
        upload_dir = (BACKEND_ROOT / upload_dir).resolve()

    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


async def save_upload_file(file: UploadFile, user_id: int) -> Dict[str, Optional[str]]:
    """
    Persist an uploaded file and return metadata for downstream processing.

    The return payload includes the cloud URL (if any), storage identifier,
    local filesystem path, and the storage provider used.
    """

    storage_metadata: Dict[str, Optional[str]] = {}
    temp_path: Optional[str] = None

    try:
        # Create a unique filename regardless of backend
        file_extension = Path(file.filename or "").suffix
        unique_filename = f"{user_id}_{uuid.uuid4()}{file_extension}"

        # Write the uploaded file to a temporary file first
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        if settings.cloud_storage_configured:
            # Upload to Cloudinary and keep temp file for processing/cleanup
            file_url, public_id = upload_file_to_cloud(
                temp_path,
                unique_filename,
                file.content_type or "application/octet-stream",
            )

            storage_metadata = {
                "file_url": file_url,
                "public_id": public_id,
                "temp_path": temp_path,
                "storage": "cloud",
                "content_type": file.content_type,
            }
        else:
            # Persist to local storage directory
            upload_dir = _resolve_upload_directory()
            destination = upload_dir / unique_filename
            shutil.move(temp_path, destination)

            base_url = (settings.PUBLIC_API_BASE_URL or "").rstrip("/")
            relative_url = f"/static/uploads/{unique_filename}"
            file_url = f"{base_url}{relative_url}" if base_url else relative_url

            storage_metadata = {
                "file_url": file_url,
                "public_id": None,
                "actual_path": str(destination),
                "storage": "local",
                "content_type": file.content_type,
            }

            # Local files are now at the destination; don't clean up temp separately
            temp_path = None

        return storage_metadata

    except Exception as exc:  # noqa: B902
        print(f"❌ Error saving upload file: {exc}")
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def cleanup_temp_file(temp_path: str):
    """Clean up temporary files created during upload processing."""

    try:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
    except Exception as exc:  # noqa: B902
        print(f"⚠️ Warning: Could not clean up temp file {temp_path}: {exc}")


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""

    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0