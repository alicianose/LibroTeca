from flask import Flask, render_template
import sirope
from flask_login import LoginManager
from routes.auth_routes import auth_bp  # Importar el Blueprint
from models.user import User  # Importar la clase User



# Crear app Flask
app = Flask(__name__)
app.secret_key = "tu_clave_secreta_unica_y_segura"  # Cambia esto por algo único y seguro
app.register_blueprint(auth_bp)
srp = sirope.Sirope()
# Configurar LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # Ruta para redirigir si no está autenticado
# Definir la función user_loader
@login_manager.user_loader
def load_user(user_id):
    return srp.find_first(User, lambda u: u.id == user_id)



@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
