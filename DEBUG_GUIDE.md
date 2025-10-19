# 🔧 GUIA DE DEBUG - Botões Não Funcionam

## ❌ PROBLEMA REPORTADO

**Sintomas:**
- ✅ Frontend carrega visualmente
- ❌ Botões não respondem ("Gerar Imagens", "Galeria", "Admin")
- ❌ Upload de imagem não funciona
- ❌ Nenhuma interação funciona

---

## 🔍 DIAGNÓSTICO

### Possíveis Causas:

1. **React Router não inicializado**
   - Rotas não carregando corretamente
   - JavaScript com erro antes do Router iniciar

2. **Variável de ambiente vazia**
   - `REACT_APP_BACKEND_URL` pode não estar sendo lida
   - Build não incluiu a variável

3. **Erro de JavaScript silencioso**
   - Erro bloqueando execução
   - Event listeners não sendo registrados

4. **Problema de build/cache**
   - Build incompleto
   - Cache antigo sendo servido

---

## 🛠️ PÁGINA DE DEBUG

Criamos uma página de teste independente do React:

### 📍 **URL: https://foto-video-fantasia.onrender.com/debug.html**

Esta página testa:
- ✅ Conectividade com backend
- ✅ API de vozes
- ✅ Upload de imagem
- ✅ Galeria
- ✅ Informações do ambiente

**Como usar:**
1. Abra a URL acima
2. A página testa automaticamente o backend
3. Clique nos botões para testar cada função
4. Veja os resultados em tempo real

---

## 🔧 SOLUÇÕES

### Solução 1: Forçar Rebuild Completo

```bash
# Via API
python -c "
import requests
API_KEY = 'rnd_kbYq0mcIml5b2eOSsGUmfSDmlT8S'
SERVICE_ID = 'srv-d3qd08ali9vc73c8a5f0'
headers = {'Authorization': 'Bearer ' + API_KEY, 'Content-Type': 'application/json'}
response = requests.post(
    'https://api.render.com/v1/services/' + SERVICE_ID + '/deploys',
    headers=headers,
    json={'clearCache': 'clear'}
)
print('Deploy iniciado:', response.json().get('id'))
"
```

### Solução 2: Verificar Console do Navegador

**No navegador:**
1. Pressione `F12` (DevTools)
2. Aba "Console"
3. Procure por erros em vermelho
4. Copie e envie os erros

**Erros comuns:**
- `undefined is not a function` → Biblioteca faltando
- `Cannot read property 'X' of undefined` → Variável vazia
- `Failed to fetch` → Backend offline/CORS

### Solução 3: Verificar Network Tab

**No navegador:**
1. `F12` → Aba "Network"
2. Recarregue a página (`Ctrl+F5`)
3. Veja se arquivos JS carregam (status 200)
4. Veja se há erros 404

**O que procurar:**
- `main.XXXXX.js` deve retornar **200 OK**
- Arquivos CSS devem carregar
- Requisições para `/api/*` podem falhar inicialmente (backend hibernando)

### Solução 4: Limpar Cache do Navegador

**Ctrl+Shift+Delete** → Limpar:
- ☑️ Imagens e arquivos em cache
- ☑️ Cookies e dados de sites

Ou use **Ctrl+F5** para hard reload.

### Solução 5: Teste em Modo Anônimo

Abra em **janela anônima** (Ctrl+Shift+N):
- Remove extensões do navegador
- Remove cache
- Testa estado "limpo"

---

## 📋 CHECKLIST DE VERIFICAÇÃO

Execute na ordem:

### 1. ✅ Backend Está Online?
```bash
curl https://gerador-fantasia.onrender.com/health
```
Esperado: `{"status":"healthy",...}`

Se retornar 502:
```bash
python wake_backend.py
```

### 2. ✅ Página de Debug Funciona?
Abra: https://foto-video-fantasia.onrender.com/debug.html

Se a debug funciona mas a página principal não:
→ Problema é no código React, não no backend

### 3. ✅ Console tem Erros?
`F12` → Console

Se houver erros:
→ Copie e analise

### 4. ✅ Arquivos JS Carregam?
`F12` → Network → Recarregar

Se `main.js` retorna 404:
→ Problema no build/deploy

### 5. ✅ Variável de Ambiente Está Setada?
No console do navegador, digite:
```javascript
console.log(window.location.origin)
// Deve mostrar: https://foto-video-fantasia.onrender.com
```

---

## 🔍 TESTES DETALHADOS

### Teste A: React Router

Tente acessar diretamente:
- https://foto-video-fantasia.onrender.com/
- https://foto-video-fantasia.onrender.com/gallery
- https://foto-video-fantasia.onrender.com/admin

Se retornar 404:
→ Arquivo `_redirects` não está funcionando

**Solução:**
Verificar se `frontend/public/_redirects` existe com:
```
/*    /index.html   200
```

### Teste B: JavaScript Carrega

No console:
```javascript
document.querySelectorAll('script').length
```

Deve retornar > 0 (pelo menos 1 script)

Se retornar 0:
→ Scripts não estão sendo injetados

### Teste C: React Inicializa

No console:
```javascript
document.getElementById('root')
```

Deve retornar um elemento `<div id="root">...</div>`

Se retornar `null`:
→ React não está montando

---

## 🚀 AÇÕES IMEDIATAS

1. **Abra a página de debug:**
   https://foto-video-fantasia.onrender.com/debug.html

2. **Teste cada função:**
   - Backend (deve estar verde ✅)
   - Vozes (deve listar 26 vozes)
   - Upload (selecione imagem e teste)
   - Galeria (pode estar vazia, mas não deve dar erro)

3. **Copie os resultados**

4. **Se debug funciona:**
   → Problema é no código React (não no backend/API)
   → Precisamos ver Console do navegador na página principal

5. **Se debug NÃO funciona:**
   → Problema é no backend
   → Execute `python wake_backend.py`

---

## 📞 PRÓXIMOS PASSOS

Com base nos resultados da página de debug, podemos:

### Se Tudo Verde na Debug:
→ Problema é específico do React
→ Preciso ver console do navegador (`F12`)
→ Pode ser erro de build

### Se Algum Vermelho na Debug:
→ Problema é no backend/API
→ Verificar logs do Render
→ Pode ser API Keys faltando

---

## 🎯 INFORMAÇÕES PARA DEBUG

**Por favor, forneça:**

1. **Resultado da página debug.html**
   - Todos os 4 testes (backend, vozes, upload, galeria)

2. **Console do navegador (F12)**
   - Erros em vermelho
   - Warnings em amarelo

3. **Network tab (F12)**
   - Status dos arquivos .js
   - Requisições que falharam

4. **URL que você está acessando**
   - Confirmar se é: https://foto-video-fantasia.onrender.com

---

**Próxima ação:** Acesse https://foto-video-fantasia.onrender.com/debug.html e me envie os resultados!
