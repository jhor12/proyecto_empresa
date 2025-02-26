from app import db, Usuario, app
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = Usuario(
        nombre="Administrador",
        username="admin",
        email="jhorstep@gmail.com",
        contraseña=generate_password_hash("12345", method="pbkdf2:sha256"),
        es_admin=True
    )

    db.session.add(admin)
    db.session.commit()

    print("Administrador creado con éxito")
