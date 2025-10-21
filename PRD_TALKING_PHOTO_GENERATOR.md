# PRD - Talking Photo Generator
## Product Requirements Document

**Versão:** 2.0  
**Data:** 21 de Outubro de 2025  
**Status:** Produção  
**Autor:** Maurício Amorim

---

## 📋 Sumário Executivo

### Visão Geral
O **Talking Photo Generator** é uma aplicação web que transforma imagens estáticas em vídeos animados com áudio sincronizado, utilizando Inteligência Artificial de última geração. A aplicação permite que usuários criem vídeos profissionais a partir de fotos, com narração realista e movimentos cinematográficos.

### Objetivo
Democratizar a criação de vídeos animados através de uma interface intuitiva, oferecendo acesso a tecnologias de ponta em IA generativa com custos otimizados.

### Proposta de Valor
- ✅ **Economia de 62%** - Custos reduzidos usando Google Veo 3.1 via Gemini API
- ✅ **Qualidade Premium** - Modelos de IA de última geração (Veo 3.1, Gemini 2.0, ElevenLabs)
- ✅ **Simplicidade** - Interface drag-and-drop com 3 etapas simples
- ✅ **Flexibilidade** - Múltiplos modelos de vídeo e vozes de áudio
- ✅ **Transparência** - Estimativa de custos em tempo real antes da geração

---

## 🎯 Público-Alvo

### Usuários Primários
1. **Criadores de Conteúdo** - YouTubers, TikTokers, Instagramers
2. **Profissionais de Marketing** - Agências, freelancers de publicidade
3. **Educadores** - Professores criando materiais audiovisuais
4. **Empresários** - Apresentações comerciais, pitch decks animados

### Personas
**Persona 1: Maria - Criadora de Conteúdo**
- Idade: 28 anos
- Objetivo: Criar vídeos virais para redes sociais
- Dor: Edição de vídeo tradicional é cara e demorada
- Necessidade: Gerar vídeos rapidamente com qualidade profissional

**Persona 2: Carlos - Empresário**
- Idade: 42 anos
- Objetivo: Criar apresentações impactantes para investidores
- Dor: Contratar estúdio de animação é muito caro
- Necessidade: Ferramenta acessível para criar vídeos corporativos

---

## 🏗️ Arquitetura do Sistema

### Stack Tecnológico

#### **Backend**
- **Framework:** FastAPI (Python 3.10+)
- **Banco de Dados:** SQLite (aiosqlite) - Sem necessidade de servidor externo
- **Servidor:** Uvicorn com hot-reload
- **Autenticação:** Variáveis de ambiente (.env)

#### **Frontend**
- **Framework:** React 19
- **Build Tool:** Create React App + Craco
- **Roteamento:** React Router DOM v7
- **Estilização:** Tailwind CSS 3.4
- **Componentes UI:** Radix UI (acessibilidade nativa)
- **Animações:** Framer Motion
- **HTTP Client:** Axios
- **Notificações:** Sonner (toast notifications)

#### **Integrações de IA**
1. **Google Gemini 2.0 Flash**
   - Análise de imagens com IA
   - Geração de prompts cinematográficos
   - Geração de imagens (Nano Banana)
   - **Custo:** $0.039 por imagem

2. **Google Veo 3.1 (Gemini API)** ⭐ **PRINCIPAL**
   - Geração de vídeos texto-para-vídeo
   - Geração de vídeos imagem-para-vídeo
   - Resolução: 720p / 1080p
   - Duração: 4s, 6s ou 8s
   - Áudio nativo incluído
   - **Custo:** $0.076/segundo (62% mais barato que alternativas)
   - **SDK:** google-genai v1.45.0
   - **Modelo:** veo-3.1-generate-preview

3. **ElevenLabs**
   - Text-to-Speech de alta qualidade
   - Múltiplas vozes (crianças, adultos, idosos)
   - Controles de estabilidade, similaridade e velocidade
   - **Custo:** ~$0.30 por minuto de áudio

#### **Infraestrutura**
- **Desenvolvimento:** localhost (Backend: 8000, Frontend: 3000)
- **Produção:** Render.com (backend) + Vercel/Netlify (frontend)
- **Armazenamento:** Sistema de arquivos local + URLs públicas

---

## 📐 Estrutura de Dados

### **Modelos de Dados (Pydantic)**

#### 1. ImageAnalysis
```python
{
  "id": "uuid-v4",
  "image_url": "https://...",
  "cloudinary_id": "optional_id",
  "analysis": "Descrição gerada por IA da imagem",
  "suggested_model": "veo3",
  "timestamp": "ISO-8601"
}
```

#### 2. AudioGeneration
```python
{
  "id": "uuid-v4",
  "audio_url": "https://...",
  "source": "generated | uploaded",
  "duration": 5.2,
  "text": "Texto narrado",
  "voice_id": "cgSgspJ2msm6clMCkdW9",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "speed": 1.0,
    "style": 0.0
  },
  "cost": 0.30,
  "timestamp": "ISO-8601"
}
```

#### 3. VideoGeneration
```python
{
  "id": "uuid-v4",
  "image_id": "ref-to-image",
  "audio_id": "ref-to-audio (optional)",
  "model": "veo3 | sora2 | wav2lip | open-sora | wav2lip-free | google_veo3",
  "provider": "google_gemini",  // PADRÃO
  "mode": "premium | economico",
  "prompt": "Descrição do vídeo desejado",
  "duration": 8.0,
  "cost": 0.61,
  "estimated_cost": 0.61,
  "status": "pending | processing | completed | failed",
  "result_url": "https://...",
  "error": null,
  "timestamp": "ISO-8601"
}
```

#### 4. GeneratedImage
```python
{
  "id": "uuid-v4",
  "prompt": "Prompt usado para gerar a imagem",
  "image_url": "https://...",
  "cost": 0.039,
  "timestamp": "ISO-8601"
}
```

#### 5. TokenUsage
```python
{
  "id": "uuid-v4",
  "service": "gemini | elevenlabs | google_veo",
  "operation": "analyze | generate_audio | generate_video",
  "cost": 0.61,
  "details": {
    "duration": 8,
    "provider": "google_gemini",
    "model": "veo3"
  },
  "timestamp": "ISO-8601"
}
```

#### 6. APIBalance
```python
{
  "id": "uuid-v4",
  "service": "gemini | elevenlabs | google_veo",
  "initial_balance": 100.00,
  "current_balance": 87.45,
  "last_updated": "ISO-8601"
}
```

### **Banco de Dados SQLite**

**Arquivo:** `backend/database/video_gen.db`

**Tabelas:**
1. `image_analyses` - Análises de imagens
2. `audio_generations` - Áudios gerados/enviados
3. `video_generations` - Vídeos gerados
4. `generated_images` - Imagens geradas por IA
5. `token_usage` - Histórico de uso de tokens/custos
6. `api_balances` - Saldos das APIs

**Características:**
- ✅ Sem servidor externo necessário
- ✅ Backup simples (copiar arquivo .db)
- ✅ Async operations (aiosqlite)
- ✅ Migrations automáticas no startup
- ✅ ACID compliance

---

## 🎨 Funcionalidades Detalhadas

### **1. Upload e Captura de Imagem**

#### Requisitos Funcionais
- [ ] RF-001: Upload de imagem via drag-and-drop
- [ ] RF-002: Upload de imagem via seleção de arquivo
- [ ] RF-003: Captura de foto via webcam
- [ ] RF-004: Pré-visualização da imagem antes do envio
- [ ] RF-005: Validação de formato (JPG, PNG, WEBP)
- [ ] RF-006: Validação de tamanho (máx 10MB)

#### Fluxo do Usuário
1. Usuário acessa a página inicial (Step 1)
2. Usuário escolhe entre:
   - **Upload:** Arrasta arquivo ou clica para selecionar
   - **Webcam:** Clica no botão "Usar Câmera"
3. Sistema valida a imagem
4. Sistema exibe preview da imagem
5. Usuário clica em "Analisar Imagem"

#### Regras de Negócio
- RN-001: Formatos aceitos: JPG, PNG, WEBP
- RN-002: Tamanho máximo: 10MB
- RN-003: Resolução mínima: 256x256px
- RN-004: Resolução máxima: 4096x4096px

---

### **2. Análise de Imagem com IA**

#### Requisitos Funcionais
- [ ] RF-007: Análise automática da imagem com Gemini 2.0
- [ ] RF-008: Geração de descrição detalhada
- [ ] RF-009: Sugestão de modelo de vídeo ideal
- [ ] RF-010: Geração de prompts cinematográficos
- [ ] RF-011: Identificação de elementos da cena
- [ ] RF-012: Sugestões de movimentos de câmera

#### Análise Fornecida
```
Exemplo de Output:
- Descrição: "Mulher sorrindo em ambiente externo, luz natural"
- Elementos: ["pessoa", "rosto", "fundo desfocado", "luz natural"]
- Sugestão de modelo: "veo3"
- Prompts sugeridos:
  * "A woman smiling and waving at the camera"
  * "Close-up of a happy person with natural lighting"
  * "Portrait shot with cinematic depth of field"
```

#### Tecnologia
- **Modelo:** Gemini 2.0 Flash
- **API:** Google Generative AI
- **Custo:** Incluído no plano (sem custo adicional)
- **Tempo:** ~2-3 segundos

---

### **3. Geração de Áudio (Text-to-Speech)**

#### Requisitos Funcionais
- [ ] RF-013: Conversão de texto em áudio com ElevenLabs
- [ ] RF-014: Seleção de voz (20+ vozes disponíveis)
- [ ] RF-015: Controle de velocidade (0.5x a 2.0x)
- [ ] RF-016: Controle de estabilidade (0.0 a 1.0)
- [ ] RF-017: Controle de similaridade (0.0 a 1.0)
- [ ] RF-018: Preview do áudio antes de gerar vídeo
- [ ] RF-019: Upload de áudio customizado (alternativa)

#### Vozes Disponíveis
**Categoria: Crianças**
- Rachel (criança feminina)
- Drew (criança masculina)

**Categoria: Adultos**
- Lily (feminino)
- Adam (masculino)
- Charlie (masculino jovem)
- Domi (feminino jovem)

**Categoria: Idosos**
- Dorothy (feminino)
- Bill (masculino)

#### Configurações
```javascript
{
  "voice_id": "cgSgspJ2msm6clMCkdW9",  // ID da voz
  "stability": 0.5,                    // 0=variável, 1=estável
  "similarity_boost": 0.75,            // Fidelidade ao original
  "speed": 1.0,                        // 0.5x a 2.0x
  "style": 0.0                         // Exagero emocional
}
```

#### Custo
- **Modelo:** Multilingual v2
- **Preço:** ~$0.30 por minuto
- **Exemplo:** 30 segundos = $0.15

---

### **4. Geração de Vídeo**

#### Requisitos Funcionais - Provider Principal
- [ ] RF-020: Geração de vídeo com Google Veo 3.1 (Gemini API)
- [ ] RF-021: Modo texto-para-vídeo (sem imagem)
- [ ] RF-022: Modo imagem-para-vídeo (com imagem de entrada)
- [ ] RF-023: Seleção de duração (4s, 6s, 8s)
- [ ] RF-024: Seleção de resolução (720p, 1080p)
- [ ] RF-025: Seleção de aspect ratio (16:9, 9:16)
- [ ] RF-026: Áudio nativo incluído automaticamente
- [ ] RF-027: Polling automático até conclusão
- [ ] RF-028: Exibição de progresso em tempo real

#### Modelos de Vídeo Disponíveis

##### ⭐ **Google Veo 3.1 (Gemini API)** - RECOMENDADO
**Características:**
- Provider: `google_gemini`
- Modelo: `veo-3.1-generate-preview`
- Resolução: 720p / 1080p
- Duração: 4s, 6s, 8s
- Aspect Ratio: 16:9, 9:16
- Áudio: ✅ Incluído nativamente
- Qualidade: ⭐⭐⭐⭐⭐ (5/5)
- Custo: **$0.076/segundo** (62% economia vs FAL)

**Exemplo de Custo:**
- 4s: $0.30
- 6s: $0.46
- 8s: $0.61

**Latência:**
- Text-to-video: 11s - 6min
- Image-to-video: 11s - 6min
- Média: ~60-90 segundos

**SDK:** google-genai v1.45.0  
**Documentação:** https://ai.google.dev/gemini-api/docs/video

##### 🔄 **Modelos Alternativos** (Descontinuados)
- **Veo 3 (FAL.AI):** $0.20/s (sem áudio) ou $0.40/s (com áudio)
- **Sora 2 (FAL.AI):** $0.20/s
- **Wav2lip (FAL.AI):** $0.15/s

**Nota:** FAL.AI mantido apenas como fallback histórico. Não recomendado para novos projetos.

#### Configuração de Geração
```javascript
{
  "image_url": "https://...",           // URL da imagem
  "model": "google_veo3",               // Sempre google_veo3
  "provider": "google_gemini",          // PADRÃO (economia 62%)
  "mode": "premium",                    // Sempre premium
  "prompt": "A woman smiling...",       // Descrição do vídeo
  "duration": 8,                        // 4, 6 ou 8 segundos
  "resolution": "1080p",                // 720p ou 1080p
  "aspect_ratio": "16:9"                // 16:9 ou 9:16
}
```

#### Fluxo de Geração
1. Usuário configura parâmetros do vídeo
2. Sistema estima custo em tempo real
3. Usuário confirma geração
4. Sistema envia request para Gemini API
5. Sistema faz polling a cada 5 segundos
6. Sistema exibe progresso (0-100%)
7. Vídeo finalizado é salvo no banco
8. Usuário recebe URL do vídeo

#### Tratamento de Erros
- Timeout: 10 minutos máximo
- Retry: 3 tentativas com backoff exponencial
- Fallback: Nenhum (Gemini é o único provider)
- Logging: Todos os erros são salvos no banco

---

### **5. Estimativa de Custos**

#### Requisitos Funcionais
- [ ] RF-029: Cálculo de custo estimado antes da geração
- [ ] RF-030: Exibição de custo em USD
- [ ] RF-031: Comparação com provider alternativo
- [ ] RF-032: Atualização em tempo real ao mudar parâmetros
- [ ] RF-033: Histórico de custos por operação

#### Fórmula de Cálculo

**Google Veo 3.1 (Gemini API):**
```
Custo = duração (segundos) × $0.076
```

**Exemplos:**
- 4 segundos: $0.30
- 6 segundos: $0.46
- 8 segundos: $0.61

**ElevenLabs:**
```
Custo = duração (minutos) × $0.30
```

**Gemini Image Generation:**
```
Custo = $0.039 por imagem
```

#### Interface de Exibição
```
💰 Custo Estimado: $0.61
⏱️ Duração: 8 segundos
📊 Economia: 62% vs FAL.AI ($3.20)
```

---

### **6. Galeria de Projetos**

#### Requisitos Funcionais
- [ ] RF-034: Listagem de todos os projetos criados
- [ ] RF-035: Filtro por tipo (vídeo, áudio, imagem)
- [ ] RF-036: Ordenação por data
- [ ] RF-037: Preview de thumbnails
- [ ] RF-038: Download de arquivos
- [ ] RF-039: Exclusão de projetos
- [ ] RF-040: Visualização de detalhes (custo, data, modelo)

#### Layout
- Grid responsivo (3 colunas desktop, 2 tablet, 1 mobile)
- Cards com:
  - Thumbnail/preview
  - Título/prompt
  - Data de criação
  - Custo
  - Modelo usado
  - Status
  - Ações (Download, Delete, View)

---

### **7. Painel Administrativo**

#### Requisitos Funcionais
- [ ] RF-041: Login com senha
- [ ] RF-042: Visualização de saldos de API
- [ ] RF-043: Histórico de uso por serviço
- [ ] RF-044: Gráficos de consumo
- [ ] RF-045: Estatísticas gerais
- [ ] RF-046: Exportação de relatórios

#### Métricas Exibidas
1. **Saldos de API**
   - Google Gemini: $XX.XX
   - ElevenLabs: $XX.XX
   - Total gasto: $XX.XX

2. **Estatísticas de Uso**
   - Vídeos gerados: XX
   - Áudios gerados: XX
   - Imagens analisadas: XX
   - Custo médio por vídeo: $XX.XX

3. **Gráficos**
   - Gastos por dia (últimos 30 dias)
   - Gastos por serviço (pizza chart)
   - Modelos mais usados (bar chart)

---

## 🔐 Segurança e Autenticação

### Variáveis de Ambiente (.env)

```bash
# Google Gemini API (Análise + Geração de Imagens + Veo 3.1)
GEMINI_KEY=AIzaSyC_bfQ_bFZmb1YHWviCwHicuXVxaCgMje0

# ElevenLabs (Text-to-Speech)
ELEVENLABS_KEY=sk_xxx

# Backend URL
BACKEND_URL=http://localhost:8000

# Admin Password
ADMIN_PASSWORD=admin123

# Database Path (opcional)
DB_PATH=./database/video_gen.db
```

### Segurança
- ✅ Variáveis de ambiente nunca expostas no frontend
- ✅ Admin protegido por senha
- ✅ CORS configurado para domínios específicos
- ✅ Rate limiting em endpoints críticos
- ✅ Validação de input em todos os endpoints
- ✅ Sanitização de prompts antes de enviar para IA

---

## 📊 API Endpoints

### **Análise de Imagem**

#### `POST /api/image/analyze`
Analisa uma imagem com Google Gemini 2.0.

**Request:**
```json
{
  "image_data": "base64_encoded_image"
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "id": "uuid",
    "image_url": "https://...",
    "analysis": "Descrição da imagem",
    "suggested_model": "veo3",
    "timestamp": "2025-10-21T..."
  }
}
```

---

### **Geração de Áudio**

#### `POST /api/audio/generate`
Gera áudio com ElevenLabs TTS.

**Request:**
```json
{
  "text": "Olá, este é um teste",
  "voice_id": "cgSgspJ2msm6clMCkdW9",
  "stability": 0.5,
  "similarity_boost": 0.75,
  "speed": 1.0,
  "style": 0.0
}
```

**Response:**
```json
{
  "success": true,
  "audio": {
    "id": "uuid",
    "audio_url": "https://...",
    "duration": 5.2,
    "cost": 0.15,
    "timestamp": "2025-10-21T..."
  }
}
```

#### `GET /api/audio/voices`
Lista todas as vozes disponíveis.

**Response:**
```json
{
  "success": true,
  "voices": [
    {
      "voice_id": "cgSgspJ2msm6clMCkdW9",
      "name": "Rachel",
      "category": "Criança",
      "gender": "Feminino",
      "age": "child"
    }
  ]
}
```

---

### **Geração de Vídeo**

#### `POST /api/video/generate`
Gera vídeo com Google Veo 3.1 (Gemini API).

**Request:**
```json
{
  "image_url": "https://...",
  "model": "google_veo3",
  "provider": "google_gemini",
  "mode": "premium",
  "prompt": "A woman smiling and waving",
  "duration": 8,
  "resolution": "1080p",
  "aspect_ratio": "16:9"
}
```

**Response:**
```json
{
  "success": true,
  "video": {
    "id": "uuid",
    "status": "processing",
    "estimated_cost": 0.61,
    "timestamp": "2025-10-21T..."
  }
}
```

#### `GET /api/video/status/{video_id}`
Consulta status de geração de vídeo.

**Response:**
```json
{
  "success": true,
  "video": {
    "id": "uuid",
    "status": "completed",
    "result_url": "https://...",
    "cost": 0.61,
    "duration": 8.0,
    "model": "google_veo3",
    "provider": "google_gemini"
  }
}
```

#### `POST /api/video/estimate-cost`
Estima custo de geração de vídeo.

**Request:**
```json
{
  "model": "google_veo3",
  "provider": "google_gemini",
  "mode": "premium",
  "duration": 8,
  "with_audio": false
}
```

**Response:**
```json
{
  "success": true,
  "estimated_cost": 0.61,
  "breakdown": {
    "video": 0.61,
    "audio": 0.00,
    "total": 0.61
  },
  "comparison": {
    "fal_cost": 3.20,
    "savings": 2.59,
    "savings_percentage": "62%"
  }
}
```

#### `GET /api/video/providers`
Lista providers disponíveis e recomendações.

**Response:**
```json
{
  "success": true,
  "default_provider": "google_veo31_gemini",
  "providers": [
    {
      "id": "google_veo31_gemini",
      "name": "Veo 3.1 (Gemini API) ⭐",
      "provider": "google_gemini",
      "available": true,
      "recommended": true,
      "cost_per_second": 0.076,
      "features": ["Áudio nativo", "720p/1080p", "16:9/9:16"],
      "savings_vs_fal": "62%"
    }
  ],
  "recommendation": {
    "provider": "google_veo31_gemini",
    "reason": "62% mais barato + áudio nativo incluído",
    "savings": "$2.59 por vídeo de 8s (vs FAL.AI)"
  }
}
```

---

### **Geração de Imagem**

#### `POST /api/image/generate`
Gera imagem com Gemini Nano Banana.

**Request:**
```json
{
  "prompt": "A beautiful sunset over mountains"
}
```

**Response:**
```json
{
  "success": true,
  "image": {
    "id": "uuid",
    "prompt": "A beautiful sunset...",
    "image_url": "https://...",
    "cost": 0.039,
    "timestamp": "2025-10-21T..."
  }
}
```

---

### **Galeria**

#### `GET /api/gallery/videos`
Lista todos os vídeos gerados.

**Response:**
```json
{
  "success": true,
  "videos": [
    {
      "id": "uuid",
      "prompt": "A woman smiling...",
      "result_url": "https://...",
      "thumbnail_url": "https://...",
      "model": "google_veo3",
      "provider": "google_gemini",
      "cost": 0.61,
      "duration": 8.0,
      "status": "completed",
      "timestamp": "2025-10-21T..."
    }
  ]
}
```

#### `GET /api/gallery/audios`
Lista todos os áudios gerados.

#### `GET /api/gallery/images`
Lista todas as imagens geradas.

---

### **Administração**

#### `POST /api/admin/verify-password`
Verifica senha de admin.

**Request:**
```json
{
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "valid": true
}
```

#### `GET /api/admin/token-usage`
Retorna estatísticas de uso.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_spent": 125.50,
    "by_service": {
      "google_gemini": 85.30,
      "elevenlabs": 40.20
    },
    "recent_operations": [...]
  }
}
```

#### `GET /api/admin/balances`
Retorna saldos das APIs.

**Response:**
```json
{
  "success": true,
  "balances": [
    {
      "service": "google_gemini",
      "initial_balance": 100.00,
      "current_balance": 87.45,
      "spent": 12.55
    },
    {
      "service": "elevenlabs",
      "initial_balance": 50.00,
      "current_balance": 38.20,
      "spent": 11.80
    }
  ]
}
```

---

## 🎨 Interface do Usuário

### **Estrutura de Navegação**

```
/ (HomePage)
├── Step 1: Upload/Captura de Imagem
│   ├── Upload via Drag & Drop
│   ├── Upload via File Selector
│   └── Captura via Webcam
│
├── Step 2: Análise e Configuração
│   ├── Análise Automática da Imagem
│   ├── Seleção de Modelo de Vídeo
│   ├── Edição de Prompt
│   ├── Geração/Upload de Áudio
│   └── Estimativa de Custo
│
├── Step 3: Geração de Vídeo
│   ├── Progresso em Tempo Real
│   ├── Preview do Vídeo
│   ├── Download
│   └── Compartilhamento
│
/gallery
├── Vídeos Gerados
├── Áudios Gerados
└── Imagens Geradas
│
/admin
├── Dashboard
├── Saldos de API
├── Histórico de Uso
└── Estatísticas
```

### **Componentes UI (Radix UI)**

- ✅ Button - Botões acessíveis
- ✅ Card - Containers de conteúdo
- ✅ Tabs - Navegação entre seções
- ✅ Select - Dropdowns (modelos, vozes)
- ✅ Slider - Controles (velocidade, estabilidade)
- ✅ Alert - Notificações inline
- ✅ Dialog - Modais (confirmações)
- ✅ Progress - Barras de progresso
- ✅ Textarea - Inputs de texto multi-linha
- ✅ Toast (Sonner) - Notificações temporárias

### **Paleta de Cores (Tailwind)**

```css
/* Cores Primárias */
--primary: 262.1 83.3% 57.8%        /* Roxo vibrante */
--primary-foreground: 210 20% 98%   /* Texto claro */

/* Cores de Fundo */
--background: 0 0% 100%              /* Branco */
--foreground: 222.2 84% 4.9%         /* Texto escuro */

/* Cores de Destaque */
--accent: 210 40% 96.1%              /* Cinza claro */
--accent-foreground: 222.2 47.4% 11.2% /* Texto escuro */

/* Cores de Borda */
--border: 214.3 31.8% 91.4%          /* Cinza suave */
--input: 214.3 31.8% 91.4%           /* Cinza suave */
--ring: 262.1 83.3% 57.8%            /* Roxo (focus) */

/* Estados */
--destructive: 0 84.2% 60.2%         /* Vermelho */
--success: 142.1 76.2% 36.3%         /* Verde */
--warning: 47.9 95.8% 53.1%          /* Amarelo */
```

### **Animações (Framer Motion)**

```javascript
// Fade In
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
/>

// Slide Up
<motion.div
  initial={{ y: 20, opacity: 0 }}
  animate={{ y: 0, opacity: 1 }}
  transition={{ duration: 0.5 }}
/>

// Scale
<motion.div
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
/>
```

---

## 🚀 Instalação e Deploy

### **Pré-requisitos**

- **Python:** 3.10 ou superior
- **Node.js:** 18.x ou superior
- **npm:** 10.x ou superior
- **Git:** Para versionamento

### **Instalação Local**

#### 1. Clone o Repositório
```bash
git clone https://github.com/mauricioamorim3r/talking-photo-generator.git
cd talking-photo-generator
```

#### 2. Configure Variáveis de Ambiente
Crie arquivo `.env` na pasta `backend/`:

```bash
# Google Gemini API
GEMINI_KEY=sua_chave_aqui

# ElevenLabs API
ELEVENLABS_KEY=sua_chave_aqui

# Backend URL
BACKEND_URL=http://localhost:8000

# Admin Password
ADMIN_PASSWORD=admin123
```

#### 3. Instale Dependências do Backend
```bash
cd backend
pip install -r requirements.txt
```

**Dependências Principais:**
- fastapi==0.110.1
- uvicorn[standard]
- aiosqlite==0.19.0
- google-genai==1.45.0
- google-generativeai==0.8.5
- elevenlabs==2.18.0
- python-multipart
- python-dotenv
- pillow
- pydantic

#### 4. Instale Dependências do Frontend
```bash
cd ../frontend
npm install --legacy-peer-deps
```

**Dependências Principais:**
- react==19.0.0
- react-dom==19.0.0
- react-router-dom==7.5.1
- axios==1.12.2
- tailwindcss==3.4.17
- framer-motion==12.23.24
- radix-ui (múltiplos pacotes)
- lucide-react==0.507.0
- sonner==2.0.3

#### 5. Execute a Aplicação

**Opção A: Scripts Automáticos (Windows)**
```bash
# Inicia Backend + Frontend
start-all.bat

# Ou individualmente:
start-backend.bat
start-frontend.bat
```

**Opção B: Manual**
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm start
```

#### 6. Acesse a Aplicação
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Admin:** http://localhost:3000/admin

---

### **Deploy em Produção**

#### **Backend (Render.com)**

1. **Crie Web Service no Render**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

2. **Configure Environment Variables**
   ```
   GEMINI_KEY=xxx
   ELEVENLABS_KEY=xxx
   ADMIN_PASSWORD=xxx
   BACKEND_URL=https://seu-backend.onrender.com
   ```

3. **Configure `render.yaml`**
   ```yaml
   services:
     - type: web
       name: talking-photo-backend
       env: python
       buildCommand: "pip install -r requirements.txt"
       startCommand: "uvicorn server:app --host 0.0.0.0 --port $PORT"
       envVars:
         - key: PYTHON_VERSION
           value: 3.10
   ```

#### **Frontend (Vercel/Netlify)**

1. **Build Settings**
   - Build Command: `npm run build`
   - Publish Directory: `build`

2. **Environment Variables**
   ```
   REACT_APP_BACKEND_URL=https://seu-backend.onrender.com
   ```

3. **Redirects (para SPA)**
   Criar `public/_redirects`:
   ```
   /*    /index.html   200
   ```

---

## 📈 Métricas e KPIs

### **Métricas Técnicas**

1. **Performance**
   - Tempo de análise de imagem: < 3s
   - Tempo de geração de áudio: < 10s
   - Tempo de geração de vídeo: 60-90s (média)
   - Uptime do backend: > 99.5%

2. **Custos**
   - Custo médio por vídeo: $0.61 (8s)
   - Economia vs FAL.AI: 62%
   - Custo de áudio: $0.15 (30s)
   - Custo de análise: $0.00

3. **Qualidade**
   - Taxa de sucesso de vídeos: > 95%
   - Taxa de erro de API: < 2%
   - Satisfação do usuário: > 4.5/5

### **Métricas de Negócio**

1. **Engajamento**
   - Vídeos gerados por usuário: Média de 5/mês
   - Taxa de retorno: > 60%
   - Tempo médio na plataforma: 15 min

2. **Conversão**
   - Taxa de conclusão do fluxo: > 80%
   - Taxa de download: > 90%
   - Taxa de compartilhamento: > 30%

---

## 🔧 Manutenção e Troubleshooting

### **Logs e Monitoramento**

**Backend Logging:**
```python
logger.info("✅ Vídeo gerado com sucesso")
logger.warning("⚠️ Provider temporariamente indisponível")
logger.error("❌ Erro ao gerar vídeo")
```

**Arquivos de Log:**
- Backend: Console output (stdout)
- Frontend: Browser console
- Database: `backend/database/video_gen.db`

### **Problemas Comuns**

#### 1. Erro: "GEMINI_KEY not found"
**Solução:** Configure a variável de ambiente no arquivo `.env`

#### 2. Erro: "Port 8000 already in use"
**Solução:** Mate processos Python rodando:
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force
```

#### 3. Erro: "Module 'google.genai' not found"
**Solução:** Reinstale dependências:
```bash
pip install google-genai==1.45.0
```

#### 4. Frontend não carrega
**Solução:** Verifique se `REACT_APP_BACKEND_URL` está configurado corretamente

#### 5. Vídeo trava em "processing"
**Solução:** 
- Verifique logs do backend
- Confirme saldo da API Gemini
- Aguarde até 10 minutos (timeout)

---

## 📚 Referências e Documentação

### **Google Gemini API**
- Documentação Oficial: https://ai.google.dev/
- Gemini API Video: https://ai.google.dev/gemini-api/docs/video
- Cookbook Veo 3.1: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_Veo.ipynb
- Blog Announcement: https://developers.googleblog.com/pt-br/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api/

### **ElevenLabs**
- API Docs: https://elevenlabs.io/docs/api-reference
- Voice Library: https://elevenlabs.io/voice-library
- Pricing: https://elevenlabs.io/pricing

### **Frameworks e Bibliotecas**
- FastAPI: https://fastapi.tiangolo.com/
- React 19: https://react.dev/
- Tailwind CSS: https://tailwindcss.com/
- Radix UI: https://www.radix-ui.com/
- Framer Motion: https://www.framer.com/motion/

---

## 🗺️ Roadmap Futuro

### **Versão 2.1 (Q1 2026)**
- [ ] Suporte a múltiplos idiomas (i18n)
- [ ] Histórico de prompts salvos
- [ ] Templates de vídeo pré-configurados
- [ ] Export em múltiplos formatos (MP4, GIF, WEBM)

### **Versão 2.2 (Q2 2026)**
- [ ] Integração com redes sociais (upload direto)
- [ ] Editor de vídeo básico (trim, crop)
- [ ] Watermark customizado
- [ ] Colaboração multi-usuário

### **Versão 3.0 (Q3 2026)**
- [ ] Autenticação com Google/GitHub
- [ ] Planos de assinatura (Free/Pro/Enterprise)
- [ ] API pública para desenvolvedores
- [ ] Marketplace de templates

---

## 📝 Notas Finais

### **Decisões de Arquitetura**

1. **Por que SQLite em vez de MongoDB?**
   - Simplicidade de deploy (sem servidor externo)
   - Backup trivial (copiar arquivo .db)
   - Performance adequada para escala inicial
   - Custo zero de infraestrutura

2. **Por que Google Veo 3.1 (Gemini) em vez de FAL.AI?**
   - 62% mais barato ($0.076/s vs $0.40/s)
   - Áudio nativo incluído
   - API oficial do Google (estabilidade)
   - Documentação completa
   - Modelo de última geração

3. **Por que React 19 em vez de Next.js?**
   - Simplicidade para MVP
   - Sem necessidade de SSR/SSG
   - Deploy mais simples
   - Menor curva de aprendizado

### **Licença**
Proprietário - Maurício Amorim © 2025

### **Contato**
- GitHub: @mauricioamorim3r
- Email: mauricio@example.com

---

**Última atualização:** 21 de Outubro de 2025  
**Versão do Documento:** 2.0  
**Status:** ✅ Produção
