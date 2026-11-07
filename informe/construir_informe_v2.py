"""Versión sencilla del informe (estilo documento de Word, primera persona, menos tablas).

Uso:  python3 informe/construir_informe_v2.py   y luego   node informe/imprimir.js v2
"""
import re
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
IMG = RAIZ / "modelos" / "imagenes"
CAP = DOCS / "ai-studio" / "capturas"
CAPB = DOCS / "ai-studio" / "capturas-build"
REPO = "https://github.com/juanvs1985/sga-arquitectura"
AISTUDIO = ("https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221NcbJ3YkHGzE2xID9EykCrpI4RXmgqqe8"
            "%22%5D,%22action%22:%22open%22,%22userId%22:%22113748348275050694995%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing")
YOUTUBE = "https://youtu.be/XETzIcJ7SuE"
FECHA = "8 de noviembre de 2026"

partes = []
P = partes.append


def md(t):
    return markdown.markdown(t, extensions=["tables", "sane_lists"])


def h(n, t, nonum=False):
    return f'<h{n}{" class=\"nonum\"" if nonum else ""}>{t}</h{n}>'


def fig(n, titulo, src, nota, ancho="100%", horizontal=False):
    html = (f'<figure class="fig"><p class="fig-num">Figura {n}</p><p class="fig-tit">{titulo}</p>'
            f'<img src="{src}" style="width:{ancho}"><p class="fig-nota"><em>Nota.</em> {nota}</p></figure>')
    return f'<section class="horizontal">{html}</section>' if horizontal else html


# ------------------------------------------------------------ portada
video_txt = YOUTUBE if YOUTUBE else "[pendiente]"
P(f"""<section class="portada">
<p>Corporación Unificada Nacional de Educación Superior – CUN</p>
<p>Ingeniería de Sistemas</p>
<p class="espacio">Arquitectura de Software (INGS0763)</p>
<p class="titulo">Diseño de la arquitectura de un sistema de gestión académica mediante Google AI Studio</p>
<p class="espacio">Juan Pablo Vargas Sánchez</p>
<p>Docente: Alexander Calderón Martínez</p>
<p class="espacio">{FECHA}</p>
<p class="enlaces">Video: <span class="{'' if YOUTUBE else 'pendiente'}">{video_txt}</span><br>Repositorio: {REPO}</p>
</section>""")
P('<section class="toc-pagina"><h2 class="nonum">Contenido</h2><ol id="toc"></ol></section>')

# ------------------------------------------------------------ 1
P(h(2, "Introducción y descripción del problema"))
P(md("""
La institución de educación superior del caso maneja la información de estudiantes, docentes, programas, asignaturas, grupos, matrículas, notas y horarios en archivos y aplicaciones que no están conectados entre sí. Eso trae tres problemas: hay datos duplicados que no coinciden, las consultas son lentas porque toca buscar en varios lados, y no queda registro de quién cambió una nota, una matrícula o un rol.

En este trabajo propongo la arquitectura de software de un sistema de gestión académica (SGA) que reúna toda esa información en un solo lugar, se use desde el navegador y controle el acceso según el rol de cada usuario. Parto de los 12 requerimientos funcionales y 12 no funcionales del enunciado y llego a una arquitectura, cinco decisiones documentadas y seis modelos del sistema.

Para el diseño usé Google AI Studio (Gemini 3.8 Flash) como apoyo en siete pasos, y luego AI Studio Build para generar un prototipo navegable. No acepté todo lo que propuso la IA: en la sección 9 explico qué tomé, qué cambié y qué descarté, y por qué.

Es importante aclarar que, como dice el enunciado, no se implementó el sistema. Todo lo que describo aquí es diseño propuesto; el prototipo de Build es una maqueta con datos simulados y no la implementación de esta arquitectura.
"""))

# ------------------------------------------------------------ 2
P(h(2, "Objetivos"))
P(md("""
### Objetivo general

Diseñar y justificar la arquitectura de software de un sistema de gestión académica seguro, mantenible, escalable y accesible desde la web, a partir de sus requerimientos, usando Google AI Studio de forma crítica.

### Objetivos específicos

1. Analizar el caso y escribir los requerimientos con criterios que se puedan verificar, junto con actores, supuestos, restricciones y reglas de negocio.
2. Escoger un estilo arquitectónico y justificarlo frente a otras opciones.
3. Representar el sistema con los modelos de casos de uso, componentes, despliegue, datos y secuencia.
4. Relacionar cada requerimiento con los componentes que lo cumplen y con la forma de comprobarlo.
5. Identificar riesgos y puntos únicos de falla, y proponer cómo validar las decisiones más críticas.
6. Documentar cómo usé AI Studio y qué hice con cada una de sus respuestas.
"""))

# ------------------------------------------------------------ 3
P(h(2, "Alcance, actores, supuestos y restricciones"))
P(md("""
### Alcance

El trabajo cubre los 24 requerimientos del enunciado, el diseño de la arquitectura con sus modelos, las decisiones, los riesgos y la evaluación del uso de la IA. Quedan por fuera la implementación, el diseño detallado de las pantallas, la integración real con otros sistemas de la institución (solo dejo la API preparada), y cosas que ningún requerimiento pide, como prerrequisitos de asignaturas o notificaciones por correo.

### Actores

- **Administrador:** maneja usuarios, roles y permisos; registra y desactiva estudiantes y docentes; consulta la auditoría.
- **Coordinador académico:** maneja programas, planes, asignaturas, periodos y grupos; asigna docentes, matricula estudiantes y saca reportes.
- **Docente:** consulta sus grupos, registra y publica notas.
- **Estudiante:** consulta sus asignaturas, su horario y sus notas publicadas.

Como actores secundarios están el servicio de copias de seguridad y, más adelante, otras plataformas de la institución que podrían usar la API.

### Supuestos

Como el caso no dice todo, tuve que asumir algunas cosas:

1. La matrícula la registra el coordinador. Dejar que el estudiante se matricule solo queda como una mejora futura.
2. "Desactivar" un estudiante o docente significa cambiarle el estado, no borrarlo, para no perder el historial.
3. Las notas tienen dos estados, borrador y publicada; el estudiante solo ve las publicadas.
4. Un usuario puede tener más de un rol (por ejemplo, un docente que también coordina) y escoge con cuál trabaja al entrar.
5. El escenario de referencia es de 300 usuarios al mismo tiempo, con picos en semanas de matrícula y cierre de notas.
6. El presupuesto de la institución es moderado.

### Restricciones

La aplicación tiene que ser web y funcionar en navegadores recientes, en computador y celular. Todo el tráfico va por HTTPS, las contraseñas se guardan con hash y nunca en texto plano, y las interfaces se exponen como API REST documentada. La disponibilidad mensual debe ser de al menos 99,5 %, lo que deja como máximo unas 3,6 horas de caída no programada al mes. Y por el enunciado, no se deben usar datos personales reales en prompts, capturas ni en el repositorio.
"""))

# ------------------------------------------------------------ 4
P(h(2, "Requerimientos funcionales y no funcionales"))
P(md("""
Para cada requerimiento escribí un criterio de aceptación, es decir, cómo sabría uno que se cumple. Esto me sirvió después para revisar lo que proponía la IA.

### Requerimientos funcionales

| Id | Requerimiento | Actor | Cómo se comprueba |
|---|---|---|---|
| RF-01 | Autenticación | Todos | Con credenciales válidas entra; con inválidas no; al cerrar sesión el token deja de servir |
| RF-02 | Roles y permisos | Administrador | Un estudiante que llama una función de docente recibe "sin permiso" (403) |
| RF-03 | Gestión de estudiantes | Administrador, coordinador | Se crea, edita y desactiva; el desactivado no se puede matricular |
| RF-04 | Gestión de docentes | Administrador, coordinador | Igual al anterior; el desactivado no se puede asignar a un grupo |
| RF-05 | Programas y asignaturas | Coordinador | No deja crear dos asignaturas con el mismo código |
| RF-06 | Grupos y periodos | Coordinador | Se crea el grupo con cupo, docente, horario y aula o enlace |
| RF-07 | Matrícula | Coordinador | Con cupo y sin duplicado matricula; si no, rechaza con el motivo |
| RF-08 | Calificaciones | Docente | Solo registra notas en sus grupos |
| RF-09 | Consulta de resultados | Estudiante | Ve su horario y solo las notas publicadas |
| RF-10 | Reportes | Coordinador, administrador | El reporte por periodo y programa coincide con los datos |
| RF-11 | Búsqueda y filtros | Usuarios autorizados | Busca por código, nombre, programa, periodo o estado según el rol |
| RF-12 | Auditoría | Administrador | Cada login, cambio de rol, matrícula y cambio de nota queda registrado |

### Requerimientos no funcionales

| Id | Requerimiento | Cómo se mide |
|---|---|---|
| RNF-01 | Seguridad | Todo por HTTPS, contraseñas con Argon2id, acceso por rol |
| RNF-02 | Rendimiento | Con 300 usuarios, el 95 % de las consultas comunes en 3 s o menos |
| RNF-03 | Disponibilidad | 99,5 % mensual |
| RNF-04 | Escalabilidad | Agregar servidores sin cambiar el código |
| RNF-05 | Mantenibilidad | Cambiar una regla de notas solo toca el módulo de calificaciones |
| RNF-06 | Usabilidad y accesibilidad | Se puede usar con teclado; buen contraste (WCAG 2.1 AA) |
| RNF-07 | Integridad | Dos solicitudes por el último cupo dejan una sola matrícula |
| RNF-08 | Interoperabilidad | API REST documentada con OpenAPI |
| RNF-09 | Respaldo | Pérdida máxima de 15 min de datos y recuperación en menos de 2 h |
| RNF-10 | Trazabilidad | Cada requerimiento aparece en la matriz con su componente |
| RNF-11 | Privacidad | Un estudiante no puede ver los datos de otro |
| RNF-12 | Compatibilidad | Funciona en Chrome, Edge, Firefox y Safari, en celular y computador |

### Reglas de negocio

Del análisis salieron reglas que el sistema tiene que validar en la lógica de negocio y no solo en la pantalla. Las más importantes son:

1. Un estudiante no puede quedar dos veces en el mismo grupo, ni en dos grupos de la misma asignatura en el mismo periodo.
2. No se puede matricular en un grupo sin cupo. Si llegan dos solicitudes al mismo tiempo por el último cupo, solo una puede quedar.
3. Solo se matricula en periodos abiertos y dentro de las fechas; solo estudiantes activos.
4. No se permite cruce de horario, ni para el estudiante ni para el docente.
5. El docente solo pone notas a estudiantes de sus grupos, entre 0,0 y 5,0.
6. Cuando el coordinador cierra las notas del periodo, el docente ya no puede cambiarlas.
7. Si se cambia una nota ya publicada, queda en la auditoría con el valor anterior, el nuevo y una justificación.
8. Cada quien ve solo lo suyo: el estudiante sus datos, el docente sus grupos.
9. En un grupo presencial el cupo no puede ser mayor que la capacidad del aula.
10. Los registros de auditoría no se pueden modificar ni borrar.

Algunas de estas reglas no las tenía al principio y salieron de las respuestas de la IA (las fechas, el cierre de notas, el cruce de horario y la capacidad del aula).

### Análisis

Al revisar los requerimientos me di cuenta de que no todos pesan igual. Los que realmente definen la arquitectura son la disponibilidad (RNF-03), la mantenibilidad (RNF-05) y sobre todo la integridad de la matrícula (RNF-07); los demás se resuelven con medidas puntuales. El RNF-09 no daba cifras, así que propuse una pérdida máxima de 15 minutos de datos y 2 horas para recuperar el servicio. Al inicio había puesto 24 horas y 4 horas, pero lo bajé después de ver la propuesta de la IA, porque los servicios de base de datos administrados ya traen recuperación a un punto en el tiempo.
"""))

# ------------------------------------------------------------ 5
P(h(2, "Arquitectura seleccionada y justificación"))
P(md("""
Escogí un **monolito modular en capas**. Es una sola aplicación, pero dividida en seis módulos según el área del negocio: identidad y acceso, gestión académica, matrículas, calificaciones, reportes y auditoría. Cada módulo tiene sus tres capas (controlador, dominio y repositorio), solo se comunica con los demás a través de interfaces y tiene su propio esquema dentro de una misma base de datos PostgreSQL. La aplicación se expone como una API REST y se despliega en dos servidores detrás de un balanceador.

### Opciones que comparé

Comparé tres opciones: capas sin módulos, monolito modular y microservicios.

| Criterio | Capas sin módulos | Monolito modular | Microservicios |
|---|---|---|---|
| Consistencia de la matrícula | Buena (una transacción) | Buena (una transacción) | Difícil: cada servicio con su base, riesgo de sobrecupo |
| Rendimiento con 300 usuarios | Suficiente | Bueno, llamadas en memoria | Latencia por la red |
| Mantenibilidad | Se va enredando con el tiempo | Buena, módulos separados | Buena por servicio, pero contratos complejos |
| Costo y operación | Bajo | Bajo | Alto |

### Por qué esta y no microservicios

La razón principal es la matrícula. Es el requisito más delicado: dos estudiantes no pueden quedarse con el mismo último cupo. Con una sola base de datos eso se resuelve con una transacción; con microservicios cada servicio tendría su base y habría que coordinarlos con consistencia eventual, lo que abre la puerta al sobrecupo.

Además, 300 usuarios concurrentes no es una carga tan grande: dos servidores alcanzan y se puede agregar un tercero sin tocar el código. Y para la mantenibilidad no hace falta partir el sistema en servicios; basta con que los módulos tengan límites claros. A eso se suma que el presupuesto es moderado y el equipo es pequeño.

No escogí solo capas porque las capas por sí solas no evitan que la lógica de matrícula, notas y auditoría termine mezclada. Los módulos ponen esos límites.

Si en el futuro algún módulo necesita crecer aparte, ya tiene su interfaz y su esquema, así que se podría sacar como un servicio poco a poco (patrón Strangler Fig).

La IA recomendó el mismo estilo cuando se lo pregunté, pero planteaba capas y módulos como opciones excluyentes. Para mí se complementan: módulos por fuera y capas por dentro.
"""))

# ------------------------------------------------------------ 6 modelos
P(h(2, "Modelo del sistema"))
P(md("Hice los diagramas en Mermaid y el de casos de uso con un script que genera SVG; los archivos fuente están en el repositorio, en la carpeta `modelos/fuentes`. En todos usé los mismos nombres de actores, módulos y entidades."))

P(h(3, "Casos de uso"))
P(md("""
El diagrama muestra los cuatro actores y 15 casos de uso. Hay un caso interno, *registrar evento de auditoría*, que no tiene actor: lo incluyen siempre los casos que hay que auditar (iniciar sesión, gestionar roles, matricular y registrar notas), y así se cumple el RF-12.

Los casos más importantes son:

- **Matricular estudiante (CU-07):** el coordinador inscribe a un estudiante en uno o varios grupos; el sistema revisa cupo, duplicados, cruce de horario y fechas.
- **Registrar calificaciones (CU-08) y publicarlas (CU-09):** el docente pone las notas en borrador y luego las publica para que el estudiante las vea.
- **Cerrar notas del periodo (CU-10):** el coordinador bloquea la edición de notas.
- **Consultar horario y notas (CU-11):** el estudiante ve solo lo suyo.
- **Consultar auditoría (CU-14):** solo el administrador.
"""))
P(fig(1, "Diagrama de casos de uso", str(IMG / "01-casos-de-uso.svg"),
      "Elaboración propia.", horizontal=True))

P(h(3, "Componentes (vista lógica)"))
P(md("""
En la figura 2 están los seis módulos con su ruta REST. Las flechas indican qué módulo usa a cuál, y la etiqueta es la interfaz que usa. Ningún módulo entra a las tablas de otro; si necesita algo, lo pide por la interfaz.
"""))
P(fig(2, "Módulos, interfaces y dependencias", str(IMG / "02a-componentes-modulos.svg"), "Elaboración propia.", ancho="70%"))
P(md("""
En resumen, cada módulo hace lo siguiente:

- **Identidad y acceso** maneja usuarios, contraseñas, roles e inicio y cierre de sesión. Le da a los demás la interfaz `IContextoSeguridad` (quién es el usuario y con qué rol está).
- **Gestión académica** maneja estudiantes, docentes, programas, planes, asignaturas, periodos, grupos, horarios y aulas. Expone `IConsultaAcademica` para que otros pregunten, por ejemplo, si un estudiante está activo.
- **Matrículas** hace la matrícula con todas las validaciones dentro de una transacción. Es dueño de la tabla de cupos y expone `IConsultaMatriculas`.
- **Calificaciones** registra, publica y corrige notas, revisando que el docente sea el del grupo y que las notas no estén cerradas.
- **Reportes** solo lee, a través de vistas de la base de datos con un usuario que no puede escribir.
- **Auditoría** guarda los eventos y solo los deja consultar al administrador. Expone `IRegistroAuditoria`.

La búsqueda y los filtros (RF-11) van en los listados de cada módulo, y siempre se aplica lo que el rol puede ver. Todos los endpoints se documentarían con OpenAPI.

Por dentro, todos los módulos tienen la misma estructura de tres capas (figura 3): el controlador recibe la petición, el dominio tiene las reglas y el repositorio habla con la base de datos. El dominio solo conoce el contrato del repositorio, no la base de datos, así que se podría cambiar la base sin tocar las reglas.
"""))
P(fig(3, "Estructura interna de un módulo (matrículas)", str(IMG / "02b-componentes-capas-modulo.svg"), "Elaboración propia.", ancho="58%"))

P(h(3, "Despliegue"))
P(md("""
Para el despliegue (figura 4) busqué que no hubiera un solo punto que tumbara todo el sistema, pero sin irme a algo costoso como Kubernetes en varias regiones.

Delante va Cloudflare, en su plan gratuito, que se encarga del certificado HTTPS, de frenar ataques y de servir la interfaz web. La API corre en dos contenedores Docker en una red privada, detrás del balanceador del proveedor. Si uno se cae, el otro sigue atendiendo. La base de datos es un PostgreSQL administrado con una réplica en otra zona que toma el control sola si falla la principal. Los respaldos se hacen todos los días y además se guarda el registro continuo de cambios (WAL), cifrado y en otra región. Las contraseñas de la base y las llaves de los tokens no van en el código: se guardan en un gestor de secretos. Y hay un monitor externo que avisa si el sistema se cae.
"""))
P(fig(4, "Nodos, canales y seguridad", str(IMG / "03-despliegue.svg"), "Elaboración propia.", ancho="72%"))

P(h(3, "Modelo de datos"))
P(md("""
La figura 5 muestra las entidades y cómo se relacionan. Cada una pertenece al esquema de un módulo: Usuario, Rol y Sesión a identidad; Estudiante, Docente, Programa, Plan de estudio, Asignatura, Periodo, Grupo, Horario y Aula a gestión académica; Matrícula, Detalle de matrícula y Cupo de grupo a matrículas; Evaluación y Calificación a calificaciones; y Evento de auditoría a auditoría.

Algunas relaciones que vale la pena explicar:

- Usuario y Rol es de muchos a muchos, porque un mismo usuario puede tener varios roles.
- La matrícula es una por estudiante y periodo, y tiene un detalle por cada grupo.
- Cada grupo tiene sus evaluaciones (por ejemplo, Parcial 1 con 30 %) y la nota de cada estudiante se guarda por evaluación.
- El cupo ocupado no está en Grupo sino en Cupo de grupo, que es del módulo de matrículas.

Para que no haya duplicados ni sobrecupo, aunque falle el código, la base de datos tiene restricciones: una matrícula por estudiante y periodo, no repetir grupo ni asignatura dentro de la misma matrícula, y que los ocupados nunca pasen del cupo máximo. Los atributos completos de cada entidad están en el modelo detallado del repositorio.
"""))
P(fig(5, "Entidades principales y cardinalidades", str(IMG / "04b-datos-entidades.svg"),
      "Notación de pata de gallo. Elaboración propia.", horizontal=True))

P(h(3, "Secuencia de la matrícula"))
P(md("""
Escogí modelar la matrícula porque es el proceso más delicado. En la figura 6 se ve el flujo completo:

Primero el pipeline de seguridad revisa el token y el rol. Después, antes de bloquear nada, el sistema valida lo que no depende del cupo: que el estudiante esté activo, que el periodo esté abierto y que no haya cruce de horario. Ahí sí abre una transacción y bloquea solo la fila del cupo de ese grupo (`SELECT ... FOR UPDATE`). Si no hay cupo o ya tiene la asignatura, deshace todo y responde con un error 409. Si hay cupo, guarda la matrícula, suma uno a los ocupados y escribe la auditoría, todo en la misma transacción.
"""))
P(fig(6, "Flujo de la matrícula", str(IMG / "05a-secuencia-matricula.svg"), "Elaboración propia.", horizontal=True))
P(md("""
La figura 7 muestra el caso que más me preocupaba: dos solicitudes al mismo tiempo por el último cupo. La primera toma el bloqueo; la segunda espera. Cuando la primera termina, la segunda ve que ya no hay cupo y se rechaza. El grupo nunca queda con 31 de 30. Cuando se matriculan varios grupos a la vez, los bloqueos se toman en orden para evitar que dos solicitudes se queden esperándose entre sí; esa idea la tomé de la IA.
"""))
P(fig(7, "Dos solicitudes por el último cupo", str(IMG / "05b-secuencia-concurrencia.svg"), "Elaboración propia.", ancho="72%"))

# ------------------------------------------------------------ 7 matriz
P(h(2, "Matriz de trazabilidad"))
P(md("""
En esta matriz relaciono cada requerimiento con el módulo que lo cumple, los modelos donde aparece y cómo se comprobaría. Como no se implementó el sistema, la última columna es la prueba que propongo, no un resultado.

| Req. | Componente | Modelos | Decisión | Cómo se comprobaría |
|---|---|---|---|---|
| RF-01 | Identidad y acceso | CU-01, componentes, datos | ADR-004 | Prueba de login válido, inválido y cierre de sesión |
| RF-02 | Identidad y acceso, cada módulo | CU-02, componentes | ADR-004 | Llamar cada servicio con los 4 roles y revisar los 403 |
| RF-03 | Gestión académica | CU-03, datos | — | Desactivar un estudiante e intentar matricularlo |
| RF-04 | Gestión académica | CU-04, datos | — | Desactivar un docente e intentar asignarlo |
| RF-05 | Gestión académica | CU-05, datos | — | Crear dos asignaturas con el mismo código |
| RF-06 | Gestión académica, matrículas | CU-06, datos | — | Grupo con cruce de horario o cupo mayor que el aula |
| RF-07 | Matrículas | CU-07, secuencia, datos | ADR-002 | Pruebas de cada regla y prueba de concurrencia |
| RF-08 | Calificaciones | CU-08, CU-10, datos | — | Nota en grupo ajeno, nota de 5,5, nota después del cierre |
| RF-09 | Calificaciones | CU-11, datos | — | El estudiante no ve notas en borrador |
| RF-10 | Reportes | CU-12, componentes | — | Comparar el reporte con un conteo directo |
| RF-11 | Todos los listados | CU-13 | — | Un docente solo encuentra sus grupos |
| RF-12 | Auditoría | CU-14, CU-15, secuencia | ADR-005 | Matar el proceso en medio de matrículas y comparar los conteos |
| RNF-01 | Cloudflare, identidad, red privada | Despliegue | ADR-003, ADR-004 | Escaneo con OWASP ZAP; revisar que solo haya hashes |
| RNF-02 | API, base de datos | Despliegue | ADR-001 | Prueba de carga con 300 usuarios (k6) |
| RNF-03 | Balanceador, 2 nodos, réplica | Despliegue | ADR-003 | Apagar un nodo y forzar el cambio de base de datos |
| RNF-04 | API sin estado | Despliegue | ADR-004 | Agregar un tercer nodo sin cambiar código |
| RNF-05 | Módulos con interfaces | Componentes | ADR-001 | Pruebas de arquitectura (ArchUnit) |
| RNF-06 | Interfaz web | — | — | Lighthouse y axe; usar el sistema solo con teclado |
| RNF-07 | Matrículas, restricciones | Secuencia, datos | ADR-002 | 50 solicitudes por 1 cupo: debe quedar 1 matrícula |
| RNF-08 | API REST | Componentes | — | Validar la especificación OpenAPI |
| RNF-09 | Base de datos, respaldo | Despliegue | ADR-003 | Simulacro de restauración cada tres meses |
| RNF-10 | Esta matriz, ADR, auditoría | Todos | — | Revisar que todo requerimiento tenga fila |
| RNF-11 | Filtros por rol en cada módulo | Componentes | ADR-004 | El estudiante A pide datos del B y recibe 403 |
| RNF-12 | Interfaz web | Despliegue | — | Probar en 4 navegadores y 2 tamaños de pantalla |

Los requerimientos que quedan más débiles son la accesibilidad y la compatibilidad, porque dependen de cómo se haga la interfaz, que no está en el alcance.
"""))

# ------------------------------------------------------------ 8 decisiones y riesgos
P(h(2, "Decisiones arquitectónicas y análisis de riesgos"))
P(md("""
### Decisiones

Documenté cinco decisiones con el formato ADR (contexto, decisión, opciones y consecuencias), siguiendo a Nygard (2011). El texto completo de cada una está en el repositorio, en `docs/adr`.

**ADR-001. Monolito modular en capas.** Lo expliqué en la sección 5. La consecuencia negativa es que el sistema crece completo y no por partes, y que los límites entre módulos dependen de la disciplina del equipo.

**ADR-002. Bloqueo de fila en la matrícula.** Para que no haya sobrecupo, la matrícula bloquea la fila del cupo del grupo dentro de una transacción. Consideré también el control optimista, pero con mucha gente peleando el último cupo genera muchos reintentos fallidos, y una cola de solicitudes, que agregaba otro componente sin necesidad. Lo malo es que un grupo muy pedido hace fila; por eso las validaciones que no dependen del cupo van antes del bloqueo y la espera máxima es de 5 segundos.

**ADR-003. Despliegue con réplicas y respaldo externo.** Dos servidores para la API, base de datos con réplica en otra zona y respaldo continuo. Un solo servidor era más barato pero no alcanza el 99,5 %, y Kubernetes en varias regiones era demasiado para 300 usuarios. Queda la dependencia de proveedores externos que manejan datos personales.

**ADR-004. Inicio de sesión sin estado.** Un token de 15 minutos y otro de renovación de 8 horas que cambia cada vez que se usa. Así cualquier servidor atiende cualquier petición. Lo malo es que después de cerrar sesión el token corto sigue sirviendo hasta 15 minutos.

**ADR-005. Auditoría en la misma transacción.** El registro de auditoría se guarda en la misma transacción del cambio, así que si el cambio queda guardado, la auditoría también. La IA proponía hacerlo de forma asíncrona, pero así se podían perder registros si el servidor se caía en el momento justo.

### Atributos de calidad

En pocas palabras, cada atributo lo atiendo así: el rendimiento con llamadas en memoria, índices y un pool aparte para los reportes; la disponibilidad con redundancia y cambio automático de base de datos; la integridad con la transacción y las restricciones; la recuperación con los respaldos; la seguridad con HTTPS, Argon2id, roles y red privada; y la mantenibilidad con los módulos y sus interfaces.

### Riesgos y puntos únicos de falla

Revisé componente por componente qué pasaría si fallara. Los nodos de la API, el balanceador y la base de datos están duplicados, así que no tumban el sistema. Redis y el bus de eventos no existen en mi diseño. Quedan dos puntos únicos de falla que acepto: Cloudflare, que si falla obligaría a apuntar el DNS directo al balanceador, y la región del proveedor de nube, que si cae completa se recuperaría desde el respaldo en otra región en unas 2 horas.

Califiqué los riesgos con probabilidad por impacto, de 1 a 3 cada uno:

| Riesgo | Nivel | Qué hago al respecto |
|---|---|---|
| Sobrecupo o matrícula duplicada | Alto (9) | Bloqueo de fila, restricciones y prueba de concurrencia |
| Un cambio sin auditoría | Alto (6) | Auditoría en la misma transacción y prueba matando el proceso |
| Se agotan las conexiones a la base | Alto (6) | Límite de conexiones por servidor y pool aparte para reportes |
| Un estudiante ve datos de otro | Alto (6) | Filtros por rol en cada módulo |
| Datos personales en proveedores sin contrato | Alto (6) | Revisión jurídica (Ley 1581 de 2012) antes de salir a producción |
| Fila larga si se habilita la automatrícula | Medio (4) | Rechazo inmediato si el grupo ya está lleno |
| Los reportes ponen lento el sistema | Medio (4) | Vistas de solo lectura y pool aparte |
| Usuario con dos roles usa permisos del otro | Medio (4) | Un solo rol activo en el token |
| Robo de token en un computador compartido | Medio (4) | Tokens cortos que rotan |
| Los módulos se van mezclando | Medio (4) | Pruebas de arquitectura |
| El superusuario de la base altera la auditoría | Medio (3) | Copia diaria de la auditoría en almacenamiento bloqueado |
| El respaldo no sirve cuando se necesita | Medio (3) | Simulacro de restauración |

### Límites y validación

El sistema crece completo y no por módulo, la base principal recibe todas las escrituras y un grupo muy pedido siempre va a hacer fila. Para 300 usuarios no es un problema, pero son los límites a tener en cuenta.

Las decisiones que habría que comprobar antes de construir el sistema son: una prueba de carga subiendo de 50 a 500 usuarios (70 % consultas, 20 % matrículas y 10 % reportes), una prueba de 300 usuarios peleando 5 cupos en 2 segundos, apagar un servidor y forzar el cambio de base de datos, un simulacro de restauración, y matar el proceso en medio de matrículas para revisar que no se pierda ninguna auditoría. Varias de estas pruebas las propuso la misma IA en su autocrítica.
"""))

# ------------------------------------------------------------ 9 IA
P(h(2, "Uso de Google AI Studio"))
P(md(f"""
### Cómo lo usé

Usé el Playground de AI Studio con Gemini 3.8 Flash, con razonamiento en alto y la búsqueda en Google apagada para que solo trabajara con el caso. Todo fue el 4 de noviembre de 2026, en una sola conversación. El enlace a la conversación original es: {AISTUDIO}

Antes de abrir AI Studio hice mi propio análisis de los requerimientos y tenía una idea del estilo que quería. Lo hice así a propósito, para tener contra qué comparar lo que respondiera. Después le mandé siete prompts en el orden en que se diseña una arquitectura, sin corregirlo entre uno y otro:

1. Análisis del problema: le di el caso y los 24 requerimientos y le pedí actores, supuestos, restricciones y reglas.
2. Estilo arquitectónico: que comparara capas, monolito modular y microservicios.
3. Componentes: módulos, interfaces y un diagrama.
4. Modelo de datos.
5. Secuencia de la matrícula, incluyendo dos solicitudes por el último cupo.
6. Despliegue, seguridad y respaldo con presupuesto moderado.
7. Que criticara su propia propuesta como evaluador externo.

El texto de cada prompt está en el anexo C y las capturas en el anexo B.

Además de AI Studio, me apoyé en Claude (Anthropic) para organizar la redacción del documento y dibujar los diagramas en Mermaid. Las decisiones y la revisión de las respuestas de Gemini las hice contrastándolas con los requerimientos del caso.
"""))
P(fig(8, "Prompt P1 enviado a Gemini", str(CAP / "P1-01.png"), "Captura de Google AI Studio.", ancho="70%"))
P(md("""
### Qué hice con las respuestas

Revisé cada propuesta de cada respuesta y la clasifiqué como aceptada, modificada o descartada. En total fueron 93 propuestas:

| Prompt | Aceptadas | Modificadas | Descartadas |
|---|---|---|---|
| P1 Análisis | 11 | 6 | 1 |
| P2 Estilo | 5 | 5 | 0 |
| P3 Componentes | 5 | 9 | 1 |
| P4 Datos | 6 | 7 | 1 |
| P5 Secuencia | 2 | 7 | 0 |
| P6 Despliegue | 10 | 4 | 1 |
| P7 Autocrítica | 8 | 2 | 2 |
| Total | 47 | 40 | 6 |

El detalle de cada una está en el anexo A. Lo más importante que corregí fue:

- **La auditoría.** En el P3 y el P5 la IA propuso guardarla de forma asíncrona, después de confirmar el cambio. Si el servidor se cae justo en medio, el cambio queda sin registro, y eso va contra el RF-12. Lo cambié a la misma transacción. En el P7 la propia IA reconoció ese riesgo.
- **El aislamiento entre módulos.** La IA dijo que ningún módulo debía tocar las tablas de otro, pero después, en la matrícula, bloqueaba la tabla de grupos, que es de gestión académica. Lo resolví con una tabla de cupos propia del módulo de matrículas. Lo repitió en el P3, el P4, el P5 y otra vez en el prototipo.
- **Cosas de más.** Propuso Redis cuatro veces, además de almacenamiento WORM, colas, un servicio de notificaciones y ABAC. Ninguno lo pedía un requerimiento, así que los quité o los simplifiqué.
- **Cosas que faltaban.** En el modelo de datos no estaban los planes de estudio, el estado de publicación de las notas ni las fechas del periodo, y el porcentaje de cada evaluación se repetía en cada nota.
- **Los diagramas.** Tres de los cuatro que generó salieron ilegibles (figura 9), así que los rehice todos.

También tomé ideas buenas que yo no tenía: el cierre de notas, el cruce de horario, el orden de los bloqueos, la recuperación a un punto en el tiempo, la capacidad del aula, el rol activo y el plan de pruebas.
"""))
P(fig(9, "Diagrama de componentes que generó la IA (P3)", str(CAP / "P3-06.png"), "Captura de Google AI Studio. Por esto rehice el diagrama (figura 2).", ancho="46%"))
P(md("""
### Prototipo en AI Studio Build

Después usé AI Studio Build para generar un prototipo navegable. En lugar de pedirle "un sistema académico", le pasé mi arquitectura: los seis módulos con sus tres capas en carpetas separadas, las interfaces, las reglas de negocio, el rol activo, la auditoría y una página con las cinco decisiones. También le pedí un botón que simulara dos solicitudes por el último cupo. El prompt está en el repositorio (`docs/ai-studio/PROMPT-BUILD.txt`).

El prototipo salió con los cuatro perfiles, el menú según el rol (por ejemplo, el coordinador no ve la auditoría), la baja lógica de estudiantes, la matrícula con sus cinco validaciones y la simulación del último cupo (figuras 10 y 11).

Pero al revisarlo encontré dos cosas:

- En la explicación del botón de concurrencia, la IA volvió a bloquear la tabla `grupos`, que es del módulo académico, en vez de la tabla de cupos del módulo de matrículas. Es el mismo error que ya le había corregido en el diseño, así que se lo volví a corregir.
- Gemini dice que la auditoría es "transaccional ACID" y que la simulación prueba la concurrencia. No es así: el prototipo guarda los datos en memoria del navegador, donde no hay transacciones, y JavaScript corre en un solo hilo, así que las dos solicitudes en realidad se procesan una tras otra. El botón sirve para ilustrar la idea, pero la garantía real la da PostgreSQL.

Por eso insisto en que el prototipo es una maqueta con datos simulados y no la implementación de la arquitectura.
"""))
P(fig(10, "Prototipo: listado de estudiantes como coordinador", str(CAPB / "B-01-estudiantes-coordinador.png"),
      "Captura de AI Studio Build. Se ve la baja lógica y el menú sin auditoría.", ancho="78%"))
P(fig(11, "Prototipo: matrícula y explicación del bloqueo", str(CAPB / "B-02-matriculas-fundamento-adr002.png"),
      "Captura de AI Studio Build. En el recuadro la IA bloquea la tabla grupos, que es de otro módulo.", ancho="78%"))
P(md("""
### Lo que aprendí usando la IA

La IA acertó en lo grande: recomendó el mismo estilo, los mismos módulos y el bloqueo de fila, y su plan de pruebas fue bueno. También me dio ideas que no tenía. Pero tendió a meter cosas de más, se contradijo (defendía el aislamiento entre módulos y luego lo rompía) y repitió errores que ya le había corregido. Por eso no basta con corregirla una vez: cada respuesta hay que revisarla contra los requerimientos.
"""))

# ------------------------------------------------------------ 10 conclusiones
P(h(2, "Conclusiones"))
P(md("""
1. Un monolito modular en capas cumple los 24 requerimientos con menos complejidad y costo que los microservicios. La decisión sale de los requerimientos, sobre todo de la integridad de la matrícula, y no de qué tecnología está de moda.
2. La matrícula es la parte más delicada del sistema porque junta reglas de negocio, concurrencia y auditoría. Con una transacción, el bloqueo de fila y las restricciones en la base de datos no puede haber sobrecupo aunque falle el código.
3. El 99,5 % de disponibilidad se logra duplicando lo que podía tumbar el sistema (servidores, balanceador y base de datos). Quedan dos riesgos que acepto: Cloudflare y la región de la nube.
4. Todos los requerimientos quedaron con su componente, su modelo y una forma de comprobarlos. Los más débiles son la accesibilidad y la compatibilidad, que dependen de la interfaz.
5. La IA me ahorró mucho tiempo pero no reemplazó el trabajo de pensar. Lo útil fue tener mi propio análisis antes de consultarla y revisar cada respuesta.

Como recomendación, antes de construir el sistema habría que hacer las pruebas de la sección 8, confirmar los supuestos con la institución (sobre todo quién matricula y los tiempos de respaldo) y revisar los contratos con los proveedores por el manejo de datos personales.
"""))
P(md(f"""
**Enlaces**

- Video: {YOUTUBE or '[pendiente]'}
- Repositorio: {REPO}
"""))

# ------------------------------------------------------------ referencias
P(h(2, "Referencias", nonum=True))
P("""<div class="referencias">
<p>Bass, L., Clements, P., &amp; Kazman, R. (2021). <em>Software architecture in practice</em> (4.ª ed.). Addison-Wesley.</p>
<p>Congreso de la República de Colombia. (2012, 17 de octubre). <em>Ley Estatutaria 1581 de 2012, por la cual se dictan disposiciones generales para la protección de datos personales</em>. Diario Oficial n.º 48.587.</p>
<p>Google. (2026). <em>Gemini 3.8 Flash</em> [Modelo de lenguaje de gran tamaño]. Google AI Studio. https://aistudio.google.com</p>
<p>International Organization for Standardization. (2011). <em>Systems and software engineering: Systems and software Quality Requirements and Evaluation (SQuaRE). System and software quality models</em> (ISO/IEC 25010:2011).</p>
<p>Kendall, K. E., &amp; Kendall, J. E. (2011). <em>Análisis y diseño de sistemas</em> (8.ª ed.). Pearson Educación.</p>
<p>Kruchten, P. (1995). The 4+1 view model of architecture. <em>IEEE Software, 12</em>(6), 42–50. https://doi.org/10.1109/52.469759</p>
<p>Nygard, M. (2011, 15 de noviembre). <em>Documenting architecture decisions</em>. Cognitect. https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions</p>
<p>Pressman, R. S., &amp; Maxim, B. R. (2021). <em>Ingeniería de software: Un enfoque práctico</em> (9.ª ed.). McGraw-Hill Education.</p>
<p>Richards, M., &amp; Ford, N. (2020). <em>Fundamentals of software architecture: An engineering approach</em>. O'Reilly Media.</p>
<p>Sommerville, I. (2011). <em>Ingeniería de software</em> (9.ª ed.). Pearson Educación.</p>
</div>""")

# ------------------------------------------------------------ anexos
ev = (DOCS / "ai-studio" / "evaluacion-ia.md").read_text(encoding="utf-8")
cuerpo_ev = ev.split("---", 1)[1].split("## Resumen general")[0]
cuerpo_ev = re.sub(r"(?m)^## (P\d) · (.*)$", lambda m: f"### {m.group(1)} · {m.group(2).lower()}", cuerpo_ev)
cuerpo_ev = re.sub(r"(?m)^---\s*$", "", cuerpo_ev)
P(h(2, "Anexo A. Evaluación de cada respuesta de la IA", nonum=True))
P('<div class="anexo-a">' + md(cuerpo_ev).replace("<h3>", '<h3 class="nonum">') + "</div>")

P(h(2, "Anexo B. Capturas de la conversación en AI Studio", nonum=True))
P("<p>Capturas en el orden de la conversación. La primera de cada prompt muestra lo que envié.</p>")
temas = {"P1": "análisis del problema", "P2": "estilo arquitectónico", "P3": "componentes",
         "P4": "modelo de datos", "P5": "secuencia de la matrícula", "P6": "despliegue", "P7": "autocrítica"}
P('<div class="capturas">')
for p, t in temas.items():
    for f in sorted(CAP.glob(f"{p}-*.png")):
        P(f'<figure class="cap"><img src="{f}"><figcaption>{f.stem} · {t}</figcaption></figure>')
P("</div>")

guia = (DOCS / "ai-studio" / "GUIA-PROMPTS.md").read_text(encoding="utf-8")
P(h(2, "Anexo C. Texto de los prompts", nonum=True))
for tit, txt in re.findall(r"## (P\d · [^\n]+)\n\n```text\n(.*?)```", guia, flags=re.S):
    P(f'<h3 class="nonum">{tit[:5]}{tit[5:].lower()}</h3><pre class="prompt">{txt.replace("&", "&amp;").replace("<", "&lt;")}</pre>')

plantilla = (Path(__file__).parent / "plantilla_v2.html").read_text(encoding="utf-8")
(Path(__file__).parent / "informe_v2.html").write_text(plantilla.replace("{{CUERPO}}", "\n".join(partes)), encoding="utf-8")
print("informe_v2.html generado")
