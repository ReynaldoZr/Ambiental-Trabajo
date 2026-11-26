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

CREATE TABLE IF NOT EXISTS voto_mision (semana TEXT, estudiante_id INTEGER, modo TEXT, PRIMARY KEY(semana,estudiante_id));
CREATE TABLE IF NOT EXISTS intento (
    reto TEXT PRIMARY KEY,
    aciertos INTEGER NOT NULL CHECK (aciertos >= 0)
);

CREATE TABLE IF NOT EXISTS estudiante (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    facultad TEXT NOT NULL,
    carrera TEXT NOT NULL,
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS publicacion (
    id INTEGER PRIMARY KEY,
    tipo TEXT NOT NULL CHECK (tipo IN ('Mensaje', 'Aviso', 'Desafío', 'Evento')),
    titulo TEXT NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_publicacion TEXT NOT NULL,
    fecha_evento TEXT NOT NULL DEFAULT '',
    lugar TEXT NOT NULL DEFAULT '',
    premio TEXT NOT NULL DEFAULT '',
    es_ejemplo INTEGER NOT NULL DEFAULT 0 CHECK (es_ejemplo IN (0, 1)),
    activa INTEGER NOT NULL DEFAULT 1 CHECK (activa IN (0, 1)),
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS participacion_reto (
    reto TEXT NOT NULL,
    participante TEXT NOT NULL,
    facultad TEXT NOT NULL,
    aciertos INTEGER NOT NULL CHECK (aciertos >= 0),
    puntos INTEGER NOT NULL CHECK (puntos >= 0),
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estudiante_id INTEGER REFERENCES estudiante(id),
    PRIMARY KEY (reto, participante)
);

CREATE TABLE IF NOT EXISTS participacion_encuesta (
    encuesta TEXT NOT NULL,
    estudiante_id INTEGER NOT NULL REFERENCES estudiante(id),
    facultad TEXT NOT NULL,
    opcion INTEGER NOT NULL CHECK (opcion >= 0),
    puntos INTEGER NOT NULL DEFAULT 5 CHECK (puntos >= 0),
    creado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (encuesta, estudiante_id)
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
        publicacion_columnas = {
            fila["name"] for fila in db.execute("PRAGMA table_info(publicacion)")
        }
        for columna, definicion in (("actividad", "TEXT DEFAULT 'Campus'"), ("horas", "INTEGER DEFAULT 0")):
            if columna not in publicacion_columnas:
                db.execute(f"ALTER TABLE publicacion ADD COLUMN {columna} {definicion}")
        if "premio" not in publicacion_columnas:
            db.execute("ALTER TABLE publicacion ADD COLUMN premio TEXT NOT NULL DEFAULT ''")
        if "es_ejemplo" not in publicacion_columnas:
            db.execute(
                "ALTER TABLE publicacion ADD COLUMN es_ejemplo INTEGER NOT NULL DEFAULT 0"
            )
        columnas = {fila["name"] for fila in db.execute("PRAGMA table_info(reporte)")}
        if "actualizado" not in columnas:
            db.execute("ALTER TABLE reporte ADD COLUMN actualizado TEXT NOT NULL DEFAULT ''")
            db.execute("UPDATE reporte SET actualizado = creado WHERE actualizado = ''")
        if "estudiante_id" not in columnas:
            db.execute("ALTER TABLE reporte ADD COLUMN estudiante_id INTEGER REFERENCES estudiante(id)")
        participacion_columnas = {
            fila["name"] for fila in db.execute("PRAGMA table_info(participacion_reto)")
        }
        if "estudiante_id" not in participacion_columnas:
            db.execute(
                "ALTER TABLE participacion_reto ADD COLUMN estudiante_id INTEGER REFERENCES estudiante(id)"
            )
        db.commit()
