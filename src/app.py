import os
from flask import Flask, render_template
import sirope
from flask_login import LoginManager, current_user
from routes.auth_routes import auth_bp  # Importar el Blueprint
from models.user import User  # Importar la clase User
from werkzeug.utils import secure_filename





# Crear app Flask
app = Flask(__name__)
app.secret_key = "tu_clave_secreta_unica_y_segura"  # Cambia esto por algo único y seguro
app.register_blueprint(auth_bp)
srp = sirope.Sirope()
# Configuración para subir archivos
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Tamaño máximo: 16 MB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Configurar LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # Ruta para redirigir si no está autenticado
# Definir la función user_loader
@login_manager.user_loader
def load_user(user_id):
    return srp.find_first(User, lambda u: u.id == user_id)

@app.context_processor
def inject_user():
    return dict(current_user=current_user)


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
