# backend/src/employee_search.py

from src.models.employee import Employee
from difflib import SequenceMatcher
import re

def find_employee_by_name(search_term, threshold=0.7):
    """
    Busca funcionário por nome com correspondência fuzzy e case-insensitive
    
    Args:
        search_term (str): Termo de busca (pode ser nome parcial)
        threshold (float): Limite mínimo de similaridade (0.0 a 1.0)
    
    Returns:
        dict: Resultado da busca com funcionário encontrado ou lista de opções
    """
    try:
        # Limpar e normalizar o termo de busca
        search_term = search_term.strip().lower()
        
        if not search_term:
            return {
                "status": "error",
                "message": "Nome do funcionário não pode estar vazio."
            }
        
        # Buscar todos os funcionários ativos
        try:
            employees = Employee.query.filter_by(active=True).all()
        except:
            # Fallback caso o campo active não exista
            employees = Employee.query.all()
        
        if not employees:
            return {
                "status": "error",
                "message": "Nenhum funcionário ativo encontrado no sistema."
            }
        
        # Lista para armazenar correspondências
        matches = []
        
        for employee in employees:
            employee_name = employee.name.lower()
            
            # Verificar correspondência exata (case-insensitive)
            if search_term == employee_name:
                return {
                    "status": "success",
                    "employee": employee,
                    "match_type": "exact"
                }
            
            # Verificar se o termo de busca é uma parte do nome completo do funcionário
            if search_term in employee_name.split():
                matches.append({
                    "employee": employee,
                    "similarity": 0.95, # Alta similaridade para correspondência de palavra
                    "match_type": "partial_word"
                })
                continue

            # Verificar se o nome completo do funcionário contém o termo de busca
            if search_term in employee_name:
                matches.append({
                    "employee": employee,
                    "similarity": 0.9, # Similaridade para correspondência de substring
                    "match_type": "contains"
                })
                continue
            
            # Calcular similaridade usando SequenceMatcher
            similarity = SequenceMatcher(None, search_term, employee_name).ratio()
            
            if similarity >= threshold:
                matches.append({
                    "employee": employee,
                    "similarity": similarity,
                    "match_type": "fuzzy"
                })
            
            # Verificar similaridade por palavras individuais (para nomes compostos)
            search_words = search_term.split()
            name_words = employee_name.split()
            
            word_matches = 0
            total_words = len(search_words)
            
            for search_word in search_words:
                for name_word in name_words:
                    if (search_word == name_word or 
                        SequenceMatcher(None, search_word, name_word).ratio() >= 0.9):
                        word_matches += 1
                        break
            
            if word_matches > 0:
                word_similarity = word_matches / total_words
                if word_similarity >= threshold:
                    matches.append({
                        "employee": employee,
                        "similarity": word_similarity,
                        "match_type": "word_match"
                    })
        
        # Remover duplicatas e ordenar por similaridade
        unique_matches = {}
        for match in matches:
            emp_id = match["employee"].id
            if emp_id not in unique_matches or match["similarity"] > unique_matches[emp_id]["similarity"]:
                unique_matches[emp_id] = match
        
        sorted_matches = sorted(unique_matches.values(), key=lambda x: x["similarity"], reverse=True)
        
        if not sorted_matches:
            return {
                "status": "error",
                "message": f"Funcionário '{search_term}' não encontrado. Verifique o nome e tente novamente.",
                "available_employees": [emp.name for emp in employees[:5]]
            }
        
        # Se há apenas uma correspondência com alta similaridade, retornar diretamente
        if len(sorted_matches) == 1 and sorted_matches[0]["similarity"] >= 0.85: # Ajustado para 0.85
            return {
                "status": "success",
                "employee": sorted_matches[0]["employee"],
                "match_type": sorted_matches[0]["match_type"],
                "similarity": sorted_matches[0]["similarity"]
            }
        
        # Se há múltiplas correspondências ou baixa similaridade, retornar opções
        if len(sorted_matches) > 1 or (len(sorted_matches) == 1 and sorted_matches[0]["similarity"] < 0.85): # Ajustado para 0.85
            return {
                "status": "multiple_matches",
                "message": f"Múltiplos funcionários encontrados para '{search_term}'. Escolha uma opção:",
                "options": [
                    {
                        "id": match["employee"].id,
                        "name": match["employee"].name,
                        "similarity": match["similarity"],
                        "match_type": match["match_type"]
                    }
                    for match in sorted_matches[:5]  # Limitar a 5 opções
                ]
            }
        
        # Retornar a melhor correspondência
        best_match = sorted_matches[0]
        return {
            "status": "success",
            "employee": best_match["employee"],
            "match_type": best_match["match_type"],
            "similarity": best_match["similarity"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na busca de funcionário: {str(e)}"
        }

def extract_employee_name_from_command(command):
    """
    Extrai o nome do funcionário de um comando em linguagem natural
    
    Args:
        command (str): Comando em linguagem natural
    
    Returns:
        str: Nome extraído do comando
    """
    try:
        # Palavras comuns a serem removidas
        stop_words = [
            'vale', 'para', 'de', 'adiciona', 'criar', 'registra', 'registrar',
            'r$', 'rs', 'reais', 'real', 'funcionário', 'funcionario',
            'um', 'uma', 'o', 'a', 'do', 'da', 'no', 'na',
            'viagem', 'hotel', 'hospedagem', 'horas', 'trabalho',
            'folha', 'pagamento', 'salário', 'salario',
            'imprime', 'imprimir', 'mostra', 'lista', 'gera', 'gerar', 'consulta', 'calcula'
        ]
        
        # Remover valores monetários e números
        command_clean = re.sub(r'r\$\s*\d+(?:[.,]\d{2})?', '', command, flags=re.IGNORECASE)
        command_clean = re.sub(r'\d+(?:[.,]\d{2})?\s*(?:r\$|rs|reais?)', '', command_clean, flags=re.IGNORECASE)
        command_clean = re.sub(r'\d+(?:[.,]\d{2})?', '', command_clean)
        
        # Remover datas
        command_clean = re.sub(r'\d{2}/\d{2}(?:/\d{4})?', '', command_clean)
        
        # Dividir em palavras e filtrar
        words = command_clean.split()
        name_words = []
        
        for word in words:
            # Limpar caracteres especiais
            clean_word = re.sub(r'[^\w]', '', word)
            
            # Verificar se não é uma stop word e não é um número
            if (clean_word.lower() not in stop_words and 
                clean_word and 
                not clean_word.isdigit() and
                len(clean_word) > 1):
                name_words.append(clean_word)
        
        # Retornar as primeiras 2-3 palavras como nome
        if name_words:
            return ' '.join(name_words[:3])
        
        return ""
        
    except Exception as e:
        return ""

def search_employee_interactive(search_term):
    """
    Busca interativa que retorna mensagem formatada para o chat
    
    Args:
        search_term (str): Termo de busca
    
    Returns:
        dict: Resultado formatado para resposta do chat
    """
    result = find_employee_by_name(search_term)
    
    if result["status"] == "success":
        employee = result["employee"]
        match_info = ""
        if "similarity" in result and result["similarity"] < 1.0:
            match_info = f" (similaridade: {result['similarity']:.0%})"
        
        return {
            "status": "success",
            "employee": employee,
            "message": f"Funcionário encontrado: {employee.name}{match_info}"
        }
    
    elif result["status"] == "multiple_matches":
        options_text = "\n".join([
            f"{i+1}. {opt['name']} (similaridade: {opt['similarity']:.0%})"
            for i, opt in enumerate(result["options"])
        ])
        
        return {
            "status": "multiple_matches",
            "options": result["options"],
            "message": f"{result['message']}\n{options_text}\n\nResponda com o número da opção desejada."
        }
    
    else:
        available = ""
        if "available_employees" in result:
            available = f"\n\nFuncionários disponíveis: {', '.join(result['available_employees'])}"
        
        return {
            "status": "error",
            "message": f"{result['message']}{available}"
        }

