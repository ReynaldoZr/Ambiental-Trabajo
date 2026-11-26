# Acuerdos del grupo

## Versión 0.5 local

**Objetivo.** Mostrar el recorrido básico de reporte y respuesta, dar razones rápidas para volver a la plataforma y hacer visible la participación colectiva sin convertirla en trabajo obligatorio.

| Tema | Acuerdo para la demostración |
| --- | --- |
| Nombre | JaguarVerde, como en la propuesta de la asignatura. EcoReport U fue la referencia de requisitos de reportes. |
| Alcance | Inicio, Comunidad, Campaña, Reportes y Administración. Siete categorías de incidencias; foto obligatoria; seguimiento con estado, fecha y observación. |
| Datos | Una base local SQLite. Fotos normalizadas, perfiles estudiantiles y participaciones quedan guardadas en la base local, fuera de Git. Se usan datos ficticios. |
| Estudiantes | Registro de demostración con nombre, facultad y carrera. El registro es autodeclarado, no lleva contraseña y no verifica identidad. Cada perfil consulta solo sus reportes. |
| Administración | Un solo usuario local `admin`, con contraseña aleatoria inicial cuyo hash se guarda fuera de Git. Administración muestra todos los reportes y perfiles y permite actualizar estados. |
| Retos y encuesta | Reto de tres preguntas rota semanalmente; cada acierto da 10 puntos. Una encuesta rápida por semana da 5 puntos por votar y sus resultados orientan actividades futuras. Solo se admite un voto por perfil y semana. |
| Muro | Al volver a Inicio aparece un mensaje distinto, que se conserva al navegar por Comunidad. Comunidad muestra avisos, desafíos, encuestas, eventos, progreso e insignias. Administración programa publicaciones, fecha y lugar de evento, y reconocimiento propuesto; puede ocultar o reactivar contenido. |
| Incentivo | La Copa JaguarVerde se decide con puntos del reto y la encuesta al cierre del semestre. La unidad líder recibe insignia digital, mención en el Muro y espacio para presentar una idea en una actividad UAM existente. Un kit reutilizable o planta es opcional y solo se anuncia si la UAM lo aprueba. No hay canje por horas, becas ni servicios. |
| Marcador | Puntos del reto y la encuesta agrupados por unidad. Un mismo perfil solo registra un intento y un voto por semana; se pueden crear perfiles no verificados, por lo que el marcador es simbólico y no acredita participación real. |
| Agenda | Los eventos indican la actividad y las horas autorizadas por colaborar. La etiqueta Muestra distingue horas ilustrativas. Los favoritos se guardan en el navegador. |
| Misión | La práctica da retroalimentación inmediata. El modo más votado por estudiantes se muestra la semana siguiente. |
| Datos de muestra | Inicio muestra hasta dos eventos al lado de la bienvenida, con los eventos publicados vigentes primero. La Ruta y la Final de la Copa aparecen como muestras por confirmar y se pueden ocultar. Si el Muro está vacío, también se agrega un aviso, un mensaje y un desafío. |
| Resumen | Consultable por semestre. Muestra reportes por estado y categoría, respuestas al reto y la encuesta, y puntos por unidad. No estima litros o energía ahorrados sin método validado. |
| Actividades | Retos digitales automáticos semanalmente; como máximo una actividad presencial principal por semestre, integrada a un evento UAM ya programado; publicación del resumen al cierre de cada semestre. |
| Beneficios | Participación voluntaria, aprendizaje, respuesta visible, identidad de facultad y reconocimiento simbólico. Los puntos no se canjean por horas laborales, becas ni servicio social en este prototipo. |
| Calendario | El prototipo divide el año en enero-junio y julio-diciembre solo para agrupar datos. La universidad debe ajustar los periodos a su calendario académico antes de un piloto. |
| Entrega | Demo local desde IntelliJ IDEA o su terminal. El código se comparte en GitHub mediante un PR. |

La versión 0.5 se ejecuta en local. El repositorio comparte el código y las instrucciones de arranque.

## Plan sencillo para la universidad

- El grupo prepara o revisa un banco pequeño de preguntas y consejos; el sitio cambia el reto cada semana sin que la universidad organice una actividad cada semana.
- Al inicio del semestre, Vida Estudiantil o Educación Ambiental confirma una facultad anfitriona, una fecha que ya exista en el calendario y la persona de contacto de mantenimiento.
- Una vez por semestre, la facultad anfitriona puede hacer la Ruta JaguarVerde: puesto con QR, recorrido voluntario de 45 minutos y registro de hallazgos en la plataforma. No requiere sensores ni compras.
- Al cierre del semestre, compartir el resumen y reconocer una idea o a la unidad más activa con una mención o exposición breve. La respuesta a cada reporte depende de la revisión y capacidad del área responsable.
- Antes de publicar información, confirmar qué reportes pueden verse públicamente. Para uso real hacen falta cuentas o un método acordado de validación, privacidad y acceso institucional.

## Cómo acordar un cambio

Anotar la fecha, la fuente o el enlace a la issue, qué cambia, por qué y quién lo acordó. Indicar qué parte de la demostración afecta y dejar las ideas que puedan esperar en una tarea aparte. Para la entrega académica, seguir la consigna de la profesora. La propuesta JaguarVerde, los requisitos de EcoReport U y las conversaciones del equipo sirven de referencia para ajustar el alcance.

## Fuentes de contexto

- Propuesta académica JaguarVerde, apartados 3 a 6. Reportes, siete categorías, boletín, retos interfacultades y beneficios institucionales.
- [Programas académicos de la UAM](https://www.uam.edu.ni/). Nombres de facultades y UAM College usados como unidades académicas seleccionables en el prototipo.
- Prompt de EcoReport U. Requisitos de una versión más amplia, de los que se eligió el recorrido básico.
- [Reglas de la calculadora](https://github.com/ReynaldoZr/AlgebraCalcuadora/blob/main/AGENTS.md). Referencia del flujo de revisión en GitHub.

El usuario es quien revisa y decide sobre los cambios. No se debe esperar ni solicitar aprobación adicional de otro integrante, excepto si el usuario la pide. Publicar o integrar cambios cuando el usuario lo autorice expresamente en la tarea; no cambiar protecciones del repositorio por iniciativa propia.
