import uuid
from werkzeug.utils import secure_filename
import os
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
import sirope
from flask_login import current_user
from models.user import User
from models.book import Book
from models.review import Review
from models.likereview import LikeReview
from models.coment import Coment
from models.userbook import UserBook
from datetime import datetime


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
    books = list(srp.load_all(Book))
    return render_template("debug_users.html", users=users, books=books)

@auth_bp.route("/reviews", methods=["GET", "POST"])
@login_required
def reviews():
    if request.method == "POST":
        # Procesar el comentario
        review_id = request.form.get("review_id")
        text = request.form.get("text")
        user_id = current_user.id

        # Crear un nuevo comentario y guardarlo en la base de datos
        new_coment = Coment(str(uuid.uuid4()), user_id, review_id, text)
        srp.save(new_coment)
        flash("Comentario añadido exitosamente.", "success")
        return redirect(url_for("auth.reviews"))

    # GET: Renderizar la página de reseñas
    reviews = sorted(srp.load_all(Review), key=lambda r: r.timestamp, reverse=True)
    users = {user.id: user.username for user in srp.load_all(User)}
    books = {book.id: book.title for book in srp.load_all(Book)}
    likes = {}
    user_likes = set()
    for like in srp.load_all(LikeReview):
        if like.review_id in likes:
            likes[like.review_id] += 1
        else:
            likes[like.review_id] = 1

        if like.user_id == current_user.id:
            user_likes.add(like.review_id)

    # Cargar los comentarios
    comments = {}
    for coment in srp.load_all(Coment):
        if coment.review_id not in comments:
            comments[coment.review_id] = []
        comments[coment.review_id].append(coment)

    return render_template("reviews.html", reviews=reviews, users=users, books=books, likes=likes, user_likes=user_likes, comments=comments)
@auth_bp.route("/addbook", methods=["GET", "POST"])
@login_required
def add_book():
    if request.method == "POST":
        # Procesar los datos del formulario
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        author = request.form.get("author")
        descr = request.form.get("descr")
        genre = request.form.get("genre")
        # Manejar la subida de la portada
        cover = request.files["cover"]
        if cover:
            filename = secure_filename(cover.filename)
            cover.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        # Crear un nuevo libro y guardarlo en la base de datos
        new_book = Book(str(uuid.uuid4()), isbn, title, author, descr, filename, genre, current_user.username)
        srp.save(new_book)
        flash("Libro añadido exitosamente.", "success")
        return redirect(url_for("auth.reviews"))

    return render_template("add_book.html")

@auth_bp.route("/books", methods=["GET"])
@login_required
def books():
    # Cargar todos los libros desde la base de datos
    books = list(srp.load_all(Book))
    return render_template("books.html", books=books)

@auth_bp.route("/addreview", methods=["GET", "POST"])
@login_required
def add_review():
    book_id = request.args.get("book_id")
    if request.method == "POST":
        # Procesar los datos del formulario de reseña
        score = request.form.get("score")
        coment = request.form.get("coment")
        user_id = current_user.id
       
        # Crear una nueva reseña y guardarla en la base de datos
        new_review = Review(str(uuid.uuid4()), user_id, book_id, score, coment, datetime.now())
        srp.save(new_review)
        flash("Reseña añadida exitosamente.", "success")
        return redirect(url_for("auth.books"))

    return render_template("add_review.html", book_id=book_id)

@auth_bp.route("/like_review", methods=["POST"])
@login_required
def like_review():
    review_id = request.form.get("review_id")
    user_id = current_user.id

    # Verificar si el usuario ya dio like a esta reseña
    existing_like = srp.find_first(LikeReview, lambda l: l.user_id == user_id and l.review_id == review_id)
    if existing_like:
          # Si ya existe el like, eliminarlo
        srp.delete(existing_like)  # Eliminar el like existente
        flash("Like eliminado.", "info")

    else:
        # Crear un nuevo like y guardarlo en la base de datos
        new_like = LikeReview(str(uuid.uuid4()), user_id, review_id)
        srp.save(new_like)
        flash("Like añadido exitosamente.", "success")

    return redirect(url_for("auth.reviews"))

@auth_bp.route("/mybooks", methods=["GET"])
@login_required
def my_books():
    # Filtrar los libros añadidos por el usuario actual
    user_books = [book for book in srp.load_all(Book) if book.addedby == current_user.username]
    return render_template("my_books.html", books=user_books)

@auth_bp.route("/myreviews", methods=["GET"])
@login_required
def my_reviews():
    # Filtrar las reseñas creadas por el usuario actual
    user_reviews = [review for review in srp.load_all(Review) if review.user_id == current_user.id]

    # Filtrar los comentarios hechos por el usuario actual
    user_comments = [coment for coment in srp.load_all(Coment) if coment.user_id == current_user.id]

    # Cargar los datos necesarios para mostrar las reseñas y comentarios
    users = {user.id: user.username for user in srp.load_all(User)}
    books = {book.id: book.title for book in srp.load_all(Book)}

    return render_template("my_reviews.html", reviews=user_reviews, comments=user_comments, users=users, books=books)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


