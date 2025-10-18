# 🚀 Deploy Checklist - Render

## Antes do Deploy

### 1. Código e Configuração
- [ ] Todos os arquivos commitados
- [ ] `render.yaml` configurado
- [ ] `Procfile` criado
- [ ] `runtime.txt` criado
- [ ] `build.sh` criado
- [ ] `.gitignore` atualizado

### 2. Dependências
- [ ] `backend/requirements.txt` atualizado
- [ ] `frontend/package.json` atualizado
- [ ] Testado localmente com `start-all.bat`

### 3. API Keys Disponíveis
- [ ] `GEMINI_KEY` - Google Gemini API
- [ ] `ELEVENLABS_API_KEY` - ElevenLabs TTS
- [ ] `FAL_KEY` - FAL.AI (imagens e vídeos)
- [ ] `CLOUDINARY_CLOUD_NAME` - Storage
- [ ] `CLOUDINARY_API_KEY` - Storage
- [ ] `CLOUDINARY_API_SECRET` - Storage

## Durante o Deploy

### 4. Criar Serviços no Render

#### Backend (Web Service)
- [ ] Conectar repositório GitHub
- [ ] Nome: `talking-photo-backend`
- [ ] Branch: `main`
- [ ] Root Directory: `backend`
- [ ] Runtime: Python 3
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- [ ] Adicionar todas as Environment Variables
- [ ] Health Check Path: `/health`
- [ ] Deploy iniciado

#### Frontend (Static Site)
- [ ] Conectar repositório GitHub
- [ ] Nome: `talking-photo-frontend`
- [ ] Branch: `main`
- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm install --legacy-peer-deps && npm run build`
- [ ] Publish Directory: `build`
- [ ] Environment Variable: `REACT_APP_BACKEND_URL=[URL_DO_BACKEND]`
- [ ] Deploy iniciado

### 5. Aguardar Deploy
- [ ] Backend build completo (5-10 min)
- [ ] Frontend build completo (5-10 min)
- [ ] Sem erros nos logs

## Após o Deploy

### 6. Testes Básicos

#### Backend
- [ ] Health check: `https://[backend-url]/health`
- [ ] API root: `https://[backend-url]/`
- [ ] Generated images: `https://[backend-url]/api/images/generated`

#### Frontend
- [ ] Abrir no navegador: `https://[frontend-url]`
- [ ] Página carrega sem erros
- [ ] Sem erros de CORS no console
- [ ] Links de navegação funcionam

### 7. Testes Funcionais
- [ ] Gerar uma imagem com FLUX
- [ ] Upload de imagem funciona
- [ ] Análise de imagem funciona
- [ ] Geração de áudio funciona
- [ ] Geração de vídeo funciona
- [ ] Galeria exibe itens

### 8. Configurações Opcionais
- [ ] Configurar domínio customizado
- [ ] Configurar UptimeRobot (manter backend acordado)
- [ ] Configurar Google Analytics
- [ ] Adicionar mais variáveis de ambiente se necessário

## Problemas Comuns

### "Cannot connect to backend"
- [ ] Verificar se `REACT_APP_BACKEND_URL` está correto
- [ ] Verificar se backend está rodando (pode estar em sleep)
- [ ] Aguardar 30-60s para cold start

### "CORS Error"
- [ ] Verificar se está acessando via HTTPS
- [ ] Verificar logs do backend

### "Build Failed"
- [ ] Verificar logs de build
- [ ] Confirmar que `--legacy-peer-deps` está no build command
- [ ] Verificar versão do Node (18.17.0)

### "Service Unavailable"
- [ ] Backend em sleep (esperado no free tier)
- [ ] Aguardar wake up (30-60s)

## URLs Importantes

- [ ] Backend URL: `_________________________________`
- [ ] Frontend URL: `_________________________________`
- [ ] Dashboard Render: `https://dashboard.render.com`
- [ ] Repositório GitHub: `https://github.com/mauricioamorim3r/talking-photo-generator`

## Notas

Data do Deploy: __________
Tempo de Build: __________
Problemas Encontrados: 
_______________________________________________
_______________________________________________
_______________________________________________

Deploy bem-sucedido? [ ] Sim [ ] Não

---

**Para instruções detalhadas, consulte: RENDER_DEPLOY.md**
