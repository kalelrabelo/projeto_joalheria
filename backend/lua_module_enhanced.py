# backend/src/lua_module_enhanced.py

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
import os
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

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

lua_enhanced_bp = Blueprint("lua_enhanced", __name__)

# Configuração para relatórios
REPORTS_FOLDER = '/tmp/lua_reports'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf', 'docx'}

# Criar diretório de relatórios se não existir
os.makedirs(REPORTS_FOLDER, exist_ok=True)

def generate_report_pdf(report_name, report_data):
    """Gerar PDF de relatório"""
    try:
        path = os.path.join(REPORTS_FOLDER, f"{report_name}.pdf")
        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter

        # Título do relatório
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Relatório: {report_name}")

        # Data de geração
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # Conteúdo do relatório
        y = height - 120
        c.setFont("Helvetica", 10)

        if isinstance(report_data, dict):
            for key, value in report_data.items():
                if y < 50:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 10)
                c.drawString(50, y, f"{key}: {value}")
                y -= 20
        elif isinstance(report_data, list):
            for item in report_data:
                if y < 50:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 10)
                c.drawString(50, y, str(item))
                y -= 20
        else:
            c.drawString(50, y, str(report_data))

        c.save()
        return path
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
        return None

def execute_action(command: str):
    """Interpretar e executar comandos em linguagem natural"""
    try:
        command = (command or "").lower().strip()

        # Vales
        if "vale" in command or "adiantamento" in command:
            return handle_vale_command(command)
        # Viagens e hospedagens
        elif any(k in command for k in ["viagem", "hospedagem", "hotel"]):
            return handle_travel_command(command)
        # Produção
        elif any(k in command for k in ["produção", "producao", "horas", "trabalho"]):
            return handle_production_command(command)
        # Caixa
        elif any(k in command for k in ["caixa", "entrada", "saída", "saida"]):
            return handle_caixa_command(command)
        # Folha de Pagamento
        elif any(k in command for k in ["folha", "pagamento", "salário", "salario"]):
            return handle_payroll_command(command)
        # Relatórios
        elif any(k in command for k in ["relatório", "relatorio"]):
            return handle_report_command(command)
        # Configurações
        elif any(k in command for k in ["horário", "horario", "configuração", "configuracao"]):
            return handle_config_command(command)
