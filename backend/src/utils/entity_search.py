# backend/src/entity_search.py

from difflib import SequenceMatcher
import re

def find_entity_by_name(entity_class, search_term, threshold=0.6):
    """
    Busca entidade por nome com correspondência fuzzy e case-insensitive
    
    Args:
        entity_class: Classe do modelo (Employee, Customer, Supplier)
        search_term (str): Termo de busca (pode ser nome parcial)
        threshold (float): Limite mínimo de similaridade (0.0 a 1.0)
    
    Returns:
        dict: Resultado da busca com entidade encontrada ou lista de opções
    """
    try:
        # Limpar e normalizar o termo de busca
        search_term = search_term.strip().lower()
        
        if not search_term:
            return {
                "status": "error",
                "message": f"Nome da entidade não pode estar vazio."
            }
        
        # Buscar todas as entidades ativas
        try:
            entities = entity_class.query.filter_by(active=True).all()
        except:
            # Fallback caso o campo active não exista
            entities = entity_class.query.all()
        
        if not entities:
            entity_name = entity_class.__name__.lower()
            return {
                "status": "error",
                "message": f"Nenhum(a) {entity_name} ativo(a) encontrado(a) no sistema."
            }
        
        # Lista para armazenar correspondências
        matches = []
        
        for entity in entities:
            entity_name = entity.name.lower()
            
            # Verificar correspondência exata (case-insensitive)
            if search_term == entity_name:
                return {
                    "status": "success",
                    "entity": entity,
                    "match_type": "exact"
                }
            
            # Verificar se o termo está contido no nome
            if search_term in entity_name:
                matches.append({
                    "entity": entity,
                    "similarity": 1.0,
                    "match_type": "contains"
                })
                continue
            
            # Verificar se o nome está contido no termo
            if entity_name in search_term:
                matches.append({
                    "entity": entity,
                    "similarity": 0.9,
                    "match_type": "partial"
                })
                continue
            
            # Calcular similaridade usando SequenceMatcher
            similarity = SequenceMatcher(None, search_term, entity_name).ratio()
            
            if similarity >= threshold:
                matches.append({
                    "entity": entity,
                    "similarity": similarity,
                    "match_type": "fuzzy"
                })
            
            # Verificar similaridade por palavras individuais
            search_words = search_term.split()
            name_words = entity_name.split()
            
            word_matches = 0
            total_words = len(search_words)
            
            for search_word in search_words:
                for name_word in name_words:
                    if (search_word in name_word or 
                        name_word in search_word or 
                        SequenceMatcher(None, search_word, name_word).ratio() >= 0.8):
                        word_matches += 1
                        break
            
            if word_matches > 0:
                word_similarity = word_matches / total_words
                if word_similarity >= threshold:
                    matches.append({
                        "entity": entity,
                        "similarity": word_similarity,
                        "match_type": "word_match"
                    })
        
        # Remover duplicatas e ordenar por similaridade
        unique_matches = {}
        for match in matches:
            entity_id = match["entity"].id
            if entity_id not in unique_matches or match["similarity"] > unique_matches[entity_id]["similarity"]:
                unique_matches[entity_id] = match
        
        sorted_matches = sorted(unique_matches.values(), key=lambda x: x["similarity"], reverse=True)
        
        if not sorted_matches:
            entity_name = entity_class.__name__.lower()
            return {
                "status": "error",
                "message": f"{entity_class.__name__} '{search_term}' não encontrado(a). Verifique o nome e tente novamente.",
                "available_entities": [ent.name for ent in entities[:5]]
            }
        
        # Se há apenas uma correspondência com alta similaridade, retornar diretamente
        if len(sorted_matches) == 1 and sorted_matches[0]["similarity"] >= 0.8:
            return {
                "status": "success",
                "entity": sorted_matches[0]["entity"],
                "match_type": sorted_matches[0]["match_type"],
                "similarity": sorted_matches[0]["similarity"]
            }
        
        # Se há múltiplas correspondências, retornar opções
        if len(sorted_matches) > 1:
            entity_name = entity_class.__name__.lower()
            return {
                "status": "multiple_matches",
                "message": f"Múltiplos(as) {entity_name}s encontrados(as) para '{search_term}'. Escolha uma opção:",
                "options": [
                    {
                        "id": match["entity"].id,
                        "name": match["entity"].name,
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
            "entity": best_match["entity"],
            "match_type": best_match["match_type"],
            "similarity": best_match["similarity"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na busca: {str(e)}"
        }

def extract_entity_name_from_command(command, entity_type="funcionario"):
    """
    Extrai o nome da entidade de um comando em linguagem natural
    
    Args:
        command (str): Comando em linguagem natural
        entity_type (str): Tipo da entidade ("funcionario", "cliente", "fornecedor")
    
    Returns:
        str: Nome extraído do comando
    """
    try:
        # Palavras comuns a serem removidas baseadas no tipo de entidade
        base_stop_words = [
            'um', 'uma', 'o', 'a', 'do', 'da', 'no', 'na', 'para', 'de',
            'adiciona', 'criar', 'registra', 'registrar', 'buscar', 'procurar',
            'r$', 'rs', 'reais', 'real'
        ]
        
        entity_stop_words = {
            "funcionario": ['funcionário', 'funcionario', 'vale', 'viagem', 'hotel', 'hospedagem', 'horas', 'trabalho', 'folha', 'pagamento', 'salário', 'salario'],
            "cliente": ['cliente', 'customer', 'pedido', 'encomenda', 'venda', 'compra'],
            "fornecedor": ['fornecedor', 'supplier', 'compra', 'material', 'produto']
        }
        
        stop_words = base_stop_words + entity_stop_words.get(entity_type, [])
        
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
            return ' '.join(name_words[:3]).title()
        
        return ""
        
    except Exception as e:
        return ""

def search_entity_interactive(entity_class, search_term):
    """
    Busca interativa que retorna mensagem formatada para o chat
    
    Args:
        entity_class: Classe do modelo
        search_term (str): Termo de busca
    
    Returns:
        dict: Resultado formatado para resposta do chat
    """
    result = find_entity_by_name(entity_class, search_term)
    entity_name = entity_class.__name__.lower()
    
    if result["status"] == "success":
        entity = result["entity"]
        match_info = ""
        if "similarity" in result and result["similarity"] < 1.0:
            match_info = f" (similaridade: {result['similarity']:.0%})"
        
        return {
            "status": "success",
            "entity": entity,
            "message": f"{entity_class.__name__} encontrado(a): {entity.name}{match_info}"
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
        if "available_entities" in result:
            available = f"\n\n{entity_class.__name__}s disponíveis: {', '.join(result['available_entities'])}"
        
        return {
            "status": "error",
            "message": f"{result['message']}{available}"
        }

