# backend/src/lua_free_intelligent.py

from flask import Blueprint, request, jsonify
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Importar os novos módulos de IA gratuita
from src.lua_core.lua_free_ai_engine import lua_free_ai, IntentResult
from src.lua_core.lua_intelligent_reasoning import lua_reasoning, ReasoningResult

# Importar módulos existentes para compatibilidade
from src.lua_core.lua_module_enhanced import execute_action as execute_enhanced_action

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar blueprint
lua_free_bp = Blueprint('lua_free', __name__)

class LuaFreeIntelligent:
    """LUA Free Intelligent - IA gratuita com vida própria"""
    
    def __init__(self):
        # Memória de conversa
        self.conversation_memory = []
        self.max_memory_size = 20
        
        # Contexto da sessão
        self.session_context = {}
        
        # Estatísticas
        self.stats = {
            'total_interactions': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'unknown_commands': 0,
            'learned_patterns': 0
        }
        
        # Cache de respostas
        self.response_cache = {}
        
        logger.info("LUA Free Intelligent inicializada com sucesso")
    
    def process_natural_command(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processa comando em linguagem natural usando IA gratuita"""
        try:
            self.stats['total_interactions'] += 1
            logger.info(f"[LUA FREE] Processando comando: {user_input}")
            
            # Atualizar contexto
            if context:
                self.session_context.update(context)
            
            # Etapa 1: Classificação de intenção e extração de entidades
            intent_result = lua_free_ai.classify_intent(user_input)
            
            logger.info(f"[LUA FREE] Intenção classificada: {intent_result.intent} (confiança: {intent_result.confidence:.2f})")
            
            # Etapa 2: Raciocínio inteligente
            reasoning_result = lua_reasoning.reason_about_command(
                user_input, 
                {
                    'intent': intent_result.intent,
                    'confidence': intent_result.confidence,
                    'entities': intent_result.entities
                }
            )
            
            logger.info(f"[LUA FREE] Ação determinada: {reasoning_result.action} (confiança: {reasoning_result.confidence:.2f})")
            
            # Etapa 3: Executar ação ou solicitar confirmação
            if reasoning_result.requires_confirmation and reasoning_result.confidence < 0.8:
                response = self._handle_confirmation_request(reasoning_result, intent_result)
            else:
                response = self._execute_determined_action(reasoning_result, intent_result, user_input)
            
            # Salvar na memória
            self._save_to_memory(user_input, response, intent_result, reasoning_result)
            
            return response
            
        except Exception as e:
            logger.error(f"[LUA FREE] Erro no processamento: {str(e)}")
            self.stats['failed_actions'] += 1
            return {
                'message': f"Desculpe, ocorreu um erro ao processar seu comando. Erro: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
    
    def _handle_confirmation_request(self, reasoning_result: ReasoningResult, intent_result: IntentResult) -> Dict[str, Any]:
        """Lida com solicitações que requerem confirmação"""
        
        if reasoning_result.action == "request_clarification":
            return {
                'message': reasoning_result.reasoning,
                'status': 'needs_clarification',
                'suggestions': reasoning_result.suggestions,
                'original_text': intent_result.raw_text,
                'confidence': reasoning_result.confidence,
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
        
        elif reasoning_result.action == "suggest_similar":
            similar_command = reasoning_result.parameters.get('similar_command', {})
            return {
                'message': f"Não tenho certeza do que você quer dizer. Você quis dizer algo como: '{similar_command.get('text', '')}'?",
                'status': 'suggestion',
                'suggestions': [
                    f"Sim, execute: {similar_command.get('text', '')}",
                    "Não, vou reformular",
                    "Mostrar ajuda"
                ],
                'suggested_action': similar_command.get('action', ''),
                'confidence': reasoning_result.confidence,
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
        
        else:
            # Confirmação para ação específica
            action_descriptions = {
                'registrar_vale': f"registrar um vale de R$ {reasoning_result.parameters.get('valor', '?')} para {reasoning_result.parameters.get('funcionario', '?')}",
                'gerar_relatorio': f"gerar um relatório de {reasoning_result.parameters.get('tipo', 'geral')}",
                'consultar_dados': f"consultar dados de {reasoning_result.parameters.get('tipo', 'sistema')}",
                'calcular_valores': f"realizar cálculos financeiros"
            }
            
            description = action_descriptions.get(reasoning_result.action, reasoning_result.action)
            
            return {
                'message': f"Entendi que você quer {description}. Confirma?",
                'status': 'confirmation_required',
                'action': reasoning_result.action,
                'parameters': reasoning_result.parameters,
                'confidence': reasoning_result.confidence,
                'reasoning': reasoning_result.reasoning,
                'suggestions': ["Sim, executar", "Não, cancelar", "Modificar parâmetros"],
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
    
    def _execute_determined_action(self, reasoning_result: ReasoningResult, intent_result: IntentResult, original_text: str) -> Dict[str, Any]:
        """Executa a ação determinada pelo raciocínio"""
        
        try:
            action = reasoning_result.action
            parameters = reasoning_result.parameters
            
            # Mapear ações para funções existentes
            if action == "registrar_vale":
                return self._execute_vale_action(parameters, original_text)
            
            elif action == "gerar_relatorio":
                return self._execute_report_action(parameters, original_text)
            
            elif action == "consultar_dados":
                return self._execute_query_action(parameters, original_text)
            
            elif action == "solicitar_ajuda":
                return self._execute_help_action(parameters, original_text)
            
            elif action == "cumprimentar":
                return {
                    'message': "Olá! Sou a LUA Free Intelligent, sua assistente com IA gratuita. Como posso ajudar você hoje?",
                    'status': 'success',
                    'suggestions': [
                        "Adicionar vale para funcionário",
                        "Gerar relatório",
                        "Consultar dados",
                        "Ver ajuda"
                    ],
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent'
                }
            
            elif action == "despedir":
                return {
                    'message': "Até logo! Estarei aqui quando precisar de mim.",
                    'status': 'success',
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent'
                }
            
            elif action == "agradecer":
                return {
                    'message': "De nada! Fico feliz em ajudar. Precisa de mais alguma coisa?",
                    'status': 'success',
                    'suggestions': [
                        "Sim, preciso de mais ajuda",
                        "Não, obrigado",
                        "Mostrar funcionalidades"
                    ],
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent'
                }
            
            else:
                # Ação não mapeada - tentar fallback para sistema anterior
                return self._fallback_to_enhanced_system(original_text, reasoning_result)
                
        except Exception as e:
            logger.error(f"[LUA FREE] Erro na execução da ação {action}: {str(e)}")
            self.stats['failed_actions'] += 1
            return {
                'message': f"Erro ao executar ação '{action}': {str(e)}",
                'status': 'error',
                'action': action,
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
    
    def _execute_vale_action(self, parameters: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Executa ação de registrar vale"""
        funcionario = parameters.get('funcionario')
        valor = parameters.get('valor')
        
        # Verificar parâmetros obrigatórios
        if not funcionario:
            return {
                'message': "Para registrar o vale, preciso saber o nome do funcionário. Qual é o nome?",
                'status': 'missing_parameter',
                'missing': 'funcionario',
                'partial_parameters': parameters,
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
        
        if not valor:
            return {
                'message': f"Para registrar o vale para {funcionario}, preciso saber o valor. Qual é o valor?",
                'status': 'missing_parameter',
                'missing': 'valor',
                'partial_parameters': parameters,
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
        
        # Validar valor
        try:
            valor_float = float(valor)
            if valor_float <= 0:
                return {
                    'message': f"O valor do vale deve ser positivo. Valor informado: R$ {valor_float:.2f}",
                    'status': 'invalid_parameter',
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent'
                }
        except:
            return {
                'message': f"Valor inválido: '{valor}'. Por favor, informe um valor numérico válido.",
                'status': 'invalid_parameter',
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
        
        # Executar usando sistema existente
        try:
            # Construir comando para o sistema existente
            command_for_enhanced = f"adiciona vale para {funcionario} de {valor_float}"
            result = execute_enhanced_action(command_for_enhanced)
            
            self.stats['successful_actions'] += 1
            
            # Adaptar resposta
            if isinstance(result, dict) and result.get('status') == 'success':
                return {
                    'message': f"✅ Vale de R$ {valor_float:.2f} registrado com sucesso para {funcionario}!",
                    'status': 'success',
                    'action': 'registrar_vale',
                    'funcionario': funcionario,
                    'valor': valor_float,
                    'data': result.get('data', {}),
                    'download_url': result.get('download_url'),
                    'filename': result.get('filename'),
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent'
                }
            else:
                return {
                    'message': f"Vale registrado para {funcionario} no valor de R$ {valor_float:.2f}",
                    'status': 'success',
                    'action': 'registrar_vale',
                    'funcionario': funcionario,
                    'valor': valor_float,
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent'
                }
                
        except Exception as e:
            logger.error(f"[LUA FREE] Erro ao executar vale: {str(e)}")
            return {
                'message': f"Erro ao registrar vale: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
    
    def _execute_report_action(self, parameters: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Executa ação de gerar relatório"""
        tipo = parameters.get('tipo', 'geral')
        formato = parameters.get('formato', 'pdf')
        
        try:
            # Construir comando para o sistema existente
            command_for_enhanced = f"gera relatório de {tipo}"
            if 'pdf' in original_text.lower():
                command_for_enhanced += " e baixa pdf"
            
            result = execute_enhanced_action(command_for_enhanced)
            
            self.stats['successful_actions'] += 1
            
            # Adaptar resposta
            if isinstance(result, dict):
                return {
                    'message': f"✅ Relatório de {tipo} gerado com sucesso!",
                    'status': 'success',
                    'action': 'gerar_relatorio',
                    'tipo': tipo,
                    'formato': formato,
                    'data': result.get('data', {}),
                    'download_url': result.get('download_url'),
                    'filename': result.get('filename'),
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent'
                }
            else:
                return {
                    'message': f"Relatório de {tipo} gerado",
                    'status': 'success',
                    'action': 'gerar_relatorio',
                    'tipo': tipo,
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent'
                }
                
        except Exception as e:
            logger.error(f"[LUA FREE] Erro ao gerar relatório: {str(e)}")
            return {
                'message': f"Erro ao gerar relatório: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
    
    def _execute_query_action(self, parameters: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Executa ação de consultar dados"""
        tipo = parameters.get('tipo', 'geral')
        
        try:
            # Mapear tipos de consulta para comandos do sistema existente
            command_mapping = {
                'estoque': 'mostra estoque',
                'funcionarios': 'lista funcionários',
                'vendas': 'mostra vendas',
                'caixa': 'mostra caixa',
                'encomendas': 'mostra encomendas'
            }
            
            command_for_enhanced = command_mapping.get(tipo, f"mostra {tipo}")
            result = execute_enhanced_action(command_for_enhanced)
            
            self.stats['successful_actions'] += 1
            
            # Adaptar resposta
            if isinstance(result, dict):
                return {
                    'message': f"✅ Dados de {tipo} consultados com sucesso!",
                    'status': 'success',
                    'action': 'consultar_dados',
                    'tipo': tipo,
                    'data': result.get('data', {}),
                    'show_in_interface': result.get('show_in_interface', False),
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent'
                }
            else:
                return {
                    'message': f"Dados de {tipo} consultados",
                    'status': 'success',
                    'action': 'consultar_dados',
                    'tipo': tipo,
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent'
                }
                
        except Exception as e:
            logger.error(f"[LUA FREE] Erro na consulta: {str(e)}")
            return {
                'message': f"Erro na consulta de {tipo}: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent'
            }
    
    def _execute_help_action(self, parameters: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Executa ação de ajuda"""
        return {
            'message': """🤖 **LUA Free Intelligent - Ajuda**

Sou uma IA gratuita que entende comandos em linguagem natural. Posso ajudar com:

**💰 Vales e Adiantamentos:**
• "Adiciona vale para João de R$500"
• "Registra adiantamento de 300 para Maria"

**📊 Relatórios:**
• "Gera relatório de caixa"
• "Relatório financeiro em PDF"
• "Mostra relatório de vendas"

**🔍 Consultas:**
• "Mostra estoque"
• "Lista funcionários"
• "Ver vendas do dia"

**🧠 Inteligência:**
• Entendo comandos em linguagem natural
• Nunca direi "comando não reconhecido"
• Aprendo com suas interações
• Posso inferir o que você quer mesmo com comandos novos

Digite qualquer coisa em português que eu tentarei entender e executar!""",
            'status': 'success',
            'action': 'mostrar_ajuda',
            'capabilities': [
                'registrar_vale',
                'gerar_relatorio',
                'consultar_dados',
                'raciocinio_inteligente',
                'aprendizado_continuo'
            ],
            'timestamp': datetime.now().isoformat(),
            'processed_by': 'lua_free_intelligent'
        }
    
    def _fallback_to_enhanced_system(self, original_text: str, reasoning_result: ReasoningResult) -> Dict[str, Any]:
        """Fallback para o sistema enhanced quando ação não é mapeada"""
        try:
            logger.info(f"[LUA FREE] Usando fallback para sistema enhanced: {original_text}")
            
            result = execute_enhanced_action(original_text)
            
            if isinstance(result, dict) and result.get('status') == 'success':
                self.stats['successful_actions'] += 1
                result['processed_by'] = 'lua_free_intelligent_fallback'
                result['reasoning'] = reasoning_result.reasoning
                return result
            else:
                # Se o sistema enhanced também não conseguiu, usar resposta inteligente
                self.stats['unknown_commands'] += 1
                return {
                    'message': f"Entendi que você quer '{original_text}', mas ainda não sei como executar isso. Pode reformular ou escolher uma das opções?",
                    'status': 'unknown_action',
                    'original_text': original_text,
                    'reasoning': reasoning_result.reasoning,
                    'suggestions': reasoning_result.suggestions,
                    'confidence': reasoning_result.confidence,
                    'timestamp': datetime.now().isoformat(),
                    'processed_by': 'lua_free_intelligent_fallback'
                }
                
        except Exception as e:
            logger.error(f"[LUA FREE] Erro no fallback: {str(e)}")
            return {
                'message': f"Não consegui processar '{original_text}'. Erro: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_free_intelligent_fallback'
            }
    
    def _save_to_memory(self, user_input: str, response: Dict[str, Any], intent_result: IntentResult, reasoning_result: ReasoningResult):
        """Salva interação na memória para aprendizado"""
        memory_entry = {
            'user_input': user_input,
            'response': response,
            'intent': intent_result.intent,
            'intent_confidence': intent_result.confidence,
            'entities': intent_result.entities,
            'action': reasoning_result.action,
            'action_confidence': reasoning_result.confidence,
            'reasoning': reasoning_result.reasoning,
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversation_memory.append(memory_entry)
        
        # Manter apenas últimas interações
        if len(self.conversation_memory) > self.max_memory_size:
            self.conversation_memory = self.conversation_memory[-self.max_memory_size:]
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Retorna resumo da conversa"""
        if not self.conversation_memory:
            return {
                'total_interactions': 0,
                'recent_topics': [],
                'success_rate': 0.0
            }
        
        # Calcular estatísticas
        successful = sum(1 for entry in self.conversation_memory if entry['response'].get('status') == 'success')
        success_rate = successful / len(self.conversation_memory) if self.conversation_memory else 0
        
        # Extrair tópicos recentes
        recent_topics = list(set([
            entry['action'] for entry in self.conversation_memory[-10:]
            if entry['action'] not in ['unknown', 'error']
        ]))
        
        return {
            'total_interactions': len(self.conversation_memory),
            'recent_topics': recent_topics,
            'success_rate': success_rate,
            'stats': self.stats
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Retorna capacidades da LUA Free Intelligent"""
        return {
            'ai_features': [
                'Classificação de intenções com SpaCy',
                'Extração de entidades inteligente',
                'Raciocínio baseado em regras avançadas',
                'Aprendizado contínuo',
                'Fallback inteligente',
                'Nunca responde "comando não reconhecido"'
            ],
            'supported_actions': [
                'registrar_vale',
                'gerar_relatorio',
                'consultar_dados',
                'calcular_valores',
                'configurar_sistema',
                'solicitar_ajuda'
            ],
            'languages': ['Português Brasileiro'],
            'cost': 'Gratuito - sem APIs pagas',
            'version': '1.0.0'
        }

# Instância global da LUA Free Intelligent
lua_free = LuaFreeIntelligent()

# Endpoints da API

@lua_free_bp.route("/lua_free/chat", methods=["POST"])
def free_chat():
    """Endpoint principal para chat com a LUA Free Intelligent"""
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        context = data.get("context", {})
        
        if not message:
            return jsonify({
                "message": "Por favor, digite uma mensagem.",
                "status": "error"
            }), 400
        
        # Processar comando
        response = lua_free.process_natural_command(message, context)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"[LUA FREE] Erro no endpoint de chat: {str(e)}")
        return jsonify({
            "message": f"Erro interno do servidor: {str(e)}",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500

@lua_free_bp.route("/lua_free/conversation_summary", methods=["GET"])
def conversation_summary():
    """Endpoint para resumo da conversa"""
    try:
        summary = lua_free.get_conversation_summary()
        return jsonify(summary)
    except Exception as e:
        logger.error(f"[LUA FREE] Erro no resumo da conversa: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lua_free_bp.route("/lua_free/capabilities", methods=["GET"])
def capabilities():
    """Endpoint para capacidades da LUA Free"""
    try:
        caps = lua_free.get_capabilities()
        return jsonify(caps)
    except Exception as e:
        logger.error(f"[LUA FREE] Erro nas capacidades: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lua_free_bp.route("/lua_free/health", methods=["GET"])
def health_check():
    """Endpoint para verificação de saúde"""
    try:
        return jsonify({
            "status": "healthy",
            "ai_engine": "spacy + scikit-learn",
            "memory_size": len(lua_free.conversation_memory),
            "stats": lua_free.stats,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"[LUA FREE] Erro no health check: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lua_free_bp.route("/lua_free/reset_conversation", methods=["POST"])
def reset_conversation():
    """Endpoint para resetar conversa"""
    try:
        lua_free.conversation_memory.clear()
        lua_free.session_context.clear()
        
        return jsonify({
            "message": "Conversa resetada! Sou a LUA Free Intelligent, pronta para ajudar.",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"[LUA FREE] Erro ao resetar conversa: {str(e)}")
        return jsonify({"error": str(e)}), 500

