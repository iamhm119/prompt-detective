"""
Cloud storage service for handling uploads and thumbnails
Uses Cloudinary for free image/video storage
"""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Tuple
from pathlib import Path

# Initialize Cloudinary (will be configured via environment variables)
def init_cloudinary():
    """Initialize Cloudinary with environment variables"""
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )

def upload_file_to_cloud(file_path: str, filename: str, content_type: str) -> Tuple[str, str]:
    """
    Upload file to Cloudinary and return (public_url, public_id)
    """
    try:
        init_cloudinary()
        
        # Determine resource type based on content type
        resource_type = "video" if content_type.startswith("video") else "image"
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_path,
            public_id=f"prompt-detective/{filename}",
            resource_type=resource_type,
            overwrite=True,
            transformation=[
                {"quality": "auto", "fetch_format": "auto"}
            ] if resource_type == "image" else []
        )
        
        return result["secure_url"], result["public_id"]
    
    except Exception as e:
        print(f"❌ Failed to upload to Cloudinary: {e}")
        raise

def generate_thumbnail_url(public_id: str, content_type: str) -> str:
    """
    Generate thumbnail URL from Cloudinary public_id
    """
    try:
        init_cloudinary()
        
        if content_type.startswith("video"):
            # Generate video thumbnail
            thumbnail_url = cloudinary.CloudinaryVideo(public_id).build_url(
                start_offset="auto",
                duration="1.0",
                crop="fill",
                width=200,
                height=200,
                quality="auto",
                format="jpg"
            )
        else:
            # Generate image thumbnail
            thumbnail_url = cloudinary.CloudinaryImage(public_id).build_url(
                crop="fill",
                width=200,
                height=200,
                quality="auto",
                format="jpg"
            )
        
        return thumbnail_url
    
    except Exception as e:
        print(f"❌ Failed to generate thumbnail URL: {e}")
        return ""

def delete_file_from_cloud(public_id: str, content_type: str) -> bool:
    """
    Delete file from Cloudinary
    """
    try:
        init_cloudinary()
        
        resource_type = "video" if content_type.startswith("video") else "image"
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        
        return result.get("result") == "ok"
    
    except Exception as e:
        print(f"❌ Failed to delete from Cloudinary: {e}")
        return False