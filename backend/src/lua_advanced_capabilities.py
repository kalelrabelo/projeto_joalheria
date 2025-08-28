# backend/src/lua_advanced_capabilities.py

import os
import json
import openai
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import re

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
class AdvancedAnalysis:
    """Resultado de análise avançada"""
    insights: List[str]
    recommendations: List[str]
    predictions: Dict[str, Any]
    confidence_score: float
    data_quality: str

class LuaAdvancedCapabilities:
    """Capacidades avançadas da LUA com IA e análise preditiva"""
    
    def __init__(self):
        # Configurar cliente OpenAI
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
        # Cache para análises
        self.analysis_cache = {}
        
        # Configurações de análise
        self.analysis_config = {
            'min_data_points': 5,
            'confidence_threshold': 0.7,
            'prediction_horizon_days': 30
        }

    def perform_business_intelligence_analysis(self, analysis_type: str, parameters: Dict[str, Any] = None) -> AdvancedAnalysis:
        """Realiza análise de inteligência de negócios avançada"""
        try:
            logger.info(f"Iniciando análise de BI: {analysis_type}")
            
            if analysis_type == 'financial_trends':
                return self._analyze_financial_trends(parameters)
            elif analysis_type == 'employee_performance':
                return self._analyze_employee_performance(parameters)
            elif analysis_type == 'inventory_optimization':
                return self._analyze_inventory_optimization(parameters)
            elif analysis_type == 'sales_forecasting':
                return self._analyze_sales_forecasting(parameters)
            elif analysis_type == 'cost_analysis':
                return self._analyze_cost_patterns(parameters)
            elif analysis_type == 'customer_behavior':
                return self._analyze_customer_behavior(parameters)
            else:
                return self._general_business_analysis(analysis_type, parameters)
                
        except Exception as e:
            logger.error(f"Erro na análise de BI: {str(e)}")
            return AdvancedAnalysis(
                insights=[f"Erro na análise: {str(e)}"],
                recommendations=["Verificar dados e tentar novamente"],
                predictions={},
                confidence_score=0.0,
                data_quality="error"
            )

    def _analyze_financial_trends(self, parameters: Dict[str, Any] = None) -> AdvancedAnalysis:
        """Analisa tendências financeiras"""
        try:
            # Obter dados financeiros
            transactions = CaixaTransaction.query.order_by(CaixaTransaction.date.desc()).limit(100).all()
            
            if len(transactions) < self.analysis_config['min_data_points']:
                return AdvancedAnalysis(
                    insights=["Dados insuficientes para análise de tendências"],
                    recommendations=["Aguardar mais transações para análise precisa"],
                    predictions={},
                    confidence_score=0.2,
                    data_quality="insufficient"
                )
            
            # Preparar dados para análise
            df_data = []
            for t in transactions:
                df_data.append({
                    'date': datetime.strptime(t.date, '%Y-%m-%d') if isinstance(t.date, str) else t.date,
                    'amount': t.amount,
                    'type': 'entrada' if t.amount > 0 else 'saida'
                })
            
            df = pd.DataFrame(df_data)
            
            # Análise de tendências
            monthly_totals = df.groupby(df['date'].dt.to_period('M')).agg({
                'amount': 'sum'
            }).reset_index()
            
            # Calcular métricas
            total_entradas = df[df['amount'] > 0]['amount'].sum()
            total_saidas = abs(df[df['amount'] < 0]['amount'].sum())
            saldo_atual = total_entradas - total_saidas
            
            # Tendência mensal
            if len(monthly_totals) >= 2:
                trend = "crescente" if monthly_totals['amount'].iloc[-1] > monthly_totals['amount'].iloc[-2] else "decrescente"
            else:
                trend = "estável"
            
            # Usar IA para insights avançados
            ai_insights = self._get_ai_financial_insights(df, saldo_atual, trend)
            
            insights = [
                f"Saldo atual: R$ {saldo_atual:.2f}",
                f"Total de entradas: R$ {total_entradas:.2f}",
                f"Total de saídas: R$ {total_saidas:.2f}",
                f"Tendência mensal: {trend}",
                f"Número de transações analisadas: {len(transactions)}"
            ]
            
            recommendations = [
                "Monitorar fluxo de caixa semanalmente",
                "Considerar reserva de emergência se saldo baixo",
                "Analisar principais categorias de gastos"
            ]
            
            # Adicionar insights da IA
            if ai_insights:
                insights.extend(ai_insights.get('insights', []))
                recommendations.extend(ai_insights.get('recommendations', []))
            
            predictions = {
                'saldo_projetado_30_dias': saldo_atual + (monthly_totals['amount'].mean() if len(monthly_totals) > 0 else 0),
                'tendencia': trend,
                'risco_fluxo_caixa': 'baixo' if saldo_atual > 10000 else 'médio' if saldo_atual > 5000 else 'alto'
            }
            
            return AdvancedAnalysis(
                insights=insights,
                recommendations=recommendations,
                predictions=predictions,
                confidence_score=0.8,
                data_quality="good"
            )
            
        except Exception as e:
            logger.error(f"Erro na análise financeira: {str(e)}")
            return AdvancedAnalysis(
                insights=[f"Erro na análise financeira: {str(e)}"],
                recommendations=["Verificar dados financeiros"],
                predictions={},
                confidence_score=0.0,
                data_quality="error"
            )

    def _analyze_employee_performance(self, parameters: Dict[str, Any] = None) -> AdvancedAnalysis:
        """Analisa performance dos funcionários"""
        try:
            employees = Employee.query.filter_by(active=True).all()
            vales = Vale.query.filter(Vale.date >= datetime.now() - timedelta(days=90)).all()
            
            # Análise de vales por funcionário
            vales_por_funcionario = {}
            for vale in vales:
                emp_id = vale.employee_id
                if emp_id not in vales_por_funcionario:
                    vales_por_funcionario[emp_id] = {'total': 0, 'count': 0}
                vales_por_funcionario[emp_id]['total'] += abs(vale.amount)
                vales_por_funcionario[emp_id]['count'] += 1
            
            insights = [
                f"Total de funcionários ativos: {len(employees)}",
                f"Funcionários com vales nos últimos 90 dias: {len(vales_por_funcionario)}",
                f"Total de vales no período: {len(vales)}"
            ]
            
            # Identificar funcionários com mais vales
            if vales_por_funcionario:
                max_vales_emp = max(vales_por_funcionario.items(), key=lambda x: x[1]['count'])
                emp = Employee.query.get(max_vales_emp[0])
                if emp:
                    insights.append(f"Funcionário com mais vales: {emp.name} ({max_vales_emp[1]['count']} vales)")
            
            recommendations = [
                "Monitorar padrões de solicitação de vales",
                "Considerar treinamento para funcionários com muitos vales",
                "Implementar sistema de avaliação de performance"
            ]
            
            predictions = {
                'funcionarios_risco_rotatividade': len([emp for emp in employees if emp.id in vales_por_funcionario and vales_por_funcionario[emp.id]['count'] > 3]),
                'media_vales_por_funcionario': sum(v['count'] for v in vales_por_funcionario.values()) / len(vales_por_funcionario) if vales_por_funcionario else 0
            }
            
            return AdvancedAnalysis(
                insights=insights,
                recommendations=recommendations,
                predictions=predictions,
                confidence_score=0.7,
                data_quality="good"
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de funcionários: {str(e)}")
            return AdvancedAnalysis(
                insights=[f"Erro na análise: {str(e)}"],
                recommendations=["Verificar dados de funcionários"],
                predictions={},
                confidence_score=0.0,
                data_quality="error"
            )

    def _analyze_inventory_optimization(self, parameters: Dict[str, Any] = None) -> AdvancedAnalysis:
        """Analisa otimização de inventário"""
        try:
            inventory_items = Inventory.query.all()
            
            if not inventory_items:
                return AdvancedAnalysis(
                    insights=["Nenhum item no inventário encontrado"],
                    recommendations=["Adicionar itens ao inventário"],
                    predictions={},
                    confidence_score=0.1,
                    data_quality="insufficient"
                )
            
            # Análise de estoque
            total_items = len(inventory_items)
            low_stock_items = [item for item in inventory_items if hasattr(item, 'quantity_available') and hasattr(item, 'minimum_stock') and item.quantity_available < item.minimum_stock]
            
            # Calcular valor total do estoque
            total_value = sum(getattr(item, 'cost_per_unit', 0) * getattr(item, 'quantity_available', 0) for item in inventory_items)
            
            insights = [
                f"Total de itens no inventário: {total_items}",
                f"Itens com estoque baixo: {len(low_stock_items)}",
                f"Valor total do estoque: R$ {total_value:.2f}",
                f"Percentual de itens com estoque baixo: {(len(low_stock_items) / total_items * 100):.1f}%"
            ]
            
            recommendations = [
                "Reabastecer itens com estoque baixo",
                "Implementar sistema de alerta automático",
                "Revisar níveis mínimos de estoque periodicamente"
            ]
            
            if len(low_stock_items) > 0:
                recommendations.append(f"Priorizar reposição de {len(low_stock_items)} itens críticos")
            
            predictions = {
                'itens_criticos': len(low_stock_items),
                'investimento_reposicao_estimado': sum(getattr(item, 'cost_per_unit', 0) * (getattr(item, 'minimum_stock', 0) - getattr(item, 'quantity_available', 0)) for item in low_stock_items if getattr(item, 'quantity_available', 0) < getattr(item, 'minimum_stock', 0)),
                'risco_desabastecimento': 'alto' if len(low_stock_items) > total_items * 0.3 else 'médio' if len(low_stock_items) > total_items * 0.1 else 'baixo'
            }
            
            return AdvancedAnalysis(
                insights=insights,
                recommendations=recommendations,
                predictions=predictions,
                confidence_score=0.9,
                data_quality="excellent"
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de inventário: {str(e)}")
            return AdvancedAnalysis(
                insights=[f"Erro na análise: {str(e)}"],
                recommendations=["Verificar dados de inventário"],
                predictions={},
                confidence_score=0.0,
                data_quality="error"
            )

    def _analyze_sales_forecasting(self, parameters: Dict[str, Any] = None) -> AdvancedAnalysis:
        """Analisa e prevê vendas"""
        try:
            orders = Order.query.filter(Order.order_date >= datetime.now() - timedelta(days=180)).all()
            
            if len(orders) < self.analysis_config['min_data_points']:
                return AdvancedAnalysis(
                    insights=["Dados insuficientes para previsão de vendas"],
                    recommendations=["Aguardar mais pedidos para análise precisa"],
                    predictions={},
                    confidence_score=0.2,
                    data_quality="insufficient"
                )
            
            # Preparar dados
            df_data = []
            for order in orders:
                df_data.append({
                    'date': order.order_date,
                    'value': getattr(order, 'total_price', 0) or 0,
                    'status': getattr(order, 'status', 'unknown')
                })
            
            df = pd.DataFrame(df_data)
            
            # Análise mensal
            monthly_sales = df.groupby(df['date'].dt.to_period('M')).agg({
                'value': 'sum',
                'date': 'count'
            }).rename(columns={'date': 'count'}).reset_index()
            
            total_sales = df['value'].sum()
            avg_order_value = df['value'].mean()
            completed_orders = len(df[df['status'] == 'completed'])
            
            insights = [
                f"Total de pedidos nos últimos 6 meses: {len(orders)}",
                f"Valor total de vendas: R$ {total_sales:.2f}",
                f"Valor médio por pedido: R$ {avg_order_value:.2f}",
                f"Pedidos concluídos: {completed_orders}"
            ]
            
            # Tendência
            if len(monthly_sales) >= 2:
                trend = "crescente" if monthly_sales['value'].iloc[-1] > monthly_sales['value'].iloc[-2] else "decrescente"
                insights.append(f"Tendência de vendas: {trend}")
            
            recommendations = [
                "Monitorar conversão de pedidos",
                "Analisar sazonalidade das vendas",
                "Focar em aumentar valor médio do pedido"
            ]
            
            # Previsão simples baseada na média
            avg_monthly_sales = monthly_sales['value'].mean() if len(monthly_sales) > 0 else 0
            
            predictions = {
                'vendas_projetadas_proximo_mes': avg_monthly_sales,
                'crescimento_estimado': ((monthly_sales['value'].iloc[-1] / monthly_sales['value'].iloc[-2] - 1) * 100) if len(monthly_sales) >= 2 else 0,
                'meta_sugerida_mes': avg_monthly_sales * 1.1  # 10% de crescimento
            }
            
            return AdvancedAnalysis(
                insights=insights,
                recommendations=recommendations,
                predictions=predictions,
                confidence_score=0.7,
                data_quality="good"
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de vendas: {str(e)}")
            return AdvancedAnalysis(
                insights=[f"Erro na análise: {str(e)}"],
                recommendations=["Verificar dados de vendas"],
                predictions={},
                confidence_score=0.0,
                data_quality="error"
            )

    def _analyze_cost_patterns(self, parameters: Dict[str, Any] = None) -> AdvancedAnalysis:
        """Analisa padrões de custos"""
        try:
            costs = Cost.query.filter(Cost.date >= datetime.now() - timedelta(days=90)).all()
            
            if not costs:
                return AdvancedAnalysis(
                    insights=["Nenhum dado de custo encontrado"],
                    recommendations=["Registrar custos para análise"],
                    predictions={},
                    confidence_score=0.1,
                    data_quality="insufficient"
                )
            
            total_costs = sum(getattr(cost, 'amount', 0) for cost in costs)
            avg_cost = total_costs / len(costs) if costs else 0
            
            insights = [
                f"Total de custos nos últimos 90 dias: R$ {total_costs:.2f}",
                f"Custo médio: R$ {avg_cost:.2f}",
                f"Número de registros de custo: {len(costs)}"
            ]
            
            recommendations = [
                "Categorizar custos para melhor análise",
                "Implementar controle de custos por categoria",
                "Monitorar custos variáveis vs fixos"
            ]
            
            predictions = {
                'custo_projetado_mes': total_costs / 3,  # Média mensal
                'categoria_maior_gasto': 'materiais',  # Placeholder
                'oportunidade_economia': total_costs * 0.05  # 5% de economia potencial
            }
            
            return AdvancedAnalysis(
                insights=insights,
                recommendations=recommendations,
                predictions=predictions,
                confidence_score=0.6,
                data_quality="fair"
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de custos: {str(e)}")
            return AdvancedAnalysis(
                insights=[f"Erro na análise: {str(e)}"],
                recommendations=["Verificar dados de custos"],
                predictions={},
                confidence_score=0.0,
                data_quality="error"
            )

    def _analyze_customer_behavior(self, parameters: Dict[str, Any] = None) -> AdvancedAnalysis:
        """Analisa comportamento de clientes"""
        try:
            orders = Order.query.all()
            
            if not orders:
                return AdvancedAnalysis(
                    insights=["Nenhum pedido encontrado para análise"],
                    recommendations=["Aguardar pedidos de clientes"],
                    predictions={},
                    confidence_score=0.1,
                    data_quality="insufficient"
                )
            
            # Análise básica de clientes
            customers_with_orders = set()
            repeat_customers = {}
            
            for order in orders:
                if hasattr(order, 'customer') and order.customer:
                    customer_id = order.customer.id
                    customers_with_orders.add(customer_id)
                    
                    if customer_id not in repeat_customers:
                        repeat_customers[customer_id] = 0
                    repeat_customers[customer_id] += 1
            
            total_customers = len(customers_with_orders)
            repeat_customer_count = len([c for c in repeat_customers.values() if c > 1])
            
            insights = [
                f"Total de clientes com pedidos: {total_customers}",
                f"Clientes recorrentes: {repeat_customer_count}",
                f"Taxa de retenção: {(repeat_customer_count / total_customers * 100):.1f}%" if total_customers > 0 else "Taxa de retenção: 0%"
            ]
            
            recommendations = [
                "Implementar programa de fidelidade",
                "Acompanhar satisfação do cliente",
                "Criar campanhas para clientes recorrentes"
            ]
            
            predictions = {
                'potencial_crescimento_base': total_customers * 0.2,  # 20% de crescimento
                'clientes_risco_churn': total_customers - repeat_customer_count,
                'valor_lifetime_estimado': 1000  # Placeholder
            }
            
            return AdvancedAnalysis(
                insights=insights,
                recommendations=recommendations,
                predictions=predictions,
                confidence_score=0.5,
                data_quality="fair"
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de clientes: {str(e)}")
            return AdvancedAnalysis(
                insights=[f"Erro na análise: {str(e)}"],
                recommendations=["Verificar dados de clientes"],
                predictions={},
                confidence_score=0.0,
                data_quality="error"
            )

    def _general_business_analysis(self, analysis_type: str, parameters: Dict[str, Any] = None) -> AdvancedAnalysis:
        """Análise geral de negócios usando IA"""
        try:
            # Usar IA para análise geral
            system_prompt = f"""Você é um consultor de negócios especializado em joalherias. 
            
Analise o tipo de análise solicitada: {analysis_type}
Parâmetros: {json.dumps(parameters or {}, ensure_ascii=False)}

Forneça insights, recomendações e previsões relevantes para uma joalheria.
Responda em formato JSON:
{{
    "insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"],
    "predictions": {{"key": "value"}},
    "confidence_score": 0.8
}}"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": system_prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            
            return AdvancedAnalysis(
                insights=result.get('insights', [f"Análise {analysis_type} processada com IA"]),
                recommendations=result.get('recommendations', ["Implementar melhorias baseadas na análise"]),
                predictions=result.get('predictions', {}),
                confidence_score=result.get('confidence_score', 0.6),
                data_quality="ai_generated"
            )
            
        except Exception as e:
            logger.error(f"Erro na análise geral: {str(e)}")
            return AdvancedAnalysis(
                insights=[f"Análise {analysis_type} em desenvolvimento"],
                recommendations=["Funcionalidade será implementada em breve"],
                predictions={},
                confidence_score=0.3,
                data_quality="placeholder"
            )

    def _get_ai_financial_insights(self, df: pd.DataFrame, saldo_atual: float, trend: str) -> Optional[Dict[str, Any]]:
        """Obtém insights financeiros usando IA"""
        try:
            # Preparar dados para a IA
            summary = {
                'saldo_atual': saldo_atual,
                'tendencia': trend,
                'total_transacoes': len(df),
                'maior_entrada': df[df['amount'] > 0]['amount'].max() if len(df[df['amount'] > 0]) > 0 else 0,
                'maior_saida': abs(df[df['amount'] < 0]['amount'].min()) if len(df[df['amount'] < 0]) > 0 else 0
            }
            
            prompt = f"""Como consultor financeiro especializado em joalherias, analise estes dados:
            
{json.dumps(summary, ensure_ascii=False)}

Forneça insights específicos e recomendações práticas.
Responda em JSON:
{{
    "insights": ["insight específico 1", "insight específico 2"],
    "recommendations": ["recomendação prática 1", "recomendação prática 2"]
}}"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            logger.error(f"Erro nos insights de IA: {str(e)}")
            return None

    def generate_executive_summary(self, analyses: List[AdvancedAnalysis]) -> str:
        """Gera resumo executivo das análises"""
        try:
            # Compilar dados das análises
            all_insights = []
            all_recommendations = []
            
            for analysis in analyses:
                all_insights.extend(analysis.insights)
                all_recommendations.extend(analysis.recommendations)
            
            # Usar IA para gerar resumo executivo
            prompt = f"""Como consultor executivo, crie um resumo executivo profissional baseado nestas análises de uma joalheria:

INSIGHTS:
{json.dumps(all_insights, ensure_ascii=False)}

RECOMENDAÇÕES:
{json.dumps(all_recommendations, ensure_ascii=False)}

Crie um resumo executivo conciso, profissional e acionável em português brasileiro."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=600
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Erro no resumo executivo: {str(e)}")
            return "Resumo executivo não disponível no momento."

# Instância global das capacidades avançadas
lua_advanced = LuaAdvancedCapabilities()

