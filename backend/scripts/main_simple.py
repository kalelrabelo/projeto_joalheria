import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados (usando SQLite para simplicidade)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///joalheria.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Configuração da SECRET_KEY
app.config["SECRET_KEY"] = "sua_chave_secreta_aqui"

# Desativar modo debug em produção
app.config["DEBUG"] = True

# Importar e registrar apenas as rotas que existem
try:
    from src.routes.jewelry import jewelry_bp
    app.register_blueprint(jewelry_bp, url_prefix="/api/jewelry")
    print("✅ Jewelry routes carregadas")
except ImportError as e:
    print(f"❌ Erro ao carregar jewelry routes: {e}")

try:
    from src.routes.caixa import caixa_bp
    app.register_blueprint(caixa_bp, url_prefix="/api/caixa")
    print("✅ Caixa routes carregadas")
except ImportError as e:
    print(f"❌ Erro ao carregar caixa routes: {e}")

try:
    from src.lua_module import lua_bp
    app.register_blueprint(lua_bp, url_prefix="/api/lua")
    print("✅ Lua module carregado")
except ImportError as e:
    print(f"❌ Erro ao carregar lua module: {e}")

try:
    from src.lua_module_enhanced import lua_enhanced_bp
    app.register_blueprint(lua_enhanced_bp, url_prefix="/api/lua_enhanced")
    print("✅ Lua enhanced module carregado")
except ImportError as e:
    print(f"❌ Erro ao carregar lua enhanced module: {e}")

# Rota de teste
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "Backend funcionando!", "timestamp": datetime.now().isoformat()})

# Rota de status
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados inicializado")
    
    print("🚀 Iniciando servidor Flask...")
    print("📍 Acesse: http://localhost:5000/api/test")
    print("📍 Status: http://localhost:5000/api/status")
    
    app.run(debug=True, host="0.0.0.0", port=5000)

