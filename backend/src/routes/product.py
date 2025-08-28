
from src.models.jewelry import Jewelry

product_bp = Blueprint("product", __name__)

@product_bp.route("/product", methods=["GET"])
def get_product():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search", "")
        escondido = request.args.get("escondido", type=bool)
        webexport = request.args.get("webexport", type=bool)
        
        query = Jewelry.query
        
        if search:
            query = query.filter(
                (Jewelry.descricao.contains(search)) |
                (Jewelry.noticia.contains(search))
            )
        
        if escondido is not None:
            query = query.filter(Jewelry.escondido == escondido)
            
        if webexport is not None:
            query = query.filter(Jewelry.webexport == webexport)
        
        order_by = request.args.get("order_by", "idj")
        order_dir = request.args.get("order_dir", "asc")
        
        if hasattr(Jewelry, order_by):
            column = getattr(Jewelry, order_by)
            if order_dir == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        product_list = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            "product": product_list,
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

@product_bp.route("/product/<int:product_id>", methods=["GET"])
def get_product_by_id(product_id):
    try:
        product = Jewelry.query.get_or_404(product_id)
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_bp.route("/product", methods=["POST"])
def create_product():
    try:
        data = request.get_json()
        
        product = Jewelry(
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
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify(product.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@product_bp.route("/product/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        product = Jewelry.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({"message": "Produto eliminado com sucesso"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@product_bp.route("/product/stats", methods=["GET"])
def get_product_stats():
    try:
        total = Jewelry.query.count()
        visiveis = Jewelry.query.filter(Jewelry.escondido == False).count()
        web_export = Jewelry.query.filter(Jewelry.webexport == True).count()
        
        avg_price = db.session.query(db.func.avg(Jewelry.preco2)).scalar() or 0
        
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





