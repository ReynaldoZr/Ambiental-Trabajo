"""Rutas de JaguarVerde, un prototipo web local de Educación Ambiental."""
from io import BytesIO
from pathlib import Path
import secrets

from flask import (
    Flask, abort, flash, redirect, render_template, request, send_file,
    session, url_for,
)
from PIL import Image, ImageOps, UnidentifiedImageError

from campana import TEMA
from datos import CATEGORIAS, ESTADOS, iniciar_db, obtener_db


VERSION = "0.1"
MAX_FOTO = 5 * 1024 * 1024


def preparar_foto(archivo):
    """Valida una foto y guarda una copia JPEG acotada, sin metadatos."""
    if not archivo or not archivo.filename:
        raise ValueError("Adjunta una foto del problema.")
    contenido = archivo.stream.read(MAX_FOTO + 1)
    if len(contenido) > MAX_FOTO:
        raise ValueError("La foto debe pesar como máximo 5 MB.")
    try:
        with Image.open(BytesIO(contenido), formats=("JPEG", "PNG", "WEBP")) as original:
            if original.width * original.height > 24_000_000:
                raise ValueError("La foto es demasiado grande en píxeles.")
            foto = ImageOps.exif_transpose(original).convert("RGB")
            foto.thumbnail((1600, 1600))
            copia = Image.new("RGB", foto.size)
            copia.paste(foto)
            salida = BytesIO()
            copia.save(salida, "JPEG", quality=85)
            return salida.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise ValueError("Usa una foto válida en formato JPG, PNG o WebP.") from error


def crear_app(ruta_db=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=secrets.token_hex(32),
        DATABASE=ruta_db or Path(app.instance_path) / "jaguarverde.sqlite",
        MAX_CONTENT_LENGTH=MAX_FOTO + 128 * 1024,
        TRUSTED_HOSTS=["127.0.0.1", "localhost", "[::1]"],
    )
    iniciar_db(app)

    @app.context_processor
    def datos_comunes():
        if "token_formulario" not in session:
            session["token_formulario"] = secrets.token_urlsafe(32)
        return {"version": VERSION, "token_formulario": session["token_formulario"]}

    @app.before_request
    def proteger_formularios():
        if request.method == "POST":
            esperado = session.get("token_formulario")
            recibido = request.form.get("token_formulario", "")
            if not esperado or not secrets.compare_digest(esperado.encode(), recibido.encode()):
                abort(400)

    @app.get("/")
    def inicio():
        db = obtener_db()
        resueltos = db.execute("SELECT COUNT(*) FROM reporte WHERE estado = 'Resuelto'").fetchone()[0]
        intento = db.execute("SELECT aciertos FROM intento WHERE reto = ?", (TEMA["id"],)).fetchone()
        return render_template("inicio.html", tema=TEMA, intento=intento, resueltos=resueltos)

    @app.post("/reto")
    def reto():
        preguntas = TEMA["preguntas"]
        respuestas = [request.form.get(f"respuesta_{i}") for i in range(len(preguntas))]
        if any(respuesta not in ("0", "1", "2") for respuesta in respuestas):
            flash("Responde las tres preguntas para completar el reto.", "error")
        else:
            aciertos = sum(int(respuesta) == pregunta[2]
                           for respuesta, pregunta in zip(respuestas, preguntas))
            db = obtener_db()
            with db:
                db.execute("INSERT OR IGNORE INTO intento (reto, aciertos) VALUES (?, ?)",
                           (TEMA["id"], aciertos))
        return redirect(url_for("inicio", _anchor="reto"))

    @app.route("/reportes", methods=["GET", "POST"])
    def reportes():
        db = obtener_db()
        datos = {}
        error = None
        if request.method == "POST":
            campos = {"titulo": 80, "ubicacion": 100, "descripcion": 350}
            datos = {campo: request.form.get(campo, "").strip() for campo in campos}
            datos["categoria"] = request.form.get("categoria", "")
            if any(not datos[campo] or len(datos[campo]) > limite for campo, limite in campos.items()):
                error = "Completa el título, la ubicación y la descripción dentro de los límites indicados."
            elif datos["categoria"] not in CATEGORIAS:
                error = "Selecciona una categoría de la lista."
            else:
                try:
                    foto = preparar_foto(request.files.get("foto"))
                except ValueError as problema:
                    error = str(problema)
                else:
                    with db:
                        db.execute(
                            """INSERT INTO reporte (titulo, categoria, ubicacion, descripcion, foto)
                               VALUES (?, ?, ?, ?, ?)""",
                            (datos["titulo"], datos["categoria"], datos["ubicacion"],
                             datos["descripcion"], foto),
                        )
                    flash("Reporte guardado. Puedes consultar su estado aquí.", "exito")
                    return redirect(url_for("reportes", _anchor="seguimiento"))
        return render_template("reportes.html", reportes=listar_reportes(), datos=datos,
                               categorias=CATEGORIAS, error=error), (400 if error else 200)

    @app.get("/administracion")
    def administracion():
        return render_template("administracion.html", reportes=listar_reportes(), estados=ESTADOS)

    @app.post("/administracion/<int:reporte_id>")
    def actualizar(reporte_id):
        estado = request.form.get("estado", "")
        observacion = request.form.get("observacion", "").strip()
        if estado not in ESTADOS or len(observacion) > 350:
            flash("Elige un estado válido y escribe hasta 350 caracteres.", "error")
        else:
            db = obtener_db()
            with db:
                cambio = db.execute(
                    "UPDATE reporte SET estado = ?, observacion = ? WHERE id = ?",
                    (estado, observacion, reporte_id),
                )
                if cambio.rowcount == 0:
                    abort(404)
            flash("Actualización guardada.", "exito")
        return redirect(url_for("administracion", _anchor=f"reporte-{reporte_id}"))

    @app.get("/reportes/<int:reporte_id>/foto")
    def ver_foto(reporte_id):
        fila = obtener_db().execute("SELECT foto FROM reporte WHERE id = ?", (reporte_id,)).fetchone()
        if fila is None:
            abort(404)
        respuesta = send_file(BytesIO(fila["foto"]), mimetype="image/jpeg", max_age=0)
        respuesta.headers["X-Content-Type-Options"] = "nosniff"
        return respuesta

    @app.errorhandler(413)
    def foto_grande(_error):
        flash("La foto supera el límite de 5 MB. Vuelve a completar el reporte con una foto más ligera.", "error")
        return redirect(url_for("reportes"))

    return app


def listar_reportes():
    return obtener_db().execute(
        """SELECT id, titulo, categoria, ubicacion, descripcion, estado, observacion
           FROM reporte ORDER BY id DESC"""
    ).fetchall()


if __name__ == "__main__":
    crear_app().run(host="127.0.0.1", port=5000)
