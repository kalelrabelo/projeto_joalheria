from flask import Blueprint, request, jsonify, send_file
from src.models.user import db
from src.models.pattern import Pattern
from src.models.pattern_image import PatternImage
from werkzeug.utils import secure_filename
import os
import csv
import shutil
from datetime import datetime

patterns_enhanced_bp = Blueprint("patterns_enhanced", __name__)

# ===== ROTAS PARA PADRÕES =====

@patterns_enhanced_bp.route("/patterns", methods=["GET"])
def get_patterns():
    try:
        # Parâmetros de filtro
        tipo = request.args.get('tipo')
        colecao = request.args.get('colecao')
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        include_images = request.args.get('include_images', 'false').lower() == 'true'
        
        query = Pattern.query
        
        # Aplicar filtros
        if tipo:
            query = query.filter(Pattern.tipo == tipo)
        if colecao:
            query = query.filter(Pattern.colecao == colecao)
        if search:
            query = query.filter(
                db.or_(
                    Pattern.nome.contains(search),
                    Pattern.noticia.contains(search),
                    Pattern.colecao.contains(search)
                )
            )
        
        # Paginação
        patterns = query.order_by(Pattern.idpa.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'patterns': [pattern.to_dict(include_images=include_images) for pattern in patterns.items],
            'total': patterns.total,
            'pages': patterns.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': patterns.has_next,
            'has_prev': patterns.has_prev
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@patterns_enhanced_bp.route("/patterns/<int:id>", methods=["GET"])
def get_pattern(id):
    try:
        include_images = request.args.get('include_images', 'true').lower() == 'true'
        pattern = Pattern.query.get_or_404(id)
        return jsonify(pattern.to_dict(include_images=include_images)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== ROTAS PARA IMAGENS DE PADRÕES =====

@patterns_enhanced_bp.route("/patterns/<int:pattern_id>/images", methods=["POST"])
def upload_pattern_image(pattern_id):
    try:
        pattern = Pattern.query.get_or_404(pattern_id)
        
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400
        
        # Verificar tipo de arquivo
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        file_extension = os.path.splitext(secure_filename(file.filename))[1].lower()
        
        if file_extension not in allowed_extensions:
            return jsonify({"error": "Tipo de arquivo não permitido"}), 400
        
        # Ler dados do arquivo
        file_data = file.read()
        
        # Criar imagem
        pattern_image = PatternImage.create_from_file(
            pattern_id=pattern_id,
            file_data=file_data,
            filename=secure_filename(file.filename),
            original_filename=file.filename
        )
        
        if isinstance(pattern_image, dict) and "error" in pattern_image:
            return jsonify(pattern_image), 500
        
        # Definir como primária se for a primeira imagem
        if pattern.get_image_count() == 0:
            pattern_image.is_primary = True
        
        db.session.add(pattern_image)
        db.session.commit()
        
        return jsonify({
            "image": pattern_image.to_dict(),
            "message": "Imagem enviada com sucesso"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@patterns_enhanced_bp.route("/patterns/images/<filename>", methods=["GET"])
def serve_pattern_image(filename):
    try:
        image = PatternImage.query.filter_by(filename=filename).first_or_404()
        return send_file(image.file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@patterns_enhanced_bp.route("/patterns/<int:pattern_id>/images/<int:image_id>/primary", methods=["POST"])
def set_primary_image(pattern_id, image_id):
    try:
        pattern = Pattern.query.get_or_404(pattern_id)
        image = PatternImage.query.filter_by(id=image_id, pattern_id=pattern_id).first_or_404()
        
        result = image.set_as_primary()
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 500
        
        return jsonify({"message": "Imagem definida como primária"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@patterns_enhanced_bp.route("/patterns/<int:pattern_id>/images/<int:image_id>", methods=["DELETE"])
def delete_pattern_image(pattern_id, image_id):
    try:
        pattern = Pattern.query.get_or_404(pattern_id)
        image = PatternImage.query.filter_by(id=image_id, pattern_id=pattern_id).first_or_404()
        
        # Deletar arquivo físico
        image.delete_file()
        
        # Se era a imagem primária, definir outra como primária
        was_primary = image.is_primary
        
        db.session.delete(image)
        
        if was_primary and pattern.images:
            # Definir a primeira imagem restante como primária
            remaining_images = [img for img in pattern.images if img.id != image_id]
            if remaining_images:
                remaining_images[0].is_primary = True
        
        db.session.commit()
        
        return jsonify({"message": "Imagem excluída com sucesso"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ===== ROTAS PARA IMPORTAÇÃO DE DADOS =====

@patterns_enhanced_bp.route("/patterns/import", methods=["POST"])
def import_patterns():
    """Importa padrões do sistema antigo"""
    try:
        # Verificar se há dados para importar
        import_data = request.get_json()
        
        if not import_data or 'patterns' not in import_data:
            return jsonify({"error": "Dados de importação não fornecidos"}), 400
        
        imported_count = 0
        errors = []
        
        for pattern_data in import_data['patterns']:
            try:
                # Verificar se já existe
                existing = Pattern.query.filter_by(idpa=pattern_data['idpa']).first()
                if existing:
                    continue
                
                # Criar novo padrão
                new_pattern = Pattern(
                    idpa=pattern_data['idpa'],
                    foto=pattern_data.get('foto'),
                    tipo=pattern_data.get('tipo'),
                    code=pattern_data.get('code'),
                    colecao=pattern_data.get('colecao'),
                    nome=pattern_data.get('nome'),
                    tempo=pattern_data.get('tempo', 0.0),
                    noticia=pattern_data.get('noticia'),
                    comp=pattern_data.get('comp', 0.0),
                    lag=pattern_data.get('lag', 0.0),
                    alt=pattern_data.get('alt', 0.0)
                )
                
                db.session.add(new_pattern)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Erro ao importar padrão {pattern_data.get('idpa', 'N/A')}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            "message": f"{imported_count} padrões importados com sucesso",
            "imported_count": imported_count,
            "errors": errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@patterns_enhanced_bp.route("/patterns/import-images", methods=["POST"])
def import_pattern_images():
    """Importa imagens dos padrões do sistema antigo"""
    try:
        source_dir = request.json.get('source_directory')
        if not source_dir or not os.path.exists(source_dir):
            return jsonify({"error": "Diretório de origem não encontrado"}), 400
        
        imported_count = 0
        errors = []
        
        # Listar arquivos de imagem no diretório
        for filename in os.listdir(source_dir):
            if filename.startswith('padroes_') and filename.endswith(('.bmp', '.jpg', '.jpeg', '.png')):
                try:
                    # Extrair ID do padrão do nome do arquivo
                    # Formato: padroes_XXX_foto.bmp
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        idpa = int(parts[1])
                        
                        # Encontrar padrão correspondente
                        pattern = Pattern.query.filter_by(idpa=idpa).first()
                        if not pattern:
                            continue
                        
                        # Verificar se já tem imagem
                        if pattern.images:
                            continue
                        
                        # Ler arquivo
                        file_path = os.path.join(source_dir, filename)
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                        
                        # Criar imagem
                        pattern_image = PatternImage.create_from_file(
                            pattern_id=pattern.id,
                            file_data=file_data,
                            filename=filename,
                            original_filename=filename
                        )
                        
                        if isinstance(pattern_image, dict) and "error" in pattern_image:
                            errors.append(f"Erro ao importar {filename}: {pattern_image['error']}")
                            continue
                        
                        pattern_image.is_primary = True
                        db.session.add(pattern_image)
                        imported_count += 1
                        
                except Exception as e:
                    errors.append(f"Erro ao processar {filename}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            "message": f"{imported_count} imagens importadas com sucesso",
            "imported_count": imported_count,
            "errors": errors
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ===== ROTAS AUXILIARES =====

@patterns_enhanced_bp.route("/patterns/tipos", methods=["GET"])
def get_pattern_types():
    """Retorna os tipos de padrões disponíveis"""
    return jsonify(Pattern.get_tipos()), 200

@patterns_enhanced_bp.route("/patterns/colecoes", methods=["GET"])
def get_pattern_collections():
    """Retorna as coleções disponíveis"""
    return jsonify(Pattern.get_colecoes()), 200

@patterns_enhanced_bp.route("/patterns/stats", methods=["GET"])
def get_pattern_stats():
    """Retorna estatísticas dos padrões"""
    try:
        total_patterns = Pattern.query.count()
        
        # Contagem por tipo
        tipos_count = db.session.query(
            Pattern.tipo, 
            db.func.count(Pattern.id).label('count')
        ).group_by(Pattern.tipo).all()
        
        # Contagem por coleção
        colecoes_count = db.session.query(
            Pattern.colecao, 
            db.func.count(Pattern.id).label('count')
        ).filter(Pattern.colecao.isnot(None)).group_by(Pattern.colecao).all()
        
        # Padrões com imagens
        patterns_with_images = db.session.query(Pattern).join(PatternImage).distinct().count()
        
        return jsonify({
            "total_patterns": total_patterns,
            "patterns_with_images": patterns_with_images,
            "patterns_without_images": total_patterns - patterns_with_images,
            "by_type": [{"tipo": tipo, "count": count} for tipo, count in tipos_count],
            "by_collection": [{"colecao": colecao, "count": count} for colecao, count in colecoes_count]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

