from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:jorge@localhost/jhorstep'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'tu_clave_secreta'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Configurar la carpeta donde se guardarán las imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crear la carpeta si no existe

# Extensiones permitidas (solo imágenes)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Verifica si la extensión del archivo es válida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Modelo de Usuario
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)

# Modelo de Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.String(200), nullable=True)  # Ruta de la imagen

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route("/admin")
@login_required
def admin():
    if not current_user.es_admin:
        flash("Acceso denegado. No tienes permisos de administrador.", "danger")
        return redirect(url_for("inicio_admi"))

    usuarios = Usuario.query.all()
    return render_template("administrador.html", usuarios=usuarios)

@app.route("/inicio_admi")
@login_required
def inicio_admi():
    return render_template("inicio_admi.html")

@app.route("/categoria")
@login_required
def categoria():
    return render_template("categoria.html")

@app.route("/inicio")
@login_required
def inicio():
    return render_template("inicio.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]
        contraseña = generate_password_hash(request.form["password"], method="pbkdf2:sha256")

        usuario_existente = Usuario.query.filter_by(username=username).first()
        email_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            flash("El nombre de usuario ya está en uso.", "danger")
        elif email_existente:
            flash("El correo electrónico ya está registrado.", "danger")
        else:
            nuevo_usuario = Usuario(nombre=nombre, username=username, email=email, contraseña=contraseña)
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
    
    return render_template("registro.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        contraseña = request.form["password"]

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.contraseña, contraseña):
            login_user(usuario)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("admin" if usuario.es_admin else "inicio"))
        
        flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("login"))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)


# Rutas de otras páginas
@app.route("/adidas")
def adidas():
    return render_template("adidas.html")

@app.route("/nike_admi")
def nike_admi():
    return render_template("recuperacion.html")

@app.route("/recuperacion")
def recuperacion():
    return render_template("recuperacion.html")

@app.route("/nike")
def nike():
    return render_template("nike.html")

@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")

@app.route("/puma")
def puma():
    return render_template("puma.html")

@app.route("/reebok")
def reebok():
    return render_template("reebok.html")

@app.route("/vans")
def vans():
    return render_template("vans.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
