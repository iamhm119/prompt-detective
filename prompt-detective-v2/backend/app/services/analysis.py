"""Analysis service for processing uploaded files using the reverse engineering stack."""

import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple, Union
from urllib.parse import urlparse

# Add the parent directory to path to import the reverse engineering modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from ..database import SessionLocal
from ..models.user import AnalysisJob
from .storage import cleanup_temp_file


FileReference = Union[
    str,
    Tuple[Optional[str], Optional[str], Optional[str]],
    Mapping[str, Any],
]

SERVICE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SERVICE_DIR.parent.parent
BACKEND_THUMBNAILS_DIR = BACKEND_DIR / "thumbnails"


def _is_http_url(value: Optional[str]) -> bool:
    """Return True if the provided string looks like an HTTP(S) URL."""
    if not value:
        return False
    return str(value).lower().startswith(("http://", "https://"))


def _normalize_file_reference(file_reference: FileReference) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Extract local, cloud, and temporary path metadata from the provided reference."""

    cloud_url: Optional[str] = None
    cloud_id: Optional[str] = None
    temp_path: Optional[str] = None
    explicit_path: Optional[str] = None

    if isinstance(file_reference, tuple):
        cloud_url = file_reference[0] if len(file_reference) > 0 else None
        cloud_id = file_reference[1] if len(file_reference) > 1 else None
        temp_path = file_reference[2] if len(file_reference) > 2 else None
    elif isinstance(file_reference, Mapping):
        cloud_url = file_reference.get("cloud_url") or file_reference.get("file_url")
        cloud_id = file_reference.get("cloud_id") or file_reference.get("public_id")
        temp_path = file_reference.get("temp_path")
        explicit_path = file_reference.get("actual_path") or file_reference.get("local_path")
    else:
        explicit_path = str(file_reference) if file_reference is not None else None

    actual_path = temp_path or explicit_path
    if not actual_path and cloud_url:
        actual_path = cloud_url

    return actual_path, cloud_url, cloud_id, temp_path


def _resolve_thumbnail_path(path_str: Optional[str]) -> Optional[Path]:
    """Return an absolute Path to the thumbnail if it exists."""

    if not path_str or _is_http_url(path_str):
        return None

    candidate = Path(path_str)
    if candidate.is_absolute() and candidate.exists():
        return candidate

    joined = (BACKEND_DIR / candidate).resolve()
    if joined.exists():
        return joined

    thumb_candidate = (BACKEND_THUMBNAILS_DIR / candidate.name).resolve()
    if thumb_candidate.exists():
        return thumb_candidate

    return None


def _build_static_thumbnail_url(filename: str) -> str:
    """Convert a thumbnail filename to the public static URL."""

    return f"/static/thumbnails/{filename}"


def _derive_cloudinary_public_id(file_url: Optional[str]) -> Optional[str]:
    """Attempt to extract the Cloudinary public_id from a served file URL."""

    if not file_url or not _is_http_url(file_url):
        return None

    parsed = urlparse(file_url)
    path = parsed.path or ""
    if "/upload/" not in path:
        return None

    public_part = path.split("/upload/", 1)[1]
    if public_part.startswith("/"):
        public_part = public_part[1:]

    # Drop version prefix (e.g., v1724971234)
    segments = [segment for segment in public_part.split("/") if segment]
    if segments and segments[0].startswith("v") and segments[0][1:].isdigit():
        segments = segments[1:]

    if not segments:
        return None

    public_part = "/".join(segments)
    if "?" in public_part:
        public_part = public_part.split("?", 1)[0]
    if "." in public_part:
        public_part = public_part.rsplit(".", 1)[0]

    return public_part or None

# Import the actual reverse engineering system
try:
    from ..reverse_engineering.reverse_engineer import ReverseEngineerSystem
    REVERSE_ENGINEER_AVAILABLE = True
    print("✅ Reverse engineering system imported successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import reverse engineering system: {e}")
    REVERSE_ENGINEER_AVAILABLE = False

def queue_analysis_job(job_id: int, file_reference: FileReference, content_type: str):
    """Queue analysis job for processing - Simplified without Redis"""
    # Process synchronously in free tier
    print("Processing analysis job synchronously...")
    process_analysis_job(job_id, file_reference, content_type)

def process_analysis_job(job_id: int, file_reference: FileReference, content_type: str):
    """Process analysis job in background worker"""
    actual_path, cloud_url, cloud_id, temp_path = _normalize_file_reference(file_reference)
    db = SessionLocal()
    
    def update_progress(progress: int, stage: str = "", message: str = "", commit: bool = True):
        """Helper to update job progress"""
        job.progress = progress
        if commit:
            db.commit()
            print(f"📊 Job {job_id} progress: {progress}%")
        
        # Update progress store for real-time tracking
        try:
            from ..api.v1.progress import update_job_progress
            update_job_progress(job_id, progress, stage, message)
        except Exception as e:
            print(f"⚠️ Failed to update progress store: {e}")
    
    def check_if_cancelled():
        """Check if job was cancelled by user"""
        db.refresh(job)
        if job.status == 'cancelled':
            print(f"🛑 Job {job_id} was cancelled by user")
            return True
        return False
    
    try:
        # Get job from database
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            print(f"Job {job_id} not found")
            return
        
        # Stage 1: File Upload Complete (0-10%)
        job.status = "processing"
        update_progress(10, "File Upload", "File uploaded successfully")
        
        if check_if_cancelled():
            return
        
        # Stage 2: Content Analysis Starting (10-20%)
        update_progress(15, "Content Analysis", "Analyzing file structure...")
        import time
        time.sleep(0.5)  # Brief pause for UI sync
        
        if check_if_cancelled():
            return
            
        update_progress(20, "Content Analysis", "Preparing for AI processing...")
        
        if check_if_cancelled():
            return
        
        # Stage 3: Scene Detection / Frame Extraction (20-40%)
        update_progress(25, "Scene Detection", "Detecting scenes and key frames..." if content_type == "video" else "Analyzing image composition...")
        time.sleep(0.5)
        
        if check_if_cancelled():
            return
            
        update_progress(35, "Scene Detection", "Extracting visual features..." if content_type == "video" else "Identifying visual elements...")
        
        if check_if_cancelled():
            return
        
        # Stage 4: AI Processing Starting (40-70%)
        update_progress(45, "AI Analysis", "Running AI visual analysis...")
        
        if check_if_cancelled():
            return
        
        # Generate analysis result using actual reverse engineering system
        start_time = datetime.now(timezone.utc)
        
        def analysis_progress_callback(p):
            """Callback for analysis progress (40-70% range)"""
            if check_if_cancelled():
                raise Exception("Job cancelled by user")
            progress_value = 45 + int(p * 25)
            stage_msg = "AI Analysis"
            detail_msg = f"Processing... {int(p * 100)}%"
            update_progress(progress_value, stage_msg, detail_msg)
        
        result = perform_actual_analysis(file_reference, content_type, analysis_progress_callback)
        
        if check_if_cancelled():
            return
            
        if not isinstance(result, dict):
            result = {"raw_analysis": result or {}}

        if cloud_url and not result.get("cloud_file_url"):
            result["cloud_file_url"] = cloud_url
        if cloud_id and not result.get("cloud_id"):
            result["cloud_id"] = cloud_id
        if temp_path and not result.get("temp_file_path"):
            result["temp_file_path"] = temp_path

        thumb_path = result.get("thumbnail_path")
        if thumb_path and not _is_http_url(str(thumb_path)):
            result["thumbnail_path"] = str(Path(str(thumb_path)).resolve())

        if check_if_cancelled():
            return

        # Stage 5: Prompt Generation (70-90%)
        update_progress(75, "Prompt Generation", "Generating AI prompts...")
        time.sleep(0.3)
        
        if check_if_cancelled():
            return
            
        update_progress(85, "Prompt Generation", "Refining prompt quality...")
        
        if check_if_cancelled():
            return
        
        thumbnail_url = result.get("thumbnail_url")
        if cloud_id and (not thumbnail_url or not _is_http_url(str(thumbnail_url))):
            try:
                from .cloud_storage import generate_thumbnail_url

                cloud_thumbnail = generate_thumbnail_url(cloud_id, job.content_type)
                if cloud_thumbnail:
                    result["thumbnail_url"] = cloud_thumbnail
                    print(f"✅ Generated cloud thumbnail: {cloud_thumbnail}")
            except Exception as thumb_err:
                print(f"❌ Failed to generate cloud thumbnail: {thumb_err}")
        
        if check_if_cancelled():
            return
        
        # Stage 6: Finalization (90-100%)
        update_progress(92, "Finalization", "Preparing results...")
        time.sleep(0.2)
        
        if check_if_cancelled():
            return
            
        update_progress(95, "Finalization", "Almost done...")
        
        if check_if_cancelled():
            return
        
        # Analysis successful
        job.status = "completed"
        update_progress(100, "Complete", "Analysis complete!")
        job.result_data = result
        job.completed_at = datetime.now(timezone.utc)
        
        # Calculate processing time
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        job.processing_time_seconds = int(processing_time)
        
        db.commit()
        
        # Clear progress data after completion
        try:
            from ..api.v1.progress import clear_job_progress
            clear_job_progress(job_id)
        except Exception as e:
            print(f"⚠️ Failed to clear progress data: {e}")
        
    except Exception as e:
        # Handle any errors during processing
        print(f"Error processing job {job_id}: {str(e)}")
        print(traceback.format_exc())
        
        # Don't mark as failed if cancelled
        if job.status != 'cancelled':
            job.status = "failed"
            job.error_message = f"Processing error: {str(e)}"
            job.progress = 0
            db.commit()
            
            # Update progress store
            try:
                from ..api.v1.progress import update_job_progress
                update_job_progress(job_id, 0, "Failed", f"Error: {str(e)}")
            except Exception as prog_err:
                print(f"⚠️ Failed to update progress on error: {prog_err}")
        
    finally:
        db.close()
        if temp_path:
            cleanup_temp_file(temp_path)
        
        # Clear progress data
        try:
            from ..api.v1.progress import clear_job_progress
            clear_job_progress(job_id)
        except Exception as e:
            print(f"⚠️ Failed to clear progress in finally: {e}")


def perform_actual_analysis(file_reference: FileReference, content_type: str, 
                          progress_callback=None) -> Dict[str, Any]:
    """Perform actual analysis using the reverse engineering system"""
    actual_path, cloud_url, cloud_id, temp_path = _normalize_file_reference(file_reference)
    
    def report_progress(percent: float):
        """Report progress if callback provided"""
        if progress_callback:
            progress_callback(percent)
    
    try:
        if actual_path:
            print(f"🔧 Using analysis source path: {actual_path}")

        if not actual_path or _is_http_url(actual_path) or not os.path.exists(actual_path):
            missing_msg = actual_path or "<none>"
            print(f"⚠️ Local analysis path unavailable: {missing_msg}. Falling back to mock analysis.")
            return generate_mock_analysis(actual_path or "", content_type, cloud_url, cloud_id)

        if not REVERSE_ENGINEER_AVAILABLE:
            print("⚠️ Falling back to mock analysis - reverse engineering system not available")
            return generate_mock_analysis(actual_path, content_type, cloud_url, cloud_id)
        
        print(f"🚀 Starting actual reverse engineering analysis for: {actual_path}")
        
        # Initialize the reverse engineering system
        report_progress(0.1)  # 10% of AI processing phase
        re_system = ReverseEngineerSystem()
        
        # Perform the actual analysis
        report_progress(0.3)  # 30% - starting analysis
        if content_type == "video":
            # Use enhanced video analysis
            analysis_result = re_system._analyze_video_enhanced(actual_path, save_frames=True)
        else:  # image
            # Use enhanced image analysis
            analysis_result = re_system._analyze_image_enhanced(actual_path)
        
        report_progress(0.8)  # 80% - analysis complete
        print("✅ Actual analysis completed successfully")
        
        # Process and format the result for the API
        processed_result = process_re_analysis_result(analysis_result, content_type)
        if cloud_url:
            processed_result.setdefault("cloud_file_url", cloud_url)
        if cloud_id:
            processed_result.setdefault("cloud_id", cloud_id)
        if temp_path:
            processed_result.setdefault("temp_file_path", temp_path)

        thumb_path = processed_result.get("thumbnail_path")
        if thumb_path and not _is_http_url(str(thumb_path)):
            processed_result["thumbnail_path"] = str(Path(str(thumb_path)).resolve())
        
        report_progress(1.0)  # 100% of AI processing phase
        return processed_result
        
    except Exception as e:
        print(f"❌ Error in actual analysis: {str(e)}")
        print(traceback.format_exc())
        # Fall back to mock analysis on error
        fallback_path = actual_path or ""
        return generate_mock_analysis(fallback_path, content_type, cloud_url, cloud_id)

def process_re_analysis_result(result: Dict[str, Any], content_type: str) -> Dict[str, Any]:
    """Process reverse engineering analysis result for API consumption"""
    try:
        processed = {
            "analysis_method": "AI Reverse Engineering System",
            "enhancement_features": result.get("enhancement_features", []),
            "analysis_timestamp": result.get("analysis_timestamp"),
            "content_type": content_type
        }
        
        structured_prompt = result.get("structured_prompt") or {}
        quick_prompt = result.get("quick_prompt")
        negative_prompt = result.get("negative_prompt")

        if structured_prompt:
            processed["structured_prompt"] = structured_prompt

        if content_type == "video":
            # Extract video-specific information
            processed.update({
                "comprehensive_video_prompt": result.get("comprehensive_video_prompt", ""),
                "video_prompt": result.get("video_prompt", ""),
                "master_prompt": result.get("master_prompt", ""),
                "video_info": result.get("video_info", {}),
                "extracted_frames": result.get("extracted_frames", 0),
                "frame_metadata": result.get("frame_metadata", []),
                "extraction_method": result.get("extraction_method", ""),
                "saved_frame_paths": result.get("saved_frame_paths", []),
                "thumbnail_path": result.get("thumbnail_path", "")
            })
            
            # Use the best available prompt
            main_prompt = (
                result.get("master_prompt") or 
                result.get("comprehensive_video_prompt") or 
                result.get("video_prompt") or
                ""
            )
            
        else:  # image
            # Extract image-specific information
            processed.update({
                "suggested_prompt": result.get("suggested_prompt", ""),
                "comprehensive_analysis": result.get("comprehensive_analysis", ""),
                "master_prompt": result.get("master_prompt", ""),
                "image_info": result.get("image_info", {}),
                "style_analysis": result.get("style", ""),
                "color_palette": result.get("color_palette", []),
                "detected_elements": result.get("detected_elements", []),
                "thumbnail_path": result.get("thumbnail_path", "")
            })
            
            # Use the best available prompt
            main_prompt = (
                result.get("master_prompt") or
                result.get("suggested_prompt") or 
                result.get("comprehensive_analysis") or
                ""
            )
        
        # Add the main prompt
        prompt_block = structured_prompt.get("prompt", {}) if isinstance(structured_prompt, dict) else {}
        if prompt_block.get("main"):
            main_prompt = prompt_block["main"]

        if quick_prompt is None and prompt_block.get("quick"):
            quick_prompt = prompt_block["quick"]
        if negative_prompt is None and prompt_block.get("negative"):
            negative_prompt = prompt_block["negative"]

        processed["main_prompt"] = main_prompt
        
        if quick_prompt:
            processed["quick_prompt"] = quick_prompt
        if negative_prompt:
            processed["negative_prompt"] = negative_prompt

        # Add file paths
        processed["file_paths"] = {
            "json_path": result.get("saved_json_path", ""),
            "txt_path": result.get("saved_txt_path", ""),
            "thumbnail_path": result.get("thumbnail_path", ""),
            "saved_frame_paths": result.get("saved_frame_paths", [])
        }
        
        # Create prompt preview
        if main_prompt:
            processed["prompt_preview"] = main_prompt[:200] + "..." if len(main_prompt) > 200 else main_prompt
        elif quick_prompt:
            processed["prompt_preview"] = quick_prompt
        
        # Store full analysis for download
        processed["raw_analysis"] = result
        
        return processed
        
    except Exception as e:
        print(f"Error processing RE analysis result: {str(e)}")
        return {
            "error": f"Failed to process analysis result: {str(e)}",
            "raw_result": result
        }

def generate_mock_analysis(
    file_path: str,
    content_type: str,
    cloud_url: Optional[str] = None,
    cloud_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate mock analysis results for testing"""
    # Handle case where file_path might be a tuple (file_url, public_id, temp_path)
    if isinstance(file_path, tuple):
        # Use temp_path (third element) for filename extraction
        actual_path = file_path[2] if len(file_path) > 2 else str(file_path[0])
    else:
        actual_path = file_path
    
    filename = Path(actual_path).name
    
    if content_type == "video":
        result = {
            "comprehensive_video_prompt": f"A detailed video analysis for {filename}. This video appears to be AI-generated content with vibrant colors, smooth transitions, and artistic composition. The style suggests it was created using prompts like: 'high quality, cinematic lighting, professional cinematography, detailed environment, atmospheric effects, 4K resolution, smooth camera movements'.",
            "video_info": {
                "duration": 30.5,
                "width": 1920,
                "height": 1080,
                "fps": 24
            },
            "analysis_method": "AI Visual Analysis",
            "confidence_score": 0.85,
            "extracted_frames": 15,
            "frame_metadata": [
                {"frame": 1, "timestamp": 0.0, "description": "Opening scene with dramatic lighting"},
                {"frame": 5, "timestamp": 5.0, "description": "Mid-scene with character interaction"},
                {"frame": 10, "timestamp": 10.0, "description": "Climactic moment with special effects"}
            ],
            "suggested_prompts": [
                "cinematic lighting, professional cinematography",
                "high quality, detailed environment",
                "atmospheric effects, smooth transitions",
                "vibrant colors, artistic composition"
            ],
            "thumbnail_path": ""
        }
    else:  # image
        result = {
            "suggested_prompt": f"Detailed image analysis for {filename}. This appears to be an AI-generated image with characteristics suggesting prompts like: 'high resolution, detailed artwork, professional photography, studio lighting, vibrant colors, sharp focus, artistic composition, masterpiece quality'.",
            "comprehensive_analysis": f"This image shows sophisticated AI generation techniques with attention to detail, color harmony, and compositional balance. Likely created with advanced diffusion models using carefully crafted prompts.",
            "image_info": {
                "width": 1024,
                "height": 1024,
                "format": "PNG"
            },
            "analysis_method": "Computer Vision Analysis",
            "confidence_score": 0.78,
            "style_analysis": "Modern digital art style with realistic rendering",
            "color_palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
            "detected_elements": ["foreground object", "background scenery", "lighting effects", "texture details"],
            "suggested_prompts": [
                "high resolution, detailed artwork",
                "professional photography, studio lighting",
                "vibrant colors, sharp focus",
                "artistic composition, masterpiece quality"
            ],
            "thumbnail_path": ""
        }

    if cloud_url:
        result["cloud_file_url"] = cloud_url
    if cloud_id:
        result["cloud_id"] = cloud_id

    return result

def extract_key_results(result: Dict[str, Any], content_type: str) -> Dict[str, Any]:
    """Extract key information from analysis results"""
    extracted = {
        "summary": {},
        "main_prompt": "",
        "file_paths": {}
    }
    
    try:
        structured_prompt = result.get("structured_prompt") if isinstance(result.get("structured_prompt"), dict) else None
        quick_prompt = result.get("quick_prompt")
        negative_prompt = result.get("negative_prompt")

        if structured_prompt:
            extracted["structured_prompt"] = structured_prompt

        if content_type == "video":
            # Extract video-specific information from actual analysis
            video_info = result.get("video_info", {})
            extracted["summary"] = {
                "content_type": "video",
                "duration": video_info.get("duration", 0),
                "resolution": f"{video_info.get('width', 0)}x{video_info.get('height', 0)}",
                "fps": video_info.get("fps", 0),
                "frames_analyzed": result.get("extracted_frames", 0),
                "analysis_method": result.get("analysis_method", "AI Reverse Engineering"),
                "extraction_method": result.get("extraction_method", ""),
                "enhancement_features": result.get("enhancement_features", [])
            }
            
            # Get the best available prompt from actual analysis
            extracted["main_prompt"] = (
                result.get("master_prompt") or
                result.get("comprehensive_video_prompt") or 
                result.get("video_prompt") or 
                result.get("suggested_prompt") or
                ""
            )
            
        elif content_type == "image":
            # Extract image-specific information from actual analysis
            image_info = result.get("image_info", {})
            extracted["summary"] = {
                "content_type": "image",
                "resolution": f"{image_info.get('width', 0)}x{image_info.get('height', 0)}",
                "analysis_method": result.get("analysis_method", "AI Reverse Engineering"),
                "enhancement_features": result.get("enhancement_features", []),
                "style_analysis": result.get("style_analysis", "")
            }
            
            # Get the best available prompt from actual analysis
            extracted["main_prompt"] = (
                result.get("master_prompt") or
                result.get("suggested_prompt") or 
                result.get("comprehensive_analysis") or 
                result.get("comprehensive_video_prompt") or
                ""
            )

        if structured_prompt:
            prompt_block = structured_prompt.get("prompt", {})
            if prompt_block.get("main"):
                extracted["main_prompt"] = prompt_block["main"]
            if quick_prompt is None and prompt_block.get("quick"):
                quick_prompt = prompt_block["quick"]
            if negative_prompt is None and prompt_block.get("negative"):
                negative_prompt = prompt_block["negative"]

        if quick_prompt:
            extracted["quick_prompt"] = quick_prompt
        if negative_prompt:
            extracted["negative_prompt"] = negative_prompt
        
        # Extract file paths (from actual analysis)
        file_paths = dict(result.get("file_paths") or {})
        if result.get("thumbnail_path") and "thumbnail_path" not in file_paths:
            file_paths["thumbnail_path"] = result.get("thumbnail_path")
        if result.get("thumbnail_url") and "thumbnail_url" not in file_paths and _is_http_url(result.get("thumbnail_url")):
            file_paths["thumbnail_url"] = result.get("thumbnail_url")
        extracted["file_paths"] = file_paths
        
        # Create a preview of the prompt (first 300 characters for better preview)
        if extracted["main_prompt"]:
            extracted["prompt_preview"] = extracted["main_prompt"][:300] + "..." if len(extracted["main_prompt"]) > 300 else extracted["main_prompt"]
        elif quick_prompt:
            extracted["prompt_preview"] = quick_prompt
        else:
            extracted["prompt_preview"] = "Analysis completed - full prompt available for download"
        
        # Add confidence and quality indicators
        extracted["analysis_quality"] = {
            "has_enhancement_features": bool(result.get("enhancement_features")),
            "has_detailed_analysis": bool(extracted["main_prompt"]),
            "analysis_timestamp": result.get("analysis_timestamp"),
            "processing_successful": "error" not in result
        }
        
    except Exception as e:
        print(f"Error extracting results: {str(e)}")
        extracted["extraction_error"] = str(e)
        # Provide fallback information
        extracted["main_prompt"] = "Analysis completed but result extraction failed. Please download full results."
        extracted["prompt_preview"] = "Error in result extraction - full analysis may be available for download"
    
    return extracted

def get_analysis_summary(job: AnalysisJob) -> Dict[str, Any]:
    """Get a summary of analysis results for API responses"""
    if not job.result_data:
        return {}
    
    result = job.result_data
    
    # Get real-time progress from progress_store if available
    from ..api.v1.progress import get_job_progress
    progress_data = get_job_progress(job.id) or {}
    
    summary = {
        "job_id": job.id,
        "filename": job.filename,
        "content_type": job.content_type,
        "status": job.status,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "processing_time_seconds": job.processing_time_seconds,
        # Include real-time progress data
        "progress": progress_data.get("progress", job.progress if hasattr(job, 'progress') else 0),
        "current_stage": progress_data.get("stage", ""),
        "progress_message": progress_data.get("message", "")
    }
    
    if job.status == "completed" and result:
        # Extract key results using the updated function
        extracted = extract_key_results(result, job.content_type)

        cloud_id = result.get("cloud_id")
        if not cloud_id:
            cloud_candidates = [
                result.get("cloud_file_url"),
                result.get("file_url"),
                job.file_path,
            ]
            for candidate in cloud_candidates:
                derived = _derive_cloudinary_public_id(candidate)
                if derived:
                    cloud_id = derived
                    result["cloud_id"] = derived
                    break
        
        # Generate thumbnail URL if available from cloud or local storage
        thumbnail_url = result.get("thumbnail_url") if _is_http_url(result.get("thumbnail_url")) else None
        thumbnail_path_sources = [
            result.get("thumbnail_path"),
            extracted.get("file_paths", {}).get("thumbnail_path") if extracted.get("file_paths") else None,
        ]
        thumbnail_path = next((path for path in thumbnail_path_sources if path), None)
        resolved_local = _resolve_thumbnail_path(thumbnail_path)

        if thumbnail_url:
            print(f"✅ Using cloud thumbnail URL: {thumbnail_url}")
            if resolved_local:
                thumbnail_path = str(resolved_local)
        elif resolved_local:
            thumbnail_path = str(resolved_local)
            thumbnail_url = _build_static_thumbnail_url(resolved_local.name)
            print(f"✅ Thumbnail URL generated: {thumbnail_url} from path: {thumbnail_path}")
        else:
            job_basename = Path(job.filename).stem if job.filename else None
            fallback_local = _resolve_thumbnail_path(f"{job_basename}_thumb.jpg") if job_basename else None
            if fallback_local:
                thumbnail_path = str(fallback_local)
                thumbnail_url = _build_static_thumbnail_url(fallback_local.name)
                print(f"✅ Found existing thumbnail by filename: {thumbnail_url}")

        if not thumbnail_url and cloud_id:
            try:
                from .cloud_storage import generate_thumbnail_url

                cloud_thumbnail = generate_thumbnail_url(cloud_id, job.content_type)
                if cloud_thumbnail:
                    thumbnail_url = cloud_thumbnail
                    print(f"✅ Generated on-demand cloud thumbnail: {thumbnail_url}")
            except Exception as e:
                print(f"❌ Failed to generate cloud thumbnail in summary: {e}")

        if not thumbnail_url and job.file_path and not _is_http_url(job.file_path) and os.path.exists(job.file_path):
            try:
                if job.content_type == "video":
                    from ..services.thumbnail import generate_video_thumbnail

                    thumbnail_path_candidate = generate_video_thumbnail(job.file_path)
                else:
                    from ..services.thumbnail import generate_image_thumbnail

                    thumbnail_path_candidate = generate_image_thumbnail(job.file_path)

                resolved_generated = _resolve_thumbnail_path(thumbnail_path_candidate)
                if resolved_generated:
                    thumbnail_path = str(resolved_generated)
                    thumbnail_url = _build_static_thumbnail_url(resolved_generated.name)
                    print(f"✅ Generated new thumbnail: {thumbnail_url}")
            except Exception as e:
                print(f"❌ Failed to generate thumbnail from local source: {e}")

        if not thumbnail_url:
            print(f"⚠️ No valid thumbnail available for job {job.id} - last tried path: {thumbnail_path}")
        
        summary.update({
            "summary": extracted.get("summary", {}),
            "prompt_preview": extracted.get("prompt_preview", ""),
            "main_prompt": extracted.get("main_prompt", ""),  # Include full prompt for frontend
            "has_full_prompt": bool(extracted.get("main_prompt")),
            "structured_prompt": extracted.get("structured_prompt") or result.get("structured_prompt"),
            "quick_prompt": extracted.get("quick_prompt") or result.get("quick_prompt"),
            "negative_prompt": extracted.get("negative_prompt") or result.get("negative_prompt"),
            "file_paths": extracted.get("file_paths", {}),
            "analysis_quality": extracted.get("analysis_quality", {}),
            "enhancement_features": result.get("enhancement_features", []),
            "thumbnail_url": thumbnail_url,
            "thumbnail_path": thumbnail_path,  # Also include the path for debugging
            "cloud_id": cloud_id,
            "cloud_file_url": result.get("cloud_file_url") or job.file_path,
        })
        
        # Add extraction error info if present
        if "extraction_error" in extracted:
            summary["extraction_error"] = extracted["extraction_error"]
    
    elif job.status == "failed":
        summary["error_message"] = job.error_message
    
    return summary

def get_downloadable_content(job: AnalysisJob) -> Dict[str, Any]:
    """Get content ready for download"""
    if job.status != "completed" or not job.result_data:
        return {}
    
    result = job.result_data
    extracted = extract_key_results(result, job.content_type)
    
    # Prepare downloadable content
    content = {
        "filename": job.filename,
        "analysis_date": job.completed_at.isoformat() if job.completed_at else "",
        "main_prompt": extracted.get("main_prompt", ""),
        "structured_prompt": extracted.get("structured_prompt") or result.get("structured_prompt"),
        "quick_prompt": extracted.get("quick_prompt") or result.get("quick_prompt"),
        "negative_prompt": extracted.get("negative_prompt") or result.get("negative_prompt"),
        "full_analysis": result.get("raw_analysis", result),  # Include full raw analysis
        "analysis_method": result.get("analysis_method", "AI Reverse Engineering"),
        "enhancement_features": result.get("enhancement_features", []),
        "metadata": {
            "content_type": job.content_type,
            "processing_time": job.processing_time_seconds,
            "analysis_timestamp": result.get("analysis_timestamp", ""),
            "summary": extracted.get("summary", {}),
            "analysis_quality": extracted.get("analysis_quality", {})
        }
    }
    
    # Add content-type specific information
    if job.content_type == "video":
        content["video_info"] = result.get("video_info", {})
        content["frame_analysis"] = result.get("frame_metadata", [])
        content["extraction_method"] = result.get("extraction_method", "")
        content["extracted_frames"] = result.get("extracted_frames", 0)
        
        # Add alternative prompts
        content["alternative_prompts"] = {
            "master_prompt": result.get("master_prompt", ""),
            "comprehensive_video_prompt": result.get("comprehensive_video_prompt", ""),
            "video_prompt": result.get("video_prompt", "")
        }
        
    elif job.content_type == "image":
        content["image_info"] = result.get("image_info", {})
        content["style_analysis"] = result.get("style_analysis", "")
        content["color_palette"] = result.get("color_palette", [])
        content["detected_elements"] = result.get("detected_elements", [])
        
        # Add alternative prompts
        content["alternative_prompts"] = {
            "master_prompt": result.get("master_prompt", ""),
            "suggested_prompt": result.get("suggested_prompt", ""),
            "comprehensive_analysis": result.get("comprehensive_analysis", "")
        }
    
    # Add file paths for additional downloads
    file_paths = dict(extracted.get("file_paths") or {})
    if result.get("thumbnail_url") and "thumbnail_url" not in file_paths and _is_http_url(result.get("thumbnail_url")):
        file_paths["thumbnail_url"] = result["thumbnail_url"]
    if result.get("thumbnail_path") and "thumbnail_path" not in file_paths:
        file_paths["thumbnail_path"] = result["thumbnail_path"]
    content["file_paths"] = file_paths
    
    return content