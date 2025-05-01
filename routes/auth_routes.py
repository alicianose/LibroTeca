import uuid
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
import sirope
from models.user import User

auth_bp = Blueprint("auth", __name__)
srp = sirope.Sirope()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Procesar los datos del formulario de inicio de sesión
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Buscar el usuario en la base de datos
        user = srp.find_first(User, lambda u: u.username == username and u.password == password)
        
        if user:
            login_user(user)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("auth.reviews"))  # Redirigir a la página principal
        else:
            flash("Nombre de usuario o contraseña incorrectos.", "error")
    
    # Renderizar la plantilla de inicio de sesión para solicitudes GET
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Procesar los datos del formulario de registro
        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Guardar el usuario en la base de datos usando sirope
        user = User(str(uuid.uuid4()), name, username, email, password)
        srp.save(user)
        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("register.html")

@auth_bp.route("/debug/users", methods=["GET"])
def debug_users():
    users = list(srp.load_all(User))  # Cargar todos los usuarios desde la base de datos
    return render_template("debug_users.html", users=users)

@auth_bp.route("/reviews", methods=["GET"])
@login_required
def reviews():
    return render_template("reviews.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


