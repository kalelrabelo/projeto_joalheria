
from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.jewelry import Jewelry
from src.models.pattern import Pattern
# from src.main import cache # Removido para evitar importação circular

jewelry_bp = Blueprint("jewelry", __name__)

@jewelry_bp.route("/jewelry", methods=["GET"])
# @cache.cached(query_string=True) # Removido temporariamente para evitar importação circular
def get_jewelry():
    """Listar todas as joias com filtros opcionais"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search", "")
        escondido = request.args.get("escondido", type=bool)
        webexport = request.args.get("webexport", type=bool)
        
        query = Jewelry.query
        
        # Filtros
        if search:
            query = query.filter(
                (Jewelry.descricao.contains(search)) |
                (Jewelry.noticia.contains(search))
            )
        
        if escondido is not None:
            query = query.filter(Jewelry.escondido == escondido)
            
        if webexport is not None:
            query = query.filter(Jewelry.webexport == webexport)
        
        # Ordenação
        order_by = request.args.get("order_by", "idj")
        order_dir = request.args.get("order_dir", "asc")
        
        if hasattr(Jewelry, order_by):
            column = getattr(Jewelry, order_by)
            if order_dir == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        
        # Paginação
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        jewelry_list = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            "jewelry": jewelry_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@jewelry_bp.route("/jewelry/<int:jewelry_id>", methods=["GET"])
def get_jewelry_by_id(jewelry_id):
    """Obter uma joia específica"""
    try:
        jewelry = Jewelry.query.get_or_404(jewelry_id)
        return jsonify(jewelry.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@jewelry_bp.route("/jewelry", methods=["POST"])
def create_jewelry():
    """Criar uma nova joia"""
    try:
        data = request.get_json()
        
        jewelry = Jewelry(
            idj=data.get("idj"),
            idjimp=data.get("idjimp"),
            idpa=data.get("idpa"),
            foto=data.get("foto"),
            noticia=data.get("noticia"),
            descricao=data.get("descricao"),
            escondido=data.get("escondido", False),
            precomat=data.get("precomat", 0.0),
            precoped=data.get("precoped", 0.0),
            precotem=data.get("precotem", 0.0),
            preco0=data.get("preco0", 0.0),
            preco1=data.get("preco1", 0.0),
            preco2=data.get("preco2", 0.0),
            lucro1=data.get("lucro1", 1.0),
            lucro2=data.get("lucro2", 1.2),
            qmin=data.get("qmin", 0.0),
            precoweb=data.get("precoweb"),
            webexport=data.get("webexport", False)
        )
        
        db.session.add(jewelry)
        db.session.commit()
        
        # cache.clear() # Removido temporariamente para evitar importação circular
        
        return jsonify(jewelry.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@jewelry_bp.route("/jewelry/<int:jewelry_id>", methods=["DELETE"])
def delete_jewelry(jewelry_id):
    """Eliminar uma joia"""
    try:
        jewelry = Jewelry.query.get_or_404(jewelry_id)
        db.session.delete(jewelry)
        db.session.commit()
        
        # cache.clear() # Removido temporariamente para evitar importação circular
        
        return jsonify({"message": "Joia eliminada com sucesso"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@jewelry_bp.route("/jewelry/stats", methods=["GET"])
# @cache.cached() # Removido temporariamente para evitar importação circular
def get_jewelry_stats():
    """Obter estatísticas das joias"""
    try:
        total = Jewelry.query.count()
        visiveis = Jewelry.query.filter(Jewelry.escondido == False).count()
        web_export = Jewelry.query.filter(Jewelry.webexport == True).count()
        
        # Preço médio
        avg_price = db.session.query(db.func.avg(Jewelry.preco2)).scalar() or 0
        
        # Joias por tipo (baseado no padrão)
        tipos_query = db.session.query(
            Pattern.tipo, 
            db.func.count(Jewelry.id)
        ).join(Jewelry, Pattern.id == Jewelry.idpa).group_by(Pattern.tipo).all()
        
        tipos = [{"tipo": tipo, "count": count} for tipo, count in tipos_query]
        
        return jsonify({
            "total": total,
            "visiveis": visiveis,
            "web_export": web_export,
            "preco_medio": round(avg_price, 2),
            "tipos": tipos
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500





