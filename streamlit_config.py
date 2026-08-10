"""
Streamlit App Configuration
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime
from services.admin_seed import ensure_admin_from_env

# App configuration
APP_CONFIG = {
    "title": "AI Reverse Engineering System",
    "icon": "🎬",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "max_upload_size": 200,  # MB
    "supported_video_formats": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"],
    "supported_image_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"],
    "default_max_frames": 10,
    "default_threshold": 0.15,
    "theme": {
        "primary_color": "#1f77b4",
        "background_color": "#ffffff",
        "secondary_background_color": "#f0f2f6",
        "text_color": "#262730"
    }
}

# Streamlit page config
def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title=APP_CONFIG["title"],
        page_icon=APP_CONFIG["icon"],
        layout=APP_CONFIG["layout"],
        initial_sidebar_state=APP_CONFIG["initial_sidebar_state"],
        menu_items={
            'Get Help': 'mailto:tryreverseai@gmail.com',
            'Report a bug': 'https://github.com/your-repo/issues',
            'About': f"{APP_CONFIG['title']} - Extract prompts from AI-generated content"
        }
    )

# Custom CSS
def load_custom_css():
    """Load custom CSS for the app"""
    css = f"""
    <style>
        /* Main styling */
        .main-header {{
            font-size: 3rem;
            color: {APP_CONFIG["theme"]["primary_color"]};
            text-align: center;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            font-weight: bold;
        }}
        
        .sub-header {{
            font-size: 1.5rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        /* Feature boxes */
        .feature-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .feature-box:hover {{
            transform: translateY(-5px);
        }}
        
        .feature-box h4 {{
            margin-bottom: 0.5rem;
            font-size: 1.2rem;
        }}
        
        /* Status boxes */
        .success-box {{
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin: 1rem 0;
            border-left: 5px solid #2E8B57;
        }}
        
        .warning-box {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin: 1rem 0;
            border-left: 5px solid #DC143C;
        }}
        
        .info-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin: 1rem 0;
            border-left: 5px solid {APP_CONFIG["theme"]["primary_color"]};
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.75rem 2rem;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }}
        
        /* File uploader */
        .stFileUploader {{
            border: 2px dashed {APP_CONFIG["theme"]["primary_color"]};
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            background-color: rgba(31, 119, 180, 0.1);
        }}
        
        /* Progress bars */
        .stProgress .st-bo {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }}
        
        /* Metrics */
        .metric-container {{
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 4px solid {APP_CONFIG["theme"]["primary_color"]};
        }}
        
        /* Sidebar */
        .css-1d391kg {{
            background-color: #f8f9fa;
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background-color: rgba(31, 119, 180, 0.1);
            border-radius: 5px;
        }}
        
        /* Tables */
        .dataframe {{
            border-radius: 10px;
            overflow: hidden;
        }}
        
        /* Text areas */
        .stTextArea textarea {{
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        }}
        
        .stTextArea textarea:focus {{
            border-color: {APP_CONFIG["theme"]["primary_color"]};
            box-shadow: 0 0 5px rgba(31, 119, 180, 0.3);
        }}
        
        /* Cards */
        .result-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
            margin: 1rem 0;
        }}
        
        /* Animation for loading */
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        
        .loading-animation {{
            animation: pulse 2s infinite;
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .main-header {{
                font-size: 2rem;
            }}
            
            .feature-box {{
                padding: 1rem;
            }}
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Utility functions for the app
def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_duration(seconds):
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}m {int(remaining_seconds)}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(remaining_minutes)}m"

def create_download_link(data, filename, link_text):
    """Create a download link for data"""
    import base64
    
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def validate_file_type(filename):
    """Validate if file type is supported"""
    file_ext = Path(filename).suffix.lower()
    
    if file_ext in APP_CONFIG["supported_video_formats"]:
        return "video"
    elif file_ext in APP_CONFIG["supported_image_formats"]:
        return "image"
    else:
        return None

def get_file_info(uploaded_file):
    """Get comprehensive file information"""
    return {
        "name": uploaded_file.name,
        "size": len(uploaded_file.getvalue()),
        "size_formatted": format_file_size(len(uploaded_file.getvalue())),
        "type": uploaded_file.type,
        "content_type": validate_file_type(uploaded_file.name)
    }

# Session state management
def initialize_session_state():
    """Initialize session state variables"""
    # Ensure admin user exists (idempotent). No UI exposure; logs only if debug desired.
    try:
        _ = ensure_admin_from_env()
    except Exception:
        # Do not block UI on seeding issues
        pass
    default_states = {
        'analysis_results': [],
        'current_analysis': None,
        'system_initialized': False,
        'uploaded_files': [],
        'processing_queue': [],
        'batch_processing': False,
        'total_files_processed': 0,
        'total_analysis_time': 0.0,
        'app_settings': {
            'max_frames': APP_CONFIG["default_max_frames"],
            'threshold': APP_CONFIG["default_threshold"],
            'save_frames_default': True,
            'detailed_analysis_default': True,
            'theme': 'light'
        }
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Error handling
def handle_error(error, context=""):
    """Handle errors gracefully with user-friendly messages"""
    error_messages = {
        "API_KEY_MISSING": "❌ GROQ API key is missing. Please check your .env file.",
        "API_ERROR": "❌ API request failed. Please check your connection and try again.",
        "FILE_TOO_LARGE": f"❌ File is too large. Maximum size is {APP_CONFIG['max_upload_size']} MB.",
        "UNSUPPORTED_FORMAT": "❌ File format not supported. Check the help section for supported formats.",
        "PROCESSING_ERROR": "❌ Error during processing. Please try with a different file.",
        "SYSTEM_ERROR": "❌ System error occurred. Please refresh the page and try again."
    }
    
    error_type = getattr(error, 'type', 'SYSTEM_ERROR')
    message = error_messages.get(error_type, f"❌ {str(error)}")
    
    if context:
        message += f" Context: {context}"
    
    st.error(message)
    
    # Log error for debugging
    if hasattr(st, 'logger'):
        st.logger.error(f"Error in {context}: {str(error)}")

# App state management
def save_app_state():
    """Save current app state"""
    state_data = {
        'settings': st.session_state.get('app_settings', {}),
        'total_processed': st.session_state.get('total_files_processed', 0),
        'total_time': st.session_state.get('total_analysis_time', 0.0)
    }
    
    # Save to local storage or file if needed
    return state_data

def load_app_state():
    """Load saved app state"""
    # Load from local storage or file if needed
    pass

# Performance monitoring
def track_performance(func):
    """Decorator to track function performance"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Update session state with performance metrics
        if 'performance_metrics' not in st.session_state:
            st.session_state.performance_metrics = []
        
        st.session_state.performance_metrics.append({
            'function': func.__name__,
            'duration': end_time - start_time,
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    return wrapper
