# backend/src/customer_commands.py

import re
from datetime import datetime
from src.models.user import db
from src.models.customer import Customer
from src.models.order import Order
from src.entity_search import extract_entity_name_from_command, find_entity_by_name

def handle_customer_command(command):
    """Processar comandos relacionados a clientes"""
    try:
        # Determinar tipo de comando
        if any(palavra in command for palavra in ["pedido", "encomenda", "venda"]):
            return handle_customer_order_command(command)
        elif any(palavra in command for palavra in ["cadastrar", "adicionar", "novo cliente"]):
            return handle_customer_registration_command(command)
        elif any(palavra in command for palavra in ["buscar", "procurar", "encontrar"]):
            return handle_customer_search_command(command)
        else:
            return handle_customer_general_command(command)
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao processar comando de cliente: {str(e)}"
        }

def handle_customer_order_command(command):
    """Processar comandos de pedidos de clientes"""
    try:
        # Extrair nome do cliente
        nome_cliente = extract_entity_name_from_command(command, "cliente")
        
        if not nome_cliente:
            return {
                "status": "error",
                "message": "Não foi possível identificar o nome do cliente. Tente: 'pedido para Maria Silva'"
            }
        
        # Buscar cliente usando busca inteligente
        search_result = find_entity_by_name(Customer, nome_cliente)
        
        if search_result["status"] == "error":
            # Se cliente não existe, sugerir cadastro
            return {
                "status": "customer_not_found",
                "message": f"Cliente '{nome_cliente}' não encontrado. Deseja cadastrar este cliente primeiro?",
                "suggested_name": nome_cliente
            }
        
        elif search_result["status"] == "multiple_matches":
            options_text = "\n".join([
                f"{i+1}. {opt['name']}"
                for i, opt in enumerate(search_result["options"])
            ])
            return {
                "status": "multiple_matches",
                "message": f"Múltiplos clientes encontrados para '{nome_cliente}'. Escolha uma opção:\n{options_text}",
                "options": search_result["options"]
            }
        
        cliente = search_result["entity"]
        
        # Extrair valor do pedido
        valor_match = re.search(r'(?:r\$|rs|valor)\s*(\d+(?:[.,]\d{2})?)', command)
        if not valor_match:
            valor_match = re.search(r'(\d+(?:[.,]\d{2})?)', command)
        
        valor = float(valor_match.group(1).replace(',', '.')) if valor_match else 0.0
        
        # Extrair descrição do produto/joia
        produto_match = re.search(r'(?:joia|anel|colar|brinco|pulseira|produto)\s+([^,]+)', command)
        produto = produto_match.group(1).strip() if produto_match else "Produto personalizado"
        
        return {
            "status": "success",
            "message": f"📝 Pedido registrado para {cliente.name}: {produto}, valor R${valor:.2f}",
            "data": {
                "cliente": cliente.name,
                "cliente_id": cliente.id,
                "produto": produto,
                "valor": valor
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao processar pedido: {str(e)}"
        }

def handle_customer_registration_command(command):
    """Processar comandos de cadastro de clientes"""
    try:
        # Extrair nome do cliente
        nome_cliente = extract_entity_name_from_command(command, "cliente")
        
        if not nome_cliente:
            return {
                "status": "error",
                "message": "Não foi possível identificar o nome do cliente. Tente: 'cadastrar cliente Maria Silva'"
            }
        
        # Verificar se cliente já existe
        existing_customer = Customer.query.filter(Customer.name.ilike(f'%{nome_cliente}%')).first()
        
        if existing_customer:
            return {
                "status": "already_exists",
                "message": f"Cliente '{existing_customer.name}' já está cadastrado no sistema.",
                "customer": existing_customer
            }
        
        # Extrair informações adicionais do comando
        email_match = re.search(r'email\s+([^\s,]+@[^\s,]+)', command)
        telefone_match = re.search(r'(?:telefone|fone|tel)\s+([^\s,]+)', command)
        
        email = email_match.group(1) if email_match else None
        telefone = telefone_match.group(1) if telefone_match else None
        
        # Criar novo cliente
        novo_cliente = Customer(
            name=nome_cliente,
            email=email,
            phone=telefone,
            notes=f"Cliente cadastrado via comando Lua: {command}"
        )
        
        db.session.add(novo_cliente)
        db.session.commit()
        
        contact_info = ""
        if email or telefone:
            contact_info = f" (Email: {email or 'N/A'}, Telefone: {telefone or 'N/A'})"
        
        return {
            "status": "success",
            "message": f"✅ Cliente {nome_cliente} cadastrado com sucesso{contact_info}",
            "data": {
                "cliente": nome_cliente,
                "cliente_id": novo_cliente.id,
                "email": email,
                "telefone": telefone
            }
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Erro ao cadastrar cliente: {str(e)}"
        }

def handle_customer_search_command(command):
    """Processar comandos de busca de clientes"""
    try:
        # Extrair nome do cliente
        nome_cliente = extract_entity_name_from_command(command, "cliente")
        
        if not nome_cliente:
            return {
                "status": "error",
                "message": "Não foi possível identificar o nome do cliente. Tente: 'buscar cliente Maria'"
            }
        
        # Buscar cliente usando busca inteligente
        search_result = find_entity_by_name(Customer, nome_cliente)
        
        if search_result["status"] == "success":
            cliente = search_result["entity"]
            contact_info = []
            if cliente.email:
                contact_info.append(f"Email: {cliente.email}")
            if cliente.phone:
                contact_info.append(f"Telefone: {cliente.phone}")
            
            contact_str = f" ({', '.join(contact_info)})" if contact_info else ""
            
            return {
                "status": "success",
                "message": f"👤 Cliente encontrado: {cliente.name}{contact_str}",
                "data": {
                    "cliente": cliente.to_dict()
                }
            }
        
        elif search_result["status"] == "multiple_matches":
            options_text = "\n".join([
                f"{i+1}. {opt['name']}"
                for i, opt in enumerate(search_result["options"])
            ])
            return {
                "status": "multiple_matches",
                "message": f"Múltiplos clientes encontrados para '{nome_cliente}':\n{options_text}",
                "options": search_result["options"]
            }
        
        else:
            return search_result
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao buscar cliente: {str(e)}"
        }

def handle_customer_general_command(command):
    """Processar comandos gerais relacionados a clientes"""
    try:
        # Listar clientes
        if any(palavra in command for palavra in ["listar", "todos", "clientes"]):
            customers = Customer.query.filter_by(active=True).limit(10).all()
            
            if not customers:
                return {
                    "status": "success",
                    "message": "Nenhum cliente cadastrado no sistema."
                }
            
            customer_list = "\n".join([
                f"• {customer.name}" + (f" - {customer.phone}" if customer.phone else "")
                for customer in customers
            ])
            
            return {
                "status": "success",
                "message": f"👥 Clientes cadastrados:\n{customer_list}",
                "data": {
                    "total_customers": len(customers),
                    "customers": [c.to_dict() for c in customers]
                }
            }
        
        else:
            return {
                "status": "error",
                "message": "Comando de cliente não reconhecido. Tente: 'cadastrar cliente [nome]', 'buscar cliente [nome]', 'pedido para [nome]'"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao processar comando: {str(e)}"
        }

