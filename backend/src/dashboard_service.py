# -*- coding: utf-8 -*-
"""
Serviço para Dashboard Editável
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, func, extract
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from database import SessionLocal, Funcionario, Vale, Venda, MovimentacaoCaixa, ConsumoEnergia, Joia, Cliente, Encomenda, FolhaPagamento, DashboardWidget, DashboardLayout, DashboardFilter, DashboardQuery

class DashboardService:
    """Serviço principal do Dashboard Editável"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    # ==================== DADOS PARA COMPARAÇÃO ====================
    
    def get_conta_luz_comparacao(self, mes_atual: int = None, ano_atual: int = None) -> Dict[str, Any]:
        """Compara conta de luz do mês atual com o anterior"""
        if not mes_atual:
            mes_atual = datetime.now().month
        if not ano_atual:
            ano_atual = datetime.now().year
        
        # Mês anterior
        if mes_atual == 1:
            mes_anterior = 12
            ano_anterior = ano_atual - 1
        else:
            mes_anterior = mes_atual - 1
            ano_anterior = ano_atual
        
        # Buscar dados
        conta_atual = self.db.query(ConsumoEnergia).filter(
            ConsumoEnergia.mes_referencia == mes_atual,
            ConsumoEnergia.ano_referencia == ano_atual
        ).first()
        
        conta_anterior = self.db.query(ConsumoEnergia).filter(
            ConsumoEnergia.mes_referencia == mes_anterior,
            ConsumoEnergia.ano_referencia == ano_anterior
        ).first()
        
        resultado = {
            "mes_atual": {
                "mes": mes_atual,
                "ano": ano_atual,
                "consumo_kwh": conta_atual.consumo_kwh if conta_atual else 0,
                "valor": conta_atual.valor_conta if conta_atual else 0
            },
            "mes_anterior": {
                "mes": mes_anterior,
                "ano": ano_anterior,
                "consumo_kwh": conta_anterior.consumo_kwh if conta_anterior else 0,
                "valor": conta_anterior.valor_conta if conta_anterior else 0
            }
        }
        
        # Calcular diferenças
        if conta_atual and conta_anterior:
            resultado["diferenca_valor"] = conta_atual.valor_conta - conta_anterior.valor_conta
            resultado["diferenca_consumo"] = conta_atual.consumo_kwh - conta_anterior.consumo_kwh
            resultado["percentual_valor"] = ((conta_atual.valor_conta - conta_anterior.valor_conta) / conta_anterior.valor_conta * 100) if conta_anterior.valor_conta > 0 else 0
            resultado["percentual_consumo"] = ((conta_atual.consumo_kwh - conta_anterior.consumo_kwh) / conta_anterior.consumo_kwh * 100) if conta_anterior.consumo_kwh > 0 else 0
        
        return resultado
    
    def get_gastos_lucros_mes(self, mes: int = None, ano: int = None) -> Dict[str, Any]:
        """Obtém gastos e lucros do mês"""
        if not mes:
            mes = datetime.now().month
        if not ano:
            ano = datetime.now().year
        
        # Vendas do mês
        vendas = self.db.query(func.sum(Venda.valor_total)).filter(
            extract('month', Venda.data_venda) == mes,
            extract('year', Venda.data_venda) == ano
        ).scalar() or 0
        
        # Gastos do mês (saídas do caixa)
        gastos = self.db.query(func.sum(MovimentacaoCaixa.valor)).filter(
            MovimentacaoCaixa.tipo == 'saida',
            extract('month', MovimentacaoCaixa.data_movimentacao) == mes,
            extract('year', MovimentacaoCaixa.data_movimentacao) == ano
        ).scalar() or 0
        
        # Entradas do mês (além das vendas)
        outras_entradas = self.db.query(func.sum(MovimentacaoCaixa.valor)).filter(
            MovimentacaoCaixa.tipo == 'entrada',
            extract('month', MovimentacaoCaixa.data_movimentacao) == mes,
            extract('year', MovimentacaoCaixa.data_movimentacao) == ano
        ).scalar() or 0
        
        total_receitas = vendas + outras_entradas
        lucro_bruto = total_receitas - gastos
        
        return {
            "mes": mes,
            "ano": ano,
            "vendas": vendas,
            "outras_entradas": outras_entradas,
            "total_receitas": total_receitas,
            "gastos": gastos,
            "lucro_bruto": lucro_bruto,
            "margem_lucro": (lucro_bruto / total_receitas * 100) if total_receitas > 0 else 0
        }
    
    def get_ultimos_vales_mes(self, mes: int = None, ano: int = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém os últimos vales do mês"""
        if not mes:
            mes = datetime.now().month
        if not ano:
            ano = datetime.now().year
        
        vales = self.db.query(Vale).join(Funcionario).filter(
            extract('month', Vale.data_vale) == mes,
            extract('year', Vale.data_vale) == ano
        ).order_by(Vale.data_vale.desc()).limit(limit).all()
        
        resultado = []
        for vale in vales:
            resultado.append({
                "id": vale.id,
                "funcionario_nome": vale.funcionario.nome_completo,
                "valor": vale.valor,
                "motivo": vale.motivo,
                "data_vale": vale.data_vale.isoformat(),
                "status": vale.status,
                "observacoes": vale.observacoes
            })
        
        return resultado
    
    # ==================== FILTROS DISPONÍVEIS ====================
    
    def get_all_filters(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna todos os filtros disponíveis organizados por grupo"""
        filtros = {
            "funcionarios": [
                {"nome": "Status", "campo": "status", "tipo": "select", "opcoes": ["ativo", "inativo"]},
                {"nome": "Cargo", "campo": "cargo", "tipo": "select", "opcoes": self._get_distinct_values("funcionarios", "cargo")},
                {"nome": "Data Admissão", "campo": "data_admissao", "tipo": "date_range"},
                {"nome": "Salário", "campo": "salario", "tipo": "number_range"},
                {"nome": "Nome", "campo": "nome_completo", "tipo": "text"}
            ],
            "vendas": [
                {"nome": "Data Venda", "campo": "data_venda", "tipo": "date_range"},
                {"nome": "Forma Pagamento", "campo": "forma_pagamento", "tipo": "select", "opcoes": self._get_distinct_values("vendas", "forma_pagamento")},
                {"nome": "Status", "campo": "status", "tipo": "select", "opcoes": ["concluida", "cancelada", "pendente"]},
                {"nome": "Valor Total", "campo": "valor_total", "tipo": "number_range"},
                {"nome": "Cliente", "campo": "cliente_id", "tipo": "select", "opcoes": self._get_clientes_options()},
                {"nome": "Funcionário", "campo": "funcionario_id", "tipo": "select", "opcoes": self._get_funcionarios_options()}
            ],
            "joias": [
                {"nome": "Categoria", "campo": "categoria", "tipo": "select", "opcoes": self._get_distinct_values("joias", "categoria")},
                {"nome": "Material", "campo": "material", "tipo": "select", "opcoes": self._get_distinct_values("joias", "material")},
                {"nome": "Status", "campo": "status", "tipo": "select", "opcoes": ["ativo", "inativo"]},
                {"nome": "Preço Venda", "campo": "preco_venda", "tipo": "number_range"},
                {"nome": "Quantidade Estoque", "campo": "quantidade_estoque", "tipo": "number_range"},
                {"nome": "Nome", "campo": "nome", "tipo": "text"}
            ],
            "clientes": [
                {"nome": "Status", "campo": "status", "tipo": "select", "opcoes": ["ativo", "inativo"]},
                {"nome": "Data Cadastro", "campo": "created_at", "tipo": "date_range"},
                {"nome": "Nome", "campo": "nome_completo", "tipo": "text"},
                {"nome": "CPF/CNPJ", "campo": "cpf_cnpj", "tipo": "text"}
            ],
            "encomendas": [
                {"nome": "Status", "campo": "status", "tipo": "select", "opcoes": ["pendente", "em_producao", "concluida", "entregue"]},
                {"nome": "Data Pedido", "campo": "data_pedido", "tipo": "date_range"},
                {"nome": "Data Prevista", "campo": "data_prevista", "tipo": "date_range"},
                {"nome": "Preço Acordado", "campo": "preco_acordado", "tipo": "number_range"},
                {"nome": "Cliente", "campo": "cliente_id", "tipo": "select", "opcoes": self._get_clientes_options()}
            ],
            "vales": [
                {"nome": "Data Vale", "campo": "data_vale", "tipo": "date_range"},
                {"nome": "Status", "campo": "status", "tipo": "select", "opcoes": ["ativo", "pago", "cancelado"]},
                {"nome": "Valor", "campo": "valor", "tipo": "number_range"},
                {"nome": "Funcionário", "campo": "funcionario_id", "tipo": "select", "opcoes": self._get_funcionarios_options()},
                {"nome": "Motivo", "campo": "motivo", "tipo": "text"}
            ],
            "caixa": [
                {"nome": "Tipo", "campo": "tipo", "tipo": "select", "opcoes": ["entrada", "saida"]},
                {"nome": "Categoria", "campo": "categoria", "tipo": "select", "opcoes": self._get_distinct_values("movimentacao_caixa", "categoria")},
                {"nome": "Data Movimentação", "campo": "data_movimentacao", "tipo": "date_range"},
                {"nome": "Valor", "campo": "valor", "tipo": "number_range"},
                {"nome": "Forma Pagamento", "campo": "forma_pagamento", "tipo": "select", "opcoes": self._get_distinct_values("movimentacao_caixa", "forma_pagamento")}
            ],
            "energia": [
                {"nome": "Mês Referência", "campo": "mes_referencia", "tipo": "select", "opcoes": [str(i) for i in range(1, 13)]},
                {"nome": "Ano Referência", "campo": "ano_referencia", "tipo": "select", "opcoes": [str(i) for i in range(2020, 2030)]},
                {"nome": "Consumo kWh", "campo": "consumo_kwh", "tipo": "number_range"},
                {"nome": "Valor Conta", "campo": "valor_conta", "tipo": "number_range"}
            ]
        }
        
        return filtros
    
    def _get_distinct_values(self, table: str, column: str) -> List[str]:
        """Obtém valores distintos de uma coluna"""
        try:
            query = text(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column}")
            result = self.db.execute(query).fetchall()
            return [row[0] for row in result if row[0]]
        except:
            return []
    
    def _get_clientes_options(self) -> List[Dict[str, Any]]:
        """Obtém opções de clientes para filtros"""
        clientes = self.db.query(Cliente).filter(Cliente.status == 'ativo').all()
        return [{"value": c.id, "label": c.nome_completo} for c in clientes]
    
    def _get_funcionarios_options(self) -> List[Dict[str, Any]]:
        """Obtém opções de funcionários para filtros"""
        funcionarios = self.db.query(Funcionario).filter(Funcionario.status == 'ativo').all()
        return [{"value": f.id, "label": f.nome_completo} for f in funcionarios]
    
    # ==================== WIDGETS DO DASHBOARD ====================
    
    def create_widget(self, widget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo widget no dashboard"""
        widget = DashboardWidget(**widget_data)
        self.db.add(widget)
        self.db.commit()
        self.db.refresh(widget)
        
        return {
            "id": widget.id,
            "titulo": widget.titulo,
            "tipo": widget.tipo,
            "configuracao": widget.configuracao,
            "posicao_x": widget.posicao_x,
            "posicao_y": widget.posicao_y,
            "largura": widget.largura,
            "altura": widget.altura,
            "grupo": widget.grupo,
            "subgrupo": widget.subgrupo,
            "filtros": widget.filtros,
            "ativo": widget.ativo
        }
    
    def update_widget(self, widget_id: int, widget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza um widget existente"""
        widget = self.db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
        if not widget:
            raise ValueError("Widget não encontrado")
        
        for key, value in widget_data.items():
            if hasattr(widget, key):
                setattr(widget, key, value)
        
        widget.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(widget)
        
        return {
            "id": widget.id,
            "titulo": widget.titulo,
            "tipo": widget.tipo,
            "configuracao": widget.configuracao,
            "posicao_x": widget.posicao_x,
            "posicao_y": widget.posicao_y,
            "largura": widget.largura,
            "altura": widget.altura,
            "grupo": widget.grupo,
            "subgrupo": widget.subgrupo,
            "filtros": widget.filtros,
            "ativo": widget.ativo
        }
    
    def delete_widget(self, widget_id: int) -> bool:
        """Remove um widget do dashboard"""
        widget = self.db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
        if not widget:
            return False
        
        self.db.delete(widget)
        self.db.commit()
        return True
    
    def get_user_widgets(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtém todos os widgets de um usuário"""
        widgets = self.db.query(DashboardWidget).filter(
            DashboardWidget.usuario_id == user_id,
            DashboardWidget.ativo == True
        ).all()
        
        resultado = []
        for widget in widgets:
            resultado.append({
                "id": widget.id,
                "titulo": widget.titulo,
                "tipo": widget.tipo,
                "configuracao": widget.configuracao,
                "posicao_x": widget.posicao_x,
                "posicao_y": widget.posicao_y,
                "largura": widget.largura,
                "altura": widget.altura,
                "grupo": widget.grupo,
                "subgrupo": widget.subgrupo,
                "filtros": widget.filtros,
                "ativo": widget.ativo
            })
        
        return resultado
    
    # ==================== DADOS PARA WIDGETS ====================
    
    def get_widget_data(self, widget_id: int, filtros: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obtém dados para um widget específico"""
        widget = self.db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
        if not widget:
            raise ValueError("Widget não encontrado")
        
        # Aplicar filtros do widget e filtros adicionais
        filtros_finais = widget.filtros or {}
        if filtros:
            filtros_finais.update(filtros)
        
        # Executar query baseada no tipo e configuração do widget
        if widget.tipo == "comparison":
            return self._get_comparison_data(widget, filtros_finais)
        elif widget.tipo == "metric":
            return self._get_metric_data(widget, filtros_finais)
        elif widget.tipo == "chart":
            return self._get_chart_data(widget, filtros_finais)
        elif widget.tipo == "table":
            return self._get_table_data(widget, filtros_finais)
        else:
            return {"error": "Tipo de widget não suportado"}
    
    def _get_comparison_data(self, widget: DashboardWidget, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém dados para widgets de comparação"""
        config = widget.configuracao or {}
        
        if config.get("comparison_type") == "conta_luz":
            return self.get_conta_luz_comparacao()
        elif config.get("comparison_type") == "vendas_mes":
            return self._compare_vendas_mes()
        elif config.get("comparison_type") == "gastos_mes":
            return self._compare_gastos_mes()
        
        return {"error": "Tipo de comparação não configurado"}
    
    def _get_metric_data(self, widget: DashboardWidget, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém dados para widgets de métrica"""
        config = widget.configuracao or {}
        
        if config.get("metric_type") == "total_vendas":
            return self._get_total_vendas(filtros)
        elif config.get("metric_type") == "total_vales":
            return self._get_total_vales(filtros)
        elif config.get("metric_type") == "lucro_mes":
            return self.get_gastos_lucros_mes()
        
        return {"error": "Tipo de métrica não configurado"}
    
    def _get_chart_data(self, widget: DashboardWidget, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém dados para widgets de gráfico"""
        config = widget.configuracao or {}
        
        if config.get("chart_type") == "vendas_tempo":
            return self._get_vendas_por_tempo(filtros)
        elif config.get("chart_type") == "vales_funcionario":
            return self._get_vales_por_funcionario(filtros)
        
        return {"error": "Tipo de gráfico não configurado"}
    
    def _get_table_data(self, widget: DashboardWidget, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém dados para widgets de tabela"""
        config = widget.configuracao or {}
        
        if config.get("table_type") == "ultimos_vales":
            return {"data": self.get_ultimos_vales_mes()}
        elif config.get("table_type") == "vendas_recentes":
            return {"data": self._get_vendas_recentes(filtros)}
        
        return {"error": "Tipo de tabela não configurado"}
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _compare_vendas_mes(self) -> Dict[str, Any]:
        """Compara vendas do mês atual com o anterior"""
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        
        if mes_atual == 1:
            mes_anterior = 12
            ano_anterior = ano_atual - 1
        else:
            mes_anterior = mes_atual - 1
            ano_anterior = ano_atual
        
        vendas_atual = self.db.query(func.sum(Venda.valor_total)).filter(
            extract('month', Venda.data_venda) == mes_atual,
            extract('year', Venda.data_venda) == ano_atual
        ).scalar() or 0
        
        vendas_anterior = self.db.query(func.sum(Venda.valor_total)).filter(
            extract('month', Venda.data_venda) == mes_anterior,
            extract('year', Venda.data_venda) == ano_anterior
        ).scalar() or 0
        
        diferenca = vendas_atual - vendas_anterior
        percentual = (diferenca / vendas_anterior * 100) if vendas_anterior > 0 else 0
        
        return {
            "mes_atual": {"valor": vendas_atual, "mes": mes_atual, "ano": ano_atual},
            "mes_anterior": {"valor": vendas_anterior, "mes": mes_anterior, "ano": ano_anterior},
            "diferenca": diferenca,
            "percentual": percentual
        }
    
    def _compare_gastos_mes(self) -> Dict[str, Any]:
        """Compara gastos do mês atual com o anterior"""
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        
        if mes_atual == 1:
            mes_anterior = 12
            ano_anterior = ano_atual - 1
        else:
            mes_anterior = mes_atual - 1
            ano_anterior = ano_atual
        
        gastos_atual = self.db.query(func.sum(MovimentacaoCaixa.valor)).filter(
            MovimentacaoCaixa.tipo == 'saida',
            extract('month', MovimentacaoCaixa.data_movimentacao) == mes_atual,
            extract('year', MovimentacaoCaixa.data_movimentacao) == ano_atual
        ).scalar() or 0
        
        gastos_anterior = self.db.query(func.sum(MovimentacaoCaixa.valor)).filter(
            MovimentacaoCaixa.tipo == 'saida',
            extract('month', MovimentacaoCaixa.data_movimentacao) == mes_anterior,
            extract('year', MovimentacaoCaixa.data_movimentacao) == ano_anterior
        ).scalar() or 0
        
        diferenca = gastos_atual - gastos_anterior
        percentual = (diferenca / gastos_anterior * 100) if gastos_anterior > 0 else 0
        
        return {
            "mes_atual": {"valor": gastos_atual, "mes": mes_atual, "ano": ano_atual},
            "mes_anterior": {"valor": gastos_anterior, "mes": mes_anterior, "ano": ano_anterior},
            "diferenca": diferenca,
            "percentual": percentual
        }
    
    def _get_total_vendas(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém total de vendas com filtros"""
        query = self.db.query(func.sum(Venda.valor_total))
        
        # Aplicar filtros de data se especificados
        if filtros.get("data_inicio"):
            query = query.filter(Venda.data_venda >= filtros["data_inicio"])
        if filtros.get("data_fim"):
            query = query.filter(Venda.data_venda <= filtros["data_fim"])
        
        total = query.scalar() or 0
        
        return {"valor": total, "tipo": "vendas"}
    
    def _get_total_vales(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém total de vales com filtros"""
        query = self.db.query(func.sum(Vale.valor))
        
        # Aplicar filtros de data se especificados
        if filtros.get("data_inicio"):
            query = query.filter(Vale.data_vale >= filtros["data_inicio"])
        if filtros.get("data_fim"):
            query = query.filter(Vale.data_vale <= filtros["data_fim"])
        
        total = query.scalar() or 0
        
        return {"valor": total, "tipo": "vales"}
    
    def _get_vendas_por_tempo(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém vendas agrupadas por tempo"""
        # Implementar lógica para gráfico de vendas por tempo
        return {"data": [], "labels": []}
    
    def _get_vales_por_funcionario(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém vales agrupados por funcionário"""
        # Implementar lógica para gráfico de vales por funcionário
        return {"data": [], "labels": []}
    
    def _get_vendas_recentes(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Obtém vendas recentes"""
        vendas = self.db.query(Venda).join(Cliente).join(Funcionario).order_by(Venda.data_venda.desc()).limit(10).all()
        
        resultado = []
        for venda in vendas:
            resultado.append({
                "id": venda.id,
                "cliente": venda.cliente.nome_completo if venda.cliente else "N/A",
                "funcionario": venda.funcionario.nome_completo if venda.funcionario else "N/A",
                "valor_total": venda.valor_total,
                "data_venda": venda.data_venda.isoformat(),
                "forma_pagamento": venda.forma_pagamento,
                "status": venda.status
            })
        
        return resultado

