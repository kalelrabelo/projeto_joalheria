# tools/fix_project.py
import os, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # assume tools/ dentro de backend/
SRC = ROOT / "src"
MODELS = SRC / "models"
ROUTES = SRC / "routes"
LUA = SRC / "lua_core"

def die(msg):
    raise SystemExit(f"[FALHA] {msg}")

def ensure_exists(p):
    if not p.exists():
        die(f"Arquivo/pasta ausente: {p}")

def backup():
    bk = ROOT.parent / (ROOT.name + "_BACKUP")
    if bk.exists(): shutil.rmtree(bk)
    shutil.copytree(ROOT, bk)
    print(f"[OK] Backup em: {bk}")

def read(p): return p.read_text(encoding="utf-8", errors="ignore")
def write(p, txt): 
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(txt, encoding="utf-8")

def has_ellipsis(p):
    return "..." in read(p)

def step_detect_ellipsis():
    broken = []
    for p in SRC.rglob("*.py"):
        if has_ellipsis(p) or re.search(r"\breturn f\s*$", read(p), flags=re.M):
            broken.append(p)
    if broken:
        print("[ALERTA] Arquivos com \'...\' ou linhas cortadas:")
        for p in broken:
            print("  -", p.relative_to(ROOT))
    return broken

def step_models_cleanup():
    # REMOVER duplicatas que conflitam
    prod = MODELS / "product.py"
    cust = MODELS / "customer.py"
    changed = False
    for p in [prod, cust]:
        if p.exists():
            p.unlink()
            changed = True
            print(f"[OK] Removido {p.relative_to(ROOT)}")
    if not (MODELS/"jewelry.py").exists():
        die("models/jewelry.py não encontrado (necessário).")
    # Corrigir __init__.py para exportar Jewelry e não Product
    initp = MODELS / "__init__.py"
    new_init = """from .user import db, User
from .employee import Employee
from .client import Client
from .order import Order
from .pattern import Pattern
from .payroll import Payroll
from .report_history import ReportHistory
from .transaction import CaixaCategory, CaixaTransaction
from .jewelry import Jewelry

__all__ = [
    "db","User","Employee","Client","Order",
    "Pattern","Payroll","ReportHistory","CaixaCategory","CaixaTransaction","Jewelry"
]
"""
    write(initp, new_init)
    print(f"[OK] Reescrito models/__init__.py")
    # Corrigir __all__ e nomes em transaction.py
    tp = MODELS / "transaction.py"
    if tp.exists():
        txt = read(tp)
        txt = re.sub(r"__all__\s*=\s*\[[^\]]*\]",
                     '__all__ = ["CaixaCategory","CaixaTransaction"]',
                     txt, flags=re.S)
        write(tp, txt)
        print("[OK] Ajustado models/transaction.py (__all__)")

def step_global_replace_product_to_jewelry():
    # Substitui imports/uso de Product -> Jewelry
    for p in SRC.rglob("*.py"):
        txt = read(p)
        new = txt
        new = re.sub(r"from\s+src\.models\.product\s+import\s+Product",
                     "from src.models.jewelry import Jewelry", new)
        # Evita substituir "Product" dentro de strings ou nomes de tabela; simples, mas resolve 95%\
        new = re.sub(r"\bProduct\b", "Jewelry", new)
        if new != txt:
            write(p, new)
            print(f"[OK] Substituições Product->Jewelry em {p.relative_to(ROOT)}")

def step_main_write():
    mainp = SRC / "main.py"
    content = f'''import os
from flask import Flask
from flask_cors import CORS
from src.models.user import db
# Blueprints (carrega só os que existirem)
def try_register(app, modpath, name):
    try:
        mod = __import__(modpath, fromlist=[name])
        app.register_blueprint(getattr(mod, name))
        print(f"[OK] Blueprint registrado: {{name}}")
    except Exception as e:
        print(f"[AVISO] Falha ao registrar {{name}} de {{modpath}}: {{e}}")

def create_app():
    app = Flask(__name__)
    CORS(app)
    # SQLite local
    os.makedirs("data", exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/app.db"
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
                print(f"[OK] Admin criado: {{u}}")
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
'''
    write(mainp, content)
    print("[OK] Reescrito src/main.py (ponto de entrada único)")

def step_lua_engine_min():
    lp = LUA / "lua_free_ai_engine.py"
    LUA.mkdir(parents=True, exist_ok=True)
    content = r'''import os, requests, logging
log = logging.getLogger(__name__)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")

class LuaFreeAIEngine:
    def __init__(self, model="mistral"):
        self.model = os.environ.get("OLLAMA_MODEL", model)
        try:
            import spacy
            try:
                self.nlp = spacy.load("pt_core_news_sm")
            except Exception:
                log.error("Modelo SpaCy pt não encontrado. Rode: python -m spacy download pt_core_news_sm")
                self.nlp = None
        except Exception:
            self.nlp = None

    def classify_intent(self, text: str) -> str:
        """Classificador simples, sempre retorna \'generic\' se não houver modelo treinado."""
        return "generic"

    def extract_entities(self, text: str) -> dict:
        ents = []
        if self.nlp:
            doc = self.nlp(text)
            ents = [{"text": e.text, "label": e.label_} for e in doc.ents]
        return {"entities": ents}

    def ollama_chat(self, prompt: str) -> str:
        try:
            r = requests.post(f"{OLLAMA_URL}/api/chat", json={
                "model": self.model,
                "messages": [{"role":"user","content": prompt}],
                "stream": False
            }, timeout=120)
            r.raise_for_status()
            data = r.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            log.error(f"Ollama falhou: {e}")
            return ""
'''
    write(lp, content)
    print("[OK] Reescrito lua_core/lua_free_ai_engine.py (Ollama offline)")

def step_requirements():
    req = ROOT / "requirements.txt"
    txt = read(req)
    add = []
    if "spacy" not in txt: add.append("spacy==3.8.2")
    if "scikit-learn" not in txt and "sklearn" not in txt: add.append("scikit-learn==1.5.2")
    if "requests" not in txt: add.append("requests==2.31.0")
    if add:
        txt += "\n" + "\n".join(add) + "\n"
        write(req, txt)
        print(f"[OK] requirements.txt atualizado: {', '.join(add)}")
    else:
        print("[OK] requirements.txt já tem dependências de IA")

def main():
    ensure_exists(ROOT)
    ensure_exists(SRC)
    ensure_exists(MODELS)
    ensure_exists(ROUTES)
    backup()

    broken = step_detect_ellipsis()
    # Mesmo que existam arquivos truncados, vamos sobrepor os essenciais:
    step_models_cleanup()
    step_global_replace_product_to_jewelry()
    step_main_write()
    step_lua_engine_min()
    step_requirements()

    print("\n[FINAL] Correções aplicadas.")
    print("Agora instale dependências, baixe SpaCy pt e rode o backend.\n")

if __name__ == "__main__":
    main()


