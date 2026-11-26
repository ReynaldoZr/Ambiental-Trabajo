"""Rutas de JaguarVerde, un prototipo web local de Educación Ambiental."""
from io import BytesIO
from datetime import date, datetime
from pathlib import Path
import re
import secrets

from flask import (
    Flask, abort, flash, redirect, render_template, request, send_file,
    session, url_for,
)
from PIL import Image, ImageOps, UnidentifiedImageError

from campana import FACULTADES, obtener_reto_actual
from datos import CATEGORIAS, ESTADOS, iniciar_db, obtener_db


VERSION = "0.2"
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
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.config.update(
        SECRET_KEY=obtener_clave_sesion(Path(app.instance_path)),
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
        tema = obtener_reto_actual()
        intento = None
        if session.get("participante_id"):
            intento = db.execute(
                "SELECT aciertos, puntos FROM participacion_reto WHERE reto = ? AND participante = ?",
                (tema["id"], session["participante_id"]),
            ).fetchone()
        clasificacion = obtener_clasificacion(db, tema["id"])
        return render_template("inicio.html", tema=tema, intento=intento,
                               resueltos=resueltos, clasificacion=clasificacion,
                               facultades=FACULTADES)

    @app.post("/reto")
    def reto():
        tema = obtener_reto_actual()
        preguntas = tema["preguntas"]
        respuestas = [request.form.get(f"respuesta_{i}") for i in range(len(preguntas))]
        facultad = request.form.get("facultad", "")
        if facultad not in FACULTADES:
            flash("Selecciona tu facultad o unidad académica para participar.", "error")
        elif any(respuesta not in ("0", "1", "2") for respuesta in respuestas):
            flash("Responde las tres preguntas para completar el reto.", "error")
        else:
            aciertos = sum(int(respuesta) == pregunta[2]
                           for respuesta, pregunta in zip(respuestas, preguntas))
            participante = session.get("participante_id")
            if not participante:
                participante = secrets.token_urlsafe(24)
                session["participante_id"] = participante
            db = obtener_db()
            with db:
                guardado = db.execute(
                    """INSERT OR IGNORE INTO participacion_reto
                       (reto, participante, facultad, aciertos, puntos)
                       VALUES (?, ?, ?, ?, ?)""",
                    (tema["id"], participante, facultad, aciertos, aciertos * 10),
                )
            if guardado.rowcount:
                flash(f"¡Reto completado! Sumaste {aciertos * 10} puntos para tu facultad.", "exito")
            else:
                flash("Ya participaste en el reto de esta semana.", "aviso")
        return redirect(url_for("inicio", _anchor="reto"))

    @app.get("/campana")
    def campana():
        db = obtener_db()
        periodos = listar_periodos(db)
        solicitado = request.args.get("periodo", "")
        periodo = next((p for p in periodos if p["id"] == solicitado), periodos[0])
        resumen = obtener_resumen_semestre(db, periodo)
        return render_template("campana.html", periodo=periodo, periodos=periodos,
                               resumen=resumen)

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
                    "UPDATE reporte SET estado = ?, observacion = ?, actualizado = CURRENT_TIMESTAMP WHERE id = ?",
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
        """SELECT id, titulo, categoria, ubicacion, descripcion, estado, observacion, creado, actualizado
           FROM reporte ORDER BY id DESC"""
    ).fetchall()


def obtener_clave_sesion(carpeta_instancia):
    """Conserva la identidad anónima del navegador entre reinicios locales."""
    archivo = carpeta_instancia / ".clave_jaguarverde"
    try:
        return archivo.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        clave = secrets.token_hex(32)
        try:
            with archivo.open("x", encoding="utf-8") as salida:
                salida.write(clave)
        except FileExistsError:
            return archivo.read_text(encoding="utf-8").strip()
        return clave


def obtener_clasificacion(db, reto_id):
    return db.execute(
        """SELECT facultad, SUM(puntos) AS puntos, COUNT(*) AS participaciones
           FROM participacion_reto WHERE reto = ? GROUP BY facultad
           ORDER BY puntos DESC, facultad COLLATE NOCASE LIMIT 3""",
        (reto_id,),
    ).fetchall()


def periodo_desde_id(periodo_id):
    coincidencia = re.fullmatch(r"(\d{4})-([12])", periodo_id or "")
    if not coincidencia:
        return None
    anio, semestre = int(coincidencia.group(1)), int(coincidencia.group(2))
    inicio = f"{anio}-{'01-01' if semestre == 1 else '07-01'} 00:00:00"
    fin = f"{anio}-{'07-01' if semestre == 1 else '01-01'} 00:00:00"
    if semestre == 2:
        fin = f"{anio + 1}-01-01 00:00:00"
    return {"id": periodo_id, "etiqueta": f"Semestre {semestre} · {anio}",
            "inicio": inicio, "fin": fin}


def listar_periodos(db):
    hoy = date.today()
    actual = f"{hoy.year}-{1 if hoy.month <= 6 else 2}"
    ids = {actual}
    filas = db.execute(
        "SELECT creado FROM reporte UNION ALL SELECT creado FROM participacion_reto"
    ).fetchall()
    for fila in filas:
        try:
            fecha = datetime.strptime(fila["creado"][:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        ids.add(f"{fecha.year}-{1 if fecha.month <= 6 else 2}")
    return [periodo_desde_id(periodo_id) for periodo_id in sorted(ids, reverse=True)]


def obtener_resumen_semestre(db, periodo):
    desde, hasta = periodo["inicio"], periodo["fin"]
    reportes = db.execute(
        """SELECT estado, COUNT(*) AS cantidad FROM reporte
           WHERE creado >= ? AND creado < ? GROUP BY estado""", (desde, hasta),
    ).fetchall()
    categorias = db.execute(
        """SELECT categoria, COUNT(*) AS cantidad FROM reporte
           WHERE creado >= ? AND creado < ? GROUP BY categoria
           ORDER BY cantidad DESC, categoria COLLATE NOCASE""", (desde, hasta),
    ).fetchall()
    participacion = db.execute(
        """SELECT COUNT(*) AS envios, COUNT(DISTINCT participante) AS personas,
                  COALESCE(SUM(puntos), 0) AS puntos
           FROM participacion_reto WHERE creado >= ? AND creado < ?""", (desde, hasta),
    ).fetchone()
    puntos = db.execute(
        """SELECT facultad, SUM(puntos) AS puntos, COUNT(*) AS participaciones
           FROM participacion_reto WHERE creado >= ? AND creado < ?
           GROUP BY facultad ORDER BY puntos DESC, facultad COLLATE NOCASE""",
        (desde, hasta),
    ).fetchall()
    estados = {fila["estado"]: fila["cantidad"] for fila in reportes}
    return {"total_reportes": sum(estados.values()), "estados": estados,
            "categorias": categorias, "participacion": participacion, "puntos": puntos}


if __name__ == "__main__":
    crear_app().run(host="127.0.0.1", port=5000)
