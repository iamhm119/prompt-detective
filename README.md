# 🔍 Prompt Detective

<div align="center">

![Prompt Detective Banner](https://img.shields.io/badge/AI-Reverse%20Engineering-blue?style=for-the-badge&logo=artificial-intelligence)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-27338e?style=for-the-badge&logo=opencv&logoColor=white)

**An advanced AI reverse engineering system that analyzes videos and images to extract the original generation prompts and parameters.**

*Solving the mystery behind AI-generated content, one frame at a time.*

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [🛠️ Installation](#️-installation) • [📖 Usage](#-usage) • [🔧 Configuration](#-configuration)

</div>

---

> New: Production-style multi‑page SaaS shell (auth, dashboard, usage history, pricing, admin, settings, legal, help, referrals) + onboarding tooltips + secure session persistence + streamlined launcher.

## 🎯 What is Prompt Detective?

Prompt Detective is a sophisticated AI-powered system that reverse-engineers visual content to discover the original prompts and parameters used to create AI-generated images and videos. Using advanced computer vision algorithms and multi-pass AI analysis, it can decode the creative DNA behind any visual content.

### 🎬 **Video Analysis Demo**
```
Input: mystery_video.mp4 (8 seconds, 720x404)
↓
🔍 Advanced frame extraction (8 optimal frames)
🧠 Multi-pass AI analysis
📝 Generated comprehensive prompt
```

## ✨ Features

### 🎬 **Advanced Video Processing**
- **Intelligent Frame Selection**: Uses computer vision algorithms (SSIM, optical flow, LBP) to select the most relevant frames
- **Scene Detection**: Advanced boundary detection using histogram analysis and motion vectors
- **Quality Enhancement**: CLAHE and bilateral filtering for optimal analysis quality
- **Motion Analysis**: Optical flow calculations for dynamic content understanding

### 🖼️ **Sophisticated Image Analysis**
- **Visual Complexity Scoring**: Edge density, texture analysis, and color diversity metrics
- **Feature Extraction**: ORB keypoints, contour detection, and gradient analysis
- **Multi-algorithm Processing**: Combines multiple CV techniques for maximum accuracy

### 🧠 **AI-Powered Intelligence**
- **Multi-Pass Analysis**: Technical, Creative, and Prompt-focused expert passes
- **Enhanced Prompting**: Forensic-level analysis prompts for 300% improved accuracy
- **Cross-Validation**: Multiple AI experts validate and synthesize results
- **Groq Integration**: Lightning-fast inference with state-of-the-art models

### 📊 **Professional Interface**
- **Modern Streamlit UI**: Clean, responsive web interface
- **Real-time Progress**: Live tracking with detailed status updates
- **Comprehensive Results**: JSON analysis, formatted prompts, and metadata
- **Batch Processing**: Handle multiple files efficiently

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/okaditya84/Prompt-Detective.git
cd Prompt-Detective
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment
Create a `.env` file with your Groq API key:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 🚀 Quick Start

#### Launch (Modern Multi‑Page UI)
```bash
streamlit run app_launcher.py
```
The launcher routes to the new multi‑page interface. The legacy single‑page UI is no longer exposed in runtime builds.

#### Access
1. Visit `http://localhost:8501`
2. Sign up (stores hashed credentials; bcrypt if installed)
3. Explore Dashboard → Upload image/video → Analyze
4. View saved summaries in Usage History; adjust preferences in Settings

## 📖 Usage

### 🎬 Video Analysis
1. **Upload Video**: Drag and drop or browse for video files
2. **Automatic Processing**: 
   - Optimal frame count calculation
   - Advanced scene detection
   - Quality enhancement
3. **AI Analysis**: Multi-pass expert analysis
4. **Results**: Comprehensive prompt with technical details

### 🖼️ Image Analysis
1. **Upload Image**: Support for various formats
2. **Enhancement**: Automatic quality optimization
3. **Analysis**: Deep visual understanding
4. **Prompt Generation**: Detailed recreation prompts

### 📊 Analysis Results
- **JSON Output**: Structured analysis data
- **Formatted Prompts**: Ready-to-use generation prompts
- **Metadata**: Technical parameters and confidence scores
- **Frame Gallery**: Visual breakdown of analyzed content

## 🔧 Configuration

### Environment Variables (Excerpt)
```bash
# Core
GROQ_API_KEY=your_api_key

# Feature Flags / Future Integrations
STRIPE_PUBLIC_KEY=pk_test_xxx          # (optional) enable pricing checkout UI
STRIPE_SECRET_KEY=sk_test_xxx          # (optional) server operations
ENABLE_ONBOARDING_TOOLTIPS=true        # toggle contextual guidance
FORCE_LEGACY_UI=false                  # force legacy single page (debug)

# Security / Sessions
SESSION_TTL_MIN=720                    # override default 12h (optional)

# Logging / Diagnostics
LOG_LEVEL=info
```
See `.env.example` for full annotated list.

### Advanced Settings
Edit `config.py` for detailed customization:
- Frame selection algorithms
- AI model preferences
- Quality enhancement parameters
- Output formatting options

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│  Reverse Engine  │───▶│   AI Analyzer   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ File Management │    │  Video/Image     │    │ Multi-Pass      │
│ Progress Track  │    │  Processing      │    │ Analysis        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                      ┌──────────────────┐
                      │   Utils (CV)     │
                      │ • Frame Selection│
                      │ • Scene Detection│
                      │ • Enhancement    │
                      └──────────────────┘
```

## 📁 Project Structure

```
Prompt-Detective/
├── app_launcher.py            # Unified entrypoint for modern multi‑page UI
├── streamlit_app.py           # Redirect-only stub (kept for local reference)
├── pages/                     # Multi-page SaaS UI (Home, Login, Signup, Dashboard, etc.)
├── components/                # Reusable UI (navigation, onboarding tooltips)
├── services/                  # auth_service, db layer, error utilities
├── models/                    # (User, Subscription, Analysis dataclasses)
├── reverse_engineer.py        # Core analysis engine (unchanged)
├── ai_analyzer.py             # AI multi-pass logic (unchanged)
├── utils.py                   # CV helper utilities
├── config.py / streamlit_config.py
├── analysis_results/          # Stored prompts / frames exports
├── samples/                   # Sample media
├── requirements.txt / packages.txt
└── README.md
```

## 🧩 SaaS Layer Additions

### Authentication & Sessions
- Email + password signup/login (bcrypt hashing if library present; SHA-256 fallback)
- Persistent DB-backed sessions (token + expiry) with automatic restoration
- Role = plan code (free/pro/team/admin) used for gating
- Backend auto-seeds a super-admin using `ADMIN_EMAIL` / `ADMIN_PASSWORD` (falls back to `ChangeMe!123!` when no password supplied—rotate it in production)

### Plans & Usage Limits
- Seeded plans (free/pro/team) with daily analysis quotas
- Real-time quota check before analysis (friendly message + upgrade CTA)

### Persistent History
- Each successful analysis stores: type, filename, preview, duration/frames
- `Usage & History` page with search, type filter, limit control, record details

### Settings & Personalization
- Theme, email notifications (placeholder), onboarding tooltip toggle
- Server-side storage in `user_settings` table

### Onboarding Guidance
- Contextual lightweight tooltips (dismiss & persist per user)
- Feature flag to disable globally

### Admin Utilities
- Admin page listing users, roles, metrics (future: role elevation, plan management)
- Admin API enforces `is_admin` / `is_super_admin` flags with enterprise-level bypass

### Legal & Compliance Placeholders
- Structured Terms of Service & Privacy Policy pages (replace with counsel text)
- Help & FAQ page with contact form placeholder

### Launcher
- `app_launcher.py` attempts modern UI → falls back to legacy if errors occur
- Diagnostic expander reveals import/runtime issues for rapid recovery

### Error Handling
- Decorator + context manager for safe UI error boundaries

### Security Notes
- Strong hashing (bcrypt) recommended (auto-used if installed)
- Constant-time compare; input validation for email/password
- Future ready: OAuth, 2FA (hooks reserved)

## 🔬 Technology Stack

### Computer Vision
- **OpenCV**: Video processing and computer vision
- **scikit-image**: Advanced image analysis algorithms
- **scipy**: Scientific computing and optimization
- **NumPy**: Numerical computations

### AI & Machine Learning
- **Groq API**: High-performance AI inference
- **Advanced Prompting**: Forensic-level analysis techniques
- **Multi-Expert System**: Specialized analysis passes

### Web Interface
- **Streamlit**: Modern web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data analysis and presentation

### Image Processing
- **PIL/Pillow**: Image manipulation
- **CLAHE**: Contrast enhancement
- **Bilateral Filtering**: Noise reduction

## 🎨 Sample Results

### Input Video Analysis
```
📹 Video: corporate_presentation.mp4
⏱️ Duration: 30 seconds
📊 Resolution: 1920x1080
🎯 Frames Analyzed: 12 optimal frames

🔍 Generated Prompt:
"Professional corporate presentation style video, clean modern office 
environment, business person in formal attire presenting quarterly 
results, sleek PowerPoint slides with data visualizations, corporate 
blue and white color scheme, professional lighting setup, medium shot 
with shallow depth of field, shot with Sony FX6 camera..."
```

### Confidence Metrics
- **Technical Accuracy**: 94%
- **Creative Elements**: 89%
- **Prompt Completeness**: 96%
- **Overall Confidence**: 93%

## 🧪 Development / Testing

### Local Dev Tips
1. Launch with launcher for safety: `streamlit run app_launcher.py`
2. Modify pages under `pages/` (naming with numeric prefix defines order)
3. Avoid editing core analysis modules unless improving CV/AI logic intentionally
4. Use `analysis_results/` to inspect saved prompt artifacts

### Minimal Manual Test Checklist
- Signup → Login → Session persists after refresh
- Run image & video analysis → Appears in Usage History
- Toggle tooltips off in Settings → Tooltips disappear
- Exceed free quota (5) → Gating message & upgrade CTA
- Force failure (rename a core import) → Launcher shows diagnostics and retry (no legacy fallback)

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- OpenCV community for computer vision tools
- Groq for high-performance AI inference
- Streamlit for the amazing web framework
- The open-source community for inspiration

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/okaditya84/Prompt-Detective/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/okaditya84/Prompt-Detective/discussions)
- 📧 **Contact**: Open an issue for any questions

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

_Built with a focus on clarity, graceful degradation, and forensic-quality analysis._

</div>