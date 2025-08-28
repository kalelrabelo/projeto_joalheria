# backend/src/lua_file_processor.py

import pandas as pd
import PyPDF2
import re
from datetime import datetime, timedelta
import json
import os
from werkzeug.utils import secure_filename

class EnergyFileProcessor:
    """Processador de arquivos de energia (PDF, CSV, XLSX)"""
    
    def __init__(self):
        self.supported_formats = ['pdf', 'csv', 'xlsx', 'xls']
        self.energy_data_history = []
    
    def process_energy_file(self, file_path, file_type):
        """Processa arquivo de energia e extrai dados relevantes"""
        try:
            if file_type.lower() == 'pdf':
                return self._process_energy_pdf(file_path)
            elif file_type.lower() == 'csv':
                return self._process_energy_csv(file_path)
            elif file_type.lower() in ['xlsx', 'xls']:
                return self._process_energy_excel(file_path)
            else:
                return {
                    "status": "error",
                    "message": f"Formato de arquivo não suportado: {file_type}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao processar arquivo de energia: {str(e)}"
            }
    
    def _process_energy_pdf(self, file_path):
        """Processa PDF de conta de energia"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
            
            # Extrair dados da conta de energia
            energy_data = self._extract_energy_data_from_text(text_content)
            
            if energy_data:
                self._save_energy_data(energy_data)
                return {
                    "status": "success",
                    "message": "Conta de energia processada com sucesso",
                    "data": energy_data
                }
            else:
                return {
                    "status": "error",
                    "message": "Não foi possível extrair dados de energia do PDF"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao processar PDF de energia: {str(e)}"
            }
    
    def _process_energy_csv(self, file_path):
        """Processa CSV de dados de energia"""
        try:
            df = pd.read_csv(file_path)
            
            # Tentar identificar colunas relevantes
            energy_columns = self._identify_energy_columns(df.columns.tolist())
            
            if not energy_columns:
                return {
                    "status": "error",
                    "message": "Não foi possível identificar colunas de energia no CSV"
                }
            
            # Processar dados
            energy_data = self._process_energy_dataframe(df, energy_columns)
            
            if energy_data:
                self._save_energy_data(energy_data)
                return {
                    "status": "success",
                    "message": "Dados de energia CSV processados com sucesso",
                    "data": energy_data
                }
            else:
                return {
                    "status": "error",
                    "message": "Erro ao processar dados do CSV"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao processar CSV de energia: {str(e)}"
            }
    
    def _process_energy_excel(self, file_path):
        """Processa Excel de dados de energia"""
        try:
            # Tentar ler todas as planilhas
            excel_file = pd.ExcelFile(file_path)
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Tentar identificar colunas relevantes
                energy_columns = self._identify_energy_columns(df.columns.tolist())
                
                if energy_columns:
                    # Processar dados da primeira planilha válida encontrada
                    energy_data = self._process_energy_dataframe(df, energy_columns)
                    
                    if energy_data:
                        self._save_energy_data(energy_data)
                        return {
                            "status": "success",
                            "message": f"Dados de energia Excel processados com sucesso (planilha: {sheet_name})",
                            "data": energy_data
                        }
            
            return {
                "status": "error",
                "message": "Não foi possível identificar dados de energia no Excel"
            }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao processar Excel de energia: {str(e)}"
            }
    
    def _extract_energy_data_from_text(self, text):
        """Extrai dados de energia de texto (PDF)"""
        try:
            energy_data = {
                "source": "pdf",
                "processed_at": datetime.now().isoformat(),
                "consumption_kwh": None,
                "cost_total": None,
                "cost_per_kwh": None,
                "period_start": None,
                "period_end": None,
                "raw_text": text[:500]  # Primeiros 500 caracteres para referência
            }
            
            # Padrões para extrair dados comuns de contas de energia
            patterns = {
                "consumption": [
                    r'consumo.*?(\d+(?:,\d+)?)\s*kwh',
                    r'energia.*?(\d+(?:,\d+)?)\s*kwh',
                    r'(\d+(?:,\d+)?)\s*kwh'
                ],
                "cost": [
                    r'total.*?r\$\s*(\d+(?:,\d+)?)',
                    r'valor.*?r\$\s*(\d+(?:,\d+)?)',
                    r'r\$\s*(\d+(?:,\d+)?)'
                ],
                "period": [
                    r'período.*?(\d{2}/\d{2}/\d{4}).*?(\d{2}/\d{2}/\d{4})',
                    r'(\d{2}/\d{2}/\d{4}).*?(\d{2}/\d{2}/\d{4})'
                ]
            }
            
            text_lower = text.lower()
            
            # Extrair consumo em kWh
            for pattern in patterns["consumption"]:
                match = re.search(pattern, text_lower)
                if match:
                    energy_data["consumption_kwh"] = float(match.group(1).replace(',', '.'))
                    break
            
            # Extrair custo total
            for pattern in patterns["cost"]:
                match = re.search(pattern, text_lower)
                if match:
                    energy_data["cost_total"] = float(match.group(1).replace(',', '.'))
                    break
            
            # Extrair período
            for pattern in patterns["period"]:
                match = re.search(pattern, text_lower)
                if match:
                    energy_data["period_start"] = match.group(1)
                    energy_data["period_end"] = match.group(2)
                    break
            
            # Calcular custo por kWh se possível
            if energy_data["consumption_kwh"] and energy_data["cost_total"]:
                energy_data["cost_per_kwh"] = energy_data["cost_total"] / energy_data["consumption_kwh"]
            
            return energy_data if energy_data["consumption_kwh"] or energy_data["cost_total"] else None
            
        except Exception as e:
            print(f"Erro ao extrair dados de energia do texto: {str(e)}")
            return None
    
    def _identify_energy_columns(self, columns):
        """Identifica colunas relevantes para dados de energia"""
        energy_keywords = {
            "consumption": ["consumo", "kwh", "energia", "consumption", "energy"],
            "cost": ["custo", "valor", "preco", "cost", "price", "total"],
            "date": ["data", "periodo", "mes", "date", "period", "month"],
            "hour": ["hora", "hour", "time", "horario"]
        }
        
        identified_columns = {}
        
        for col in columns:
            col_lower = str(col).lower()
            
            for category, keywords in energy_keywords.items():
                if any(keyword in col_lower for keyword in keywords):
                    if category not in identified_columns:
                        identified_columns[category] = col
                    break
        
        return identified_columns
    
    def _process_energy_dataframe(self, df, energy_columns):
        """Processa DataFrame com dados de energia"""
        try:
            energy_data = {
                "source": "structured_data",
                "processed_at": datetime.now().isoformat(),
                "total_records": len(df),
                "consumption_kwh": None,
                "cost_total": None,
                "cost_per_kwh": None,
                "daily_data": [],
                "hourly_data": []
            }
            
            # Processar consumo total
            if "consumption" in energy_columns:
                consumption_col = energy_columns["consumption"]
                if consumption_col in df.columns:
                    total_consumption = df[consumption_col].sum()
                    energy_data["consumption_kwh"] = float(total_consumption)
            
            # Processar custo total
            if "cost" in energy_columns:
                cost_col = energy_columns["cost"]
                if cost_col in df.columns:
                    total_cost = df[cost_col].sum()
                    energy_data["cost_total"] = float(total_cost)
            
            # Calcular custo por kWh
            if energy_data["consumption_kwh"] and energy_data["cost_total"]:
                energy_data["cost_per_kwh"] = energy_data["cost_total"] / energy_data["consumption_kwh"]
            
            # Processar dados por período se houver coluna de data
            if "date" in energy_columns and energy_columns["date"] in df.columns:
                date_col = energy_columns["date"]
                
                # Agrupar por data se possível
                try:
                    df[date_col] = pd.to_datetime(df[date_col])
                    daily_summary = df.groupby(df[date_col].dt.date).agg({
                        energy_columns.get("consumption", df.columns[0]): "sum",
                        energy_columns.get("cost", df.columns[0]): "sum"
                    }).to_dict('index')
                    
                    energy_data["daily_data"] = [
                        {
                            "date": str(date),
                            "consumption": float(data.get(energy_columns.get("consumption", ""), 0)),
                            "cost": float(data.get(energy_columns.get("cost", ""), 0))
                        }
                        for date, data in daily_summary.items()
                    ]
                except:
                    pass  # Se não conseguir processar datas, continua sem dados diários
            
            return energy_data
            
        except Exception as e:
            print(f"Erro ao processar DataFrame de energia: {str(e)}")
            return None
    
    def _save_energy_data(self, energy_data):
        """Salva dados de energia no histórico"""
        self.energy_data_history.append(energy_data)
        
        # Manter apenas os últimos 12 meses de dados
        if len(self.energy_data_history) > 12:
            self.energy_data_history = self.energy_data_history[-12:]
    
    def calculate_energy_metrics(self, period="month"):
        """Calcula métricas de energia por período"""
        if not self.energy_data_history:
            return {
                "status": "error",
                "message": "Nenhum dado de energia disponível"
            }
        
        try:
            latest_data = self.energy_data_history[-1]
            
            metrics = {
                "period": period,
                "calculated_at": datetime.now().isoformat(),
                "consumption_kwh": latest_data.get("consumption_kwh", 0),
                "cost_total": latest_data.get("cost_total", 0),
                "cost_per_kwh": latest_data.get("cost_per_kwh", 0)
            }
            
            # Calcular métricas por período
            if period == "day" and latest_data.get("daily_data"):
                daily_data = latest_data["daily_data"]
                if daily_data:
                    avg_daily_consumption = sum(d["consumption"] for d in daily_data) / len(daily_data)
                    avg_daily_cost = sum(d["cost"] for d in daily_data) / len(daily_data)
                    
                    metrics.update({
                        "daily_avg_consumption": avg_daily_consumption,
                        "daily_avg_cost": avg_daily_cost,
                        "days_in_period": len(daily_data)
                    })
            
            elif period == "week":
                if metrics["consumption_kwh"] and metrics["cost_total"]:
                    metrics.update({
                        "weekly_avg_consumption": metrics["consumption_kwh"] / 4,  # Aproximação
                        "weekly_avg_cost": metrics["cost_total"] / 4
                    })
            
            elif period == "month":
                # Dados mensais já estão no formato correto
                pass
            
            return {
                "status": "success",
                "message": f"Métricas de energia calculadas para {period}",
                "data": metrics
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao calcular métricas de energia: {str(e)}"
            }
    
    def get_energy_history(self, months=6):
        """Retorna histórico de dados de energia"""
        return {
            "status": "success",
            "data": self.energy_data_history[-months:] if months else self.energy_data_history,
            "total_records": len(self.energy_data_history)
        }
    
    def generate_energy_alerts(self):
        """Gera alertas baseados no consumo de energia"""
        if len(self.energy_data_history) < 2:
            return {
                "status": "info",
                "message": "Dados insuficientes para gerar alertas",
                "alerts": []
            }
        
        try:
            current_data = self.energy_data_history[-1]
            previous_data = self.energy_data_history[-2]
            
            alerts = []
            
            # Alerta de aumento de consumo
            if (current_data.get("consumption_kwh", 0) > 
                previous_data.get("consumption_kwh", 0) * 1.2):
                alerts.append({
                    "type": "warning",
                    "title": "Aumento significativo no consumo",
                    "message": f"Consumo aumentou {((current_data.get('consumption_kwh', 0) / previous_data.get('consumption_kwh', 1)) - 1) * 100:.1f}% em relação ao período anterior"
                })
            
            # Alerta de aumento de custo
            if (current_data.get("cost_total", 0) > 
                previous_data.get("cost_total", 0) * 1.15):
                alerts.append({
                    "type": "warning",
                    "title": "Aumento no custo de energia",
                    "message": f"Custo aumentou {((current_data.get('cost_total', 0) / previous_data.get('cost_total', 1)) - 1) * 100:.1f}% em relação ao período anterior"
                })
            
            # Alerta de eficiência
            current_efficiency = current_data.get("cost_per_kwh", 0)
            previous_efficiency = previous_data.get("cost_per_kwh", 0)
            
            if current_efficiency > previous_efficiency * 1.1:
                alerts.append({
                    "type": "info",
                    "title": "Mudança na tarifa de energia",
                    "message": f"Custo por kWh aumentou de R$ {previous_efficiency:.3f} para R$ {current_efficiency:.3f}"
                })
            
            return {
                "status": "success",
                "alerts": alerts,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao gerar alertas de energia: {str(e)}",
                "alerts": []
            }

# Instância global do processador de energia
energy_processor = EnergyFileProcessor()

