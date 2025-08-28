#!/usr/bin/env python3
"""
Script para importar dados dos arquivos TXT reformatados para o banco de dados
"""

import os
import sys
import re
from datetime import datetime

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import SessionLocal, Funcionario, Joia, Cliente, Venda, Encomenda, MovimentacaoCaixa, ConsumoEnergia, Material, DashboardWidget, DashboardLayout, DashboardFilter, DashboardQuery, Base, engine

# from main import app # Remover esta linha se main.py não for mais o entrypoint

# Configuração do banco SQLite


def parse_date(date_str):
    """Converte string de data para datetime"""
    if not date_str or date_str == 'nan':
        return None
    
    try:
        # Formato: MM/DD/YY HH:MM:SS
        return datetime.strptime(date_str, '%m/%d/%y %H:%M:%S')
    except:
        try:
            # Formato: MM/DD/YY
            return datetime.strptime(date_str, '%m/%d/%y')
        except:
            return None

def parse_float(value_str):
    """Converte string para float, retorna None se inválido"""
    if not value_str or value_str == 'nan':
        return None
    try:
        return float(value_str)
    except:
        return None

def parse_int(value_str):
    """Converte string para int, retorna None se inválido"""
    if not value_str or value_str == 'nan':
        return None
    try:
        return int(float(value_str))
    except:
        return None

def import_financial_transactions(file_path):
    """Importa transações financeiras do arquivo caixa_reformatted.txt"""
    print("Importando transações financeiras...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir em registros
    registros = content.split('Registro ')[1:]  # Remove o primeiro elemento vazio
    
    count = 0
    for registro in registros:
        lines = registro.strip().split('\n')
        data = {}
        
        for line in lines[1:]:  # Pula a primeira linha que contém o número do registro
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        if 'data' in data and 'valor1' in data:
            transaction = FinancialTransaction(
                data=parse_date(data.get('data')),
                mes=parse_int(data.get('mes')),
                ano=parse_int(data.get('ano')),
                valor1=parse_float(data.get('valor1')),
                valor2=parse_float(data.get('valor2')),
                valor=data.get('valor', 'R$'),
                imposto=parse_float(data.get('imposto')),
                imposto2=parse_float(data.get('imposto2')),
                imposto3=parse_float(data.get('imposto3')),
                descricao=data.get('descricao', ''),
                grupo1=data.get('grupo1', ''),
                grupo2=data.get('grupo2', ''),
                idc=parse_float(data.get('idc')),
                nome=data.get('nome'),
                noticia=data.get('noticia'),
                caixa=parse_float(data.get('caixa', '0'))
            )
            
            db.session.add(transaction)
            count += 1
    
    db.session.commit()
    print(f"Importadas {count} transações financeiras")

def import_production_reports(file_path):
    """Importa relatórios de produção do arquivo cartas_reformatted.txt"""
    print("Importando relatórios de produção...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    registros = content.split('Registro ')[1:]
    
    count = 0
    for registro in registros:
        lines = registro.strip().split('\n')
        data = {}
        
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        if 'data' in data and 'assunto' in data:
            report = ProductionReport(
                data=parse_date(data.get('data')),
                lugar=data.get('lugar', ''),
                assunto=data.get('assunto', ''),
                mensagem=data.get('mensagem', ''),
                autor=data.get('autor', ''),
                estado=data.get('estado', 'OK'),
                noticia=data.get('noticia')
            )
            
            db.session.add(report)
            count += 1
    
    db.session.commit()
    print(f"Importados {count} relatórios de produção")

def import_advanced_orders(file_path):
    """Importa encomendas avançadas do arquivo encomendas_reformatted.txt"""
    print("Importando encomendas avançadas...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    registros = content.split('Registro ')[1:]
    
    count = 0
    for registro in registros:
        lines = registro.strip().split('\n')
        data = {}
        
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        if 'idc' in data and 'data_encomenda' in data:
            order = AdvancedOrder(
                idc=parse_int(data.get('idc')),
                data_encomenda=parse_date(data.get('data_encomenda')),
                modo_encomenda=data.get('modo_encomenda'),
                pessoala=data.get('pessoala'),
                pessoaaqui=data.get('pessoaaqui'),
                praco=parse_date(data.get('praco')),
                estado_encomenda=data.get('estado_encomenda', 'novo'),
                noticia=data.get('noticia'),
                ultimanota=parse_int(data.get('ultimanota', '0')),
                imposto1=data.get('imposto1'),
                imposto1v=parse_float(data.get('imposto1v')),
                imposto2=data.get('imposto2'),
                imposto2v=parse_float(data.get('imposto2v')),
                imposto3=data.get('imposto3'),
                imposto3v=parse_float(data.get('imposto3v')),
                imposto4=data.get('imposto4'),
                imposto4v=parse_float(data.get('imposto4v')),
                imposto5=data.get('imposto5'),
                imposto5v=parse_float(data.get('imposto5v')),
                imposto6=data.get('imposto6'),
                imposto6v=parse_float(data.get('imposto6v')),
                desconto_encomenda=parse_float(data.get('desconto_encomenda', '0')),
                valor_total_encomenda=data.get('valor_total_encomenda', 'R$'),
                cambio=parse_float(data.get('cambio', '1')),
                praco1=parse_int(data.get('praco1', '30')),
                praco1f=parse_float(data.get('praco1f', '1.1')),
                praco2=parse_int(data.get('praco2', '60')),
                praco2f=parse_float(data.get('praco2f', '1.15')),
                praco3=parse_int(data.get('praco3', '90')),
                praco3f=parse_float(data.get('praco3f', '1.2')),
                taxa1v=parse_float(data.get('taxa1v', '0')),
                taxa2v=parse_float(data.get('taxa2v', '0')),
                taxa3v=parse_float(data.get('taxa3v', '0')),
                entregaonde=data.get('entregaonde'),
                fabricarate=parse_date(data.get('fabricarate'))
            )
            
            db.session.add(order)
            count += 1
    
    db.session.commit()
    print(f"Importadas {count} encomendas avançadas")

def import_discounts(file_path):
    """Importa tabela de descontos do arquivo descontos_reformatted.txt"""
    print("Importando tabela de descontos...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    registros = content.split('Registro ')[1:]
    
    count = 0
    for registro in registros:
        lines = registro.strip().split('\n')
        data = {}
        
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        if 'soma' in data and 'desconto' in data:
            discount = DiscountTable(
                soma=parse_float(data.get('soma')),
                desconto=parse_float(data.get('desconto'))
            )
            
            db.session.add(discount)
            count += 1
    
    db.session.commit()
    print(f"Importados {count} descontos")

def import_cost_calculations(file_path):
    """Importa cálculos de custo do arquivo custos_reformatted.txt"""
    print("Importando cálculos de custo...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    registros = content.split('Registro ')[1:]
    
    count = 0
    for registro in registros:
        lines = registro.strip().split('\n')
        data = {}
        
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        if 'ano' in data and 'mes' in data:
            calculation = CostCalculation(
                ano=parse_int(data.get('ano')),
                mes=parse_int(data.get('mes')),
                empregados=parse_int(data.get('empregados')),
                horas_por_semana=parse_int(data.get('HorasPorSemana')),
                rs_por_hora=parse_float(data.get('RSporHora'))
            )
            
            db.session.add(calculation)
            count += 1
    
    db.session.commit()
    print(f"Importados {count} cálculos de custo")

def import_stones(file_path):
    """Importa pedras expandidas do arquivo pedras_reformatted.txt"""
    print("Importando catálogo expandido de pedras...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    registros = content.split('Registro ')[1:]
    
    count = 0
    for registro in registros:
        lines = registro.strip().split('\n')
        data = {}
        
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        if 'idpe' in data:
            idpe = parse_int(data.get('idpe'))
            
            # Verificar se a pedra já existe
            existing_stone = Stone.query.filter_by(idpe=idpe).first()
            if existing_stone:
                # Atualizar pedra existente com novos campos
                existing_stone.tipo_pedra = data.get('tipo_pedra')
                existing_stone.lapidacao_pedra = data.get('lapidacao_pedra')
                existing_stone.material_pedra = data.get('material_pedra')
                existing_stone.cor_pedra = data.get('cor_pedra')
                existing_stone.comprimento_pedra = parse_float(data.get('comprimento_pedra'))
                existing_stone.largura_pedra = parse_float(data.get('largura_pedra'))
                existing_stone.altura_pedra = parse_float(data.get('altura_pedra'))
                existing_stone.peso_pedra = parse_float(data.get('peso_pedra'))
                existing_stone.preco_pedra = parse_float(data.get('preco_pedra'))
                existing_stone.status_estoque = data.get('status_estoque')
                existing_stone.nasjoias = parse_int(data.get('nasjoias', '0'))
                count += 1
            else:
                # Criar nova pedra
                stone = Stone(
                    idpe=idpe,
                    foto=data.get('foto'),
                    tipo_pedra=data.get('tipo_pedra'),
                    lapidacao_pedra=data.get('lapidacao_pedra'),
                    material_pedra=data.get('material_pedra'),
                    cor_pedra=data.get('cor_pedra'),
                    comprimento_pedra=parse_float(data.get('comprimento_pedra')),
                    largura_pedra=parse_float(data.get('largura_pedra')),
                    altura_pedra=parse_float(data.get('altura_pedra')),
                    peso_pedra=parse_float(data.get('peso_pedra')),
                    preco_pedra=parse_float(data.get('preco_pedra')),
                    noticia=data.get('noticia'),
                    status_estoque=data.get('status_estoque'),
                    qmin=parse_float(data.get('qmin', '0')),
                    nasjoias=parse_int(data.get('nasjoias', '0')),
                    # Campos de compatibilidade
                    tipo=data.get('tipo_pedra'),
                    lapidacao=data.get('lapidacao_pedra'),
                    material=data.get('material_pedra'),
                    cor=data.get('cor_pedra'),
                    comprimento=parse_float(data.get('comprimento_pedra')),
                    largura=parse_float(data.get('largura_pedra')),
                    altura=parse_float(data.get('altura_pedra')),
                    peso=parse_float(data.get('peso_pedra')),
                    preco=parse_float(data.get('preco_pedra')),
                    ststoque=data.get('status_estoque')
                )
                
                db.session.add(stone)
                count += 1
    
    db.session.commit()
    print(f"Importadas/atualizadas {count} pedras")

def main():
    """Função principal para importar todos os dados"""
    data_dir = '/home/ubuntu/new_data/reformatted_txts_for_viewing_new (1)'
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        # Importar dados
        files_to_import = [
            ('caixa_reformatted.txt', import_financial_transactions),
            ('cartas_reformatted.txt', import_production_reports),
            ('encomendas_reformatted.txt', import_advanced_orders),
            ('descontos_reformatted.txt', import_discounts),
            ('custos_reformatted.txt', import_cost_calculations),
            ('pedras_reformatted.txt', import_stones)
        ]
        
        for filename, import_func in files_to_import:
            file_path = os.path.join(data_dir, filename)
            if os.path.exists(file_path):
                try:
                    import_func(file_path)
                except Exception as e:
                    print(f"Erro ao importar {filename}: {e}")
            else:
                print(f"Arquivo não encontrado: {file_path}")
        
        print("Importação concluída!")

if __name__ == '__main__':
    main()

