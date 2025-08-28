from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import os

class ValePrinter:
    def __init__(self):
        self.output_dir = "/tmp/vales_impressos"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_vale_pdf(self, employee_name, vale_amount, remaining_salary):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vale_{employee_name.replace(' ', '_')}_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)

            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter

            # Título
            c.setFont("Helvetica-Bold", 24)
            c.drawString(inch, height - inch, "Comprovante de Vale")

            # Informações do Vale
            c.setFont("Helvetica", 12)
            y_position = height - inch - 0.5 * inch
            c.drawString(inch, y_position, f"Funcionário: {employee_name}")
            y_position -= 0.25 * inch
            c.drawString(inch, y_position, f"Valor do Vale: R$ {vale_amount:.2f}")
            y_position -= 0.25 * inch
            c.drawString(inch, y_position, f"Data e Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            y_position -= 0.25 * inch
            c.drawString(inch, y_position, f"Salário Restante: R$ {remaining_salary:.2f}")

            # Campo para Assinatura
            y_position -= 1.0 * inch
            c.drawString(inch, y_position, "_____________________________________")
            y_position -= 0.2 * inch
            c.drawString(inch, y_position, "Assinatura do Funcionário")

            c.save()
            return {"status": "success", "filepath": filepath, "message": "PDF do vale gerado com sucesso."}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao gerar PDF do vale: {str(e)}"}

    def print_vale(self, pdf_path):
        try:
            # Simulação de impressão
            # Em um ambiente real, aqui seria a integração com uma API de impressão ou comando de sistema
            print(f"[VALE PRINTER] Enviando PDF para impressão: {pdf_path}")
            return {"status": "success", "message": "Vale enviado para impressão (simulado)."}
        except Exception as e:
            return {"status": "error", "message": f"Erro ao enviar vale para impressão: {str(e)}"}

vale_printer = ValePrinter()


