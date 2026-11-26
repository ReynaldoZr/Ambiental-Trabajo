"""Mensajes breves para invitar a volver a JaguarVerde."""


MENSAJES_DIARIOS = (
    ("¿Te haces un 3 de 3?", "Cada acierto le da 10 puntos a tu facultad."),
    ("¿Qué cambiarías en el campus?", "Tu voto cuenta y suma 5 puntos para tu unidad."),
    ("Una fuga deja pistas", "Si ves un grifo goteando, anota el edificio y el piso."),
    ("¿Quién va ganando?", "Mira qué unidad lidera la carrera por la Copa JaguarVerde."),
    ("Desbloquea tu primera insignia", "Completa el reto y revisa tu progreso en Comunidad."),
    ("Hoy toca mirar arriba", "¿Quedaron luces encendidas en un aula vacía? Ubica el lugar."),
    ("Un termo para el camino", "Si puedes, lleva tu botella reutilizable a la próxima clase."),
    ("Foto al problema", "Si haces un reporte, encuadra el lugar sin mostrar rostros."),
)


TIPOS_PUBLICACION = ("Mensaje", "Aviso", "Desafío", "Evento")


ENCUESTAS_SEMANALES = (
    {
        "pregunta": "¿Qué mejora te gustaría ver primero en el campus?",
        "opciones": ("Cuidar el agua", "Reducir residuos", "Ahorrar energía"),
    },
    {
        "pregunta": "¿Qué misión harías con tu grupo?",
        "opciones": ("Una semana con termo", "Detectar fugas", "Cuidar un área verde"),
    },
    {
        "pregunta": "¿Qué lugar merece una Ruta JaguarVerde?",
        "opciones": ("Baños y grifos", "Aulas y pasillos", "Áreas verdes"),
    },
)


EJEMPLOS_REPORTE = (
    {
        "titulo": "Goteo en un lavamanos",
        "categoria": "Agua",
        "ubicacion": "Edificio de ejemplo, baño del primer piso",
        "descripcion": "Ejemplo de cómo indicar el punto exacto y describir brevemente lo observado.",
    },
    {
        "titulo": "Luces encendidas en un aula vacía",
        "categoria": "Electricidad",
        "ubicacion": "Aula de ejemplo, segundo piso",
        "descripcion": "Ejemplo de reporte. No manipules interruptores dañados ni equipos eléctricos.",
    },
    {
        "titulo": "Contenedor lleno",
        "categoria": "Residuos sólidos",
        "ubicacion": "Pasillo de ejemplo, junto a la entrada",
        "descripcion": "Ejemplo: especifica qué ocurre y dónde, sin mover objetos potencialmente peligrosos.",
    },
)
