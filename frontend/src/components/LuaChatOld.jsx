import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, Upload, X, Minimize2, Maximize2, CheckCircle, AlertCircle, Clock, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';

const LuaChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Olá! Sou a Lua, sua assistente de IA especializada na Joalheria Antonio Rabelo. Agora posso executar comandos diretos em TODOS os módulos! Experimente:\n\n• 'Lua, adiciona um vale para João de R$500'\n• 'Lua, registra um vale de 300 reais para o funcionário Rodrigo e imprime para mim'\n• 'Registra uma viagem para Pedro, hotel R$1.200'\n• 'Adiciona 5 horas de trabalho do funcionário Maria'\n• 'Mostra relatório financeiro mensal'\n• 'Calcula energia mensal'\n• 'Importa conta de energia' (com upload)\n• 'Consulta estoque de materiais'\n• 'Lista funcionários'\n• 'Mostra vendas do mês'\n\nTambém posso processar arquivos de energia (PDF, CSV, XLSX), manter contexto das nossas conversas e imprimir comprovantes de vales!",
      sender: "lua",
      timestamp: new Date().toLocaleTimeString(),
      type: "welcome"
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getMessageIcon = (type, status) => {
    if (status === 'success') return <CheckCircle className="h-4 w-4 text-green-400" />;
    if (status === 'error') return <AlertCircle className="h-4 w-4 text-red-400" />;
    if (type === 'command') return <Zap className="h-4 w-4 text-blue-400" />;
    return null;
  };

  const getMessageBadge = (type, status) => {
    if (status === 'success') return <Badge className="bg-green-600 text-white text-xs">Executado</Badge>;
    if (status === 'error') return <Badge className="bg-red-600 text-white text-xs">Erro</Badge>;
    if (type === 'command') return <Badge className="bg-blue-600 text-white text-xs">Comando</Badge>;
    return null;
  };

  const isCommand = (message) => {
    const commandKeywords = [
      'adiciona', 'registra', 'cria', 'vale', 'viagem', 'horas', 'trabalho',
      'relatório', 'relatorio', 'mostra', 'altera', 'atualiza', 'configura',
      'energia', 'calcula', 'importa', 'consulta', 'lista', 'estoque',
      'funcionário', 'funcionario', 'vendas', 'financeiro', 'custo', 'lucro',
      'histórico', 'historico', 'alertas', 'produção', 'producao', 'imprime', 'imprimir'
    ];
    return commandKeywords.some(keyword => message.toLowerCase().includes(keyword));
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() && !selectedFile) return;

    const messageType = isCommand(inputMessage) ? 'command' : 'chat';
    
    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: "user",
      timestamp: new Date().toLocaleTimeString(),
      file: selectedFile,
      type: messageType
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      let response;
      
      if (selectedFile) {
        // Verificar se é arquivo de energia
        const fileName = selectedFile.name.toLowerCase();
        const isEnergyFile = fileName.includes('energia') || fileName.includes('luz') || 
                           fileName.includes('energy') || fileName.includes('conta');
        
        if (isEnergyFile || inputMessage.toLowerCase().includes('energia')) {
          // Upload de arquivo de energia
          const formData = new FormData();
          formData.append('file', selectedFile);
          
          response = await fetch('http://localhost:5000/api/lua/energy/upload', {
            method: 'POST',
            body: formData
          });
        } else {
          // Upload de arquivo normal
          const formData = new FormData();
          formData.append('file', selectedFile);
          
          response = await fetch('http://localhost:5000/api/lua/upload', {
            method: 'POST',
            body: formData
          });
        }
      } else if (messageType === 'command') {
        // Comando direto para execução com contexto
        const sessionId = localStorage.getItem('lua_session_id') || 
                         `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('lua_session_id', sessionId);
        
        response = await fetch('http://localhost:5000/api/lua/enhanced', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            command: inputMessage,
            session_id: sessionId
          })
        });
      } else {
        // Mensagem de chat normal
        response = await fetch('http://localhost:5000/api/lua/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: inputMessage })
        });
      }

      const data = await response.json();
      
      // Verificar se um relatório foi gerado e fazer download automático
      if (data.report_generated && data.download_url) {
        try {
          // Fazer download do PDF automaticamente
          const downloadResponse = await fetch(`http://localhost:5000/api${data.download_url}`);
          if (downloadResponse.ok) {
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
            
            // Adicionar informação de download na mensagem
            data.response = data.response + " ✅ PDF baixado automaticamente!";
          }
        } catch (downloadError) {
          console.error('Erro ao baixar relatório:', downloadError);
          data.response = data.response + " ⚠️ Erro ao baixar PDF automaticamente.";
        }
      }
      
      const luaMessage = {
        id: Date.now() + 1,
        text: data.message || data.response || "Resposta recebida com sucesso!",
        sender: "lua",
        timestamp: new Date().toLocaleTimeString(),
        data: data.processing_result || data.data || data,
        status: data.status || 'success',
        type: messageType === 'command' ? 'command_response' : 'chat_response',
        downloadUrl: data.download_url || null,
        filename: data.filename || null
      };

      setMessages(prev => [...prev, luaMessage]);
      setSelectedFile(null);
      
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: "Desculpe, ocorreu um erro ao processar sua solicitação. Verifique se o servidor está rodando e tente novamente.",
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
    "Mostra relatório financeiro",
    "Adiciona vale para João de R$300", 
    "Registra vale para Maria de R$500 e imprime",
    "Registra viagem para Pedro",
    "Relatório de estoque",
    "Calcula energia mensal",
    "Lista funcionários",
    "Consulta vendas do mês",
    "Histórico de energia"
  ];

  const handleQuickCommand = (command) => {
    setInputMessage(command);
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          className="h-14 w-14 rounded-full bg-blue-600 hover:bg-blue-700 shadow-lg animate-pulse"
        >
          <MessageCircle className="h-6 w-6 text-white" />
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Card className={`w-96 bg-gray-900 border-gray-700 shadow-xl transition-all duration-300 ${isMinimized ? 'h-16' : 'h-[500px]'}`}>
        <CardHeader className="flex flex-row items-center justify-between p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Lua - IA Assistant
            <Badge className="bg-green-500 text-white text-xs animate-pulse">Online</Badge>
          </CardTitle>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMinimized(!isMinimized)}
              className="text-white hover:bg-blue-700 p-1"
            >
              {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-blue-700 p-1"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        {!isMinimized && (
          <CardContent className="p-0 flex flex-col h-[436px]">
            {/* Comandos rápidos */}
            <div className="p-3 bg-gray-800 border-b border-gray-700">
              <p className="text-xs text-gray-400 mb-2">Comandos rápidos:</p>
              <div className="flex flex-wrap gap-1">
                {quickCommands.map((command, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    size="sm"
                    onClick={() => handleQuickCommand(command)}
                    className="text-xs text-blue-400 hover:text-white hover:bg-blue-600 p-1 h-6"
                  >
                    {command}
                  </Button>
                ))}
              </div>
            </div>

            {/* Área de mensagens */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs p-3 rounded-lg ${
                      message.sender === 'user'
                        ? message.type === 'command'
                          ? 'bg-blue-600 text-white border-l-4 border-yellow-400'
                          : 'bg-blue-600 text-white'
                        : message.status === 'error'
                        ? 'bg-red-600 text-white'
                        : message.status === 'success'
                        ? 'bg-green-700 text-white'
                        : 'bg-gray-700 text-gray-100'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {getMessageIcon(message.type, message.status)}
                      <div className="flex-1">
                        <p className="text-sm whitespace-pre-line">{message.text}</p>
                        {message.file && (
                          <p className="text-xs mt-1 opacity-75">📎 {message.file.name}</p>
                        )}
                        {message.data && message.data.analysis && (
                          <div className="text-xs mt-2 opacity-75 bg-black bg-opacity-20 p-2 rounded">
                            <p>📊 Análise: {JSON.stringify(message.data.analysis, null, 2).substring(0, 100)}...</p>
                          </div>
                        )}
                        {message.data && message.data.funcionario && (
                          <div className="text-xs mt-2 opacity-90 bg-black bg-opacity-20 p-2 rounded">
                            <p>👤 Funcionário: {message.data.funcionario}</p>
                            {message.data.valor && <p>💰 Valor: R$ {message.data.valor}</p>}
                            {message.data.horas && <p>⏰ Horas: {message.data.horas}h</p>}
                          </div>
                        )}
                        {message.downloadUrl && message.filename && (
                          <div className="text-xs mt-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                const link = document.createElement('a');
                                link.href = `http://localhost:5000/api${message.downloadUrl}`;
                                link.download = message.filename;
                                link.click();
                              }}
                              className="text-blue-300 hover:text-white hover:bg-blue-600 p-1 h-6 text-xs"
                            >
                              📄 Baixar {message.filename}
                            </Button>
                          </div>
                        )}
                        <div className="flex items-center justify-between mt-1">
                          <p className="text-xs opacity-75">{message.timestamp}</p>
                          {getMessageBadge(message.type, message.status)}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-700 text-gray-100 p-3 rounded-lg flex items-center gap-2">
                    <Clock className="h-4 w-4 animate-spin" />
                    <p className="text-sm">Lua está processando...</p>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Área de input */}
            <div className="p-4 border-t border-gray-700">
              {selectedFile && (
                <div className="mb-2 p-2 bg-gray-800 rounded-lg flex items-center justify-between">
                  <span className="text-sm text-gray-300">📎 {selectedFile.name}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={removeFile}
                    className="text-gray-400 hover:text-white p-1"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
              
              <div className="flex gap-2">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Digite um comando ou mensagem..."
                  className="flex-1 bg-gray-800 border-gray-600 text-white placeholder-gray-400"
                  disabled={isLoading}
                />
                
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  accept=".csv,.xlsx,.xls,.pdf,.docx"
                  className="hidden"
                />
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-gray-400 hover:text-white"
                  disabled={isLoading}
                >
                  <Upload className="h-4 w-4" />
                </Button>
                
                <Button
                  onClick={sendMessage}
                  disabled={isLoading || (!inputMessage.trim() && !selectedFile)}
                  className={`${isCommand(inputMessage) ? 'bg-yellow-600 hover:bg-yellow-700' : 'bg-blue-600 hover:bg-blue-700'}`}
                >
                  {isCommand(inputMessage) ? <Zap className="h-4 w-4" /> : <Send className="h-4 w-4" />}
                </Button>
              </div>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  );
};

export default LuaChat;

