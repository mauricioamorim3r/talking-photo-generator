import { useState } from 'react';
import { Lock, DollarSign, TrendingUp, Activity, ArrowLeft } from 'lucide-react';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import '../styles/AdminPanel.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminPanel = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [usageData, setUsageData] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/verify`, {
        password: password
      });

      if (response.data.success) {
        setIsAuthenticated(true);
        toast.success('Acesso concedido!');
        fetchUsageData();
      }
    } catch (error) {
      console.error('Error verifying password:', error);
      toast.error('Senha incorreta');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsageData = async () => {
    try {
      const response = await axios.get(`${API}/tokens/usage`);
      if (response.data.success) {
        setUsageData(response.data);
      }
    } catch (error) {
      console.error('Error fetching usage data:', error);
      toast.error('Erro ao carregar dados de uso');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="admin-login">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="login-card-wrapper"
        >
          <Card className="login-card" data-testid="login-card">
            <CardHeader>
              <div className="login-icon">
                <Lock className="w-12 h-12" />
              </div>
              <CardTitle>Painel Administrativo</CardTitle>
              <CardDescription>
                Digite a senha para acessar o painel de controle
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLogin} className="login-form">
                <Input
                  type="password"
                  placeholder="Digite a senha"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  data-testid="password-input"
                />
                <Button 
                  type="submit" 
                  className="w-full" 
                  disabled={loading || !password}
                  data-testid="login-button"
                >
                  {loading ? 'Verificando...' : 'Entrar'}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  className="w-full"
                  onClick={() => window.location.href = '/'}
                  data-testid="back-to-home-button"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Voltar para Home
                </Button>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="admin-panel">
      <header className="admin-header">
        <div className="container">
          <h1>Painel Administrativo</h1>
          <Button variant="outline" onClick={() => window.location.href = '/'} data-testid="back-button">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar
          </Button>
        </div>
      </header>

      <main className="admin-content">
        <div className="container">
          <div className="stats-grid">
            {/* Total Spent Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card className="stat-card" data-testid="total-spent-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Total Gasto
                  </CardTitle>
                  <DollarSign className="h-4 w-4 text-red-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold" data-testid="total-spent-value">
                    ${usageData?.total_spent?.toFixed(2) || '0.00'}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Todas as operações
                  </p>
                </CardContent>
              </Card>
            </motion.div>

            {/* FAL.AI Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="stat-card" data-testid="fal-cost-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    FAL.AI (Vídeos)
                  </CardTitle>
                  <TrendingUp className="h-4 w-4 text-purple-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold" data-testid="fal-cost-value">
                    ${usageData?.by_service?.fal_ai?.toFixed(2) || '0.00'}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Geração de vídeos
                  </p>
                </CardContent>
              </Card>
            </motion.div>

            {/* ElevenLabs Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card className="stat-card" data-testid="elevenlabs-cost-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    ElevenLabs (Áudios)
                  </CardTitle>
                  <Activity className="h-4 w-4 text-blue-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold" data-testid="elevenlabs-cost-value">
                    ${usageData?.by_service?.elevenlabs?.toFixed(2) || '0.00'}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Geração de áudios
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Recent Operations */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-8"
          >
            <Card data-testid="recent-operations-card">
              <CardHeader>
                <CardTitle>Operações Recentes</CardTitle>
                <CardDescription>
                  Últimas 10 operações realizadas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="operations-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Serviço</th>
                        <th>Operação</th>
                        <th>Custo</th>
                        <th>Data</th>
                      </tr>
                    </thead>
                    <tbody>
                      {usageData?.recent_operations?.map((op, index) => (
                        <tr key={index} data-testid={`operation-row-${index}`}>
                          <td>
                            <span className="service-badge">{op.service}</span>
                          </td>
                          <td>{op.operation}</td>
                          <td className="cost-cell">${op.cost?.toFixed(2)}</td>
                          <td className="date-cell">
                            {new Date(op.timestamp).toLocaleString('pt-BR')}
                          </td>
                        </tr>
                      ))}
                      {(!usageData?.recent_operations || usageData.recent_operations.length === 0) && (
                        <tr>
                          <td colSpan="4" className="text-center text-gray-500 py-8">
                            Nenhuma operação registrada ainda
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* API Keys Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-8"
          >
            <Card>
              <CardHeader>
                <CardTitle>Chaves de API</CardTitle>
                <CardDescription>
                  Gerencie as chaves de API utilizadas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="api-keys-info">
                  <p className="text-gray-600">
                    As chaves de API estão configuradas no servidor. Para alterar, entre em contato com o administrador do sistema.
                  </p>
                  <div className="mt-4 space-y-2">
                    <div className="key-item">
                      <span className="key-label">FAL.AI:</span>
                      <span className="key-status">Ativa</span>
                    </div>
                    <div className="key-item">
                      <span className="key-label">ElevenLabs:</span>
                      <span className="key-status">Ativa</span>
                    </div>
                    <div className="key-item">
                      <span className="key-label">Gemini:</span>
                      <span className="key-status">Ativa</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </main>
    </div>
  );
};

export default AdminPanel;