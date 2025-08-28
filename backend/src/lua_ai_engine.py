# backend/src/lua_ai_engine.py

import os
import re
import json
import openai
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

# Importar modelos do banco de dados
from src.models.user import db
from src.models.employee import Employee
from src.models.caixa import CaixaTransaction
from src.models.inventory import Inventory
from src.models.order import Order
from src.models.cost import Cost, Profit
from src.models.payment import Payment
from src.models.payroll import Payroll
from src.models.financial import FinancialTransaction
from src.models.vale import Vale
from src.models.material import Material
from src.models.jewelry import Jewelry

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Intent:
    """Representa uma intenção identificada no comando do usuário"""
    name: str
    confidence: float
    entities: Dict[str, Any]
    
@dataclass
class AIResponse:
    """Resposta estruturada da IA"""
    message: str
    status: str
    data: Optional[Dict[str, Any]] = None
    action_taken: Optional[str] = None
    download_url: Optional[str] = None
    show_in_interface: bool = False
    tipo: Optional[str] = None

class LuaAIEngine:
    """Motor de IA avançado para a LUA com capacidades de PLN e raciocínio"""
    
    def __init__(self):
        # Configurar cliente OpenAI
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
        # Contexto da conversa
        self.conversation_context = []
        
        # Mapeamento de intenções para ações
        self.intent_action_map = {
            'registrar_vale': self._handle_vale_action,
            'gerar_relatorio': self._handle_report_action,
            'consultar_estoque': self._handle_inventory_action,
            'consultar_vendas': self._handle_sales_action,
            'consultar_funcionarios': self._handle_employees_action,
            'consultar_encomendas': self._handle_orders_action,
            'consultar_financeiro': self._handle_financial_action,
            'calcular_custos': self._handle_cost_calculation_action,
            'gerar_descricao_produto': self._handle_product_description_action,
            'configurar_sistema': self._handle_system_config_action,
            'consultar_historico': self._handle_history_action,
        }
        
        # Padrões de entidades
        self.entity_patterns = {
            'valor': [
                r'(?:r\$|rs|reais?)\s*(\d+(?:[.,]\d{2})?)',
                r'(\d+(?:[.,]\d{2})?)\s*(?:r\$|rs|reais?)',
                r'(\d+(?:[.,]\d{2})?)'
            ],
            'funcionario': [
                r'(?:para|funcionário|funcionario|empregado)\s+([a-záàâãéèêíìîóòôõúùûç\s]+?)(?:\s+de|\s+no|\s*$)',
                r'([a-záàâãéèêíìîóòôõúùûç]+(?:\s+[a-záàâãéèêíìîóòôõúùûç]+)*)'
            ],
            'data': [
                r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
                r'(hoje|ontem|amanhã|esta semana|semana passada|este mês|mês passado)'
            ],
            'tipo_relatorio': [
                r'relatório\s+(?:de\s+)?(\w+)',
                r'relatorio\s+(?:de\s+)?(\w+)'
            ]
        }

    def process_command(self, user_input: str) -> AIResponse:
        """Processa um comando do usuário usando IA avançada"""
        try:
            logger.info(f"Processando comando: {user_input}")
            
            # Adicionar ao contexto da conversa
            self.conversation_context.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Manter apenas os últimos 10 turnos de conversa
            if len(self.conversation_context) > 20:
                self.conversation_context = self.conversation_context[-20:]
            
            # Classificar intenção usando IA
            intent = self._classify_intent(user_input)
            logger.info(f"Intenção identificada: {intent.name} (confiança: {intent.confidence})")
            
            # Se a confiança for muito baixa, usar raciocínio com LLM
            if intent.confidence < 0.6:
                return self._handle_with_llm_reasoning(user_input)
            
            # Executar ação baseada na intenção
            if intent.name in self.intent_action_map:
                response = self.intent_action_map[intent.name](user_input, intent.entities)
            else:
                response = self._handle_unknown_intent(user_input, intent)
            
            # Adicionar resposta ao contexto
            self.conversation_context.append({
                'role': 'assistant',
                'content': response.message,
                'timestamp': datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar comando: {str(e)}")
            return AIResponse(
                message=f"Desculpe, ocorreu um erro ao processar seu comando: {str(e)}",
                status="error"
            )

    def _classify_intent(self, user_input: str) -> Intent:
        """Classifica a intenção do usuário usando IA"""
        try:
            # Prompt para classificação de intenção
            system_prompt = """Você é um assistente especializado em classificar intenções de comandos para um sistema de joalheria.

Analise o comando do usuário e classifique em uma das seguintes intenções:

1. registrar_vale - Registrar vale/adiantamento para funcionário
2. gerar_relatorio - Gerar relatórios (financeiro, estoque, vendas, etc.)
3. consultar_estoque - Consultar inventário/estoque
4. consultar_vendas - Consultar vendas/pedidos
5. consultar_funcionarios - Consultar informações de funcionários
6. consultar_encomendas - Consultar encomendas
7. consultar_financeiro - Consultar informações financeiras
8. calcular_custos - Calcular custos e lucros
9. gerar_descricao_produto - Gerar descrição de produtos
10. configurar_sistema - Configurar sistema
11. consultar_historico - Consultar histórico
12. conversa_geral - Conversa geral/saudações

Responda APENAS com um JSON no formato:
{
    "intent": "nome_da_intencao",
    "confidence": 0.95,
    "entities": {
        "valor": "500.00",
        "funcionario": "João",
        "tipo_relatorio": "financeiro"
    }
}

Extraia também as entidades relevantes do comando."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            # Parsear resposta JSON
            result = json.loads(response.choices[0].message.content.strip())
            
            return Intent(
                name=result.get('intent', 'conversa_geral'),
                confidence=result.get('confidence', 0.5),
                entities=result.get('entities', {})
            )
            
        except Exception as e:
            logger.error(f"Erro na classificação de intenção: {str(e)}")
            # Fallback para classificação baseada em regras
            return self._classify_intent_fallback(user_input)

    def _classify_intent_fallback(self, user_input: str) -> Intent:
        """Classificação de intenção usando regras (fallback)"""
        user_input_lower = user_input.lower()
        entities = {}
        
        # Extrair entidades usando regex
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_input_lower)
                if match:
                    entities[entity_type] = match.group(1).strip()
                    break
        
        # Classificar intenção baseada em palavras-chave
        if any(word in user_input_lower for word in ['vale', 'adiantamento']):
            return Intent('registrar_vale', 0.8, entities)
        elif any(word in user_input_lower for word in ['relatório', 'relatorio']):
            return Intent('gerar_relatorio', 0.8, entities)
        elif any(word in user_input_lower for word in ['estoque', 'inventário', 'inventario']):
            return Intent('consultar_estoque', 0.8, entities)
        elif 'vendas' in user_input_lower:
            return Intent('consultar_vendas', 0.8, entities)
        elif any(word in user_input_lower for word in ['funcionário', 'funcionario', 'empregado']):
            return Intent('consultar_funcionarios', 0.8, entities)
        elif 'encomendas' in user_input_lower:
            return Intent('consultar_encomendas', 0.8, entities)
        elif any(word in user_input_lower for word in ['financeiro', 'caixa', 'dinheiro']):
            return Intent('consultar_financeiro', 0.8, entities)
        elif any(word in user_input_lower for word in ['custo', 'lucro', 'margem']):
            return Intent('calcular_custos', 0.8, entities)
        elif any(word in user_input_lower for word in ['descrição', 'descricao', 'produto']):
            return Intent('gerar_descricao_produto', 0.8, entities)
        elif any(word in user_input_lower for word in ['configurar', 'configuração', 'configuracao']):
            return Intent('configurar_sistema', 0.8, entities)
        elif any(word in user_input_lower for word in ['histórico', 'historico']):
            return Intent('consultar_historico', 0.8, entities)
        else:
            return Intent('conversa_geral', 0.3, entities)

    def _handle_with_llm_reasoning(self, user_input: str) -> AIResponse:
        """Usa LLM para raciocinar sobre comandos complexos ou não reconhecidos"""
        try:
            # Obter informações do sistema para contexto
            system_info = self._get_system_context()
            
            system_prompt = f"""Você é LUA, uma assistente de IA avançada para um sistema de joalheria. Você tem acesso às seguintes funcionalidades:

FUNCIONALIDADES DISPONÍVEIS:
- Registrar vales/adiantamentos para funcionários
- Gerar relatórios (financeiro, estoque, vendas, funcionários)
- Consultar estoque/inventário
- Consultar vendas e encomendas
- Consultar informações de funcionários
- Calcular custos e lucros
- Gerar descrições de produtos
- Configurar sistema

CONTEXTO ATUAL DO SISTEMA:
{json.dumps(system_info, indent=2, ensure_ascii=False)}

HISTÓRICO DA CONVERSA:
{json.dumps(self.conversation_context[-6:], indent=2, ensure_ascii=False)}

Analise o comando do usuário e:
1. Se for possível executar com as funcionalidades disponíveis, explique como faria
2. Se não for possível, explique por que e sugira alternativas
3. Seja sempre útil e proativa
4. Mantenha o tom profissional mas amigável

Responda em português brasileiro."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Tentar identificar se a IA sugeriu uma ação específica
            action_suggestions = self._extract_action_suggestions(ai_response, user_input)
            
            return AIResponse(
                message=ai_response,
                status="success",
                data=action_suggestions,
                action_taken="llm_reasoning"
            )
            
        except Exception as e:
            logger.error(f"Erro no raciocínio com LLM: {str(e)}")
            return AIResponse(
                message="Desculpe, não consegui processar completamente seu comando. Pode tentar reformular ou ser mais específico?",
                status="info"
            )

    def _extract_action_suggestions(self, ai_response: str, user_input: str) -> Optional[Dict[str, Any]]:
        """Extrai sugestões de ação da resposta da IA"""
        suggestions = {}
        
        # Verificar se a IA mencionou funcionalidades específicas
        if 'relatório' in ai_response.lower():
            suggestions['suggested_action'] = 'gerar_relatorio'
        elif 'vale' in ai_response.lower():
            suggestions['suggested_action'] = 'registrar_vale'
        elif 'estoque' in ai_response.lower():
            suggestions['suggested_action'] = 'consultar_estoque'
        
        return suggestions if suggestions else None

    def _get_system_context(self) -> Dict[str, Any]:
        """Obtém contexto atual do sistema para fornecer à IA"""
        try:
            context = {
                'timestamp': datetime.now().isoformat(),
                'funcionarios_ativos': Employee.query.filter_by(active=True).count(),
                'total_funcionarios': Employee.query.count(),
                'itens_estoque': Inventory.query.count(),
                'pedidos_pendentes': Order.query.filter_by(status='pending').count(),
                'vales_mes_atual': Vale.query.filter(
                    Vale.date >= datetime.now().replace(day=1)
                ).count()
            }
            return context
        except Exception as e:
            logger.error(f"Erro ao obter contexto do sistema: {str(e)}")
            return {'error': 'Não foi possível obter contexto do sistema'}

    # Implementações das ações específicas
    def _handle_vale_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de registrar vale"""
        # Importar função existente
        from src.lua_module_enhanced import handle_vale_command
        
        try:
            result = handle_vale_command(user_input)
            return AIResponse(
                message=result.get('message', 'Vale processado com sucesso'),
                status=result.get('status', 'success'),
                data=result.get('data'),
                download_url=result.get('download_url'),
                action_taken='registrar_vale'
            )
        except Exception as e:
            return AIResponse(
                message=f"Erro ao processar vale: {str(e)}",
                status="error"
            )

    def _handle_report_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de gerar relatório"""
        from src.lua_module_enhanced import handle_report_command
        
        try:
            result = handle_report_command(user_input)
            return AIResponse(
                message=result.get('message', 'Relatório gerado com sucesso'),
                status=result.get('status', 'success'),
                data=result.get('data'),
                download_url=result.get('download_url'),
                action_taken='gerar_relatorio'
            )
        except Exception as e:
            return AIResponse(
                message=f"Erro ao gerar relatório: {str(e)}",
                status="error"
            )

    def _handle_inventory_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de consultar estoque"""
        from src.lua_module_enhanced import handle_inventory_command
        
        try:
            result = handle_inventory_command(user_input)
            return AIResponse(
                message=result.get('message', 'Consulta de estoque realizada'),
                status=result.get('status', 'success'),
                data=result.get('data'),
                show_in_interface=True,
                tipo='estoque',
                action_taken='consultar_estoque'
            )
        except Exception as e:
            return AIResponse(
                message=f"Erro ao consultar estoque: {str(e)}",
                status="error"
            )

    def _handle_sales_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de consultar vendas"""
        from src.lua_module_enhanced import handle_sales_command
        
        try:
            result = handle_sales_command(user_input)
            return AIResponse(
                message=result.get('message', 'Consulta de vendas realizada'),
                status=result.get('status', 'success'),
                data=result.get('data'),
                show_in_interface=True,
                tipo='vendas',
                action_taken='consultar_vendas'
            )
        except Exception as e:
            return AIResponse(
                message=f"Erro ao consultar vendas: {str(e)}",
                status="error"
            )

    def _handle_employees_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de consultar funcionários"""
        try:
            employees = Employee.query.filter_by(active=True).all()
            employees_data = [
                {
                    'id': emp.id,
                    'name': emp.name,
                    'position': getattr(emp, 'position', 'N/A'),
                    'salary': getattr(emp, 'salary', 0),
                    'hire_date': emp.hire_date.strftime('%d/%m/%Y') if hasattr(emp, 'hire_date') and emp.hire_date else 'N/A'
                }
                for emp in employees
            ]
            
            return AIResponse(
                message=f"Encontrados {len(employees_data)} funcionários ativos",
                status="success",
                data=employees_data,
                show_in_interface=True,
                tipo='funcionarios',
                action_taken='consultar_funcionarios'
            )
        except Exception as e:
            return AIResponse(
                message=f"Erro ao consultar funcionários: {str(e)}",
                status="error"
            )

    def _handle_orders_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de consultar encomendas"""
        from src.lua_module_enhanced import handle_encomendas_command
        
        try:
            result = handle_encomendas_command(user_input)
            return AIResponse(
                message=result.get('message', 'Consulta de encomendas realizada'),
                status=result.get('status', 'success'),
                data=result.get('data'),
                show_in_interface=True,
                tipo='encomendas',
                action_taken='consultar_encomendas'
            )
        except Exception as e:
            return AIResponse(
                message=f"Erro ao consultar encomendas: {str(e)}",
                status="error"
            )

    def _handle_financial_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de consultar informações financeiras"""
        try:
            transactions = CaixaTransaction.query.all()
            total_entradas = sum(t.amount for t in transactions if t.amount > 0)
            total_saidas = sum(abs(t.amount) for t in transactions if t.amount < 0)
            saldo = total_entradas - total_saidas
            
            financial_data = {
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_atual': saldo,
                'total_transacoes': len(transactions),
                'resumo': f'Entradas: R$ {total_entradas:.2f}, Saídas: R$ {total_saidas:.2f}, Saldo: R$ {saldo:.2f}'
            }
            
            return AIResponse(
                message=f"Situação financeira atual: {financial_data['resumo']}",
                status="success",
                data=financial_data,
                action_taken='consultar_financeiro'
            )
        except Exception as e:
            return AIResponse(
                message=f"Erro ao consultar informações financeiras: {str(e)}",
                status="error"
            )

    def _handle_cost_calculation_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de calcular custos"""
        return AIResponse(
            message="Funcionalidade de cálculo de custos em desenvolvimento. Em breve estará disponível!",
            status="info",
            action_taken='calcular_custos'
        )

    def _handle_product_description_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de gerar descrição de produto"""
        try:
            # Usar IA para gerar descrição criativa
            product_prompt = f"""Gere uma descrição atrativa e profissional para um produto de joalheria baseado neste comando: {user_input}

A descrição deve:
- Ser elegante e sofisticada
- Destacar qualidade e exclusividade
- Mencionar materiais nobres
- Ser adequada para um catálogo de joalheria
- Ter entre 50-100 palavras

Responda apenas com a descrição, sem explicações adicionais."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": product_prompt}],
                temperature=0.8,
                max_tokens=200
            )
            
            description = response.choices[0].message.content.strip()
            
            return AIResponse(
                message=f"Descrição gerada com sucesso:\n\n{description}",
                status="success",
                data={'description': description},
                action_taken='gerar_descricao_produto'
            )
        except Exception as e:
            return AIResponse(
                message=f"Erro ao gerar descrição: {str(e)}",
                status="error"
            )

    def _handle_system_config_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de configurar sistema"""
        return AIResponse(
            message="Funcionalidade de configuração do sistema em desenvolvimento. Em breve estará disponível!",
            status="info",
            action_taken='configurar_sistema'
        )

    def _handle_history_action(self, user_input: str, entities: Dict[str, Any]) -> AIResponse:
        """Implementa ação de consultar histórico"""
        from src.lua_module_enhanced import handle_pdf_history_command
        
        try:
            result = handle_pdf_history_command(user_input)
            return AIResponse(
                message=result.get('message', 'Consulta de histórico realizada'),
                status=result.get('status', 'success'),
                data=result.get('data'),
                action_taken='consultar_historico'
            )
        except Exception as e:
            return AIResponse(
                message=f"Erro ao consultar histórico: {str(e)}",
                status="error"
            )

    def _handle_unknown_intent(self, user_input: str, intent: Intent) -> AIResponse:
        """Lida com intenções não reconhecidas usando raciocínio com IA"""
        return self._handle_with_llm_reasoning(user_input)

# Instância global do motor de IA
lua_ai_engine = LuaAIEngine()

