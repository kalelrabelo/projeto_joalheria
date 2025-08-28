import os
from flask import Flask
from flask_cors import CORS
from src.models.user import db

# Blueprints (carrega só os que existirem)
def try_register(app, modpath, name):
    try:
        mod = __import__(modpath, fromlist=[name])
        app.register_blueprint(getattr(mod, name))
        print(f"[OK] Blueprint registrado: {name}")
    except Exception as e:
        print(f"[AVISO] Falha ao registrar {name} de {modpath}: {e}")

def create_app():
    app = Flask(__name__)
    CORS(app)
    # SQLite local
    # Use um caminho absoluto para o banco de dados
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'data', 'app.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # seed de admins
        from src.models.user import User
        seed_admins = [("rabelo","rabeloce"),("lucia","luciace"),("darvin","darvince")]
        for u, pwd in seed_admins:
            if not User.query.filter_by(username=u).first():
                User.create_admin(u, pwd)
                print(f"[OK] Admin criado: {u}")
    # rotas
    try_register(app, "src.routes.user", "user_bp")
    try_register(app, "src.routes.jewelry", "jewelry_bp")
    try_register(app, "src.routes.employees", "employees_bp")
    try_register(app, "src.routes.orders", "orders_bp")
    try_register(app, "src.routes.caixa", "caixa_bp")
    try_register(app, "src.routes.dashboard", "dashboard_bp")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)




from src.lua_core.lua_free_ai_engine import LuaFreeAIEngine
lua_free_ai = LuaFreeAIEngine()





from threading import Thread

@app.route("/start_stt_worker", methods=["POST"])
def start_stt_worker():
    MODEL_PATH = "/home/ubuntu/projeto_joalheria/backend/resources/vosk/pt/vosk-model-small-pt-0.3"
    try:
        from src.vosk_stt_worker import VoskSTTWorker
        worker = VoskSTTWorker(MODEL_PATH)
        # Inicia o worker em uma thread separada para não bloquear o servidor Flask
        Thread(target=worker.start_listening).start()
        return {"status": "Vosk STT Worker iniciado com sucesso!"}, 200
    except Exception as e:
        return {"status": f"Erro ao iniciar Vosk STT Worker: {e}"}, 500



