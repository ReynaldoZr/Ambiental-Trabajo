# JaguarVerde · versión 0.2

Prototipo web para Educación Ambiental. Permite reportar problemas ambientales del campus con foto, consultar su estado, completar retos semanales sobre agua, energía y residuos, ver un marcador anónimo por unidad académica y revisar un resumen seleccionable por semestre.

## Abrir en IntelliJ IDEA

1. En **File → Open**, abre la carpeta `JaguarVerde` (o la carpeta del repositorio clonado). Para usar el botón de ejecución, usa el complemento Python de IntelliJ y configura `.venv/Scripts/python.exe` como intérprete del proyecto si el IDE lo solicita.
2. Selecciona **JaguarVerde** en la lista de configuraciones y pulsa **Run**. También puedes iniciar el proyecto desde la terminal del IDE como se indica abajo.
3. Abre **http://127.0.0.1:5000** en el navegador. Esa dirección funciona en la misma computadora donde ejecutas el programa. Detén la aplicación con el botón Stop o Ctrl+C en la terminal.

## Preparar y ejecutar en Windows

Necesitas Windows, Python 3.12 y una conexión a Internet para instalar las dependencias la primera vez. IntelliJ IDEA es opcional; también puedes usar PowerShell.

En la terminal, entra a la carpeta del proyecto y prepara el entorno una sola vez:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Cada vez que quieras abrir JaguarVerde, ejecuta:

```powershell
.\.venv\Scripts\python.exe app.py
```

Cuando aparezca el mensaje de que Flask está ejecutándose, abre esta dirección en Chrome o en otro navegador de la misma computadora:

**http://127.0.0.1:5000**

La aplicación escucha solo en la computadora local; no está publicada para que otras personas entren desde sus dispositivos. Deja abierta la terminal mientras la usas. Para cerrar, vuelve a esa terminal y pulsa **Ctrl+C**.

Si `python` no se reconoce al preparar el entorno, instala Python 3.12 y activa la opción para agregarlo al PATH; después vuelve a abrir PowerShell. Si el puerto 5000 ya está ocupado, cierra la ejecución anterior de JaguarVerde y vuelve a iniciar el programa.

## Cómo probar el prototipo

Usa información inventada y una foto de prueba; no subas datos personales ni imágenes de personas.

1. En **Inicio**, contesta las tres preguntas del reto y elige una facultad. Comprueba que se muestre el puntaje y que aumente el marcador de esa semana.
2. Intenta contestar el mismo reto otra vez desde el mismo navegador. El sistema debe indicar que ya participaste en ese reto semanal.
3. En **Reportes**, crea un reporte ficticio con una foto JPG, PNG o WebP de hasta 5 MB. Anota el número del caso que aparece.
4. En **Administración**, busca ese caso, cambia su estado a **En proceso** o **Resuelto** y guarda una observación.
5. Regresa a **Reportes**, busca el caso y confirma que aparecen el nuevo estado, la observación y la fecha de actualización.
6. Abre **Campaña**, cambia el periodo y revisa el resumen de reportes, participación y puntos.
7. Reinicia la aplicación y confirma que el reporte y el marcador siguen guardados.

El reto se limita a un intento por navegador mediante una cookie. Borrar la cookie o usar otro navegador permite volver a participar, por eso los puntos son demostrativos y no certifican identidad, horas ni asistencia.

## Datos locales

La base de demostración se guarda en `instance/jaguarverde.sqlite`. La aplicación crea la carpeta y la base al iniciar; si ya existe una base de la versión 0.1, conserva los reportes y prepara el nuevo campo de seguimiento. Las fotos se guardan dentro de esa base. La clave de sesión también se crea en la carpeta local `instance/`. Estos archivos no se suben a GitHub.

Para empezar una demostración limpia, usa una copia nueva del proyecto o pide al equipo que te ayude a reiniciar los datos. No compartas la carpeta `instance/`: contiene la base local y las fotos de prueba.

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
