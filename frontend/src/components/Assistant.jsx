import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import {
  Bot,
  Zap,
  History,
  BarChart3,
  TrendingUp,
  Send,
  CheckCircle,
  AlertCircle,
  Clock,
  DollarSign,
  Receipt,
  Users,
  Calendar,
  Mic
} from 'lucide-react';
import LuaChat from './LuaChat';
import EnergyDashboard from './EnergyDashboard';
import FinanceDashboard from './FinanceDashboard';
import PrinterConfig from './PrinterConfig';
import VoiceAssistant from './VoiceAssistant';
import ValeHistory from './ValeHistory';

const LuaAssistant = () => {
  const [customCommand, setCustomCommand] = useState('');
  const [actionHistory, setActionHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('commands');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    fetchActionHistory();

    if ('webkitSpeechRecognition' in window) {
      recognitionRef.current = new window.webkitSpeechRecognition();
      recognitionRef.current.continuous = false; // Processa um comando por vez
      recognitionRef.current.interimResults = false; // Não mostra resultados provisórios
      recognitionRef.current.lang = 'pt-BR';

      recognitionRef.current.onstart = () => {
        setIsListening(true);
        console.log('Reconhecimento de voz iniciado...');
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        console.log('Reconhecimento de voz finalizado.');
      };

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('Comando de voz recebido:', transcript);
        setCustomCommand(transcript);
        executeCustomCommand(transcript); // Executa o comando imediatamente
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Erro no reconhecimento de voz:', event.error);
        setIsListening(false);
      };
    } else {
      console.warn('Web Speech API não suportada neste navegador.');
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const fetchActionHistory = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/lua/history');
      const data = await response.json();
      
      if (data.status === 'success') {
        setActionHistory(data.actions || []);
      }
    } catch (error) {
      console.error('Erro ao buscar histórico:', error);
    }
  };

  const executeCustomCommand = async (commandTextParam) => {
    const commandText = commandTextParam || customCommand || "";
    if (!commandText.trim()) return;

    setLoading(true);
    try {
      const sessionId = localStorage.getItem('lua_session_id') || 
                       `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('lua_session_id', sessionId);

      const response = await fetch('http://localhost:5000/api/lua/enhanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          command: commandText,
          session_id: sessionId
        })
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        alert(`✅ ${result.message}`);
        fetchActionHistory(); // Atualizar histórico
        setCustomCommand('');
      } else {
        alert(`❌ ${result.message}`);
      }
    } catch (error) {
      alert('❌ Erro ao executar comando');
    } finally {
      setLoading(false);
    }
  };

  const executeQuickCommand = async (command) => {
    setCustomCommand(command);
    await executeCustomCommand(command);
  };

  const quickCommands = [
    {
      title: "Relatório Financeiro",
      command: "mostra resumo financeiro mensal",
      icon: <DollarSign className="h-4 w-4" />,
      color: "bg-green-600"
    },
    {
      title: "Relatório de Estoque", 
      command: "consulta estoque de materiais",
      icon: <BarChart3 className="h-4 w-4" />,
      color: "bg-blue-600"
    },
    {
      title: "Relatório de Funcionários",
      command: "lista funcionários ativos",
      icon: <Users className="h-4 w-4" />,
      color: "bg-purple-600"
    },
    {
      title: "Vale R$300 para João",
      command: "adiciona vale para João de R$300",
      icon: <Receipt className="h-4 w-4" />,
      color: "bg-orange-600"
    },
    {
      title: "Vale + Impressão",
      command: "registra vale para Maria de R$500 e imprime",
      icon: <Receipt className="h-4 w-4" />,
      color: "bg-red-600"
    },
    {
      title: "Análise de Energia",
      command: "calcula energia mensal",
      icon: <Zap className="h-4 w-4" />,
      color: "bg-yellow-600"
    }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-400" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-400" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'success':
        return <Badge className="bg-green-600 text-white">Sucesso</Badge>;
      case 'error':
        return <Badge className="bg-red-600 text-white">Erro</Badge>;
      default:
        return <Badge className="bg-yellow-600 text-white">Processando</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
            <Bot className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Assistente Lua</h1>
            <p className="text-gray-400">Central de comando e monitoramento da IA</p>
          </div>
        </div>
        <Badge className="bg-green-500 text-white animate-pulse">
          Online
        </Badge>
      </div>

      {/* Assistente de Voz */}
      <VoiceAssistant onCommand={executeCustomCommand} />

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-7 bg-gray-800">
          <TabsTrigger value="commands" className="text-white">
            <Zap className="mr-2 h-4 w-4" />
            Comandos
          </TabsTrigger>
          <TabsTrigger value="history" className="text-white">
            <History className="mr-2 h-4 w-4" />
            Histórico
          </TabsTrigger>
          <TabsTrigger value="financial" className="text-white">
            <DollarSign className="mr-2 h-4 w-4" />
            Financeiro
          </TabsTrigger>
          <TabsTrigger value="energy" className="text-white">
            <Zap className="mr-2 h-4 w-4" />
            Energia
          </TabsTrigger>
          <TabsTrigger value="vales" className="text-white">
            <Receipt className="mr-2 h-4 w-4" />
            Vales
          </TabsTrigger>
          <TabsTrigger value="printer" className="text-white">
            <Receipt className="mr-2 h-4 w-4" />
            Impressora
          </TabsTrigger>
          <TabsTrigger value="insights" className="text-white">
            <TrendingUp className="mr-2 h-4 w-4" />
            Insights
          </TabsTrigger>
        </TabsList>

        {/* Tab: Comandos Rápidos */}
        <TabsContent value="commands" className="space-y-6">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Zap className="mr-2 h-5 w-5" />
                Comandos Rápidos
              </CardTitle>
              <CardDescription className="text-gray-400">
                Execute ações comuns com um clique
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {quickCommands.map((cmd, index) => (
                  <Button
                    key={index}
                    onClick={() => executeQuickCommand(cmd.command)}
                    className={`${cmd.color} hover:opacity-80 h-auto p-4 flex flex-col items-start space-y-2`}
                    disabled={loading}
                  >
                    <div className="flex items-center space-x-2">
                      {cmd.icon}
                      <span className="font-semibold">{cmd.title}</span>
                    </div>
                    <span className="text-xs opacity-80 text-left">
                      {cmd.command}
                    </span>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Comando Personalizado */}
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Comando Personalizado</CardTitle>
              <CardDescription className="text-gray-400">
                Digite qualquer comando em linguagem natural
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2">
                <Input
                  placeholder="Digite um comando personalizado..."
                  value={customCommand}
                  onChange={(e) => setCustomCommand(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && executeCustomCommand()}
                  className="bg-gray-700 border-gray-600 text-white"
                />
                <Button 
                  onClick={executeCustomCommand}
                  disabled={loading || !customCommand.trim()}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
                <Button 
                  onClick={() => {
                    if (isListening) {
                      recognitionRef.current.stop();
                    } else {
                      recognitionRef.current.start();
                    }
                  }}
                  disabled={!("webkitSpeechRecognition" in window)}
                  className={isListening ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"}
                >
                  <Mic className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Histórico de Ações */}
        <TabsContent value="history" className="space-y-6">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Histórico de Ações Executadas</CardTitle>
              <CardDescription className="text-gray-400">
                Últimas ações realizadas pela Lua
              </CardDescription>
            </CardHeader>
            <CardContent>
              {actionHistory.length > 0 ? (
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {actionHistory.map((action, index) => (
                    <div key={index} className="p-4 bg-gray-700 rounded-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1">
                          {getStatusIcon(action.result?.status)}
                          <div className="flex-1">
                            <p className="text-white font-medium">
                              {action.command}
                            </p>
                            <p className="text-gray-400 text-sm mt-1">
                              {action.result?.message || 'Comando executado'}
                            </p>
                            <p className="text-gray-500 text-xs mt-2">
                              {new Date(action.timestamp).toLocaleString('pt-BR')}
                            </p>
                          </div>
                        </div>
                        <div className="ml-4">
                          {getStatusBadge(action.result?.status)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <History className="h-12 w-12 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-400">Nenhuma ação executada ainda</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Dashboard Financeiro */}
        <TabsContent value="financial">
          <FinanceDashboard />
        </TabsContent>

        {/* Tab: Dashboard de Energia */}
        <TabsContent value="energy">
          <EnergyDashboard />
        </TabsContent>

        {/* Tab: Histórico de Vales */}
        <TabsContent value="vales">
          <ValeHistory />
        </TabsContent>

        {/* Tab: Configuração de Impressora */}
        <TabsContent value="printer">
          <PrinterConfig />
        </TabsContent>

        {/* Tab: Insights */}
        <TabsContent value="insights" className="space-y-6">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">📊 Insights Estratégicos</CardTitle>
              <CardDescription className="text-gray-400">
                Análises e sugestões baseadas em dados
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-blue-900 border border-blue-700 rounded-lg">
                  <h4 className="font-semibold text-white mb-2">💡 Sugestões da Lua</h4>
                  <ul className="space-y-2 text-blue-100 text-sm">
                    <li>• Monitore o consumo de energia mensalmente para identificar padrões</li>
                    <li>• Analise a distribuição de vales por funcionário para otimizar pagamentos</li>
                    <li>• Compare receitas e despesas para melhorar a margem de lucro</li>
                    <li>• Use comandos de contexto para análises mais eficientes</li>
                  </ul>
                </div>
                
                <div className="p-4 bg-green-900 border border-green-700 rounded-lg">
                  <h4 className="font-semibold text-white mb-2">🎯 Próximos Passos</h4>
                  <ul className="space-y-2 text-green-100 text-sm">
                    <li>• Configure alertas automáticos para variações significativas</li>
                    <li>• Implemente metas mensais de lucro e acompanhe o progresso</li>
                    <li>• Analise tendências sazonais nos dados históricos</li>
                    <li>• Otimize processos baseado nos insights gerados</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Chat da Lua sempre disponível */}
      <LuaChat />
    </div>
  );
};

export default LuaAssistant;

