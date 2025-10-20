# 🚀 DESENVOLVIMENTO LOCAL - Setup Completo

## 📋 Pré-requisitos

- Python 3.10+
- Node.js 18+
- Git

## 🔧 Setup Backend (Localhost)

### 1. Instalar dependências

```bash
cd backend
pip install -r requirements.txt
pip install google-cloud-aiplatform  # Para Veo Google Direct
```

### 2. Criar arquivo `.env` na raiz do projeto

```bash
# backend/.env

# APIs Obrigatórias
GEMINI_KEY=sua_chave_gemini
FAL_KEY=sua_chave_fal

# APIs Opcionais
ELEVENLABS_API_KEY=sua_chave_elevenlabs

# Google Cloud (para Veo Direct - OPCIONAL)
GOOGLE_CLOUD_PROJECT_ID=seu_project_id
GOOGLE_APPLICATION_CREDENTIALS=./veo-service-account.json

# Configuração
PORT=8000
```

### 3. Iniciar backend

```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Backend estará em: http://localhost:8000

## 🎨 Setup Frontend (Localhost)

### 1. Instalar dependências

```bash
cd frontend
npm install --legacy-peer-deps
```

### 2. Criar arquivo `.env` no frontend

```bash
# frontend/.env.local

REACT_APP_API_URL=http://localhost:8000
```

### 3. Iniciar frontend

```bash
cd frontend
npm start
```

Frontend estará em: http://localhost:3000

## ✅ Teste Rápido

1. Abra http://localhost:3000
2. Faça upload de uma imagem
3. Veja a análise do Gemini
4. Escolha o provider de vídeo (FAL.AI ou Google Direct)
5. Gere o vídeo

## 🔥 Comandos Rápidos

### Start All (Windows)
```bash
start-all.bat
```

### Start Backend Only
```bash
start-backend.bat
```

### Start Frontend Only
```bash
start-frontend.bat
```

## 📝 URLs Locais

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## 🐛 Troubleshooting

### Backend não inicia
```bash
# Verificar porta 8000
netstat -ano | findstr :8000

# Matar processo se necessário
taskkill /PID <pid> /F
```

### Frontend não conecta ao backend
- Verificar se backend está rodando
- Verificar `.env.local` tem `REACT_APP_API_URL=http://localhost:8000`
- Limpar cache: `npm start` com Ctrl+C e reiniciar

### Erro de CORS
- Backend já está configurado para aceitar localhost:3000
- Verificar `server.py` tem CORS habilitado
