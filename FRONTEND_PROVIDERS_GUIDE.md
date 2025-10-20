# 🎬 Sistema de Múltiplos Providers de Vídeo

## 📋 Overview

Agora a aplicação suporta **múltiplos providers** de geração de vídeo:
- **FAL.AI** (Veo 3.1, Sora 2, Wav2lip) - Sempre disponível
- **Google Veo 3.1 Direct** - Economia de 60-75% (requer configuração)

## 🏗️ Arquitetura

```
Frontend (React)
    ↓
Backend API (/video/providers, /video/generate)
    ↓
VideoProviderManager
    ↓
    ├─ FAL.AI Provider (fal_client)
    └─ Google Direct Provider (Vertex AI)
```

## 🔌 API Endpoints

### 1. GET /api/video/providers

**Descrição:** Lista providers disponíveis e seus custos

**Response:**
```json
{
  "success": true,
  "providers": [
    {
      "id": "fal_veo3",
      "name": "Veo 3.1 (FAL.AI)",
      "provider": "fal",
      "description": "Google Veo 3.1 via FAL.AI - Alta qualidade",
      "available": true,
      "cost_per_second": 0.20,
      "cost_per_second_with_audio": 0.40,
      "max_duration": 8,
      "supports_audio": true,
      "quality": "premium"
    },
    {
      "id": "google_veo3",
      "name": "Veo 3.1 (Google Direct)",
      "provider": "google",
      "description": "Google Veo 3.1 direto - 60% mais barato",
      "available": true,
      "cost_per_second": 0.12,
      "cost_per_second_with_audio": 0.15,
      "max_duration": 8,
      "supports_audio": true,
      "quality": "premium",
      "savings_vs_fal": "60%"
    }
  ],
  "default_provider": "fal_veo3"
}
```

### 2. POST /api/video/generate

**Request Body:**
```json
{
  "image_url": "https://...",
  "model": "veo3",
  "provider": "google",  // NOVO: "fal" ou "google"
  "mode": "premium",
  "prompt": "Uma criança feliz correndo...",
  "duration": 8,
  "audio_url": null
}
```

**Response:**
```json
{
  "success": true,
  "video_id": "abc-123",
  "video_url": "https://storage.googleapis.com/...",
  "provider": "google_veo3",
  "cost": 1.20,
  "duration": 8,
  "status": "completed"
}
```

## 🎨 Frontend - Como Implementar

### Opção 1: Selector Simples (Recomendado)

```jsx
import React, { useState, useEffect } from 'react';

function VideoGenerator() {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('fal_veo3');
  
  useEffect(() => {
    // Carregar providers disponíveis
    fetch('http://localhost:8000/api/video/providers')
      .then(res => res.json())
      .then(data => {
        setProviders(data.providers);
        setSelectedProvider(data.default_provider);
      });
  }, []);
  
  const handleGenerate = async () => {
    const response = await fetch('http://localhost:8000/api/video/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_url: imageUrl,
        model: 'veo3',
        provider: selectedProvider === 'google_veo3' ? 'google' : 'fal',
        mode: 'premium',
        prompt: prompt,
        duration: 8
      })
    });
    
    const result = await response.json();
    console.log('Vídeo gerado:', result);
  };
  
  return (
    <div>
      <h3>Escolha o Provider:</h3>
      
      <select 
        value={selectedProvider} 
        onChange={(e) => setSelectedProvider(e.target.value)}
      >
        {providers.map(p => (
          <option key={p.id} value={p.id}>
            {p.name} - ${p.cost_per_second_with_audio}/seg
            {p.savings_vs_fal && ` (Economia: ${p.savings_vs_fal})`}
          </option>
        ))}
      </select>
      
      <button onClick={handleGenerate}>Gerar Vídeo</button>
    </div>
  );
}
```

### Opção 2: Cards com Comparação

```jsx
function ProviderSelector({ onSelect, selected }) {
  const [providers, setProviders] = useState([]);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/video/providers')
      .then(res => res.json())
      .then(data => setProviders(data.providers));
  }, []);
  
  return (
    <div className="provider-grid">
      {providers.map(provider => (
        <div 
          key={provider.id}
          className={`provider-card ${selected === provider.id ? 'selected' : ''}`}
          onClick={() => onSelect(provider.id)}
        >
          <h4>{provider.name}</h4>
          <p>{provider.description}</p>
          
          <div className="pricing">
            <div>Sem áudio: ${provider.cost_per_second}/seg</div>
            <div>Com áudio: ${provider.cost_per_second_with_audio}/seg</div>
          </div>
          
          {provider.savings_vs_fal && (
            <div className="badge savings">
              🎉 Economize {provider.savings_vs_fal}
            </div>
          )}
          
          {!provider.available && (
            <div className="badge unavailable">
              ⚙️ Requer configuração
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
```

### Opção 3: Auto-Select (Mais Barato)

```jsx
function SmartVideoGenerator() {
  const [bestProvider, setBestProvider] = useState(null);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/video/providers')
      .then(res => res.json())
      .then(data => {
        // Seleciona automaticamente o mais barato
        const sorted = data.providers.sort((a, b) => 
          a.cost_per_second_with_audio - b.cost_per_second_with_audio
        );
        setBestProvider(sorted[0]);
      });
  }, []);
  
  const handleGenerate = async () => {
    // Usa automaticamente o provider mais barato
    const response = await fetch('http://localhost:8000/api/video/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_url: imageUrl,
        model: 'veo3',
        provider: bestProvider.provider,
        mode: 'premium',
        prompt: prompt,
        duration: 8
      })
    });
  };
  
  return (
    <div>
      <div className="auto-provider-info">
        ℹ️ Usando automaticamente: {bestProvider?.name}
        (${bestProvider?.cost_per_second_with_audio}/seg)
      </div>
      
      <button onClick={handleGenerate}>Gerar Vídeo</button>
    </div>
  );
}
```

## 💰 Calculadora de Custos

```jsx
function CostCalculator({ duration, withAudio, provider }) {
  const [cost, setCost] = useState(0);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/video/estimate-cost', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'veo3',
        provider: provider,
        mode: 'premium',
        duration: duration,
        with_audio: withAudio
      })
    })
    .then(res => res.json())
    .then(data => setCost(data.estimated_cost));
  }, [duration, withAudio, provider]);
  
  return (
    <div className="cost-preview">
      Custo estimado: ${cost.toFixed(2)}
    </div>
  );
}
```

## 🎯 UX Recommendations

### 1. **Badge de Economia**
```jsx
{provider.savings_vs_fal && (
  <span className="savings-badge">
    💰 Economize {provider.savings_vs_fal}
  </span>
)}
```

### 2. **Tooltip Explicativo**
```jsx
<Tooltip content="Google Veo Direct usa API do Google diretamente, resultando em custos 60% menores que FAL.AI">
  <InfoIcon />
</Tooltip>
```

### 3. **Comparação Visual**
```jsx
<div className="cost-comparison">
  <div className="provider-option">
    <h4>FAL.AI</h4>
    <div className="price">$3.20</div>
    <div className="details">Via intermediário</div>
  </div>
  
  <div className="vs">vs</div>
  
  <div className="provider-option best">
    <h4>Google Direct</h4>
    <div className="price">$1.20</div>
    <div className="details">Direto do Google</div>
    <div className="badge">60% mais barato ✨</div>
  </div>
</div>
```

## 🧪 Testes

```bash
# Testar providers disponíveis
python test_providers_local.py

# Testar geração via FAL.AI
curl -X POST http://localhost:8000/api/video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://...",
    "model": "veo3",
    "provider": "fal",
    "prompt": "Uma criança feliz",
    "duration": 8
  }'

# Testar geração via Google Direct
curl -X POST http://localhost:8000/api/video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://...",
    "model": "veo3",
    "provider": "google",
    "prompt": "Uma criança feliz",
    "duration": 8
  }'
```

## 📊 Analytics Sugeridos

```jsx
function trackProviderUsage(provider, cost, duration) {
  // Google Analytics
  gtag('event', 'video_generated', {
    provider: provider,
    cost: cost,
    duration: duration
  });
  
  // Amplitude
  amplitude.track('Video Generated', {
    provider: provider,
    cost: cost,
    duration: duration,
    savings: provider === 'google' ? '60%' : '0%'
  });
}
```

## 🚀 Próximos Passos

1. **Frontend:** Adicionar selector de provider no UI de geração
2. **Backend:** Já está pronto! ✅
3. **Testes:** Testar localmente com ambos providers
4. **Deploy:** Configurar Google Cloud no Render (se quiser economia)

## 💡 Dicas

- **Desenvolvimento:** Use FAL.AI (mais fácil de configurar)
- **Produção:** Use Google Direct (60-75% mais barato)
- **Opção:** Deixe usuário escolher (máxima flexibilidade)
