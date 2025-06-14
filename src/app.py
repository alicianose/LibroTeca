import os
from tokenize import Comment
from flask import Flask, render_template
import sirope
from flask_login import LoginManager, current_user
from models.book import Book
from models.likereview import LikeReview
from models.review import Review
from models.userbook import UserBook
from routes.auth_routes import auth_bp  # Importar el Blueprint
from models.user import User  # Importar la clase User
from werkzeug.utils import secure_filename





# Crear app Flask
app = Flask(__name__)
app.secret_key = "tu_clave_secreta_unica_y_segura"  
app.register_blueprint(auth_bp)
srp = sirope.Sirope()
# Configuración para subir archivos
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login" 

@login_manager.user_loader
def load_user(user_id):
    return srp.find_first(User, lambda u: u.id == user_id)

@app.context_processor
def inject_user():
    return dict(current_user=current_user)


@app.route("/")
def index():
    return render_template("index.html")
@app.route("/reset_db")
def reset_db():
    models = [User, Book, Review, Comment, LikeReview, UserBook]

    for model in models:
        for oid in srp.load_all_keys(model):
            srp.delete(oid)

    return "Se ha eliminado todo"

if __name__ == "__main__":
    app.run(debug=True)
