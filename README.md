# Talking Photo Generator

🎬 Transform static images into animated videos with synchronized audio using AI! This application uses multiple AI services (FAL.AI, ElevenLabs, Google Gemini, Cloudinary) to create professional talking photos with cinematic effects.

## Features

- 📸 **Image Upload** - Upload images or capture with webcam
- 🎨 **AI Image Generation** - Generate images with Gemini 2.0
- 🧠 **Smart Analysis** - Automatic image analysis with cinematic prompt suggestions
- 🎤 **Text-to-Speech** - Generate natural voice audio with ElevenLabs
- 🎥 **Video Generation** - Multiple models available:
  - **Premium Mode**: Veo 3, Sora 2, Wav2lip (paid)
  - **Economico Mode**: Open-Sora, Wav2lip Free (free)
- 🖼️ **Gallery** - View and manage all generated content
- 💰 **Cost Tracking** - Monitor API usage and spending
- 🔒 **Admin Panel** - Manage API balances and view statistics

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLite** - Local database (no external DB required!)
- **Google Gemini 2.0** - Image analysis and generation
- **FAL.AI** - Premium video generation (Veo 3, Sora 2)
- **ElevenLabs** - High-quality text-to-speech
- **Cloudinary** - Image storage and CDN
- **HuggingFace Spaces** - Free video generation alternatives

### Frontend
- **React 19** - Modern React with hooks
- **Tailwind CSS** - Utility-first styling
- **Radix UI** - Accessible component primitives
- **Framer Motion** - Smooth animations
- **Axios** - HTTP client

## Quick Start

### Prerequisites

- Python 3.10+ with pip
- Node.js 16+ with npm
- All API keys are already configured in `.env` file

### Installation

1. **Clone the repository** (if not already done)
   ```bash
   cd talking-photo-generator
   ```

2. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install aiosqlite google-generativeai fastapi uvicorn elevenlabs fal-client cloudinary python-multipart python-dotenv gradio-client pillow
   cd ..
   ```

3. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   cd ..
   ```

### Running the Application

#### Option 1: Start Both Servers (Recommended)
Double-click `start-all.bat` or run:
```bash
start-all.bat
```

#### Option 2: Start Servers Individually

**Backend (Terminal 1):**
```bash
start-backend.bat
```
Or manually:
```bash
cd backend
python -m uvicorn server:app --reload --port 8001
```

**Frontend (Terminal 2):**
```bash
start-frontend.bat
```
Or manually:
```bash
cd frontend
npm start
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## Usage Guide

### 1. Generate/Upload Image
- Upload an existing image or capture one with your webcam
- Or use the Image Generator to create a new image with AI

### 2. Image Analysis
- The system automatically analyzes your image with Gemini
- Receives cinematic prompt suggestions optimized for each model
- Choose between Premium or Economico mode

### 3. Generate Audio (Optional)
- Enter text for text-to-speech conversion
- Select voice and adjust voice settings
- Or skip to use silent video

### 4. Generate Video
- Choose your model:
  - **Veo 3**: Best quality, cinematic shots, audio sync
  - **Sora 2**: Great physics, native audio
  - **Wav2lip**: Lip synchronization with audio
  - **Open-Sora**: Free alternative
- Edit the auto-generated prompt if needed
- Click Generate Video and wait for processing

### 5. View Results
- Videos appear in the Gallery when completed
- Download or delete generated content
- View costs and usage statistics in Admin Panel

## Project Structure

```
talking-photo-generator/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── database.py            # SQLite database manager
│   ├── emergent_wrapper.py   # Gemini API wrapper
│   ├── .env                   # Backend environment variables
│   ├── database/              # SQLite database file (auto-created)
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/            # React page components
│   │   ├── components/       # UI components
│   │   └── App.js            # Main React app
│   ├── .env                  # Frontend environment variables
│   └── package.json          # Node dependencies
├── start-all.bat             # Start both servers (Windows)
├── start-backend.bat         # Start backend only (Windows)
├── start-frontend.bat        # Start frontend only (Windows)
├── CLAUDE.md                 # Development documentation
└── README.md                 # This file
```

## Configuration

### API Keys (Already Configured)

All API keys are pre-configured in `.env` files:

- ✅ FAL_KEY - Video generation (Veo 3, Sora 2, Wav2lip)
- ✅ ELEVENLABS_KEY - Text-to-speech
- ✅ GEMINI_KEY - Image analysis and generation
- ✅ CLOUDINARY credentials - Image storage

### Database

- **Type**: SQLite (local file-based)
- **Location**: `backend/database/video_gen.db`
- **Auto-created**: Database and tables created automatically on first run
- **No setup required**: No MongoDB installation needed!

## Cost Information

### Premium Models (Paid)
- **Veo 3**: $0.20-0.40 per second (with/without audio)
- **Sora 2**: $0.10 per second
- **Wav2lip**: $0.05 per second
- **ElevenLabs TTS**: ~$0.30 per 1000 characters
- **Gemini Image**: ~$0.039 per image

### Economico Models (Free)
- **Open-Sora**: Free (HuggingFace)
- **Wav2lip Free**: Free (HuggingFace)

Track your spending in the Admin Panel!

## Troubleshooting

### Backend won't start
```bash
cd backend
python test_server.py
```
This will check if all imports and database are working.

### Frontend won't start
Make sure you installed with `--legacy-peer-deps`:
```bash
cd frontend
npm install --legacy-peer-deps
```

### Database issues
Delete the database file and restart:
```bash
rm backend/database/video_gen.db
```
It will be recreated automatically.

### Content Policy Violations
The backend automatically sanitizes prompts to avoid violating AI policies. If you still get errors:
- Avoid words like "threatening", "violent", "attack"
- Don't mention "facial identity" or "facial fidelity"
- Use neutral descriptive words instead

## Development

### Backend Development
```bash
cd backend
python -m uvicorn server:app --reload --port 8001
```

### Frontend Development
```bash
cd frontend
npm start
```

### Testing Backend
```bash
cd backend
python test_server.py
```

### Database Schema

See `backend/database.py` for complete schema. Main tables:
- `image_analyses` - Analyzed images with AI prompts
- `audio_generations` - Generated audio files
- `video_generations` - Generated videos
- `generated_images` - AI-generated images
- `token_usage` - API cost tracking
- `api_balances` - Service balance management

## Admin Features

Access the Admin Panel at http://localhost:3000/admin

- View total API spending
- Track costs by service
- See recent operations
- Manage API balances
- Password: `mauricio123` (configured in backend/.env)

## Support

For issues or questions:
1. Check `CLAUDE.md` for detailed technical documentation
2. Review backend logs for error messages
3. Check the FastAPI docs at http://localhost:8001/docs

## License

Private project for Fabrica Alegria.
