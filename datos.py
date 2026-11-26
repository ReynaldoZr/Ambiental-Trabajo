"""Acceso a la base local y a su esquema."""
import sqlite3
from pathlib import Path

from flask import current_app, g


ESTADOS = ("Pendiente", "En proceso", "Resuelto")
CATEGORIAS = (
    "Agua", "Electricidad", "Residuos sólidos", "Higiene ambiental",
    "Infraestructura y drenajes", "Áreas verdes", "Otras situaciones",
)

ESQUEMA = """
CREATE TABLE IF NOT EXISTS reporte (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    categoria TEXT NOT NULL,
    ubicacion TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    foto BLOB NOT NULL,
    estado TEXT NOT NULL DEFAULT 'Pendiente'
        CHECK (estado IN ('Pendiente', 'En proceso', 'Resuelto')),
    observacion TEXT NOT NULL DEFAULT '',
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS intento (
    reto TEXT PRIMARY KEY,
    aciertos INTEGER NOT NULL CHECK (aciertos >= 0)
);

CREATE TABLE IF NOT EXISTS participacion_reto (
    reto TEXT NOT NULL,
    participante TEXT NOT NULL,
    facultad TEXT NOT NULL,
    aciertos INTEGER NOT NULL CHECK (aciertos >= 0),
    puntos INTEGER NOT NULL CHECK (puntos >= 0),
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reto, participante)
);
"""


def obtener_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def cerrar_db(_error=None):
    conexion = g.pop("db", None)
    if conexion is not None:
        conexion.close()


def iniciar_db(app):
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(cerrar_db)
    with app.app_context():
        db = obtener_db()
        db.executescript(ESQUEMA)
        columnas = {fila["name"] for fila in db.execute("PRAGMA table_info(reporte)")}
        if "actualizado" not in columnas:
            db.execute("ALTER TABLE reporte ADD COLUMN actualizado TEXT NOT NULL DEFAULT ''")
            db.execute("UPDATE reporte SET actualizado = creado WHERE actualizado = ''")
        db.commit()
