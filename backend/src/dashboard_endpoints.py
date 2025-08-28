# -*- coding: utf-8 -*-
"""
Endpoints para Dashboard Editável
"""

from flask import Blueprint, request, jsonify
from dashboard_service import DashboardService
import json

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/test', methods=['GET'])
def test_dashboard():
    """Teste do módulo dashboard"""
    return jsonify({
        "status": "success",
        "message": "Dashboard API funcionando",
        "endpoints": [
            "/api/dashboard/widgets",
            "/api/dashboard/filters",
            "/api/dashboard/data/conta-luz",
            "/api/dashboard/data/gastos-lucros",
            "/api/dashboard/data/vales"
        ]
    })

@dashboard_bp.route('/filters', methods=['GET'])
def get_all_filters():
    """Obtém todos os filtros disponíveis"""
    try:
        service = DashboardService()
        filtros = service.get_all_filters()
        return jsonify({
            "status": "success",
            "data": filtros
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/data/conta-luz', methods=['GET'])
def get_conta_luz_comparacao():
    """Compara conta de luz do mês atual com o anterior"""
    try:
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        service = DashboardService()
        dados = service.get_conta_luz_comparacao(mes, ano)
        
        return jsonify({
            "status": "success",
            "data": dados,
            "widget_type": "comparison",
            "title": "Comparação Conta de Luz"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/data/gastos-lucros', methods=['GET'])
def get_gastos_lucros():
    """Obtém gastos e lucros do mês"""
    try:
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        service = DashboardService()
        dados = service.get_gastos_lucros_mes(mes, ano)
        
        return jsonify({
            "status": "success",
            "data": dados,
            "widget_type": "metric",
            "title": "Gastos e Lucros do Mês"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/data/vales', methods=['GET'])
def get_ultimos_vales():
    """Obtém os últimos vales do mês"""
    try:
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        limit = request.args.get('limit', 10, type=int)
        
        service = DashboardService()
        dados = service.get_ultimos_vales_mes(mes, ano, limit)
        
        return jsonify({
            "status": "success",
            "data": dados,
            "widget_type": "table",
            "title": "Últimos Vales do Mês"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/widgets', methods=['GET'])
def get_user_widgets():
    """Obtém widgets do usuário"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({
                "status": "error",
                "message": "user_id é obrigatório"
            }), 400
        
        service = DashboardService()
        widgets = service.get_user_widgets(user_id)
        
        return jsonify({
            "status": "success",
            "data": widgets
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/widgets', methods=['POST'])
def create_widget():
    """Cria um novo widget"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Dados do widget são obrigatórios"
            }), 400
        
        service = DashboardService()
        widget = service.create_widget(data)
        
        return jsonify({
            "status": "success",
            "data": widget
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/widgets/<int:widget_id>', methods=['PUT'])
def update_widget(widget_id):
    """Atualiza um widget existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Dados do widget são obrigatórios"
            }), 400
        
        service = DashboardService()
        widget = service.update_widget(widget_id, data)
        
        return jsonify({
            "status": "success",
            "data": widget
        })
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/widgets/<int:widget_id>', methods=['DELETE'])
def delete_widget(widget_id):
    """Remove um widget"""
    try:
        service = DashboardService()
        success = service.delete_widget(widget_id)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Widget removido com sucesso"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Widget não encontrado"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/widgets/<int:widget_id>/data', methods=['GET'])
def get_widget_data(widget_id):
    """Obtém dados para um widget específico"""
    try:
        # Obter filtros da query string
        filtros = {}
        for key, value in request.args.items():
            if key not in ['widget_id']:
                filtros[key] = value
        
        service = DashboardService()
        dados = service.get_widget_data(widget_id, filtros)
        
        return jsonify({
            "status": "success",
            "data": dados
        })
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/lua/command', methods=['POST'])
def process_lua_command():
    """Processa comandos da LUA para o dashboard"""
    try:
        data = request.get_json()
        comando = data.get('comando', '').lower()
        
        service = DashboardService()
        
        # Processar comandos específicos da LUA
        if 'conta de luz' in comando and 'compare' in comando:
            dados = service.get_conta_luz_comparacao()
            return jsonify({
                "status": "success",
                "data": dados,
                "widget_suggestion": {
                    "tipo": "comparison",
                    "titulo": "Comparação Conta de Luz",
                    "configuracao": {"comparison_type": "conta_luz"}
                },
                "message": "Comparação de conta de luz gerada. Deseja adicionar ao dashboard?"
            })
        
        elif 'gasto' in comando and 'lucro' in comando:
            dados = service.get_gastos_lucros_mes()
            return jsonify({
                "status": "success",
                "data": dados,
                "widget_suggestion": {
                    "tipo": "metric",
                    "titulo": "Gastos e Lucros",
                    "configuracao": {"metric_type": "lucro_mes"}
                },
                "message": "Dados de gastos e lucros gerados. Deseja adicionar ao dashboard?"
            })
        
        elif 'vales' in comando and 'mês' in comando:
            dados = service.get_ultimos_vales_mes()
            return jsonify({
                "status": "success",
                "data": dados,
                "widget_suggestion": {
                    "tipo": "table",
                    "titulo": "Últimos Vales do Mês",
                    "configuracao": {"table_type": "ultimos_vales"}
                },
                "message": "Lista de vales gerada. Deseja adicionar ao dashboard?"
            })
        
        else:
            return jsonify({
                "status": "info",
                "message": "Comando não reconhecido. Tente: 'compare conta de luz', 'mostre gastos e lucros', 'últimos vales do mês'"
            })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/groups', methods=['GET'])
def get_groups_subgroups():
    """Obtém grupos e subgrupos disponíveis no sistema"""
    try:
        grupos = {
            "funcionarios": {
                "nome": "Funcionários",
                "subgrupos": ["gestao", "folha_pagamento", "vales", "performance"]
            },
            "vendas": {
                "nome": "Vendas",
                "subgrupos": ["vendas_diarias", "vendas_mensais", "vendas_por_funcionario", "formas_pagamento"]
            },
            "joias": {
                "nome": "Joias",
                "subgrupos": ["estoque", "categorias", "materiais", "precos"]
            },
            "clientes": {
                "nome": "Clientes",
                "subgrupos": ["cadastros", "historico_compras", "aniversarios", "preferencias"]
            },
            "encomendas": {
                "nome": "Encomendas",
                "subgrupos": ["pendentes", "em_producao", "concluidas", "prazos"]
            },
            "financeiro": {
                "nome": "Financeiro",
                "subgrupos": ["caixa", "receitas", "despesas", "lucros"]
            },
            "energia": {
                "nome": "Energia",
                "subgrupos": ["consumo", "custos", "comparacoes", "historico"]
            }
        }
        
        return jsonify({
            "status": "success",
            "data": grupos
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@dashboard_bp.route('/templates', methods=['GET'])
def get_widget_templates():
    """Obtém templates de widgets pré-configurados"""
    try:
        templates = [
            {
                "id": "conta_luz_comparacao",
                "nome": "Comparação Conta de Luz",
                "tipo": "comparison",
                "grupo": "energia",
                "subgrupo": "comparacoes",
                "configuracao": {"comparison_type": "conta_luz"},
                "descricao": "Compara conta de luz do mês atual com o anterior"
            },
            {
                "id": "gastos_lucros_mes",
                "nome": "Gastos e Lucros do Mês",
                "tipo": "metric",
                "grupo": "financeiro",
                "subgrupo": "lucros",
                "configuracao": {"metric_type": "lucro_mes"},
                "descricao": "Mostra gastos, receitas e lucro do mês"
            },
            {
                "id": "ultimos_vales",
                "nome": "Últimos Vales",
                "tipo": "table",
                "grupo": "funcionarios",
                "subgrupo": "vales",
                "configuracao": {"table_type": "ultimos_vales"},
                "descricao": "Lista os últimos vales concedidos"
            },
            {
                "id": "vendas_mes",
                "nome": "Vendas do Mês",
                "tipo": "metric",
                "grupo": "vendas",
                "subgrupo": "vendas_mensais",
                "configuracao": {"metric_type": "total_vendas"},
                "descricao": "Total de vendas do mês atual"
            },
            {
                "id": "estoque_baixo",
                "nome": "Estoque Baixo",
                "tipo": "table",
                "grupo": "joias",
                "subgrupo": "estoque",
                "configuracao": {"table_type": "estoque_baixo"},
                "descricao": "Joias com estoque abaixo do mínimo"
            }
        ]
        
        return jsonify({
            "status": "success",
            "data": templates
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

