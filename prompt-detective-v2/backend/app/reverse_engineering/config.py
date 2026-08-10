"""
Configuration settings for the AI Reverse Engineering System
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the system"""
    
    # Environment Configuration
    APP_ENV = os.getenv("APP_ENV", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app_data.sqlite3")
    
    # Feature Flags
    ENABLE_USAGE_ANALYTICS = os.getenv("ENABLE_USAGE_ANALYTICS", "true").lower() == "true"
    ENABLE_LEGACY_FALLBACK = os.getenv("ENABLE_LEGACY_FALLBACK", "true").lower() == "true"
    SHOW_EXPERIMENTAL_PARAMS = os.getenv("SHOW_EXPERIMENTAL_PARAMS", "false").lower() == "true"
    ENABLE_DEBUG_TOOLBAR = os.getenv("ENABLE_DEBUG_TOOLBAR", "false").lower() == "true"
    
    # API Configuration
    GROQ_API_KEY = (
        os.getenv("GROQ_API_KEY") or 
        (hasattr(__import__('streamlit'), 'secrets') and 
         getattr(__import__('streamlit').secrets, 'GROQ_API_KEY', None))
    )
    GROQ_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"  # Vision model for image analysis
    
    # API Limitations
    MAX_IMAGES_PER_REQUEST = 5   # Groq vision model limit
    
    # Maximum Accuracy Configuration
    ENABLE_ENSEMBLE_ANALYSIS = os.getenv("ENABLE_ENSEMBLE_ANALYSIS", "true").lower() == "true"
    ENABLE_CONFIDENCE_SCORING = os.getenv("ENABLE_CONFIDENCE_SCORING", "true").lower() == "true"
    ENABLE_TEMPORAL_ANALYSIS = os.getenv("ENABLE_TEMPORAL_ANALYSIS", "true").lower() == "true"
    ENABLE_PROMPT_OPTIMIZATION = os.getenv("ENABLE_PROMPT_OPTIMIZATION", "true").lower() == "true"
    ENABLE_CONSISTENCY_VALIDATION = os.getenv("ENABLE_CONSISTENCY_VALIDATION", "true").lower() == "true"
    
    # Ensemble Configuration
    ENSEMBLE_NUM_VARIATIONS = int(os.getenv("ENSEMBLE_NUM_VARIATIONS", "3"))  # 3 different perspectives
    ENSEMBLE_TEMPERATURE_BASE = float(os.getenv("ENSEMBLE_TEMPERATURE_BASE", "0.1"))  # Starting temperature
    
    # Quality Thresholds
    MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.6"))
    HIGH_CONFIDENCE_THRESHOLD = float(os.getenv("HIGH_CONFIDENCE_THRESHOLD", "0.8"))
    
    # Video Processing Configuration
    VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    # Frame Selection Parameters
    MIN_FRAME_DIFFERENCE = 0.15  # Minimum difference threshold for frame selection
    MAX_FRAMES_PER_VIDEO = 10    # Maximum frames to extract per video
    FRAME_RESIZE_WIDTH = 1024    # Resize frames for processing
    
    # Scene Detection Parameters
    SCENE_THRESHOLD = 30.0       # Threshold for scene change detection
    MIN_SCENE_LENGTH = 1.0       # Minimum scene length in seconds
    
    # Output Configuration
    OUTPUT_DIR = "analysis_results"
    FRAMES_DIR = "extracted_frames"
    
    # Cloud deployment configuration
    @staticmethod
    def is_cloud_deployment():
        """Check if running in cloud environment"""
        return (
            os.getenv("STREAMLIT_SHARING_MODE") is not None or
            "/mount/src/" in os.getcwd() or
            "streamlit" in os.getenv("HOME", "").lower()
        )
    
    # Prompt Enhancement
    DETAILED_ANALYSIS = True
    INCLUDE_TECHNICAL_DETAILS = True
    STYLE_ANALYSIS = True
    COMPOSITION_ANALYSIS = True
