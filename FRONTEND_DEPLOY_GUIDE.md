# 🚀 Guia Completo: Deploy Frontend no Render

## 📋 Pré-requisitos

✅ Backend já está no ar: https://gerador-fantasia.onrender.com  
✅ Código está no GitHub  
✅ Você tem conta no Render.com

---

## 🎯 Passo a Passo - Deploy Frontend (Static Site)

### **PASSO 1: Acessar Render Dashboard**

1. Acesse: https://dashboard.render.com/
2. Faça login na sua conta
3. Você verá seu serviço **talking-photo-backend** (já funcionando ✅)

---

### **PASSO 2: Criar Novo Static Site**

1. Clique no botão **"New +"** (canto superior direito)
2. Selecione **"Static Site"**

![Render New Service](https://docs.render.com/images/create-new-service.png)

---

### **PASSO 3: Conectar Repositório GitHub**

1. Na tela "Create a new Static Site", procure por:
   - **Repository:** `mauricioamorim3r/talking-photo-generator`
   
2. Se não aparecer:
   - Clique em **"Configure GitHub"**
   - Autorize o acesso ao repositório
   - Volte para a tela de criação

3. Clique em **"Connect"** ao lado do repositório

---

### **PASSO 4: Configurar o Static Site**

Preencha os campos:

#### **Name (Nome do Serviço)**
```
talking-photo-frontend
```

#### **Region (Região)**
```
Oregon (US West)
```
*(Mesma região do backend para menor latência)*

#### **Branch**
```
main
```

#### **Root Directory**
```
frontend
```
⚠️ **IMPORTANTE:** Isso diz ao Render que o código está na pasta `frontend/`

#### **Build Command**
```bash
npm install --legacy-peer-deps && npm run build
```

#### **Publish Directory**
```
build
```
*(Onde o React coloca os arquivos compilados)*

---

### **PASSO 5: Configurar Variáveis de Ambiente**

Role até a seção **"Environment Variables"** e clique em **"Add Environment Variable"**

Adicione esta variável:

| Key | Value |
|-----|-------|
| `REACT_APP_API_URL` | `https://gerador-fantasia.onrender.com` |

⚠️ **IMPORTANTE:** Use exatamente `REACT_APP_API_URL` (React precisa do prefixo `REACT_APP_`)

---

### **PASSO 6: Verificar Configurações**

Antes de criar, confira se está assim:

```yaml
✅ Name: talking-photo-frontend
✅ Root Directory: frontend
✅ Build Command: npm install --legacy-peer-deps && npm run build
✅ Publish Directory: build
✅ Environment Variables:
   - REACT_APP_API_URL = https://gerador-fantasia.onrender.com
```

---

### **PASSO 7: Criar Static Site**

1. Clique no botão **"Create Static Site"** (no final da página)
2. O Render vai começar o build automaticamente

---

### **PASSO 8: Acompanhar o Build**

Você verá os logs em tempo real:

```
==> Cloning from GitHub...
✅ Clone successful

==> Checking out commit...
✅ Checkout successful

==> Installing Node.js 18.17.0...
✅ Node installed

==> Running build command...
npm install --legacy-peer-deps
✅ Dependencies installed

npm run build
✅ Build successful

==> Uploading static site...
✅ Upload complete

==> Your site is live 🎉
```

**Tempo estimado:** 5-8 minutos

---

### **PASSO 9: Obter URL do Frontend**

Após o build:

1. O Render vai mostrar a URL do seu site
2. Será algo como: `https://talking-photo-frontend.onrender.com`
3. Clique na URL para abrir o site!

---

## 🔧 Configuração Adicional (OPCIONAL)

### **Custom Domain (Domínio Personalizado)**

Se você tem um domínio:

1. Vá em **"Settings"** do Static Site
2. Role até **"Custom Domains"**
3. Clique em **"Add Custom Domain"**
4. Siga as instruções para configurar o DNS

---

### **Configurar Redirecionamento do Backend**

Para que o frontend encontre o backend, precisamos atualizar o CORS no backend.

**Opção A: Permitir todos os domínios (desenvolvimento)**
- Já está configurado ✅ (CORS com `origins=["*"]`)

**Opção B: Restringir ao domínio do frontend (produção)**
- Adicione no Render (backend) → Environment:
  ```
  FRONTEND_URL=https://talking-photo-frontend.onrender.com
  ```
- Atualize `server.py` para usar essa variável no CORS

---

## 🧪 Testar o Frontend

### **1. Abrir no Navegador**
```
https://talking-photo-frontend.onrender.com
```

### **2. Verificar Console (F12)**
- Abra DevTools (F12)
- Vá na aba **Console**
- NÃO deve ter erros de CORS
- NÃO deve ter erros de conexão com API

### **3. Testar Funcionalidades**
- [ ] Upload de imagem funciona
- [ ] Geração de prompt funciona
- [ ] TTS funciona
- [ ] Geração de vídeo funciona
- [ ] Galeria carrega

---

## ❌ Solução de Problemas Comuns

### **Problema 1: Build Falha com "Module not found"**

**Solução:**
```bash
# Limpar cache do npm
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

Depois faça um novo commit e o Render vai rebuildar.

---

### **Problema 2: Site carrega mas não conecta com API**

**Sintomas:**
- Console mostra: `Failed to fetch` ou `Network Error`
- Requests para API falham

**Verificações:**

1. **Checar variável de ambiente:**
   - Render Dashboard → talking-photo-frontend → Environment
   - `REACT_APP_API_URL` deve ser `https://gerador-fantasia.onrender.com`

2. **Checar se backend está online:**
   ```bash
   curl https://gerador-fantasia.onrender.com/health
   ```

3. **Checar CORS no backend:**
   - Deve permitir requisições do frontend
   - Já está configurado com `origins=["*"]` ✅

**Solução:**
- Vá em Settings → Environment Variables
- Edite `REACT_APP_API_URL`
- Clique em **"Save Changes"**
- Render vai rebuildar automaticamente

---

### **Problema 3: Página em branco após deploy**

**Causas possíveis:**
1. `Publish Directory` errado
2. Build falhou silenciosamente
3. Rotas do React não configuradas

**Solução:**

1. **Verificar Publish Directory:**
   - Deve ser `build` (não `dist` ou `public`)

2. **Adicionar redirect rules (se necessário):**
   - Crie arquivo `frontend/public/_redirects`:
     ```
     /*    /index.html   200
     ```
   - Commit e push
   - Render vai rebuildar

3. **Verificar logs de build:**
   - Procure por erros TypeScript
   - Procure por warnings que viraram erros

---

### **Problema 4: CSS não carrega / Site sem estilos**

**Solução:**

Adicione no `frontend/public/index.html`:
```html
<base href="/" />
```

Ou edite `frontend/package.json`:
```json
{
  "homepage": "."
}
```

---

### **Problema 5: Build muito lento**

**Otimizações:**

1. **Usar cache do npm:**
   - Já habilitado automaticamente no Render ✅

2. **Build Command otimizado:**
   ```bash
   npm ci --legacy-peer-deps && npm run build
   ```
   (`npm ci` é mais rápido que `npm install`)

---

## 📊 Checklist Final

Antes de considerar o deploy completo, verifique:

### **Backend** ✅
- [x] Backend online: https://gerador-fantasia.onrender.com
- [x] Health check passa: `/health`
- [x] CORS configurado
- [x] Environment variables configuradas

### **Frontend** 🔄
- [ ] Static Site criado no Render
- [ ] Build passou sem erros
- [ ] Site acessível publicamente
- [ ] `REACT_APP_API_URL` configurado corretamente
- [ ] Console sem erros (F12)
- [ ] Todas as funcionalidades testadas

### **Integração** 🔄
- [ ] Frontend consegue fazer requests para backend
- [ ] Upload de imagem funciona
- [ ] APIs de IA respondem
- [ ] Galeria funciona

---

## 🎉 Resultado Esperado

Após seguir todos os passos:

✅ **Frontend:** `https://talking-photo-frontend.onrender.com`  
✅ **Backend:** `https://gerador-fantasia.onrender.com`  
✅ **Ambos funcionando e integrados**  

---

## 📝 Comandos Úteis

### **Forçar Rebuild Manual**
1. Dashboard → talking-photo-frontend
2. Clique em **"Manual Deploy"**
3. Selecione **"Clear build cache & deploy"**

### **Ver Logs em Tempo Real**
1. Dashboard → talking-photo-frontend
2. Clique na aba **"Logs"**
3. Logs são atualizados automaticamente

### **Rollback para Deploy Anterior**
1. Dashboard → talking-photo-frontend
2. Vá em **"Events"**
3. Encontre o deploy anterior
4. Clique em **"Rollback to this deploy"**

---

## 🆘 Precisa de Ajuda?

Se encontrar problemas:

1. **Copie os logs de erro** (Dashboard → Logs)
2. **Me envie** a mensagem de erro completa
3. Vou ajudar a resolver! 🤝

---

## 📚 Links Úteis

- **Render Docs - Static Sites:** https://render.com/docs/static-sites
- **Render Docs - Environment Variables:** https://render.com/docs/environment-variables
- **React Deployment:** https://create-react-app.dev/docs/deployment/

---

**Criado em:** 19/10/2025  
**Status:** 📋 Guia Pronto - Siga os passos acima!  
**Tempo estimado:** 10-15 minutos
