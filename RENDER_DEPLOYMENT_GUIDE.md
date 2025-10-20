# 🚀 Guia de Deploy no Render.com

## ✅ Status da Validação do `render.yaml`

**Data:** 19 de Outubro de 2025  
**Validação:** Comparação entre `render.yaml` e código do projeto

---

## 📊 Resumo da Validação

| Item | Status | Observações |
|------|--------|-------------|
| **Backend Service** | ✅ **CORRETO** | Configuração alinhada com o código |
| **Frontend Service** | ✅ **CORRETO** | Build estático configurado adequadamente |
| **Health Check** | ✅ **IMPLEMENTADO** | Endpoint `/health` existe e funcional |
| **Env Vars** | ✅ **CORRIGIDO** | `ELEVENLABS_KEY` alinhado, `BACKEND_URL` adicionado |
| **Build Script** | ✅ **VALIDADO** | `build.sh` compatível com Linux/Render |
| **Secrets** | ⚠️ **AÇÃO NECESSÁRIA** | Configurar secrets no painel do Render |

---

## 🔧 Correções Aplicadas

### 1. ✅ Variável ElevenLabs Corrigida

**Problema Identificado:**
- `render.yaml` definia: `ELEVENLABS_API_KEY`
- Código backend espera: `ELEVENLABS_KEY`

**Correção Aplicada:**
```yaml
# ANTES (ERRADO)
- key: ELEVENLABS_API_KEY
  sync: false

# DEPOIS (CORRETO)
- key: ELEVENLABS_KEY
  sync: false
```

**Impacto:** Agora o `/health` endpoint detectará corretamente a configuração do ElevenLabs.

---

### 2. ✅ BACKEND_URL Adicionado

**Motivo:**
O código backend lê `BACKEND_URL` com fallback para `http://localhost:8001`. Para deploy no Render, deve apontar para o domínio público.

**Correção Aplicada:**
```yaml
- key: BACKEND_URL
  value: https://talking-photo-backend.onrender.com
```

**⚠️ IMPORTANTE:** Confirme se `talking-photo-backend.onrender.com` é o domínio correto do seu serviço no painel do Render. Atualize se necessário.

---

## 🔒 Configuração de Secrets no Painel do Render

### Variáveis que DEVEM ser configuradas como Secrets:

No painel do Render, acesse cada serviço e adicione as seguintes variáveis de ambiente:

#### **Backend Service: `talking-photo-backend`**

| Variável | Tipo | Onde Obter | Obrigatória? |
|----------|------|------------|--------------|
| `GEMINI_KEY` | Secret | [Google AI Studio](https://aistudio.google.com/app/apikey) | ✅ Sim |
| `ELEVENLABS_KEY` | Secret | [ElevenLabs API Keys](https://elevenlabs.io/app/settings/api-keys) | ✅ Sim |
| `FAL_KEY` | Secret | [FAL.AI Dashboard](https://fal.ai/dashboard/keys) | ✅ Sim |
| `CLOUDINARY_CLOUD_NAME` | Secret | [Cloudinary Console](https://console.cloudinary.com/) | ⚠️ Opcional* |
| `CLOUDINARY_API_KEY` | Secret | [Cloudinary Console](https://console.cloudinary.com/) | ⚠️ Opcional* |
| `CLOUDINARY_API_SECRET` | Secret | [Cloudinary Console](https://console.cloudinary.com/) | ⚠️ Opcional* |

**\*Nota sobre Cloudinary:** O sistema atualmente usa **Base64 direto** (sem Cloudinary). As variáveis Cloudinary são opcionais, mas o `/health` endpoint reportará "not_configured" se ausentes.

---

## 📝 Passo a Passo para Deploy

### **1️⃣ Preparação Local (Já Feito)**

- ✅ `render.yaml` corrigido e validado
- ✅ Endpoint `/health` implementado
- ✅ `build.sh` testado e funcional
- ✅ Env vars alinhadas com o código

### **2️⃣ Criar Serviços no Render**

#### **Opção A: Deploy via `render.yaml` (Recomendado)**

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em **"New +"** → **"Blueprint"**
3. Conecte seu repositório GitHub: `mauricioamorim3r/talking-photo-generator`
4. O Render detectará automaticamente o `render.yaml`
5. Revise os serviços:
   - ✅ `talking-photo-backend` (Web Service)
   - ✅ `talking-photo-frontend` (Static Site)
6. Clique em **"Apply"**

#### **Opção B: Deploy Manual**

**Backend:**
1. **New +** → **Web Service**
2. Conecte o repositório
3. Configurações:
   - **Name:** `talking-photo-backend`
   - **Region:** Oregon (ou outro)
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `./build.sh`
   - **Start Command:** `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

**Frontend:**
1. **New +** → **Static Site**
2. Conecte o repositório
3. Configurações:
   - **Name:** `talking-photo-frontend`
   - **Branch:** `main`
   - **Build Command:** `cd frontend && npm install --legacy-peer-deps && npm run build`
   - **Publish Directory:** `frontend/build`

---

### **3️⃣ Configurar Secrets (CRÍTICO)**

**Para o Backend Service:**

1. Acesse o serviço `talking-photo-backend`
2. Vá em **"Environment"** → **"Environment Variables"**
3. Adicione cada variável manualmente:

```bash
# Clique em "Add Environment Variable" para cada uma:

GEMINI_KEY=sua_chave_gemini_aqui
ELEVENLABS_KEY=sua_chave_elevenlabs_aqui
FAL_KEY=sua_chave_fal_aqui
BACKEND_URL=https://talking-photo-backend.onrender.com

# Opcional (se usar Cloudinary):
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret
```

4. Clique em **"Save Changes"**
5. O serviço será **redeploy automaticamente**

**Para o Frontend Service:**

1. Acesse o serviço `talking-photo-frontend`
2. Vá em **"Environment"**
3. Adicione:

```bash
REACT_APP_BACKEND_URL=https://talking-photo-backend.onrender.com
```

4. **⚠️ IMPORTANTE:** Atualize para o domínio REAL do backend (veja no painel do Render)

---

### **4️⃣ Validar Deploy**

#### **A. Testar Health Check do Backend**

Após deploy completo, acesse:
```
https://talking-photo-backend.onrender.com/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T...",
  "services": {
    "api": "ok",
    "database": "ok",
    "cloudinary": "not_configured",  // OK se não usar
    "gemini": "configured",          // ✅ DEVE ser "configured"
    "elevenlabs": "configured",      // ✅ DEVE ser "configured"
    "fal": "configured"              // ✅ DEVE ser "configured"
  }
}
```

**Se algum serviço mostrar "not_configured":**
- Volte ao passo 3 e verifique se a secret foi adicionada corretamente
- Aguarde o redeploy (leva ~2 minutos)
- Teste novamente

#### **B. Testar API de Providers**

```bash
curl https://talking-photo-backend.onrender.com/api/video/providers
```

**Resposta esperada:**
```json
[
  {
    "id": "fal_veo3",
    "name": "FAL.AI Veo 3.1",
    "provider": "fal",
    ...
  },
  {
    "id": "google_veo3",
    "name": "Google Veo 3 Direct",
    "provider": "google",
    ...
  }
]
```

#### **C. Testar Frontend**

Acesse:
```
https://talking-photo-frontend.onrender.com
```

**Verificar:**
- ✅ Página carrega sem erros 404
- ✅ Console não mostra erros de CORS
- ✅ Backend está conectado (testar upload de imagem)
- ✅ Provider cards aparecem após análise

---

## 🐛 Troubleshooting

### **Problema 1: Backend não inicia**

**Erro:** `ModuleNotFoundError: No module named 'fastapi'`

**Solução:**
1. Verifique se `build.sh` tem permissão de execução:
   ```bash
   chmod +x build.sh
   ```
2. Confirme que `requirements-minimal.txt` existe no diretório `backend/`
3. Veja os logs de build no painel do Render

### **Problema 2: Frontend não conecta ao backend**

**Erro no Console:** `net::ERR_CONNECTION_REFUSED`

**Solução:**
1. Confirme que `REACT_APP_BACKEND_URL` aponta para o domínio correto
2. Verifique se o backend está rodando (acesse `/health`)
3. Confirme CORS no backend (já configurado em `server.py`)

### **Problema 3: `/health` retorna "not_configured" para APIs**

**Causa:** Secrets não foram definidos corretamente

**Solução:**
1. Acesse **Environment Variables** no painel do Render
2. Clique em **"Add Environment Variable"**
3. Cole a chave completa (sem espaços extras)
4. Salve e aguarde redeploy
5. Teste `/health` novamente após 2 minutos

### **Problema 4: Build do Frontend falha**

**Erro:** `ENOENT: no such file or directory`

**Solução:**
1. Confirme que o `buildCommand` está correto:
   ```bash
   cd frontend && npm install --legacy-peer-deps && npm run build
   ```
2. Verifique se `package.json` existe em `frontend/`
3. Confirme `NODE_VERSION: 18.17.0` no `render.yaml`

### **Problema 5: Database resets após deploy**

**Causa:** Render Free Tier não suporta disco persistente

**Observação no `render.yaml`:**
```yaml
databases: []
  # SQLite database will be in persistent disk
  # Note: Render free tier doesn't support persistent disk
  # Database will reset on each deploy
  # Consider upgrading to paid plan for persistent storage
```

**Soluções:**
- **Gratuita:** Aceitar que o banco reseta (ok para desenvolvimento)
- **Paga:** Upgrade para plano Starter ($7/mês) com disco persistente
- **Alternativa:** Migrar para PostgreSQL (Render oferece 90 dias grátis)

---

## 📊 Checklist Final de Deploy

Antes de considerar o deploy completo, confirme:

### **Backend**
- [ ] Serviço criado no Render
- [ ] `build.sh` executou sem erros
- [ ] Uvicorn iniciou corretamente
- [ ] `/health` retorna status 200
- [ ] Todas as APIs mostram "configured" no `/health`
- [ ] `/api/video/providers` retorna 3 providers
- [ ] Logs não mostram erros críticos

### **Frontend**
- [ ] Build gerou arquivos em `frontend/build/`
- [ ] Site acessível via domínio `.onrender.com`
- [ ] Página inicial carrega sem erros 404
- [ ] Console DevTools sem erros de CORS
- [ ] Upload de imagem funciona
- [ ] Provider cards aparecem após análise

### **Integração**
- [ ] Frontend consegue chamar `/api/video/providers`
- [ ] Análise de imagem via Gemini funciona
- [ ] Geração de vídeo com FAL.AI funciona
- [ ] Geração de vídeo com Google funciona
- [ ] Custos calculados corretamente

---

## 🎯 Próximos Passos (Pós-Deploy)

### **1. Monitoramento**

Configure alertas no Render:
- **Uptime Monitoring:** Render faz ping no `/health` automaticamente
- **Logs:** Acompanhe erros em tempo real no painel
- **Metrics:** Veja CPU, memória e requests no dashboard

### **2. Domínio Customizado (Opcional)**

1. Vá em **Settings** do serviço frontend
2. Clique em **"Custom Domains"**
3. Adicione seu domínio (ex: `videomagic.app`)
4. Configure DNS conforme instruções do Render
5. SSL/TLS será provisionado automaticamente

### **3. Upgrade para Plano Pago (Se Necessário)**

**Limitações do Free Tier:**
- ⏱️ Backend "hiberna" após 15 minutos inativo
- 💾 Database reseta a cada deploy
- 🚀 100 GB de bandwidth/mês
- ⏳ Primeiro request após hibernação demora ~30 segundos

**Benefícios do Starter ($7/mês):**
- ✅ Sem hibernação
- ✅ Disco persistente (512 MB SSD)
- ✅ 400 GB de bandwidth
- ✅ Priority builds

### **4. Backup de Database (Se Usar Paid Plan)**

```bash
# Script para backup automático (adicionar no backend)
# backend/backup_db.py

import sqlite3
from datetime import datetime
import os

def backup_database():
    db_path = "database/app.db"
    backup_dir = "database/backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}/backup_{timestamp}.db"
    
    conn = sqlite3.connect(db_path)
    backup_conn = sqlite3.connect(backup_path)
    conn.backup(backup_conn)
    backup_conn.close()
    conn.close()
    
    print(f"✅ Backup criado: {backup_path}")

if __name__ == "__main__":
    backup_database()
```

### **5. CI/CD Automático**

O Render já faz deploy automático a cada push na branch `main`. Para controlar:

1. **Auto-Deploy ON:** Deploy automático em cada commit
2. **Auto-Deploy OFF:** Deploy manual via botão no painel

Configurar em: **Settings** → **Build & Deploy** → **Auto-Deploy**

---

## 📚 Referências Úteis

- [Render Docs - Web Services](https://render.com/docs/web-services)
- [Render Docs - Static Sites](https://render.com/docs/static-sites)
- [Render Docs - Environment Variables](https://render.com/docs/configure-environment-variables)
- [Render Docs - Health Checks](https://render.com/docs/health-checks)
- [FastAPI on Render](https://render.com/docs/deploy-fastapi)
- [React on Render](https://render.com/docs/deploy-create-react-app)

---

## ✅ Conclusão

Seu `render.yaml` está **100% validado e pronto para deploy**! 🎉

**Correções aplicadas:**
1. ✅ `ELEVENLABS_API_KEY` → `ELEVENLABS_KEY`
2. ✅ `BACKEND_URL` adicionado
3. ✅ Validação do endpoint `/health`
4. ✅ Build script confirmado funcional

**Próxima ação:** Seguir o **Passo a Passo** acima e configurar os secrets no painel do Render.

---

**🚀 Boa sorte com o deploy!**

Se encontrar qualquer problema, volte a este guia e consulte a seção **Troubleshooting**.

**Data do documento:** 19 de Outubro de 2025  
**Última atualização:** Após validação completa do `render.yaml`
