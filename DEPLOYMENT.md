# Streamlit Cloud Deployment Guide

## Files Required for Deployment

1. **packages.txt** - System dependencies for OpenCV
2. **requirements.txt** - Python dependencies (updated to use opencv-python-headless)
3. **.streamlit/config.toml** - Streamlit configuration
4. **.streamlit/secrets.toml** - Template for secrets (don't commit actual keys)

## Deployment Steps

### 1. Prepare Your Repository
Ensure all the following files are in your repository root:
- `packages.txt`
- `requirements.txt` 
- `.streamlit/config.toml`
- All your Python files

### 2. Set Up Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Connect your GitHub repository
3. Select the repository: `Prompt-Detective`
4. Set main file path: `app_launcher.py`
5. Set branch: `main`

### 3. Configure Secrets
In the Streamlit Cloud dashboard:
1. Go to your app settings
2. Click on "Secrets" 
3. Add your environment variables:
```toml
GROQ_API_KEY = "your_actual_groq_api_key_here"
```

### 4. Deploy
Click "Deploy" and wait for the build to complete.

## Troubleshooting

### OpenCV Issues
If you still get OpenCV errors:
1. Verify `packages.txt` is in the repository root
2. Ensure `opencv-python-headless` is in requirements.txt
3. Check the build logs for dependency installation errors

### API Key Issues
1. Verify the API key is correctly set in Streamlit secrets
2. Check that the key has the correct permissions
3. Test the key locally first

### File Size Limits
- Streamlit Cloud has upload limits
- Large videos may need to be processed in chunks
- Consider implementing file compression

## File Structure
```
your-repo/
├── app_launcher.py
├── reverse_engineer.py
├── config.py
├── utils.py
├── ai_analyzer.py
├── requirements.txt
├── packages.txt
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml (template)
└── README.md
```
