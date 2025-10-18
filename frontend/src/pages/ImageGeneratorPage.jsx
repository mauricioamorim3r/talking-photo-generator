import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Sparkles, Image as ImageIcon, Download, Trash2, Video, Lightbulb, Wand2 } from 'lucide-react';
import './ImageGeneratorPage.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const PROMPT_LIBRARY = {
  realistic: [
    {
      title: "Figura Realista 3D",
      prompt: "Create a 1/7 scale hyper-realistic figure of a character, standing on a round transparent acrylic base on a computer desk, with a premium collector's toy box next to it. Studio lighting, 4K quality."
    },
    {
      title: "Produto Comercial",
      prompt: "Professional product photography of a luxury item on a clean white background, studio lighting with soft shadows, 8K ultra-detailed, commercial advertising quality."
    },
    {
      title: "Retrato Fotorrealista",
      prompt: "Photorealistic portrait of a person with cinematic lighting, shallow depth of field, bokeh background, shot with 85mm f/1.4 lens, professional fashion photography style."
    }
  ],
  anime: [
    {
      title: "Personagem Anime",
      prompt: "Anime style character illustration, vibrant colors, clean linework, detailed eyes, cel-shaded rendering, professional manga art quality."
    },
    {
      title: "Cena de Fantasia Anime",
      prompt: "Fantasy anime scene with magical elements, dramatic lighting, detailed background with floating particles, Studio Ghibli inspired art style."
    },
    {
      title: "Chibi Kawaii",
      prompt: "Cute chibi character in kawaii style, pastel colors, big eyes, simple background with sparkles and hearts, adorable expression."
    }
  ],
  editing: [
    {
      title: "Remover Fundo",
      prompt: "Remove the background and make this look like a professional studio product shot with clean white background."
    },
    {
      title: "Melhorar Qualidade",
      prompt: "Enhance image quality, improve details and sharpness, fix lighting and colors, maintain original style and composition."
    },
    {
      title: "Estilo Artístico",
      prompt: "Transform this image into an artistic painting style with vibrant colors, painterly brushstrokes, and enhanced creative interpretation."
    }
  ]
};

function ImageGeneratorPage() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [imageHistory, setImageHistory] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('realistic');

  useEffect(() => {
    loadImageHistory();
  }, []);

  const loadImageHistory = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/images/generated`);
      if (response.data.success) {
        setImageHistory(response.data.images);
      }
    } catch (error) {
      console.error('Error loading image history:', error);
    }
  };

  const generateImage = async () => {
    if (!prompt.trim()) {
      toast.error('Por favor, insira um prompt');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${BACKEND_URL}/api/images/generate`, {
        prompt: prompt
      });

      if (response.data.success) {
        setGeneratedImage(response.data);
        toast.success('Imagem gerada com sucesso!');
        loadImageHistory(); // Reload history
      }
    } catch (error) {
      console.error('Error generating image:', error);
      toast.error(error.response?.data?.detail || 'Erro ao gerar imagem');
    } finally {
      setLoading(false);
    }
  };

  const downloadImage = (imageUrl, imageId) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `generated_image_${imageId}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Download iniciado!');
  };

  const deleteImage = async (imageId) => {
    try {
      await axios.delete(`${BACKEND_URL}/api/images/generated/${imageId}`);
      toast.success('Imagem deletada!');
      loadImageHistory();
      if (generatedImage?.image_id === imageId) {
        setGeneratedImage(null);
      }
    } catch (error) {
      console.error('Error deleting image:', error);
      toast.error('Erro ao deletar imagem');
    }
  };

  const useForVideo = (imageUrl) => {
    // Navigate to home page with image URL
    navigate('/', { state: { imageUrl } });
    toast.success('Imagem selecionada! Redirecionando para geração de vídeo...');
  };

  const usePromptTemplate = (template) => {
    setPrompt(template);
    toast.success('Prompt aplicado! Você pode editá-lo antes de gerar.');
  };

  return (
    <div className="image-generator-page">
      <div className="page-header">
        <h1>
          <ImageIcon className="header-icon" />
          Gerador de Imagens AI
        </h1>
        <p className="page-subtitle">
          Crie imagens incríveis com Gemini 2.5 Flash Image (Nano Banana)
        </p>
      </div>

      <div className="generator-container">
        {/* Prompt Editor */}
        <Card className="prompt-card">
          <CardHeader>
            <CardTitle>
              <Wand2 className="w-5 h-5 mr-2" />
              Editor de Prompt
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Descreva a imagem que você quer gerar... Seja específico e detalhado!"
              rows={6}
              className="prompt-textarea"
            />
            
            <div className="quick-actions">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setPrompt(prompt + ' with cinematic lighting and dramatic atmosphere')}
              >
                <Lightbulb className="w-4 h-4 mr-1" />
                + Iluminação
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setPrompt(prompt + ', hyper-realistic, 8K quality, ultra-detailed')}
              >
                <Sparkles className="w-4 h-4 mr-1" />
                + Qualidade
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setPrompt(prompt + ' in anime style with vibrant colors')}
              >
                Estilo Anime
              </Button>
            </div>

            <Button
              onClick={generateImage}
              disabled={loading || !prompt.trim()}
              className="generate-button"
              size="lg"
            >
              {loading ? (
                <>
                  <Sparkles className="w-5 h-5 mr-2 animate-spin" />
                  Gerando...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  Gerar Imagem
                </>
              )}
            </Button>

            <p className="cost-info">
              💰 Custo: $0.039 por imagem (~R$ 0,20)
            </p>
          </CardContent>
        </Card>

        {/* Prompt Library */}
        <Card className="library-card">
          <CardHeader>
            <CardTitle>
              <Lightbulb className="w-5 h-5 mr-2" />
              Biblioteca de Prompts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="category-selector">
              <Button
                variant={selectedCategory === 'realistic' ? 'default' : 'outline'}
                onClick={() => setSelectedCategory('realistic')}
                size="sm"
              >
                Realista
              </Button>
              <Button
                variant={selectedCategory === 'anime' ? 'default' : 'outline'}
                onClick={() => setSelectedCategory('anime')}
                size="sm"
              >
                Anime
              </Button>
              <Button
                variant={selectedCategory === 'editing' ? 'default' : 'outline'}
                onClick={() => setSelectedCategory('editing')}
                size="sm"
              >
                Edição
              </Button>
            </div>

            <div className="prompt-templates">
              {PROMPT_LIBRARY[selectedCategory].map((template, index) => (
                <div key={index} className="prompt-template">
                  <h4>{template.title}</h4>
                  <p>{template.prompt}</p>
                  <Button
                    size="sm"
                    onClick={() => usePromptTemplate(template.prompt)}
                  >
                    Usar Este Prompt
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Generated Image Preview */}
      {generatedImage && (
        <Card className="result-card">
          <CardHeader>
            <CardTitle>Imagem Gerada</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="generated-image-container">
              <img
                src={generatedImage.image_url}
                alt="Generated"
                className="generated-image"
              />
              <div className="image-actions">
                <Button onClick={() => downloadImage(generatedImage.image_url, generatedImage.image_id)}>
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
                <Button onClick={() => useForVideo(generatedImage.image_url)}>
                  <Video className="w-4 h-4 mr-2" />
                  Gerar Vídeo
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => deleteImage(generatedImage.image_id)}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Deletar
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Image History */}
      {imageHistory.length > 0 && (
        <Card className="history-card">
          <CardHeader>
            <CardTitle>Galeria de Imagens Geradas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="image-grid">
              {imageHistory.map((img) => (
                <div key={img.id} className="history-image-item">
                  <img src={img.image_url} alt={img.prompt} />
                  <div className="history-image-overlay">
                    <p className="history-prompt">{img.prompt.substring(0, 60)}...</p>
                    <div className="history-actions">
                      <Button size="sm" onClick={() => useForVideo(img.image_url)}>
                        <Video className="w-3 h-3" />
                      </Button>
                      <Button size="sm" onClick={() => downloadImage(img.image_url, img.id)}>
                        <Download className="w-3 h-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => deleteImage(img.id)}
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default ImageGeneratorPage;
