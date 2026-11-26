"""Rutas de JaguarVerde, un prototipo web local de Educación Ambiental."""
from io import BytesIO
from datetime import date, datetime, timedelta
from functools import wraps
import json
from pathlib import Path
import re
import secrets

from flask import (
    Flask, abort, flash, redirect, render_template, request, send_file,
    session, url_for,
)
from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.security import check_password_hash, generate_password_hash

from campana import FACULTADES, obtener_reto_actual
from comunidad import (
    EJEMPLOS_REPORTE, ENCUESTAS_SEMANALES, MENSAJES_DIARIOS, TIPOS_PUBLICACION,
)
from datos import CATEGORIAS, ESTADOS, iniciar_db, obtener_db


VERSION = "0.5"
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
        ADMIN_FILE=Path(app.instance_path) / ".administrador.json",
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),
        MAX_CONTENT_LENGTH=MAX_FOTO + 128 * 1024,
        TRUSTED_HOSTS=["127.0.0.1", "localhost", "[::1]"],
    )
    iniciar_db(app)
    asegurar_administrador(app.config["ADMIN_FILE"])
    cargar_publicaciones_demo(app)

    def estudiante_actual():
        estudiante_id = session.get("estudiante_id")
        if not estudiante_id:
            return None
        return obtener_db().execute(
            "SELECT id, nombre, facultad, carrera FROM estudiante WHERE id = ?",
            (estudiante_id,),
        ).fetchone()

    def solo_administracion(funcion):
        @wraps(funcion)
        def protegida(*args, **kwargs):
            if not session.get("es_administrador"):
                flash("Inicia sesión como administrador para abrir esta sección.", "aviso")
                return redirect(url_for("login_administrador"))
            return funcion(*args, **kwargs)
        return protegida

    @app.context_processor
    def datos_comunes():
        if "token_formulario" not in session:
            session["token_formulario"] = secrets.token_urlsafe(32)
        return {
            "version": VERSION,
            "token_formulario": session["token_formulario"],
            "estudiante": estudiante_actual(),
            "admin_activo": bool(session.get("es_administrador")),
        }

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
        estudiante = estudiante_actual()
        if estudiante:
            intento = db.execute(
                "SELECT aciertos, puntos FROM participacion_reto WHERE reto = ? AND participante = ?",
                (tema["id"], str(estudiante["id"])),
            ).fetchone()
        mensaje_diario = obtener_mensaje_bienvenida(db, renovar=True)
        clasificacion = obtener_clasificacion(db, tema["id"])
        semana_anterior = obtener_reto_actual(date.today() - timedelta(days=7))["id"]
        ganador = db.execute("SELECT modo FROM voto_mision WHERE semana=? GROUP BY modo ORDER BY COUNT(*) DESC, modo LIMIT 1", (semana_anterior,)).fetchone()
        modo = ganador["modo"] if ganador else ("Detective","Duelo","Safari")[tema["semana"] % 3]
        voto = db.execute("SELECT modo FROM voto_mision WHERE semana=? AND estudiante_id=?", (tema["id"], estudiante["id"])).fetchone() if estudiante else None
        impacto = db.execute("SELECT categoria, estado FROM reporte ORDER BY actualizado DESC, id DESC LIMIT 1").fetchone()
        puntos_semestre = obtener_clasificacion_semestre(db)
        return render_template("inicio.html", tema=tema, intento=intento,
                               resueltos=resueltos, clasificacion=clasificacion,
                               facultades=FACULTADES, estudiante=estudiante,
                               mensaje_diario=mensaje_diario,
                               eventos=obtener_eventos(db)[:2], modo=modo, voto=voto, impacto=impacto,
                               puntos_semestre=puntos_semestre)

    @app.post("/reto")
    def reto():
        estudiante = estudiante_actual()
        if not estudiante:
            flash("Regístrate como estudiante para participar en el reto.", "aviso")
            return redirect(url_for("entrada_estudiante", siguiente="/"))
        tema = obtener_reto_actual()
        preguntas = tema["preguntas"]
        respuestas = [request.form.get(f"respuesta_{i}") for i in range(len(preguntas))]
        if any(respuesta not in ("0", "1", "2") for respuesta in respuestas):
            flash("Responde las tres preguntas para completar el reto.", "error")
        else:
            aciertos = sum(int(respuesta) == pregunta[2]
                           for respuesta, pregunta in zip(respuestas, preguntas))
            participante = str(estudiante["id"])
            db = obtener_db()
            with db:
                guardado = db.execute(
                    """INSERT OR IGNORE INTO participacion_reto
                       (reto, participante, facultad, aciertos, puntos, estudiante_id)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (tema["id"], participante, estudiante["facultad"], aciertos,
                     aciertos * 10, estudiante["id"]),
                )
            if guardado.rowcount:
                flash(f"¡Reto completado! Sumaste {aciertos * 10} puntos para tu facultad.", "exito")
            else:
                flash("Ya participaste en el reto de esta semana.", "aviso")
        return redirect(url_for("inicio", _anchor="reto"))

    @app.get("/bienvenida")
    def nueva_bienvenida():
        respuesta = app.json.response(obtener_mensaje_bienvenida(obtener_db(), renovar=True))
        respuesta.headers["Cache-Control"] = "no-store"
        return respuesta

    @app.post("/encuesta")
    def responder_encuesta():
        estudiante = estudiante_actual()
        if not estudiante:
            flash("Entra como estudiante para votar y sumar 5 puntos a tu unidad.", "aviso")
            return redirect(url_for("entrada_estudiante", siguiente="/comunidad#encuesta"))
        tema = obtener_reto_actual()
        encuesta = encuesta_actual(tema)
        opcion = request.form.get("opcion", "")
        if not opcion.isdigit() or not 0 <= int(opcion) < len(encuesta["opciones"]):
            flash("Elige una opción de la encuesta.", "error")
        else:
            db = obtener_db()
            with db:
                guardado = db.execute(
                    """INSERT OR IGNORE INTO participacion_encuesta
                       (encuesta, estudiante_id, facultad, opcion, puntos)
                       VALUES (?, ?, ?, ?, 5)""",
                    (tema["id"], estudiante["id"], estudiante["facultad"], int(opcion)),
                )
            if guardado.rowcount:
                flash("¡Voto registrado! Sumaste 5 puntos para tu facultad.", "exito")
            else:
                flash("Ya votaste en la encuesta de esta semana. ¡Vuelve la próxima!", "aviso")
        return redirect(url_for("comunidad", _anchor="encuesta"))

    @app.route("/estudiantes/entrar", methods=["GET", "POST"])
    def entrada_estudiante():
        siguiente = destino_estudiante(request.values.get("siguiente", "/"))
        error = None
        datos = {}
        if request.method == "POST":
            datos = {
                "nombre": request.form.get("nombre", "").strip(),
                "facultad": request.form.get("facultad", ""),
                "carrera": request.form.get("carrera", "").strip(),
            }
            if not 2 <= len(datos["nombre"]) <= 100:
                error = "Escribe tu nombre completo (de 2 a 100 caracteres)."
            elif datos["facultad"] not in FACULTADES:
                error = "Selecciona una facultad o unidad académica válida."
            elif not 2 <= len(datos["carrera"]) <= 100:
                error = "Escribe tu carrera (de 2 a 100 caracteres)."
            else:
                db = obtener_db()
                with db:
                    creado = db.execute(
                        "INSERT INTO estudiante (nombre, facultad, carrera) VALUES (?, ?, ?)",
                        (datos["nombre"], datos["facultad"], datos["carrera"]),
                    )
                estudiante_id = creado.lastrowid
                session.clear()
                session["estudiante_id"] = estudiante_id
                session.permanent = True
                flash("Ya puedes participar y consultar tus propios reportes.", "exito")
                return redirect(siguiente)
        return render_template("entrada_estudiante.html", facultades=FACULTADES,
                               datos=datos, error=error, siguiente=siguiente), (400 if error else 200)

    @app.post("/estudiantes/salir")
    def salir_estudiante():
        session.clear()
        flash("Se cerró la sesión de estudiante en este navegador.", "aviso")
        return redirect(url_for("inicio"))

    @app.route("/administracion/entrar", methods=["GET", "POST"])
    def login_administrador():
        error = None
        if request.method == "POST":
            usuario = request.form.get("usuario", "").strip()
            contrasena = request.form.get("contrasena", "")
            cuenta = leer_administrador(app.config["ADMIN_FILE"])
            if usuario == cuenta["usuario"] and check_password_hash(cuenta["hash"], contrasena):
                session.clear()
                session["es_administrador"] = True
                session.permanent = False
                flash("Sesión de administración iniciada.", "exito")
                return redirect(url_for("administracion"))
            error = "El usuario o la contraseña no son correctos."
        return render_template("login_administrador.html", error=error), (401 if error else 200)

    @app.post("/administracion/salir")
    def salir_administrador():
        session.clear()
        flash("Se cerró la sesión de administración.", "aviso")
        return redirect(url_for("inicio"))

    @app.get("/campana")
    def campana():
        db = obtener_db()
        periodos = listar_periodos(db)
        solicitado = request.args.get("periodo", "")
        periodo = next((p for p in periodos if p["id"] == solicitado), periodos[0])
        resumen = obtener_resumen_semestre(db, periodo)
        return render_template("campana.html", periodo=periodo, periodos=periodos,
                               resumen=resumen,
                               periodo_actual=periodo_desde_id(
                                   f"{date.today().year}-{1 if date.today().month <= 6 else 2}"
                               )["id"])

    @app.post("/elegir-mision")
    def elegir_mision():
        persona = estudiante_actual()
        if not persona:
            return redirect(url_for("entrada_estudiante", siguiente="/"))
        modo = request.form.get("modo")
        if modo not in ("Detective", "Duelo", "Safari"):
            abort(400)
        db = obtener_db()
        with db:
            db.execute("INSERT OR IGNORE INTO voto_mision VALUES (?, ?, ?)",
                       (obtener_reto_actual()["id"], persona["id"], modo))
        return redirect(url_for("inicio", _anchor="elegir"))

    @app.get("/agenda")
    def agenda():
        return render_template("agenda.html", eventos=obtener_eventos(obtener_db()))

    @app.get("/comunidad")
    def comunidad():
        db = obtener_db()
        hoy = date.today().isoformat()
        estudiante = estudiante_actual()
        mensaje_diario = obtener_mensaje_bienvenida(db)
        publicaciones = db.execute(
            """SELECT * FROM publicacion
               WHERE activa = 1 AND tipo IN ('Aviso', 'Desafío') AND fecha_publicacion <= ?
               ORDER BY fecha_publicacion DESC, id DESC LIMIT 12""",
            (hoy,),
        ).fetchall()
        eventos = obtener_eventos(db)
        tema = obtener_reto_actual()
        clasificacion = obtener_clasificacion(db, tema["id"])
        encuesta = encuesta_actual(tema)
        voto = None
        insignias = []
        puntos_personales = 0
        if estudiante:
            voto = db.execute(
                "SELECT opcion FROM participacion_encuesta WHERE encuesta = ? AND estudiante_id = ?",
                (tema["id"], estudiante["id"]),
            ).fetchone()
            insignias = obtener_insignias(db, estudiante["id"])
            puntos_personales = obtener_puntos_personales(db, estudiante["id"], tema["id"])
        resultados_encuesta = obtener_resultados_encuesta(db, tema["id"], encuesta["opciones"])
        clasificacion_semestre = obtener_clasificacion_semestre(db)
        return render_template(
            "comunidad.html", mensaje_diario=mensaje_diario,
            publicaciones=publicaciones, eventos=eventos,
            tema=tema, clasificacion=clasificacion, encuesta=encuesta,
            voto=voto, resultados_encuesta=resultados_encuesta,
            insignias=insignias, puntos_personales=puntos_personales,
            clasificacion_semestre=clasificacion_semestre,
        )

    @app.route("/reportes", methods=["GET", "POST"])
    def reportes():
        estudiante = estudiante_actual()
        if not estudiante:
            flash("Identifícate como estudiante antes de enviar o consultar reportes.", "aviso")
            return redirect(url_for("entrada_estudiante", siguiente="/reportes"))
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
                            """INSERT INTO reporte
                               (titulo, categoria, ubicacion, descripcion, foto, estudiante_id)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (datos["titulo"], datos["categoria"], datos["ubicacion"],
                             datos["descripcion"], foto, estudiante["id"]),
                        )
                    flash("Reporte guardado. Puedes consultar su estado aquí.", "exito")
                    return redirect(url_for("reportes", _anchor="seguimiento"))
        return render_template("reportes.html", reportes=listar_reportes(estudiante["id"]), datos=datos,
                               categorias=CATEGORIAS, ejemplos=EJEMPLOS_REPORTE,
                               error=error), (400 if error else 200)

    @app.get("/administracion")
    @solo_administracion
    def administracion():
        estudiantes = obtener_db().execute(
            "SELECT id, nombre, facultad, carrera, creado FROM estudiante ORDER BY nombre COLLATE NOCASE"
        ).fetchall()
        return render_template("administracion.html", reportes=listar_reportes(),
                               estados=ESTADOS, estudiantes=estudiantes)

    @app.route("/administracion/muro", methods=["GET", "POST"])
    @solo_administracion
    def administrar_muro():
        error = None
        datos = {}
        if request.method == "POST":
            datos = {
                "tipo": request.form.get("tipo", ""),
                "titulo": request.form.get("titulo", "").strip(),
                "mensaje": request.form.get("mensaje", "").strip(),
                "fecha_publicacion": request.form.get("fecha_publicacion", ""),
                "fecha_evento": request.form.get("fecha_evento", ""),
                "lugar": request.form.get("lugar", "").strip(),
                "premio": request.form.get("premio", "").strip(),
            }
            actividad = request.form.get("actividad", "Campus")
            horas = request.form.get("horas", "0")
            if actividad not in ("Campus", "Cine", "Deporte", "Voluntariado", "Trueque") or horas not in tuple(map(str, range(9))):
                error = "Selecciona una actividad y una cantidad válida de horas."
            elif datos["tipo"] not in TIPOS_PUBLICACION:
                error = "Selecciona un tipo de publicación válido."
            elif not 3 <= len(datos["titulo"]) <= 90:
                error = "Escribe un título de 3 a 90 caracteres."
            elif not 5 <= len(datos["mensaje"]) <= 500:
                error = "Escribe un mensaje de 5 a 500 caracteres."
            elif not fecha_valida(datos["fecha_publicacion"]):
                error = "Selecciona una fecha válida para publicar."
            elif datos["tipo"] == "Evento" and not fecha_valida(datos["fecha_evento"]):
                error = "Selecciona una fecha válida para el evento."
            elif datos["tipo"] == "Evento" and not 2 <= len(datos["lugar"]) <= 120:
                error = "Indica un lugar de 2 a 120 caracteres para el evento."
            elif datos["tipo"] == "Evento" and len(datos["premio"]) > 160:
                error = "El reconocimiento debe tener hasta 160 caracteres."
            elif datos["tipo"] == "Evento" and datos["fecha_evento"] < date.today().isoformat():
                error = "La fecha del evento debe ser hoy o una fecha futura."
            elif (datos["tipo"] == "Evento"
                  and datos["fecha_evento"] < datos["fecha_publicacion"]):
                error = "El evento no puede ocurrir antes de que se publique su aviso."
            else:
                db = obtener_db()
                with db:
                    db.execute(
                        """INSERT INTO publicacion
                           (tipo, titulo, mensaje, fecha_publicacion, fecha_evento, lugar, premio, actividad, horas)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (datos["tipo"], datos["titulo"], datos["mensaje"],
                         datos["fecha_publicacion"], datos["fecha_evento"], datos["lugar"],
                         datos["premio"] if datos["tipo"] == "Evento" else "", actividad, int(horas)),
                    )
                flash("Publicado en el Muro JaguarVerde.", "exito")
                return redirect(url_for("administrar_muro"))
        publicaciones = obtener_db().execute(
            "SELECT * FROM publicacion ORDER BY activa DESC, fecha_publicacion DESC, id DESC"
        ).fetchall()
        return render_template(
            "administracion_muro.html", publicaciones=publicaciones,
            tipos=TIPOS_PUBLICACION, fecha_hoy=date.today().isoformat(),
            datos=datos, error=error,
        ), (400 if error else 200)

    @app.post("/administracion/muro/<int:publicacion_id>/alternar")
    @solo_administracion
    def alternar_publicacion(publicacion_id):
        db = obtener_db()
        with db:
            cambio = db.execute(
                "UPDATE publicacion SET activa = CASE activa WHEN 1 THEN 0 ELSE 1 END WHERE id = ?",
                (publicacion_id,),
            )
            if cambio.rowcount == 0:
                abort(404)
        flash("Se actualizó la publicación del muro.", "exito")
        return redirect(url_for("administrar_muro"))

    @app.post("/administracion/<int:reporte_id>")
    @solo_administracion
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
        fila = obtener_db().execute(
            "SELECT foto, estudiante_id FROM reporte WHERE id = ?", (reporte_id,)
        ).fetchone()
        if fila is None:
            abort(404)
        estudiante = estudiante_actual()
        if not session.get("es_administrador") and (
            estudiante is None or estudiante["id"] != fila["estudiante_id"]
        ):
            abort(403)
        respuesta = send_file(BytesIO(fila["foto"]), mimetype="image/jpeg", max_age=0)
        respuesta.headers["X-Content-Type-Options"] = "nosniff"
        return respuesta

    @app.errorhandler(413)
    def foto_grande(_error):
        flash("La foto supera el límite de 5 MB. Vuelve a completar el reporte con una foto más ligera.", "error")
        return redirect(url_for("reportes"))

    return app


def listar_reportes(estudiante_id=None):
    consulta = """SELECT reporte.id, reporte.titulo, reporte.categoria, reporte.ubicacion,
                      reporte.descripcion, reporte.estado, reporte.observacion,
                      reporte.creado, reporte.actualizado, reporte.estudiante_id,
                      estudiante.nombre AS nombre_estudiante,
                      estudiante.facultad AS facultad_estudiante,
                      estudiante.carrera AS carrera_estudiante
               FROM reporte LEFT JOIN estudiante ON estudiante.id = reporte.estudiante_id"""
    if estudiante_id is None:
        return obtener_db().execute(consulta + " ORDER BY reporte.id DESC").fetchall()
    return obtener_db().execute(
        consulta + " WHERE reporte.estudiante_id = ? ORDER BY reporte.id DESC",
        (estudiante_id,),
    ).fetchall()


def destino_estudiante(valor):
    return valor if valor in {"/", "/reportes", "/comunidad"} else "/"


def fecha_valida(valor):
    try:
        date.fromisoformat(valor)
    except (TypeError, ValueError):
        return False
    return True


def obtener_mensaje_bienvenida(db, renovar=False):
    """Elige un mensaje distinto al volver a Inicio y lo conserva al navegar."""
    if session.get("mensaje_bienvenida") and not renovar:
        return session["mensaje_bienvenida"]
    hoy = date.today().isoformat()
    publicados = db.execute(
        """SELECT titulo, mensaje FROM publicacion
           WHERE activa = 1 AND tipo = 'Mensaje' AND fecha_publicacion <= ?
           ORDER BY fecha_publicacion DESC, id DESC""",
        (hoy,),
    ).fetchall()
    mensajes = [(fila["titulo"], fila["mensaje"]) for fila in publicados]
    mensajes.extend(MENSAJES_DIARIOS)
    anterior = session.get("mensaje_bienvenida")
    opciones = [mensaje for mensaje in mensajes if mensaje[0] != (anterior or {}).get("titulo")]
    titulo, mensaje = secrets.choice(opciones or mensajes)
    resultado = {"titulo": titulo, "mensaje": mensaje}
    session["mensaje_bienvenida"] = resultado
    return resultado


def encuesta_actual(tema):
    encuesta = ENCUESTAS_SEMANALES[(tema["semana"] - 1) % len(ENCUESTAS_SEMANALES)]
    return {"id": tema["id"], **encuesta}


def obtener_resultados_encuesta(db, encuesta_id, opciones):
    filas = db.execute(
        "SELECT opcion, COUNT(*) AS votos FROM participacion_encuesta WHERE encuesta = ? GROUP BY opcion",
        (encuesta_id,),
    ).fetchall()
    conteos = {fila["opcion"]: fila["votos"] for fila in filas}
    total = sum(conteos.values())
    return [
        {
            "texto": opcion,
            "votos": conteos.get(indice, 0),
            "porcentaje": round(conteos.get(indice, 0) * 100 / total) if total else 0,
        }
        for indice, opcion in enumerate(opciones)
    ]


def obtener_insignias(db, estudiante_id):
    retos = db.execute(
        "SELECT COUNT(DISTINCT reto) FROM participacion_reto WHERE estudiante_id = ?",
        (estudiante_id,),
    ).fetchone()[0]
    votos = db.execute(
        "SELECT COUNT(*) FROM participacion_encuesta WHERE estudiante_id = ?",
        (estudiante_id,),
    ).fetchone()[0]
    reportes = db.execute(
        "SELECT COUNT(*) FROM reporte WHERE estudiante_id = ?",
        (estudiante_id,),
    ).fetchone()[0]
    return [
        {"nombre": "Primer reto", "icono": "✳", "avance": f"{min(retos, 1)}/1", "obtenida": retos >= 1},
        {"nombre": "Racha verde", "icono": "✦", "avance": f"{min(retos, 3)}/3", "obtenida": retos >= 3},
        {"nombre": "Voz del campus", "icono": "◉", "avance": f"{min(votos, 3)}/3", "obtenida": votos >= 3},
        {"nombre": "Ojos Jaguar", "icono": "⌖", "avance": f"{min(reportes, 1)}/1", "obtenida": reportes >= 1},
    ]


def obtener_puntos_personales(db, estudiante_id, reto_id):
    return db.execute(
        """SELECT COALESCE(SUM(puntos), 0) FROM (
             SELECT puntos FROM participacion_reto WHERE estudiante_id = ? AND reto = ?
             UNION ALL
             SELECT puntos FROM participacion_encuesta WHERE estudiante_id = ? AND encuesta = ?
           )""",
        (estudiante_id, reto_id, estudiante_id, reto_id),
    ).fetchone()[0]


def obtener_eventos(db):
    hoy = date.today().isoformat()
    return db.execute(
        """SELECT * FROM publicacion
           WHERE activa = 1 AND tipo = 'Evento' AND fecha_publicacion <= ?
             AND (fecha_evento >= ? OR es_ejemplo = 1)
           ORDER BY es_ejemplo, CASE WHEN es_ejemplo = 0 THEN fecha_evento END, id""",
        (hoy, hoy),
    ).fetchall()


def cargar_publicaciones_demo(app):
    """Completa la agenda de muestra sin duplicar ni reactivar ejemplos."""
    with app.app_context():
        db = obtener_db()
        hoy = date.today().isoformat()
        eventos = (
            ("Ruta JaguarVerde · ejemplo", "Búsqueda de pistas por equipos. Encuentra tres oportunidades para cuidar el campus.", "Insignia de explorador"),
            ("Final de la Copa JaguarVerde", "Miniquiz entre facultades, podio y presentación de la idea ambiental ganadora.", "Mención en el Muro y kit reutilizable sujeto a aprobación"),
        )
        with db:
            db.execute(
                """UPDATE publicacion SET mensaje = ?, premio = ?, fecha_evento = '', lugar = ''
                   WHERE tipo = 'Evento' AND es_ejemplo = 1 AND titulo = ?
                     AND mensaje LIKE 'Borrador demostrativo.%'""",
                (eventos[0][1], eventos[0][2], eventos[0][0]),
            )
            vacio = not db.execute("SELECT 1 FROM publicacion LIMIT 1").fetchone()
            if vacio:
                db.executemany(
                    """INSERT INTO publicacion (tipo, titulo, mensaje, fecha_publicacion, es_ejemplo)
                       VALUES (?, ?, ?, ?, 1)""",
                    (
                        ("Mensaje", "¿Puedes mover el marcador?", "Tres preguntas bastan para sumar hasta 30 puntos.", hoy),
                        ("Aviso", "Tu reporte empieza con una pista", "Agrega edificio, piso y un punto de referencia.", hoy),
                        ("Desafío", "Reto de muestra: 3 preguntas + 1 voto", "Juega y vota para sumar hasta 35 puntos.", hoy),
                    ),
                )
            db.executemany(
                """INSERT INTO publicacion
                   (tipo, titulo, mensaje, fecha_publicacion, premio, es_ejemplo)
                   SELECT 'Evento', ?, ?, ?, ?, 1
                   WHERE NOT EXISTS (
                       SELECT 1 FROM publicacion WHERE tipo = 'Evento' AND es_ejemplo = 1 AND titulo = ?
                   )""",
                [(titulo, mensaje, hoy, premio, titulo) for titulo, mensaje, premio in eventos],
            )


            for categoria, titulo, detalle, horas in (
                ("Cine", "Cine bajo los árboles", "Función ambiental y votación por la próxima película.", 0),
                ("Deporte", "Partido por el campus", "Arma tu equipo y trae tu termo para el partido amistoso.", 0),
                ("Trueque", "Cambia un libro", "Trae un libro usado y elige otro en la mesa de intercambio.", 0),
                ("Voluntariado", "Equipo de la Ruta", "Ayuda a preparar las estaciones y orientar a los equipos. Horas ilustrativas para colaboradores.", 2),
            ):
                db.execute("""INSERT INTO publicacion
                    (tipo,titulo,mensaje,fecha_publicacion,es_ejemplo,actividad,horas)
                    SELECT 'Evento',?,?,?,1,?,? WHERE NOT EXISTS
                    (SELECT 1 FROM publicacion WHERE es_ejemplo=1 AND titulo=?)""",
                    (titulo, detalle, hoy, categoria, horas, titulo))


def leer_administrador(archivo):
    return json.loads(archivo.read_text(encoding="utf-8"))


def asegurar_administrador(archivo):
    if archivo.exists():
        return
    contrasena = secrets.token_urlsafe(16)
    cuenta = {"usuario": "admin", "hash": generate_password_hash(contrasena)}
    archivo.write_text(json.dumps(cuenta), encoding="utf-8")
    acceso = archivo.parent / "acceso_administrador.txt"
    acceso.write_text(
        "Acceso inicial local de JaguarVerde\n"
        "Usuario: admin\n"
        f"Contraseña: {contrasena}\n\n"
        "Guarda estos datos. Este archivo está excluido de Git.\n",
        encoding="utf-8",
    )


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
           FROM (
             SELECT facultad, puntos FROM participacion_reto WHERE reto = ?
             UNION ALL
             SELECT facultad, puntos FROM participacion_encuesta WHERE encuesta = ?
           ) GROUP BY facultad
           ORDER BY puntos DESC, facultad COLLATE NOCASE LIMIT 3""",
        (reto_id, reto_id),
    ).fetchall()


def obtener_clasificacion_semestre(db):
    hoy = date.today()
    periodo_id = f"{hoy.year}-{1 if hoy.month <= 6 else 2}"
    periodo = periodo_desde_id(periodo_id)
    return db.execute(
        """SELECT facultad, SUM(puntos) AS puntos, COUNT(*) AS participaciones
           FROM (
             SELECT facultad, puntos FROM participacion_reto WHERE creado >= ? AND creado < ?
             UNION ALL
             SELECT facultad, puntos FROM participacion_encuesta WHERE creado >= ? AND creado < ?
           ) GROUP BY facultad
           ORDER BY puntos DESC, facultad COLLATE NOCASE LIMIT 3""",
        (periodo["inicio"], periodo["fin"], periodo["inicio"], periodo["fin"]),
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
        """SELECT creado FROM reporte
           UNION ALL SELECT creado FROM participacion_reto
           UNION ALL SELECT creado FROM participacion_encuesta"""
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
           FROM (
             SELECT COALESCE(CAST(estudiante_id AS TEXT), participante) AS participante,
                    puntos, creado FROM participacion_reto WHERE creado >= ? AND creado < ?
             UNION ALL
             SELECT CAST(estudiante_id AS TEXT) AS participante, puntos, creado
                    FROM participacion_encuesta WHERE creado >= ? AND creado < ?
           )""", (desde, hasta, desde, hasta),
    ).fetchone()
    puntos = db.execute(
        """SELECT facultad, SUM(puntos) AS puntos, COUNT(*) AS participaciones
           FROM (
             SELECT facultad, puntos FROM participacion_reto WHERE creado >= ? AND creado < ?
             UNION ALL
             SELECT facultad, puntos FROM participacion_encuesta WHERE creado >= ? AND creado < ?
           ) GROUP BY facultad ORDER BY puntos DESC, facultad COLLATE NOCASE""",
        (desde, hasta, desde, hasta),
    ).fetchall()
    estados = {fila["estado"]: fila["cantidad"] for fila in reportes}
    return {"total_reportes": sum(estados.values()), "estados": estados,
            "categorias": categorias, "participacion": participacion, "puntos": puntos}


if __name__ == "__main__":
    crear_app().run(host="127.0.0.1", port=5000)
