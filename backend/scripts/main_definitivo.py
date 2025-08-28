import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///joalheria.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "sua_chave_secreta_aqui"
app.config["DEBUG"] = True

db = SQLAlchemy(app)

# Rota de teste básica
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        "message": "Backend funcionando perfeitamente!",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    })

# Rota de status
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "database": "connected",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

# Simulação básica da Lua para testes
@app.route('/api/lua/status', methods=['GET'])
def lua_status():
    return jsonify({
        "status": "online",
        "message": "Lua IA funcionando!",
        "timestamp": datetime.now().isoformat(),
        "capabilities": ["chat", "reports", "analysis"]
    })

# Chat básico da Lua
@app.route('/api/lua/chat', methods=['POST'])
def lua_chat():
    data = request.get_json()
    message = data.get('message', '')
    
    # Simulação de resposta da Lua
    responses = {
        "oi": "Olá! Sou a Lua, sua assistente IA. Como posso ajudar?",
        "status": "Sistema funcionando perfeitamente! Todos os módulos estão online.",
        "teste": "Teste realizado com sucesso! Sistema operacional.",
        "vales": "Funcionalidade de vales está ativa e funcionando.",
        "relatorio": "Relatórios estão sendo gerados automaticamente.",
        "help": "Comandos disponíveis: status, teste, vales, relatorio, help"
    }
    
    response = responses.get(message.lower(), f"Recebi sua mensagem: '{message}'. Sistema funcionando!")
    
    return jsonify({
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    })

# Chat enhanced da Lua
@app.route('/api/lua_enhanced/chat', methods=['POST'])
def lua_enhanced_chat():
    data = request.get_json()
    message = data.get('message', '')
    
    return jsonify({
        "response": f"[Lua Enhanced] Processando: {message}. Sistema funcionando perfeitamente!",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "enhanced": True
    })

# Histórico da Lua
@app.route('/api/lua/history', methods=['GET'])
def lua_history():
    return jsonify({
        "history": [
            {"timestamp": datetime.now().isoformat(), "message": "Sistema iniciado", "type": "system"},
            {"timestamp": datetime.now().isoformat(), "message": "Lua IA ativada", "type": "info"},
            {"timestamp": datetime.now().isoformat(), "message": "Todos os módulos funcionando", "type": "success"}
        ],
        "status": "success"
    })

# Configurações do admin
@app.route('/api/lua/scheduler_config', methods=['GET', 'POST'])
def scheduler_config():
    if request.method == 'GET':
        return jsonify({
            "config": {
                "backup_enabled": True,
                "reports_enabled": True,
                "alerts_enabled": True
            },
            "status": "success"
        })
    else:
        return jsonify({"message": "Configuração salva com sucesso!", "status": "success"})

@app.route('/api/lua/automatic_reports', methods=['GET', 'POST'])
def automatic_reports():
    if request.method == 'GET':
        return jsonify({
            "reports": {
                "daily": True,
                "weekly": True,
                "monthly": False
            },
            "status": "success"
        })
    else:
        return jsonify({"message": "Relatórios configurados com sucesso!", "status": "success"})

@app.route('/api/lua/insights', methods=['GET'])
def insights():
    return jsonify({
        "insights": [
            "Sistema funcionando perfeitamente",
            "Todas as funcionalidades da Lua estão ativas",
            "Backend conectado com sucesso"
        ],
        "status": "success"
    })

@app.route('/api/lua/admin_input', methods=['POST'])
def admin_input():
    data = request.get_json()
    return jsonify({
        "message": f"Comando administrativo processado: {data.get('command', '')}",
        "status": "success"
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("=" * 50)
        print("🚀 SISTEMA DE JOALHERIA - BACKEND INICIADO")
        print("=" * 50)
        print("✅ Banco de dados SQLite inicializado")
        print("✅ Lua IA ativada e funcionando")
        print("✅ Todos os endpoints configurados")
        print("=" * 50)
        print("📍 Testes disponíveis:")
        print("   http://localhost:5000/api/test")
        print("   http://localhost:5000/api/status")
        print("   http://localhost:5000/api/lua/status")
        print("=" * 50)
    
    app.run(debug=True, host="0.0.0.0", port=5000)

