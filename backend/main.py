import os
import sys
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, send_file
from flask_cors import CORS

# Importar db primeiro
from src.models.user import db

# Importar modelos
from src.models.user import User
from src.models.jewelry import Jewelry
from src.models.material import Material
from src.models.pattern import Pattern
from src.models.pattern_image import PatternImage

from src.models.employee import Employee
from src.models.vale import Vale
from src.models.payment import Payment
from src.models.caixa import CaixaCategory, CaixaTransaction
from src.models.payroll import Payroll
from src.models.order import Order
from src.models.inventory import Inventory
from src.models.cost import Cost, Profit
from src.models.nota import Nota
from src.models.imposto import Imposto
from src.models.financial import FinancialTransaction, ProductionReport, AdvancedOrder, DiscountTable, CostCalculation

# Importar blueprints
from src.routes.user import user_bp
from src.routes.jewelry import jewelry_bp
from src.routes.materials import materials_bp
from src.routes.patterns import patterns_bp
from src.routes.patterns_enhanced import patterns_enhanced_bp

from src.routes.dashboard import dashboard_bp
from src.routes.employees import employees_bp
from src.routes.vales import vales_bp
from src.routes.payments import payments_bp
from src.routes.payroll import payroll_bp
from src.routes.caixa import caixa_bp
from src.routes.orders import orders_bp
from src.routes.inventory import inventory_bp
from src.routes.costs import costs_bp
from src.routes.notas import notas_bp
from src.routes.financial import financial_bp
from src.lua_core.lua_module import lua_bp
from src.lua_core.lua_module_enhanced import lua_enhanced_bp
from src.lua_core.lua_super_intelligent import lua_super_bp
from src.lua_core.lua_free_intelligent import lua_free_bp


app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app)

# Configuração da base de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(jewelry_bp, url_prefix="/api")
app.register_blueprint(materials_bp, url_prefix="/api")
app.register_blueprint(patterns_bp, url_prefix="/api")
app.register_blueprint(patterns_enhanced_bp, url_prefix="/api")

app.register_blueprint(dashboard_bp, url_prefix="/api")
app.register_blueprint(employees_bp, url_prefix="/api")
app.register_blueprint(vales_bp, url_prefix="/api")
app.register_blueprint(payments_bp, url_prefix="/api")
app.register_blueprint(payroll_bp, url_prefix="/api")
app.register_blueprint(caixa_bp, url_prefix="/api")
app.register_blueprint(orders_bp, url_prefix="/api")
app.register_blueprint(inventory_bp, url_prefix="/api")
app.register_blueprint(costs_bp, url_prefix="/api")
app.register_blueprint(notas_bp, url_prefix="/api")
app.register_blueprint(financial_bp, url_prefix="/api")
app.register_blueprint(lua_bp, url_prefix="/api")
app.register_blueprint(lua_enhanced_bp, url_prefix="/api")
app.register_blueprint(lua_super_bp, url_prefix="/api")
app.register_blueprint(lua_free_bp, url_prefix="/api")


# Rota para servir o frontend React
@app.route('/')
def serve_frontend():
    return send_file(os.path.join(app.static_folder, 'index.html'))

@app.route('/<path:path>')
def serve_static_files(path):
    # Se o arquivo existe no diretório static, serve ele
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Caso contrário, serve o index.html (para roteamento do React)
    else:
        return send_file(os.path.join(app.static_folder, 'index.html'))

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



