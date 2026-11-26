# JaguarVerde · versión 0.1

Prototipo web para Educación Ambiental. Permite reportar un problema del campus con una foto, actualizar su estado desde la vista de mantenimiento y consultar el resultado. En Inicio hay un consejo y un reto de tres preguntas sobre el agua.

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
2. En **Administración**, revisa la foto, marca el caso como **Resuelto** y guarda una observación.
3. Vuelve a **Reportes** para leer la respuesta. Vuelve a **Inicio** para ver el contador actualizado y probar el reto.
4. Reinicia la aplicación. El reporte, su estado y el resultado del reto siguen guardados.

La base de demostración se crea en `instance/jaguarverde.sqlite` y queda fuera de Git. Incluye las fotos normalizadas y el intento del reto. Las dos vistas se usan en el mismo equipo sin inicio de sesión. Usa datos ficticios.

## Dónde se hace cada cambio

| Archivo | Responsabilidad |
| --- | --- |
| `app.py` | Páginas, formularios y acciones del prototipo. |
| `datos.py` | Conexión y tablas de SQLite. |
| `campana.py` | Consejo, preguntas y respuestas del reto. |
| `templates/` y `static/` | Pantallas HTML y diseño visual. |

Lee [AGENTS.md](AGENTS.md) y [los acuerdos del equipo](docs/ACUERDOS.md) antes de preparar un cambio.
