from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
import sirope
from models.usuario import Usuario

auth_bp = Blueprint("auth", __name__)
srp = sirope.Sirope()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Aquí pones el formulario login
    ...

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # Aquí pones el formulario de registro
    ...

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


