# 🚨 CORREÇÃO: Como Configurar no Render Dashboard

O erro acontece porque você criou o serviço **manualmente** no Render, e ele está ignorando o `render.yaml`.

## ⚠️ PROBLEMA IDENTIFICADO

Quando você cria um serviço Python manualmente no Render, ele usa comandos padrão:
- Build: `pip install -r requirements.txt` (no diretório raiz ❌)
- Start: `python app.py` (não funciona para FastAPI ❌)

## ✅ SOLUÇÃO: Configurar Build Command Manualmente

### Passo 1: Acessar o Serviço

1. Vá para o Render Dashboard
2. Clique no serviço **talking-photo-backend**
3. Vá em **Settings** (no menu lateral)

### Passo 2: Atualizar Build Command

Role até a seção **Build & Deploy** e altere:

**Build Command:**
```bash
chmod +x build.sh && ./build.sh
```

**Start Command:**
```bash
cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Passo 3: Salvar e Re-deploy

1. Clique em **Save Changes** no final da página
2. Vá para a aba **Events** ou **Logs**
3. Clique em **Manual Deploy** → **Clear build cache & deploy**

---

## 🎯 ALTERNATIVA: Usar Blueprint (Mais Fácil)

Se preferir usar o `render.yaml` automático:

### Passo 1: Deletar Serviço Atual
1. No serviço talking-photo-backend
2. Settings → Scroll até o final
3. **Delete Service**

### Passo 2: Criar via Blueprint
1. Render Dashboard → **New +** → **Blueprint**
2. Conecte o repositório: `mauricioamorim3r/talking-photo-generator`
3. O Render detecta `render.yaml` automaticamente
4. Configure as variáveis de ambiente (ver abaixo)
5. Clique em **Apply**

---

## 🔐 Variáveis de Ambiente (Importante!)

Não esqueça de adicionar no serviço (Settings → Environment):

```
GEMINI_KEY=sua_chave_aqui
ELEVENLABS_API_KEY=sua_chave_aqui
FAL_KEY=sua_chave_aqui
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=sua_api_secret
```

---

## 📊 Como Verificar se Funcionou

Após o deploy, você deve ver nos logs:

```
📦 Installing Python dependencies...
Current directory: /opt/render/project/src
Changed to backend directory: /opt/render/project/src/backend
Checking requirements.txt: -rw-r--r-- 1 render render 234 Oct 19 12:34 requirements.txt
✅ Backend build completed!
```

E depois:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

---

## 🆘 Se Continuar com Erro

Me envie o **log completo** do build para eu te ajudar.

O log está em: **Logs** tab do serviço no Render.

---

**Escolha uma das opções acima e me avise o resultado!** 🚀
