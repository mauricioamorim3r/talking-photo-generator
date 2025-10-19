# 🔧 Configuração MCP Server do Render

Este guia mostra como configurar o MCP (Model Context Protocol) Server do Render para fazer deploys diretamente pelo VS Code/Copilot.

---

## 📋 Pré-requisitos

1. ✅ Conta no Render.com
2. ✅ API Key do Render
3. ✅ VS Code com Copilot/Claude instalado

---

## 🔑 PASSO 1: Obter API Key do Render

### 1.1 Acessar Dashboard do Render
```
https://dashboard.render.com/
```

### 1.2 Ir para Account Settings
1. Clique no seu avatar (canto superior direito)
2. Clique em **"Account Settings"**

### 1.3 Gerar API Key
1. No menu lateral, clique em **"API Keys"**
2. Clique em **"Create API Key"**
3. Dê um nome: `MCP Server - Copilot`
4. Clique em **"Create API Key"**
5. **⚠️ COPIE A KEY AGORA** (só aparece uma vez!)
6. Salve em local seguro (exemplo: `rnd_xxxxxxxxxxxxxxxxxxxx`)

---

## 🛠️ PASSO 2: Entender a Arquitetura

O Render fornece um **MCP Server hospedado** em:

```
https://mcp.render.com/mcp
```

**✅ VANTAGENS:**
- ❌ Não precisa instalar nada localmente
- ✅ Sempre atualizado automaticamente
- ✅ Funciona direto no VS Code/Cursor/Claude
- ✅ Apenas precisa da API Key

**📦 Alternativa Local (Opcional - não recomendado):**
Se realmente quiser rodar localmente, pode usar Docker:
```bash
docker run -i --rm -e RENDER_API_KEY=sua_key ghcr.io/render-oss/render-mcp-server
```

Mas vamos usar o **servidor hospedado** (mais fácil!).

---

## ⚙️ PASSO 3: Configurar MCP no VS Code

### 3.1 Localizar arquivo de configuração

O arquivo de configuração do MCP depende da sua ferramenta:

**Para Cursor:**
```
~/.cursor/mcp.json
```
Ou no Windows:
```
C:\Users\SEU_USUARIO\.cursor\mcp.json
```

**Para GitHub Copilot:**
```
%APPDATA%\Code\User\globalStorage\github.copilot\mcpServers.json
```

**Para Claude Desktop:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 3.2 Criar/Editar o arquivo de configuração

**⚠️ IMPORTANTE:** Use o **servidor hospedado** do Render (não local)!

Adicione esta configuração:

```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer rnd_COLOQUE_SUA_API_KEY_AQUI"
      }
    }
  }
}
```

**⚠️ SUBSTITUA** `rnd_COLOQUE_SUA_API_KEY_AQUI` pela sua API Key real!

### 3.3 Exemplo completo (Cursor)

Arquivo: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer rnd_abc123xyz456def789ghi012jkl345"
      }
    }
  }
}
```

### 3.4 Exemplo para GitHub Copilot

Arquivo: `%APPDATA%\Code\User\globalStorage\github.copilot\mcpServers.json`

```json
{
  "servers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer rnd_COLOQUE_SUA_API_KEY_AQUI"
      }
    }
  }
}
```

**Nota:** GitHub Copilot usa `"servers"` em vez de `"mcpServers"`.

---

## 🔄 PASSO 4: Reiniciar VS Code

1. Feche completamente o VS Code
2. Abra novamente
3. O MCP Server do Render estará disponível!

---

## 🧪 PASSO 5: Testar a Conexão

### 5.1 Via Copilot Chat

Abra o Copilot Chat e pergunte:

```
Liste todos os serviços no meu Render
```

Ou:

```
Mostre o status do serviço talking-photo-backend no Render
```

### 5.2 Comandos disponíveis

O MCP Server do Render suporta:

- **Listar serviços:** `list-services`
- **Detalhes do serviço:** `get-service <service-id>`
- **Criar serviço:** `create-service`
- **Atualizar serviço:** `update-service`
- **Fazer deploy:** `deploy-service`
- **Ver logs:** `get-logs <service-id>`
- **Listar deploys:** `list-deploys <service-id>`

---

## 🚀 PASSO 6: Fazer Deploy via MCP

### 6.1 Criar o Frontend via MCP

Agora você pode pedir ao Copilot:

```
Crie um Static Site no Render com estas configurações:
- Nome: talking-photo-frontend
- Repositório: mauricioamorim3r/talking-photo-generator
- Branch: main
- Root Directory: frontend
- Build Command: npm install --legacy-peer-deps && npm run build
- Publish Directory: build
- Environment Variable: REACT_APP_API_URL=https://gerador-fantasia.onrender.com
```

### 6.2 Ver status do deploy

```
Mostre o status do último deploy do talking-photo-frontend
```

### 6.3 Ver logs

```
Mostre os logs do talking-photo-frontend
```

---

## 📝 Exemplo de Uso Completo

Depois de configurado, você pode fazer tudo via comandos:

```
Eu: "Liste todos os meus serviços no Render"
Copilot: [lista de serviços]

Eu: "Faça um redeploy do talking-photo-backend"
Copilot: [inicia o redeploy]

Eu: "Mostre o status do deploy"
Copilot: [mostra status em tempo real]

Eu: "Se houver erro, mostre os logs"
Copilot: [mostra logs completos]
```

---

## 🔐 Segurança da API Key

### ⚠️ IMPORTANTE: Nunca commite a API Key!

**❌ NÃO FAÇA:**
```bash
git add cline_mcp_settings.json
git commit -m "Add MCP config"
```

**✅ FAÇA:**

Adicione ao `.gitignore`:
```gitignore
# MCP Settings (contém API keys)
**/cline_mcp_settings.json
**/mcpServers.json
```

### 🔒 Alternativa Segura: Usar Variável de Ambiente

Em vez de colocar a key no arquivo, use variável de ambiente:

```json
{
  "mcpServers": {
    "render": {
      "command": "npx",
      "args": ["-y", "@render-oss/mcp-server-render"],
      "env": {
        "RENDER_API_KEY": "${env:RENDER_API_KEY}"
      }
    }
  }
}
```

Então configure a variável no sistema:

```powershell
# Temporária (só esta sessão)
$env:RENDER_API_KEY = "rnd_suachaveaqui"

# Permanente (usuário)
[System.Environment]::SetEnvironmentVariable('RENDER_API_KEY', 'rnd_suachaveaqui', 'User')
```

---

## 🐛 Troubleshooting

### Problema 1: MCP Server não aparece

**Solução:**
1. Verifique se o arquivo de configuração está no local correto
2. Verifique se o JSON está válido (use um validador JSON online)
3. Reinicie o VS Code completamente

### Problema 2: Erro de autenticação

**Solução:**
1. Verifique se a API Key está correta
2. Verifique se não há espaços extras na key
3. Gere uma nova API Key no Render

### Problema 3: Comando não encontrado

**Solução:**
```powershell
# Instalar globalmente
npm install -g @render-oss/mcp-server-render

# Ou usar npx sempre
npx -y @render-oss/mcp-server-render
```

---

## 📚 Documentação Oficial

- **Render MCP Server:** https://render.com/docs/mcp-server
- **Render API Docs:** https://api-docs.render.com/
- **MCP Protocol:** https://modelcontextprotocol.io/

---

## ✅ Checklist de Configuração

- [ ] API Key do Render obtida
- [ ] MCP Server instalado (`npm install -g @render-oss/mcp-server-render`)
- [ ] Arquivo de configuração criado
- [ ] API Key adicionada ao arquivo de configuração
- [ ] VS Code reiniciado
- [ ] Testado comando "Liste serviços no Render"
- [ ] Deploy funcionando via MCP

---

## 🎯 Benefícios do MCP

✅ **Deploy direto pelo chat** - sem sair do VS Code
✅ **Ver logs em tempo real** - debugging mais rápido
✅ **Gerenciar múltiplos serviços** - tudo em um lugar
✅ **Automação completa** - scripts e workflows
✅ **Integração com Copilot** - comandos em linguagem natural

---

## 🆘 Precisa de Ajuda?

1. **Verifique os logs:**
   - VS Code → Help → Toggle Developer Tools
   - Console → procure por erros do MCP

2. **Teste manualmente:**
   ```powershell
   npx @render-oss/mcp-server-render
   ```

3. **Entre em contato:**
   - Discord do Render
   - GitHub Issues: https://github.com/render-oss/mcp-server-render

---

**Criado em:** 19/10/2025  
**Documentação:** render.com/docs/mcp-server  
**Versão MCP:** 1.0.0+
