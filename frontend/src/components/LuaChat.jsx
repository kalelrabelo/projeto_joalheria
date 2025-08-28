import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, Upload, X, Minimize2, Maximize2, CheckCircle, AlertCircle, Clock, Zap, Download } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { useModal } from '@/contexts/ModalContext'; // Importar useModal
import FuncionariosModal from './modals/FuncionariosModal';
import VendasModal from './modals/VendasModal';
import EncomendasLuaModal from './modals/EncomendasLuaModal';
import ValesLuaModal from './modals/ValesLuaModal';
import EnergiaModal from './modals/EnergiaModal';

const LuaChatEnhanced = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  
  // Estados para todos os modais
  const [funcionariosModalOpen, setFuncionariosModalOpen] = useState(false);
  const [showFuncionariosModal, setShowFuncionariosModal] = useState(false);
  const [funcionariosData, setFuncionariosData] = useState([]);
  
  const [vendasModalOpen, setVendasModalOpen] = useState(false);
  const [showVendasModal, setShowVendasModal] = useState(false);
  const [vendasData, setVendasData] = useState([]);
  
  const [encomendasModalOpen, setEncomendasModalOpen] = useState(false);
  const [showEncomendasModal, setShowEncomendasModal] = useState(false);
  const [encomendasData, setEncomendasData] = useState([]);
  
  const [valesModalOpen, setValesModalOpen] = useState(false);
  const [showValesModal, setShowValesModal] = useState(false);
  const [valesData, setValesData] = useState([]);
  
  const [energiaModalOpen, setEnergiaModalOpen] = useState(false);
  const [showEnergiaModal, setShowEnergiaModal] = useState(false);
  const [energiaData, setEnergiaData] = useState({});
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const { openModal } = useModal(); // Usar o hook useModal

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Listener para eventos de modal do VoiceAssistant
    const handleOpenModal = (event) => {
      const { tipo, data, response } = event.detail;
      console.log('🔍 DEBUG - Evento de modal recebido:', { tipo, data, response });
      
      if (tipo === 'funcionarios') {
        setFuncionariosData(data);
        setShowFuncionariosModal(true);
      } else if (tipo === 'vendas') {
        setVendasData(data);
        setShowVendasModal(true);
      } else if (tipo === 'vales') {
        setValesData(data);
        setShowValesModal(true);
      } else if (tipo === 'encomendas') {
        setEncomendasData(data);
        setShowEncomendasModal(true);
      } else if (tipo === 'energia') {
        setEnergiaData(data);
        setShowEnergiaModal(true);
      }
    };

    // Listener para processar resposta da Lua via VoiceAssistant
    const handleProcessLuaResponse = (event) => {
      const { data, inputMessage } = event.detail;
      console.log('🔍 DEBUG - Processando resposta da Lua via voz:', data);
      
      // Usar EXATAMENTE a mesma lógica do chat
      if (data.show_in_interface && data.data) {
        console.log('✅ DEBUG - Condição atendida: show_in_interface=true e data existe');
        
        // NÃO ABRIR O CHAT - Modal deve aparecer direto na tela principal
        // setIsOpen(true);
        // setIsMinimized(false);
        
        // Abrir modal automaticamente baseado no tipo de dados
        if (data.tipo === 'funcionarios') {
          console.log('🧑‍💼 DEBUG - Abrindo modal de funcionários:', data.data);
          setFuncionariosData(data.data);
          setShowFuncionariosModal(true);
        } else if (data.tipo === 'encomendas') {
          console.log('📦 DEBUG - Abrindo modal de encomendas:', data.data);
          setEncomendasData(data.data);
          setShowEncomendasModal(true);
        } else if (data.tipo === 'vendas') {
          console.log('💰 DEBUG - Abrindo modal de vendas:', data.data);
          setVendasData(data.data);
          setShowVendasModal(true);
        } else if (data.tipo === 'vales') {
          console.log('💳 DEBUG - Abrindo modal de vales:', data.data);
          setValesData(data.data);
          setShowValesModal(true);
        } else if (data.tipo === 'energia') {
          console.log('⚡ DEBUG - Abrindo modal de energia:', data.data);
          setEnergiaData(data.data);
          setShowEnergiaModal(true);
        }
      }
    };

    window.addEventListener('openLuaModal', handleOpenModal);
    window.addEventListener('processLuaResponse', handleProcessLuaResponse);
    
    return () => {
      window.removeEventListener('openLuaModal', handleOpenModal);
      window.removeEventListener('processLuaResponse', handleProcessLuaResponse);
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getMessageIcon = (type, status) => {
    if (status === 'success') return <CheckCircle className="h-4 w-4 text-white" />;
    if (status === 'error') return <AlertCircle className="h-4 w-4 text-white" />;
    if (type === 'command') return <Zap className="h-4 w-4 text-white" />;
    return null;
  };

  const getMessageBadge = (type, status) => {
    if (status === 'success') return <Badge className="bg-green-700 text-white text-xs">✅ Executado</Badge>;
    if (status === 'error') return <Badge className="bg-red-700 text-white text-xs">❌ Erro</Badge>;
    if (type === 'command') return <Badge className="bg-blue-700 text-white text-xs">⚡ Comando</Badge>;
    return null;
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

  const downloadFile = (url, filename) => {
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
        // Upload de arquivo
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        response = await fetch('http://localhost:5000/api/lua_enhanced/upload', {
          method: 'POST',
          body: formData
        });
      } else {
        // Mensagem de chat normal ou comando
        console.log('🚀 DEBUG - Enviando requisição para:', messageType === 'command' ? '/api/lua_enhanced/chat' : '/api/lua/chat');
        console.log('🚀 DEBUG - Mensagem:', inputMessage);
        
        if (messageType === 'command') {
          // Comando específico
          response = await fetch("/api/lua_enhanced/chat", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              message: inputMessage,
              command: inputMessage
            })
          });
        } else {
          // Mensagem de chat normal
          response = await fetch("/api/lua/chat", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: inputMessage })
          });
        }
      }

      console.log('🔍 DEBUG - Status da resposta:', response.status);
      console.log('🔍 DEBUG - Response OK:', response.ok);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // DEBUG: Log completo da resposta
      console.log('🔍 DEBUG - Resposta completa da Lua:', data);
      console.log('🔍 DEBUG - show_in_interface:', data.show_in_interface);
      console.log('🔍 DEBUG - tipo:', data.tipo);
      console.log('🔍 DEBUG - data:', data.data);
      
      // Lógica para abrir modal de vales
      if (inputMessage.toLowerCase().includes('últimos vales da semana') || inputMessage.toLowerCase().includes('ultimos vales da semana')) {
        openModal('vale', data.data); // Assumindo que data.data contém os dados dos vales
      }

      // Lógica para abrir modal de encomendas
      if (inputMessage.toLowerCase().includes('encomendas de hoje') || inputMessage.toLowerCase().includes('encomendas de alguma data específica')) {
        openModal('encomendas', data.data); // Assumindo que data.data contém os dados das encomendas
      }

      // Lógica para abrir modal de inventário
      if (inputMessage.toLowerCase().includes('inventário') || inputMessage.toLowerCase().includes('inventario') || inputMessage.toLowerCase().includes('estoque')) {
        openModal('inventory', data.data); // Assumindo que data.data contém os dados do inventário
      }

      // Lógica para abrir modal de vendas
      if (inputMessage.toLowerCase().includes('vendas')) {
        openModal('sales', data.data); // Assumindo que data.data contém os dados das vendas
      }

      // Lógica para abrir modal de histórico de PDFs
      if (inputMessage.toLowerCase().includes('histórico de pdfs') || inputMessage.toLowerCase().includes('historico de pdfs') || inputMessage.toLowerCase().includes('últimos pdfs') || inputMessage.toLowerCase().includes('ultimos pdfs')) {
        openModal('pdfHistory', data.data); // Assumindo que data.data contém os dados do histórico de PDFs
      }

      // Verificar se um relatório foi gerado e fazer download automático
      if (data.download_url) {
        try {
          // Fazer download do PDF automaticamente
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
          
          // Adicionar informação de download na mensagem
          data.response = (data.response || data.message) + " ✅ PDF baixado automaticamente para sua pasta Downloads!";
        } catch (downloadError) {
          console.error('Erro ao baixar relatório:', downloadError);
          data.response = (data.response || data.message) + " ⚠️ Erro ao baixar PDF automaticamente.";
        }
      }
      
      // Verificar se a Lua IA retornou dados para exibir na interface
      if (data.show_in_interface && data.data) {
        console.log('✅ DEBUG - Condição atendida: show_in_interface=true e data existe');
        
        // Abrir modal automaticamente baseado no tipo de dados
        if (data.tipo === 'funcionarios') {
          console.log('🧑‍💼 DEBUG - Abrindo modal de funcionários:', data.data);
          setFuncionariosData(data.data);
          setShowFuncionariosModal(true);
        } else if (data.tipo === 'encomendas') {
          console.log('📦 DEBUG - Abrindo modal de encomendas:', data.data);
          setEncomendasData(data.data);
          setShowEncomendasModal(true);
        } else if (data.tipo === 'vendas') {
          console.log('💰 DEBUG - Abrindo modal de vendas:', data.data);
          setVendasData(data.data);
          setShowVendasModal(true);
        } else if (data.tipo === 'vales') {
          console.log('💳 DEBUG - Abrindo modal de vales:', data.data);
          setValesData(data.data);
          setShowValesModal(true);
        } else if (data.tipo === 'energia') {
          console.log('⚡ DEBUG - Abrindo modal de energia:', data.data);
          setEnergiaData(data.data);
          setShowEnergiaModal(true);
        } else if (data.tipo === 'estoque') {
          console.log('📊 DEBUG - Abrindo modal de estoque:', data.data);
          // Usar modal existente do sistema
          openModal('inventory', data.data);
        } else {
          console.log('❓ DEBUG - Tipo não reconhecido:', data.tipo);
        }
      } else {
        console.log('❌ DEBUG - Condição NÃO atendida:');
        console.log('   - show_in_interface:', data.show_in_interface);
        console.log('   - data existe:', !!data.data);
      }

      const luaMessage = {
        id: Date.now() + 1,
        text: data.message || data.response || "Resposta recebida com sucesso!",
        sender: "lua",
        timestamp: new Date().toLocaleTimeString(),
        data: data.data || data.processing_result || data,
        status: data.status || 'success',
        type: messageType === 'command' ? 'command_response' : 'chat_response',
        downloadUrl: data.download_url || null,
        filename: data.filename || null,
        showData: data.show_in_interface || false,
        dataType: data.tipo || null
      };

      setMessages(prev => [...prev, luaMessage]);
      setSelectedFile(null);
      
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: "❌ Desculpe, ocorreu um erro ao processar sua solicitação. Verifique se o servidor está rodando na porta 5000 e tente novamente.",
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
    "Gera relatório de caixa e baixa no meu computador",
    "Adiciona vale para João de R$300 e imprime", 
    "Registra vale para Maria de R$500 e gera PDF",
    "Mostra relatório financeiro mensal",
    "Relatório de estoque com download",
    "Gera relatório de funcionários",
    "Lista vendas do mês",
    "Calcula energia mensal",
    "Mostra histórico de PDFs"
  ];

  const handleQuickCommand = (command) => {
    setInputMessage(command);
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-20 right-6 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          className="h-14 w-14 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg animate-pulse"
        >
          <MessageCircle className="h-6 w-6 text-white" />
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-20 right-6 z-50">
      <Card className={`w-96 bg-gray-900 border-gray-700 shadow-xl transition-all duration-300 ${isMinimized ? 'h-16' : 'h-[500px]'}`}>
        <CardHeader className="flex flex-row items-center justify-between p-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white rounded-t-lg">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Lua
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
              <p className="text-xs text-gray-400 mb-2">⚡ Comandos rápidos com PDF:</p>
              <div className="flex flex-wrap gap-1">
                {quickCommands.map((command, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    size="sm"
                    onClick={() => handleQuickCommand(command)}
                    className="text-xs text-blue-400 hover:text-white hover:bg-gradient-to-r hover:from-blue-600 hover:to-orange-600 p-1 h-6"
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
                    className={`max-w-[70%] p-3 rounded-xl shadow-md ${
                      message.sender === 'user'
                        ? 'bg-blue-500 text-white rounded-br-none ml-auto'
                        : message.status === 'error'
                        ? 'bg-red-500 text-white rounded-bl-none'
                        : message.status === 'success'
                        ? 'bg-green-500 text-white rounded-bl-none'
                        : 'bg-gray-700 text-gray-100 rounded-bl-none'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {getMessageIcon(message.type, message.status)}
                      <div className="flex-1">
                        <p className="text-sm whitespace-pre-line">{message.text}</p>
                        {message.file && (
                          <p className="text-xs mt-1 opacity-75">📎 {message.file.name}</p>
                        )}
                        {message.downloadUrl && (
                          <div className="mt-2">
                            <Button
                              size="sm"
                              onClick={() => {
                                const filename = message.downloadUrl.split('/').pop();
                                downloadFile(message.downloadUrl, filename);
                              }}
                              className="bg-green-600 hover:bg-green-700 text-white text-xs flex items-center gap-1"
                            >
                              <Download className="h-3 w-3" />
                              Baixar PDF
                            </Button>
                          </div>
                        )}
                        {message.data && message.data.analysis && (
                          <div className="text-xs mt-2 opacity-75 bg-black bg-opacity-20 p-2 rounded">
                            <p>📊 Análise: {JSON.stringify(message.data.analysis, null, 2).substring(0, 100)}...</p>
                          </div>
                        )}
                        {message.data && message.data.funcionario && (
                          <div className="text-xs mt-2 opacity-90 bg-black bg-opacity-20 p-2 rounded">
                            <p>👤 Funcionário: {message.data.funcionario}</p>
                            {message.data.valor && !isNaN(message.data.valor) && <p>💰 Valor: R$ {message.data.valor}</p>}
                            {message.data.horas && !isNaN(message.data.horas) && <p>⏰ Horas: {message.data.horas}h</p>}
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
                  <div className="bg-gradient-to-r from-gray-700 to-gray-600 text-gray-100 p-3 rounded-lg flex items-center gap-2">
                    <Clock className="h-4 w-4 animate-spin" />
                    <p className="text-sm">🤖 Lua está processando e gerando PDF...</p>
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
                  placeholder={selectedFile ? "Adicione uma mensagem para o arquivo..." : "Converse com a Lua..."}
                  className="flex-1 bg-gray-800 border-gray-700 text-white placeholder-gray-400"
                  disabled={isLoading}
                />
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => fileInputRef.current.click()}
                  className="bg-gray-800 border-gray-700 text-white hover:bg-gray-700"
                  disabled={isLoading}
                >
                  <Upload className="h-4 w-4" />
                </Button>
                <Button
                  type="submit"
                  size="icon"
                  onClick={sendMessage}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                  disabled={isLoading}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        )}
      </Card>
      
      {/* Modal de Funcionários */}
      <FuncionariosModal
        isOpen={showFuncionariosModal}
        onClose={() => setShowFuncionariosModal(false)}
        funcionarios={funcionariosData}
      />
      
      {/* Modal de Vendas */}
      <VendasModal
        isOpen={showVendasModal}
        onClose={() => setShowVendasModal(false)}
        vendas={vendasData}
      />
      
      {/* Modal de Encomendas */}
      <EncomendasLuaModal
        isOpen={showEncomendasModal}
        onClose={() => setShowEncomendasModal(false)}
        encomendas={encomendasData}
      />
      
      {/* Modal de Vales */}
      <ValesLuaModal
        isOpen={showValesModal}
        onClose={() => setShowValesModal(false)}
        vales={valesData}
      />
      
      {/* Modal de Energia */}
      <EnergiaModal
        isOpen={showEnergiaModal}
        onClose={() => setShowEnergiaModal(false)}
        energiaData={energiaData}
      />
    </div>
  );
};

export default LuaChatEnhanced;

