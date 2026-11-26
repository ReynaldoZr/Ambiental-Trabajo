# JaguarVerde · versión 0.5 local

Prototipo web local para Educación Ambiental. Incluye mensajes de bienvenida, retos y encuestas rápidas, insignias, marcador por unidad y una Copa JaguarVerde de cierre de semestre. También permite enviar reportes y seguir su estado. Administración programa avisos y eventos desde el Muro.

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

1. En **Participar**, registra un estudiante de prueba con nombre, facultad y carrera.
2. Abre **Inicio**. La bienvenida cambia al volver y puedes pulsar **Otra misión**. A su lado, abre una tarjeta para ver los detalles del evento. **Ver agenda** abre `/agenda`, donde puedes filtrar eventos por actividad u horas y guardar tus favoritos en el navegador.
3. En **Inicio**, contesta el reto semanal: cada acierto da 10 puntos. Vota en la encuesta semanal de Comunidad para sumar 5 puntos más. Cada perfil tiene un intento y un voto por semana.
4. En **Reportes**, crea un reporte ficticio con una foto JPG, PNG o WebP de hasta 5 MB.
5. Usa **Cambiar estudiante** y registra un segundo perfil de prueba. En **Mis reportes** debe aparecer solo lo enviado desde ese segundo perfil, no el reporte del primero.
6. Cambia de perfil nuevamente y entra por **Acceso administrador** con el usuario y la contraseña local indicados abajo.
7. En **Administración**, revisa estudiantes y reportes. Abre **Gestionar muro** para crear un mensaje, aviso, desafío o evento; asigna fecha de publicación y, para eventos, fecha, lugar, tipo de actividad, horas autorizadas por colaborar y reconocimiento propuesto. Oculta o reactiva publicaciones cuando sea necesario.
8. Cierra la sesión de administración y visita **Comunidad** para ver las publicaciones visibles. Abre **Campaña** para revisar las cifras agregadas.

La identificación estudiantil es autodeclarada y no verifica que una persona pertenezca a la universidad. Borrar la cookie o crear otro registro permite participar más de una vez; por eso los puntos son demostrativos y no certifican identidad, horas ni asistencia. La administración requiere una contraseña local; su hash se guarda fuera de Git.

## Incentivo de participación

- Cada respuesta correcta del reto suma **10 puntos**; votar en la encuesta semanal suma **5**, sin respuestas incorrectas.
- Insignias personales: **Primer reto**, **Racha verde** (tres retos), **Voz del campus** (tres encuestas) y **Ojos Jaguar** (primer reporte).
- Al cierre del semestre, la unidad líder gana la **Copa JaguarVerde**: insignia digital, mención en el Muro y espacio para presentar una idea en un encuentro integrado a una actividad UAM existente.
- Un kit reutilizable o una planta puede proponerse como premio físico, pero solo se anuncia si la UAM lo aprueba. Los puntos no se canjean por horas, becas ni servicios.

La agenda agrega eventos de muestra de campus, cine, deporte, trueque y voluntariado por única vez, aun si el Muro ya tiene otras publicaciones. Se identifican como propuestas por confirmar y se pueden ocultar desde Administración. Los eventos vigentes publicados por administración aparecen primero. Los ejemplos de reportes rellenan el formulario para enseñar el formato; hay que sustituirlos por observaciones reales antes de enviar.

## Accesos del prototipo

- **Estudiantes:** abre `http://127.0.0.1:5000/estudiantes/entrar`, escribe nombre completo, facultad y carrera, y luego podrás responder retos y enviar reportes. La sesión se conserva en ese navegador hasta 30 días; **Cambiar estudiante** permite usar otro perfil en el mismo equipo.
- **Administración:** abre `http://127.0.0.1:5000/administracion/entrar`. El único usuario inicial es `admin`. Al preparar por primera vez la versión local, la contraseña aleatoria se guarda en `instance/acceso_administrador.txt`. El archivo se excluye de Git; no lo envíes ni lo compartas.
- **Comunidad:** abre `http://127.0.0.1:5000/comunidad` para ver el mensaje de esta visita, los avisos, desafíos, eventos próximos y el marcador semanal.
- **Gestionar el Muro:** inicia sesión como administrador y abre `http://127.0.0.1:5000/administracion/muro`. Programa mensajes, avisos y desafíos; en eventos indica fecha, lugar y reconocimiento propuesto. Las publicaciones pueden ocultarse y volver a mostrarse.
- Administración muestra los datos personales de los registros estudiantiles y todos los reportes. Los estudiantes solo ven los reportes enviados desde su perfil. La página Campaña presenta cifras agregadas.

Este es un prototipo local para una demostración con datos ficticios. No hay verificación de cuentas estudiantiles, recuperación de contraseña ni publicación de red. Antes de usarlo con estudiantes reales, la universidad debe aprobar el propósito, los datos solicitados, privacidad, responsables y forma de validar identidades.

## Datos locales

La base de demostración se guarda en `instance/jaguarverde.sqlite`. La aplicación crea la carpeta y la base al iniciar; si ya existe una base anterior, conserva sus datos y agrega las tablas de encuesta y publicaciones. Si el Muro está vacío, añade una muestra etiquetada con fecha relativa al día de inicio. Las fotos se guardan dentro de la base. La clave de sesión, el hash del administrador y el acceso inicial se crean localmente en `instance/`; esos archivos no se suben a GitHub.

Para empezar una demostración limpia, usa una copia nueva del proyecto o pide al equipo que te ayude a reiniciar los datos. No compartas la carpeta `instance/`: contiene la base local, las fotos de prueba y el acceso local de administración.

## Recorrido para la defensa

1. Desde Inicio, elige **Reportar un problema**. Crea un caso ficticio con una foto JPG, PNG o WebP de hasta 5 MB.
2. En **Administración**, revisa la foto, cambia el estado y guarda una observación.
3. Vuelve a **Reportes** para consultar el estado y la fecha de actualización. En **Inicio**, completa el reto semanal; en **Comunidad**, responde la encuesta para sumar 5 puntos más.
4. Abre **Campaña** para ver el resumen y la unidad que va al frente de la Copa JaguarVerde en el periodo elegido.
5. Reinicia la aplicación. Los reportes, sus estados y las participaciones del reto siguen guardados.

La base local se crea en `instance/jaguarverde.sqlite` y queda fuera de Git. Incluye fotos normalizadas, perfiles estudiantiles y participaciones del reto. Una cookie firmada conserva el perfil seleccionado en ese navegador por hasta 30 días. No hay verificación de identidad estudiantil; el marcador es demostrativo y no acredita asistencia ni horas. Usa datos ficticios.

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
