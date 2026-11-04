"""Construye informe/informe.html a partir de los documentos del repositorio.

Uso:  python3 informe/construir_informe.py   (luego: node informe/imprimir.js)
"""
import re
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
IMG = RAIZ / "modelos" / "imagenes"
CAP = DOCS / "ai-studio" / "capturas"
REPO = "https://github.com/juanvs1985/sga-arquitectura"
AISTUDIO = ("https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221NcbJ3YkHGzE2xID9EykCrpI4RXmgqqe8"
            "%22%5D,%22action%22:%22open%22,%22userId%22:%22113748348275050694995%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing")
YOUTUBE = None  # Se completa cuando el video esté publicado.
FECHA = "8 de noviembre de 2026"

# Numeración de figuras: repositorio -> informe
MAPA_FIG = {"1": "1", "2a": "2", "2b": "3", "3": "4", "4": "5", "5a": "6", "5b": "7"}


def leer(rel):
    return (DOCS / rel).read_text(encoding="utf-8")


def seccion(texto, inicio):
    """Devuelve el cuerpo de la sección '## <inicio>…' hasta la siguiente '## '."""
    partes = re.split(r"(?m)^## ", texto)
    for p in partes[1:]:
        if p.startswith(inicio):
            return p.split("\n", 1)[1].strip()
    raise KeyError(inicio)


def sin_titulo_doc(texto):
    """Quita el '# Título' inicial de un documento."""
    return re.sub(r"\A# .*\n", "", texto).strip()


def renumerar(texto):
    texto = re.sub(r"Figura (5a|5b|2a|2b|1|3|4)\b", lambda m: "Figura " + MAPA_FIG[m.group(1)], texto)
    reemplazos = {
        "(Fig. 1)": "(Figura 1)", "(Fig. 2a/2b)": "(Figuras 2 y 3)", "(Fig. 3)": "(Figura 4)",
        "(Fig. 4)": "(Figura 5)", "(Fig. 5a/5b)": "(Figuras 6 y 7)", "SE (5a, 5b)": "SE (Fig. 6 y 7)",
        "SE (5a, pasos 28–29)": "SE (Fig. 6, pasos 28–29)", "CO (2a, 2b)": "CO (Fig. 2 y 3)",
    }
    for a, b in reemplazos.items():
        texto = texto.replace(a, b)
    return texto


def enlaces_repo(texto):
    """Convierte enlaces relativos de los .md en enlaces absolutos al repositorio."""
    def rep(m):
        etiqueta, destino = m.group(1), m.group(2)
        if destino.startswith("http"):
            return m.group(0)
        destino = re.sub(r"^(\.\./)+", "", destino)
        return f"[{etiqueta}]({REPO}/blob/main/{destino})"
    return re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", rep, texto)


def md(texto, _sin_uso=None, desplazamiento=0):
    """Markdown -> HTML. 'desplazamiento' baja todos los encabezados ese número de niveles."""
    def bajar(m):
        n = len(m.group(1)) + desplazamiento
        titulo = re.sub(r"^\d+(\.\d+)*\s+", "", m.group(2))
        return "#" * min(n, 6) + " " + titulo
    texto = re.sub(r"(?m)^(#{2,5}) (.*)$", bajar, texto)
    texto = enlaces_repo(renumerar(texto))
    return markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists"])


def quitar_mermaid(texto):
    return re.sub(r"```mermaid.*?```\s*", "", texto, flags=re.S)


def figura(num, titulo, src, nota, ancho="100%", horizontal=False, alto=None):
    estilo = f"width:{ancho};" + (f"max-height:{alto};" if alto else "")
    html = (f'<figure class="fig"><p class="fig-num">Figura {num}</p><p class="fig-tit">{titulo}</p>'
            f'<img src="{src}" style="{estilo}" alt="{titulo}"><p class="fig-nota"><em>Nota.</em> {nota}</p></figure>')
    return f'<section class="horizontal">{html}</section>' if horizontal else html


def tabla_tit(num, titulo):
    return f'<p class="tab-num">Tabla {num}</p><p class="tab-tit">{titulo}</p>'


def h(nivel, texto, id_=None, numerado=True):
    clase = "" if numerado else ' class="nonum"'
    ident = f' id="{id_}"' if id_ else ""
    return f"<h{nivel}{clase}{ident}>{texto}</h{nivel}>"


analisis = leer("01-analisis-requisitos.md")
partes = []
P = partes.append

# ---------------------------------------------------------------- Portada
P(f"""
<section class="portada">
  <p class="inst">Corporación Unificada Nacional de Educación Superior · CUN</p>
  <p class="inst2">Escuela de Ingenierías · Ingeniería de Sistemas</p>
  <div class="titulo-bloque">
    <p class="asig">Arquitectura de Software (INGS0763)</p>
    <h1 class="titulo">Diseño de la arquitectura de un Sistema de Gestión Académica mediante Google AI Studio</h1>
    <p class="subtitulo">Actividad de aprendizaje de las semanas 3, 4, 5 y 6</p>
  </div>
  <div class="datos">
    <p><span>Estudiante</span>Juan Pablo Vargas Sánchez</p>
    <p><span>Docente</span>Alexander Calderón Martínez</p>
    <p><span>Fecha</span>{FECHA}</p>
  </div>
</section>
""")

# ---------------------------------------------------------------- Contenido
P('<section class="toc-pagina"><h2 class="nonum">Contenido</h2><ol id="toc"></ol></section>')

# ---------------------------------------------------------------- 1. Introducción
P(h(2, "Introducción y descripción del problema", "intro"))
P(md("""
Una institución de educación superior administra hoy la información de estudiantes, docentes, programas, asignaturas, grupos, matrículas, calificaciones y horarios en archivos y aplicaciones independientes. Esa dispersión genera tres problemas concretos: datos duplicados que se contradicen, consultas lentas y manuales, y la imposibilidad de saber quién cambió una nota, una matrícula o un rol, y cuándo.

Este informe presenta la **arquitectura de software de un Sistema de Gestión Académica (SGA)** que centraliza esa información en una sola fuente de verdad, accesible desde el navegador y controlada por roles. La propuesta parte de 12 requerimientos funcionales y 12 no funcionales, los traduce en criterios verificables y los resuelve con un estilo arquitectónico, cinco decisiones documentadas y seis modelos del sistema.

Google AI Studio (modelo Gemini 3.8 Flash) se usó como herramienta de apoyo en siete etapas del diseño. Cada propuesta de la IA se contrastó con los requerimientos y se aceptó, modificó o descartó con una justificación explícita (sección 9). La arquitectura final es responsabilidad del autor y no una transcripción de lo que sugirió la IA.

**Alcance de la entrega.** Siguiendo el enunciado, este trabajo produce una **arquitectura y sus modelos**, no una implementación. Todas las capacidades descritas son **propuestas de diseño**: ninguna se implementó ni se probó todavía. Para cada una, la matriz de trazabilidad indica cómo se verificaría.
""", 3))
P(md("### Problemas actuales y requerimientos que los atacan\n\n" + seccion(analisis, "1.1").split("\n\n", 1)[1], 3))

# ---------------------------------------------------------------- 2. Objetivos
P(h(2, "Objetivos", "objetivos"))
P(md("""
### Objetivo general

Diseñar y justificar la arquitectura de software de un Sistema de Gestión Académica seguro, mantenible, escalable y accesible desde la web, a partir de sus requerimientos funcionales y no funcionales, usando Google AI Studio de forma crítica como herramienta de apoyo.

### Objetivos específicos

1. Analizar el caso y especificar los requerimientos funcionales y no funcionales con criterios de aceptación verificables, junto con los actores, supuestos, restricciones y reglas de negocio.
2. Seleccionar y justificar un estilo arquitectónico frente al tamaño del sistema y sus atributos de calidad, comparando al menos tres alternativas.
3. Representar el sistema mediante modelos de casos de uso, componentes, despliegue, datos conceptual y secuencia, con nombres y relaciones consistentes entre sí.
4. Relacionar cada requerimiento con los componentes, modelos y decisiones que lo satisfacen, y con el método para verificarlo.
5. Identificar riesgos, puntos únicos de falla, problemas de seguridad y límites de escalabilidad, y proponer cómo validar las decisiones críticas.
6. Documentar el uso de Google AI Studio y evaluar cada una de sus propuestas como aceptada, modificada o descartada.
""", 3))

# ---------------------------------------------------------------- 3. Alcance, actores, supuestos y restricciones
P(h(2, "Alcance, actores, supuestos y restricciones", "alcance"))
P(md("""
### Alcance

**Dentro del alcance:** los 12 RF y 12 RNF del enunciado; el diseño de la arquitectura, sus modelos, decisiones, riesgos y método de verificación; la evaluación del uso de la IA.

**Fuera del alcance:** la implementación del sistema, la interfaz gráfica detallada, la integración real con otras plataformas institucionales (solo se deja la API preparada, RNF-08), los prerrequisitos entre asignaturas y las notificaciones por correo, que ningún requerimiento pide.
""", 3))
P(md("### Actores\n\n" + seccion(analisis, "1.2"), 3))
P(md("### Supuestos\n\n" + seccion(analisis, "1.3"), 3))
P(md("### Restricciones\n\n" + seccion(analisis, "1.4"), 3))

# ---------------------------------------------------------------- 4. Requerimientos
P(h(2, "Requerimientos funcionales y no funcionales", "requerimientos"))
P(md("### Requerimientos funcionales\n\n" + seccion(analisis, "1.6"), 3))
P(md("### Requerimientos no funcionales\n\n" + seccion(analisis, "1.7"), 3))
P(md("### Reglas de negocio\n\n" + seccion(analisis, "1.5"), 3))
P(md("### Análisis de los requerimientos\n\n" + seccion(analisis, "1.8"), 3))

# ---------------------------------------------------------------- 5. Arquitectura
adr1 = leer("adr/ADR-001-estilo-monolito-modular.md")
P(h(2, "Arquitectura seleccionada y justificación", "arquitectura"))
P(md("""
### La arquitectura en una frase

Un **monolito modular en capas**: una sola aplicación desplegable, dividida en seis módulos por área de negocio (identidad y acceso, gestión académica, matrículas, calificaciones, reportes y auditoría). Cada módulo tiene tres capas internas (controlador, dominio y repositorio), se comunica con los demás solo por interfaces y es dueño de su propio esquema en una única base de datos PostgreSQL. El sistema se expone como **API REST** y se despliega en **dos nodos sin estado** detrás de un balanceador, con la base de datos en **alta disponibilidad** y respaldo externo continuo.

### Alternativas evaluadas
""", 3))
P(md(seccion(adr1, "Argumentos"), 3))
P(md("""
### Por qué monolito modular y no microservicios

La decisión se tomó por los requerimientos, no por la tecnología de moda:

- **La consistencia de la matrícula (RNF-07) es el requisito más delicado.** Con una sola base de datos, el control de cupos y duplicados se resuelve con una transacción ACID. Con microservicios, cada servicio tendría su propia base y habría que coordinar con consistencia eventual (patrón Saga), lo que abre la puerta al sobrecupo.
- **300 usuarios concurrentes (RNF-02) es una carga moderada.** Las llamadas entre módulos ocurren en memoria, sin latencia de red; dos nodos bastan, y se puede agregar un tercero sin cambios (RNF-04).
- **La mantenibilidad (RNF-05) no exige microservicios.** Exige límites claros, y los módulos con interfaces y esquemas propios los dan, sin la complejidad operativa de orquestar decenas de servicios.
- **El contexto lo favorece:** presupuesto moderado (S-08) y un equipo pequeño.

**Por qué no un monolito en capas sin módulos:** las capas solas no impiden que la lógica de matrícula, notas y auditoría se mezcle con el tiempo. Los módulos agregan esos límites verticales.

**Camino de evolución:** si en el futuro un módulo necesita escalar por separado, ya tiene su interfaz y su esquema, de modo que puede extraerse como servicio de forma gradual (patrón Strangler Fig).

Google AI Studio recomendó el mismo estilo (respuesta P2). La sección 9 explica qué se tomó de su análisis y qué se corrigió: por ejemplo, que capas y módulos no son excluyentes sino complementarios.
""", 3))

# ---------------------------------------------------------------- 6. Modelos
P(h(2, "Modelo del sistema", "modelos"))
P(md("Los seis modelos usan los mismos nombres de actores, módulos, interfaces y entidades. Los diagramas se elaboraron en Mermaid y SVG; sus archivos fuente están en el repositorio (`modelos/fuentes/`).", 3))

cu = sin_titulo_doc(leer("modelos/01-casos-de-uso.md"))
cu = re.sub(r"## Figura 1\..*?\n\n!\[.*?\)\n\n\*Fuente:.*?\*\n", "", cu, flags=re.S)
P(h(3, "Modelo de casos de uso", "m-cu"))
P(md(cu.replace("## Descripción de los casos de uso principales", "#### Descripción de los casos de uso principales"), 3))
P(figura(1, "Diagrama de casos de uso del SGA", str(IMG / "01-casos-de-uso.svg"),
         "Las figuras son actores; las elipses, casos de uso; el rectángulo, el límite del sistema. Las flechas «include» indican que el caso siempre ejecuta CU-15 (auditoría, RF-12). Fuente: elaboración propia.",
         horizontal=True))

comp = sin_titulo_doc(leer("modelos/02-componentes.md"))
comp = quitar_mermaid(comp)
comp = re.sub(r"## Figura 2a\..*?\n\n\*Fuente:.*?\*\n", "", comp, flags=re.S)
comp_a, comp_b = comp.split("## Figura 2b.")
comp_b = re.sub(r"\A.*?\n\n\*Fuente:.*?\*\n", "", comp_b, flags=re.S)
P(h(3, "Modelo de componentes (vista lógica)", "m-comp"))
P(figura(2, "Módulos, interfaces y dependencias", str(IMG / "02a-componentes-modulos.svg"),
         "Cada caja azul es un módulo con su ruta REST; la etiqueta de cada flecha es la interfaz que consume. Ningún módulo accede a las tablas de otro. Fuente: elaboración propia.",
         ancho="74%"))
P(md(comp_a.replace("## Responsabilidades e interfaces", "#### Responsabilidades e interfaces"), 3))
P(figura(3, "Estructura interna de un módulo (Matrículas)", str(IMG / "02b-componentes-capas-modulo.svg"),
         "Todos los módulos siguen la misma estructura de tres capas, con el dominio dependiendo solo de contratos. Fuente: elaboración propia.",
         ancho="62%"))
P(md(comp_b, 3))

dep = quitar_mermaid(sin_titulo_doc(leer("modelos/03-despliegue.md")))
dep = re.sub(r"## Figura 3\..*?\n\n\*Fuente:.*?\*\n", "", dep, flags=re.S)
P(h(3, "Modelo de despliegue", "m-dep"))
P(figura(4, "Nodos, canales y controles de seguridad", str(IMG / "03-despliegue.svg"),
         "Las líneas continuas son canales de comunicación con su protocolo; las punteadas, dependencias operativas. Fuente: elaboración propia a partir de ADR-003.",
         ancho="76%"))
P(md(dep.replace("## Nodos", "#### Nodos").replace("## Controles de seguridad por canal", "#### Controles de seguridad por canal"), 3))

dat = quitar_mermaid(sin_titulo_doc(leer("modelos/04-datos.md")))
dat = re.sub(r"## Figura 4\..*?\n\n\*Fuente:.*?\*\n", "", dat, flags=re.S)
P(h(3, "Modelo de datos conceptual", "m-datos"))
P(figura(5, "Entidades principales y cardinalidades", str(IMG / "04b-datos-entidades.svg"),
         "Notación de pata de gallo: || uno y solo uno · o| cero o uno · |{ uno o muchos · o{ cero o muchos. Los atributos de cada entidad están en el modelo completo del repositorio (modelos/imagenes/04-datos-conceptual.png). Fuente: elaboración propia.",
         horizontal=True))
dat = re.sub(r"\*\*Notación \(pata de gallo\):\*\*.*?\n", "", dat)
for t in ["Entidades por módulo", "Cardinalidades más importantes", "Restricciones de integridad (RNF-07)"]:
    dat = dat.replace("## " + t, "#### " + t)
P(md(dat, 3))
P(md("""
#### Atributos principales

| Entidad | Atributos principales |
|---|---|
| Usuario | id_usuario (PK), correo (único), hash_contrasena (Argon2id), nombres, apellidos, estado |
| Rol / UsuarioRol | id_rol (PK), código (único: ADMIN, COORDINADOR, DOCENTE, ESTUDIANTE) / (id_usuario, id_rol) |
| Sesion | id_sesion (PK), id_usuario, hash del token de renovación, expira_en, revocada |
| Estudiante / Docente | id (PK), id_usuario (único), código (único), id_programa (solo estudiante), estado |
| Programa / PlanEstudio | código (único), nombre, nivel / id_programa, versión, vigente |
| Asignatura | id_asignatura (PK), id_plan, código (único), nombre, créditos, semestre |
| PeriodoAcademico | código (único), fechas de inicio y fin, inicio y fin de matrícula, límite de notas, notas_cerradas |
| Grupo | id_grupo (PK), id_asignatura, id_periodo, id_docente, código, cupo_maximo |
| Horario / Aula | día, hora de inicio y fin, id_aula o enlace / código, sede, capacidad |
| CupoGrupo | id_grupo (PK), cupo_maximo, ocupados (CHECK ocupados ≤ cupo_maximo) |
| Matricula / DetalleMatricula | id_estudiante, id_periodo, fecha, estado / id_matricula, id_grupo, id_asignatura, estado |
| Evaluacion / Calificacion | id_grupo, nombre, porcentaje / id_detalle, id_evaluacion, nota (0,0–5,0), estado (Borrador o Publicada) |
| EventoAuditoria | id_usuario, acción, entidad, id del registro, valor anterior y nuevo, justificación, fecha y hora, IP, id de correlación |
""", 3))

sec = quitar_mermaid(sin_titulo_doc(leer("modelos/05-secuencia.md")))
sec_a, sec_b = sec.split("## Figura 5b.")
sec_a = re.sub(r"## Figura 5a\..*?\n\n\*Fuente:.*?\*\n", "", sec_a, flags=re.S)
sec_b = re.sub(r"\A.*?\n\n\*Fuente:.*?\*\n", "", sec_b, flags=re.S)
P(h(3, "Vista de secuencia: matrícula de un estudiante", "m-sec"))
P(md(sec_a.split("**Puntos clave")[0], 3))
P(figura(6, "Flujo completo de la matrícula", str(IMG / "05a-secuencia-matricula.svg"),
         "Los pasos 7 a 13 validan sin bloquear; los pasos 18 a 30 forman una sola transacción con bloqueo de fila (ADR-002) y auditoría (ADR-005). Fuente: elaboración propia.",
         horizontal=True))
P(md("**Puntos clave" + sec_a.split("**Puntos clave")[1], 3))
P(figura(7, "Dos solicitudes simultáneas por el último cupo", str(IMG / "05b-secuencia-concurrencia.svg"),
         "Escenario de aceptación de RNF-07. Fuente: elaboración propia.", ancho="78%"))
P(md(sec_b, 3))

# ---------------------------------------------------------------- 7. Matriz
traz = sin_titulo_doc(leer("modelos/06-trazabilidad.md"))
P(h(2, "Matriz de trazabilidad de requerimientos", "trazabilidad"))
P(md(traz, desplazamiento=1))

# ---------------------------------------------------------------- 8. Decisiones, atributos y riesgos
P(h(2, "Decisiones arquitectónicas, atributos de calidad y análisis de riesgos", "decisiones"))
P(md("""
### Decisiones arquitectónicas

Las decisiones se documentaron con el formato de registro de decisiones arquitectónicas (ADR) propuesto por Nygard (2011): contexto, decisión, opciones consideradas y consecuencias. El enunciado pide al menos tres; se documentaron cinco. El texto completo de cada una está en el repositorio (`docs/adr/`).

| ADR | Decisión | Requerimientos | Alternativas descartadas | Consecuencia principal |
|---|---|---|---|---|
| ADR-001 | **Monolito modular en capas**, un esquema por módulo, API REST | RNF-02, 03, 04, 05, 07, 09 | Capas sin módulos; microservicios | Consistencia ACID en un solo artefacto; el sistema escala completo, no por módulo |
| ADR-002 | **Bloqueo pesimista** de la fila `cupo_grupo` en una transacción, en orden ascendente de grupo, con validaciones previas sin bloqueo y restricciones únicas | RF-07, RNF-07, RNF-02 | Control optimista; cola de solicitudes | Nunca hay sobrecupo; un grupo muy popular hace fila |
| ADR-003 | **Dos nodos sin estado**, balanceador administrado, **PostgreSQL con réplica** en otra zona, respaldo continuo (RPO 15 min, RTO 2 h), Cloudflare | RNF-01, 03, 04, 09 | Un solo servidor; Kubernetes multirregión | Sin puntos únicos de falla internos; dependencia de proveedores externos |
| ADR-004 | **Autenticación sin estado:** JWT de 15 min, renovación de 8 h con rotación, rol activo único | RF-01, RF-02, RNF-01, 04, 11 | Sesión en memoria; lista negra en Redis | Cualquier nodo atiende cualquier petición; el token sigue válido hasta 15 min tras cerrar sesión |
| ADR-005 | **Auditoría en la misma transacción** del cambio, tabla de solo inserción, exportación diaria | RF-12, RNF-07, RNF-10 | Bus de eventos asíncrono; almacenamiento WORM | Ningún cambio queda sin auditar; la tabla crece y se particiona por mes |

### Atributos de calidad y tácticas

| Atributo (ISO/IEC 25010) | Requerimiento | Escenario de calidad (estímulo → medida) | Táctica arquitectónica |
|---|---|---|---|
| Eficiencia de desempeño | RNF-02 | 300 usuarios concurrentes en operación normal → P95 de consultas comunes ≤ 3 s | Llamadas en memoria, índices, caché de catálogos, pool separado para reportes |
| Fiabilidad: disponibilidad | RNF-03 | Falla de un nodo o de la base primaria → el servicio sigue; disponibilidad mensual ≥ 99,5 % | Redundancia activa, conmutación automática, despliegues sin interrupción |
| Fiabilidad: integridad | RNF-07 | 50 solicitudes simultáneas por 1 cupo → exactamente 1 matrícula | Transacción con bloqueo de fila y restricciones de base de datos |
| Fiabilidad: recuperabilidad | RNF-09 | Pérdida de la base de datos → restaurada en ≤ 2 h con pérdida ≤ 15 min | Respaldo diario + WAL continuo, almacenamiento externo con bloqueo |
| Seguridad | RNF-01, RNF-11 | Usuario sin permiso pide un recurso → 403; tráfico siempre cifrado | TLS, Argon2id, RBAC más filtros por propietario, red privada |
| Mantenibilidad | RNF-05 | Cambiar una regla de notas → solo se modifica el módulo Calificaciones | Módulos con interfaces, inversión de dependencias, pruebas de arquitectura |
| Compatibilidad | RNF-08, RNF-12 | Integración externa o navegador distinto → funciona según contrato | API REST con OpenAPI; interfaz web responsiva |
""", 3))
ries = sin_titulo_doc(leer("07-riesgos.md"))
P(md("### Análisis de riesgos\n\n" + ries.replace("## 7.", "#### 7."), 3).replace("<h5>", "<h4>").replace("</h5>", "</h4>"))

# ---------------------------------------------------------------- 9. Evidencias de AI Studio
ev = leer("ai-studio/evaluacion-ia.md")
P(h(2, "Evidencias del uso de Google AI Studio", "ia"))
P(md(f"""
### Configuración y método

| Elemento | Valor |
|---|---|
| Herramienta | Google AI Studio (Playground) |
| Modelo | Gemini 3.8 Flash (`gemini-3.8-flash`) |
| Nivel de razonamiento | High |
| Búsqueda en Google (grounding) | Desactivada, para que el modelo razonara solo con el caso y los requerimientos |
| Fecha | 4 de noviembre de 2026 |
| Conversación original | [Enlace a Google AI Studio]({AISTUDIO}) |
| Respuestas completas y capturas | [docs/ai-studio en el repositorio]({REPO}/tree/main/docs/ai-studio) |

**Método.** El análisis propio de los requerimientos (sección 4) y la decisión preliminar del estilo se hicieron **antes** de consultar a la IA, para tener un criterio contra el cual evaluarla. Luego se enviaron siete prompts en una sola conversación, en el orden del diseño, sin corregir a la IA entre prompts. Cada propuesta de cada respuesta se clasificó como **aceptada**, **modificada** o **descartada**, con una justificación basada en los requerimientos.

### Prompts utilizados

| Prompt | Etapa del diseño | Qué se le pidió | Capturas (Anexo B) |
|---|---|---|---|
| P1 | Análisis del problema | Actores, supuestos, restricciones, reglas de negocio y clasificación de los RNF, con el caso y los 24 requerimientos completos | P1-01 a P1-06 |
| P2 | Estilo arquitectónico | Comparar capas, monolito modular y microservicios frente a los RNF y recomendar uno | P2-01 a P2-04 |
| P3 | Componentes | Módulos, responsabilidades, interfaces REST, dependencias y diagrama Mermaid | P3-01 a P3-07 |
| P4 | Datos | Entidades, atributos, cardinalidades y restricciones contra matrículas duplicadas | P4-01 a P4-05 |
| P5 | Secuencia | Matrícula con validación de cupo, duplicados y dos solicitudes por el último cupo | P5-01 a P5-04 |
| P6 | Despliegue | Nodos, canales, seguridad, disponibilidad del 99,5 % y respaldo con presupuesto moderado | P6-01 a P6-05 |
| P7 | Autocrítica | Evaluar como auditor externo la propia propuesta: vacíos, fallas, riesgos y validación | P7-01 a P7-06 |

El texto completo de cada prompt está en el Anexo C.
""", 3))
P(figura(8, "Prompt P1 enviado a Gemini con el caso y los requerimientos", str(CAP / "P1-01.png"),
         "Captura de la conversación en Google AI Studio. Fuente: Google AI Studio (2026).", ancho="78%"))
P(md("""
### Resultado de la evaluación

| Prompt | Aceptadas | Modificadas | Descartadas | Observación |
|---|---|---|---|---|
| P1 Análisis | 11 | 6 | 1 | Aportó tres reglas que no se tenían: fechas límite, cierre de notas y cruce de horarios |
| P2 Estilo | 5 | 5 | — | Recomendó el mismo estilo; se corrigió que capas y módulos se combinan |
| P3 Componentes | 5 | 9 | 1 | Auditoría asíncrona que podía perder eventos; bloqueo sobre tablas de otro módulo |
| P4 Datos | 6 | 7 | 1 | Faltaban planes de estudio, estado de publicación y fechas del periodo; porcentaje mal normalizado |
| P5 Secuencia | 2 | 7 | — | Aportó el orden de bloqueos contra interbloqueos; validaba dentro del bloqueo |
| P6 Despliegue | 10 | 4 | 1 | La más útil: base de datos en alta disponibilidad, respaldo continuo, Cloudflare |
| P7 Autocrítica | 8 | 2 | 2 | Tres de sus críticas ya estaban corregidas en el diseño del autor |
| **Total** | **47** | **40** | **6** | **93 propuestas evaluadas** |

La evaluación detallada de las 93 propuestas, una por fila y con su justificación, está en el Anexo A.

### Ajustes más importantes realizados a las propuestas de la IA

1. **Auditoría (P3, P5).** La IA propuso registrar la auditoría con un bus de eventos asíncrono después del COMMIT. Si el proceso se cae entre ambos pasos, el cambio queda sin auditar, lo que viola RF-12. Se reemplazó por una escritura en la misma transacción (ADR-005). En su autocrítica (P7), la propia IA reconoció este riesgo.
2. **Aislamiento entre módulos (P3, P4, P5).** La IA defendió que ningún módulo toca las tablas de otro, pero luego bloqueó la tabla Grupo desde Matrículas. Se resolvió con la entidad CupoGrupo, propiedad de Matrículas (ADR-002).
3. **Sobredimensionamiento.** Redis se propuso cuatro veces, además de almacenamiento WORM, colas de matrícula, servicio de notificaciones y ABAC. Se descartaron o simplificaron por no tener un requerimiento que los justifique (S-08).
4. **Vacíos frente al enunciado (P4).** Se agregaron planes de estudio (RF-05), estado de publicación de notas (RF-09) y fechas del periodo (RN-11), y se normalizó el porcentaje de las evaluaciones.
5. **Mejoras aceptadas.** De la IA se tomaron el cierre de notas, el cruce de horarios, el orden de bloqueos, la recuperación a un punto en el tiempo (RPO 15 min), la capacidad del aula, el rol activo y el plan de pruebas de validación.
""", 3))
P(figura(9, "Diagrama de componentes generado por la IA (P3)", str(CAP / "P3-06.png"),
         "El diagrama de la IA resultó ilegible: líneas cruzadas, un recuadro vacío y nombres en dos idiomas. Se redibujó como la Figura 2. Fuente: Google AI Studio (2026).", ancho="52%"))
P(md("""
### Conclusiones sobre el uso de la IA
""" + ev.split("**Conclusiones sobre el uso de la IA:**")[1].strip(), 3))

# ---------------------------------------------------------------- 10. Video y repositorio
P(h(2, "Video de presentación y repositorio", "entregables"))
video = (f"[{YOUTUBE}]({YOUTUBE})" if YOUTUBE else
         '<span class="pendiente">[Enlace pendiente: se agrega cuando el video esté publicado en YouTube]</span>')
P(md(f"""
| Entregable | Enlace |
|---|---|
| Video o *pitch* en YouTube | {video} |
| Repositorio del proyecto (GitHub) | [{REPO}]({REPO}) |

El repositorio contiene el análisis, los seis modelos con sus archivos fuente (Mermaid y SVG) y exportados (PNG), las cinco decisiones arquitectónicas, el análisis de riesgos y todas las evidencias de Google AI Studio (respuestas completas, capturas y evaluación).
""", 3))

# ---------------------------------------------------------------- 11. Conclusiones
P(h(2, "Conclusiones y recomendaciones", "conclusiones"))
P(md("""
### Conclusiones

1. **Un monolito modular en capas cubre los 24 requerimientos** con menos complejidad y costo que una arquitectura de microservicios. La decisión se sostiene en los atributos de calidad del caso, en especial la consistencia de la matrícula (RNF-07), y no en preferencias tecnológicas.
2. **La matrícula es el corazón técnico del sistema.** Combina reglas de negocio, concurrencia y auditoría. Resolverla con una transacción, un bloqueo de fila y restricciones en la base de datos garantiza que no haya sobrecupo aunque falle la lógica de la aplicación.
3. **La disponibilidad del 99,5 % se logra eliminando los puntos únicos de falla internos** (nodos, balanceador y base de datos redundantes). Los riesgos residuales (Cloudflare y la región del proveedor) quedan identificados y aceptados de forma explícita.
4. **La trazabilidad es completa en el diseño:** cada requerimiento tiene componente, modelo, decisión y método de verificación. Los menos sustentados (accesibilidad y compatibilidad) dependen de la implementación de la interfaz.
5. **La IA aceleró el diseño, pero no lo reemplazó.** Acertó en lo estructural y aportó ideas valiosas, pero también sobredimensionó, se contradijo y repitió errores ya corregidos. Solo la revisión sistemática contra los requerimientos permitió aprovechar lo útil y descartar lo incorrecto.

### Recomendaciones

1. **Antes de implementar,** ejecutar las pruebas de validación de la sección 8: carga con 300 usuarios, concurrencia sobre el último cupo, caída de un nodo y simulacro de restauración.
2. **Validar con la institución** los supuestos (en especial quién matricula y los valores de RPO y RTO) y revisar los contratos de tratamiento de datos con los proveedores (Ley 1581 de 2012).
3. **Construir primero los módulos de mayor riesgo** (Identidad y acceso, y Matrículas) e incluir desde el inicio las pruebas de arquitectura que protegen los límites entre módulos.
4. **Si se habilita la automatrícula,** repetir la prueba de contención extrema y reconsiderar la estrategia de bloqueo antes de abrirla.
5. **Al usar IA en diseño de software,** hacer un análisis propio antes de consultarla, pedirle una autocrítica al final y registrar qué se acepta y qué no, con su justificación.
""", 3))

# ---------------------------------------------------------------- Referencias
P(h(2, "Referencias", "referencias", numerado=False))
P("""<div class="referencias">
<p>Bass, L., Clements, P., &amp; Kazman, R. (2021). <em>Software architecture in practice</em> (4.ª ed.). Addison-Wesley.</p>
<p>Congreso de la República de Colombia. (2012, 17 de octubre). <em>Ley Estatutaria 1581 de 2012, por la cual se dictan disposiciones generales para la protección de datos personales</em>. Diario Oficial n.º 48.587.</p>
<p>Google. (2026). <em>Gemini 3.8 Flash</em> [Modelo de lenguaje de gran tamaño]. Google AI Studio. https://aistudio.google.com</p>
<p>International Organization for Standardization. (2011). <em>Systems and software engineering: Systems and software Quality Requirements and Evaluation (SQuaRE). System and software quality models</em> (ISO/IEC 25010:2011).</p>
<p>Kendall, K. E., &amp; Kendall, J. E. (2011). <em>Análisis y diseño de sistemas</em> (8.ª ed.). Pearson Educación.</p>
<p>Kruchten, P. (1995). The 4+1 view model of architecture. <em>IEEE Software, 12</em>(6), 42–50. https://doi.org/10.1109/52.469759</p>
<p>Nygard, M. (2011, 15 de noviembre). <em>Documenting architecture decisions</em>. Cognitect. https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions</p>
<p>PostgreSQL Global Development Group. (2026). <em>PostgreSQL documentation: Explicit locking</em>. https://www.postgresql.org/docs/current/explicit-locking.html</p>
<p>Pressman, R. S., &amp; Maxim, B. R. (2021). <em>Ingeniería de software: Un enfoque práctico</em> (9.ª ed.). McGraw-Hill Education.</p>
<p>Richards, M., &amp; Ford, N. (2020). <em>Fundamentals of software architecture: An engineering approach</em>. O'Reilly Media.</p>
<p>Sommerville, I. (2011). <em>Ingeniería de software</em> (9.ª ed.). Pearson Educación.</p>
<p>World Wide Web Consortium. (2018). <em>Web Content Accessibility Guidelines (WCAG) 2.1</em>. https://www.w3.org/TR/WCAG21/</p>
</div>""")

# ---------------------------------------------------------------- Anexo A
P(h(2, "Anexo A. Evaluación detallada de las respuestas de la IA", "anexo-a", numerado=False))
ev_cuerpo = ev.split("---", 1)[1].split("## Resumen general")[0]
P(md(ev_cuerpo.replace("## P", "### P"), 3).replace("<h3>", '<h3 class="nonum">'))

# ---------------------------------------------------------------- Anexo B
P(h(2, "Anexo B. Capturas de la conversación en Google AI Studio", "anexo-b", numerado=False))
P('<p>Capturas en el orden de la conversación. La primera captura de cada prompt muestra el texto enviado; las siguientes, la respuesta. La captura P5-04 muestra al final el envío del prompt P6.</p>')
temas = {"P1": "Análisis del problema", "P2": "Estilo arquitectónico", "P3": "Componentes y vista lógica",
         "P4": "Modelo de datos conceptual", "P5": "Secuencia de la matrícula", "P6": "Despliegue, seguridad y respaldo",
         "P7": "Revisión crítica"}
for p, tema in temas.items():
    P(f'<h3 class="nonum anexo-p">{p} · {tema}</h3><div class="capturas">')
    for f in sorted(CAP.glob(f"{p}-*.png")):
        P(f'<figure class="cap"><img src="{f}" alt="{f.stem}"><figcaption>{f.stem}</figcaption></figure>')
    P("</div>")

# ---------------------------------------------------------------- Anexo C
guia = leer("ai-studio/GUIA-PROMPTS.md")
P(h(2, "Anexo C. Texto de los prompts", "anexo-c", numerado=False))
for bloque in re.findall(r"## (P\d · [^\n]+)\n\n```text\n(.*?)```", guia, flags=re.S):
    P(f'<h3 class="nonum">{bloque[0]}</h3><pre class="prompt">{bloque[1].replace("&", "&amp;").replace("<", "&lt;")}</pre>')

cuerpo = "\n".join(partes)
plantilla = (Path(__file__).parent / "plantilla.html").read_text(encoding="utf-8")
(Path(__file__).parent / "informe.html").write_text(plantilla.replace("{{CUERPO}}", cuerpo), encoding="utf-8")
print("informe.html generado")
