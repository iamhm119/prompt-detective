"""
Thumbnail generation service for images and videos
"""
import os
import shutil
from pathlib import Path

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    print("⚠️ PIL/Pillow not available for image thumbnails")
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    print("⚠️ OpenCV not available for video thumbnails")
    CV2_AVAILABLE = False

# Thumbnail directory - place in backend/thumbnails to match static serving
current_dir = Path(__file__).parent.parent  # Go up to backend/app -> backend/
THUMBNAIL_DIR = current_dir / "thumbnails"
THUMBNAIL_DIR.mkdir(exist_ok=True)
print(f"🔧 Thumbnail directory: {THUMBNAIL_DIR.absolute()}")

def generate_image_thumbnail(image_path: str, max_size: int = 512) -> str:
    """Generate thumbnail for image file"""
    if not PIL_AVAILABLE:
        print("❌ PIL not available, cannot generate image thumbnail")
        return None
        
    try:
        print(f"🔧 Generating image thumbnail for: {image_path}")
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Calculate thumbnail size maintaining aspect ratio
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Generate thumbnail filename
            original_name = Path(image_path).stem
            thumbnail_name = f"{original_name}_thumb.jpg"
            thumbnail_path = THUMBNAIL_DIR / thumbnail_name
            
            # Save thumbnail
            img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
            
            print(f"✅ Generated image thumbnail: {thumbnail_path}")
            return str(thumbnail_path.absolute())
            
    except Exception as e:
        print(f"❌ Failed to generate image thumbnail: {e}")
        return None

def generate_video_thumbnail(video_path: str, max_size: int = 512) -> str:
    """Generate thumbnail from first frame of video"""
    if not CV2_AVAILABLE:
        print("❌ OpenCV not available, cannot generate video thumbnail")
        return None
        
    try:
        print(f"🔧 Generating video thumbnail for: {video_path}")
        # Open video file
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"❌ Cannot open video file: {video_path}")
            return None
        
        # Read first frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print(f"❌ Cannot read frame from video: {video_path}")
            return None
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        if not PIL_AVAILABLE:
            print("❌ PIL not available for image processing")
            return None
            
        img = Image.fromarray(frame_rgb)
        
        # Calculate thumbnail size maintaining aspect ratio
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Generate thumbnail filename
        original_name = Path(video_path).stem
        thumbnail_name = f"{original_name}_thumb.jpg"
        thumbnail_path = THUMBNAIL_DIR / thumbnail_name
        
        # Save thumbnail
        img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
        
        print(f"✅ Generated video thumbnail: {thumbnail_path}")
        return str(thumbnail_path.absolute())
        
    except Exception as e:
        print(f"❌ Failed to generate video thumbnail: {e}")
        return None

def copy_existing_thumbnail(source_path: str, target_name: str) -> str:
    """Copy existing thumbnail to thumbnails directory"""
    try:
        if not os.path.exists(source_path):
            return None
            
        target_path = THUMBNAIL_DIR / f"{target_name}_thumb.jpg"
        shutil.copy2(source_path, target_path)
        
        print(f"✅ Copied thumbnail: {target_path}")
        return str(target_path.absolute())
        
    except Exception as e:
        print(f"❌ Failed to copy thumbnail: {e}")
        return None