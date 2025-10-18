import { useState, useEffect } from 'react';
import { Trash2, Download, Video, Music, Image as ImageIcon, ArrowLeft, Play, Loader2 } from 'lucide-react';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import '../styles/GalleryPage.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const GalleryPage = () => {
  const [loading, setLoading] = useState(true);
  const [videos, setVideos] = useState([]);
  const [audios, setAudios] = useState([]);
  const [images, setImages] = useState([]);
  const [selectedTab, setSelectedTab] = useState('videos');

  useEffect(() => {
    fetchGalleryItems();
  }, []);

  const fetchGalleryItems = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/gallery/items`);
      if (response.data.success) {
        setVideos(response.data.videos || []);
        setAudios(response.data.audios || []);
        setImages(response.data.images || []);
      }
    } catch (error) {
      console.error('Error fetching gallery items:', error);
      toast.error('Erro ao carregar galeria');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (type, id) => {
    if (!window.confirm('Tem certeza que deseja deletar este item?')) {
      return;
    }

    try {
      await axios.delete(`${API}/gallery/${type}/${id}`);
      toast.success('Item deletado com sucesso!');
      fetchGalleryItems();
    } catch (error) {
      console.error('Error deleting item:', error);
      toast.error('Erro ao deletar item');
    }
  };

  const handleDownload = async (url, filename) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      toast.success('Download iniciado!');
    } catch (error) {
      console.error('Error downloading:', error);
      toast.error('Erro ao fazer download');
    }
  };

  return (
    <div className="gallery-page">
      {/* Header */}
      <header className="gallery-header">
        <div className="container">
          <motion.div 
            className="header-content"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Button 
              variant="ghost" 
              onClick={() => window.location.href = '/'}
              data-testid="back-button"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Voltar
            </Button>
            <h1>Minha Galeria</h1>
          </motion.div>
        </div>
      </header>

      {/* Main Content */}
      <main className="gallery-content">
        <div className="container">
          <Tabs value={selectedTab} onValueChange={setSelectedTab} className="gallery-tabs">
            <TabsList className="gallery-tabs-list">
              <TabsTrigger value="videos" data-testid="videos-tab">
                <Video className="w-4 h-4 mr-2" />
                Vídeos ({videos.length})
              </TabsTrigger>
              <TabsTrigger value="audios" data-testid="audios-tab">
                <Music className="w-4 h-4 mr-2" />
                Áudios ({audios.length})
              </TabsTrigger>
              <TabsTrigger value="images" data-testid="images-tab">
                <ImageIcon className="w-4 h-4 mr-2" />
                Imagens ({images.length})
              </TabsTrigger>
            </TabsList>

            {/* Videos Tab */}
            <TabsContent value="videos">
              {loading ? (
                <div className="loading-state">
                  <Loader2 className="w-12 h-12 animate-spin text-purple-500" />
                  <p>Carregando vídeos...</p>
                </div>
              ) : videos.length === 0 ? (
                <div className="empty-state" data-testid="empty-videos">
                  <Video className="w-16 h-16 text-gray-300" />
                  <h3>Nenhum vídeo gerado ainda</h3>
                  <p>Seus vídeos gerados aparecerão aqui</p>
                  <Button onClick={() => window.location.href = '/'}>Gerar Primeiro Vídeo</Button>
                </div>
              ) : (
                <div className="gallery-grid">
                  {videos.map((video, index) => (
                    <motion.div
                      key={video.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Card className="gallery-card" data-testid={`video-card-${index}`}>
                        <CardHeader>
                          <div className="card-header-content">
                            <div>
                              <CardTitle className="text-sm">
                                {video.model?.toUpperCase()} - {video.mode === 'economico' ? '🆓 Grátis' : '👑 Premium'}
                              </CardTitle>
                              <CardDescription>
                                {new Date(video.timestamp).toLocaleDateString('pt-BR')}
                              </CardDescription>
                            </div>
                            <div className="card-actions">
                              <Button
                                size="icon"
                                variant="ghost"
                                onClick={() => handleDownload(video.result_url, `video-${video.id}.mp4`)}
                                data-testid={`download-video-${index}`}
                              >
                                <Download className="w-4 h-4" />
                              </Button>
                              <Button
                                size="icon"
                                variant="ghost"
                                onClick={() => handleDelete('video', video.id)}
                                data-testid={`delete-video-${index}`}
                              >
                                <Trash2 className="w-4 h-4 text-red-500" />
                              </Button>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="video-preview">
                            <video src={video.result_url} controls className="preview-media" />
                          </div>
                          <div className="video-info">
                            <p className="prompt-text">{video.prompt}</p>
                            <div className="video-meta">
                              <span>Duração: {video.duration}s</span>
                              {video.mode === 'premium' && video.cost > 0 && (
                                <span className="cost-badge">Custo: ${video.cost.toFixed(2)}</span>
                              )}
                              {video.mode === 'economico' && (
                                <span className="free-badge">GRÁTIS</span>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Audios Tab */}
            <TabsContent value="audios">
              {loading ? (
                <div className="loading-state">
                  <Loader2 className="w-12 h-12 animate-spin text-purple-500" />
                  <p>Carregando áudios...</p>
                </div>
              ) : audios.length === 0 ? (
                <div className="empty-state" data-testid="empty-audios">
                  <Music className="w-16 h-16 text-gray-300" />
                  <h3>Nenhum áudio gerado ainda</h3>
                  <p>Seus áudios gerados aparecerão aqui</p>
                </div>
              ) : (
                <div className="gallery-grid">
                  {audios.map((audio, index) => (
                    <motion.div
                      key={audio.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Card className="gallery-card audio-card" data-testid={`audio-card-${index}`}>
                        <CardHeader>
                          <div className="card-header-content">
                            <div>
                              <CardTitle className="text-sm">Áudio Gerado</CardTitle>
                              <CardDescription>
                                {new Date(audio.timestamp).toLocaleDateString('pt-BR')}
                              </CardDescription>
                            </div>
                            <div className="card-actions">
                              <Button
                                size="icon"
                                variant="ghost"
                                onClick={() => handleDownload(audio.audio_url, `audio-${audio.id}.mp3`)}
                                data-testid={`download-audio-${index}`}
                              >
                                <Download className="w-4 h-4" />
                              </Button>
                              <Button
                                size="icon"
                                variant="ghost"
                                onClick={() => handleDelete('audio', audio.id)}
                                data-testid={`delete-audio-${index}`}
                              >
                                <Trash2 className="w-4 h-4 text-red-500" />
                              </Button>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <audio src={audio.audio_url} controls className="audio-player" />
                          {audio.text && (
                            <p className="audio-text">{audio.text}</p>
                          )}
                          <div className="audio-meta">
                            {audio.duration && <span>Duração: {audio.duration.toFixed(1)}s</span>}
                            {audio.cost > 0 && (
                              <span className="cost-badge">Custo: ${audio.cost.toFixed(2)}</span>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Images Tab */}
            <TabsContent value="images">
              {loading ? (
                <div className="loading-state">
                  <Loader2 className="w-12 h-12 animate-spin text-purple-500" />
                  <p>Carregando imagens...</p>
                </div>
              ) : images.length === 0 ? (
                <div className="empty-state" data-testid="empty-images">
                  <ImageIcon className="w-16 h-16 text-gray-300" />
                  <h3>Nenhuma imagem analisada ainda</h3>
                  <p>Suas imagens analisadas aparecerão aqui</p>
                </div>
              ) : (
                <div className="gallery-grid">
                  {images.map((image, index) => {
                    let analysisData = {};
                    try {
                      analysisData = JSON.parse(image.analysis);
                    } catch (e) {
                      analysisData = {};
                    }
                    
                    return (
                      <motion.div
                        key={image.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <Card className="gallery-card image-card" data-testid={`image-card-${index}`}>
                          <CardHeader>
                            <div className="card-header-content">
                              <div>
                                <CardTitle className="text-sm">Imagem Analisada</CardTitle>
                                <CardDescription>
                                  {new Date(image.timestamp).toLocaleDateString('pt-BR')}
                                </CardDescription>
                              </div>
                              <div className="card-actions">
                                <Button
                                  size="icon"
                                  variant="ghost"
                                  onClick={() => handleDelete('image', image.id)}
                                  data-testid={`delete-image-${index}`}
                                >
                                  <Trash2 className="w-4 h-4 text-red-500" />
                                </Button>
                              </div>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <img src={image.image_url} alt="Analyzed" className="preview-media" />
                            {analysisData.description && (
                              <div className="image-analysis">
                                <p><strong>Descrição:</strong> {analysisData.description}</p>
                                <p><strong>Tipo:</strong> {analysisData.subject_type}</p>
                                {analysisData.recommended_model_premium && (
                                  <p><strong>Modelo Sugerido:</strong> {analysisData.recommended_model_premium.toUpperCase()}</p>
                                )}
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      </motion.div>
                    );
                  })}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
};

export default GalleryPage;