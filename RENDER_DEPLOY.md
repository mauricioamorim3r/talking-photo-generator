# 🚀 Guia de Deploy no Render

Este guia contém todas as instruções para fazer deploy do **Talking Photo Generator** no Render.

## 📋 Pré-requisitos

Antes de começar, você precisa ter:
- ✅ Conta no [Render](https://render.com) (gratuita)
- ✅ Repositório GitHub atualizado
- ✅ API Keys configuradas:
  - `GEMINI_KEY` - Google Gemini API
  - `ELEVENLABS_API_KEY` - ElevenLabs TTS
  - `FAL_KEY` - FAL.AI para geração de imagens e vídeos
  - `CLOUDINARY_CLOUD_NAME` - Cloudinary storage
  - `CLOUDINARY_API_KEY` - Cloudinary API Key
  - `CLOUDINARY_API_SECRET` - Cloudinary API Secret

---

## 🎯 Opção 1: Deploy com render.yaml (Recomendado)

### Passo 1: Preparar o repositório

O arquivo `render.yaml` já está configurado no repositório. Certifique-se de que todos os arquivos foram commitados:

```bash
git add .
git commit -m "chore: Prepare for Render deployment"
git push origin main
```

### Passo 2: Criar Blueprint no Render

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em **"New +"** → **"Blueprint"**
3. Conecte seu repositório GitHub: `mauricioamorim3r/talking-photo-generator`
4. O Render detectará automaticamente o arquivo `render.yaml`
5. Clique em **"Apply"**

### Passo 3: Configurar Variáveis de Ambiente

Após criar o blueprint, configure as variáveis de ambiente para o **backend**:

#### Backend Service Environment Variables:
```
GEMINI_KEY=sua_chave_gemini_aqui
ELEVENLABS_API_KEY=sua_chave_elevenlabs_aqui
FAL_KEY=sua_chave_fal_aqui
CLOUDINARY_CLOUD_NAME=seu_cloud_name_aqui
CLOUDINARY_API_KEY=sua_api_key_aqui
CLOUDINARY_API_SECRET=sua_api_secret_aqui
PYTHON_VERSION=3.10.0
```

#### Frontend Service Environment Variables:
```
REACT_APP_BACKEND_URL=https://talking-photo-backend.onrender.com
NODE_VERSION=18.17.0
```

⚠️ **IMPORTANTE**: Substitua `talking-photo-backend` pela URL real do seu serviço backend no Render.

---

## 🎯 Opção 2: Deploy Manual (Separado)

### Backend (API)

1. **Criar Web Service**
   - No Render Dashboard, clique em **"New +"** → **"Web Service"**
   - Conecte o repositório GitHub
   - Configure:
     - **Name**: `talking-photo-backend`
     - **Region**: Oregon (US West)
     - **Branch**: `main`
     - **Root Directory**: `backend`
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
     - **Instance Type**: Free

2. **Adicionar Environment Variables** (seção "Environment"):
   ```
   GEMINI_KEY=sua_chave_gemini_aqui
   ELEVENLABS_API_KEY=sua_chave_elevenlabs_aqui
   FAL_KEY=sua_chave_fal_aqui
   CLOUDINARY_CLOUD_NAME=seu_cloud_name_aqui
   CLOUDINARY_API_KEY=sua_api_key_aqui
   CLOUDINARY_API_SECRET=sua_api_secret_aqui
   PYTHON_VERSION=3.10.0
   ```

3. **Configurar Health Check**
   - Path: `/health`
   - Port: deixe em branco (usa a porta padrão)

4. **Deploy**
   - Clique em **"Create Web Service"**
   - Aguarde o build e deploy (5-10 minutos)
   - Anote a URL gerada (ex: `https://talking-photo-backend.onrender.com`)

### Frontend (React)

1. **Criar Static Site**
   - No Render Dashboard, clique em **"New +"** → **"Static Site"**
   - Conecte o repositório GitHub
   - Configure:
     - **Name**: `talking-photo-frontend`
     - **Region**: Oregon (US West)
     - **Branch**: `main`
     - **Root Directory**: `frontend`
     - **Build Command**: `npm install --legacy-peer-deps && npm run build`
     - **Publish Directory**: `build`

2. **Adicionar Environment Variable**:
   ```
   REACT_APP_BACKEND_URL=https://talking-photo-backend.onrender.com
   ```
   ⚠️ Use a URL do backend criado no passo anterior

3. **Deploy**
   - Clique em **"Create Static Site"**
   - Aguarde o build (5-10 minutos)

---

## ⚠️ Limitações do Plano Free

O plano gratuito do Render tem algumas limitações:

### Backend:
- ⏸️ **Sleep após inatividade**: O serviço entra em sleep após 15 minutos sem uso
- 🕐 **Cold Start**: Primeira requisição após sleep pode levar 30-60 segundos
- 💾 **Sem disco persistente**: Banco SQLite será resetado a cada deploy
- 🔄 **750 horas/mês**: Serviço pode ficar offline no final do mês

### Frontend:
- ✅ Servido via CDN (sempre online)
- ✅ Sem limitação de tráfego

### Soluções:
1. **Para manter o serviço acordado**: Use um serviço de ping como [UptimeRobot](https://uptimerobot.com/)
2. **Para dados persistentes**: Migre para plano pago ($7/mês) com disco persistente
3. **Alternativa gratuita**: Use Railway.app ou Fly.io para backend

---

## 🔍 Verificação Pós-Deploy

Após o deploy, teste os seguintes endpoints:

### Backend API:
```bash
# Health check
curl https://talking-photo-backend.onrender.com/health

# API info
curl https://talking-photo-backend.onrender.com/

# Generated images
curl https://talking-photo-backend.onrender.com/api/images/generated
```

### Frontend:
- Abra no navegador: `https://talking-photo-frontend.onrender.com`
- Teste geração de imagem
- Verifique console do navegador (não deve ter erros de CORS)

---

## 🐛 Troubleshooting

### Problema: "Cannot connect to backend"
**Solução**: Verifique se a variável `REACT_APP_BACKEND_URL` está correta no frontend

### Problema: "Service Unavailable 503"
**Solução**: Backend está em sleep. Aguarde 30-60s para acordar.

### Problema: "CORS Error"
**Solução**: O backend já está configurado para aceitar qualquer origem. Verifique se está acessando via HTTPS.

### Problema: "Database reset on deploy"
**Solução**: Isso é esperado no plano free. Para persistência, considere:
- Migrar para plano pago com disco persistente
- Usar banco de dados externo (Supabase, PlanetScale)

### Problema: "Build failed - npm ERR!"
**Solução**: 
- Certifique-se de usar `--legacy-peer-deps` no build command
- Verifique se `NODE_VERSION=18.17.0` está configurado

### Problema: "Python module not found"
**Solução**:
- Verifique se `requirements.txt` está atualizado
- Certifique-se de que o build command está correto

---

## 📊 Monitoramento

### Logs do Backend:
1. Acesse seu serviço no Render Dashboard
2. Clique na aba **"Logs"**
3. Use filtros para debug

### Logs do Frontend:
- Console do navegador (F12)
- Network tab para verificar requisições

### Métricas:
- Render fornece métricas básicas de CPU/Memory na aba "Metrics"

---

## 🔄 Atualizações Futuras

### Deploy Automático:
O Render faz deploy automático quando você faz push para `main`:

```bash
git add .
git commit -m "feat: Nova funcionalidade"
git push origin main
```

O Render detecta o push e inicia o deploy automaticamente.

### Deploy Manual:
Se quiser forçar um redeploy:
1. Acesse o serviço no Render Dashboard
2. Clique em **"Manual Deploy"** → **"Deploy latest commit"**

---

## 💡 Próximos Passos

Depois do deploy bem-sucedido:

1. ✅ Configure domínio customizado (opcional)
2. ✅ Configure UptimeRobot para manter backend acordado
3. ✅ Adicione Google Analytics (opcional)
4. ✅ Configure backup do banco de dados
5. ✅ Migre para plano pago se precisar de persistência

---

## 📞 Suporte

Se tiver problemas:
- 📧 Suporte Render: [https://render.com/docs](https://render.com/docs)
- 💬 Discord Render: [https://discord.gg/render](https://discord.gg/render)
- 🐛 Issues GitHub: Abra uma issue no repositório

---

## ✅ Checklist Final

Antes de fazer o deploy, confirme:

- [ ] Todas as API keys estão disponíveis
- [ ] Código foi commitado e pushed para GitHub
- [ ] `render.yaml` está no root do projeto
- [ ] `requirements.txt` está atualizado
- [ ] Frontend aponta para URL correta do backend
- [ ] Testou localmente antes do deploy

---

**Pronto para deploy! 🚀**

Bom deploy e qualquer dúvida, consulte este guia novamente.
