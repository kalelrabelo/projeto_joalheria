# backend/src/lua_super_intelligent.py

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import os
import json
import logging

# Importar o novo motor de IA e capacidades avançadas
from src.lua_ai_engine import lua_ai_engine, AIResponse
from src.lua_advanced_capabilities import lua_advanced, AdvancedAnalysis

# Importar módulos existentes para compatibilidade
from src.lua_core.lua_module_enhanced import execute_action as execute_enhanced_action
from src.lua_core.lua_module import ANTONIO_RABELO_HISTORY

lua_super_bp = Blueprint("lua_super", __name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração para relatórios
REPORTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
    os.pardir, os.pardir, os.pardir, 
    'tmp', 'lua_reports')

# Criar diretório de relatórios se não existir
os.makedirs(REPORTS_FOLDER, exist_ok=True)

class LuaSuperIntelligent:
    """LUA Super Inteligente - Versão avançada com IA e vida própria"""
    
    def __init__(self):
        self.ai_engine = lua_ai_engine
        self.conversation_memory = []
        self.user_preferences = {}
        self.learning_data = []
        
    def process_natural_command(self, user_input: str, user_context: dict = None) -> dict:
        """Processa comandos em linguagem natural com IA avançada"""
        try:
            logger.info(f"[LUA SUPER] Processando comando: {user_input}")
            
            # Adicionar contexto do usuário se fornecido
            if user_context:
                self.user_preferences.update(user_context)
            
            # Usar o motor de IA para processar o comando
            ai_response: AIResponse = self.ai_engine.process_command(user_input)
            
            # Converter resposta da IA para formato esperado pelo frontend
            response = {
                'message': ai_response.message,
                'response': ai_response.message,
                'status': ai_response.status,
                'data': ai_response.data,
                'show_in_interface': ai_response.show_in_interface,
                'tipo': ai_response.tipo,
                'download_url': ai_response.download_url,
                'action_taken': ai_response.action_taken,
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_super_intelligent'
            }
            
            # Salvar na memória de conversa
            self._save_to_memory(user_input, response)
            
            # Aprender com a interação
            self._learn_from_interaction(user_input, response)
            
            logger.info(f"[LUA SUPER] Resposta gerada: {response['status']}")
            return response
            
        except Exception as e:
            logger.error(f"[LUA SUPER] Erro ao processar comando: {str(e)}")
            error_response = {
                'message': f"Desculpe, ocorreu um erro interno. Vou tentar processar de outra forma: {str(e)}",
                'status': 'error',
                'fallback_attempted': True,
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_super_intelligent'
            }
            
            # Tentar fallback para o sistema anterior
            try:
                fallback_response = execute_enhanced_action(user_input)
                error_response['fallback_response'] = fallback_response
                error_response['message'] = fallback_response.get('message', error_response['message'])
                error_response['status'] = fallback_response.get('status', 'error')
                error_response['data'] = fallback_response.get('data')
            except Exception as fallback_error:
                logger.error(f"[LUA SUPER] Fallback também falhou: {str(fallback_error)}")
                error_response['fallback_error'] = str(fallback_error)
            
            return error_response
    
    def _save_to_memory(self, user_input: str, response: dict):
        """Salva interação na memória de conversa"""
        try:
            memory_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'response': response,
                'success': response.get('status') == 'success'
            }
            
            self.conversation_memory.append(memory_entry)
            
            # Manter apenas as últimas 100 interações
            if len(self.conversation_memory) > 100:
                self.conversation_memory = self.conversation_memory[-100:]
                
        except Exception as e:
            logger.error(f"[LUA SUPER] Erro ao salvar na memória: {str(e)}")
    
    def _learn_from_interaction(self, user_input: str, response: dict):
        """Aprende com as interações para melhorar futuras respostas"""
        try:
            learning_entry = {
                'timestamp': datetime.now().isoformat(),
                'input_pattern': user_input.lower(),
                'action_taken': response.get('action_taken'),
                'success': response.get('status') == 'success',
                'user_satisfaction': None  # Pode ser implementado com feedback do usuário
            }
            
            self.learning_data.append(learning_entry)
            
            # Manter apenas os últimos 500 dados de aprendizado
            if len(self.learning_data) > 500:
                self.learning_data = self.learning_data[-500:]
                
        except Exception as e:
            logger.error(f"[LUA SUPER] Erro no aprendizado: {str(e)}")
    
    def get_conversation_summary(self) -> dict:
        """Retorna um resumo da conversa atual"""
        try:
            total_interactions = len(self.conversation_memory)
            successful_interactions = sum(1 for entry in self.conversation_memory if entry.get('success', False))
            
            recent_topics = []
            for entry in self.conversation_memory[-10:]:
                action = entry.get('response', {}).get('action_taken')
                if action and action not in recent_topics:
                    recent_topics.append(action)
            
            return {
                'total_interactions': total_interactions,
                'successful_interactions': successful_interactions,
                'success_rate': successful_interactions / total_interactions if total_interactions > 0 else 0,
                'recent_topics': recent_topics,
                'user_preferences': self.user_preferences
            }
        except Exception as e:
            logger.error(f"[LUA SUPER] Erro ao gerar resumo: {str(e)}")
            return {'error': str(e)}
    
    def process_advanced_analysis(self, analysis_request: str, parameters: dict = None) -> dict:
        """Processa solicitações de análise avançada"""
        try:
            logger.info(f"[LUA SUPER] Processando análise avançada: {analysis_request}")
            
            # Identificar tipo de análise
            analysis_type = self._identify_analysis_type(analysis_request)
            
            # Realizar análise
            analysis_result: AdvancedAnalysis = lua_advanced.perform_business_intelligence_analysis(
                analysis_type, parameters
            )
            
            # Gerar resumo executivo se múltiplas análises
            executive_summary = None
            if analysis_result.confidence_score > 0.7:
                executive_summary = lua_advanced.generate_executive_summary([analysis_result])
            
            response = {
                'message': f"Análise {analysis_type} concluída com sucesso",
                'status': 'success',
                'analysis_type': analysis_type,
                'insights': analysis_result.insights,
                'recommendations': analysis_result.recommendations,
                'predictions': analysis_result.predictions,
                'confidence_score': analysis_result.confidence_score,
                'data_quality': analysis_result.data_quality,
                'executive_summary': executive_summary,
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lua_super_intelligent_advanced'
            }
            
            # Salvar na memória
            self._save_to_memory(analysis_request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"[LUA SUPER] Erro na análise avançada: {str(e)}")
            return {
                'message': f"Erro na análise avançada: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }
    
    def _identify_analysis_type(self, request: str) -> str:
        """Identifica o tipo de análise solicitada"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ['financeiro', 'caixa', 'dinheiro', 'receita', 'despesa']):
            return 'financial_trends'
        elif any(word in request_lower for word in ['funcionário', 'funcionario', 'empregado', 'performance']):
            return 'employee_performance'
        elif any(word in request_lower for word in ['estoque', 'inventário', 'inventario']):
            return 'inventory_optimization'
        elif any(word in request_lower for word in ['vendas', 'venda', 'previsão', 'previsao']):
            return 'sales_forecasting'
        elif any(word in request_lower for word in ['custo', 'custos', 'gasto', 'gastos']):
            return 'cost_analysis'
        elif any(word in request_lower for word in ['cliente', 'clientes', 'comportamento']):
            return 'customer_behavior'
        else:
            return 'general_business_analysis'
    
    def handle_contextual_followup(self, user_input: str) -> dict:
        """Lida com perguntas de acompanhamento baseadas no contexto"""
        try:
            # Obter contexto das últimas interações
            recent_context = []
            for entry in self.conversation_memory[-5:]:
                recent_context.append({
                    'input': entry.get('user_input', ''),
                    'action': entry.get('response', {}).get('action_taken', ''),
                    'data': entry.get('response', {}).get('data', {})
                })
            
            # Adicionar contexto à entrada do usuário
            contextual_input = f"Contexto das últimas interações: {json.dumps(recent_context, ensure_ascii=False)}\n\nPergunta atual: {user_input}"
            
            return self.process_natural_command(contextual_input)
            
        except Exception as e:
            logger.error(f"[LUA SUPER] Erro no followup contextual: {str(e)}")
            return self.process_natural_command(user_input)

# Instância global da LUA Super Inteligente
lua_super = LuaSuperIntelligent()

@lua_super_bp.route("/lua_super/advanced_analysis", methods=["POST"])
def advanced_analysis():
    """Endpoint para análises avançadas de BI"""
    try:
        data = request.get_json()
        analysis_request = data.get("analysis_request", "").strip()
        parameters = data.get("parameters", {})
        
        if not analysis_request:
            return jsonify({
                "message": "Por favor, especifique o tipo de análise desejada.",
                "status": "error"
            }), 400
        
        # Processar análise avançada
        response = lua_super.process_advanced_analysis(analysis_request, parameters)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"[LUA SUPER] Erro no endpoint de análise avançada: {str(e)}")
        return jsonify({
            "message": f"Erro interno do servidor: {str(e)}",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500

@lua_super_bp.route("/lua_super/chat", methods=["POST"])
def super_chat():
    """Endpoint principal para chat com a LUA Super Inteligente"""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        user_context = data.get("context", {})
        is_followup = data.get("is_followup", False)
        
        if not user_message:
            return jsonify({
                "message": "Por favor, digite uma mensagem.",
                "status": "error"
            }), 400
        
        # Processar comando
        if is_followup:
            response = lua_super.handle_contextual_followup(user_message)
        else:
            response = lua_super.process_natural_command(user_message, user_context)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"[LUA SUPER] Erro no endpoint de chat: {str(e)}")
        return jsonify({
            "message": f"Erro interno do servidor: {str(e)}",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500

@lua_super_bp.route("/lua_super/conversation_summary", methods=["GET"])
def get_conversation_summary():
    """Retorna resumo da conversa atual"""
    try:
        summary = lua_super.get_conversation_summary()
        return jsonify(summary)
    except Exception as e:
        logger.error(f"[LUA SUPER] Erro ao obter resumo: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lua_super_bp.route("/lua_super/reset_conversation", methods=["POST"])
def reset_conversation():
    """Reseta a conversa e memória"""
    try:
        lua_super.conversation_memory = []
        lua_super.ai_engine.conversation_context = []
        
        return jsonify({
            "message": "Conversa resetada com sucesso. Olá! Sou a LUA, sua assistente inteligente renovada. Como posso ajudar?",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"[LUA SUPER] Erro ao resetar conversa: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lua_super_bp.route("/lua_super/capabilities", methods=["GET"])
def get_capabilities():
    """Retorna as capacidades da LUA Super Inteligente"""
    capabilities = {
        "natural_language_processing": True,
        "intent_classification": True,
        "entity_extraction": True,
        "contextual_understanding": True,
        "learning_from_interactions": True,
        "fallback_reasoning": True,
        "conversation_memory": True,
        "multi_turn_dialogue": True,
        "supported_actions": [
            "registrar_vale",
            "gerar_relatorio", 
            "consultar_estoque",
            "consultar_vendas",
            "consultar_funcionarios",
            "consultar_encomendas",
            "consultar_financeiro",
            "calcular_custos",
            "gerar_descricao_produto",
            "configurar_sistema",
            "consultar_historico",
            "conversa_geral"
        ],
        "ai_features": [
            "Compreensão de linguagem natural",
            "Classificação automática de intenções",
            "Extração inteligente de entidades",
            "Raciocínio com LLM para casos complexos",
            "Memória de conversação",
            "Aprendizado contínuo",
            "Respostas contextuais",
            "Fallback inteligente"
        ],
        "version": "2.0.0",
        "description": "LUA Super Inteligente - Assistente de IA avançada com vida própria para sistema de joalheria"
    }
    
    return jsonify(capabilities)

@lua_super_bp.route("/lua_super/download/<filename>", methods=["GET"])
def download_report(filename):
    """Download de relatórios gerados"""
    try:
        file_path = os.path.join(REPORTS_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "Arquivo não encontrado"}), 404
    except Exception as e:
        logger.error(f"[LUA SUPER] Erro no download: {str(e)}")
        return jsonify({"error": str(e)}), 500

@lua_super_bp.route("/lua_super/health", methods=["GET"])
def health_check():
    """Verifica a saúde do sistema LUA Super Inteligente"""
    try:
        # Verificar se a IA está funcionando
        test_response = lua_super.ai_engine._classify_intent("teste de saúde")
        
        health_status = {
            "status": "healthy",
            "ai_engine": "operational",
            "intent_classification": "working" if test_response else "error",
            "conversation_memory_size": len(lua_super.conversation_memory),
            "learning_data_size": len(lua_super.learning_data),
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0"
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"[LUA SUPER] Erro no health check: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

