import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///proyecto.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")

def index():

    return render_template("landing.html")



@app.route("/2")

def index2():

    return render_template("duplicate.html")


@app.route("/landing", methods=["GET", "POST"])
@login_required
def landing():
    user_id = session["user_id"]
    admin = db.execute("Select admin from usuario where Id = ?" , user_id)[0]["admin"]
    usuario = db.execute("SELECT Username FROM usuario WHERE Id = ?", user_id)[0]["Username"]
    print(usuario)
    comidas = db.execute("SELECT id, nombre, descripcion, precio, precio_decuento, Descuento FROM comida")
    prueba = db.execute("SELECT nombre FROM comida")
    prueba = prueba[0]["nombre"]
    print(prueba)
    print(request.form.get("lel"))
    if admin == 'on' and len(usuario) != 0:
        return render_template("landing.html", usuario=usuario, admin='admin', comidas=comidas, prueba=prueba)
    else:
        return render_template("landing.html", usuario=usuario, comidas=comidas)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM usuario WHERE Username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
            print('o')

        # Remember which user has logged in
        session["user_id"] = rows[0]["Id"]

        # Redirect user to home page
        return redirect("/landing")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if(request.method == "POST"):
        nombre = request.form.get('name')
        apellido = request.form.get('apellido')
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        username = request.form.get('usuario')
        password = request.form.get('contraseña')
        confirmacion = request.form.get('confirmar')
        if not username:
            return apology("EL username es requerido", 400)
        elif not request.form.get("contraseña"):
            return apology("EL password es requerido", 400)
        elif not request.form.get("confirmar"):
            return apology("La confirmacion es requerida", 400)

        if password != confirmacion:
            return apology('El Password es diferente', 400)

        hash = generate_password_hash(password)

        query = db.execute("Select Username from usuario where Username = ?" , username)
        if len(query) != 0:
             return apology('El Username Ya esta usado', 400)

        try:
            db.execute("INSERT INTO usuario(nombre, apellido, Correo, Telefono, Username, hash) VALUES(?, ?, ?, ?, ?, ?)", nombre, apellido, correo, telefono, username, hash)
            return redirect('/login')
        except:
            return apology('El usuario ya esta usado', 400)

    else:

        return render_template("registro.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if(request.method == "POST"):
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        descuento = request.form.get('descuento')
        p_descuento = request.form.get('p_descuento')

        validacion = db.execute("Select nombre from comida where nombre = ?" , nombre)
        if len(validacion) != 0:
             return apology('El Platillo, Ya esta usado', 400)
        try:
            db.execute("INSERT INTO comida(nombre, descripcion, precio, precio_decuento, Descuento) VALUES(?, ?, ?, ?, ?)", nombre, descripcion, precio, descuento, p_descuento)
            return redirect('/landing')
        except:
            return apology('El usuario ya esta usado', 400)

    else:
        comidas = db.execute("SELECT nombre, descripcion, precio, precio_decuento, Descuento FROM comida")
        return render_template("admin.html", comidas=comidas)

@app.route("/administrador", methods=["GET", "POST"])
@login_required
def administrador():
    if(request.method == "POST"):
        id = request.form.get('id')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio')
        descuento = request.form.get('descuento')
        p_descuento = request.form.get('p_descuento')
        if len(id) != 1 :
            return apology('El Platillo, no existe', 400)
        else:
            db.execute("UPDATE comida SET nombre = ?, descripcion = ?, precio = ?, precio_decuento = ?, Descuento = ? WHERE id = ?", nombre, descripcion, precio, descuento, p_descuento, id)
            return redirect('/landing')
    else:
        comidas = db.execute("SELECT id, nombre, descripcion, precio, precio_decuento, Descuento FROM comida")
        return render_template("administrador.html", comidas=comidas)


@app.route("/eliminar", methods=["GET", "POST"])
@login_required
def eliminar():
    if(request.method == "POST"):
        id = request.form.get('id')
        if len(id) != 1:
            return apology('El Platillo, no existe', 400)
        else:
            db.execute("DELETE FROM comida WHERE id = ?;", id)
            return redirect('/landing')
    else:
        comidas = db.execute(
            "SELECT id, nombre, descripcion, precio, precio_decuento, Descuento FROM comida")
        return render_template("eliminar.html", comidas=comidas)


@app.route("/historial", methods=["GET", "POST"])
@login_required
def historial():
    return render_template("hs.html")