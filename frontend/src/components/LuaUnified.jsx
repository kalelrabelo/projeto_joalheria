import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Textarea } from './ui/textarea';
import { toast } from 'sonner';
import { 
  Mic, 
  MicOff, 
  Send, 
  Bot, 
  User, 
  Volume2, 
  VolumeX, 
  Settings,
  Loader2,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const LuaUnified = () => {
  // Estados principais
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  // Estados de voz
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);

  // Estados de configuração
  const [showSettings, setShowSettings] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [voiceRate, setVoiceRate] = useState(1);
  const [voicePitch, setVoicePitch] = useState(1);

  // Refs
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);

  // Inicialização
  useEffect(() => {
    initializeSpeech();
    generateSessionId();
  }, []);

  // Auto-scroll para última mensagem
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeSpeech = () => {
    // Verificar suporte a Web Speech API
    const speechRecognitionSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    const speechSynthesisSupported = 'speechSynthesis' in window;
    
    setSpeechSupported(speechRecognitionSupported && speechSynthesisSupported);
    
    if (speechRecognitionSupported) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'pt-BR';
      
      recognitionRef.current.onstart = () => {
        setIsListening(true);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        handleSendMessage(transcript);
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Erro no reconhecimento de voz:', event.error);
        setIsListening(false);
        
        if (event.error === 'not-allowed') {
          toast.error('Permissão de microfone negada. Por favor, permita o acesso ao microfone.');
        } else {
          toast.error('Erro no reconhecimento de voz. Tente novamente.');
        }
      };
    }
    
    if (speechSynthesisSupported) {
      synthRef.current = window.speechSynthesis;
    }
  };

  const generateSessionId = () => {
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (text = inputText) => {
    if (!text.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: text,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/lua_enhanced/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
          user_id: 1 // TODO: Obter do contexto de autenticação
        })
      });

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const data = await response.json();

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: data.response || 'Desculpe, não consegui processar sua solicitação.',
        timestamp: new Date(),
        intent: data.intent,
        confidence: data.confidence,
        metadata: data.metadata
      };

      setMessages(prev => [...prev, aiMessage]);

      // Falar resposta se habilitado
      if (autoSpeak && voiceEnabled && synthRef.current) {
        speakText(aiMessage.content);
      }

      // Mostrar toast de sucesso se necessário
      if (data.success && data.action_performed) {
        toast.success('Ação executada com sucesso!');
      }

    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
      toast.error('Erro ao comunicar com a IA Lua');
    } finally {
      setIsLoading(false);
    }
  };

  const startListening = () => {
    if (!speechSupported) {
      toast.error('Reconhecimento de voz não suportado neste navegador');
      return;
    }

    if (!voiceEnabled) {
      toast.error('Funcionalidade de voz não está habilitada');
      return;
    }

    try {
      recognitionRef.current?.start();
    } catch (error) {
      console.error('Erro ao iniciar reconhecimento:', error);
      toast.error('Erro ao iniciar reconhecimento de voz');
    }
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
  };

  const speakText = (text) => {
    if (!synthRef.current || !voiceEnabled) return;

    // Parar fala anterior
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pt-BR';
    utterance.rate = voiceRate;
    utterance.pitch = voicePitch;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => {
      setIsSpeaking(false);
      toast.error('Erro na síntese de voz');
    };

    synthRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    synthRef.current?.cancel();
    setIsSpeaking(false);
  };

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled);
    if (voiceEnabled) {
      stopSpeaking();
      stopListening();
    }
  };

  const clearChat = () => {
    setMessages([]);
    generateSessionId();
    toast.success('Chat limpo');
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case 'user':
        return <User className="w-4 h-4" />;
      case 'ai':
        return <Bot className="w-4 h-4" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Bot className="w-4 h-4" />;
    }
  };

  const getMessageStyle = (type) => {
    switch (type) {
      case 'user':
        return 'bg-blue-600 text-white ml-auto';
      case 'ai':
        return 'bg-gray-700 text-white mr-auto';
      case 'error':
        return 'bg-red-600 text-white mr-auto';
      default:
        return 'bg-gray-700 text-white mr-auto';
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto p-4">
      <Card className="flex-1 flex flex-col bg-gray-900 border-gray-700">
        <CardHeader className="border-b border-gray-700">
          <div className="flex items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2">
              <Bot className="w-6 h-6 text-blue-400" />
              IA Lua - Assistente Inteligente
            </CardTitle>
            <div className="flex items-center gap-2">
              {speechSupported && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleVoice}
                  className={`${voiceEnabled ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'} border-gray-600`}
                >
                  {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSettings(!showSettings)}
                className="bg-gray-600 hover:bg-gray-700 border-gray-600"
              >
                <Settings className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={clearChat}
                className="bg-gray-600 hover:bg-gray-700 border-gray-600"
              >
                Limpar
              </Button>
            </div>
          </div>
          
          {showSettings && (
            <div className="mt-4 p-4 bg-gray-800 rounded-lg space-y-4">
              <h3 className="text-white font-semibold">Configurações de Voz</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm text-gray-400">Fala Automática</label>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setAutoSpeak(!autoSpeak)}
                    className={`w-full mt-1 ${autoSpeak ? 'bg-green-600' : 'bg-gray-600'}`}
                  >
                    {autoSpeak ? 'Ativada' : 'Desativada'}
                  </Button>
                </div>
                <div>
                  <label className="text-sm text-gray-400">Velocidade: {voiceRate}</label>
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={voiceRate}
                    onChange={(e) => setVoiceRate(parseFloat(e.target.value))}
                    className="w-full mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-400">Tom: {voicePitch}</label>
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={voicePitch}
                    onChange={(e) => setVoicePitch(parseFloat(e.target.value))}
                    className="w-full mt-1"
                  />
                </div>
              </div>
            </div>
          )}
        </CardHeader>

        <CardContent className="flex-1 flex flex-col p-4">
          {/* Área de mensagens */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                <Bot className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                <p>Olá! Sou a IA Lua, sua assistente para o sistema de joalheria.</p>
                <p className="text-sm mt-2">Posso ajudar com consultas sobre estoque, vendas, funcionários e muito mais!</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex items-start gap-3 max-w-[80%] ${
                    message.type === 'user' ? 'ml-auto flex-row-reverse' : ''
                  }`}
                >
                  <div className={`p-2 rounded-full ${
                    message.type === 'user' ? 'bg-blue-600' : 
                    message.type === 'error' ? 'bg-red-600' : 'bg-gray-600'
                  }`}>
                    {getMessageIcon(message.type)}
                  </div>
                  <div className={`p-3 rounded-lg ${getMessageStyle(message.type)}`}>
                    <p className="text-sm">{message.content}</p>
                    {message.intent && (
                      <div className="mt-2 flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">
                          {message.intent}
                        </Badge>
                        {message.confidence && (
                          <span className="text-xs text-gray-400">
                            {Math.round(message.confidence * 100)}%
                          </span>
                        )}
                      </div>
                    )}
                    <div className="text-xs text-gray-400 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-full bg-gray-600">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-gray-700 text-white p-3 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Lua está pensando...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Área de input */}
          <div className="flex items-center gap-2">
            <div className="flex-1 relative">
              <Textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Digite sua mensagem ou use o microfone..."
                className="bg-gray-800 border-gray-600 text-white resize-none"
                rows={1}
                disabled={isLoading}
              />
            </div>
            
            {speechSupported && voiceEnabled && (
              <Button
                variant="outline"
                size="sm"
                onClick={isListening ? stopListening : startListening}
                disabled={isLoading}
                className={`${
                  isListening 
                    ? 'bg-red-600 hover:bg-red-700 animate-pulse' 
                    : 'bg-gray-600 hover:bg-gray-700'
                } border-gray-600`}
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </Button>
            )}
            
            {isSpeaking && (
              <Button
                variant="outline"
                size="sm"
                onClick={stopSpeaking}
                className="bg-orange-600 hover:bg-orange-700 border-gray-600"
              >
                <VolumeX className="w-4 h-4" />
              </Button>
            )}
            
            <Button
              onClick={() => handleSendMessage()}
              disabled={!inputText.trim() || isLoading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>

          {/* Status da voz */}
          {voiceEnabled && (
            <div className="mt-2 text-xs text-gray-400 flex items-center gap-4">
              <span className="flex items-center gap-1">
                {speechSupported ? (
                  <CheckCircle className="w-3 h-3 text-green-400" />
                ) : (
                  <XCircle className="w-3 h-3 text-red-400" />
                )}
                Reconhecimento de voz: {speechSupported ? 'Disponível' : 'Não suportado'}
              </span>
              {isListening && (
                <span className="flex items-center gap-1 text-red-400">
                  <Mic className="w-3 h-3" />
                  Ouvindo...
                </span>
              )}
              {isSpeaking && (
                <span className="flex items-center gap-1 text-orange-400">
                  <Volume2 className="w-3 h-3" />
                  Falando...
                </span>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default LuaUnified;

