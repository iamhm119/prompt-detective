"""
Deployment configuration for different environments
"""
import os
import sys

def is_streamlit_cloud():
    """Detect if running on Streamlit Cloud"""
    return (
        os.getenv("STREAMLIT_SHARING_MODE") is not None or
        "/mount/src/" in sys.path[0] or
        "streamlit" in os.getenv("HOME", "").lower()
    )

def is_local_dev():
    """Detect if running in local development"""
    return not is_streamlit_cloud()

def get_deployment_config():
    """Get configuration based on deployment environment"""
    if is_streamlit_cloud():
        return {
            "environment": "streamlit_cloud",
            "opencv_backend": "headless",
            "max_file_size": "200MB",
            "temp_dir": "/tmp",
            "debug_mode": False
        }
    else:
        return {
            "environment": "local",
            "opencv_backend": "full", 
            "max_file_size": "500MB",
            "temp_dir": "temp",
            "debug_mode": True
        }

# Global deployment config
DEPLOYMENT_CONFIG = get_deployment_config()
