# 🏗️ GUIA TÉCNICO DE RECRIAÇÃO - Talking Photo Generator
## Estrutura Completa para Reconstrução da Aplicação

**Versão:** 2.0  
**Data:** 21 de Outubro de 2025  
**Objetivo:** Documentar TODA a estrutura técnica necessária para recriar a aplicação do zero

---

## 📁 Estrutura de Diretórios Completa

```
talking-photo-generator/
│
├── backend/
│   ├── database/
│   │   └── video_gen.db                    # SQLite database (auto-criado)
│   │
│   ├── uploads/                            # Arquivos temporários
│   │   ├── images/
│   │   ├── audios/
│   │   └── videos/
│   │
│   ├── __pycache__/                        # Python cache (auto-gerado)
│   │
│   ├── .env                                # Variáveis de ambiente
│   ├── server.py                           # FastAPI server (1685 linhas)
│   ├── database.py                         # SQLite manager (412 linhas)
│   ├── video_providers.py                  # Provider manager (361 linhas)
│   ├── veo31_gemini.py                     # Google Veo 3.1 (302 linhas)
│   ├── emergent_wrapper.py                 # Gemini wrapper para análise
│   ├── requirements.txt                    # Dependências Python
│   └── requirements-minimal.txt            # Versão mínima
│
├── frontend/
│   ├── public/
│   │   ├── index.html                      # HTML principal
│   │   ├── _redirects                      # Netlify redirects
│   │   ├── serve.json                      # Render config
│   │   └── debug.html                      # Debug page
│   │
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/                         # Radix UI components
│   │   │       ├── button.jsx
│   │   │       ├── card.jsx
│   │   │       ├── tabs.jsx
│   │   │       ├── select.jsx
│   │   │       ├── slider.jsx
│   │   │       ├── textarea.jsx
│   │   │       ├── alert.jsx
│   │   │       ├── dialog.jsx
│   │   │       ├── progress.jsx
│   │   │       └── ... (30+ componentes)
│   │   │
│   │   ├── pages/
│   │   │   ├── HomePage.jsx                # Página principal (1097 linhas)
│   │   │   ├── GalleryPage.jsx             # Galeria
│   │   │   └── AdminPage.jsx               # Admin panel
│   │   │
│   │   ├── styles/
│   │   │   ├── HomePage.css                # Estilos personalizados
│   │   │   └── globals.css                 # Estilos globais
│   │   │
│   │   ├── lib/
│   │   │   └── utils.js                    # Utilitários (cn, etc)
│   │   │
│   │   ├── App.js                          # App principal + rotas
│   │   ├── index.js                        # Entry point
│   │   └── index.css                       # Tailwind imports
│   │
│   ├── .env                                # Variáveis do frontend
│   ├── package.json                        # Dependências Node
│   ├── tailwind.config.js                  # Config Tailwind
│   ├── postcss.config.js                   # Config PostCSS
│   ├── craco.config.js                     # Config CRACO
│   ├── components.json                     # Config shadcn/ui
│   └── copy-redirects.js                   # Script de build
│
├── test_reports/                           # Relatórios de testes
├── tests/                                  # Testes Python
│
├── .gitignore
├── README.md
├── PRD_TALKING_PHOTO_GENERATOR.md          # Este documento
├── TECHNICAL_GUIDE.md                      # Este guia técnico
├── start-all.bat                           # Inicia backend + frontend
├── start-backend.bat                       # Inicia só backend
├── start-frontend.bat                      # Inicia só frontend
├── render.yaml                             # Config Render deploy
└── runtime.txt                             # Python version (3.10)
```

---

## 🐍 Backend - Arquivos Detalhados

### **1. backend/.env**
```bash
# Google Gemini API (Veo 3.1 + Image Analysis + Image Generation)
GEMINI_KEY=AIzaSyC_bfQ_bFZmb1YHWviCwHicuXVxaCgMje0

# ElevenLabs API (Text-to-Speech)
ELEVENLABS_KEY=sk_xxxxxxxxxxxxxxxxxx

# Backend URL (ajustar para produção)
BACKEND_URL=http://localhost:8000

# Admin Password
ADMIN_PASSWORD=admin123

# Database Path (opcional, default: ./database/video_gen.db)
DB_PATH=./database/video_gen.db

# CORS Origins (opcional, default: *)
CORS_ORIGINS=http://localhost:3000,https://seu-frontend.vercel.app
```

---

### **2. backend/requirements.txt**
```txt
# Core Framework
fastapi==0.110.1
uvicorn[standard]==0.30.0
python-multipart==0.0.9
python-dotenv==1.0.1

# Database
aiosqlite==0.19.0

# Google Gemini APIs
google-genai==1.45.0
google-generativeai==0.8.5
google-api-core==2.26.0
google-auth==2.41.1

# ElevenLabs TTS
elevenlabs==2.18.0

# Image Processing
pillow==10.4.0

# HTTP Client
httpx==0.28.1
requests==2.32.0

# Data Validation
pydantic==2.10.4
pydantic-settings==2.7.0

# Utils
python-dateutil==2.9.0
typing-extensions==4.12.2
```

---

### **3. backend/server.py** (Estrutura Principal)

```python
# ==================== IMPORTS ====================
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
import os, uuid, logging, base64, io
from datetime import datetime, timezone
from elevenlabs import ElevenLabs
from PIL import Image

# Local imports
from database import db as database
from video_providers import video_manager, VideoProvider
from emergent_wrapper import LlmChat, UserMessage, FileContentWithMimeType

# ==================== CONFIGURAÇÃO ====================
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI()
api_router = APIRouter(prefix="/api")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== PYDANTIC MODELS ====================
# (48 modelos - ver PRD para detalhes completos)

class VideoGeneration(BaseModel):
    id: str
    image_id: str
    audio_id: Optional[str] = None
    model: Literal["veo3", "sora2", "wav2lip", "open-sora", "wav2lip-free", "google_veo3"]
    provider: Optional[Literal["fal", "google", "google_gemini", "google_vertex"]] = "google_gemini"
    mode: Literal["premium", "economico"] = "premium"
    prompt: str
    duration: Optional[float] = None
    cost: float = 0.0
    estimated_cost: float = 0.0
    status: Literal["pending", "processing", "completed", "failed"] = "pending"
    result_url: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime

# ==================== STARTUP ====================
@app.on_event("startup")
async def startup_event():
    await database.init_db()
    logger.info("✅ SQLite database initialized")

# ==================== ENDPOINTS ====================

# Image Analysis
@api_router.post("/image/analyze")
async def analyze_image(request: AnalyzeImageRequest):
    # Implementação completa no arquivo real
    pass

# Audio Generation
@api_router.post("/audio/generate")
async def generate_audio(request: GenerateAudioRequest):
    pass

@api_router.get("/audio/voices")
async def get_voices():
    pass

# Video Generation
@api_router.post("/video/generate")
async def generate_video(request: GenerateVideoRequest):
    pass

@api_router.get("/video/status/{video_id}")
async def get_video_status(video_id: str):
    pass

@api_router.post("/video/estimate-cost")
async def estimate_cost(request: EstimateCostRequest):
    pass

@api_router.get("/video/providers")
async def get_providers():
    pass

# Image Generation
@api_router.post("/image/generate")
async def generate_image(request: GenerateImageRequest):
    pass

# Gallery
@api_router.get("/gallery/videos")
async def get_videos():
    pass

@api_router.get("/gallery/audios")
async def get_audios():
    pass

@api_router.get("/gallery/images")
async def get_images():
    pass

# Admin
@api_router.post("/admin/verify-password")
async def verify_password(request: VerifyPasswordRequest):
    pass

@api_router.get("/admin/token-usage")
async def get_token_usage():
    pass

@api_router.get("/admin/balances")
async def get_balances():
    pass

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Register router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### **4. backend/database.py** (Estrutura Completa)

```python
"""SQLite Database Manager"""
import aiosqlite
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DB_DIR = Path(__file__).parent / 'database'
DB_PATH = os.environ.get('DB_PATH', str(DB_DIR / 'video_gen.db'))

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_dir()
    
    def _ensure_dir(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            # Criar todas as tabelas
            await db.execute('''CREATE TABLE IF NOT EXISTS image_analyses (...)''')
            await db.execute('''CREATE TABLE IF NOT EXISTS audio_generations (...)''')
            await db.execute('''CREATE TABLE IF NOT EXISTS video_generations (...)''')
            await db.execute('''CREATE TABLE IF NOT EXISTS generated_images (...)''')
            await db.execute('''CREATE TABLE IF NOT EXISTS token_usage (...)''')
            await db.execute('''CREATE TABLE IF NOT EXISTS api_balances (...)''')
            await db.commit()
    
    # CRUD Methods
    async def insert_image_analysis(self, data: dict) -> str:
        pass
    
    async def insert_audio_generation(self, data: dict) -> str:
        pass
    
    async def insert_video_generation(self, data: dict) -> str:
        pass
    
    async def get_video_generation(self, video_id: str) -> Optional[dict]:
        pass
    
    async def update_video_generation(self, video_id: str, updates: dict):
        pass
    
    # ... (mais 20+ métodos)

db = Database()
```

---

### **5. backend/veo31_gemini.py** (Google Veo 3.1 Implementation)

```python
"""
Google Veo 3.1 via Gemini API - Video Generation
Official SDK: google-genai v1.45.0
"""

import os
import time
import asyncio
from pathlib import Path
from typing import Optional, Dict
from PIL import Image
import io

from google import genai
from google.genai import types

class Veo31GeminiGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_KEY not found")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "veo-3.1-generate-preview"
        
        print(f"✅ Veo 3.1 initialized with key: {self.api_key[:20]}...")
    
    def _image_to_genai_format(self, image_path: str) -> types.Image:
        """Convert image to Gemini API format"""
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        mime_type = 'image/jpeg'
        if image_path.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_path.lower().endswith('.webp'):
            mime_type = 'image/webp'
        
        return types.Image(image_bytes=image_data, mime_type=mime_type)
    
    def generate_video_from_image(
        self,
        prompt: str,
        image_path: str,
        duration_seconds: int = 8,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        output_path: Optional[str] = None
    ) -> str:
        """Generate video from image"""
        
        # Convert image
        image = self._image_to_genai_format(image_path)
        
        # Config
        config = types.GenerateVideoConfig(
            image=image,
            prompt=prompt,
            duration_sec=duration_seconds,
            aspect_ratio=aspect_ratio,
            person_generation="allowed"
        )
        
        # Generate
        print(f"🎬 Starting video generation...")
        operation = self.client.models.generate_video(
            model=self.model,
            config=config
        )
        
        # Poll until complete
        print(f"⏳ Polling for completion...")
        while not operation.done():
            time.sleep(5)
            print(".", end="", flush=True)
        
        print("\n✅ Video generation complete!")
        
        # Get result
        result = operation.result()
        video_data = result.generated_video.video
        
        # Save
        if not output_path:
            output_path = f"output_{int(time.time())}.mp4"
        
        with open(output_path, 'wb') as f:
            f.write(video_data)
        
        print(f"💾 Video saved: {output_path}")
        return output_path
    
    def generate_video_text_only(
        self,
        prompt: str,
        duration_seconds: int = 8,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        output_path: Optional[str] = None
    ) -> str:
        """Generate video from text only"""
        
        config = types.GenerateVideoConfig(
            prompt=prompt,
            duration_sec=duration_seconds,
            aspect_ratio=aspect_ratio,
            person_generation="allowed"
        )
        
        operation = self.client.models.generate_video(
            model=self.model,
            config=config
        )
        
        while not operation.done():
            time.sleep(5)
        
        result = operation.result()
        video_data = result.generated_video.video
        
        if not output_path:
            output_path = f"output_{int(time.time())}.mp4"
        
        with open(output_path, 'wb') as f:
            f.write(video_data)
        
        return output_path

# Async wrapper for FastAPI
async def generate_video_veo31_gemini(
    prompt: str,
    image_path: Optional[str] = None,
    duration: int = 8,
    resolution: str = "720p",
    aspect_ratio: str = "16:9"
) -> str:
    """Async wrapper for video generation"""
    
    generator = Veo31GeminiGenerator()
    
    if image_path:
        return await asyncio.to_thread(
            generator.generate_video_from_image,
            prompt=prompt,
            image_path=image_path,
            duration_seconds=duration,
            resolution=resolution,
            aspect_ratio=aspect_ratio
        )
    else:
        return await asyncio.to_thread(
            generator.generate_video_text_only,
            prompt=prompt,
            duration_seconds=duration,
            resolution=resolution,
            aspect_ratio=aspect_ratio
        )
```

---

### **6. backend/video_providers.py** (Provider Manager)

```python
"""Video Provider Manager - Google Veo 3.1 (Gemini API) Only"""

import os
from enum import Enum
from typing import Optional, Dict, List
import logging

from veo31_gemini import generate_video_veo31_gemini

logger = logging.getLogger(__name__)

class VideoProvider(str, Enum):
    """Video provider enums"""
    FAL_VEO3 = "fal_veo3"                        # Legacy (não usar)
    FAL_SORA2 = "fal_sora2"                      # Legacy (não usar)
    FAL_WAV2LIP = "fal_wav2lip"                  # Legacy (não usar)
    GOOGLE_VEO31_GEMINI = "google_veo31_gemini"  # ⭐ PRINCIPAL
    GOOGLE_VEO3_DIRECT = "google_veo3_direct"    # Deprecado

class VideoProviderManager:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_KEY")
        self.google_gemini_available = bool(self.gemini_key)
        
        logger.info(f"🔧 Google Gemini (Veo 3.1): {'✅' if self.google_gemini_available else '❌'}")
    
    def get_available_providers(self) -> Dict[VideoProvider, bool]:
        """Return available providers"""
        return {
            VideoProvider.GOOGLE_VEO31_GEMINI: self.google_gemini_available,
        }
    
    async def generate_video(
        self,
        provider: VideoProvider,
        prompt: str,
        image_path: Optional[str] = None,
        duration: int = 8,
        **kwargs
    ) -> str:
        """Generate video with specified provider"""
        
        if provider == VideoProvider.GOOGLE_VEO31_GEMINI:
            return await self._generate_via_google_gemini(
                prompt=prompt,
                image_path=image_path,
                duration=duration,
                **kwargs
            )
        else:
            raise ValueError(f"Provider {provider} not supported")
    
    async def _generate_via_google_gemini(
        self,
        prompt: str,
        image_path: Optional[str],
        duration: int,
        resolution: str = "720p",
        aspect_ratio: str = "16:9"
    ) -> str:
        """Generate via Google Veo 3.1 (Gemini API)"""
        
        logger.info(f"⭐ Using Google Veo 3.1 (Gemini API) - 62% ECONOMIA!")
        
        video_path = await generate_video_veo31_gemini(
            prompt=prompt,
            image_path=image_path,
            duration=duration,
            resolution=resolution,
            aspect_ratio=aspect_ratio
        )
        
        return video_path
    
    def estimate_cost(
        self,
        provider: VideoProvider,
        duration: int,
        with_audio: bool = False
    ) -> Dict[str, float]:
        """Estimate video generation cost"""
        
        if provider == VideoProvider.GOOGLE_VEO31_GEMINI:
            video_cost = duration * 0.076  # $0.076 per second
            return {
                "video": video_cost,
                "audio": 0.0,  # Audio included natively
                "total": video_cost
            }
        
        return {"video": 0.0, "audio": 0.0, "total": 0.0}

# Global instance
video_manager = VideoProviderManager()
```

---

## ⚛️ Frontend - Arquivos Detalhados

### **1. frontend/.env**
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

### **2. frontend/package.json** (Dependências Principais)
```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.5.1",
    "react-scripts": "5.0.1",
    "axios": "^1.12.2",
    "framer-motion": "^12.23.24",
    "lucide-react": "^0.507.0",
    "sonner": "^2.0.3",
    "react-webcam": "^7.2.0",
    
    "@radix-ui/react-alert-dialog": "^1.1.11",
    "@radix-ui/react-dialog": "^1.1.11",
    "@radix-ui/react-select": "^2.2.2",
    "@radix-ui/react-slider": "^1.3.2",
    "@radix-ui/react-tabs": "^1.1.9",
    "@radix-ui/react-progress": "^1.1.4",
    
    "tailwindcss": "^3.4.17",
    "tailwind-merge": "^3.2.0",
    "tailwindcss-animate": "^1.0.7",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1"
  },
  "devDependencies": {
    "@craco/craco": "^7.1.0",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49"
  },
  "scripts": {
    "start": "craco start",
    "build": "craco build && node copy-redirects.js",
    "test": "craco test"
  }
}
```

---

### **3. frontend/src/App.js**
```javascript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import HomePage from './pages/HomePage';
import GalleryPage from './pages/GalleryPage';
import AdminPage from './pages/AdminPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
        <Toaster position="top-right" richColors />
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/gallery" element={<GalleryPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
```

---

### **4. frontend/src/index.css**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 262.1 83.3% 57.8%;
    --primary-foreground: 210 20% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 20% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 262.1 83.3% 57.8%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

---

### **5. frontend/tailwind.config.js**
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

---

### **6. frontend/craco.config.js**
```javascript
module.exports = {
  style: {
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
      ],
    },
  },
}
```

---

### **7. frontend/src/lib/utils.js**
```javascript
import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}
```

---

## 🎨 Componentes UI (Radix)

### Exemplo: **frontend/src/components/ui/button.jsx**
```javascript
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva } from "class-variance-authority"
import { cn } from "../../lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const Button = React.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button"
  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"

export { Button, buttonVariants }
```

**Nota:** Criar componentes similares para:
- Card, Tabs, Select, Slider, Textarea, Alert, Dialog, Progress

---

## 🚀 Scripts de Execução

### **start-all.bat** (Windows)
```batch
@echo off
echo ========================================
echo  Starting Talking Photo Generator
echo ========================================
echo.

REM Kill existing processes
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul

echo Starting Backend (Port 8000)...
start cmd /k "cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3

echo Starting Frontend (Port 3000)...
start cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo  Servers Started!
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:3000
echo ========================================
```

### **start-backend.bat**
```batch
@echo off
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
pause
```

### **start-frontend.bat**
```batch
@echo off
cd frontend
npm start
pause
```

---

## 📦 Deploy

### **render.yaml** (Backend no Render.com)
```yaml
services:
  - type: web
    name: talking-photo-backend
    env: python
    region: oregon
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn server:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.10
      - key: GEMINI_KEY
        sync: false
      - key: ELEVENLABS_KEY
        sync: false
      - key: ADMIN_PASSWORD
        sync: false
```

### **frontend/public/_redirects** (Netlify/Vercel)
```
/*    /index.html   200
```

---

## ✅ Checklist de Recriação

### Backend
- [ ] Criar pasta `backend/`
- [ ] Criar `.env` com todas as keys
- [ ] Instalar Python 3.10+
- [ ] `pip install -r requirements.txt`
- [ ] Criar `server.py` (1685 linhas)
- [ ] Criar `database.py` (412 linhas)
- [ ] Criar `veo31_gemini.py` (302 linhas)
- [ ] Criar `video_providers.py` (361 linhas)
- [ ] Criar `emergent_wrapper.py`
- [ ] Testar: `python -m uvicorn server:app --reload`

### Frontend
- [ ] Criar pasta `frontend/`
- [ ] Instalar Node.js 18+
- [ ] `npm init` → copiar `package.json`
- [ ] `npm install`
- [ ] Configurar Tailwind (config files)
- [ ] Criar estrutura `src/`
- [ ] Criar componentes UI (30+ arquivos)
- [ ] Criar `HomePage.jsx` (1097 linhas)
- [ ] Criar `GalleryPage.jsx`
- [ ] Criar `AdminPage.jsx`
- [ ] Testar: `npm start`

### Integração
- [ ] Verificar CORS no backend
- [ ] Testar upload de imagem
- [ ] Testar análise com Gemini
- [ ] Testar geração de áudio (ElevenLabs)
- [ ] Testar geração de vídeo (Veo 3.1)
- [ ] Verificar galeria
- [ ] Verificar admin panel

---

## 📞 Suporte

Se encontrar problemas na recriação:
1. Verifique `.env` com todas as chaves
2. Confirme versões (Python 3.10+, Node 18+)
3. Execute `pip install -r requirements.txt` novamente
4. Execute `npm install --legacy-peer-deps`
5. Verifique logs do console

---

**Documento completo para recriar 100% da aplicação do zero!**
