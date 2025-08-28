import pickle
import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Tipos de intenção suportados pela IA Lua"""
    CONSULTA_ESTOQUE = "consulta_estoque"
    CONSULTA_VENDAS = "consulta_vendas"
    CONSULTA_FUNCIONARIOS = "consulta_funcionarios"
    CONSULTA_CLIENTES = "consulta_clientes"
    RELATORIO_FINANCEIRO = "relatorio_financeiro"
    AJUDA_SISTEMA = "ajuda_sistema"
    CUMPRIMENTO = "cumprimento"
    DESPEDIDA = "despedida"
    COMANDO_INVALIDO = "comando_invalido"
    PROMPT_INJECTION = "prompt_injection"

class LuaIntentClassifier:
    """Classificador de intenções com guardrails de segurança"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or "src/lua_core/lua_intent_model.pkl"
        self.model = None
        self.load_model()
        
        # Padrões de prompt injection
        self.injection_patterns = [
            r"ignore\s+(previous|all|the)\s+(instructions?|rules?|prompts?)",
            r"forget\s+(everything|all|previous)",
            r"you\s+are\s+now\s+a\s+different",
            r"pretend\s+to\s+be",
            r"act\s+as\s+if",
            r"system\s*:\s*",
            r"admin\s*:\s*",
            r"root\s*:\s*",
            r"execute\s+(sql|query|command)",
            r"drop\s+table",
            r"delete\s+from",
            r"update\s+.*\s+set",
            r"insert\s+into",
            r"<script",
            r"javascript:",
            r"eval\s*\(",
            r"exec\s*\(",
        ]
        
        # Comandos whitelistados
        self.whitelisted_commands = {
            IntentType.CONSULTA_ESTOQUE: [
                "consultar_estoque",
                "verificar_quantidade",
                "listar_joias",
                "buscar_produto"
            ],
            IntentType.CONSULTA_VENDAS: [
                "consultar_vendas",
                "relatorio_vendas",
                "vendas_periodo",
                "vendas_funcionario"
            ],
            IntentType.CONSULTA_FUNCIONARIOS: [
                "listar_funcionarios",
                "buscar_funcionario",
                "consultar_vales",
                "folha_pagamento"
            ],
            IntentType.CONSULTA_CLIENTES: [
                "listar_clientes",
                "buscar_cliente",
                "historico_cliente"
            ],
            IntentType.RELATORIO_FINANCEIRO: [
                "relatorio_caixa",
                "movimento_financeiro",
                "balanco_periodo"
            ]
        }
    
    def load_model(self):
        """Carregar modelo de classificação de intenções"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("Modelo de intenções carregado com sucesso")
        except FileNotFoundError:
            logger.warning(f"Modelo não encontrado em {self.model_path}, usando classificação baseada em regras")
            self.model = None
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            self.model = None
    
    def detect_prompt_injection(self, text: str) -> bool:
        """Detectar tentativas de prompt injection"""
        text_lower = text.lower()
        
        for pattern in self.injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Prompt injection detectado: {pattern}")
                return True
        
        return False
    
    def classify_intent(self, text: str) -> Tuple[IntentType, float]:
        """Classificar intenção do texto de entrada"""
        
        # Verificar prompt injection primeiro
        if self.detect_prompt_injection(text):
            return IntentType.PROMPT_INJECTION, 1.0
        
        # Se temos modelo treinado, usar ele
        if self.model:
            try:
                prediction = self.model.predict([text])
                confidence = self.model.predict_proba([text]).max()
                intent = IntentType(prediction[0])
                return intent, confidence
            except Exception as e:
                logger.error(f"Erro na classificação com modelo: {e}")
        
        # Fallback para classificação baseada em regras
        return self._rule_based_classification(text)
    
    def _rule_based_classification(self, text: str) -> Tuple[IntentType, float]:
        """Classificação baseada em regras como fallback"""
        text_lower = text.lower()
        
        # Padrões de cumprimento
        if any(word in text_lower for word in ['oi', 'olá', 'bom dia', 'boa tarde', 'boa noite']):
            return IntentType.CUMPRIMENTO, 0.8
        
        # Padrões de despedida
        if any(word in text_lower for word in ['tchau', 'até logo', 'obrigado', 'valeu']):
            return IntentType.DESPEDIDA, 0.8
        
        # Padrões de consulta de estoque
        if any(word in text_lower for word in ['estoque', 'quantidade', 'produto', 'joia']):
            return IntentType.CONSULTA_ESTOQUE, 0.7
        
        # Padrões de consulta de vendas
        if any(word in text_lower for word in ['venda', 'vendeu', 'vendido', 'faturamento']):
            return IntentType.CONSULTA_VENDAS, 0.7
        
        # Padrões de consulta de funcionários
        if any(word in text_lower for word in ['funcionário', 'empregado', 'vale', 'salário']):
            return IntentType.CONSULTA_FUNCIONARIOS, 0.7
        
        # Padrões de consulta de clientes
        if any(word in text_lower for word in ['cliente', 'comprador', 'histórico']):
            return IntentType.CONSULTA_CLIENTES, 0.7
        
        # Padrões de relatório financeiro
        if any(word in text_lower for word in ['caixa', 'financeiro', 'dinheiro', 'receita']):
            return IntentType.RELATORIO_FINANCEIRO, 0.7
        
        # Padrões de ajuda
        if any(word in text_lower for word in ['ajuda', 'help', 'como', 'o que']):
            return IntentType.AJUDA_SISTEMA, 0.8
        
        return IntentType.COMANDO_INVALIDO, 0.5
    
    def is_command_whitelisted(self, intent: IntentType, command: str) -> bool:
        """Verificar se comando está na whitelist"""
        if intent not in self.whitelisted_commands:
            return False
        
        return command in self.whitelisted_commands[intent]
    
    def get_allowed_commands(self, intent: IntentType) -> List[str]:
        """Obter lista de comandos permitidos para uma intenção"""
        return self.whitelisted_commands.get(intent, [])

class LuaGuardrails:
    """Sistema de guardrails para a IA Lua"""
    
    def __init__(self):
        self.classifier = LuaIntentClassifier()
        
        # Configurações de segurança
        self.max_input_length = 1000
        self.min_confidence_threshold = 0.6
        
        # Respostas padrão para situações de segurança
        self.security_responses = {
            IntentType.PROMPT_INJECTION: "Desculpe, não posso processar esse tipo de solicitação. Por favor, faça uma pergunta sobre o sistema de joalheria.",
            IntentType.COMANDO_INVALIDO: "Não entendi sua solicitação. Posso ajudar com consultas sobre estoque, vendas, funcionários, clientes ou relatórios financeiros."
        }
    
    def validate_input(self, text: str) -> Tuple[bool, str]:
        """Validar entrada do usuário"""
        
        # Verificar tamanho
        if len(text) > self.max_input_length:
            return False, f"Texto muito longo. Máximo {self.max_input_length} caracteres."
        
        # Verificar se não está vazio
        if not text.strip():
            return False, "Por favor, digite uma pergunta ou comando."
        
        # Classificar intenção
        intent, confidence = self.classifier.classify_intent(text)
        
        # Verificar prompt injection
        if intent == IntentType.PROMPT_INJECTION:
            return False, self.security_responses[IntentType.PROMPT_INJECTION]
        
        # Verificar confiança mínima
        if confidence < self.min_confidence_threshold and intent != IntentType.COMANDO_INVALIDO:
            return False, self.security_responses[IntentType.COMANDO_INVALIDO]
        
        return True, ""
    
    def process_request(self, text: str, user_id: int) -> Dict:
        """Processar solicitação com guardrails"""
        
        # Validar entrada
        is_valid, error_message = self.validate_input(text)
        if not is_valid:
            return {
                "success": False,
                "error": error_message,
                "intent": None,
                "confidence": 0.0
            }
        
        # Classificar intenção
        intent, confidence = self.classifier.classify_intent(text)
        
        # Log da classificação
        logger.info(f"Intent classificado: {intent.value}, confiança: {confidence:.2f}, usuário: {user_id}")
        
        return {
            "success": True,
            "intent": intent,
            "confidence": confidence,
            "allowed_commands": self.classifier.get_allowed_commands(intent),
            "original_text": text
        }

