# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Talking Photo Generator** - a full-stack web application that converts static images into animated videos with synchronized audio. The system uses multiple AI services (FAL.AI, ElevenLabs, Google Gemini, Cloudinary) and offers both premium (paid) and economico (free) model options.

### Architecture

**Monorepo Structure:**
- `backend/` - FastAPI async server with SQLite database
- `frontend/` - React 19 with Create React App (CRACO), Radix UI components, Tailwind CSS
- Test files at root level (`test_*.py`, `*_test.py`)
- Quick start scripts: `start-all.bat`, `start-backend.bat`, `start-frontend.bat`

**Data Flow:**
1. User uploads/captures image → Cloudinary storage
2. Gemini 2.0 analyzes image → suggests models + generates cinematic prompts (Sora 2, Veo 3)
3. Optional: ElevenLabs generates audio from text
4. FAL.AI (premium) or HuggingFace Spaces (economico) generates video
5. Results stored in SQLite local database, displayed in gallery

## Development Commands

### Backend (Python/FastAPI)

```bash
# Install dependencies (quick install)
cd backend
pip install aiosqlite google-generativeai fastapi uvicorn elevenlabs fal-client cloudinary python-multipart python-dotenv gradio-client pillow

# Run server (default port 8001)
python -m uvicorn server:app --reload --port 8001

# Test server initialization
python test_server.py

# Run tests (if available)
python test_video_generation.py
python test_fal_direct.py
```

### Frontend (React)

```bash
cd frontend

# Install dependencies (use legacy peer deps)
npm install --legacy-peer-deps

# Development server (port 3000)
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Quick Start (Windows)

```bash
# Start both servers at once
start-all.bat

# Or start individually
start-backend.bat
start-frontend.bat
```

## Key Technical Details

### Backend Architecture (`backend/server.py`)

**API Structure:**
- Main FastAPI app with `/api` prefix router
- All endpoints under `/api/*` namespace
- Async/await pattern throughout with aiosqlite (async SQLite)

**Critical Services Integration:**

1. **Gemini 2.0 Flash** (via google-generativeai):
   - Image analysis with cinematic prompt generation
   - Image generation with Gemini 2.0
   - Model-specific templates (Sora 2 vs Veo 3)
   - Content policy sanitization (removes deepfake-triggering phrases)
   - 30s timeout protection
   - Custom wrapper in `emergent_wrapper.py` for compatibility

2. **FAL.AI Models** (Premium):
   - `fal-ai/veo3.1/image-to-video` - Fixed 8s duration, $0.20-0.40/sec
   - `fal-ai/sora-2/image-to-video` - $0.10/sec
   - `fal-ai/wav2lip` - Lip sync, $0.05/sec
   - All use async executor to avoid blocking

3. **HuggingFace Spaces** (Economico/Free):
   - `hpcai-tech/Open-Sora` - Free alternative
   - `fffiloni/Wav2Lip` - Free lip sync
   - Gradio Client integration

4. **ElevenLabs TTS**:
   - Multilingual v2 model
   - Voice settings: stability, similarity_boost, style
   - ~$0.30 per 1000 chars
   - Returns base64-encoded audio

5. **Cloudinary**:
   - Image uploads to `video-gen` folder
   - Generated images to `generated_images` folder
   - Fallback to base64 data URLs on failure

**Content Policy System:**
The backend includes a sophisticated prompt sanitization system to avoid content policy violations:
- Removes facial fidelity/identity preservation phrases (triggers deepfake detection)
- Replaces violent/threatening words with neutral alternatives
- Regex patterns in `sanitize_prompt()` and `sanitize_analysis_prompts()` functions
- Special handling for child-related content

**Database Schema (SQLite):**
```python
Tables (managed by database.py):
- image_analyses: {id, image_url, cloudinary_id, analysis(TEXT/JSON), suggested_model, timestamp}
- audio_generations: {id, audio_url, source, duration, text, voice_id, voice_settings(TEXT/JSON), cost, timestamp}
- video_generations: {id, image_id, audio_id, model, mode, prompt, duration, cost, estimated_cost, status, result_url, error, timestamp}
- generated_images: {id, prompt, image_url, cost, timestamp}
- token_usage: {id, service, operation, cost, details(TEXT/JSON), timestamp}
- api_balances: {id, service(UNIQUE), initial_balance, current_balance, last_updated}

Location: backend/database/video_gen.db
Auto-created on first server start with proper indexes
```

### Frontend Architecture

**Routing:**
- `/` - HomePage (main workflow: upload → analyze → generate)
- `/image-generator` - Gemini 2.5 Flash Image generation
- `/gallery` - View all generated content
- `/admin` - Token usage tracking and balance management

**State Management:**
- React hooks (useState, useRef) for local state
- No global state management library
- Axios for API calls to `${BACKEND_URL}/api`

**Key Components:**
- Uses shadcn/ui components (Radix UI primitives with Tailwind)
- Framer Motion for animations
- Sonner for toast notifications
- react-webcam for camera capture

**Build System:**
- CRACO extends Create React App
- Custom webpack plugins: health-check, visual-edits (metadata)
- PostCSS + Tailwind for styling

## Environment Variables

**Backend (`.env` in `backend/`):**
```
# Database (SQLite - local file)
DB_PATH=./database/video_gen.db

# AI Services
FAL_KEY=<fal.ai api key>
ELEVENLABS_KEY=<elevenlabs api key>
GEMINI_KEY=<google gemini key>

# Storage
CLOUDINARY_CLOUD_NAME=<cloudinary name>
CLOUDINARY_API_KEY=<cloudinary key>
CLOUDINARY_API_SECRET=<cloudinary secret>
CLOUDINARY_UPLOAD_PRESET=<upload preset>

# Server Configuration
BACKEND_URL=http://localhost:8001
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
ADMIN_PASSWORD=mauricio123
```

**Note**: All API keys are already configured in the project's `.env` file.

**Frontend (`.env` in `frontend/`):**
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Testing Strategy

**Backend Tests (Root Level):**
- `test_video_generation.py` - Video generation pipeline tests
- `test_fal_direct.py` - FAL.AI integration tests
- `test_fal_auth_quick.py` - FAL authentication tests
- `detailed_prompt_test.py` - Prompt sanitization tests
- `backend_test.py` - Comprehensive backend endpoint tests

**Test Reports:**
- `test_reports/` - JSON test results
- `test_result.md` - Markdown test summary

**Running Specific Tests:**
```bash
# Single test file
python test_video_generation.py

# With pytest
pytest backend_test.py -v

# Specific test function
pytest backend_test.py::test_analyze_image -v
```

## Important Implementation Notes

### Content Policy Compliance
When working with prompts or modifying AI generation:
1. NEVER include phrases about "maintaining facial identity" or "preserving facial fidelity"
2. Replace violent/threatening words automatically (see `sanitize_prompt()` in `server.py:628`)
3. Special care with child-related content - avoid close-ups, eating/drinking actions
4. The system automatically cleans prompts before sending to FAL.AI

### Model Selection Logic
- **Veo 3**: Best for high-quality cinematic shots with complex physics, audio sync (premium only)
- **Sora 2**: Physics realism, native audio generation, good for character animation (premium only)
- **Wav2lip**: Lip sync only, requires audio input (premium or free)
- **Open-Sora**: Free alternative, lower quality but functional (economico only)

### Async Patterns
- All database operations use `await` with Motor
- FAL.AI calls wrapped in `asyncio.get_event_loop().run_in_executor()` to avoid blocking
- Gemini calls have 30s timeout via `asyncio.wait_for()`

### Cost Tracking
Every paid operation creates a `TokenUsage` record:
- Image analysis: ~$0.039 (Gemini)
- Audio generation: ~$0.30 per 1000 chars (ElevenLabs)
- Video generation: varies by model and duration
- Admin panel displays running totals and balances

## Common Issues & Solutions

**FAL.AI Content Policy Violations:**
- Check logs for "content_policy_violation" errors
- Review prompt in `sanitize_prompt()` function
- Test with `/api/video/test-prompt` endpoint

**Gemini Analysis Timeout:**
- System returns default analysis after 30s
- User can manually edit prompts
- Check `EMERGENT_LLM_KEY` is valid

**SQLite Database:**
- Database file auto-created in `backend/database/video_gen.db`
- No external database server required
- All tables created automatically on first run
- To reset: delete `backend/database/video_gen.db` and restart server

**CORS Issues:**
- Update `CORS_ORIGINS` in backend `.env`
- Restart backend server after changes

## Code Style Guidelines

**Backend:**
- Type hints on function parameters and returns
- Pydantic models for all data validation
- Async/await for all I/O operations
- Logging with structured messages (`logger.info`, `logger.error`)

**Frontend:**
- Functional components with hooks
- Destructure props clearly
- Use Tailwind utility classes over custom CSS
- Toast notifications for user feedback (success/error)

## Deployment Considerations

- Backend uses SQLite (single file database - easy to backup)
- API keys must be secured in environment variables (never commit)
- Frontend build outputs to `frontend/build/`
- Backend serves on port 8001, frontend proxies API calls
- Cloudinary used for persistent storage (local uploads are temporary)
- Database backup: Simply copy `backend/database/video_gen.db` file
- Windows-optimized with `.bat` start scripts included

## Quick Start Summary

1. **First Time Setup**:
   ```bash
   # Backend
   cd backend
   pip install aiosqlite google-generativeai fastapi uvicorn elevenlabs fal-client cloudinary python-multipart python-dotenv gradio-client pillow

   # Frontend
   cd frontend
   npm install --legacy-peer-deps
   ```

2. **Run Application**:
   ```bash
   # Option A: Start everything
   start-all.bat

   # Option B: Start individually
   start-backend.bat  # Terminal 1
   start-frontend.bat # Terminal 2
   ```

3. **Access**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

4. **Test Backend**:
   ```bash
   cd backend
   python test_server.py
   ```
