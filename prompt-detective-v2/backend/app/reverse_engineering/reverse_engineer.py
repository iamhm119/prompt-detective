"""
Enhanced AI Reverse Engineering System with Advanced Frame Selection and Accuracy Optimization
Analyzes videos and images to extract generation prompts using sophisticated algorithms
"""
import os
import json
import time
from pathlib import Path
from typing import Union, Dict, Any, List, Tuple
import cv2
from PIL import Image
import numpy as np
from datetime import datetime
import traceback

from .config import Config
from .utils import VideoProcessor, ImageProcessor, SceneDetector, AdvancedFrameSelector, EnhancedSceneDetector
from .ai_analyzer import AIAnalyzer, EnhancedPromptEngine
from ..services.thumbnail import generate_image_thumbnail, generate_video_thumbnail


class ReverseEngineerSystem:
    """Main system for reverse engineering AI-generated content"""
    
    def __init__(self):
        """Initialize the reverse engineering system"""
        self.ai_analyzer = AIAnalyzer()
        self.setup_output_directories()
    
    def setup_output_directories(self):
        """Create necessary output directories"""
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(os.path.join(Config.OUTPUT_DIR, Config.FRAMES_DIR), exist_ok=True)
    
    def analyze_content(self, file_path: str, save_frames: bool = True) -> Dict[str, Any]:
        """
        Enhanced content analysis with advanced frame selection and improved accuracy
        
        Args:
            file_path: Path to the video or image file
            save_frames: Whether to save extracted frames
            
        Returns:
            Dictionary containing analysis results
        """
        print(f"🚀 Starting enhanced analysis of: {file_path}")
        
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext in Config.VIDEO_EXTENSIONS:
                return self._analyze_video_enhanced(file_path, save_frames)
            elif file_ext in Config.IMAGE_EXTENSIONS:
                return self._analyze_image_enhanced(file_path)
            else:
                return {"error": f"Unsupported file format: {file_ext}"}
        
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "traceback": traceback.format_exc()
            }
    
    def _analyze_video_enhanced(self, video_path: str, save_frames: bool = True) -> Dict[str, Any]:
        """Enhanced video analysis with intelligent frame selection"""
        print("🎬 Enhanced video analysis starting...")
        
        # Initialize enhanced video processor
        video_processor = VideoProcessor(video_path)
        video_info = video_processor.get_video_info()
        
        print(f"📹 Video info: {video_info['duration']:.1f}s, {video_info['fps']:.1f}fps, {video_info['width']}x{video_info['height']}")
        
        # Calculate optimal frame count based on video duration
        optimal_frames = self._calculate_optimal_frame_count(video_info)
        print(f"🎯 Targeting {optimal_frames} optimal frames for analysis")
        
        # Extract key frames using advanced algorithms
        frames_with_metadata = video_processor.extract_key_frames_advanced(
            max_frames=optimal_frames,
            use_scene_detection=True,
            use_motion_analysis=True,
            use_importance_scoring=True
        )
        
        if not frames_with_metadata:
            return {"error": "No frames could be extracted from video"}
        
        print(f"✅ Extracted {len(frames_with_metadata)} key frames with metadata")
        
        # Save frames if requested
        saved_frame_paths = []
        if save_frames:
            saved_frame_paths = self._save_extracted_frames_enhanced(frames_with_metadata, video_path)
        
        # Enhanced AI analysis
        analysis_result = self.ai_analyzer.analyze_video_frames(
            [(frame, ts) for frame, ts, _ in frames_with_metadata], 
            video_info
        )
        
        # Compile enhanced result
        result = {
            "content_type": "video",
            "source_file": video_path,
            "analysis_timestamp": datetime.now().isoformat(),
            "video_info": video_info,
            "extraction_method": "advanced_intelligent_selection",
            "frame_metadata": [metadata for _, _, metadata in frames_with_metadata],
            "extracted_frames": len(frames_with_metadata),
            "saved_frame_paths": saved_frame_paths,
            "enhancement_features": [
                "scene_detection",
                "motion_analysis", 
                "importance_scoring",
                "visual_diversity_selection",
                "multi_pass_ai_analysis"
            ],
            **analysis_result
        }
        
        # Save enhanced results
        json_path, txt_path = self._save_analysis_result(result, Path(video_path).stem)
        # Create thumbnail
        thumb_path = generate_video_thumbnail(video_path)
        result.update({
            "saved_json_path": json_path,
            "saved_txt_path": txt_path,
            "thumbnail_path": thumb_path or ""
        })
        
        print("✅ Enhanced video analysis completed successfully!")
        return result
    
    def _analyze_image_enhanced(self, image_path: str) -> Dict[str, Any]:
        """Enhanced image analysis with multiple validation passes"""
        print("🖼️ Enhanced image analysis starting...")
        
        # Load and preprocess image
        image = cv2.imread(image_path)
        if image is None:
            return {"error": f"Could not load image: {image_path}"}
        
        # Resize if too large but maintain quality
        image = ImageProcessor.resize_image(image, Config.FRAME_RESIZE_WIDTH)
        
        # Get image information
        height, width = image.shape[:2]
        image_info = {
            "width": width,
            "height": height,
            "channels": image.shape[2] if len(image.shape) > 2 else 1
        }
        
        print(f"📸 Image info: {width}x{height} pixels")
        
        # Enhanced AI analysis with multiple passes
        analysis_result = self.ai_analyzer.analyze_image_with_enhanced_accuracy(image)
        
        # Compile enhanced result
        result = {
            "content_type": "image",
            "source_file": image_path,
            "analysis_timestamp": datetime.now().isoformat(),
            "image_info": image_info,
            "analysis_method": "multi_pass_enhanced_accuracy",
            "enhancement_features": [
                "technical_analysis_pass",
                "creative_analysis_pass", 
                "prompt_focused_analysis",
                "expert_synthesis"
            ],
            **analysis_result
        }
        
        # Save enhanced results
        json_path, txt_path = self._save_analysis_result(result, Path(image_path).stem)
        # Create thumbnail
        thumb_path = generate_image_thumbnail(image_path)
        result.update({
            "saved_json_path": json_path,
            "saved_txt_path": txt_path,
            "thumbnail_path": thumb_path or ""
        })
        
        print("✅ Enhanced image analysis completed successfully!")
        return result
    
    def _calculate_optimal_frame_count(self, video_info: Dict) -> int:
        """Calculate optimal number of frames based on video characteristics"""
        duration = video_info.get('duration', 0)
        fps = video_info.get('fps', 30)
        
        # Base frame count on video duration
        if duration <= 5:
            base_frames = 5
        elif duration <= 15:
            base_frames = 8
        elif duration <= 30:
            base_frames = 12
        elif duration <= 60:
            base_frames = 15
        else:
            base_frames = 20
        
        # Adjust based on frame rate (higher FPS might need more frames)
        if fps > 60:
            base_frames = min(base_frames + 3, 25)
        elif fps < 24:
            base_frames = max(base_frames - 2, 5)
        
        # Ensure we don't exceed reasonable limits
        max_allowed = Config.MAX_FRAMES_PER_VIDEO
        return min(base_frames, max_allowed)
    
    def _save_extracted_frames_enhanced(self, frames_with_metadata: List, video_path: str) -> List[str]:
        """Save extracted frames with enhanced metadata"""
        video_name = Path(video_path).stem
        frames_dir = Path(Config.OUTPUT_DIR) / Config.FRAMES_DIR / f"{video_name}_enhanced_frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        print(f"💾 Saving {len(frames_with_metadata)} frames to {frames_dir}")
        
        for i, (frame, timestamp, metadata) in enumerate(frames_with_metadata):
            # Save frame
            frame_filename = f"frame_{i+1:03d}_t{timestamp:.2f}s_score{metadata.get('importance_score', 0):.2f}.jpg"
            frame_path = frames_dir / frame_filename
            cv2.imwrite(str(frame_path), frame)
            saved_paths.append(str(frame_path))
            
            # Save metadata
            metadata_path = frames_dir / f"frame_{i+1:03d}_metadata.json"
            
            # Convert numpy types for JSON serialization
            def convert_for_json(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, dict):
                    return {k: convert_for_json(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_for_json(item) for item in obj]
                return obj
            
            # Convert metadata before saving
            converted_metadata = convert_for_json(metadata)
            
            with open(metadata_path, 'w') as f:
                json.dump({
                    "frame_number": i + 1,
                    "timestamp": float(timestamp),
                    "metadata": converted_metadata,
                    "extraction_method": "advanced_intelligent_selection",
                    "frame_path": str(frame_path)
                }, f, indent=2)
        
        print(f"✅ Frames saved with enhanced metadata")
        return saved_paths
    
    def _analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze image content"""
        print(f"Analyzing image: {image_path}")
        
        # Load and preprocess image
        image = cv2.imread(image_path)
        if image is None:
            return {"error": f"Could not load image: {image_path}"}
        
        # Resize if too large
        image = ImageProcessor.resize_image(image, Config.FRAME_RESIZE_WIDTH)
        
        # Get image info
        height, width = image.shape[:2]
        image_info = {
            "width": width,
            "height": height,
            "channels": image.shape[2] if len(image.shape) > 2 else 1
        }
        
        # Analyze with AI
        print("Starting AI analysis...")
        analysis_result = self.ai_analyzer.analyze_image(image)
        
        # Compile final result
        result = {
            "content_type": "image",
            "source_file": image_path,
            "analysis_timestamp": datetime.now().isoformat(),
            "image_info": image_info,
            **analysis_result
        }
        
        # Save analysis result
        self._save_analysis_result(result, Path(image_path).stem)
        
        return result
    
    def _save_extracted_frames(self, frames_with_timestamps: List[tuple], base_name: str) -> List[str]:
        """Save extracted frames to disk"""
        saved_paths = []
        frames_dir = os.path.join(Config.OUTPUT_DIR, Config.FRAMES_DIR, base_name)
        os.makedirs(frames_dir, exist_ok=True)
        
        for i, (frame, timestamp) in enumerate(frames_with_timestamps):
            filename = f"frame_{i+1:03d}_t{timestamp:.2f}s.jpg"
            filepath = os.path.join(frames_dir, filename)
            
            # Resize frame before saving
            frame_resized = ImageProcessor.resize_image(frame, Config.FRAME_RESIZE_WIDTH)
            cv2.imwrite(filepath, frame_resized)
            saved_paths.append(filepath)
        
        return saved_paths
    
    def _save_analysis_result(self, result: Dict[str, Any], base_name: str):
        """Save analysis result to both JSON and formatted text files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON file
        json_filename = f"{base_name}_analysis_{timestamp}.json"
        json_filepath = os.path.join(Config.OUTPUT_DIR, json_filename)
        
        # Save clean text file
        txt_filename = f"{base_name}_prompt_{timestamp}.txt"
        txt_filepath = os.path.join(Config.OUTPUT_DIR, txt_filename)
        
        # Convert numpy arrays to lists for JSON serialization
        def convert_for_json(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            return obj
        
        # Create a copy without the raw image data
        json_result = {}
        for key, value in result.items():
            if key not in ['raw_image_data']:  # Exclude binary data
                json_result[key] = convert_for_json(value)
        
        # Save JSON file
        try:
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(json_result, f, indent=2, ensure_ascii=False, default=str)
            print(f"📄 JSON analysis saved to: {json_filepath}")
        except Exception as e:
            print(f"Failed to save JSON analysis: {e}")
        
        # Save formatted text file
        try:
            formatted_text = self._format_result_for_text(result)
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            print(f"📝 Formatted prompt saved to: {txt_filepath}")
        except Exception as e:
            print(f"Failed to save formatted text: {e}")
        # Return saved paths for DB storage
        return str(json_filepath), str(txt_filepath)
    
    def _format_result_for_text(self, result: Dict[str, Any]) -> str:
        """Format analysis result into clean, copy-pastable text"""
        if "error" in result:
            return f"Analysis Error: {result['error']}"
        
        lines = []
        lines.append("=" * 80)
        lines.append("AI REVERSE ENGINEERING - GENERATION PROMPT")
        lines.append("=" * 80)
        lines.append("")
        
        # Basic info
        content_type = result.get('content_type', 'Unknown').title()
        source_file = Path(result.get('source_file', 'Unknown')).name
        analysis_time = result.get('analysis_timestamp', 'Unknown')
        
        lines.append(f"Content Type: {content_type}")
        lines.append(f"Source File: {source_file}")
        lines.append(f"Analysis Date: {analysis_time}")
        lines.append("")
        
        if content_type.lower() == 'video':
            # Video-specific formatting
            video_info = result.get('video_info', {})
            lines.append("VIDEO INFORMATION:")
            lines.append("-" * 40)
            lines.append(f"Duration: {video_info.get('duration', 0):.2f} seconds")
            lines.append(f"Resolution: {video_info.get('width', 0)}x{video_info.get('height', 0)}")
            lines.append(f"FPS: {video_info.get('fps', 0):.1f}")
            lines.append(f"Frames Analyzed: {result.get('frames_analyzed', result.get('extracted_frames', 0))}")
            lines.append(f"Analysis Method: {result.get('analysis_method', 'Unknown')}")
            lines.append("")
            
            # Main video generation prompt
            main_prompt = result.get('comprehensive_video_prompt', 
                                   result.get('video_prompt', ''))
            
            if main_prompt:
                lines.append("🎬 VIDEO GENERATION PROMPT:")
                lines.append("=" * 60)
                lines.append("")
                lines.append(main_prompt.strip())
                lines.append("")
            
            # Additional details if available
            if result.get('video_narrative'):
                lines.append("📖 NARRATIVE DETAILS:")
                lines.append("-" * 30)
                lines.append(result['video_narrative'].strip())
                lines.append("")
            
            if result.get('technical_aspects'):
                lines.append("🎥 TECHNICAL ASPECTS:")
                lines.append("-" * 30)
                lines.append(result['technical_aspects'].strip())
                lines.append("")
            
            if result.get('style_consistency'):
                lines.append("🎨 VISUAL STYLE:")
                lines.append("-" * 30)
                lines.append(result['style_consistency'].strip())
                lines.append("")
            
            if result.get('motion_elements'):
                lines.append("🏃 MOTION & ANIMATION:")
                lines.append("-" * 30)
                lines.append(result['motion_elements'].strip())
                lines.append("")
        
        else:
            # Image-specific formatting
            image_info = result.get('image_info', {})
            lines.append("IMAGE INFORMATION:")
            lines.append("-" * 40)
            lines.append(f"Resolution: {image_info.get('width', 0)}x{image_info.get('height', 0)}")
            lines.append("")
            
            # Main image generation prompt
            main_prompt = (
                result.get('suggested_prompt')
                or result.get('comprehensive_analysis')
                or result.get('comprehensive_video_prompt', '')
            )
            
            if main_prompt:
                lines.append("🖼️ IMAGE GENERATION PROMPT:")
                lines.append("=" * 60)
                lines.append("")
                lines.append(main_prompt.strip())
                lines.append("")
            
            # Additional details
            if result.get('scene_description'):
                lines.append("🎬 SCENE DESCRIPTION:")
                lines.append("-" * 30)
                lines.append(result['scene_description'].strip())
                lines.append("")
            
            if result.get('style'):
                lines.append("🎨 VISUAL STYLE:")
                lines.append("-" * 30)
                lines.append(result['style'].strip())
                lines.append("")
            
            if result.get('technical_aspects'):
                lines.append("📷 TECHNICAL ASPECTS:")
                lines.append("-" * 30)
                lines.append(result['technical_aspects'].strip())
                lines.append("")
            
            if result.get('composition'):
                lines.append("🖼️ COMPOSITION:")
                lines.append("-" * 30)
                lines.append(result['composition'].strip())
                lines.append("")
        
        # Usage instructions
        lines.append("")
        lines.append("=" * 80)
        lines.append("📋 USAGE INSTRUCTIONS")
        lines.append("=" * 80)
        lines.append("")
        lines.append("💡 COPY-PASTE READY:")
        lines.append("The main prompt above is ready to use with AI video/image generators like:")
        lines.append("• RunwayML Gen-3")
        lines.append("• Stable Video Diffusion")
        lines.append("• Pika Labs")
        lines.append("• LumaAI Dream Machine")
        lines.append("• Midjourney (for images)")
        lines.append("• DALL-E 3 (for images)")
        lines.append("")
        lines.append("🔧 CUSTOMIZATION:")
        lines.append("You can modify the prompt by:")
        lines.append("• Adjusting style keywords")
        lines.append("• Adding specific aspect ratios")
        lines.append("• Changing duration (for videos)")
        lines.append("• Adding quality/resolution parameters")
        lines.append("")
        lines.append("📝 GENERATED BY:")
        lines.append("AI Reverse Engineering System")
        lines.append(f"Analysis completed on: {analysis_time}")
        lines.append("")
        
        return "\n".join(lines)
    
    def batch_analyze(self, directory_path: str, file_patterns: List[str] = None) -> List[Dict[str, Any]]:
        """
        Analyze multiple files in a directory
        
        Args:
            directory_path: Path to directory containing files
            file_patterns: List of file patterns to match (default: all supported formats)
            
        Returns:
            List of analysis results
        """
        if file_patterns is None:
            file_patterns = Config.VIDEO_EXTENSIONS + Config.IMAGE_EXTENSIONS
        
        results = []
        directory = Path(directory_path)
        
        if not directory.exists():
            return [{"error": f"Directory not found: {directory_path}"}]
        
        # Find all matching files
        files_to_analyze = []
        for pattern in file_patterns:
            files_to_analyze.extend(directory.glob(f"*{pattern}"))
        
        print(f"Found {len(files_to_analyze)} files to analyze in {directory_path}")
        
        # Analyze each file
        for i, file_path in enumerate(files_to_analyze):
            print(f"\n[{i+1}/{len(files_to_analyze)}] Analyzing: {file_path.name}")
            result = self.analyze_content(str(file_path))
            results.append(result)
        
        return results
    
    def get_analysis_summary(self, result: Dict[str, Any]) -> str:
        """Generate a human-readable summary of analysis results"""
        if "error" in result:
            return f"Analysis failed: {result['error']}"
        
        summary = []
        summary.append(f"Content Type: {result.get('content_type', 'Unknown').title()}")
        summary.append(f"Source: {Path(result.get('source_file', '')).name}")
        summary.append(f"Analysis Time: {result.get('analysis_timestamp', 'Unknown')}")
        
        if result.get('content_type') == 'video':
            video_info = result.get('video_info', {})
            summary.append(f"Duration: {video_info.get('duration', 0):.2f} seconds")
            summary.append(f"Resolution: {video_info.get('width', 0)}x{video_info.get('height', 0)}")
            summary.append(f"Frames Analyzed: {result.get('frames_analyzed', result.get('extracted_frames', 0))}")
            summary.append(f"Analysis Method: {result.get('analysis_method', 'Unknown')}")
            
            # Check for new video prompt format
            main_prompt = result.get('comprehensive_video_prompt', 
                                   result.get('video_prompt', ''))
            
            if main_prompt:
                summary.append("\n🎬 Generated Video Prompt (Preview):")
                summary.append("-" * 50)
                # Show first 300 characters
                preview = main_prompt.strip()
                if len(preview) > 300:
                    preview = preview[:300] + "..."
                summary.append(preview)
                summary.append("")
                summary.append("💡 Full prompt saved to .txt file for easy copy-paste!")
            
            # Add additional analysis details
            if result.get('video_narrative') and result['video_narrative']:
                summary.append(f"\n📖 Narrative: {result['video_narrative'][:100]}...")
            if result.get('total_batches'):
                summary.append(f"🔄 Processed in {result['total_batches']} batches")
        
        elif result.get('content_type') == 'image':
            image_info = result.get('image_info', {})
            summary.append(f"Resolution: {image_info.get('width', 0)}x{image_info.get('height', 0)}")
            
            main_prompt = result.get('suggested_prompt', 
                                   result.get('comprehensive_video_prompt', ''))
            
            if main_prompt:
                summary.append("\n🖼️ Generated Image Prompt (Preview):")
                summary.append("-" * 50)
                # Show first 300 characters
                preview = main_prompt.strip()
                if len(preview) > 300:
                    preview = preview[:300] + "..."
                summary.append(preview)
                summary.append("")
                summary.append("💡 Full prompt saved to .txt file for easy copy-paste!")
            
            # Add scene description if available
            if result.get('scene_description'):
                summary.append(f"\n🎬 Scene: {result['scene_description'][:100]}...")
        
        return "\n".join(summary)


def main():
    """Main function for testing the system"""
    system = ReverseEngineerSystem()
    
    # Example usage
    test_files = [
        "samples/sample_image.jpg",
        # Add more test files as needed
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n{'='*80}")
            print(f"Analyzing: {file_path}")
            print('='*80)
            
            result = system.analyze_content(file_path)
            summary = system.get_analysis_summary(result)
            print(summary)
        else:
            print(f"Test file not found: {file_path}")


if __name__ == "__main__":
    main()
