import { useState, useRef, useEffect } from 'react';
import { Upload, Camera, Sparkles, Video, Mic, Loader2, Download, DollarSign, Play, Wand2, AlertCircle, Crown, Zap, Grid } from 'lucide-react';
import axios from 'axios';
import Webcam from 'react-webcam';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Slider } from '../components/ui/slider';
import { Alert, AlertDescription } from '../components/ui/alert';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import '../styles/HomePage.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = () => {
  const [step, setStep] = useState(1);
  const [imageFile, setImageFile] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedMode, setSelectedMode] = useState('premium'); // premium or economico
  const [prompt, setPrompt] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [showWebcam, setShowWebcam] = useState(false);
  const [estimatedCost, setEstimatedCost] = useState(0);
  const [actualCost, setActualCost] = useState(0);
  const [showCinematicPrompt, setShowCinematicPrompt] = useState(false);
  
  // Audio generation states
  const [audioText, setAudioText] = useState('');
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState('cgSgspJ2msm6clMCkdW9');
  const [voiceSpeed, setVoiceSpeed] = useState(1.0);
  const [voiceStability, setVoiceStability] = useState(0.5);
  const [voiceSimilarity, setVoiceSimilarity] = useState(0.75);
  const [duration, setDuration] = useState(5);
  
  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);
  const voicesFetchedRef = useRef(false);

  const fetchVoices = async () => {
    // Prevent multiple calls
    if (voicesFetchedRef.current) return;
    
    try {
      voicesFetchedRef.current = true;
      const response = await axios.get(`${API}/audio/voices`);
      if (response.data.success) {
        setVoices(response.data.voices);
      }
    } catch (error) {
      console.error('Error fetching voices:', error);
      voicesFetchedRef.current = false; // Allow retry on error
      // Don't show error toast here as it's not critical
    }
  };

  const handleImageUpload = async (file) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await axios.post(`${API}/images/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (uploadResponse.data.success) {
        const imgUrl = uploadResponse.data.image_url;
        setImageUrl(imgUrl);
        setImageFile(URL.createObjectURL(file));
        toast.success('Imagem carregada com sucesso!');
        
        // Analyze image
        await analyzeImage(imgUrl);
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      toast.error('Erro ao carregar imagem');
    } finally {
      setLoading(false);
    }
  };

  const handleWebcamCapture = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    setLoading(true);
    try {
      // Convert base64 to blob
      const blob = await (await fetch(imageSrc)).blob();
      const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' });
      await handleImageUpload(file);
      setShowWebcam(false);
    } catch (error) {
      console.error('Error capturing from webcam:', error);
      toast.error('Erro ao capturar imagem');
      setLoading(false);
    }
  };

  const analyzeImage = async (imgUrl) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/images/analyze`, {
        image_url: imgUrl
      });

      if (response.data.success) {
        setAnalysis(response.data.analysis);
        // Set model based on selected mode
        if (selectedMode === 'premium') {
          const recommendedModel = response.data.analysis.recommended_model_premium || 'sora2';
          setSelectedModel(recommendedModel);
          // Use model-specific prompt
          if (recommendedModel === 'sora2') {
            setPrompt(response.data.analysis.prompt_sora2 || response.data.analysis.tips || '');
          } else if (recommendedModel === 'veo3') {
            setPrompt(response.data.analysis.prompt_veo3 || response.data.analysis.tips || '');
          } else {
            // wav2lip fallback
            setPrompt(response.data.analysis.prompt_veo3 || response.data.analysis.tips || '');
          }
        } else {
          setSelectedModel(response.data.analysis.recommended_model_economico || 'open-sora');
          setPrompt(response.data.analysis.prompt_economico || response.data.analysis.tips || '');
        }
        toast.success('Análise cinematográfica concluída!');
        setStep(2);
      }
    } catch (error) {
      console.error('Error analyzing image:', error);
      toast.error('Erro ao analisar imagem');
    } finally {
      setLoading(false);
    }
  };

  const applyCinematicPrompt = () => {
    if (selectedMode === 'premium') {
      setPrompt(analysis.full_prompt_premium || '');
    } else {
      setPrompt(analysis.full_prompt_economico || '');
    }
    toast.success('Prompt cinematográfico aplicado!');
  };

  const generateAudio = async () => {
    if (!audioText) {
      toast.error('Digite um texto para gerar o áudio');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/audio/generate`, {
        text: audioText,
        voice_id: selectedVoice,
        stability: voiceStability,
        similarity_boost: voiceSimilarity,
        speed: voiceSpeed,
        style: 0.0
      });

      if (response.data.success) {
        setAudioUrl(response.data.audio_url);
        toast.success(`Áudio gerado! Custo: $${response.data.cost.toFixed(2)}`);
      }
    } catch (error) {
      console.error('Error generating audio:', error);
      toast.error('Erro ao gerar áudio');
    } finally {
      setLoading(false);
    }
  };

  const estimateCost = async () => {
    try {
      const response = await axios.post(`${API}/video/estimate-cost`, {
        model: selectedModel,
        mode: selectedMode,
        duration: duration,
        with_audio: selectedModel === 'veo3' && audioUrl !== ''
      });

      if (response.data.success) {
        setEstimatedCost(response.data.estimated_cost);
      }
    } catch (error) {
      console.error('Error estimating cost:', error);
    }
  };

  const generateVideo = async () => {
    if (!prompt) {
      toast.error('Digite um prompt para gerar o vídeo');
      return;
    }

    if ((selectedModel === 'wav2lip' || selectedModel === 'wav2lip-free') && !audioUrl) {
      toast.error('Wav2lip requer um áudio. Gere ou faça upload de um áudio primeiro.');
      return;
    }

    setLoading(true);
    setStep(4);
    
    try {
      const response = await axios.post(`${API}/video/generate`, {
        image_url: imageUrl,
        model: selectedModel,
        mode: selectedMode,
        prompt: prompt,
        audio_url: audioUrl || null,
        duration: duration
      });

      if (response.data.success) {
        setVideoUrl(response.data.video_url);
        setActualCost(response.data.cost);
        if (response.data.is_free) {
          toast.success(`Vídeo gerado com sucesso! 🎉 GRATUITO`);
        } else {
          toast.success(`Vídeo gerado com sucesso! Custo: $${response.data.cost.toFixed(2)}`);
        }
      }
    } catch (error) {
      console.error('Error generating video:', error);
      
      // Check if it's a content policy error
      const errorDetail = error.response?.data?.detail;
      if (errorDetail && typeof errorDetail === 'object') {
        if (errorDetail.error_code === 'CONTENT_POLICY') {
          // Show detailed content policy message
          toast.error(errorDetail.message, { duration: 10000 });
        } else {
          toast.error(errorDetail.message || 'Erro ao gerar vídeo');
        }
      } else {
        toast.error('Erro ao gerar vídeo: ' + (errorDetail || error.message));
      }
      
      setStep(3);
    } finally {
      setLoading(false);
    }
  };

  // Load voices on component mount
  useEffect(() => {
    fetchVoices();
  }, []);

  // Estimate cost when model, duration, mode or audio changes
  useEffect(() => {
    if (selectedModel && duration) {
      estimateCost();
    }
  }, [selectedModel, selectedMode, duration, audioUrl]);

  return (
    <div className="home-page">
      {/* Header */}
      <header className="header">
        <div className="container">
          <motion.div 
            className="logo"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Video className="logo-icon" />
            <h1>VideoMagic AI</h1>
          </motion.div>
          <div className="header-buttons">
            <Button 
              variant="outline" 
              onClick={() => window.location.href = '/gallery'}
              data-testid="gallery-button"
            >
              <Grid className="w-4 h-4 mr-2" />
              Galeria
            </Button>
            <Button 
              variant="outline" 
              onClick={() => window.location.href = '/admin'}
              data-testid="admin-button"
            >
              <DollarSign className="w-4 h-4 mr-2" />
              Admin
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Hero Section */}
          {step === 1 && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="hero-section"
            >
              <div className="hero-text">
                <h1 className="hero-title" data-testid="hero-title">
                  Transforme Fotos em
                  <span className="gradient-text"> Vídeos Incríveis</span>
                </h1>
                <p className="hero-subtitle">
                  Use IA para animar suas imagens com movimento e áudio sincronizado
                </p>
              </div>

              <Card className="upload-card" data-testid="upload-card">
                <CardHeader>
                  <CardTitle>Comece Enviando uma Imagem</CardTitle>
                  <CardDescription>
                    Carregue uma foto ou tire uma selfie para começar
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {!showWebcam ? (
                    <div className="upload-options">
                      <Button
                        className="upload-btn"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={loading}
                        data-testid="upload-file-button"
                      >
                        {loading ? (
                          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        ) : (
                          <Upload className="w-5 h-5 mr-2" />
                        )}
                        Escolher Arquivo
                      </Button>
                      <Button
                        className="upload-btn"
                        variant="outline"
                        onClick={() => setShowWebcam(true)}
                        data-testid="open-webcam-button"
                      >
                        <Camera className="w-5 h-5 mr-2" />
                        Usar Câmera
                      </Button>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        style={{ display: 'none' }}
                        onChange={(e) => {
                          if (e.target.files?.[0]) {
                            handleImageUpload(e.target.files[0]);
                          }
                        }}
                      />
                    </div>
                  ) : (
                    <div className="webcam-container">
                      <Webcam
                        ref={webcamRef}
                        screenshotFormat="image/jpeg"
                        className="webcam"
                      />
                      <div className="webcam-actions">
                        <Button onClick={handleWebcamCapture} disabled={loading} data-testid="capture-button">
                          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Camera className="w-5 h-5" />}
                          Capturar
                        </Button>
                        <Button variant="outline" onClick={() => setShowWebcam(false)} data-testid="close-webcam-button">
                          Cancelar
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Configuration Step */}
          {step === 2 && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="config-section"
            >
              <div className="preview-section">
                <Card>
                  <CardHeader>
                    <CardTitle>Imagem Carregada</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <img src={imageFile} alt="Preview" className="preview-image" data-testid="preview-image" />
                    {analysis && (
                      <div className="analysis-box" data-testid="analysis-box">
                        <h4><Sparkles className="w-4 h-4 inline mr-2" />Análise da IA</h4>
                        <p><strong>Tipo:</strong> {analysis.subject_type}</p>
                        <p><strong>Descrição:</strong> {analysis.description}</p>
                        {selectedMode === 'premium' ? (
                          <>
                            <p><strong>Modelo Recomendado:</strong> {analysis.recommended_model_premium?.toUpperCase()}</p>
                            <p><strong>Motivo:</strong> {analysis.reason_premium}</p>
                          </>
                        ) : (
                          <>
                            <p><strong>Modelo Recomendado:</strong> {analysis.recommended_model_economico?.toUpperCase()}</p>
                            <p><strong>Motivo:</strong> {analysis.reason_economico}</p>
                          </>
                        )}
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="mt-3 w-full"
                          onClick={() => analyzeImage(imageUrl)}
                          disabled={loading}
                          data-testid="reanalyze-button"
                        >
                          {loading ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <Sparkles className="w-4 h-4 mr-2" />
                          )}
                          Re-analisar Imagem
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              <div className="config-panel">
                <Card>
                  <CardHeader>
                    <CardTitle>Configuração do Vídeo</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Mode Selector */}
                    <div>
                      <label className="label">Modo de Geração</label>
                      <div className="mode-selector">
                        <button
                          className={`mode-button ${selectedMode === 'premium' ? 'active premium' : ''}`}
                          onClick={() => {
                            setSelectedMode('premium');
                            setSelectedModel('veo3');
                            if (analysis) {
                              setPrompt(analysis.full_prompt_premium || '');
                            }
                          }}
                          data-testid="premium-mode-button"
                        >
                          <Crown className="w-5 h-5" />
                          <div>
                            <div className="mode-title">Premium</div>
                            <div className="mode-subtitle">Melhor qualidade</div>
                          </div>
                        </button>
                        <button
                          className={`mode-button ${selectedMode === 'economico' ? 'active economico' : ''}`}
                          onClick={() => {
                            setSelectedMode('economico');
                            setSelectedModel('open-sora');
                            if (analysis) {
                              setPrompt(analysis.full_prompt_economico || '');
                            }
                          }}
                          data-testid="economico-mode-button"
                        >
                          <Zap className="w-5 h-5" />
                          <div>
                            <div className="mode-title">Econômico</div>
                            <div className="mode-subtitle">100% Gratuito</div>
                          </div>
                        </button>
                      </div>
                    </div>

                    {/* Warning for Economico mode */}
                    {selectedMode === 'economico' && (
                      <Alert className="economico-warning">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Modo Econômico:</strong> Modelos gratuitos via HuggingFace. Pode haver fila de processamento e qualidade pode ser inferior ao Premium.
                        </AlertDescription>
                      </Alert>
                    )}

                    <div>
                      <label className="label">Modelo de IA</label>
                      <Select value={selectedModel} onValueChange={setSelectedModel}>
                        <SelectTrigger data-testid="model-select">
                          <SelectValue placeholder="Escolha um modelo" />
                        </SelectTrigger>
                        <SelectContent>
                          {selectedMode === 'premium' ? (
                            <>
                              <SelectItem value="veo3">🎬 Veo 3.1 - Alta Qualidade + Áudio Nativo ($0.20-0.40/seg)</SelectItem>
                              <SelectItem value="sora2">⚡ Sora 2 - Com Áudio Nativo ($0.10/seg)</SelectItem>
                              <SelectItem value="wav2lip">👄 Wav2lip - Sincronização Labial ($0.05/seg)</SelectItem>
                            </>
                          ) : (
                            <>
                              <SelectItem value="open-sora">🆓 Open-Sora v2 - Gratuito</SelectItem>
                              <SelectItem value="wav2lip-free">👄 Wav2lip Free - Gratuito</SelectItem>
                            </>
                          )}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="label">Duração (segundos): {duration}s</label>
                      <Slider
                        value={[duration]}
                        onValueChange={(val) => setDuration(val[0])}
                        min={3}
                        max={10}
                        step={1}
                        data-testid="duration-slider"
                      />
                    </div>

                    {/* Cinematic Prompt Section */}
                    {analysis && analysis.cinematic_prompt && (
                      <div className="cinematic-section">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowCinematicPrompt(!showCinematicPrompt)}
                          data-testid="toggle-cinematic-button"
                        >
                          <Wand2 className="w-4 h-4 mr-2" />
                          {showCinematicPrompt ? 'Ocultar' : 'Ver'} Sugestões Cinematográficas
                        </Button>
                        
                        {showCinematicPrompt && (
                          <div className="cinematic-prompts" data-testid="cinematic-prompts">
                            <h5>Elementos Cinematográficos:</h5>
                            
                            <div className="cinematic-item">
                              <strong>Assunto e Ação:</strong> {analysis.cinematic_prompt.subject_action}
                            </div>
                            
                            {analysis.cinematic_prompt.facial_fidelity && (
                              <div className="cinematic-item critical">
                                <strong>⚠️ Fidelidade Facial (Crítico):</strong> {analysis.cinematic_prompt.facial_fidelity}
                              </div>
                            )}
                            
                            <div className="cinematic-item">
                              <strong>Tipo de Plano:</strong> {analysis.cinematic_prompt.camera_shot}
                            </div>
                            
                            <div className="cinematic-item">
                              <strong>Movimento:</strong> {analysis.cinematic_prompt.camera_movement}
                            </div>
                            
                            <div className="cinematic-item">
                              <strong>Iluminação:</strong> {analysis.cinematic_prompt.lighting}
                            </div>
                            
                            <div className="cinematic-item">
                              <strong>Lente:</strong> {analysis.cinematic_prompt.lens}
                            </div>
                            
                            <div className="cinematic-item">
                              <strong>Estilo de Cor:</strong> {analysis.cinematic_prompt.color_style}
                            </div>
                            
                            {analysis.cinematic_prompt.audio_instruction && (selectedModel === 'veo3' || selectedModel === 'sora2') && (
                              <div className="cinematic-item audio">
                                <strong>🎵 Instrução de Áudio:</strong> {analysis.cinematic_prompt.audio_instruction}
                              </div>
                            )}
                            
                            <div className="cinematic-item">
                              <strong>Qualidade:</strong> {analysis.cinematic_prompt.quality}
                            </div>
                            
                            <Button 
                              size="sm" 
                              onClick={applyCinematicPrompt}
                              className="mt-3"
                              data-testid="apply-cinematic-button"
                            >
                              Aplicar Prompt Completo
                            </Button>
                          </div>
                        )}
                      </div>
                    )}

                    <div>
                      <label className="label">Prompt do Vídeo</label>
                      <Textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Descreva como quer animar a imagem..."
                        rows={6}
                        data-testid="prompt-textarea"
                      />
                      {(selectedModel === 'veo3' || selectedModel === 'sora2') && (
                        <p className="model-info">
                          🎵 {selectedModel === 'veo3' ? 'Veo 3' : 'Sora 2'} gera áudio automaticamente sincronizado com o vídeo. 
                          Inclua instruções de áudio no prompt (ex: "com sons de risadas e conversas")
                        </p>
                      )}
                      {(selectedModel === 'wav2lip' || selectedModel === 'wav2lip-free') && (
                        <p className="model-info wav2lip-info">
                          👄 Wav2lip requer áudio separado para sincronização labial. Você precisará gerar/fazer upload de áudio na próxima etapa.
                        </p>
                      )}
                    </div>

                    {selectedMode === 'premium' && estimatedCost > 0 && (
                      <div className="cost-box" data-testid="cost-estimate">
                        <DollarSign className="w-5 h-5" />
                        <span>Custo Estimado: ${estimatedCost.toFixed(2)}</span>
                      </div>
                    )}

                    {selectedMode === 'economico' && (
                      <div className="free-box" data-testid="free-badge">
                        <Zap className="w-5 h-5" />
                        <span>100% GRATUITO</span>
                      </div>
                    )}

                    <Button 
                      className="w-full" 
                      size="lg"
                      onClick={() => {
                        // Veo 3 e Sora 2 geram áudio nativo, pular etapa de áudio
                        if (selectedModel === 'veo3' || selectedModel === 'sora2') {
                          generateVideo();
                        } else {
                          // Wav2lip e outros precisam de áudio separado
                          setStep(3);
                        }
                      }}
                      data-testid="continue-to-audio-button"
                    >
                      {(selectedModel === 'veo3' || selectedModel === 'sora2') ? 'Gerar Vídeo com Áudio Nativo' : 'Continuar para Configurar Áudio'}
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </motion.div>
          )}

          {/* Audio Step */}
          {step === 3 && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="audio-section"
            >
              <Card>
                <CardHeader>
                  <CardTitle>Configuração de Áudio (Opcional)</CardTitle>
                  <CardDescription>
                    Gere um áudio ou pule para criar o vídeo apenas com a imagem
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="generate" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="generate" data-testid="generate-audio-tab">Gerar Áudio</TabsTrigger>
                      <TabsTrigger value="upload" data-testid="upload-audio-tab">Fazer Upload</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="generate" className="space-y-4">
                      <div>
                        <label className="label">Texto para Áudio</label>
                        <Textarea
                          value={audioText}
                          onChange={(e) => setAudioText(e.target.value)}
                          placeholder="Digite o texto que será falado..."
                          rows={4}
                          data-testid="audio-text-textarea"
                        />
                      </div>

                      <div>
                        <label className="label">Voz</label>
                        <Select value={selectedVoice} onValueChange={setSelectedVoice}>
                          <SelectTrigger data-testid="voice-select">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {voices.map((voice) => (
                              <SelectItem key={voice.voice_id} value={voice.voice_id}>
                                {voice.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <label className="label">Velocidade: {voiceSpeed.toFixed(1)}x</label>
                        <Slider
                          value={[voiceSpeed]}
                          onValueChange={(val) => setVoiceSpeed(val[0])}
                          min={0.5}
                          max={2.0}
                          step={0.1}
                          data-testid="speed-slider"
                        />
                      </div>

                      <div>
                        <label className="label">Estabilidade: {(voiceStability * 100).toFixed(0)}%</label>
                        <Slider
                          value={[voiceStability]}
                          onValueChange={(val) => setVoiceStability(val[0])}
                          min={0}
                          max={1}
                          step={0.05}
                          data-testid="stability-slider"
                        />
                      </div>

                      <Button 
                        className="w-full" 
                        onClick={generateAudio}
                        disabled={loading || !audioText}
                        data-testid="generate-audio-button"
                      >
                        {loading ? (
                          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        ) : (
                          <Mic className="w-5 h-5 mr-2" />
                        )}
                        Gerar Áudio
                      </Button>

                      {audioUrl && (
                        <div className="audio-preview" data-testid="audio-preview">
                          <audio controls src={audioUrl} className="w-full" />
                        </div>
                      )}
                    </TabsContent>

                    <TabsContent value="upload">
                      <div className="text-center py-8">
                        <p className="text-gray-600 mb-4">Funcionalidade de upload de áudio em desenvolvimento</p>
                      </div>
                    </TabsContent>
                  </Tabs>

                  <div className="flex gap-3 mt-6">
                    <Button 
                      variant="outline" 
                      onClick={() => setStep(2)}
                      data-testid="back-to-config-button"
                    >
                      Voltar
                    </Button>
                    <Button 
                      className="flex-1" 
                      size="lg"
                      onClick={generateVideo}
                      disabled={loading}
                      data-testid="generate-video-button"
                    >
                      {loading ? (
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      ) : (
                        <Play className="w-5 h-5 mr-2" />
                      )}
                      Gerar Vídeo
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Result Step */}
          {step === 4 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="result-section"
            >
              <Card>
                <CardHeader>
                  <CardTitle>
                    {loading ? 'Gerando seu vídeo...' : 'Vídeo Pronto!'}
                  </CardTitle>
                  <CardDescription>
                    {loading ? 'Isso pode levar alguns minutos' : `Custo total: $${actualCost.toFixed(2)}`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="loading-state" data-testid="loading-spinner">
                      <Loader2 className="w-16 h-16 animate-spin text-purple-500" />
                      <p className="mt-4 text-gray-600">Processando com {selectedModel.toUpperCase()}...</p>
                    </div>
                  ) : videoUrl ? (
                    <div className="video-result" data-testid="video-result">
                      <video controls src={videoUrl} className="result-video" />
                      <div className="result-actions">
                        <Button size="lg" asChild data-testid="download-button">
                          <a href={videoUrl} download>
                            <Download className="w-5 h-5 mr-2" />
                            Baixar Vídeo
                          </a>
                        </Button>
                        <Button 
                          variant="outline" 
                          size="lg"
                          onClick={() => {
                            setStep(1);
                            setImageFile(null);
                            setImageUrl('');
                            setAnalysis(null);
                            setSelectedModel('');
                            setPrompt('');
                            setAudioUrl('');
                            setVideoUrl('');
                          }}
                          data-testid="create-new-button"
                        >
                          Criar Novo Vídeo
                        </Button>
                      </div>
                    </div>
                  ) : null}
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
};

export default HomePage;