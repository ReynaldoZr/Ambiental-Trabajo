"""Contenido breve que se rota en los retos semanales de JaguarVerde."""

from datetime import date


FACULTADES = (
    "UAM College",
    "Facultad de Odontología",
    "Facultad de Ciencias Médicas",
    "Facultad de Marketing, Diseño y Ciencias de la Comunicación",
    "Facultad de Ciencias Administrativas y Económicas",
    "Facultad de Ingeniería y Arquitectura",
    "Facultad de Ciencias Jurídicas, Humanidades y Relaciones Internacionales",
)

RETOS = (
    {
        "tema": "Agua",
        "titulo": "Cuidemos el agua",
        "consejo": "Una fuga pequeña también cuenta. Indica el edificio y el punto exacto para que mantenimiento pueda encontrarla.",
        "preguntas": (
            ("¿Qué haces si un grifo sigue goteando después de cerrarlo?",
             ("Lo reporto con una foto y la ubicación", "Lo dejo para fin de semestre", "Intento desmontarlo"), 0),
            ("¿Qué ubicación ayuda más a encontrar una fuga?",
             ("En el campus", "En un baño", "Baño del primer piso, junto a la entrada"), 2),
            ("¿Qué conviene hacer si el mismo incidente ya está reportado?",
             ("Mandarlo varias veces", "Consultar el estado del reporte existente", "Cambiarle el título y reenviarlo"), 1),
        ),
    },
    {
        "tema": "Energía",
        "titulo": "La energía también se cuida",
        "consejo": "Si ves luces o equipos encendidos en un espacio vacío, anota dónde ocurre y repórtalo; no manipules instalaciones.",
        "preguntas": (
            ("¿Qué situación conviene reportar?",
             ("Luces encendidas en un aula vacía", "Una luz encendida durante una clase", "Un equipo que está siendo utilizado"), 0),
            ("¿Qué información ayuda a ubicar el desperdicio?",
             ("Solo el nombre del edificio", "Edificio, piso y aula si se conocen", "Una opinión sobre el consumo"), 1),
            ("¿Qué debes hacer si el interruptor parece dañado?",
             ("Abrirlo para revisarlo", "Avisar con la ubicación", "Seguir probándolo muchas veces"), 1),
        ),
    },
    {
        "tema": "Residuos",
        "titulo": "Cada residuo en su lugar",
        "consejo": "Un contenedor lleno o residuos acumulados pueden reportarse con una ubicación concreta y una foto segura.",
        "preguntas": (
            ("¿Qué haces si un contenedor está desbordado?",
             ("Lo reporto e indico el punto", "Dejo la bolsa al lado", "Muevo los residuos a otro contenedor al azar"), 0),
            ("¿Qué dato facilita la atención?",
             ("El color del edificio", "La ubicación y el tipo de problema", "Cuántas personas pasaron"), 1),
            ("¿Qué haces si hay objetos peligrosos entre los residuos?",
             ("No los manipulo y aviso del lugar", "Los recojo sin protección", "Los escondo en otro recipiente"), 0),
        ),
    },
)


def obtener_reto_actual(hoy=None):
    """Rota un reto por semana ISO y devuelve un identificador único semanal."""
    hoy = hoy or date.today()
    anio, semana, _dia = hoy.isocalendar()
    indice = (semana - 1) % len(RETOS)
    reto = RETOS[indice].copy()
    reto["id"] = f"{anio}-S{semana:02d}"
    reto["semana"] = semana
    reto["periodo"] = f"Semana {semana} de {anio}"
    return reto
