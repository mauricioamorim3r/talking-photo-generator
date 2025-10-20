import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Sparkles, Image as ImageIcon, Download, Trash2, Video, Lightbulb, Wand2, Grid, Upload, X } from 'lucide-react';
import './ImageGeneratorPage.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const PROMPT_LIBRARY = {
  avatares: [
    { title: "Retrato em Pixel Art", prompt: "Transforme este retrato em um avatar de videogame de 16-bits, estilo pixel art, com uma caixa de diálogo abaixo." },
    { title: "Viagem no Tempo Anos 80", prompt: "Recrie esta foto como se tivesse sido tirada nos anos 80, com estética de filme Kodachrome, roupas e cabelo da época." },
    { title: "Terapia Criança Interior", prompt: "Crie uma cena onde eu (adulto) estou abraçando carinhosamente minha versão de 8 anos. Estilo fotografia emocional, com luz suave." },
    { title: "Companheiro Assustador", prompt: "Adicione ao meu lado um pequeno monstro amigável, no estilo dos filmes de Tim Burton." },
    { title: "Retrato a Lápis", prompt: "Recrie este retrato como um desenho a lápis de grafite hiper-realista em um caderno de esboços." },
    { title: "Retrato em Aquarela", prompt: "Transforme este retrato em uma pintura de aquarela, com pinceladas visíveis e cores suaves." },
    { title: "Transformar em Sticker", prompt: "Transforme-me em um sticker (adesivo) de vinil, com um contorno branco grosso e acabamento brilhante. Fundo transparente." },
    { title: "Avatar Funko Pop", prompt: "Transforme-me em um boneco colecionável Funko Pop, com olhos grandes e redondos, dentro de uma caixa personalizada." },
    { title: "Foto LinkedIn Profissional", prompt: "Transforme esta imagem em um headshot corporativo profissional, com fundo de escritório desfocado e iluminação de estúdio." },
    { title: "Capa de Revista Vogue", prompt: "Transforme este retrato na capa de uma revista de moda como a Vogue, com título, manchetes e pose de alta costura." },
    { title: "Retrato Histórico Vitoriano", prompt: "Recrie meu retrato como se eu fosse uma figura da nobreza vitoriana, com traje e penteado da época." },
    { title: "Silhueta Dramática", prompt: "Crie uma silhueta minha contra um pôr do sol dramático, com o contorno bem definido." },
    { title: "Caricatura Divertida", prompt: "Transforme este retrato em uma caricatura divertida, exagerando características marcantes com estilo de desenho cômico." },
    { title: "Retrato Claymation", prompt: "Transforme meu retrato em um boneco de argila (claymation), no estilo do estúdio Aardman." }
  ],
  
  estilos: [
    { title: "Efeito Pop Art Warhol", prompt: "Aplique um efeito de Pop Art a este retrato, no estilo de Andy Warhol, com cores vibrantes e contrastantes." },
    { title: "Mosaico de Azulejos", prompt: "Transforme esta imagem em um mosaico de azulejos coloridos, mantendo a forma principal reconhecível." },
    { title: "Dupla Exposição", prompt: "Crie um efeito de dupla exposição, mesclando meu retrato com uma paisagem de montanhas." },
    { title: "Pôster Minimalista", prompt: "Transforme esta imagem em um pôster de filme minimalista, usando apenas formas geométricas e 3 cores." },
    { title: "Efeito Steampunk", prompt: "Adicione elementos steampunk a este retrato: engrenagens, óculos de aviador, detalhes em cobre e latão." },
    { title: "Arte Ukiyo-e Japonesa", prompt: "Recrie esta cena no estilo de uma gravura japonesa Ukiyo-e, com traços de xilogravura e cores chapadas." },
    { title: "Videogame Retrô", prompt: "Transforme esta cena em um videogame de aventura dos anos 90, com gráficos pixelados (pixel art)." },
    { title: "Painel de Quadrinhos", prompt: "Transforme esta imagem em um painel de história em quadrinhos, com contornos pretos e balões de diálogo." },
    { title: "Arte com Colagem", prompt: "Crie uma colagem digital usando este retrato, misturado com recortes de jornais e elementos botânicos." },
    { title: "Arte de Linha Minimalista", prompt: "Extraia as linhas principais e transforme em line art minimalista, com um único traço contínuo." },
    { title: "Pintura Impressionista Monet", prompt: "Transforme esta paisagem em pintura impressionista, estilo Monet, com pinceladas curtas visíveis." },
    { title: "Arte Cubista Picasso", prompt: "Desconstrua este retrato em formas geométricas e múltiplos pontos de vista, estilo cubismo de Picasso." },
    { title: "Vitral de Igreja Gótica", prompt: "Transforme esta imagem em um vitral de igreja gótica, com contornos de chumbo e vidro colorido translúcido." }
  ],
  
  design: [
    { title: "Design de Camiseta", prompt: "Crie uma estampa para camiseta com design minimalista e gráfico. A estampa deve ser centralizada, fundo transparente." },
    { title: "Capa de Álbum Musical", prompt: "Crie a capa de um álbum de música com estilo visual psicodélico dos anos 70, cores vibrantes." },
    { title: "Logotipo Moderno", prompt: "Crie 5 opções de logotipo moderno, minimalista e elegante para uma marca." },
    { title: "Ícone de Aplicativo", prompt: "Desenvolva um ícone de aplicativo simples, reconhecível e funcional em tamanhos pequenos." },
    { title: "Design de Embalagem Luxuosa", prompt: "Crie design de embalagem para produto gourmet. Estilo luxuoso e minimalista." },
    { title: "Food Photography", prompt: "Fotografia profissional de hambúrguer artesanal em fundo de madeira rústica, iluminação de estúdio. Estilo food porn." },
    { title: "Cartão de Visitas", prompt: "Crie design de cartão de visitas clean e profissional, com espaços para informações de contato." },
    { title: "Design de Tatuagem Blackwork", prompt: "Crie um design de tatuagem em estilo blackwork com traços claros, para ser usado como referência." },
    { title: "Emoji Personalizado iOS", prompt: "Crie um emoji personalizado no estilo dos emojis padrão do iOS, com contornos suaves e cores vibrantes." },
    { title: "Ícones para Infográfico", prompt: "Crie um conjunto de 5 ícones vetoriais em estilo flat design para infográfico." },
    { title: "Mascote Estilo Pixar", prompt: "Crie um mascote amigável e carismático, no estilo de ilustração 3D da Pixar." },
    { title: "Thumbnail YouTube", prompt: "Crie uma thumbnail com alto contraste, cores chamativas e elemento de curiosidade para vídeo do YouTube." }
  ],
  
  manipulacao: [
    { title: "Colorir Foto P&B", prompt: "Colorize esta foto em preto e branco com cores realistas e historicamente apropriadas." },
    { title: "Remover Objeto", prompt: "Remova o objeto selecionado desta imagem e reconstrua o fundo de forma natural." },
    { title: "Mudar Fundo - Praia", prompt: "Mantenha a pessoa intacta, mas troque o fundo por uma praia ao pôr do sol." },
    { title: "Restaurar Foto Antiga", prompt: "Restaure esta foto antiga e danificada, removendo rasgos, manchas e corrigindo cores desbotadas." },
    { title: "Estender Imagem (Outpainting)", prompt: "Expanda as bordas desta imagem, completando o cenário de forma realista em todas as direções." },
    { title: "Adicionar Textura de Papel", prompt: "Aplique uma textura de papel amassado sobre esta imagem, com modo de mesclagem overlay." },
    { title: "Mudar Cor dos Olhos", prompt: "Mantenha todo o resto, mas mude a cor dos olhos da pessoa para azul safira." },
    { title: "Mudar Cor do Cabelo", prompt: "Mantenha todo o resto, mas mude a cor do cabelo da pessoa para loiro platinado." },
    { title: "Criar Reflexo na Água", prompt: "Adicione um reflexo realista desta cena em uma superfície de água calma abaixo dela." },
    { title: "Filtro Cinematográfico", prompt: "Aplique um filtro de gradação de cor cinematográfico, com o estilo teal and orange." },
    { title: "Corrigir Foto Borrada", prompt: "Melhore a nitidez e corrija o leve desfoque de movimento nesta imagem." },
    { title: "Mudar para Golden Hour", prompt: "Altere a iluminação desta cena de luz do meio-dia para luz do fim da tarde (golden hour)." },
    { title: "Progressão de Idade", prompt: "Recrie esta imagem, mas me mostre como eu serei com 60 anos de idade." }
  ],
  
  mundos: [
    { title: "Cenário Cyberpunk Noturno", prompt: "Crie paisagem urbana cyberpunk à noite, com chuva, arranha-céus gigantes, carros voadores e letreiros de neon." },
    { title: "Paisagem de Fantasia", prompt: "Crie paisagem de reino de fantasia, com castelos flutuantes, cachoeiras que desafiam gravidade e duas luas no céu." },
    { title: "Roma Antiga Fotorrealista", prompt: "Recrie a cidade de Roma Antiga no seu auge, em 3D fotorrealista, baseado em reconstruções históricas." },
    { title: "Design de Interiores Escandinavo", prompt: "Crie mockup de sala de estar no estilo escandinavo, com móveis e decoração minimalista." },
    { title: "Paisagem Surrealista Dalí", prompt: "Crie paisagem de sonho no estilo de Salvador Dalí, com relógios derretendo em uma praia deserta." },
    { title: "Mundo em Miniatura Tilt-Shift", prompt: "Fotografia de cidade movimentada com efeito tilt-shift, fazendo tudo parecer um mundo em miniatura." },
    { title: "Comida como Paisagem", prompt: "Crie paisagem onde montanhas são de pão, rios de chocolate e árvores de brócolis." },
    { title: "Planeta Alienígena", prompt: "Crie paisagem de planeta alienígena, com flora bioluminescente, céu roxo e formações rochosas exóticas." },
    { title: "Nova York Pós-Apocalíptica", prompt: "Crie cenário de Nova York pós-apocalíptica, com natureza retomando prédios abandonados em ruínas." },
    { title: "Mapa de Tesouro Pirata", prompt: "Desenhe mapa de tesouro pirata em estilo de pergaminho antigo, com ilustrações e caligrafia." },
    { title: "Cidade Subaquática", prompt: "Crie imagem de cidade futurista subaquática, dentro de cúpula de vidro, com peixes e baleias nadando ao redor." },
    { title: "Paisagem National Geographic", prompt: "Fotografia de paisagem das montanhas da Suíça, com qualidade da National Geographic." }
  ],
  
  criativo: [
    { title: "Pet como Personagem Disney", prompt: "Transforme este animal em um personagem no estilo clássico de animação 2D da Disney." },
    { title: "Fusão de Dois Animais", prompt: "Crie uma nova criatura híbrida que seja fusão de um leão com uma águia (grifo)." },
    { title: "Criatura Mítica Realista", prompt: "Crie sua versão de um dragão, com estilo de arte realista e sombrio." },
    { title: "Carro como Transformer", prompt: "Transforme este carro em um robô Transformer em meio a uma batalha épica." },
    { title: "Objeto em Porcelana Delft", prompt: "Crie um headphone como se fosse feito de porcelana branca com detalhes em pintura azul, estilo cerâmica de Delft." },
    { title: "Híbrido Humano-Raposa", prompt: "Crie retrato de pessoa com características sutis de raposa, com orelhas e cauda, estilo fantasia realista." },
    { title: "Capa da Invisibilidade", prompt: "Aplique efeito de capa da invisibilidade, deixando apenas contorno translúcido e distorcendo o fundo." },
    { title: "Gravidade Invertida", prompt: "Crie cena em sala onde gravidade está invertida, com pessoas e objetos flutuando em direção ao teto." },
    { title: "Pizza como Planeta", prompt: "Transforme esta pizza em um planeta flutuando no espaço, com naves de manjericão e luas de azeitona." },
    { title: "Golem de Pedra Viva", prompt: "Crie imagem de golem feito de pedras de rio, caminhando por uma floresta mística." },
    { title: "Mundo de Origami", prompt: "Recrie esta cena como se tudo fosse feito de dobraduras de papel (origami)." },
    { title: "Esculturas de Nuvens", prompt: "Crie imagem de nuvens no céu que tenham forma de animais e objetos reconhecíveis." },
    { title: "Inseto Mecânico Steampunk", prompt: "Crie uma abelha como organismo mecânico, com engrenagens e peças de metal, estilo steampunk." },
    { title: "Violão como Prédio", prompt: "Transforme este violão em prédio de arquitetura futurista, mantendo suas formas e características." }
  ],
  
  brasileiro: [
    { title: "Retrato no Pelourinho", prompt: "Retrato de mulher baiana com turbante e colares, em frente às casas coloridas do Pelourinho, Salvador. Estilo fotografia documental, cores vibrantes." },
    { title: "Capoeira no Rio", prompt: "Cena de roda de capoeira na praia de Ipanema ao pôr do sol, com Morro Dois Irmãos ao fundo. Captura de movimento, silhuetas dinâmicas." },
    { title: "Releitura Tarsila do Amaral", prompt: "Recrie este retrato no estilo da obra Abaporu de Tarsila do Amaral, mantendo cores e formas do modernismo brasileiro." },
    { title: "Festa Junina", prompt: "Cena de festa junina à noite, com bandeirinhas coloridas, fogueira grande e pessoas dançando quadrilha. Estilo pintura naïf." },
    { title: "Saci Pererê Moderno", prompt: "Crie representação realista e moderna do Saci Pererê, em floresta densa e misteriosa da Mata Atlântica." }
  ]
};

function ImageGeneratorPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [imageHistory, setImageHistory] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('avatares');
  const [referenceImage, setReferenceImage] = useState(null);
  const [referenceImagePreview, setReferenceImagePreview] = useState(null);

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

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error('Por favor, selecione um arquivo de imagem válido');
        return;
      }
      
      setReferenceImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setReferenceImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
      
      toast.success('Imagem de referência carregada!');
    }
  };

  const removeReferenceImage = () => {
    setReferenceImage(null);
    setReferenceImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    toast.info('Imagem de referência removida');
  };

  const generateImage = async () => {
    if (!prompt.trim()) {
      toast.error('Por favor, insira um prompt');
      return;
    }

    setLoading(true);
    try {
      const requestData = {
        prompt: prompt.trim()
      };
      
      // If reference image exists, convert to base64
      if (referenceImage) {
        const reader = new FileReader();
        
        // Wrap FileReader in Promise
        const base64Promise = new Promise((resolve, reject) => {
          reader.onloadend = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsDataURL(referenceImage);
        });
        
        const base64Image = await base64Promise;
        requestData.reference_image_base64 = base64Image;
      }

      const response = await axios.post(`${BACKEND_URL}/api/images/generate`, requestData, {
        headers: {
          'Content-Type': 'application/json',
        },
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
    // If reference image is loaded, add instruction to preserve facial features
    if (referenceImage) {
      const enhancedPrompt = `${template}\n\n⚠️ IMPORTANTE: Manter o rosto e expressões faciais EXATAMENTE como na imagem de referência carregada. Não alterar as feições da pessoa.`;
      setPrompt(enhancedPrompt);
      toast.success('Prompt aplicado com instrução para preservar o rosto da imagem de referência!');
    } else {
      setPrompt(template);
      toast.success('Prompt aplicado! Você pode editá-lo antes de gerar.');
    }
  };

  return (
    <div className="image-generator-page">
      <div className="page-header">
        <div className="navigation-buttons">
          <Button variant="outline" onClick={() => navigate('/')}>
            <Video className="w-4 h-4 mr-2" />
            Vídeos
          </Button>
          <Button variant="outline" onClick={() => navigate('/gallery')}>
            <Grid className="w-4 h-4 mr-2" />
            Galeria
          </Button>
          <Button variant="outline" onClick={() => navigate('/admin')}>
            Admin
          </Button>
        </div>
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
            
            {/* Reference Image Upload */}
            <div className="reference-image-section" style={{ marginTop: '1rem', marginBottom: '1rem' }}>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept="image/*"
                style={{ display: 'none' }}
              />
              
              {!referenceImagePreview ? (
                <Button
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full"
                  type="button"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Carregar Imagem de Referência (Opcional)
                </Button>
              ) : (
                <div style={{ 
                  border: '2px solid #e5e7eb', 
                  borderRadius: '8px', 
                  padding: '1rem',
                  position: 'relative'
                }}>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    marginBottom: '0.5rem'
                  }}>
                    <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>
                      📎 Imagem de Referência
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={removeReferenceImage}
                      type="button"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                  <img
                    src={referenceImagePreview}
                    alt="Reference"
                    style={{
                      width: '100%',
                      maxHeight: '200px',
                      objectFit: 'contain',
                      borderRadius: '4px'
                    }}
                  />
                  <div style={{
                    marginTop: '0.5rem',
                    padding: '0.75rem',
                    backgroundColor: '#fef3c7',
                    border: '1px solid #fbbf24',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem',
                    color: '#78350f'
                  }}>
                    <strong>✨ Imagem de Referência Carregada</strong>
                    <p style={{ margin: '0.25rem 0 0 0' }}>
                      Os prompts da biblioteca preservarão automaticamente o rosto e expressões faciais desta pessoa. Apenas o estilo, cenário ou roupas serão modificados.
                    </p>
                  </div>
                </div>
              )}
            </div>
            
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
              💰 Custo: $0.039 por imagem (~R$ 0,20) - Gemini 2.5 Flash Image
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
                variant={selectedCategory === 'avatares' ? 'default' : 'outline'}
                onClick={() => setSelectedCategory('avatares')}
                size="sm"
              >
                👤 Avatares (14)
              </Button>
              <Button
                variant={selectedCategory === 'estilos' ? 'default' : 'outline'}
                onClick={() => setSelectedCategory('estilos')}
                size="sm"
              >
                🎨 Estilos (13)
              </Button>
              <Button
                variant={selectedCategory === 'design' ? 'default' : 'outline'}
                onClick={() => setSelectedCategory('design')}
                size="sm"
              >
                📐 Design (12)
              </Button>
              <Button
                variant={selectedCategory === 'manipulacao' ? 'default' : 'outline'}
                onClick={() => setSelectedCategory('manipulacao')}
                size="sm"
              >
                ✨ Edição (13)
              </Button>
              <Button
                variant={selectedCategory === 'mundos' ? 'default' : 'outline'}
                onClick={() => setSelectedCategory('mundos')}
                size="sm"
              >
                🌍 Mundos (12)
              </Button>
              <Button
                variant={selectedCategory === 'criativo' ? 'default' : 'outline'}
                onClick={() => setSelectedCategory('criativo')}
                size="sm"
              >
                💡 Criativo (14)
              </Button>
              <Button
                variant={selectedCategory === 'brasileiro' ? 'default' : 'outline'}
                onClick={() => setSelectedCategory('brasileiro')}
                size="sm"
              >
                🇧🇷 Brasil (5)
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
