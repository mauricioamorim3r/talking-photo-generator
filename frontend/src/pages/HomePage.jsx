import { useState, useRef } from 'react';
import { Upload, Camera, Sparkles, Video, Mic, Loader2, Download, DollarSign, Play } from 'lucide-react';
import axios from 'axios';
import Webcam from 'react-webcam';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Slider } from '../components/ui/slider';
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
  const [prompt, setPrompt] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [showWebcam, setShowWebcam] = useState(false);
  const [estimatedCost, setEstimatedCost] = useState(0);
  const [actualCost, setActualCost] = useState(0);
  
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

  // Load voices on component mount
  useState(() => {
    fetchVoices();
  }, []);

  const fetchVoices = async () => {
    try {
      const response = await axios.get(`${API}/audio/voices`);
      if (response.data.success) {
        setVoices(response.data.voices);
      }
    } catch (error) {
      console.error('Error fetching voices:', error);
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
        setSelectedModel(response.data.analysis.recommended_model);
        setPrompt(response.data.analysis.tips || '');
        toast.success('Análise concluída! Modelo sugerido: ' + response.data.analysis.recommended_model.toUpperCase());
        setStep(2);
      }
    } catch (error) {
      console.error('Error analyzing image:', error);
      toast.error('Erro ao analisar imagem');
    } finally {
      setLoading(false);
    }
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

    if (selectedModel === 'wav2lip' && !audioUrl) {
      toast.error('Wav2lip requer um áudio. Gere ou faça upload de um áudio primeiro.');
      return;
    }

    setLoading(true);
    setStep(4);
    
    try {
      const response = await axios.post(`${API}/video/generate`, {
        image_url: imageUrl,
        model: selectedModel,
        prompt: prompt,
        audio_url: audioUrl || null,
        duration: duration
      });

      if (response.data.success) {
        setVideoUrl(response.data.video_url);
        setActualCost(response.data.cost);
        toast.success(`Vídeo gerado com sucesso! Custo: $${response.data.cost.toFixed(2)}`);
      }
    } catch (error) {
      console.error('Error generating video:', error);
      toast.error('Erro ao gerar vídeo: ' + (error.response?.data?.detail || error.message));
      setStep(3);
    } finally {
      setLoading(false);
    }
  };

  useState(() => {
    if (selectedModel && duration) {
      estimateCost();
    }
  }, [selectedModel, duration, audioUrl]);

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
          <Button 
            variant="outline" 
            onClick={() => window.location.href = '/admin'}
            data-testid="admin-button"
          >
            <DollarSign className="w-4 h-4 mr-2" />
            Painel Admin
          </Button>
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
                        <p><strong>Modelo Recomendado:</strong> {analysis.recommended_model?.toUpperCase()}</p>
                        <p><strong>Motivo:</strong> {analysis.reason}</p>
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
                    <div>
                      <label className="label">Modelo de IA</label>
                      <Select value={selectedModel} onValueChange={setSelectedModel}>
                        <SelectTrigger data-testid="model-select">
                          <SelectValue placeholder="Escolha um modelo" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="veo3">Veo 3 - Alta Qualidade</SelectItem>
                          <SelectItem value="sora2">Sora 2 - Custo-Benefício</SelectItem>
                          <SelectItem value="wav2lip">Wav2lip - Sincronização Labial</SelectItem>
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

                    <div>
                      <label className="label">Prompt do Vídeo</label>
                      <Textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Descreva como quer animar a imagem..."
                        rows={4}
                        data-testid="prompt-textarea"
                      />
                    </div>

                    {estimatedCost > 0 && (
                      <div className="cost-box" data-testid="cost-estimate">
                        <DollarSign className="w-5 h-5" />
                        <span>Custo Estimado: ${estimatedCost.toFixed(2)}</span>
                      </div>
                    )}

                    <Button 
                      className="w-full" 
                      size="lg"
                      onClick={() => setStep(3)}
                      data-testid="continue-to-audio-button"
                    >
                      Continuar
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