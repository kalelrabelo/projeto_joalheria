from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
import os
import re
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
from src.models.material import Material # Importar Material para Inventory
from src.models.report_history import ReportHistory # Importar ReportHistory

from src.lua_core.lua_free_ai_engine import LuaFreeAIEngine as LuaAIEngine

from src.utils.employee_search import extract_employee_name_from_command, find_employee_by_name

lua_enhanced_bp = Blueprint("lua_enhanced", __name__)

# Configuração para relatórios
REPORTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
    os.pardir, os.pardir, os.pardir, 
    'tmp', 'lua_reports')

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "pdf", "docx"}

# Criar diretório de relatórios se não existir
os.makedirs(REPORTS_FOLDER, exist_ok=True)

def generate_report_pdf(report_name, report_data, command_text):
    """Gerar PDF de relatório e registrar no histórico."""
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

        # Registrar no histórico
        new_report = ReportHistory(
            filename=os.path.basename(path),
            command=command_text,
            generated_at=datetime.now()
        )
        db.session.add(new_report)
        db.session.commit()

        return path
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
        db.session.rollback()
        return None

def execute_action(command: str):
    """Interpretar e executar comandos em linguagem natural"""
    try:
        command = (command or "").lower().strip()

        # Histórico de PDFs
        if any(k in command for k in ["histórico de pdfs", "historico de pdfs", "últimos pdfs", "ultimos pdfs"]):
            return handle_pdf_history_command(command)
        # Relatórios (verificar primeiro para evitar conflito com "caixa")
        if any(k in command for k in ["relatório", "relatorio"]):
            return handle_report_command(command)
        # Vales
        if "vale" in command or "adiantamento" in command:
            return handle_vale_command(command)
        # Encomendas
        if "encomendas" in command:
            return handle_encomendas_command(command)
        # Inventário/Estoque
        if any(k in command for k in ["inventário", "inventario", "estoque"]):
            return handle_inventory_command(command)
        # Vendas
        if "vendas" in command:
            return handle_sales_command(command)
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
        # Configurações
        elif any(k in command for k in ["horário", "horario", "configuração", "configuracao"]):
            return handle_config_command(command)
        # Geração de Descrição de Produto
        elif "gerar descrição" in command or "descrição de produto" in command:
            return handle_generate_product_description_command(command)
        else:
            return {"status": "error", "message": "Comando não reconhecido. Ex.: 'adiciona vale para João de R$500', 'gera relatório de caixa', 'gerar descrição de produto'."}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao executar comando: {str(e)}"}

def handle_vale_command(command: str):
    """Processar comandos relacionados a vales."""
    try:
        # Se for um pedido de visualização de vales
        if "mostre" in command or "ver" in command or "visualizar" in command or "últimos vales da semana" in command or "ultimos vales da semana" in command:
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            vales = Vale.query.filter(Vale.date >= start_of_week).all()
            
            if not vales:
                return {"status": "info", "message": "Nenhum vale encontrado para esta semana.", "data": []}

            vales_data = [
                {
                    "id": vale.id,
                    "employee_name": vale.employee.name,
                    "amount": vale.amount,
                    "date": vale.date.strftime("%d/%m/%Y"),
                    "description": vale.description
                }
                for vale in vales
            ]
            return {"status": "success", "message": "Aqui estão os vales da semana:", "data": vales_data}

        # Valor
        valor_match = re.search(r" (?:r\$|rs|reais?)\s*(\d+(?:[.,]\d{2})?)", command)
        if not valor_match:
            valor_match = re.search(r"(\d+(?:[.,]\d{2})?)\s*(?:r\$|rs|reais?)", command)
        if not valor_match:
            valor_match = re.search(r"(\d+(?:[.,]\d{2})?)", command)
        if not valor_match:
            return {"status": "error", "message": "Não identifiquei o valor. Use 'R$500' ou '500 reais'."}
        valor = float(valor_match.group(1).replace(",", ".")) if valor_match else 0.0

        # Funcionário
        nome_funcionario = extract_employee_name_from_command(command)
        if not nome_funcionario:
            return {"status": "error", "message": "Não identifiquei o funcionário. Ex.: 'vale para João de R$500'."}

        resultado_busca = find_employee_by_name(nome_funcionario)
        if resultado_busca["status"] == "multiple_matches":
            options_text = "\n".join([f'- {opt["name"]} (similaridade: {opt["similarity"]:.0%})' for opt in resultado_busca["options"][:5]])
            return {"status": "info", "message": f"Vários funcionários encontrados para '{nome_funcionario}'. Escolha:\n{options_text}"}
        if resultado_busca["status"] == "error":
            return {"status": "error", "message": resultado_busca["message"]}

        funcionario: Employee = resultado_busca["employee"]

        # Criar Vale
        novo_vale = Vale(
            employee_id=funcionario.id,
            amount=-valor,
            description=f"Vale para {funcionario.name} (por Rabelo)",
            date=datetime.now()
        )
        db.session.add(novo_vale)
        db.session.flush()  # garante novo_vale.id

        # Registrar no Caixa (saida)
        transacao_caixa = CaixaTransaction(
            type='saida',
            amount=-valor,
            date=datetime.now().strftime('%Y-%m-%d'),  # model usa String
            description=f"Vale para {funcionario.name} em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            employee_id=funcionario.id,
            vale_id=novo_vale.id
        )
        db.session.add(transacao_caixa)
        db.session.flush()  # garante transacao_caixa.id

        # Atualizar folha
        payroll_updated = novo_vale.update_payroll()

        # Persistir tudo
        db.session.commit()

        # PDF opcional
        download_url = None
        if ("imprime" in command) or ("imprimir" in command):
            vale_data = {
                "Funcionário": funcionario.name,
                "Valor": f"R$ {valor:.2f}",
                "Data": datetime.now().strftime('%d/%m/%Y'),
                "Descrição": novo_vale.description
            }
            pdf_path = generate_report_pdf(
                f"vale_{funcionario.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                vale_data,
                command # Passar o comando para registro no histórico
            )
            if pdf_path:
                download_url = f"/api/lua_enhanced/download/{os.path.basename(pdf_path)}"

        payroll_info = ""
        if payroll_updated:
            payroll_info = f" Folha atualizada: salário líquido R${payroll_updated.net_salary:.2f}."

        return {"status": "success", "message": f"✅ Vale de R${valor:.2f} registrado para {funcionario.name}. Transação no caixa criada.{payroll_info}", "download_url": download_url, "data": {"funcionario": funcionario.name, "valor": valor, "vale_id": novo_vale.id, "caixa_transaction_id": transacao_caixa.id}}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao processar vale: {str(e)}"}

def handle_encomendas_command(command: str):
    """Processar comandos relacionados a encomendas."""
    try:
        today = datetime.now().date()
        encomendas = Order.query.filter(db.func.date(Order.order_date) == today).all()

        if not encomendas:
            return {"status": "info", "message": "Nenhuma encomenda encontrada para hoje.", "data": []}

        encomendas_data = [
            {
                "id": encomenda.id,
                "customer_name": encomenda.customer.name if encomenda.customer else "N/A",
                "total_price": encomenda.total_price,
                "status": encomenda.status,
                "order_date": encomenda.order_date.strftime("%d/%m/%Y")
            }
            for encomenda in encomendas
        ]
        return {"status": "success", "message": "Aqui estão as encomendas de hoje:", "data": encomendas_data}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao buscar encomendas: {str(e)}"}

def handle_inventory_command(command: str):
    """Processar comandos relacionados ao inventário/estoque."""
    try:
        inventory_items = Inventory.query.all()

        if not inventory_items:
            return {"status": "info", "message": "Nenhum item no inventário encontrado.", "data": []}

        inventory_data = [
            {
                "id": item.id,
                "material_name": item.material.name if item.material else "N/A",
                "quantity_available": item.quantity_available,
                "unit": item.unit,
                "minimum_stock": item.minimum_stock,
                "cost_per_unit": item.cost_per_unit,
                "is_low_stock": item.is_low_stock()
            }
            for item in inventory_items
        ]
        return {"status": "success", "message": "Aqui está o seu inventário:", "data": inventory_data}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao buscar inventário: {str(e)}"}

def handle_sales_command(command: str):
    """Processar comandos relacionados a vendas."""
    try:
        sales = Order.query.filter(Order.status == 'completed').all()

        if not sales:
            return {"status": "info", "message": "Nenhuma venda encontrada.", "data": []}

        sales_data = [
            {
                "id": sale.id,
                "customer_name": sale.customer.name if sale.customer else "N/A",
                "total_price": sale.total_price,
                "status": sale.status,
                "order_date": sale.order_date.strftime("%d/%m/%Y")
            }
            for sale in sales
        ]
        return {"status": "success", "message": "Aqui estão as vendas:", "data": sales_data}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao buscar vendas: {str(e)}"}

def handle_report_command(command: str):
    """Processar comandos de relatórios."""
    try:
        report_type = "geral"
        if "caixa" in command:
            report_type = "caixa"
        elif "estoque" in command:
            report_type = "estoque"
        elif any(k in command for k in ["funcionario", "funcionários", "funcionarios"]):
            report_type = "funcionarios"
        elif "vendas" in command:
            report_type = "vendas"
        elif "financeiro" in command:
            report_type = "financeiro"

        if report_type == "caixa":
            transactions = CaixaTransaction.query.all()
            total_entradas = sum(t.amount for t in transactions if t.amount > 0)
            total_saidas = sum(abs(t.amount) for t in transactions if t.amount < 0)
            saldo = total_entradas - total_saidas
            report_data = {"Total de Entradas": f"R$ {total_entradas:.2f}", "Total de Saídas": f"R$ {total_saidas:.2f}", "Saldo Atual": f"R$ {saldo:.2f}", "Total de Transações": len(transactions)}
        elif report_type == "estoque":
            inventory_items = Inventory.query.all()
            total_items = len(inventory_items)
            low_stock_items = [item for item in inventory_items if getattr(item, 'quantity_available', 0) < item.minimum_stock]
            report_data = {"Total de Itens": total_items, "Itens com Estoque Baixo": len(low_stock_items)}
        elif report_type == "funcionarios":
            employees = Employee.query.all()
            active_employees = [emp for emp in employees if getattr(emp, 'active', True)]
            report_data = {"Total de Funcionários": len(employees), "Funcionários Ativos": len(active_employees), "Lista de Funcionários": [emp.name for emp in active_employees]}
        elif report_type == "vendas":
            orders = Order.query.all()
            completed_orders = [order for order in orders if getattr(order, 'status', '') == 'completed']
            total_sales = sum(getattr(order, 'total_price', 0) or 0 for order in completed_orders)
            report_data = {"Total de Pedidos": len(orders), "Pedidos Concluídos": len(completed_orders), "Valor Total de Vendas": f"R$ {total_sales:.2f}"}
        else:
            report_data = {"Relatório": "Relatório geral do sistema", "Data": datetime.now().strftime('%d/%m/%Y %H:%M')}

        pdf_filename = f"relatorio_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pdf_path = generate_report_pdf(pdf_filename, report_data, command)
        download_url = f"/api/lua_enhanced/download/{os.path.basename(pdf_path)}" if pdf_path else None

        return {"status": "success", "message": f"📊 Relatório de {report_type} gerado com sucesso!", "download_url": download_url, "data": report_data}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao gerar relatório: {str(e)}"}

def handle_travel_command(command: str):
    return {"status": "success", "message": "✈️ Comando de viagem processado. Funcionalidade em desenvolvimento."}

def handle_production_command(command: str):
    return {"status": "success", "message": "🏭 Comando de produção processado. Funcionalidade em desenvolvimento."}

def handle_caixa_command(command: str):
    """Processar comandos de caixa (entrada/saída)."""
    try:
        # Valor
        valor_match = re.search(r" (?:r\$|rs|reais?)\s*(\d+(?:[.,]\d{2})?)", command)
        if not valor_match:
            valor_match = re.search(r"(\d+(?:[.,]\d{2})?)\s*(?:r\$|rs|reais?)", command)
        if not valor_match:
            valor_match = re.search(r"(\d+(?:[.,]\d{2})?)", command)
        if not valor_match:
            return {"status": "error", "message": "Não identifiquei o valor. Use 'R$500' ou '500 reais'."}
        valor = float(valor_match.group(1).replace(",", ".")) if valor_match else 0.0

        # Tipo de transação
        tipo_transacao = 'entrada' if 'entrada' in command else 'saida'

        # Descrição
        descricao = f"{tipo_transacao.capitalize()} de R${valor:.2f} em {datetime.now().strftime('%d/%m/%Y')}"

        # Criar transação
        nova_transacao = CaixaTransaction(
            type=tipo_transacao,
            amount=valor if tipo_transacao == 'entrada' else -valor,
            date=datetime.now().strftime('%Y-%m-%d'),
            description=descricao
        )
        db.session.add(nova_transacao)
        db.session.commit()

        return {"status": "success", "message": f"Transação de {tipo_transacao} de R${valor:.2f} registrada com sucesso."}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao processar transação de caixa: {str(e)}"}

def handle_payroll_command(command: str):
    return {"status": "success", "message": "💸 Comando de folha de pagamento processado. Funcionalidade em desenvolvimento."}

def handle_config_command(command: str):
    return {"status": "success", "message": "⚙️ Comando de configuração processado. Funcionalidade em desenvolvimento."}

def handle_generate_product_description_command(command: str):
    try:
        product_name_match = re.search(r"gerar descrição para (.+)", command)
        if not product_name_match:
            return {"status": "error", "message": "Não foi possível identificar o nome do produto. Use 'gerar descrição para [nome do produto]'."}
        
        product_name = product_name_match.group(1)
        ai_engine = LuaAIEngine()
        description = ai_engine._handle_product_description_action(command, {})['message']        
        return {"status": "success", "message": f"Descrição gerada para {product_name}:\n\n{description}"}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao gerar descrição do produto: {str(e)}"}

def handle_pdf_history_command(command: str):
    """Processar comandos para obter histórico de PDFs."""
    try:
        # Obter os últimos 5 relatórios do histórico
        recent_reports = ReportHistory.query.order_by(ReportHistory.generated_at.desc()).limit(5).all()

        if not recent_reports:
            return {"status": "info", "message": "Nenhum relatório em PDF foi gerado recentemente."}

        # Formatar a lista de relatórios para exibição
        reports_list = []
        for report in recent_reports:
            reports_list.append({
                "filename": report.filename,
                "command": report.command,
                "generated_at": report.generated_at.strftime("%d/%m/%Y %H:%M"),
                "download_url": f"/api/lua_enhanced/download/{report.filename}"
            })

        return {
            "status": "success",
            "message": "Aqui estão os últimos relatórios gerados:",
            "data": reports_list
        }
    except Exception as e:
        return {"status": "error", "message": f"Erro ao obter histórico de PDFs: {str(e)}"}

@lua_enhanced_bp.route("/execute", methods=["POST"])
def execute_command_route():
    data = request.get_json()
    command = data.get("command")
    if not command:
        return jsonify({"status": "error", "message": "Comando não fornecido."}), 400
    
    result = execute_action(command)
    return jsonify(result)

@lua_enhanced_bp.route("/download/<filename>", methods=["GET"])
def download_report(filename):
    """Rota para baixar um relatório PDF."""
    try:
        path = os.path.join(REPORTS_FOLDER, filename)
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
        else:
            return jsonify({"status": "error", "message": "Arquivo não encontrado."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao baixar arquivo: {str(e)}"}), 500



