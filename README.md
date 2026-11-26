# JaguarVerde · versión 0.2

Prototipo web para Educación Ambiental. Permite reportar problemas ambientales del campus con foto, consultar su estado, completar retos semanales sobre agua, energía y residuos, ver un marcador anónimo por unidad académica y revisar un resumen seleccionable por semestre.

## Abrir en IntelliJ IDEA

1. En **File → Open**, abre la carpeta `JaguarVerde` (o la carpeta del repositorio clonado). Para usar el botón de ejecución, usa el complemento Python de IntelliJ y configura `.venv/Scripts/python.exe` como intérprete del proyecto si el IDE lo solicita.
2. Selecciona **JaguarVerde** en la lista de configuraciones y pulsa **Run**. También puedes iniciar el proyecto desde la terminal del IDE como se indica abajo.
3. Abre **http://127.0.0.1:5000** en el navegador. Detén la aplicación con el botón Stop o Ctrl+C en la terminal.

En una copia nueva, prepara el entorno en la terminal de IntelliJ (Windows, Python 3.12):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Para ejecutar desde esa misma terminal:

```powershell
.\.venv\Scripts\python.exe app.py
```

## Recorrido para la defensa

1. Desde Inicio, elige **Reportar un problema**. Crea un caso ficticio con una foto JPG, PNG o WebP de hasta 5 MB.
2. En **Administración**, revisa la foto, cambia el estado y guarda una observación.
3. Vuelve a **Reportes** para consultar el estado y la fecha de actualización. En Inicio, completa el reto y elige una unidad académica; cada acierto suma 10 puntos al marcador de esa semana.
4. Abre **Campaña** para ver los datos del semestre elegido y la propuesta de actividades universitarias.
5. Reinicia la aplicación. Los reportes, sus estados y las participaciones del reto siguen guardados.

La base local se crea en `instance/jaguarverde.sqlite` y queda fuera de Git. Incluye fotos normalizadas y participaciones del reto. Una cookie aleatoria permite que el mismo navegador participe una vez por reto semanal; no se guarda nombre ni correo. Sin inicio de sesión ni validación institucional, el marcador es una demostración: no acredita identidad, asistencia ni horas. Usa datos ficticios.

El resumen muestra reportes por estado y categoría, y puntos de retos por unidad académica. No estima ahorros de agua o energía porque todavía no existe un método validado para calcularlos. El calendario sugerido de retos, actividades y cierres semestrales está en [el plan de campaña](docs/CAMPANA_ANUAL.md). Los periodos enero-junio y julio-diciembre son una convención del prototipo; deben ajustarse al calendario académico de la UAM antes de un piloto.

## Dónde se hace cada cambio

| Archivo | Responsabilidad |
| --- | --- |
| `app.py` | Páginas, formularios y acciones del prototipo. |
| `datos.py` | Conexión, migración y tablas de SQLite. |
| `campana.py` | Facultades, preguntas y consejos de los retos rotativos. |
| `templates/` y `static/` | Pantallas HTML y diseño visual. |
| `docs/CAMPANA_ANUAL.md` | Cadencia ligera de retos, actividades y resumen semestral. |

Lee [AGENTS.md](AGENTS.md) y [los acuerdos del equipo](docs/ACUERDOS.md) antes de preparar un cambio.
