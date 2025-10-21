# 🔐 Configuração Google Service Account para Veo 3.1

## 📋 Guia Completo: Service Account + Vertex AI

### ✅ O que você já tem:
- ✅ Vertex AI API habilitada
- ✅ Projeto: `talking-photo-gen-441622`
- ✅ Código pronto para usar Service Account

---

## 🎯 Passo 1: Criar Service Account

### 1.1 Acesse o Console do Google Cloud
```
https://console.cloud.google.com/iam-admin/serviceaccounts?project=talking-photo-gen-441622
```

### 1.2 Clique em "CREATE SERVICE ACCOUNT" (no topo)

### 1.3 Preencha os dados:
- **Service account name:** `veo-video-generator`
- **Service account ID:** `veo-video-generator` (auto-gerado)
- **Description:** `Service account para gerar vídeos com Veo 3.1`

Clique em **CREATE AND CONTINUE**

---

## 🎯 Passo 2: Adicionar Permissões

### 2.1 Na seção "Grant this service account access to project"

Adicione estas 2 roles:

1. **Vertex AI User**
   - Digite: `Vertex AI User`
   - Selecione: `Vertex AI User`

2. **Service Account User** (opcional, mas recomendado)
   - Digite: `Service Account User`
   - Selecione: `Service Account User`

Clique em **CONTINUE** → **DONE**

---

## 🎯 Passo 3: Criar e Baixar Chave JSON

### 3.1 Na lista de Service Accounts, clique no service account criado:
`veo-video-generator@talking-photo-gen-441622.iam.gserviceaccount.com`

### 3.2 Vá na aba **KEYS** (no topo)

### 3.3 Clique em **ADD KEY** → **Create new key**

### 3.4 Selecione **JSON** → **CREATE**

### 3.5 O arquivo será baixado automaticamente:
```
talking-photo-gen-441622-xxxxxxxxxxxxx.json
```

⚠️ **IMPORTANTE:** Guarde este arquivo em segurança!

---

## 🎯 Passo 4: Configurar no Projeto

### 4.1 Mova o arquivo JSON para o diretório do projeto:

**Windows:**
```powershell
Move-Item "$env:USERPROFILE\Downloads\talking-photo-gen-441622-*.json" "C:\appsMau\FabricaAlegria\talking-photo-generator\backend\google-credentials.json"
```

**Ou manualmente:**
1. Copie o arquivo baixado
2. Cole em: `C:\appsMau\FabricaAlegria\talking-photo-generator\backend\`
3. Renomeie para: `google-credentials.json`

### 4.2 Adicione ao `.env` do backend:

Abra `backend/.env` e adicione/atualize:

```bash
# Google Vertex AI - Service Account (Veo 3.1 Direct)
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
GOOGLE_CLOUD_PROJECT=talking-photo-gen-441622
GOOGLE_CLOUD_REGION=us-central1
```

### 4.3 Adicione ao `.gitignore`:

⚠️ **CRÍTICO:** Nunca commite o arquivo JSON!

Execute:
```powershell
echo "backend/google-credentials.json" >> .gitignore
echo "google-credentials.json" >> .gitignore
```

---

## 🧪 Passo 5: Testar Configuração

### 5.1 Execute o teste:
```bash
python test_veo_vertex_sdk.py
```

### 5.2 Resultado esperado:
```
✅ Service Account detectado
✅ Credenciais carregadas
✅ Request enviado para Vertex AI
✅ Vídeo gerado com sucesso!
```

---

## 💰 Economia Confirmada

### Comparação de Custos (8 segundos com áudio):

| Provider | Custo/Vídeo | Custo/100 vídeos | Custo Anual |
|----------|-------------|------------------|-------------|
| **FAL.AI Veo 3.1** | $3.20 | $320 | $3,840 |
| **FAL.AI Sora 2** | $2.40 | $240 | $2,880 |
| **Google Veo Direct** | $1.20 | $120 | **$1,440** |
| **Economia** | **-$2.00** | **-$200** | **-$2,400** |

### 📊 Economia: 62% vs FAL.AI Veo 3.1

---

## 🔧 Atualizar Código (Já feito!)

O código já está pronto para detectar Service Account automaticamente:

```python
# backend/veo31_simple.py
class Veo31DirectSimple:
    def __init__(self, api_key=None, project_id=None, location="us-central1"):
        # Tenta API Key primeiro
        self.api_key = api_key or os.getenv("GOOGLE_VERTEX_API_KEY")
        
        # Se não tiver API Key, usa Service Account
        if not self.api_key:
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path:
                logger.info("✅ Using Service Account authentication")
                # Carrega credenciais automaticamente
```

---

## ✅ Checklist Final

- [ ] Service Account criado
- [ ] Permissões Vertex AI User adicionadas
- [ ] Arquivo JSON baixado
- [ ] Arquivo movido para `backend/google-credentials.json`
- [ ] `.env` atualizado com `GOOGLE_APPLICATION_CREDENTIALS`
- [ ] `.gitignore` atualizado
- [ ] Teste executado com sucesso

---

## 🚀 Próximos Passos

Após configurar, você poderá:

1. ✅ Gerar vídeos 62% mais barato
2. ✅ Usar no backend automaticamente
3. ✅ Deploy no Render sem expor credenciais
4. ✅ Escalar sem preocupações de custo

---

## 🆘 Troubleshooting

### Erro: "Could not load credentials"
```bash
# Verifique o caminho no .env:
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json

# Confirme que o arquivo existe:
ls backend/google-credentials.json
```

### Erro: 403 Permission Denied
```bash
# Verifique as roles do Service Account:
# Deve ter: "Vertex AI User"
```

### Erro: 404 Model not found
```bash
# Veo 3.1 pode não estar disponível em todas regiões
# Tente: us-central1, europe-west4
```

---

## 📞 Suporte

Se tiver algum problema, me avise com:
1. Mensagem de erro completa
2. Output do teste
3. Conteúdo do `.env` (sem expor chaves)

---

**🎉 Boa sorte! Em breve você estará economizando $2.400/ano!** 💰
