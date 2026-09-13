"""Crea un usuario admin directo en la base — el rol admin nunca se ofrece
por HTTP (ver app/schemas/usuario.py, RegistroCreate), a propósito: la única
forma de crear uno es tener acceso al servidor/base, no a la red.

Uso:
    python -m app.db.crear_admin --nombre "Martin" --email admin@granjaelmoro.com.ar --password ********
"""

import argparse

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.usuario import RolUsuario, Usuario


def crear_admin(db, nombre: str, email: str, password: str) -> Usuario:
    # El email es case-sensitive en todo el sistema (decisión del cliente,
    # ver app/schemas/usuario.py) — acá solo se recortan espacios, igual
    # que en el registro público.
    email = email.strip()
    if len(password) < 8:
        raise ValueError("La contraseña tiene que tener al menos 8 caracteres")
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise ValueError(f"Ya existe un usuario con el email {email}")

    usuario = Usuario(
        nombre=nombre,
        email=email,
        password_hash=hash_password(password),
        rol=RolUsuario.admin,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _main() -> None:
    parser = argparse.ArgumentParser(description="Crea un usuario admin")
    parser.add_argument("--nombre", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        usuario = crear_admin(db, args.nombre, args.email, args.password)
        print(f"Admin creado: id={usuario.id} email={usuario.email}")
    except ValueError as exc:
        print(f"Error: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    _main()
