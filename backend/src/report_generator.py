# backend/src/report_generator.py

import os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from src.models.caixa import CaixaTransaction
from src.models.employee import Employee
from src.models.order import Order
from src.models.inventory import Inventory
from src.models.vale import Vale
from src.models.payroll import Payroll

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_LEFT
        )
        
    def generate_financial_report(self, year=None, month=None):
        """Gerar relatório financeiro em PDF"""
        try:
            if not year:
                year = datetime.now().year
            
            # Criar diretório de relatórios se não existir
            reports_dir = "/tmp/reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Nome do arquivo
            if month:
                filename = f"relatorio_financeiro_{year}_{month:02d}.pdf"
                period_text = f"{month:02d}/{year}"
            else:
                filename = f"relatorio_financeiro_{year}.pdf"
                period_text = str(year)
            
            filepath = os.path.join(reports_dir, filename)
            
            # Criar documento PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Título
            title = Paragraph(f"Relatório Financeiro - {period_text}", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Data de geração
            generation_date = Paragraph(
                f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
                self.styles['Normal']
            )
            story.append(generation_date)
            story.append(Spacer(1, 20))
            
            # Buscar dados financeiros
            query = CaixaTransaction.query
            
            if month:
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1)
                else:
                    end_date = datetime(year, month + 1, 1)
                query = query.filter(
                    CaixaTransaction.date >= start_date.strftime('%Y-%m-%d'),
                    CaixaTransaction.date < end_date.strftime('%Y-%m-%d')
                )
            else:
                query = query.filter(
                    CaixaTransaction.date >= f"{year}-01-01",
                    CaixaTransaction.date <= f"{year}-12-31"
                )
            
            transactions = query.all()
            
            # Calcular totais
            total_receitas = sum(t.amount for t in transactions if t.amount > 0)
            total_despesas = sum(abs(t.amount) for t in transactions if t.amount < 0)
            lucro = total_receitas - total_despesas
            
            # Resumo financeiro
            summary_data = [
                ['Descrição', 'Valor'],
                ['Total de Receitas', f'R$ {total_receitas:,.2f}'],
                ['Total de Despesas', f'R$ {total_despesas:,.2f}'],
                ['Lucro Líquido', f'R$ {lucro:,.2f}']
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(Paragraph("Resumo Financeiro", self.subtitle_style))
            story.append(summary_table)
            story.append(Spacer(1, 30))
            
            # Detalhamento das transações
            if transactions:
                story.append(Paragraph("Detalhamento das Transações", self.subtitle_style))
                
                transaction_data = [['Data', 'Tipo', 'Descrição', 'Valor']]
                
                for transaction in transactions[-20:]:  # Últimas 20 transações
                    tipo = "Entrada" if transaction.amount > 0 else "Saída"
                    valor = f"R$ {abs(transaction.amount):,.2f}"
                    transaction_data.append([
                        transaction.date,
                        tipo,
                        transaction.description[:40] + "..." if len(transaction.description) > 40 else transaction.description,
                        valor
                    ])
                
                transaction_table = Table(transaction_data, colWidths=[1.2*inch, 1*inch, 2.5*inch, 1.3*inch])
                transaction_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(transaction_table)
            
            # Gerar PDF
            doc.build(story)
            
            return {
                "status": "success",
                "message": f"Relatório financeiro gerado com sucesso",
                "filepath": filepath,
                "filename": filename,
                "data": {
                    "total_receitas": total_receitas,
                    "total_despesas": total_despesas,
                    "lucro": lucro,
                    "total_transacoes": len(transactions)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao gerar relatório financeiro: {str(e)}"
            }
    
    def generate_employee_report(self, year=None, month=None):
        """Gerar relatório de funcionários em PDF"""
        try:
            if not year:
                year = datetime.now().year
            
            reports_dir = "/tmp/reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            if month:
                filename = f"relatorio_funcionarios_{year}_{month:02d}.pdf"
                period_text = f"{month:02d}/{year}"
            else:
                filename = f"relatorio_funcionarios_{year}.pdf"
                period_text = str(year)
            
            filepath = os.path.join(reports_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Título
            title = Paragraph(f"Relatório de Funcionários - {period_text}", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Data de geração
            generation_date = Paragraph(
                f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
                self.styles['Normal']
            )
            story.append(generation_date)
            story.append(Spacer(1, 20))
            
            # Buscar funcionários
            employees = Employee.query.all()
            
            if employees:
                # Lista de funcionários
                employee_data = [['Nome', 'CPF', 'Cargo', 'Salário', 'Status']]
                
                total_salarios = 0
                funcionarios_ativos = 0
                
                for employee in employees:
                    status = "Ativo" if getattr(employee, 'active', True) else "Inativo"
                    if getattr(employee, 'active', True):
                        funcionarios_ativos += 1
                        total_salarios += employee.salary or 0
                    
                    employee_data.append([
                        employee.name,
                        employee.cpf,
                        employee.role or "N/A",
                        f"R$ {employee.salary:,.2f}" if employee.salary else "N/A",
                        status
                    ])
                
                employee_table = Table(employee_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.2*inch, 0.8*inch])
                employee_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(Paragraph("Lista de Funcionários", self.subtitle_style))
                story.append(employee_table)
                story.append(Spacer(1, 30))
                
                # Resumo
                summary_data = [
                    ['Descrição', 'Valor'],
                    ['Total de Funcionários', str(len(employees))],
                    ['Funcionários Ativos', str(funcionarios_ativos)],
                    ['Total de Salários', f'R$ {total_salarios:,.2f}']
                ]
                
                summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(Paragraph("Resumo", self.subtitle_style))
                story.append(summary_table)
            
            doc.build(story)
            
            return {
                "status": "success",
                "message": f"Relatório de funcionários gerado com sucesso",
                "filepath": filepath,
                "filename": filename,
                "data": {
                    "total_funcionarios": len(employees),
                    "funcionarios_ativos": funcionarios_ativos,
                    "total_salarios": total_salarios
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao gerar relatório de funcionários: {str(e)}"
            }
    
    def generate_inventory_report(self):
        """Gerar relatório de estoque em PDF"""
        try:
            reports_dir = "/tmp/reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            filename = f"relatorio_estoque_{datetime.now().strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(reports_dir, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Título
            title = Paragraph("Relatório de Estoque", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Data de geração
            generation_date = Paragraph(
                f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
                self.styles['Normal']
            )
            story.append(generation_date)
            story.append(Spacer(1, 20))
            
            # Buscar itens do estoque
            inventory_items = Inventory.query.all()
            
            if inventory_items:
                inventory_data = [['Item', 'Quantidade', 'Status']]
                
                total_items = len(inventory_items)
                low_stock_items = 0
                
                for item in inventory_items:
                    status = "Estoque Baixo" if item.quantity < 10 else "OK"
                    if item.quantity < 10:
                        low_stock_items += 1
                    
                    item_name = item.jewelry.name if item.jewelry else f"Item {item.id}"
                    
                    inventory_data.append([
                        item_name,
                        str(item.quantity),
                        status
                    ])
                
                inventory_table = Table(inventory_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                inventory_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(Paragraph("Itens em Estoque", self.subtitle_style))
                story.append(inventory_table)
                story.append(Spacer(1, 30))
                
                # Resumo
                summary_data = [
                    ['Descrição', 'Valor'],
                    ['Total de Itens', str(total_items)],
                    ['Itens com Estoque Baixo', str(low_stock_items)],
                    ['Percentual de Alerta', f'{(low_stock_items/total_items*100):.1f}%' if total_items > 0 else '0%']
                ]
                
                summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(Paragraph("Resumo do Estoque", self.subtitle_style))
                story.append(summary_table)
            
            doc.build(story)
            
            return {
                "status": "success",
                "message": f"Relatório de estoque gerado com sucesso",
                "filepath": filepath,
                "filename": filename,
                "data": {
                    "total_items": total_items,
                    "low_stock_items": low_stock_items
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao gerar relatório de estoque: {str(e)}"
            }

# Instância global do gerador
report_generator = ReportGenerator()

