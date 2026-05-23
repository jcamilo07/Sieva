"""
app.py - Punto de entrada de la aplicacion Flask.
"""

from flask import Flask
from config import SECRET_KEY

# Crear la aplicacion Flask
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configurar middleware de autenticación y autorización
from middlewares.auth_middleware import setup_auth_middleware
setup_auth_middleware(app)


# Importar Blueprints
from routes.login import bp as auth_bp
from routes.home import bp as home_bp
from routes.modelos import bp as modelos_bp
from routes.especialidades import bp as especialidades_bp
from routes.casos_clinicos import bp as casos_clinicos_bp
from routes.criterios import bp as criterios_bp
from routes.roles import bp as roles_bp
from routes.usuarios import bp as usuarios_bp
from routes.caso_clinico_especialidad import bp as caso_clinico_especialidad_bp

from routes.puntajes_casos import bp as puntajes_casos_bp
from routes.usuario_rol import bp as usuario_rol_bp
from routes.dashboard import bp as dashboard_bp

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(modelos_bp)
app.register_blueprint(especialidades_bp)
app.register_blueprint(casos_clinicos_bp)
app.register_blueprint(criterios_bp)
app.register_blueprint(roles_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(caso_clinico_especialidad_bp)

app.register_blueprint(puntajes_casos_bp)
app.register_blueprint(usuario_rol_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5100)