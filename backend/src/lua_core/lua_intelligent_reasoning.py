# backend/src/lua_intelligent_reasoning.py

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import difflib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ReasoningResult:
    """Resultado do processo de raciocínio"""
    action: str
    confidence: float
    parameters: Dict[str, Any]
    reasoning: str
    suggestions: List[str]
    requires_confirmation: bool = False

class LuaIntelligentReasoning:
    """Sistema de raciocínio inteligente para a LUA"""
    
    def __init__(self):
        # Base de conhecimento sobre o sistema
        self.system_knowledge = self._load_system_knowledge()
        
        # Histórico de comandos para aprendizado
        self.command_history = []
        
        # Padrões de similaridade
        self.similarity_threshold = 0.6
        
        # Cache de raciocínio
        self.reasoning_cache = {}
    
    def _load_system_knowledge(self) -> Dict[str, Any]:
        """Carrega base de conhecimento sobre o sistema"""
        return {
            'actions': {
                'registrar_vale': {
                    'description': 'Registra um vale/adiantamento para funcionário',
                    'required_params': ['funcionario', 'valor'],
                    'optional_params': ['descricao', 'data'],
                    'synonyms': ['vale', 'adiantamento', 'empréstimo', 'antecipação'],
                    'examples': [
                        'adiciona vale para João de R$500',
                        'registra adiantamento de 300 reais para Maria',
                        'cria vale de 200 para Pedro'
                    ]
                },
                'gerar_relatorio': {
                    'description': 'Gera relatórios do sistema',
                    'required_params': ['tipo'],
                    'optional_params': ['periodo', 'formato'],
                    'synonyms': ['relatório', 'report', 'documento', 'listagem'],
                    'types': ['caixa', 'financeiro', 'vendas', 'estoque', 'funcionarios'],
                    'examples': [
                        'gera relatório de caixa',
                        'relatório financeiro em PDF',
                        'mostra relatório de vendas'
                    ]
                },
                'consultar_dados': {
                    'description': 'Consulta informações do sistema',
                    'required_params': ['tipo_consulta'],
                    'optional_params': ['filtros'],
                    'synonyms': ['consulta', 'busca', 'mostra', 'lista', 'ver'],
                    'types': ['estoque', 'funcionarios', 'vendas', 'caixa', 'encomendas'],
                    'examples': [
                        'mostra estoque',
                        'lista funcionários',
                        'consulta vendas do mês'
                    ]
                },
                'calcular_valores': {
                    'description': 'Realiza cálculos financeiros',
                    'required_params': ['tipo_calculo'],
                    'optional_params': ['parametros'],
                    'synonyms': ['calcula', 'soma', 'subtrai', 'multiplica', 'divide'],
                    'examples': [
                        'calcula lucro do mês',
                        'soma total de vendas',
                        'calcula comissão'
                    ]
                },
                'configurar_sistema': {
                    'description': 'Configura parâmetros do sistema',
                    'required_params': ['configuracao'],
                    'optional_params': ['valor'],
                    'synonyms': ['configura', 'ajusta', 'define', 'altera'],
                    'examples': [
                        'configura desconto padrão',
                        'ajusta margem de lucro',
                        'define alerta de estoque'
                    ]
                }
            },
            'entities': {
                'funcionario': {
                    'patterns': [r'(?:para|funcionário|funcionario)\s+([A-Za-zÀ-ÿ\s]+)', r'([A-Za-zÀ-ÿ]+)\s+(?:recebe|ganha)'],
                    'validation': 'nome_valido'
                },
                'valor': {
                    'patterns': [r'R?\$?\s*(\d+(?:[.,]\d{2})?)', r'(\d+)\s*reais?'],
                    'validation': 'valor_positivo'
                },
                'data': {
                    'patterns': [r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', r'(hoje|ontem|amanhã)'],
                    'validation': 'data_valida'
                },
                'periodo': {
                    'patterns': [r'(semana|mês|ano|trimestre)', r'últimos?\s+(\d+)\s+(dias?|semanas?|meses?)'],
                    'validation': 'periodo_valido'
                }
            },
            'business_rules': {
                'vale_maximo': 5000.0,
                'vale_minimo': 10.0,
                'formatos_relatorio': ['pdf', 'excel', 'csv'],
                'tipos_relatorio_validos': ['caixa', 'financeiro', 'vendas', 'estoque', 'funcionarios']
            }
        }
    
    def reason_about_command(self, text: str, intent_result: Optional[Dict] = None) -> ReasoningResult:
        """Raciocina sobre um comando e determina a melhor ação"""
        try:
            # Verificar cache
            cache_key = f"reasoning_{text.lower()}"
            if cache_key in self.reasoning_cache:
                return self.reasoning_cache[cache_key]
            
            # Analisar comando
            analysis = self._analyze_command_structure(text)
            
            # Tentar mapear para ação conhecida
            action_mapping = self._map_to_known_action(text, analysis, intent_result)
            
            if action_mapping['confidence'] > 0.5:
                result = self._create_reasoning_result(action_mapping, analysis)
            else:
                # Usar raciocínio avançado
                result = self._advanced_reasoning(text, analysis, intent_result)
            
            # Salvar no cache
            self.reasoning_cache[cache_key] = result
            
            # Adicionar ao histórico para aprendizado
            self._add_to_history(text, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no raciocínio: {str(e)}")
            return ReasoningResult(
                action="error",
                confidence=0.0,
                parameters={},
                reasoning=f"Erro no processamento: {str(e)}",
                suggestions=["Tente reformular o comando", "Verifique a sintaxe"]
            )
    
    def _analyze_command_structure(self, text: str) -> Dict[str, Any]:
        """Analisa a estrutura do comando"""
        analysis = {
            'verbs': [],
            'nouns': [],
            'numbers': [],
            'entities': {},
            'keywords': [],
            'sentence_type': 'declarative'
        }
        
        # Extrair verbos comuns
        verb_patterns = [
            r'\b(adiciona|registra|cria|gera|mostra|lista|consulta|calcula|configura|define|altera|atualiza|remove|deleta)\b'
        ]
        
        for pattern in verb_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            analysis['verbs'].extend(matches)
        
        # Extrair substantivos relevantes
        noun_patterns = [
            r'\b(vale|relatório|relatorio|estoque|funcionário|funcionario|venda|caixa|encomenda|cliente|produto)\b'
        ]
        
        for pattern in noun_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            analysis['nouns'].extend(matches)
        
        # Extrair números
        number_patterns = [r'\b\d+(?:[.,]\d{2})?\b', r'R\$\s*\d+(?:[.,]\d{2})?']
        
        for pattern in number_patterns:
            matches = re.findall(pattern, text)
            analysis['numbers'].extend(matches)
        
        # Determinar tipo de sentença
        if text.strip().endswith('?'):
            analysis['sentence_type'] = 'question'
        elif any(word in text.lower() for word in ['por favor', 'pode', 'consegue']):
            analysis['sentence_type'] = 'request'
        elif any(word in text.lower() for word in ['adiciona', 'registra', 'cria']):
            analysis['sentence_type'] = 'command'
        
        return analysis
    
    def _map_to_known_action(self, text: str, analysis: Dict, intent_result: Optional[Dict] = None) -> Dict[str, Any]:
        """Mapeia comando para ação conhecida"""
        text_lower = text.lower()
        best_match = {'action': 'unknown', 'confidence': 0.0, 'reasoning': ''}
        
        # Usar resultado de intenção se disponível
        if intent_result and intent_result.get('confidence', 0) > 0.5:
            action = intent_result.get('intent', 'unknown')
            if action in self.system_knowledge['actions']:
                return {
                    'action': action,
                    'confidence': intent_result['confidence'],
                    'reasoning': f"Mapeado via classificação de intenção: {action}"
                }
        
        # Mapear baseado em verbos e substantivos
        for action_name, action_info in self.system_knowledge['actions'].items():
            confidence = 0.0
            reasoning_parts = []
            
            # Verificar sinônimos
            for synonym in action_info['synonyms']:
                if synonym.lower() in text_lower:
                    confidence += 0.3
                    reasoning_parts.append(f"palavra-chave '{synonym}' encontrada")
            
            # Verificar exemplos similares
            for example in action_info['examples']:
                similarity = difflib.SequenceMatcher(None, text_lower, example.lower()).ratio()
                if similarity > self.similarity_threshold:
                    confidence += similarity * 0.4
                    reasoning_parts.append(f"similar ao exemplo '{example}' ({similarity:.2f})")
            
            # Verificar estrutura do comando
            if action_name == 'registrar_vale':
                if any(verb in analysis['verbs'] for verb in ['adiciona', 'registra', 'cria']):
                    if any(noun in analysis['nouns'] for noun in ['vale']):
                        if analysis['numbers']:
                            confidence += 0.5
                            reasoning_parts.append("estrutura de comando de vale detectada")
            
            elif action_name == 'gerar_relatorio':
                if any(verb in analysis['verbs'] for verb in ['gera', 'mostra']):
                    if any(noun in analysis['nouns'] for noun in ['relatório', 'relatorio']):
                        confidence += 0.5
                        reasoning_parts.append("estrutura de comando de relatório detectada")
            
            elif action_name == 'consultar_dados':
                if any(verb in analysis['verbs'] for verb in ['mostra', 'lista', 'consulta']):
                    if any(noun in analysis['nouns'] for noun in ['estoque', 'funcionário', 'funcionario']):
                        confidence += 0.4
                        reasoning_parts.append("estrutura de consulta detectada")
            
            if confidence > best_match['confidence']:
                best_match = {
                    'action': action_name,
                    'confidence': confidence,
                    'reasoning': '; '.join(reasoning_parts)
                }
        
        return best_match
    
    def _advanced_reasoning(self, text: str, analysis: Dict, intent_result: Optional[Dict] = None) -> ReasoningResult:
        """Raciocínio avançado para comandos não mapeados"""
        
        # Tentar inferir ação baseado no contexto
        inferred_actions = []
        
        # Análise baseada em verbos
        if analysis['verbs']:
            for verb in analysis['verbs']:
                if verb.lower() in ['adiciona', 'registra', 'cria', 'insere']:
                    if analysis['numbers'] and any(word in text.lower() for word in ['funcionário', 'funcionario', 'pessoa', 'nome']):
                        inferred_actions.append({
                            'action': 'registrar_vale',
                            'confidence': 0.6,
                            'reasoning': f"Verbo '{verb}' + número + referência a pessoa sugere registro de vale"
                        })
                    else:
                        inferred_actions.append({
                            'action': 'criar_registro',
                            'confidence': 0.4,
                            'reasoning': f"Verbo '{verb}' sugere criação de registro"
                        })
                
                elif verb.lower() in ['mostra', 'lista', 'exibe', 'consulta']:
                    inferred_actions.append({
                        'action': 'consultar_dados',
                        'confidence': 0.5,
                        'reasoning': f"Verbo '{verb}' sugere consulta de dados"
                    })
                
                elif verb.lower() in ['gera', 'cria', 'produz']:
                    if any(word in text.lower() for word in ['relatório', 'relatorio', 'documento']):
                        inferred_actions.append({
                            'action': 'gerar_relatorio',
                            'confidence': 0.7,
                            'reasoning': f"Verbo '{verb}' + referência a documento sugere geração de relatório"
                        })
                
                elif verb.lower() in ['calcula', 'soma', 'conta']:
                    inferred_actions.append({
                        'action': 'calcular_valores',
                        'confidence': 0.6,
                        'reasoning': f"Verbo '{verb}' sugere cálculo"
                    })
        
        # Análise baseada em substantivos
        if analysis['nouns']:
            for noun in analysis['nouns']:
                if noun.lower() == 'vale' and analysis['numbers']:
                    inferred_actions.append({
                        'action': 'registrar_vale',
                        'confidence': 0.7,
                        'reasoning': f"Substantivo '{noun}' + número sugere registro de vale"
                    })
                elif noun.lower() in ['relatório', 'relatorio'] and not any(a['action'] == 'gerar_relatorio' for a in inferred_actions):
                    inferred_actions.append({
                        'action': 'gerar_relatorio',
                        'confidence': 0.6,
                        'reasoning': f"Substantivo '{noun}' sugere geração de relatório"
                    })
        
        # Análise baseada em padrões de pergunta
        if analysis['sentence_type'] == 'question':
            if any(word in text.lower() for word in ['quanto', 'qual', 'como']):
                inferred_actions.append({
                    'action': 'consultar_dados',
                    'confidence': 0.5,
                    'reasoning': "Pergunta sugere consulta de informações"
                })
        
        # Selecionar melhor ação inferida
        if inferred_actions:
            best_action = max(inferred_actions, key=lambda x: x['confidence'])
            
            if best_action['confidence'] > 0.4:
                return ReasoningResult(
                    action=best_action['action'],
                    confidence=best_action['confidence'],
                    parameters=self._extract_parameters_for_action(text, best_action['action']),
                    reasoning=best_action['reasoning'],
                    suggestions=self._generate_suggestions(best_action['action']),
                    requires_confirmation=best_action['confidence'] < 0.7
                )
        
        # Se não conseguiu inferir, usar estratégia de fallback
        return self._fallback_strategy(text, analysis)
    
    def _fallback_strategy(self, text: str, analysis: Dict) -> ReasoningResult:
        """Estratégia de fallback quando não consegue determinar ação"""
        
        # Tentar encontrar comandos similares no histórico
        similar_commands = self._find_similar_commands(text)
        
        if similar_commands:
            best_similar = similar_commands[0]
            return ReasoningResult(
                action="suggest_similar",
                confidence=0.3,
                parameters={'similar_command': best_similar},
                reasoning=f"Comando similar encontrado no histórico: '{best_similar['text']}'",
                suggestions=[
                    f"Você quis dizer: {best_similar['text']}?",
                    "Reformular comando",
                    "Ver ajuda"
                ],
                requires_confirmation=True
            )
        
        # Analisar componentes e sugerir ações possíveis
        possible_actions = []
        
        if analysis['numbers']:
            possible_actions.append("Registrar vale com valor especificado")
        
        if any(word in text.lower() for word in ['relatório', 'relatorio', 'documento']):
            possible_actions.append("Gerar relatório")
        
        if any(word in text.lower() for word in ['mostra', 'lista', 'ver']):
            possible_actions.append("Consultar dados")
        
        if not possible_actions:
            possible_actions = [
                "Registrar vale para funcionário",
                "Gerar relatório",
                "Consultar dados do sistema",
                "Ver ajuda"
            ]
        
        return ReasoningResult(
            action="request_clarification",
            confidence=0.2,
            parameters={'original_text': text},
            reasoning=f"Não foi possível determinar ação específica para: '{text}'",
            suggestions=possible_actions,
            requires_confirmation=False
        )
    
    def _extract_parameters_for_action(self, text: str, action: str) -> Dict[str, Any]:
        """Extrai parâmetros específicos para uma ação"""
        parameters = {}
        
        if action == 'registrar_vale':
            # Extrair funcionário
            funcionario_patterns = [
                r'(?:para|funcionário|funcionario)\s+([A-Za-zÀ-ÿ\s]+?)(?:\s+de|\s+R\$|\s+\d|$)',
                r'([A-Za-zÀ-ÿ]+)\s+(?:recebe|ganha|de)\s+(?:R\$|\d)'
            ]
            
            for pattern in funcionario_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    parameters['funcionario'] = match.group(1).strip().title()
                    break
            
            # Extrair valor
            valor_patterns = [
                r'R?\$?\s*(\d+(?:[.,]\d{2})?)',
                r'(\d+)\s*reais?'
            ]
            
            for pattern in valor_patterns:
                match = re.search(pattern, text)
                if match:
                    valor_str = match.group(1).replace(',', '.')
                    try:
                        parameters['valor'] = float(valor_str)
                    except:
                        pass
                    break
        
        elif action == 'gerar_relatorio':
            # Extrair tipo de relatório
            tipo_patterns = [
                r'relatório\s+(?:de\s+)?([A-Za-zÀ-ÿ\s]+?)(?:\s|$)',
                r'(?:gera|gerar|mostra|mostrar)\s+relatório\s+(?:de\s+)?([A-Za-zÀ-ÿ\s]+)'
            ]
            
            for pattern in tipo_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    tipo = match.group(1).strip().lower()
                    # Mapear para tipos válidos
                    tipo_mapping = {
                        'caixa': 'caixa',
                        'financeiro': 'financeiro',
                        'vendas': 'vendas',
                        'estoque': 'estoque',
                        'funcionários': 'funcionarios',
                        'funcionarios': 'funcionarios'
                    }
                    parameters['tipo'] = tipo_mapping.get(tipo, tipo)
                    break
            
            # Extrair formato
            if any(word in text.lower() for word in ['pdf']):
                parameters['formato'] = 'pdf'
            elif any(word in text.lower() for word in ['excel', 'xlsx']):
                parameters['formato'] = 'excel'
            elif any(word in text.lower() for word in ['csv']):
                parameters['formato'] = 'csv'
        
        elif action == 'consultar_dados':
            # Determinar tipo de consulta
            if any(word in text.lower() for word in ['estoque', 'inventário']):
                parameters['tipo'] = 'estoque'
            elif any(word in text.lower() for word in ['funcionário', 'funcionarios']):
                parameters['tipo'] = 'funcionarios'
            elif any(word in text.lower() for word in ['vendas', 'venda']):
                parameters['tipo'] = 'vendas'
            elif any(word in text.lower() for word in ['caixa', 'saldo']):
                parameters['tipo'] = 'caixa'
            elif any(word in text.lower() for word in ['encomenda', 'encomendas']):
                parameters['tipo'] = 'encomendas'
        
        return parameters
    
    def _generate_suggestions(self, action: str) -> List[str]:
        """Gera sugestões baseadas na ação"""
        suggestions_map = {
            'registrar_vale': [
                "Adicionar vale para João de R$500",
                "Registrar adiantamento para funcionário",
                "Criar vale com descrição"
            ],
            'gerar_relatorio': [
                "Gerar relatório de caixa em PDF",
                "Relatório financeiro do mês",
                "Mostrar relatório de vendas"
            ],
            'consultar_dados': [
                "Mostrar estoque atual",
                "Listar funcionários ativos",
                "Ver vendas do dia"
            ],
            'calcular_valores': [
                "Calcular lucro do mês",
                "Somar total de vendas",
                "Calcular comissão"
            ]
        }
        
        return suggestions_map.get(action, [
            "Reformular comando",
            "Ver exemplos",
            "Solicitar ajuda"
        ])
    
    def _find_similar_commands(self, text: str) -> List[Dict[str, Any]]:
        """Encontra comandos similares no histórico"""
        similar = []
        
        for entry in self.command_history[-50:]:  # Últimos 50 comandos
            similarity = difflib.SequenceMatcher(None, text.lower(), entry['text'].lower()).ratio()
            if similarity > 0.5:
                similar.append({
                    'text': entry['text'],
                    'action': entry['action'],
                    'similarity': similarity
                })
        
        return sorted(similar, key=lambda x: x['similarity'], reverse=True)
    
    def _create_reasoning_result(self, action_mapping: Dict, analysis: Dict) -> ReasoningResult:
        """Cria resultado de raciocínio baseado no mapeamento de ação"""
        action = action_mapping['action']
        confidence = action_mapping['confidence']
        
        parameters = self._extract_parameters_for_action(analysis.get('original_text', ''), action)
        
        return ReasoningResult(
            action=action,
            confidence=confidence,
            parameters=parameters,
            reasoning=action_mapping['reasoning'],
            suggestions=self._generate_suggestions(action),
            requires_confirmation=confidence < 0.8
        )
    
    def _add_to_history(self, text: str, result: ReasoningResult):
        """Adiciona comando ao histórico para aprendizado"""
        self.command_history.append({
            'text': text,
            'action': result.action,
            'confidence': result.confidence,
            'timestamp': datetime.now().isoformat(),
            'parameters': result.parameters
        })
        
        # Manter apenas últimos 100 comandos
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
    
    def learn_from_feedback(self, original_text: str, correct_action: str, parameters: Dict[str, Any]):
        """Aprende com feedback do usuário"""
        # Adicionar exemplo positivo aos dados de treinamento
        # Isso poderia ser usado para retreinar o modelo
        logger.info(f"Aprendendo: '{original_text}' -> {correct_action} com parâmetros {parameters}")
        
        # Atualizar cache com correção
        cache_key = f"reasoning_{original_text.lower()}"
        if cache_key in self.reasoning_cache:
            self.reasoning_cache[cache_key] = ReasoningResult(
                action=correct_action,
                confidence=1.0,
                parameters=parameters,
                reasoning="Aprendido com feedback do usuário",
                suggestions=[]
            )

# Instância global do sistema de raciocínio
lua_reasoning = LuaIntelligentReasoning()

