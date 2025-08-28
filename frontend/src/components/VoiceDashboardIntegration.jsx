import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Mic, MicOff, Volume2, Power, PowerOff, Bot } from 'lucide-react';

const VoiceDashboardIntegration = ({ onAddWidget, onVoiceCommand }) => {
  const [isListening, setIsListening] = useState(false);
  const [isAlwaysListening, setIsAlwaysListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [isWaitingForCommand, setIsWaitingForCommand] = useState(false);
  const [lastCommand, setLastCommand] = useState('');
  const [status, setStatus] = useState('Inativo');
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const hotwordTimeoutRef = useRef(null);

  const speak = (text) => {
    if (synthRef.current && text) {
      synthRef.current.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'pt-BR';
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      
      synthRef.current.speak(utterance);
    }
  };

  const processVoiceCommand = async (command) => {
    const lowerCommand = command.toLowerCase();
    setLastCommand(command);
    
    // Comandos específicos do dashboard
    if (lowerCommand.includes('dashboard')) {
      if (lowerCommand.includes('conta de luz') && lowerCommand.includes('compare')) {
        speak('Adicionando comparação de conta de luz ao dashboard.');
        const widget = {
          titulo: 'Comparação Conta de Luz',
          tipo: 'comparison',
          configuracao: { comparison_type: 'conta_luz' },
          grupo: 'energia',
          subgrupo: 'comparacoes'
        };
        onAddWidget && onAddWidget(widget);
        return;
      }
      
      if (lowerCommand.includes('gasto') && lowerCommand.includes('lucro')) {
        speak('Adicionando dados de gastos e lucros ao dashboard.');
        const widget = {
          titulo: 'Gastos e Lucros do Mês',
          tipo: 'metric',
          configuracao: { metric_type: 'lucro_mes' },
          grupo: 'financeiro',
          subgrupo: 'lucros'
        };
        onAddWidget && onAddWidget(widget);
        return;
      }
      
      if (lowerCommand.includes('vales') && lowerCommand.includes('mês')) {
        speak('Adicionando últimos vales do mês ao dashboard.');
        const widget = {
          titulo: 'Últimos Vales do Mês',
          tipo: 'table',
          configuracao: { table_type: 'ultimos_vales' },
          grupo: 'funcionarios',
          subgrupo: 'vales'
        };
        onAddWidget && onAddWidget(widget);
        return;
      }
      
      if (lowerCommand.includes('vendas')) {
        speak('Adicionando dados de vendas ao dashboard.');
        const widget = {
          titulo: 'Vendas do Mês',
          tipo: 'metric',
          configuracao: { metric_type: 'total_vendas' },
          grupo: 'vendas',
          subgrupo: 'vendas_mensais'
        };
        onAddWidget && onAddWidget(widget);
        return;
      }
    }
    
    // Comandos de controle
    if (lowerCommand.includes('parar') || lowerCommand.includes('pare')) {
      setIsListening(false);
      setIsWaitingForCommand(false);
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      speak('Assistente de voz pausado.');
      setStatus('Pausado');
      if (isAlwaysListening) {
        setTimeout(() => startHotwordListening(), 1000);
      }
      return;
    }
    
    if (lowerCommand.includes('obrigado') || lowerCommand.includes('obrigada')) {
      speak('De nada! Estou aqui para ajudar com o dashboard.');
      setIsWaitingForCommand(false);
      if (isAlwaysListening) {
        setTimeout(() => startHotwordListening(), 1000);
      }
      return;
    }
    
    // Processar comando via API da LUA
    try {
      const response = await fetch('http://localhost:5000/api/dashboard/lua/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comando: command }),
      });

      const result = await response.json();
      
      if (result.status === 'success') {
        speak(result.message || 'Comando processado com sucesso.');
        
        if (result.widget_suggestion && onAddWidget) {
          onAddWidget(result.widget_suggestion);
        }
      } else {
        speak(result.message || 'Não entendi o comando. Tente novamente.');
      }
    } catch (error) {
      console.error('Erro ao processar comando de voz:', error);
      speak('Erro de conexão. Verifique se o servidor está funcionando.');
    }
    
    setIsWaitingForCommand(false);
    
    if (isAlwaysListening) {
      setTimeout(() => startHotwordListening(), 2000);
    }
  };

  const detectHotword = (transcript) => {
    const lowerTranscript = transcript.toLowerCase();
    
    const hotwords = ['lua', 'lúa', 'luá'];
    
    for (const hotword of hotwords) {
      if (lowerTranscript.includes(hotword)) {
        console.log('🌙 Hotword "Lua" detectada no dashboard!');
        
        const hotwordIndex = lowerTranscript.indexOf(hotword);
        const command = transcript.substring(hotwordIndex + hotword.length).trim();
        
        if (command) {
          speak('Sim, como posso ajudar com o dashboard?');
          processVoiceCommand(command);
        } else {
          speak('Oi! Como posso ajudar com o dashboard?');
          setIsWaitingForCommand(true);
          startCommandListening();
        }
        
        return true;
      }
    }
    
    return false;
  };

  const startHotwordListening = () => {
    if (!recognitionRef.current || !isAlwaysListening) return;
    
    try {
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.start();
      setIsListening(true);
      setStatus('Escutando "Lua"...');
      console.log('🎤 Escutando hotword "Lua" no dashboard...');
    } catch (error) {
      console.error('Erro ao iniciar escuta de hotword:', error);
      setTimeout(() => startHotwordListening(), 2000);
    }
  };

  const startCommandListening = () => {
    if (!recognitionRef.current) return;
    
    recognitionRef.current.stop();
    
    setTimeout(() => {
      try {
        recognitionRef.current.continuous = false;
        recognitionRef.current.start();
        setIsListening(true);
        setStatus('Aguardando comando...');
        console.log('🎤 Aguardando comando do dashboard...');
        
        hotwordTimeoutRef.current = setTimeout(() => {
          if (isWaitingForCommand) {
            setIsWaitingForCommand(false);
            speak('Tempo esgotado. Voltando à escuta.');
            setStatus('Tempo esgotado');
            if (isAlwaysListening) {
              startHotwordListening();
            }
          }
        }, 10000);
        
      } catch (error) {
        console.error('Erro ao iniciar escuta de comando:', error);
      }
    }, 500);
  };

  const toggleAlwaysListening = () => {
    if (isAlwaysListening) {
      // Parar escuta contínua
      setIsAlwaysListening(false);
      setIsListening(false);
      setIsWaitingForCommand(false);
      setStatus('Inativo');
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (hotwordTimeoutRef.current) {
        clearTimeout(hotwordTimeoutRef.current);
      }
      speak('Assistente de voz desativado.');
    } else {
      // Iniciar escuta contínua
      setIsAlwaysListening(true);
      speak('Assistente de voz ativado. Diga "Lua" para começar.');
      setTimeout(() => startHotwordListening(), 1000);
    }
  };

  const toggleManualListening = () => {
    if (isListening && !isAlwaysListening) {
      // Parar escuta manual
      setIsListening(false);
      setStatus('Inativo');
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    } else if (!isAlwaysListening) {
      // Iniciar escuta manual
      setIsListening(true);
      setStatus('Escutando...');
      if (recognitionRef.current) {
        recognitionRef.current.continuous = false;
        recognitionRef.current.start();
      }
    }
  };

  useEffect(() => {
    // Verificar suporte para Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setIsSupported(true);
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.lang = 'pt-BR';
      recognitionRef.current.interimResults = false;
      recognitionRef.current.maxAlternatives = 1;
      
      synthRef.current = window.speechSynthesis;
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript;
        console.log('🎤 Transcript:', transcript);
        
        if (isWaitingForCommand) {
          // Processar comando direto
          processVoiceCommand(transcript);
          if (hotwordTimeoutRef.current) {
            clearTimeout(hotwordTimeoutRef.current);
          }
        } else if (isAlwaysListening) {
          // Detectar hotword
          if (!detectHotword(transcript)) {
            // Continuar escutando se não detectou hotword
            setTimeout(() => startHotwordListening(), 500);
          }
        } else {
          // Escuta manual - processar comando direto
          processVoiceCommand(transcript);
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Erro de reconhecimento de voz:', event.error);
        setIsListening(false);
        
        if (event.error === 'no-speech' && isAlwaysListening) {
          setTimeout(() => startHotwordListening(), 1000);
        } else if (event.error === 'network') {
          setStatus('Erro de rede');
        } else {
          setStatus('Erro: ' + event.error);
        }
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
        
        if (isAlwaysListening && !isWaitingForCommand) {
          setTimeout(() => startHotwordListening(), 1000);
        } else if (!isAlwaysListening) {
          setStatus('Inativo');
        }
      };
    } else {
      setIsSupported(false);
      console.warn('Web Speech API não suportada neste navegador');
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (synthRef.current) {
        synthRef.current.cancel();
      }
      if (hotwordTimeoutRef.current) {
        clearTimeout(hotwordTimeoutRef.current);
      }
    };
  }, []);

  if (!isSupported) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <MicOff className="h-5 w-5" />
            Assistente de Voz Não Suportado
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">
            Seu navegador não suporta reconhecimento de voz. 
            Use Chrome, Edge ou Safari para ativar esta funcionalidade.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          Assistente de Voz - Dashboard
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Badge variant={isListening ? "default" : "secondary"}>
              {status}
            </Badge>
            {isWaitingForCommand && (
              <Badge variant="outline">Aguardando comando</Badge>
            )}
          </div>
          
          <div className="flex gap-2">
            <Button
              size="sm"
              variant={isAlwaysListening ? "default" : "outline"}
              onClick={toggleAlwaysListening}
            >
              {isAlwaysListening ? <Power className="h-4 w-4" /> : <PowerOff className="h-4 w-4" />}
            </Button>
            
            <Button
              size="sm"
              variant={isListening && !isAlwaysListening ? "default" : "outline"}
              onClick={toggleManualListening}
              disabled={isAlwaysListening}
            >
              {isListening && !isAlwaysListening ? <Mic className="h-4 w-4" /> : <MicOff className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        {lastCommand && (
          <div className="p-3 bg-gray-50 rounded">
            <p className="text-sm font-medium">Último comando:</p>
            <p className="text-sm text-gray-600">"{lastCommand}"</p>
          </div>
        )}

        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Comandos de voz para dashboard:</p>
          <div className="text-xs text-gray-600 space-y-1">
            <p>• "Lua, me mostre no dashboard conta de luz desse mês com o do mês passado e compare"</p>
            <p>• "Lua me mostra o gasto e lucro desse mês no dashboard"</p>
            <p>• "Lua me mostra no dashboard os últimos vales do mês"</p>
            <p>• "Lua, adicione vendas do mês ao dashboard"</p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Volume2 className="h-3 w-3" />
          <span>Respostas por voz ativadas</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default VoiceDashboardIntegration;

