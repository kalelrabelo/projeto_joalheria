import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Mic, MicOff, Volume2, Power, PowerOff } from 'lucide-react';

const VoiceAssistant = ({ onCommand }) => {
  const [isListening, setIsListening] = useState(false);
  const [isAlwaysListening, setIsAlwaysListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [isWaitingForCommand, setIsWaitingForCommand] = useState(false);
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const hotwordTimeoutRef = useRef(null);

  const speak = (text) => {
    if (synthRef.current && text) {
      // Cancelar qualquer fala anterior
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
    
    // Comandos de controle do assistente
    if (lowerCommand.includes('parar') || lowerCommand.includes('pare')) {
      setIsListening(false);
      setIsWaitingForCommand(false);
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      speak('Assistente pausado.');
      // Retomar escuta de hotword se estiver no modo sempre escutando
      if (isAlwaysListening) {
        setTimeout(() => startHotwordListening(), 1000);
      }
      return;
    }
    
    if (lowerCommand.includes('obrigado') || lowerCommand.includes('obrigada')) {
      speak('De nada! Estou aqui para ajudar.');
      setIsWaitingForCommand(false);
      // Retomar escuta de hotword se estiver no modo sempre escutando
      if (isAlwaysListening) {
        setTimeout(() => startHotwordListening(), 1000);
      }
      return;
    }
    
    try {
      // Enviar comando para o backend
      const response = await fetch('/api/voice/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command })
      });
      
      const result = await response.json();
      
      console.log('🔍 DEBUG - Resposta do comando de voz:', result);
      
      if (result.status === 'success') {
        // JARVIS MODE - Disparar evento direto para App principal
        if (result.show_in_interface && result.data) {
          console.log('🤖 JARVIS - Disparando evento direto para App principal');
          
          // Disparar evento JARVIS que vai direto para o App
          const jarvisEvent = new CustomEvent('jarvisCommand', {
            detail: {
              data: result
            }
          });
          window.dispatchEvent(jarvisEvent);
          
          // EXECUÇÃO SILENCIOSA - SEM FALAR
          // speak(result.response || 'Dados encontrados e exibidos na tela.');
        } else {
          // EXECUÇÃO SILENCIOSA - SEM FALAR
          // speak(result.response || result.message || 'Comando executado com sucesso.');
        }
        
        // Executar ação específica se necessário
        if (result.action === 'navigate') {
          console.log('Navegando para:', result.data?.page);
        }
        
        // Passar comando para o componente pai para execução adicional
        if (onCommand) {
          onCommand(command);
        }
      } else {
        // EXECUÇÃO SILENCIOSA - SEM FALAR ERROS
        // speak(result.message || 'Erro ao processar comando.');
      }
    } catch (error) {
      console.error('Erro ao processar comando de voz:', error);
      // EXECUÇÃO SILENCIOSA - SEM FALAR ERROS DE CONEXÃO
      // speak('Erro de conexão. Verifique se o servidor está funcionando.');
    }
    
    // Finalizar sessão de comando
    setIsWaitingForCommand(false);
    
    // Retomar escuta de hotword se estiver no modo sempre escutando
    if (isAlwaysListening) {
      setTimeout(() => startHotwordListening(), 2000);
    }
  };

  const detectHotword = (transcript) => {
    const lowerTranscript = transcript.toLowerCase();
    
    // Detectar variações da palavra "Lua"
    const hotwords = ['lua', 'lúa', 'luá'];
    
    for (const hotword of hotwords) {
      if (lowerTranscript.includes(hotword)) {
        console.log('🌙 Hotword "Lua" detectada!');
        
        // Extrair comando após a hotword
        const hotwordIndex = lowerTranscript.indexOf(hotword);
        const command = transcript.substring(hotwordIndex + hotword.length).trim();
        
        if (command) {
          // Comando direto após hotword
          speak('Sim, como posso ajudar?');
          processVoiceCommand(command);
        } else {
          // Apenas hotword, aguardar comando
          speak('Oi! Como posso ajudar?');
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
      console.log('🎤 Escutando hotword "Lua"...');
    } catch (error) {
      console.error('Erro ao iniciar escuta de hotword:', error);
      // Tentar novamente após um tempo
      setTimeout(() => startHotwordListening(), 2000);
    }
  };

  const startCommandListening = () => {
    if (!recognitionRef.current) return;
    
    // Parar reconhecimento atual
    recognitionRef.current.stop();
    
    setTimeout(() => {
      try {
        recognitionRef.current.continuous = false;
        recognitionRef.current.start();
        setIsListening(true);
        console.log('🎤 Aguardando comando...');
        
        // Timeout para retornar à escuta de hotword
        hotwordTimeoutRef.current = setTimeout(() => {
          if (isWaitingForCommand) {
            setIsWaitingForCommand(false);
            speak('Tempo esgotado. Voltando à escuta.');
            if (isAlwaysListening) {
              startHotwordListening();
            }
          }
        }, 10000); // 10 segundos de timeout
        
      } catch (error) {
        console.error('Erro ao iniciar escuta de comando:', error);
      }
    }, 500);
  };

  useEffect(() => {
    // Verificar suporte para Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setIsSupported(true);
      
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      // Configurações do reconhecimento de voz
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'pt-BR';
      recognitionRef.current.maxAlternatives = 1;

      // Eventos do reconhecimento de voz
      recognitionRef.current.onstart = () => {
        console.log('🎤 Reconhecimento de voz iniciado');
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        console.log('🎤 Reconhecimento de voz finalizado');
        
        // Se estiver no modo sempre escutando e não estiver aguardando comando, reiniciar
        if (isAlwaysListening && !isWaitingForCommand) {
          setTimeout(() => startHotwordListening(), 1000);
        }
      };

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.trim();
        console.log('🗣️ Texto reconhecido:', transcript);
        
        if (transcript) {
          if (isWaitingForCommand) {
            // Limpar timeout
            if (hotwordTimeoutRef.current) {
              clearTimeout(hotwordTimeoutRef.current);
            }
            
            // Processar comando
            processVoiceCommand(transcript);
          } else if (isAlwaysListening) {
            // Detectar hotword
            detectHotword(transcript);
          } else {
            // Modo manual
            processVoiceCommand(transcript);
          }
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('❌ Erro no reconhecimento de voz:', event.error);
        setIsListening(false);
        
        // EXECUÇÃO SILENCIOSA - SEM FEEDBACK DE ERRO
        // Feedback de erro específico
        switch (event.error) {
          case 'no-speech':
            // No modo sempre escutando, não dar feedback de "não ouvi nada"
            // if (!isAlwaysListening) {
            //   speak('Não consegui ouvir nada. Tente novamente.');
            // }
            break;
          case 'audio-capture':
            // speak('Erro no microfone. Verifique as permissões.');
            break;
          case 'not-allowed':
            // speak('Permissão negada para usar o microfone.');
            setIsAlwaysListening(false);
            break;
          default:
            // if (!isAlwaysListening) {
            //   speak('Erro no reconhecimento de voz.');
            // }
        }
        
        // Tentar reiniciar se estiver no modo sempre escutando
        if (isAlwaysListening && event.error !== 'not-allowed') {
          setTimeout(() => startHotwordListening(), 2000);
        }
      };
    }

    // Verificar suporte para síntese de voz
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (hotwordTimeoutRef.current) {
        clearTimeout(hotwordTimeoutRef.current);
      }
    };
  }, [onCommand, isAlwaysListening, isWaitingForCommand]);

  const toggleAlwaysListening = () => {
    if (isAlwaysListening) {
      // Desativar modo sempre escutando
      setIsAlwaysListening(false);
      setIsWaitingForCommand(false);
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      // EXECUÇÃO SILENCIOSA
      // speak('Modo sempre escutando desativado.');
    } else {
      // Ativar modo sempre escutando
      setIsAlwaysListening(true);
      // EXECUÇÃO SILENCIOSA
      // speak('Modo sempre escutando ativado. Diga "Lua" para me chamar.');
      setTimeout(() => startHotwordListening(), 1000);
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening && !isAlwaysListening) {
      try {
        recognitionRef.current.continuous = false;
        recognitionRef.current.start();
      } catch (error) {
        console.error('Erro ao iniciar reconhecimento:', error);
        // EXECUÇÃO SILENCIOSA
        // speak('Erro ao iniciar o reconhecimento de voz.');
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  if (!isSupported) {
    return (
      <div className="flex items-center space-x-2 p-2 bg-red-900 border border-red-700 rounded-lg">
        <MicOff className="h-4 w-4 text-red-400" />
        <span className="text-red-300 text-sm">
          Reconhecimento de voz não suportado neste navegador
        </span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-4 p-4 bg-gray-800 border border-gray-700 rounded-lg">
      <div className="flex items-center space-x-2">
        <Volume2 className="h-5 w-5 text-blue-400" />
        <span className="text-white font-medium">Assistente de Voz Lua</span>
      </div>
      
      <div className="flex items-center space-x-2">
        {/* Botão de modo sempre escutando */}
        <Button
          onClick={toggleAlwaysListening}
          className={`${
            isAlwaysListening 
              ? 'bg-blue-600 hover:bg-blue-700' 
              : 'bg-gray-600 hover:bg-gray-700'
          } transition-all duration-200`}
          size="sm"
        >
          {isAlwaysListening ? (
            <>
              <Power className="h-4 w-4 mr-2" />
              Sempre On
            </>
          ) : (
            <>
              <PowerOff className="h-4 w-4 mr-2" />
              Manual
            </>
          )}
        </Button>
        
        {/* Botão de escuta manual (só aparece quando não está no modo sempre escutando) */}
        {!isAlwaysListening && (
          <Button
            onClick={isListening ? stopListening : startListening}
            className={`${
              isListening 
                ? 'bg-red-600 hover:bg-red-700 animate-pulse' 
                : 'bg-green-600 hover:bg-green-700'
            } transition-all duration-200`}
            size="sm"
          >
            {isListening ? (
              <>
                <MicOff className="h-4 w-4 mr-2" />
                Parar
              </>
            ) : (
              <>
                <Mic className="h-4 w-4 mr-2" />
                Falar
              </>
            )}
          </Button>
        )}
        
        <Badge 
          className={`${
            isWaitingForCommand
              ? 'bg-yellow-500 text-white animate-pulse'
              : isListening 
                ? 'bg-green-500 text-white' 
                : isAlwaysListening
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-600 text-gray-300'
          }`}
        >
          {isWaitingForCommand 
            ? 'Aguardando comando...' 
            : isListening 
              ? (isAlwaysListening ? 'Escutando "Lua"...' : 'Ouvindo...') 
              : isAlwaysListening 
                ? 'Sempre ativo' 
                : 'Inativo'
          }
        </Badge>
      </div>
      
      <div className="text-xs text-gray-400">
        {isAlwaysListening 
          ? 'Diga "Lua" para ativar' 
          : 'Clique em "Falar" ou ative o modo sempre escutando'
        }
      </div>
    </div>
  );
};

export default VoiceAssistant;

