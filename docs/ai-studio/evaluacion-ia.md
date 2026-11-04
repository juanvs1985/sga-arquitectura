# Evaluación crítica de las respuestas de Google AI Studio

**Modelo:** Gemini 3.8 Flash (`gemini-3.8-flash`) · Thinking level: High · Grounding con Google Search: desactivado
**Fecha:** 4 de noviembre de 2026
**Conversación original:** [Google AI Studio](https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221NcbJ3YkHGzE2xID9EykCrpI4RXmgqqe8%22%5D,%22action%22:%22open%22,%22userId%22:%22113748348275050694995%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing)
**Método:** cada propuesta de la IA se contrastó con el enunciado (RF/RNF), con el alcance de la actividad y con el análisis propio del documento `01-analisis-requisitos.md`.

Convención: **Aceptado** = se incorpora tal cual · **Modificado** = se incorpora con cambios · **Descartado** = no se incorpora.

---

## P1 · Análisis del problema

| # | Propuesta de la IA | Decisión | Justificación |
|---|---|---|---|
| 1.1 | Cuatro actores principales: estudiante, docente, coordinador académico, administrador. | Aceptado | Coincide con RF-02 y con el análisis propio. |
| 1.2 | El **estudiante realiza su propia matrícula**. | Modificado | RF-07 no dice quién matricula. Mantenemos al coordinador como responsable (supuesto S-02) para reducir el riesgo de concurrencia masiva en esta primera versión. La autoinscripción queda como evolución: la API de matrícula es la misma y solo cambia el permiso. |
| 1.3 | **Servicio de auditoría** como actor secundario. | Modificado | La auditoría es un módulo interno del sistema (RF-12), no un actor externo. Se modela como componente, no en el diagrama de casos de uso. |
| 1.4 | Servicio de copias de seguridad como actor secundario. | Aceptado | Coincide con el análisis propio (RNF-09). |
| 1.5 | **Servicio de notificaciones** (correo/SMS). | Descartado | Ningún RF lo pide. Agregarlo amplía el alcance sin requisito que lo justifique. Se menciona como recomendación futura. |
| 1.6 | Baja lógica (soft delete) al desactivar estudiantes y docentes. | Aceptado | Igual al supuesto S-03; preserva el historial y la integridad referencial. |
| 1.7 | **Ventanas de tiempo** para matrícula y registro de notas. | Aceptado | Amplía nuestra regla RN-03 (periodo abierto). Se agrega como RN-11. |
| 1.8 | Calificaciones ponderadas en escala 0,0–5,0 con nota aprobatoria configurable. | Aceptado | Coincide con RN-06. |
| 1.9 | **Validar cruces de horario** de estudiantes y docentes. | Aceptado | Buena regla que el análisis propio no tenía. Se agrega como RN-13. |
| 1.10 | Control de concurrencia en la matrícula: optimista, pesimista **o colas**. | Modificado | Se elige bloqueo pesimista de la fila del grupo dentro de una transacción, más una restricción única en la base. Las colas se descartan: con 300 usuarios concurrentes agregan complejidad sin beneficio (ver ADR-002). |
| 1.11 | Desacoplar el proveedor de identidad para un SSO futuro (OAuth2, SAML, Google o Microsoft). | Modificado | Se acepta como punto de extensión del módulo Identidad y acceso, pero queda fuera del alcance actual: RF-01 pide credenciales propias. |
| 1.12 | Restricciones técnicas: navegador, API REST con OpenAPI, TLS, hash Argon2id o bcrypt, 3,6 h de caída al mes. | Aceptado | Coinciden con R-01 a R-05. |
| 1.13 | Caché con **Redis** para catálogos y **CDN** para estáticos. | Pendiente (se decide en P2) | Hay que validar si se justifican para 300 usuarios y presupuesto moderado. |
| 1.14 | Auditoría **WORM** (almacenamiento de una sola escritura). | Modificado | WORM es costoso para el presupuesto supuesto (S-08). Se cumple el mismo objetivo con una tabla de auditoría de solo inserción: la cuenta de la aplicación no tiene permisos de UPDATE ni DELETE sobre ella. |
| 1.15 | Cierre y **congelamiento de calificaciones**: después del cierre, el docente no edita; cualquier cambio requiere autorización con auditoría. | Aceptado | Regla valiosa que el análisis propio no tenía. Se agrega como RN-12. |
| 1.16 | Auditoría inmutable (solo adición). | Aceptado | Se agrega como RN-14, implementada como se indica en 1.14. |
| 1.17 | Control de acceso **ABAC/RBAC**. | Modificado | Se usa RBAC (RF-02) más filtros de propiedad en el dominio ("solo lo mío", "solo mis grupos"). ABAC completo no se justifica en este alcance. |
| 1.18 | Clasificación de los RNF según ISO/IEC 25010. | Aceptado | Coincide con la tabla 1.7 del análisis. Se adopta la subcaracterística "Recuperabilidad" para RNF-09. |
| 1.19 | IDs de correlación en las trazas (RNF-10). | Aceptado | Mejora la trazabilidad técnica de cada petición entre los módulos y la auditoría. |

**Balance P1:** 11 aceptadas, 6 modificadas, 1 descartada, 1 pendiente. La IA aportó tres reglas de negocio que el análisis propio no tenía: ventanas de tiempo, cierre de calificaciones y cruces de horario. En cambio, tendió a sobredimensionar la solución (WORM, colas, notificaciones, ABAC) frente al tamaño del problema.

---

## P2 · Estilo arquitectónico

| # | Propuesta de la IA | Decisión | Justificación |
|---|---|---|---|
| 2.1 | Recomendar **monolito modular** con una base de datos relacional y API REST. | Aceptado | Coincide con la decisión que el equipo ya había tomado antes de consultar a la IA. Se documenta en ADR-001 con argumentos propios: tamaño del sistema, 300 usuarios concurrentes, consistencia de la matrícula y un solo desarrollador. |
| 2.2 | Presentar "capas" y "monolito modular" como **alternativas excluyentes**, y advertir que las capas terminan en una "gran bola de lodo". | Modificado | No son excluyentes. La propuesta final combina ambos: módulos verticales por contexto de negocio y, dentro de cada módulo, capas de presentación (controlador), dominio y repositorio. El riesgo de la gran bola de lodo viene de no tener límites entre módulos, no de usar capas. |
| 2.3 | Descartar microservicios por complejidad operativa, latencia de red y consistencia eventual (Sagas) en la matrícula. | Aceptado | Argumento correcto y verificable. Además, el equipo es de una persona, lo que refuerza el descarte. |
| 2.4 | Bloqueo pesimista (`SELECT … FOR UPDATE`) **o** control optimista para los cupos. | Modificado | Se elige el bloqueo pesimista de la fila del grupo más una restricción única. Con contención alta por el último cupo, el control optimista produce muchos reintentos fallidos (ver ADR-002). |
| 2.5 | **Partición lógica de esquemas**: una base de datos con un esquema por módulo. | Aceptado | Refuerza el bajo acoplamiento: cada módulo es dueño de sus tablas y los demás solo acceden por su interfaz pública. Facilita extraer un módulo en el futuro. |
| 2.6 | 2 o 3 réplicas en contenedores Docker detrás de un balanceador para el 99,5 %. | Aceptado | Se fijan 2 réplicas como mínimo. Requisito previo: la API debe ser sin estado (sesión en token, no en memoria). |
| 2.7 | Auditoría mediante **interceptores (middleware)**. | Modificado | Un middleware no conoce el valor anterior y el nuevo de una nota. Se usa middleware para los inicios de sesión, y para matrículas, notas y roles el módulo de dominio escribe el registro de auditoría **dentro de la misma transacción** del cambio: si el cambio se guarda, la auditoría también. |
| 2.8 | Afirmaciones como rendimiento "excelente" o "supera con holgura los 3 s". | Modificado | Son afirmaciones no verificadas. Se convierten en hipótesis que se comprobarán con una prueba de carga de 300 usuarios virtuales (ver matriz de trazabilidad, RNF-02). |
| 2.9 | Si un módulo crece, extraerlo a microservicio en el futuro. | Aceptado | Se documenta como camino de evolución con el patrón Strangler Fig. |
| 1.13 | (Pendiente del P1) Caché con **Redis** y **CDN**. | Redis: Descartado · CDN: Modificado | Redis: con 300 usuarios y sesión en token no hay estado compartido que guardar; los catálogos (programas, asignaturas) se cachean en memoria de cada réplica. Se reconsidera si la prueba de carga no cumple RNF-02. CDN: la interfaz web estática se publica en un hosting que ya incluye distribución por CDN, sin costo ni componente adicional. |

**Balance P2:** 5 aceptadas, 5 modificadas (incluido el pendiente del P1). La recomendación de la IA coincide con la del equipo, pero la propuesta final corrige tres puntos: capas y módulos se combinan, la auditoría va en la misma transacción y el rendimiento se trata como una hipótesis por verificar.

---

## P3 · Componentes y vista lógica

| # | Propuesta de la IA | Decisión | Justificación |
|---|---|---|---|
| 3.1 | Seis módulos: autenticación y autorización, gestión académica, matrícula, calificaciones, reportes y búsqueda, auditoría. | Aceptado | Coinciden con los seis módulos de ADR-001. En el modelo final se nombran en español para mantener la consistencia con las entidades del enunciado. |
| 3.2 | Interfaces internas `IAcademicQueryService` e `IEnrollmentQueryService`, sin consultas SQL de un módulo a las tablas de otro. | Aceptado | Aplica el principio de inversión de dependencias y protege los límites entre módulos (RNF-05). Se renombran `IConsultaAcademica` e `IConsultaMatriculas`. |
| 3.3 | Dependencias: Matrícula → Gestión académica; Calificaciones → Gestión académica y Matrícula. | Aceptado | No hay ciclos entre módulos. Se verifica en el diagrama propio. |
| 3.4 | **"API Gateway"** como capa de entrada. | Modificado | En un monolito no hace falta un producto de API Gateway aparte. La seguridad (JWT, roles, límite de peticiones, manejo de errores) es un *pipeline* de middleware dentro de la misma aplicación, y el HTTPS termina en el balanceador (vista de despliegue). |
| 3.5 | Auditoría por un **bus de eventos en memoria asíncrono**. | Modificado | Error de diseño. Si el proceso se cae después de guardar la nota pero antes de procesar el evento, el cambio queda sin auditar, lo que viola RF-12. Además, la respuesta se contradice: en un punto dice "asíncrona" y en otro "sincrónicamente". Se reemplaza por la interfaz `IRegistroAuditoria`, que el módulo llama **dentro de la misma transacción** del cambio (ADR-005). |
| 3.6 | La matrícula abre la transacción en el esquema `enrollment`, pero bloquea la **fila del grupo**, que vive en el esquema académico. | Modificado | Inconsistencia: Matrícula estaría escribiendo en tablas de Gestión académica y rompería el aislamiento que la misma IA defiende en 3.2. Se resuelve con lo que la IA ya insinuaba en su esquema (`Quotas`): Matrícula es dueña de la tabla `cupo_grupo` (cupo máximo y ocupados) y el bloqueo se hace sobre esa fila (ADR-002). |
| 3.7 | Cerrar sesión con **lista negra de tokens en Redis**. | Modificado | Redis se descartó en P2. Se usa un token de acceso de vida corta (15 min) más un token de renovación guardado en el esquema de identidad, que se revoca al cerrar sesión (ADR-004). |
| 3.8 | Endpoints REST versionados `/api/v1/...` por módulo. | Aceptado | Cumple RNF-08. Se documentarán con OpenAPI. |
| 3.9 | Faltan endpoints para **publicar** calificaciones y **cerrar** el periodo de notas. | Modificado (agregado) | Sin ellos no se cumplen RF-09 (el estudiante solo ve notas publicadas) ni RN-12 (cierre). Se agregan `POST /calificaciones/grupos/{id}/publicar` y `POST /academico/periodos/{id}/cerrar-notas`. |
| 3.10 | Prerrequisitos de asignaturas y datos de *tenant*. | Descartado | Ningún RF pide prerrequisitos ni multiinstitución. Se dejan como evolución futura. |
| 3.11 | Reportes con lectura directa de varias tablas mediante vistas SQL (CQRS ligero) y **réplicas de lectura**. | Modificado | Se aceptan las vistas de solo lectura con un usuario de base de datos sin permisos de escritura. La réplica de lectura solo se agrega si la prueba de carga muestra que los reportes afectan a RNF-02. |
| 3.12 | Búsqueda global `GET /search?q=` en el módulo de reportes. | Modificado | RF-11 pide buscar "según el módulo". La búsqueda va en los listados de cada módulo (`?q=&periodo=&programa=&estado=`) y aplica los filtros del rol (RNF-11). |
| 3.13 | Exportar reportes a PDF y Excel. | Modificado | RF-10 pide reportes básicos. Exportar a CSV queda como "debería" y a PDF como "podría". |
| 3.14 | Justificación obligatoria al modificar una nota, guardada en la auditoría. | Aceptado | Refuerza RN-12 y RF-12. |
| 3.15 | Diagrama Mermaid generado. | Modificado | El código es válido, pero el diagrama resultante es **ilegible** (ver `P3-diagrama-ia.png`): muchas líneas cruzadas, el bus de eventos aparece como un recuadro vacío y mezcla nombres en inglés y español. El modelo final se redibuja en dos diagramas más simples (módulos y estructura interna de un módulo). |

**Balance P3:** 5 aceptadas, 9 modificadas, 1 descartada. Fue la respuesta con más correcciones. La IA describió bien los módulos y sus interfaces, pero su propuesta de auditoría asíncrona y el bloqueo sobre tablas de otro módulo contradecían requisitos y principios que ella misma había defendido en P2.

---

## P4 · Modelo de datos conceptual

| # | Propuesta de la IA | Decisión | Justificación |
|---|---|---|---|
| 4.1 | Las diez entidades del enunciado más `Horario`, `UsuarioRol` y `Auditoria`, con atributos y claves. | Aceptado | Cubre las entidades exigidas en 6.4. El diagrama ER generado es legible (`P4-diagrama-ia.png`). |
| 4.2 | Relación **M:N entre Usuario y Rol** (`UsuarioRol`). | Aceptado | Mejor que nuestro supuesto S-05 (un rol por usuario): resuelve con naturalidad al docente que además coordina. Se actualiza S-05. |
| 4.3 | Estudiante y Docente como extensión 1:0..1 de Usuario. | Aceptado | Separa las credenciales (Identidad) de los datos académicos (Gestión académica). |
| 4.4 | Matrícula en **cabecera y detalle** (`Matricula` por periodo y `DetalleMatricula` por grupo). | Aceptado | Representa bien "matricular en asignaturas o grupos de un periodo" (RF-07). |
| 4.5 | `id_asignatura` **desnormalizado** en `DetalleMatricula` para la restricción única. | Modificado | Sin control, un detalle podría quedar con un grupo de una asignatura y un `id_asignatura` de otra. Se agrega una clave foránea compuesta `(id_grupo, id_asignatura)` → `Grupo(id_grupo, id_asignatura)` que obliga a que coincidan. |
| 4.6 | `cupo_ocupado` dentro de **Grupo** y bloqueo `FOR UPDATE` sobre Grupo. | Modificado | Repite el error del P3: Matrícula escribiría en tablas de Gestión académica. Grupo conserva `cupo_maximo` y se agrega la entidad **CupoGrupo** (1:1 con Grupo, del módulo Matrículas) con `ocupados` (ADR-002). |
| 4.7 | `porcentaje` del corte guardado en **cada calificación**. | Modificado | Error de normalización: el 30 % del "Parcial 1" se repetiría en la nota de cada estudiante y podría quedar distinto entre ellos. Se crea la entidad **Evaluacion** (corte del grupo con nombre y porcentaje); `Calificacion` queda como la nota de un estudiante en una evaluación. |
| 4.8 | Calificación **sin estado de publicación**. | Modificado (agregado) | RF-09 exige que el estudiante vea solo notas publicadas. Se agrega `estado` (Borrador o Publicada) en Calificación. |
| 4.9 | Asignatura cuelga directamente de Programa; **no hay plan de estudios**. | Modificado (agregado) | RF-05 pide gestionar planes de estudio. Se agrega **PlanEstudio** (Programa 1:N PlanEstudio 1:N Asignatura). |
| 4.10 | PeriodoAcademico solo con fecha de inicio, fecha de fin y estado. | Modificado | Faltan las fechas de matrícula y de registro de notas, y el cierre (RN-11, RN-12). Se agregan `inicio_matricula`, `fin_matricula`, `limite_notas` y `notas_cerradas`. |
| 4.11 | Restricciones únicas `(id_estudiante, id_periodo)`, `(id_matricula, id_asignatura)`, `(id_matricula, id_grupo)` y `CHECK (ocupados <= cupo_maximo)`. | Aceptado | Son la segunda barrera de ADR-002 en la base de datos. El CHECK pasa a la entidad CupoGrupo. |
| 4.12 | Cruce de horarios con `EXCLUDE USING GIST`. | Descartado | Esa restricción compara filas de una misma tabla; el cruce de un estudiante involucra Horario, Grupo y DetalleMatricula. Se valida en el servicio de dominio dentro de la transacción (RN-13). |
| 4.13 | Auditoría con valores anteriores y nuevos en JSONB. | Aceptado | Cumple RF-12 y ADR-005. Se descarta otra vez la etiqueta WORM (ver 1.14). |
| 4.14 | Falta la entidad para los **tokens de renovación**. | Modificado (agregado) | ADR-004 la necesita para poder cerrar sesión. Se agrega **Sesion** en el esquema de identidad. |

**Balance P4:** 6 aceptadas, 7 modificadas, 1 descartada. El modelo de la IA es sólido como base, pero le faltaban tres elementos que el enunciado pide (planes de estudio, notas publicadas y fechas del periodo) y tenía un problema de normalización en los porcentajes.

---

## P5 · Secuencia de la matrícula

| # | Propuesta de la IA | Decisión | Justificación |
|---|---|---|---|
| 5.1 | Escenario de dos solicitudes simultáneas por el último cupo: Tx1 bloquea, Tx2 espera, Tx1 confirma, Tx2 lee 30/30, revierte y recibe **409 Conflict**. | Aceptado | Es exactamente el comportamiento que exige RNF-07 y el escenario de prueba de ADR-002. |
| 5.2 | **Ordenar los `id_grupo` de forma ascendente** antes de bloquear cuando se matriculan varios grupos a la vez. | Aceptado | Aporte valioso que el equipo no había considerado: evita interbloqueos (*deadlocks*) entre dos matrículas con grupos en común. Se agrega a ADR-002. |
| 5.3 | Bloqueo sobre la tabla **Grupo**. | Modificado | Mismo error que en P3 y P4. El bloqueo va sobre CupoGrupo (ADR-002). |
| 5.4 | Valida el estado del estudiante y los duplicados **después** de tomar el bloqueo. | Modificado | Así el bloqueo se retiene más tiempo del necesario. Las validaciones que no dependen del cupo (estudiante activo, periodo abierto, cruce de horario) se hacen **antes** del bloqueo. Dentro del bloqueo solo quedan el cupo, el duplicado y la escritura. |
| 5.5 | Auditoría **asíncrona** después del COMMIT "para no frenar la respuesta". | Modificado | Tercera vez que la IA lo propone. Se mantiene ADR-005: la auditoría va dentro de la transacción. Una inserción adicional cuesta milisegundos y garantiza que ninguna matrícula quede sin registro. |
| 5.6 | Bloqueo retenido "≤ 15 ms". | Modificado | Es una cifra no verificada. Se trata como hipótesis y se mide en la prueba de concurrencia de ADR-002. |
| 5.7 | No define qué pasa si la espera del bloqueo se alarga. | Modificado (agregado) | Se agrega un tiempo máximo de espera (`lock_timeout` de 5 s) con respuesta "intente de nuevo" (503), para no agotar las conexiones del pool. |
| 5.8 | El actor que matricula es el **estudiante**. | Modificado | Según el supuesto S-02, en esta versión matricula el coordinador. El flujo es el mismo; solo cambia el rol autorizado. |
| 5.9 | Participante "API Gateway / Auth". | Modificado | Se reemplaza por el pipeline de seguridad dentro del monolito (ver 3.4). |

**Balance P5:** 2 aceptadas, 7 modificadas. La IA resolvió bien el problema central de concurrencia y aportó la regla de ordenar los bloqueos. Pero insistió en la auditoría asíncrona y en bloquear la tabla de otro módulo, aunque ya se habían corregido.

---

## P6 · Despliegue, seguridad y respaldo

| # | Propuesta de la IA | Decisión | Justificación |
|---|---|---|---|
| 6.1 | **Cloudflare** (plan gratuito) delante del sistema: TLS, mitigación de DDoS, WAF básico y CDN. | Aceptado | Cubre RNF-01 y la CDN que quedó pendiente en P2 sin costo adicional. También permite el límite de peticiones (*rate limiting*) en el borde. |
| 6.2 | Interfaz web compilada en **almacenamiento de objetos + CDN**. | Aceptado | Los servidores de la API no gastan CPU en archivos estáticos. |
| 6.3 | Balanceador (Nginx o el del proveedor) con *health checks* y **2 instancias** de la API (2 vCPU, 4 GB) en red privada. | Aceptado | Coincide con ADR-001 y ADR-004. El tamaño de las máquinas es una estimación que se confirma con la prueba de carga (RNF-02). |
| 6.4 | **Redis** para lista negra de tokens, límite de peticiones y caché. | Descartado | Cuarta vez que la IA lo propone. Ya se resolvió sin Redis: los tokens en ADR-004, el límite de peticiones en Cloudflare y la caché de catálogos en memoria (P2). Agregarlo sumaría un componente y un punto de falla sin necesidad. |
| 6.5 | **PostgreSQL administrado con réplica en espera** y conmutación automática (60 a 120 s). | Aceptado | Elimina el punto único de falla que ADR-001 había dejado abierto. Se exige que la réplica esté en otra zona de disponibilidad. Se documenta en ADR-003. |
| 6.6 | Base de datos en **subred privada** sin IP pública; el puerto 5432 solo acepta tráfico de los nodos de la API; conexiones con TLS. | Aceptado | Defensa en profundidad para RNF-01 y RNF-11. |
| 6.7 | Secretos (llaves JWT, credenciales) fuera del repositorio, inyectados por un **gestor de secretos**. | Aceptado | Cumple además la indicación del enunciado de no publicar credenciales en el repositorio. |
| 6.8 | Token de renovación de **7 días** con rotación en cada uso. | Modificado | Se acepta la rotación (mejora ADR-004). Se mantiene una vigencia de 8 horas: en una institución educativa muchos usuarios entran desde computadores compartidos (salas, bibliotecas), y 7 días es demasiado. |
| 6.9 | **RPO ≤ 15 min** y **RTO ≤ 2 h** con respaldo diario completo más archivado continuo del WAL (recuperación a un punto en el tiempo). | Aceptado | Mejora nuestra propuesta inicial (RPO 24 h, RTO 4 h) con bajo costo, porque los servicios administrados ya incluyen PITR. Se actualiza RNF-09 en el análisis. |
| 6.10 | Respaldos cifrados (AES-256) en almacenamiento externo, regla 3-2-1, **Object Lock** con retención de 30 días. | Aceptado | Protege contra borrado accidental y *ransomware*. A diferencia de la auditoría (1.14), aquí el bloqueo de objetos es una función barata del almacenamiento y sí se justifica. |
| 6.11 | Restauración con un script probado **cada trimestre** en un entorno de pruebas. | Aceptado | Es la evidencia de cumplimiento de RNF-09 en la matriz de trazabilidad. |
| 6.12 | Despliegues **rolling update** sin interrupción. | Aceptado | Evita que las actualizaciones consuman el margen de 3,6 h de RNF-03. |
| 6.13 | No menciona **monitoreo ni alertas**. | Modificado (agregado) | Sin monitoreo no se puede medir el 99,5 % ni reaccionar a tiempo. Se agrega un monitor externo de disponibilidad con alertas, y registros centralizados con el identificador de correlación. |
| 6.14 | No considera que Cloudflare y el proveedor de nube **procesan datos personales** de estudiantes. | Modificado (agregado) | En Colombia aplica la Ley 1581 de 2012 (habeas data). Se registra como riesgo que requiere validar los contratos de tratamiento de datos con los proveedores. |
| 6.15 | Diagrama de despliegue generado. | Modificado | Otra vez ilegible (`P6-diagrama-ia.png`): textos que no se leen y flechas sueltas. Se redibuja. |

**Balance P6:** 10 aceptadas, 4 modificadas, 1 descartada. Fue la respuesta más útil de las seis: elevó el nivel de la propuesta en disponibilidad y respaldo.

---

## P7 · Revisión crítica de la propia propuesta

La IA criticó **su propia** propuesta de esta conversación. Varias de sus críticas más graves apuntan a elementos que el equipo ya había corregido en las evaluaciones anteriores. Eso confirma esas correcciones.

| # | Crítica de la IA | Decisión | Justificación |
|---|---|---|---|
| 7.1 | **Redis único** es punto único de falla (límite de peticiones, lista negra, caché). | Ya resuelto | Redis se descartó en P2, P3 y P6. El diseño final no lo usa. |
| 7.2 | La auditoría por **bus de eventos en memoria** se pierde si el proceso cae después del COMMIT; sugiere el patrón *Outbox*. | Ya resuelto | ADR-005 escribe la auditoría en la misma transacción del cambio. Es más simple que *Outbox* y no deja eventos pendientes. La prueba de caos que propone la IA (`kill -9` durante matrículas) se adopta para **demostrar** que no hay discrepancias. |
| 7.3 | Bloqueo sobre la **tabla Grupo**. | Ya resuelto | ADR-002 bloquea `cupo_grupo`, que pertenece al módulo Matrículas. |
| 7.4 | **Balanceador único** como punto único de falla. | Aceptado | Crítica válida. Se usa el balanceador administrado del proveedor, que es redundante por diseño, en lugar de un Nginx propio en una sola máquina. Se actualiza ADR-003. |
| 7.5 | **Agotamiento del pool de conexiones** de PostgreSQL con dos nodos. | Aceptado | Se fija un pool máximo por nodo (20 conexiones) y se usa el *pooler* que ofrece el servicio administrado (tipo PgBouncer). Se actualiza ADR-003. |
| 7.6 | **Contención extrema** si 250 usuarios piden el mismo grupo al mismo tiempo: la cola de bloqueos supera los 3 s. | Modificado | El riesgo es real si se habilita la automatrícula. Hoy matricula el coordinador (S-02), lo que reduce mucho la concurrencia. Se agrega a ADR-002 una **lectura previa sin bloqueo**: si el grupo ya está lleno, se rechaza de inmediato sin hacer cola. Se valida con la prueba de 300 usuarios sobre 5 cupos que propone la IA. |
| 7.7 | Los **reportes pesados** degradan el pool transaccional en el cierre de notas. | Aceptado | Los reportes usan un pool de conexiones separado y pequeño, con tiempo máximo por consulta. La réplica de lectura se activa si la prueba de carga lo exige (ver 3.11). |
| 7.8 | La **capacidad del aula** no se considera: un grupo de 40 podría quedar en un aula de 25. | Aceptado | Buena observación sobre RF-06. Se agrega la entidad **Aula** con su capacidad y la regla RN-15: en grupos presenciales, el cupo no puede superar la capacidad del aula. |
| 7.9 | Un **superusuario de la base de datos** puede alterar la auditoría. | Aceptado | Riesgo residual real. Se mitiga con una exportación diaria de los eventos de auditoría al almacenamiento con bloqueo de objetos (el mismo de los respaldos, ADR-003) y con el registro de actividad del propio servicio administrado. Así, una alteración posterior se puede detectar comparando. |
| 7.10 | **Usuarios con varios roles** sin un contexto de sesión activo. | Aceptado | Crítica válida que surge de aceptar el M:N en P4. El usuario elige el perfil con el que entra y el token lleva un único **rol activo**. Los permisos se evalúan con ese rol. Se actualiza ADR-004. |
| 7.11 | RNF-06 sin verificación automática. | Aceptado | Se incluyen axe-core y Lighthouse CI en el pipeline de integración continua (matriz de trazabilidad, RNF-06). |
| 7.12 | RNF-10 sin estándar de ADR ni versionado de la API. | Modificado | La IA no conoce los ADR del equipo (ADR-001 a ADR-005 ya existen). Se acepta lo que sí faltaba: versionado semántico de la especificación OpenAPI y commits que citan el requerimiento (por ejemplo, `RF-07: …`). |
| 7.13 | Faltan **prerrequisitos** de asignaturas (RF-05). | Descartado | RF-05 no los pide (pide código, nombre, créditos y semestre). Ya se había descartado en 3.10. Queda como evolución futura. |
| 7.14 | Calificación **a ciegas** (*blind grading*). | Descartado | No lo pide ningún requerimiento, y el docente necesita saber a quién califica. La privacidad de las notas ya la cubre RNF-11 con filtros por rol y propietario. |
| 7.15 | Plan de validación: prueba de concurrencia extrema, prueba de caos, simulacro de desastre y prueba de carga con mezcla 70 % lecturas, 20 % matrículas y 10 % reportes, de 50 a 500 usuarios. | Aceptado | Plan concreto y medible. Se incorpora al análisis de riesgos y a la matriz de trazabilidad. |

**Balance P7:** 8 aceptadas, 2 modificadas, 2 descartadas y 3 que ya estaban resueltas.

---

## Resumen general

| Prompt | Aceptadas | Modificadas | Descartadas | Ya resueltas / pendientes |
|---|---|---|---|---|
| P1 Análisis | 11 | 6 | 1 | 1 pendiente (resuelto en P2) |
| P2 Estilo | 5 | 5 | — | — |
| P3 Componentes | 5 | 9 | 1 | — |
| P4 Datos | 6 | 7 | 1 | — |
| P5 Secuencia | 2 | 7 | — | — |
| P6 Despliegue | 10 | 4 | 1 | — |
| P7 Autocrítica | 8 | 2 | 2 | 3 ya resueltas |
| **Total** | **47** | **40** | **6** | |

*La fila P2 incluye la decisión pendiente del P1 sobre Redis y la CDN, contada como modificada.*

**Conclusiones sobre el uso de la IA:**

1. **Acertó en lo estructural.** Recomendó el mismo estilo que el equipo (monolito modular), los mismos módulos y el bloqueo pesimista. Su comparación de estilos y su plan de pruebas fueron de buena calidad.
2. **Aportó ideas que el equipo no tenía:** el cierre de calificaciones, el cruce de horarios, el orden de los bloqueos para evitar interbloqueos, la recuperación a un punto en el tiempo, la capacidad del aula y el contexto de rol activo.
3. **Tendió a sobredimensionar:** Redis (cuatro veces), WORM, colas, notificaciones y ABAC, que agregan costo y componentes sin un requerimiento que los pida.
4. **Fue inconsistente consigo misma:** defendió el aislamiento entre módulos y después bloqueó tablas de otro módulo; dijo "asíncrona" y "sincrónica" para la misma auditoría. Repitió errores ya corregidos en prompts siguientes. **No basta con corregirla una vez: cada respuesta se debe revisar contra los requerimientos.**
5. **Los diagramas que generó fueron ilegibles** en tres de cuatro casos. Los modelos finales se redibujaron.
