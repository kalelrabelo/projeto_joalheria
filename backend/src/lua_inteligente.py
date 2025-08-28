from flask import Blueprint, request, jsonify
import re
from datetime import datetime, timedelta
import json

lua_inteligente_bp = Blueprint("lua_inteligente", __name__)

# Simulação de dados do sistema (em produção, viria do banco de dados)
FUNCIONARIOS = [
    {"id": 1, "nome": "João Silva", "cargo": "Vendedor", "salario": 3500, "status": "ativo"},
    {"id": 2, "nome": "Maria Santos", "cargo": "Gerente", "salario": 5500, "status": "ativo"},
    {"id": 3, "nome": "Pedro Costa", "cargo": "Ourives", "salario": 4200, "status": "ativo"},
    {"id": 4, "nome": "Ana Oliveira", "cargo": "Atendente", "salario": 2800, "status": "ativo"}
]

ENCOMENDAS = [
    {"id": 1, "cliente": "Carlos Mendes", "item": "Anel de Ouro 18k", "valor": 1200, "data": "2025-08-22", "status": "pendente"},
    {"id": 2, "cliente": "Lucia Ferreira", "item": "Colar de Prata", "valor": 850, "data": "2025-08-22", "status": "em_producao"},
    {"id": 3, "cliente": "Roberto Lima", "item": "Brincos de Diamante", "valor": 3500, "data": "2025-08-21", "status": "concluido"}
]

VENDAS = [
    {"id": 1, "produto": "Anel Solitário", "valor": 2500, "data": "2025-08-22", "vendedor": "João Silva"},
    {"id": 2, "produto": "Corrente de Ouro", "valor": 1800, "data": "2025-08-22", "vendedor": "Maria Santos"},
    {"id": 3, "produto": "Relógio Feminino", "valor": 950, "data": "2025-08-21", "vendedor": "Ana Oliveira"}
]

ESTOQUE = [
    {"item": "Ouro 18k", "quantidade": "250g", "valor_unitario": 320, "categoria": "metal"},
    {"item": "Prata 925", "quantidade": "500g", "valor_unitario": 8.5, "categoria": "metal"},
    {"item": "Diamantes", "quantidade": "15 unidades", "valor_unitario": 1200, "categoria": "pedra"},
    {"item": "Esmeraldas", "quantidade": "8 unidades", "valor_unitario": 800, "categoria": "pedra"}
]

ENERGIA = {
    "mes_anterior": {"consumo": 1250, "custo": 890.50, "periodo": "julho/2025"},
    "mes_atual": {"consumo": 1180, "custo": 826.00, "periodo": "agosto/2025"}
}

VALES = [
    {"id": 1, "funcionario": "João Silva", "valor": 500, "data": "2025-08-20", "motivo": "Vale alimentação"},
    {"id": 2, "funcionario": "Pedro Costa", "valor": 300, "data": "2025-08-22", "motivo": "Adiantamento salário"}
]

class LuaInteligente:
    def __init__(self):
        self.intencoes = {
            'funcionarios': ['funcionario', 'funcionários', 'empregado', 'empregados', 'colaborador', 'colaboradores', 'equipe', 'staff'],
            'encomendas': ['encomenda', 'encomendas', 'pedido', 'pedidos', 'ordem', 'ordens'],
            'vendas': ['venda', 'vendas', 'vendi', 'vendeu', 'faturamento', 'receita'],
            'estoque': ['estoque', 'inventário', 'inventario', 'material', 'materiais', 'produto', 'produtos'],
            'energia': ['energia', 'luz', 'eletricidade', 'consumo', 'gasto energético', 'conta de luz'],
            'vales': ['vale', 'vales', 'adiantamento', 'adiantamentos', 'empréstimo', 'emprestimo'],
            'financeiro': ['financeiro', 'dinheiro', 'lucro', 'prejuízo', 'balanço', 'resultado'],
            'relatorio': ['relatório', 'relatorio', 'report', 'resumo', 'análise', 'analise']
        }
        
        self.periodos = {
            'hoje': 0,
            'ontem': 1,
            'semana': 7,
            'mês': 30,
            'mes': 30,
            'anterior': 30
        }

    def processar_linguagem_natural(self, mensagem):
        """Processa a mensagem em linguagem natural e identifica a intenção"""
        mensagem_lower = mensagem.lower()
        
        # Identificar intenção principal
        intencao_identificada = None
        for intencao, palavras_chave in self.intencoes.items():
            if any(palavra in mensagem_lower for palavra in palavras_chave):
                intencao_identificada = intencao
                break
        
        # Identificar período temporal
        periodo = self.identificar_periodo(mensagem_lower)
        
        # Identificar se é comparação
        eh_comparacao = any(palavra in mensagem_lower for palavra in ['compare', 'comparar', 'vs', 'versus', 'diferença', 'diferenca'])
        
        return {
            'intencao': intencao_identificada,
            'periodo': periodo,
            'eh_comparacao': eh_comparacao,
            'mensagem_original': mensagem
        }

    def identificar_periodo(self, mensagem):
        """Identifica o período temporal na mensagem"""
        hoje = datetime.now().date()
        
        if 'hoje' in mensagem:
            return {'tipo': 'hoje', 'data': hoje.strftime('%Y-%m-%d')}
        elif 'ontem' in mensagem:
            ontem = hoje - timedelta(days=1)
            return {'tipo': 'ontem', 'data': ontem.strftime('%Y-%m-%d')}
        elif 'semana' in mensagem:
            return {'tipo': 'semana', 'dias': 7}
        elif 'mês' in mensagem or 'mes' in mensagem:
            if 'anterior' in mensagem or 'passado' in mensagem:
                return {'tipo': 'mes_anterior'}
            else:
                return {'tipo': 'mes_atual'}
        
        return {'tipo': 'geral'}

    def buscar_dados(self, intencao, periodo=None):
        """Busca os dados baseado na intenção identificada"""
        
        if intencao == 'funcionarios':
            return {
                'tipo': 'funcionarios',
                'dados': FUNCIONARIOS,
                'total': len(FUNCIONARIOS),
                'resumo': f"Encontrados {len(FUNCIONARIOS)} funcionários ativos"
            }
        
        elif intencao == 'encomendas':
            if periodo and periodo.get('tipo') == 'hoje':
                encomendas_hoje = [e for e in ENCOMENDAS if e['data'] == periodo['data']]
                return {
                    'tipo': 'encomendas',
                    'dados': encomendas_hoje,
                    'total': len(encomendas_hoje),
                    'resumo': f"Encontradas {len(encomendas_hoje)} encomendas para hoje"
                }
            else:
                return {
                    'tipo': 'encomendas',
                    'dados': ENCOMENDAS,
                    'total': len(ENCOMENDAS),
                    'resumo': f"Total de {len(ENCOMENDAS)} encomendas"
                }
        
        elif intencao == 'vendas':
            if periodo and periodo.get('tipo') == 'hoje':
                vendas_hoje = [v for v in VENDAS if v['data'] == periodo['data']]
                total_vendas = sum(v['valor'] for v in vendas_hoje)
                return {
                    'tipo': 'vendas',
                    'dados': vendas_hoje,
                    'total': len(vendas_hoje),
                    'valor_total': total_vendas,
                    'resumo': f"Vendas de hoje: {len(vendas_hoje)} itens, R$ {total_vendas:,.2f}"
                }
            else:
                total_vendas = sum(v['valor'] for v in VENDAS)
                return {
                    'tipo': 'vendas',
                    'dados': VENDAS,
                    'total': len(VENDAS),
                    'valor_total': total_vendas,
                    'resumo': f"Total de vendas: {len(VENDAS)} itens, R$ {total_vendas:,.2f}"
                }
        
        elif intencao == 'estoque':
            return {
                'tipo': 'estoque',
                'dados': ESTOQUE,
                'total': len(ESTOQUE),
                'resumo': f"Estoque com {len(ESTOQUE)} tipos de materiais"
            }
        
        elif intencao == 'energia':
            return {
                'tipo': 'energia',
                'dados': ENERGIA,
                'resumo': f"Consumo atual: {ENERGIA['mes_atual']['consumo']} kWh (R$ {ENERGIA['mes_atual']['custo']:.2f})"
            }
        
        elif intencao == 'vales':
            total_vales = sum(v['valor'] for v in VALES)
            return {
                'tipo': 'vales',
                'dados': VALES,
                'total': len(VALES),
                'valor_total': total_vales,
                'resumo': f"Total de {len(VALES)} vales, R$ {total_vales:,.2f}"
            }
        
        return {
            'tipo': 'nao_encontrado',
            'dados': [],
            'resumo': "Não consegui identificar o que você está procurando"
        }

    def gerar_comparacao_energia(self):
        """Gera comparação de energia entre meses"""
        atual = ENERGIA['mes_atual']
        anterior = ENERGIA['mes_anterior']
        
        diff_consumo = atual['consumo'] - anterior['consumo']
        diff_custo = atual['custo'] - anterior['custo']
        
        return {
            'tipo': 'comparacao_energia',
            'dados': {
                'mes_anterior': anterior,
                'mes_atual': atual,
                'diferenca_consumo': diff_consumo,
                'diferenca_custo': diff_custo,
                'percentual_consumo': (diff_consumo / anterior['consumo']) * 100,
                'percentual_custo': (diff_custo / anterior['custo']) * 100
            },
            'resumo': f"Comparação: {diff_consumo:+d} kWh ({diff_consumo/anterior['consumo']*100:+.1f}%), R$ {diff_custo:+.2f} ({diff_custo/anterior['custo']*100:+.1f}%)"
        }

    def processar_solicitacao(self, mensagem):
        """Método principal que processa a solicitação completa"""
        analise = self.processar_linguagem_natural(mensagem)
        
        # Casos especiais
        if analise['intencao'] == 'energia' and analise['eh_comparacao']:
            return self.gerar_comparacao_energia()
        
        # Busca padrão
        resultado = self.buscar_dados(analise['intencao'], analise['periodo'])
        
        return resultado

# Instância global da Lua Inteligente
lua_ia = LuaInteligente()

@lua_inteligente_bp.route('/chat', methods=['POST'])
def chat_inteligente():
    """Endpoint principal do chat inteligente da Lua"""
    try:
        data = request.get_json() or {}
        mensagem = data.get('message', '').strip()
        
        if not mensagem:
            return jsonify({
                'response': 'Por favor, me diga o que você gostaria de saber!',
                'status': 'error'
            })
        
        # Processar a solicitação
        resultado = lua_ia.processar_solicitacao(mensagem)
        
        # Gerar resposta inteligente
        resposta = f"✅ {resultado['resumo']}"
        
        return jsonify({
            'response': resposta,
            'data': resultado['dados'],
            'tipo': resultado['tipo'],
            'total': resultado.get('total', 0),
            'valor_total': resultado.get('valor_total'),
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'show_in_interface': True  # Sinaliza para mostrar na interface
        })
        
    except Exception as e:
        return jsonify({
            'response': f'Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        })

@lua_inteligente_bp.route('/status', methods=['GET'])
def status_inteligente():
    """Status da Lua Inteligente"""
    return jsonify({
        'status': 'online',
        'message': '🧠 Lua IA Inteligente ativa - Processamento de linguagem natural habilitado!',
        'capacidades': [
            'Processamento de linguagem natural',
            'Acesso a todos os módulos do sistema',
            'Exibição automática de dados na interface',
            'Comparações e análises em tempo real'
        ],
        'timestamp': datetime.now().isoformat()
    })

