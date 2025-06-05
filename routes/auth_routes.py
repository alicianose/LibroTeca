import uuid
from werkzeug.utils import secure_filename
import os
from flask import Blueprint, jsonify, render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
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
@auth_bp.route("/review/<review_id>")
@login_required
def review_detail(review_id):
    review = srp.find_first(Review, lambda r: r.id == review_id)
    if not review:
        flash("Reseña no encontrada.", "danger")
        return redirect(url_for("auth.reviews"))
    users = {user.id: user.username for user in srp.load_all(User)}
    books = {book.id: book.title for book in srp.load_all(Book)}
    all_comments = [c for c in srp.load_all(Coment) if c.review_id == review_id]
    return render_template("review_detail.html", review=review, users=users, books=books, comments=all_comments)

@auth_bp.route("/addbook", methods=["GET", "POST"])
@login_required
def add_book():
    if request.method == "POST":
        # Procesar los datos del formulario
        title = request.form.get("title")
        author = request.form.get("author")
        descr = request.form.get("descr")
        genre = request.form.get("genre")
        # Manejar la subida de la portada
        cover = request.files["cover"]
         # --- Comprobar si ya existe un libro con ese título y autor ---
        exists = srp.find_first(Book, lambda b: b.title.strip().lower() == title.strip().lower() and b.author.strip().lower() == author.strip().lower())
        if exists:
            flash("Ya existe un libro con ese título y autor.", "danger")
            return redirect(url_for("auth.add_book"))

        if cover:
            filename = secure_filename(cover.filename)
            cover.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = "Nodisponible.jpg"

        # Crear un nuevo libro y guardarlo en la base de datos
        new_book = Book(str(uuid.uuid4()), title, author, descr, filename, genre, current_user.username)
        srp.save(new_book)
        flash("Libro añadido exitosamente.", "success")
        return redirect(url_for("auth.reviews"))

    return render_template("add_book.html")

@auth_bp.route("/delete_book/<book_id>", methods=["POST"])
@login_required
def delete_book(book_id):
    for key in srp.load_all_keys(Book):
        book = srp.load(key)
        if book and book.id==book_id:
            srp.delete(key)
            break
    return redirect(url_for('auth.my_books'))

@auth_bp.route("/books", methods=["GET"])
@login_required
def books():
    # Cargar todos los libros desde la base de datos
    books = list(srp.load_all(Book))
    user_books = {ub.book_id: ub.state for ub in srp.load_all(UserBook) if ub.user_id == current_user.id}
    return render_template("books.html", books=books, user_books=user_books)

@auth_bp.route("/books/<book_id>")
@login_required
def book(book_id):
    book = next((b for b in srp.load_all(Book) if b.id == book_id), None)
    if not book:
        abort(404)

    # Obtener nombre del usuario que agregó el libro

    # Calcular media de puntuaciones
    reviews = [r for r in srp.load_all(Review) if r.book_id == book_id]
    avg_score = round(sum(int(r.score) for r in reviews) / len(reviews), 1) if reviews else "Sin valoraciones"

    # Ordenar reseñas por número de likes descendente
    likes = list(srp.load_all(LikeReview))
    review_likes = {r.id: sum(1 for l in likes if l.review_id == r.id) for r in reviews}
    reviews.sort(key=lambda r: review_likes.get(r.id, 0), reverse=True)

    # Ver si el libro ya está en la lista personal del usuario
    user_book = next((ub for ub in srp.load_all(UserBook)
                      if ub.user_id == current_user.id and ub.book_id == book_id), None)
    current_state = user_book.state if user_book else "Añadir a una lista"

    users = {u.id: u.username for u in srp.load_all(User)}


    return render_template("book.html",
                           book=book,
                           avg_score=avg_score,
                           reviews=reviews,
                           review_likes=review_likes,
                           current_state=current_state, 
                           users=users)


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
@auth_bp.route("/add_comment/<review_id>", methods=["POST"])
@login_required
def add_comment(review_id):
    text = request.form.get("text")
    if text:
        new_comment = Coment(str(uuid.uuid4()), current_user.id, review_id, text, datetime.now())
        srp.save(new_comment)
        flash("Comentario añadido correctamente.", "success")
    else:
        flash("El comentario no puede estar vacío.", "danger")
    return redirect(url_for("auth.review_detail", review_id=review_id))

@auth_bp.route("/like_review", methods=["POST"])
@login_required
def like_review():
    review_id = request.form.get("review_id")
    user_id = current_user.id

    # Verificar si el usuario ya dio like a esta reseña
    existing_like = srp.find_first(LikeReview, lambda l: l.user_id == user_id and l.review_id == review_id)
    if existing_like:
        # Buscar el like recorriendo todas las claves, igual que en delete_book
        for key in srp.load_all_keys(LikeReview):
            like = srp.load(key)
            if like and like.user_id == user_id and like.review_id == review_id:
                srp.delete(key)
                return jsonify({"status": "removed"})
    else:
        # Crear un nuevo like y guardarlo en la base de datos
        new_like = LikeReview(str(uuid.uuid4()), user_id, review_id)
        srp.save(new_like)
        return jsonify({"status": "added"}) 
@auth_bp.route("/mybooks")
@login_required
def my_books():
    books = srp.load_all(Book)
    my_books = [b for b in books if b.addedby == current_user.username]
    return render_template("my_books.html", books=my_books)


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

    # Crear el diccionario review_books: review_id -> título del libro
    all_reviews = list(srp.load_all(Review))
    review_books = {r.id: books[r.book_id] for r in all_reviews if r.book_id in books}

    return render_template(
        "my_reviews.html",
        reviews=user_reviews,
        comments=user_comments,
        users=users,
        books=books,
        review_books=review_books  # <-- pásalo aquí
    )

@auth_bp.route("/delete_review/<review_id>", methods=["POST"])
@login_required
def delete_review(review_id):
    # Buscar y eliminar la reseña
    for key in srp.load_all_keys(Review):
        review = srp.load(key)
        if review and review.id == review_id and review.user_id == current_user.id:
            # Eliminar los comentarios relacionados a la reseña
            for comment_key in srp.load_all_keys(Coment):
                comment = srp.load(comment_key)
                if comment and comment.review_id == review_id:
                    srp.delete(comment_key)
            # Eliminar la reseña
            srp.delete(key)
            break

    return redirect(url_for("auth.my_reviews"))

@auth_bp.route("/update_book_state", methods=["POST"])
@login_required
def update_book_state():
    try:
        data = request.get_json()
        book_id = data.get("book_id")
        new_state = data.get("state")

        # Verifica que book_id y new_state existen
        if not book_id or not new_state:
            return jsonify({"success": False, "error": "Faltan datos"}), 400

        # Buscar si ya existe un UserBook para este usuario y libro
        for key in srp.load_all_keys(UserBook):
            user_book = srp.load(key)
            if user_book.user_id == current_user.id and user_book.book_id == book_id:
                user_book.state = new_state
                srp.save(user_book)
                return jsonify({"success": True})

        # Si no existe, crear uno nuevo
        import datetime, uuid
        now = datetime.datetime.now()
        new_ub = UserBook(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            book_id=book_id,
            state=new_state,
            date=now.date().isoformat(),
            hour=now.time().strftime("%H:%M:%S")
        )
        srp.save(new_ub)
        return jsonify({"success": True})

    except Exception as e:
        import traceback
        print("Error en /update_book_state:", traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500
    
@auth_bp.route("/lists", methods=["GET"])
@login_required
def my_lists():
    all_user_books = [ub for ub in srp.load_all(UserBook) if ub.user_id == current_user.id]
    all_books = {b.id: b for b in srp.load_all(Book)}

    books_with_state = []
    for ub in all_user_books:
        book = all_books.get(ub.book_id)
        if book:
            books_with_state.append({
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "descr": book.descr,
                "cover": book.cover,
                "state": ub.state  # Estado correcto desde UserBook
            })

    # Separar en listas por estado
    pending = [b for b in books_with_state if b["state"] == "Pendiente"]
    reading = [b for b in books_with_state if b["state"] == "Leyendo"]
    read = [b for b in books_with_state if b["state"] == "Leído"]

    return render_template("lists.html", pending=pending, reading=reading, read=read)





@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


