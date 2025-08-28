import React, { useState, useRef, useEffect } from 'react';
import { 
  MessageCircle, Send, Upload, X, Minimize2, Maximize2, 
  CheckCircle, AlertCircle, Clock, Zap, Download, Brain, 
  BarChart3, TrendingUp, Users, Package, DollarSign, 
  Lightbulb, Target, Activity
} from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Progress } from '@/components/ui/progress.jsx';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx';
import { useModal } from '@/contexts/ModalContext';

const LuaSuperChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');
  const [conversationSummary, setConversationSummary] = useState(null);
  const [capabilities, setCapabilities] = useState(null);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const { openModal } = useModal();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !capabilities) {
      fetchCapabilities();
    }
  }, [isOpen]);

  const fetchCapabilities = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/lua_super/capabilities');
      if (response.ok) {
        const data = await response.json();
        setCapabilities(data);
      }
    } catch (error) {
      console.error('Erro ao buscar capacidades:', error);
    }
  };

  const fetchConversationSummary = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/lua_super/conversation_summary');
      if (response.ok) {
        const data = await response.json();
        setConversationSummary(data);
      }
    } catch (error) {
      console.error('Erro ao buscar resumo da conversa:', error);
    }
  };

  const resetConversation = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/lua_super/reset_conversation', {
        method: 'POST'
      });
      if (response.ok) {
        const data = await response.json();
        setMessages([{
          id: Date.now(),
          text: data.message,
          sender: "lua",
          timestamp: new Date().toLocaleTimeString(),
          type: 'system_message'
        }]);
        setConversationSummary(null);
      }
    } catch (error) {
      console.error('Erro ao resetar conversa:', error);
    }
  };

  const getMessageIcon = (type, status) => {
    if (status === 'success') return <CheckCircle className="h-4 w-4 text-white" />;
    if (status === 'error') return <AlertCircle className="h-4 w-4 text-white" />;
    if (type === 'advanced_analysis') return <Brain className="h-4 w-4 text-white" />;
    if (type === 'command') return <Zap className="h-4 w-4 text-white" />;
    return <MessageCircle className="h-4 w-4 text-white" />;
  };

  const getMessageBadge = (type, status) => {
    if (status === 'success') return <Badge className="bg-green-700 text-white text-xs">✅ Executado</Badge>;
    if (status === 'error') return <Badge className="bg-red-700 text-white text-xs">❌ Erro</Badge>;
    if (type === 'advanced_analysis') return <Badge className="bg-purple-700 text-white text-xs">🧠 Análise IA</Badge>;
    if (type === 'command') return <Badge className="bg-blue-700 text-white text-xs">⚡ Comando</Badge>;
    return null;
  };

  const isAdvancedAnalysisRequest = (message) => {
    const analysisKeywords = [
      'análise', 'analise', 'tendência', 'tendencia', 'previsão', 'previsao',
      'insights', 'recomendações', 'recomendacoes', 'inteligência', 'inteligencia',
      'padrões', 'padroes', 'otimização', 'otimizacao', 'performance',
      'comportamento', 'forecasting', 'business intelligence', 'bi'
    ];
    return analysisKeywords.some(keyword => message.toLowerCase().includes(keyword));
  };

  const isCommand = (message) => {
    const commandKeywords = [
      'adiciona', 'registra', 'cria', 'vale', 'viagem', 'horas', 'trabalho',
      'relatório', 'relatorio', 'mostra', 'altera', 'atualiza', 'configura',
      'energia', 'calcula', 'importa', 'consulta', 'lista', 'estoque',
      'funcionário', 'funcionario', 'vendas', 'financeiro', 'custo', 'lucro',
      'histórico', 'historico', 'alertas', 'produção', 'producao', 'imprime', 'imprimir',
      'gera', 'baixa', 'download', 'pdf'
    ];
    return commandKeywords.some(keyword => message.toLowerCase().includes(keyword));
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() && !selectedFile) return;

    const messageType = isAdvancedAnalysisRequest(inputMessage) ? 'advanced_analysis' : 
                       isCommand(inputMessage) ? 'command' : 'chat';
    
    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: "user",
      timestamp: new Date().toLocaleTimeString(),
      file: selectedFile,
      type: messageType
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      let response;
      
      if (messageType === 'advanced_analysis') {
        // Análise avançada
        response = await fetch("/api/lua_super/advanced_analysis", {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            analysis_request: currentInput,
            parameters: {}
          })
        });
      } else {
        // Chat normal ou comando
        response = await fetch("/api/lua_super/chat", {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: currentInput,
            context: {},
            is_followup: false
          })
        });
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      console.log('🔍 DEBUG - Resposta da LUA Super:', data);
      
      // Verificar se um relatório foi gerado e fazer download automático
      if (data.download_url) {
        try {
          const downloadResponse = await fetch(`http://localhost:5000${data.download_url}`);
          const blob = await downloadResponse.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          a.download = data.filename || 'relatorio.pdf';
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          
          data.message += " ✅ PDF baixado automaticamente!";
        } catch (downloadError) {
          console.error('Erro ao baixar relatório:', downloadError);
          data.message += " ⚠️ Erro ao baixar PDF automaticamente.";
        }
      }
      
      // Verificar se deve abrir modal
      if (data.show_in_interface && data.data) {
        if (data.tipo === 'funcionarios') {
          openModal('funcionarios', data.data);
        } else if (data.tipo === 'encomendas') {
          openModal('encomendas', data.data);
        } else if (data.tipo === 'vendas') {
          openModal('sales', data.data);
        } else if (data.tipo === 'vales') {
          openModal('vale', data.data);
        } else if (data.tipo === 'estoque') {
          openModal('inventory', data.data);
        }
      }

      const luaMessage = {
        id: Date.now() + 1,
        text: data.message || "Resposta processada com sucesso!",
        sender: "lua",
        timestamp: new Date().toLocaleTimeString(),
        data: data.data || data,
        status: data.status || 'success',
        type: messageType === 'advanced_analysis' ? 'advanced_analysis_response' : 
              messageType === 'command' ? 'command_response' : 'chat_response',
        downloadUrl: data.download_url || null,
        filename: data.filename || null,
        showData: data.show_in_interface || false,
        dataType: data.tipo || null,
        // Dados específicos de análise avançada
        analysisType: data.analysis_type,
        insights: data.insights,
        recommendations: data.recommendations,
        predictions: data.predictions,
        confidenceScore: data.confidence_score,
        dataQuality: data.data_quality,
        executiveSummary: data.executive_summary
      };

      setMessages(prev => [...prev, luaMessage]);
      setSelectedFile(null);
      
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: "❌ Desculpe, ocorreu um erro ao processar sua solicitação. Verifique se o servidor está rodando e tente novamente.",
        sender: "lua",
        timestamp: new Date().toLocaleTimeString(),
        status: 'error',
        type: 'error_response'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const quickCommands = [
    "Análise financeira avançada com insights e previsões",
    "Análise de performance dos funcionários",
    "Otimização de inventário com recomendações",
    "Previsão de vendas para próximo mês",
    "Análise de padrões de custos",
    "Comportamento de clientes e retenção",
    "Gera relatório de caixa e baixa PDF",
    "Adiciona vale para João de R$300",
    "Mostra estoque com alertas"
  ];

  const handleQuickCommand = (command) => {
    setInputMessage(command);
  };

  const renderAdvancedAnalysisResult = (message) => {
    if (message.type !== 'advanced_analysis_response' || !message.insights) {
      return null;
    }

    return (
      <div className="mt-4 space-y-4">
        {/* Cabeçalho da análise */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-400" />
            <span className="font-semibold text-purple-400">
              Análise: {message.analysisType?.replace('_', ' ')}
            </span>
          </div>
          {message.confidenceScore && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">Confiança:</span>
              <Progress 
                value={message.confidenceScore * 100} 
                className="w-16 h-2"
              />
              <span className="text-xs text-gray-400">
                {(message.confidenceScore * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>

        {/* Resumo executivo */}
        {message.executiveSummary && (
          <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 p-4 rounded-lg border border-purple-500/30">
            <div className="flex items-center gap-2 mb-2">
              <Target className="h-4 w-4 text-purple-400" />
              <span className="font-medium text-purple-400">Resumo Executivo</span>
            </div>
            <p className="text-sm text-gray-300 leading-relaxed">
              {message.executiveSummary}
            </p>
          </div>
        )}

        {/* Insights */}
        {message.insights && message.insights.length > 0 && (
          <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-500/30">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="h-4 w-4 text-blue-400" />
              <span className="font-medium text-blue-400">Insights</span>
            </div>
            <ul className="space-y-2">
              {message.insights.map((insight, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-300">
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 flex-shrink-0" />
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Recomendações */}
        {message.recommendations && message.recommendations.length > 0 && (
          <div className="bg-green-900/20 p-4 rounded-lg border border-green-500/30">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="h-4 w-4 text-green-400" />
              <span className="font-medium text-green-400">Recomendações</span>
            </div>
            <ul className="space-y-2">
              {message.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-300">
                  <div className="w-1.5 h-1.5 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Previsões */}
        {message.predictions && Object.keys(message.predictions).length > 0 && (
          <div className="bg-orange-900/20 p-4 rounded-lg border border-orange-500/30">
            <div className="flex items-center gap-2 mb-3">
              <BarChart3 className="h-4 w-4 text-orange-400" />
              <span className="font-medium text-orange-400">Previsões</span>
            </div>
            <div className="grid grid-cols-1 gap-2">
              {Object.entries(message.predictions).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center text-sm">
                  <span className="text-gray-400 capitalize">
                    {key.replace('_', ' ')}:
                  </span>
                  <span className="text-orange-300 font-medium">
                    {typeof value === 'number' && key.includes('valor') ? 
                      `R$ ${value.toFixed(2)}` : 
                      String(value)
                    }
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Qualidade dos dados */}
        {message.dataQuality && (
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Qualidade dos dados: {message.dataQuality}</span>
            <span>Processado por: LUA Super Inteligente</span>
          </div>
        )}
      </div>
    );
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-20 right-6 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          className="h-16 w-16 rounded-full bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 hover:from-purple-700 hover:via-blue-700 hover:to-cyan-700 shadow-xl animate-pulse"
        >
          <div className="flex flex-col items-center">
            <Brain className="h-6 w-6 text-white mb-1" />
            <span className="text-xs text-white font-bold">LUA</span>
          </div>
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-20 right-6 z-50">
      <Card className={`w-[480px] bg-gray-900 border-gray-700 shadow-2xl transition-all duration-300 ${isMinimized ? 'h-16' : 'h-[600px]'}`}>
        <CardHeader className="flex flex-row items-center justify-between p-4 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 text-white rounded-t-lg">
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <Brain className="h-6 w-6" />
            LUA Super Inteligente
            <Badge className="bg-white/20 text-white text-xs">v2.0</Badge>
          </CardTitle>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMinimized(!isMinimized)}
              className="text-white hover:bg-white/20"
            >
              {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-white/20"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        {!isMinimized && (
          <CardContent className="p-0 h-[536px] flex flex-col">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
              <TabsList className="grid w-full grid-cols-3 bg-gray-800 m-2">
                <TabsTrigger value="chat" className="text-xs">Chat IA</TabsTrigger>
                <TabsTrigger value="analytics" className="text-xs">Analytics</TabsTrigger>
                <TabsTrigger value="info" className="text-xs">Info</TabsTrigger>
              </TabsList>

              <TabsContent value="chat" className="flex-1 flex flex-col p-2 pt-0">
                {/* Área de mensagens */}
                <div className="flex-1 overflow-y-auto space-y-3 p-2 bg-gray-800 rounded-lg mb-3">
                  {messages.length === 0 && (
                    <div className="text-center text-gray-400 py-8">
                      <Brain className="h-12 w-12 mx-auto mb-4 text-purple-400" />
                      <p className="text-lg font-semibold mb-2">Olá! Sou a LUA Super Inteligente</p>
                      <p className="text-sm">
                        Agora com IA avançada, análise preditiva e capacidades de raciocínio.
                        <br />Posso entender qualquer comando e nunca direi "comando não reconhecido"!
                      </p>
                    </div>
                  )}

                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] p-3 rounded-lg ${
                          message.sender === 'user'
                            ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                            : message.status === 'error'
                            ? 'bg-red-900/50 border border-red-500/50 text-red-200'
                            : 'bg-gray-700 text-gray-100'
                        }`}
                      >
                        <div className="flex items-start gap-2 mb-1">
                          {message.sender === 'lua' && getMessageIcon(message.type, message.status)}
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs opacity-75">{message.timestamp}</span>
                              {getMessageBadge(message.type, message.status)}
                            </div>
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                            
                            {/* Renderizar resultado de análise avançada */}
                            {renderAdvancedAnalysisResult(message)}
                            
                            {message.file && (
                              <div className="mt-2 p-2 bg-black/20 rounded text-xs">
                                📎 {message.file.name}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-700 p-3 rounded-lg flex items-center gap-2">
                        <Activity className="h-4 w-4 animate-spin text-purple-400" />
                        <span className="text-sm text-gray-300">LUA está processando...</span>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Comandos rápidos */}
                <div className="mb-3">
                  <div className="text-xs text-gray-400 mb-2">Comandos sugeridos:</div>
                  <div className="flex flex-wrap gap-1">
                    {quickCommands.slice(0, 3).map((command, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickCommand(command)}
                        className="text-xs h-6 px-2 bg-gray-800 border-gray-600 hover:bg-gray-700 text-gray-300"
                      >
                        {command.length > 30 ? command.substring(0, 30) + '...' : command}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Área de input */}
                <div className="space-y-2">
                  {selectedFile && (
                    <div className="flex items-center gap-2 p-2 bg-gray-800 rounded-lg">
                      <span className="text-sm text-gray-300">📎 {selectedFile.name}</span>
                      <Button variant="ghost" size="sm" onClick={removeFile}>
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Digite qualquer comando ou pergunta..."
                      className="flex-1 bg-gray-800 border-gray-600 text-white placeholder-gray-400"
                      disabled={isLoading}
                    />
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileSelect}
                      className="hidden"
                      accept=".csv,.xlsx,.xls,.pdf,.docx"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-gray-800 border-gray-600 hover:bg-gray-700"
                      disabled={isLoading}
                    >
                      <Upload className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={sendMessage}
                      disabled={isLoading || (!inputMessage.trim() && !selectedFile)}
                      className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="analytics" className="flex-1 p-4 space-y-4">
                <div className="text-center">
                  <Button
                    onClick={fetchConversationSummary}
                    className="mb-4 bg-gradient-to-r from-purple-600 to-blue-600"
                  >
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Atualizar Analytics
                  </Button>
                </div>

                {conversationSummary && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <Card className="bg-gray-800 border-gray-700">
                        <CardContent className="p-4">
                          <div className="text-2xl font-bold text-purple-400">
                            {conversationSummary.total_interactions}
                          </div>
                          <div className="text-sm text-gray-400">Total de Interações</div>
                        </CardContent>
                      </Card>
                      
                      <Card className="bg-gray-800 border-gray-700">
                        <CardContent className="p-4">
                          <div className="text-2xl font-bold text-green-400">
                            {(conversationSummary.success_rate * 100).toFixed(1)}%
                          </div>
                          <div className="text-sm text-gray-400">Taxa de Sucesso</div>
                        </CardContent>
                      </Card>
                    </div>

                    {conversationSummary.recent_topics && (
                      <Card className="bg-gray-800 border-gray-700">
                        <CardContent className="p-4">
                          <h4 className="font-semibold mb-2 text-blue-400">Tópicos Recentes</h4>
                          <div className="flex flex-wrap gap-2">
                            {conversationSummary.recent_topics.map((topic, index) => (
                              <Badge key={index} className="bg-blue-600 text-white">
                                {topic.replace('_', ' ')}
                              </Badge>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="info" className="flex-1 p-4 space-y-4">
                <div className="space-y-4">
                  <Card className="bg-gray-800 border-gray-700">
                    <CardContent className="p-4">
                      <h4 className="font-semibold mb-2 text-purple-400 flex items-center gap-2">
                        <Brain className="h-4 w-4" />
                        Capacidades da IA
                      </h4>
                      {capabilities && capabilities.ai_features && (
                        <ul className="space-y-1 text-sm text-gray-300">
                          {capabilities.ai_features.map((feature, index) => (
                            <li key={index} className="flex items-center gap-2">
                              <CheckCircle className="h-3 w-3 text-green-400" />
                              {feature}
                            </li>
                          ))}
                        </ul>
                      )}
                    </CardContent>
                  </Card>

                  <Card className="bg-gray-800 border-gray-700">
                    <CardContent className="p-4">
                      <h4 className="font-semibold mb-2 text-blue-400">Ações Suportadas</h4>
                      {capabilities && capabilities.supported_actions && (
                        <div className="flex flex-wrap gap-1">
                          {capabilities.supported_actions.map((action, index) => (
                            <Badge key={index} className="bg-blue-600 text-white text-xs">
                              {action.replace('_', ' ')}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  <div className="flex gap-2">
                    <Button
                      onClick={resetConversation}
                      variant="outline"
                      className="flex-1 bg-gray-800 border-gray-600 hover:bg-gray-700"
                    >
                      🔄 Resetar Conversa
                    </Button>
                  </div>

                  <div className="text-center text-xs text-gray-500">
                    LUA Super Inteligente v2.0
                    <br />
                    Powered by OpenAI GPT & Advanced Analytics
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        )}
      </Card>
    </div>
  );
};

export default LuaSuperChat;

