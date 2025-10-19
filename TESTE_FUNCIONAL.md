# ✅ CHECKLIST DE TESTE FUNCIONAL

## 🎯 OBJETIVO
Verificar se todas as funcionalidades do Talking Photo Generator estão funcionando após o deploy.

---

## 📋 TESTES BÁSICOS

### 1. ✅ Navegação
- [ ] Página inicial carrega
- [ ] Menu "Gerar Imagens" funciona
- [ ] Botão "$ Admin" abre painel administrativo
- [ ] Navegação entre páginas é fluida

### 2. ✅ Upload de Imagem
- [ ] Botão de upload aparece
- [ ] Consegue selecionar imagem do computador
- [ ] Preview da imagem aparece
- [ ] Imagem é enviada para o backend

### 3. ✅ Geração de Prompt (Google Gemini)
- [ ] Campo de texto para prompt existe
- [ ] Consegue gerar prompt automático
- [ ] Prompt aparece no campo
- [ ] Pode editar o prompt gerado

### 4. ✅ Seleção de Voz (ElevenLabs)
- [ ] Lista de vozes carrega
- [ ] Vozes em português aparecem
- [ ] Consegue selecionar uma voz
- [ ] Preview de voz funciona (se disponível)

### 5. ✅ Geração de Áudio (ElevenLabs)
- [ ] Botão de gerar áudio funciona
- [ ] Áudio é gerado com sucesso
- [ ] Player de áudio aparece
- [ ] Consegue ouvir o áudio gerado

### 6. ✅ Geração de Vídeo (FAL.AI)
- [ ] Botão de gerar vídeo funciona
- [ ] Progresso de geração aparece
- [ ] Vídeo é gerado (pode levar 2-5 minutos)
- [ ] Player de vídeo aparece
- [ ] Vídeo reproduz corretamente

### 7. ✅ Galeria
- [ ] Página de galeria abre
- [ ] Vídeos gerados aparecem
- [ ] Consegue visualizar vídeos salvos
- [ ] Consegue baixar vídeos

### 8. ✅ Painel Admin
- [ ] Acessa com "$" no canto
- [ ] Lista de vídeos gerados aparece
- [ ] Estatísticas aparecem (se implementado)
- [ ] Consegue gerenciar conteúdo

---

## 🔧 TESTES TÉCNICOS

### 9. ✅ API Backend
- [ ] Health check: https://gerador-fantasia.onrender.com/health
- [ ] API de vozes: https://gerador-fantasia.onrender.com/api/audio/voices
- [ ] CORS configurado corretamente
- [ ] Respostas JSON válidas

### 10. ✅ Performance
- [ ] Primeira carga < 5 segundos
- [ ] Navegação entre páginas < 1 segundo
- [ ] Upload de imagem < 3 segundos
- [ ] Backend responde em < 2 segundos (após acordar)

---

## 🚨 PROBLEMAS CONHECIDOS

### ❌ Se Backend Retornar 502
**Causa:** Backend hibernou (Free Tier)
**Solução:** 
```bash
python wake_backend.py
```
Ou aguarde 30-60 segundos que ele acorda sozinho.

### ❌ Se Upload Falhar
**Verificar:**
1. Tamanho da imagem (< 10MB recomendado)
2. Formato (JPG, PNG)
3. Conexão com internet

### ❌ Se Geração de Vídeo Falhar
**Verificar:**
1. API Keys configuradas no Render
2. Logs do backend no Dashboard
3. Saldo das APIs (FAL.AI, etc)

---

## 📊 RESULTADO ESPERADO

Após completar este checklist:

- ✅ **10/10 testes básicos** → App 100% funcional
- ✅ **8-10/10 testes básicos** → App funcional com pequenos problemas
- ⚠️ **5-7/10 testes** → Problemas médios, precisa investigar
- ❌ **< 5/10 testes** → Problemas críticos, revisar deploy

---

## 🎯 TESTE AGORA!

1. **Faça upload de uma imagem de teste**
2. **Gere um prompt**
3. **Selecione uma voz em português** (ex: "Fernando Borges")
4. **Gere o áudio**
5. **Gere o vídeo** (aguarde 2-5 minutos)
6. **Verifique na galeria**

---

## 📞 SUPORTE

Se encontrar problemas:

1. **Verifique os logs:**
   - Frontend: Console do navegador (F12)
   - Backend: https://dashboard.render.com/web/srv-d3q80d0gjchc73b48p40

2. **Execute testes:**
   ```bash
   python test_integration.py
   python wake_backend.py
   ```

3. **Documentação:**
   - `DEPLOY_COMPLETO.md`
   - `FREE_TIER_HIBERNATION.md`

---

**Data do Teste:** _____________  
**Testado por:** _____________  
**Resultado:** ✅ PASSOU / ⚠️ PARCIAL / ❌ FALHOU
