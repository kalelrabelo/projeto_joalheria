# backend/src/supplier_commands.py

import re
from datetime import datetime
from src.models.user import db
from src.models.supplier import Supplier
from src.models.caixa import CaixaTransaction
from src.entity_search import extract_entity_name_from_command, find_entity_by_name

def handle_supplier_command(command):
    """Processar comandos relacionados a fornecedores"""
    try:
        # Determinar tipo de comando
        if any(palavra in command for palavra in ["compra", "pedido", "material"]):
            return handle_supplier_purchase_command(command)
        elif any(palavra in command for palavra in ["cadastrar", "adicionar", "novo fornecedor"]):
            return handle_supplier_registration_command(command)
        elif any(palavra in command for palavra in ["buscar", "procurar", "encontrar"]):
            return handle_supplier_search_command(command)
        else:
            return handle_supplier_general_command(command)
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao processar comando de fornecedor: {str(e)}"
        }

def handle_supplier_purchase_command(command):
    """Processar comandos de compras de fornecedores"""
    try:
        # Extrair nome do fornecedor
        nome_fornecedor = extract_entity_name_from_command(command, "fornecedor")
        
        if not nome_fornecedor:
            return {
                "status": "error",
                "message": "Não foi possível identificar o nome do fornecedor. Tente: 'compra de ouro do fornecedor João'"
            }
        
        # Buscar fornecedor usando busca inteligente
        search_result = find_entity_by_name(Supplier, nome_fornecedor)
        
        if search_result["status"] == "error":
            # Se fornecedor não existe, sugerir cadastro
            return {
                "status": "supplier_not_found",
                "message": f"Fornecedor '{nome_fornecedor}' não encontrado. Deseja cadastrar este fornecedor primeiro?",
                "suggested_name": nome_fornecedor
            }
        
        elif search_result["status"] == "multiple_matches":
            options_text = "\n".join([
                f"{i+1}. {opt['name']}"
                for i, opt in enumerate(search_result["options"])
            ])
            return {
                "status": "multiple_matches",
                "message": f"Múltiplos fornecedores encontrados para '{nome_fornecedor}'. Escolha uma opção:\n{options_text}",
                "options": search_result["options"]
            }
        
        fornecedor = search_result["entity"]
        
        # Extrair valor da compra
        valor_match = re.search(r'(?:r\$|rs|valor)\s*(\d+(?:[.,]\d{2})?)', command)
        if not valor_match:
            valor_match = re.search(r'(\d+(?:[.,]\d{2})?)', command)
        
        valor = float(valor_match.group(1).replace(',', '.')) if valor_match else 0.0
        
        # Extrair descrição do material/produto
        material_match = re.search(r'(?:ouro|prata|pedra|material|produto)\s*([^,]*)', command)
        material = material_match.group(0).strip() if material_match else "Material"
        
        # Registrar transação no caixa
        if valor > 0:
            transacao_caixa = CaixaTransaction(
                type='saida',
                amount=valor,
                date=datetime.now().strftime('%Y-%m-%d'),
                description=f"Compra de {material} - {fornecedor.name}",
                notes=f"Comando: {command}"
            )
            
            db.session.add(transacao_caixa)
            db.session.commit()
        
        return {
            "status": "success",
            "message": f"🛒 Compra registrada: {material} de {fornecedor.name}, valor R${valor:.2f}",
            "data": {
                "fornecedor": fornecedor.name,
                "fornecedor_id": fornecedor.id,
                "material": material,
                "valor": valor
            }
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Erro ao processar compra: {str(e)}"
        }

def handle_supplier_registration_command(command):
    """Processar comandos de cadastro de fornecedores"""
    try:
        # Extrair nome do fornecedor
        nome_fornecedor = extract_entity_name_from_command(command, "fornecedor")
        
        if not nome_fornecedor:
            return {
                "status": "error",
                "message": "Não foi possível identificar o nome do fornecedor. Tente: 'cadastrar fornecedor João Materiais'"
            }
        
        # Verificar se fornecedor já existe
        existing_supplier = Supplier.query.filter(Supplier.name.ilike(f'%{nome_fornecedor}%')).first()
        
        if existing_supplier:
            return {
                "status": "already_exists",
                "message": f"Fornecedor '{existing_supplier.name}' já está cadastrado no sistema.",
                "supplier": existing_supplier
            }
        
        # Extrair informações adicionais do comando
        email_match = re.search(r'email\s+([^\s,]+@[^\s,]+)', command)
        telefone_match = re.search(r'(?:telefone|fone|tel)\s+([^\s,]+)', command)
        categoria_match = re.search(r'(?:categoria|tipo|especialidade)\s+([^,]+)', command)
        
        email = email_match.group(1) if email_match else None
        telefone = telefone_match.group(1) if telefone_match else None
        categoria = categoria_match.group(1).strip() if categoria_match else None
        
        # Criar novo fornecedor
        novo_fornecedor = Supplier(
            name=nome_fornecedor,
            email=email,
            phone=telefone,
            product_category=categoria,
            notes=f"Fornecedor cadastrado via comando Lua: {command}"
        )
        
        db.session.add(novo_fornecedor)
        db.session.commit()
        
        contact_info = ""
        if email or telefone:
            contact_info = f" (Email: {email or 'N/A'}, Telefone: {telefone or 'N/A'})"
        
        category_info = f", Categoria: {categoria}" if categoria else ""
        
        return {
            "status": "success",
            "message": f"✅ Fornecedor {nome_fornecedor} cadastrado com sucesso{contact_info}{category_info}",
            "data": {
                "fornecedor": nome_fornecedor,
                "fornecedor_id": novo_fornecedor.id,
                "email": email,
                "telefone": telefone,
                "categoria": categoria
            }
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Erro ao cadastrar fornecedor: {str(e)}"
        }

def handle_supplier_search_command(command):
    """Processar comandos de busca de fornecedores"""
    try:
        # Extrair nome do fornecedor
        nome_fornecedor = extract_entity_name_from_command(command, "fornecedor")
        
        if not nome_fornecedor:
            return {
                "status": "error",
                "message": "Não foi possível identificar o nome do fornecedor. Tente: 'buscar fornecedor João'"
            }
        
        # Buscar fornecedor usando busca inteligente
        search_result = find_entity_by_name(Supplier, nome_fornecedor)
        
        if search_result["status"] == "success":
            fornecedor = search_result["entity"]
            contact_info = []
            if fornecedor.email:
                contact_info.append(f"Email: {fornecedor.email}")
            if fornecedor.phone:
                contact_info.append(f"Telefone: {fornecedor.phone}")
            if fornecedor.product_category:
                contact_info.append(f"Categoria: {fornecedor.product_category}")
            
            contact_str = f" ({', '.join(contact_info)})" if contact_info else ""
            
            return {
                "status": "success",
                "message": f"🏭 Fornecedor encontrado: {fornecedor.name}{contact_str}",
                "data": {
                    "fornecedor": fornecedor.to_dict()
                }
            }
        
        elif search_result["status"] == "multiple_matches":
            options_text = "\n".join([
                f"{i+1}. {opt['name']}"
                for i, opt in enumerate(search_result["options"])
            ])
            return {
                "status": "multiple_matches",
                "message": f"Múltiplos fornecedores encontrados para '{nome_fornecedor}':\n{options_text}",
                "options": search_result["options"]
            }
        
        else:
            return search_result
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao buscar fornecedor: {str(e)}"
        }

def handle_supplier_general_command(command):
    """Processar comandos gerais relacionados a fornecedores"""
    try:
        # Listar fornecedores
        if any(palavra in command for palavra in ["listar", "todos", "fornecedores"]):
            suppliers = Supplier.query.filter_by(active=True).limit(10).all()
            
            if not suppliers:
                return {
                    "status": "success",
                    "message": "Nenhum fornecedor cadastrado no sistema."
                }
            
            supplier_list = "\n".join([
                f"• {supplier.name}" + (f" - {supplier.product_category}" if supplier.product_category else "")
                for supplier in suppliers
            ])
            
            return {
                "status": "success",
                "message": f"🏭 Fornecedores cadastrados:\n{supplier_list}",
                "data": {
                    "total_suppliers": len(suppliers),
                    "suppliers": [s.to_dict() for s in suppliers]
                }
            }
        
        else:
            return {
                "status": "error",
                "message": "Comando de fornecedor não reconhecido. Tente: 'cadastrar fornecedor [nome]', 'buscar fornecedor [nome]', 'compra de [material] do fornecedor [nome]'"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao processar comando: {str(e)}"
        }

