# 1. Análisis del problema y de los requerimientos

## 1.1 Descripción del problema

La institución administra la información académica en archivos y aplicaciones independientes. Esto produce tres problemas concretos:

| Problema actual | Consecuencia | Requerimientos que lo atacan |
|---|---|---|
| Datos duplicados en varias fuentes | Registros contradictorios de estudiantes, docentes y notas | RF-03, RF-04, RF-05, RNF-07 |
| Consultas lentas y manuales | Estudiantes y coordinadores esperan respuestas que deberían ser inmediatas | RF-09, RF-10, RF-11, RNF-02 |
| Sin trazabilidad | No se sabe quién cambió una nota, una matrícula o un rol, ni cuándo | RF-12, RNF-10 |

El SGA centraliza esta información en una sola fuente de verdad, con acceso web controlado por roles.

## 1.2 Actores

| Actor | Tipo | Qué hace en el sistema |
|---|---|---|
| **Administrador** | Principal | Gestiona usuarios, roles y permisos; registra y desactiva estudiantes y docentes; configura parámetros generales. |
| **Coordinador académico** | Principal | Gestiona programas, planes de estudio, asignaturas, periodos y grupos; asigna docentes; matricula estudiantes; genera reportes. |
| **Docente** | Principal | Consulta sus grupos y estudiantes; registra, actualiza y publica calificaciones. |
| **Estudiante** | Principal | Consulta sus asignaturas, horario y calificaciones publicadas. |
| **Servicio de respaldo** | Secundario (sistema) | Ejecuta copias de seguridad programadas de la base de datos. |
| **Plataformas institucionales** | Secundario (futuro) | Sistemas externos (financiero, LMS) que consumirán la API REST (RNF-08). |

## 1.3 Supuestos

Lo que el caso no dice explícitamente y asumimos para poder diseñar:

| Id | Supuesto |
|---|---|
| S-01 | "Personal autorizado" en RF-03 y RF-04 corresponde al rol **coordinador académico**, además del administrador. |
| S-02 | La matrícula la registra el **coordinador académico**. Dejar que el estudiante se automatricule queda como evolución futura; la arquitectura lo permite sin cambios estructurales. |
| S-03 | "Desactivar" (RF-03, RF-04) es una **baja lógica**: el registro cambia de estado y no se borra, para conservar el historial académico y la auditoría. |
| S-04 | Las calificaciones tienen dos estados: **borrador** y **publicada**. El estudiante solo ve las publicadas (RF-09). |
| S-05 | Un usuario puede tener **uno o varios roles** (por ejemplo, un docente que también coordina) con una sola cuenta. *(Ajustado tras la evaluación de la IA, P4.)* |
| S-06 | Escenario de referencia de RNF-02: **300 usuarios concurrentes**, con picos en semanas de matrícula y cierre de notas. |
| S-07 | La institución opera una sola sede lógica; no se requiere despliegue en varias regiones. |
| S-08 | El presupuesto es moderado: se prefieren servicios administrados o de código abierto frente a licencias costosas. |
| S-09 | El estudiante no puede modificar ningún dato académico; solo consulta. |

## 1.4 Restricciones

| Id | Restricción | Origen |
|---|---|---|
| R-01 | La aplicación debe ser **web** y funcionar en navegadores recientes, en computador y móvil. | Contexto, RNF-06, RNF-12 |
| R-02 | Comunicación **solo por HTTPS**. | RNF-01 |
| R-03 | Contraseñas almacenadas con **hash y sal**, nunca en texto plano. | RNF-01 |
| R-04 | Interfaces expuestas como **API REST documentada**. | RNF-08 |
| R-05 | Disponibilidad mensual objetivo de **99,5 %** (máximo unas 3,6 horas de caída no programada al mes). | RNF-03 |
| R-06 | El alcance de esta actividad es **arquitectura y modelos**; no se exige implementar el sistema completo. | Enunciado |
| R-07 | No usar datos personales reales ni credenciales en prompts, capturas o repositorios. | Enunciado, sección 10 |

## 1.5 Reglas de negocio

Reglas que el sistema debe validar en la capa de dominio (no solo en la interfaz):

| Id | Regla | Requerimiento |
|---|---|---|
| RN-01 | Un estudiante no puede matricularse **dos veces en el mismo grupo** ni en dos grupos de la **misma asignatura** en el mismo periodo. | RF-07 |
| RN-02 | No se puede matricular en un grupo **sin cupo disponible**. Con dos solicitudes simultáneas por el último cupo, solo una debe tener éxito. | RF-07, RNF-07 |
| RN-03 | Solo se matricula en grupos de un **periodo abierto** para matrícula. | RF-06, RF-07 |
| RN-04 | Solo se matriculan estudiantes **activos**. Un estudiante desactivado conserva su historial. | RF-03, RF-07 |
| RN-05 | Un docente solo registra o modifica calificaciones de **estudiantes matriculados en los grupos que tiene asignados**. | RF-08 |
| RN-06 | Las calificaciones deben estar dentro de la **escala** definida por la institución (supuesto: 0,0 a 5,0). | RF-08 |
| RN-07 | Toda modificación de una calificación **ya publicada** queda en auditoría con el valor anterior y el nuevo. | RF-08, RF-12 |
| RN-08 | El estudiante solo consulta **sus propios** datos; el docente, los de sus grupos; el coordinador, los de su programa. | RF-02, RNF-11 |
| RN-09 | El **código** de asignatura y el **identificador** de estudiante y docente son únicos. | RF-03, RF-04, RF-05 |
| RN-10 | Un grupo pertenece a una asignatura y a un periodo, y tiene un cupo máximo mayor que cero. | RF-06 |
| RN-11 | La matrícula y el registro de notas solo se permiten **dentro de las fechas** definidas para el periodo. Fuera de ellas, estudiantes y docentes solo consultan. *(Aporte de la IA, P1.)* | RF-06, RF-07, RF-08 |
| RN-12 | Cuando el coordinador **cierra las calificaciones** del periodo, el docente ya no puede editarlas. Un cambio posterior requiere autorización del administrador y queda en auditoría. *(Aporte de la IA, P1.)* | RF-08, RF-12 |
| RN-13 | Un estudiante no puede matricular dos grupos con **cruce de horario**, y un docente no puede tener asignados dos grupos en la misma franja. *(Aporte de la IA, P1.)* | RF-06, RF-07 |
| RN-14 | Los registros de auditoría son de **solo inserción**: nadie, ni el administrador, puede modificarlos ni borrarlos. *(Aporte de la IA, P1, ajustado.)* | RF-12, RNF-10 |
| RN-15 | En un grupo presencial, el **cupo no puede superar la capacidad del aula** asignada. *(Aporte de la IA, P7.)* | RF-06 |

## 1.6 Requerimientos funcionales

Prioridad según el método MoSCoW: **M** = debe tener, **S** = debería tener.

| Id | Requerimiento | Actor | Prioridad | Módulo responsable | Criterio de aceptación verificable |
|---|---|---|---|---|---|
| RF-01 | Autenticación | Todos | M | Identidad y acceso | Con credenciales válidas se obtiene sesión; con inválidas se rechaza; al cerrar sesión el token deja de servir. |
| RF-02 | Roles y permisos | Administrador | M | Identidad y acceso | Un estudiante que llama a un endpoint de docente recibe 403. |
| RF-03 | Gestión de estudiantes | Administrador, coordinador | M | Gestión académica | Se crea, consulta, edita y desactiva un estudiante; el desactivado no aparece en la matrícula. |
| RF-04 | Gestión de docentes | Administrador, coordinador | M | Gestión académica | Igual que RF-03 para docentes; el desactivado no se puede asignar a grupos. |
| RF-05 | Programas y asignaturas | Coordinador | M | Gestión académica | No se aceptan dos asignaturas con el mismo código. |
| RF-06 | Grupos y periodos | Coordinador | M | Gestión académica | Se crea un grupo con cupo, docente, horario y aula o enlace dentro de un periodo. |
| RF-07 | Matrícula académica | Coordinador | M | Matrículas | Con cupo y sin duplicado, se matricula; sin cupo o duplicado, se rechaza con mensaje claro. |
| RF-08 | Registro de calificaciones | Docente | M | Calificaciones | El docente registra notas solo en sus grupos; fuera de ellos recibe 403. |
| RF-09 | Consulta de resultados | Estudiante | M | Calificaciones, Matrículas | El estudiante ve su horario y solo las notas publicadas. |
| RF-10 | Reportes | Coordinador, administrador | S | Reportes | Reporte de matriculados filtrado por periodo y programa coincide con los datos de la base. |
| RF-11 | Búsqueda y filtros | Usuarios autorizados | S | Transversal (cada módulo) | Buscar por identificador, nombre, programa, periodo o estado devuelve solo resultados permitidos para el rol. |
| RF-12 | Auditoría | Administrador (consulta) | M | Auditoría | Cada inicio de sesión, cambio de rol, matrícula y cambio de nota genera un registro con usuario, fecha, acción y registro afectado. |

## 1.7 Requerimientos no funcionales

| Id | Requerimiento | Atributo de calidad (ISO/IEC 25010) | Escenario o medida verificable | Táctica arquitectónica principal |
|---|---|---|---|---|
| RNF-01 | Seguridad | Seguridad | 100 % del tráfico por HTTPS; contraseñas con hash bcrypt o Argon2; prueba de acceso sin permiso devuelve 403. | TLS en el balanceador, hash de contraseñas, autorización por roles en la API. |
| RNF-02 | Rendimiento | Eficiencia de desempeño | Con 300 usuarios concurrentes en carga normal, el percentil 95 de consultas comunes ≤ 3 s. | Índices en la base, paginación, consultas de reportes separadas, caché de catálogos. |
| RNF-03 | Disponibilidad | Fiabilidad | Disponibilidad mensual ≥ 99,5 % sin contar mantenimientos programados. | Dos o más instancias de la API sin estado detrás de un balanceador; base de datos administrada con réplica. |
| RNF-04 | Escalabilidad | Eficiencia de desempeño / Flexibilidad | Duplicar instancias de la API sin cambiar código. | API sin estado (sesión en token), escalado horizontal. |
| RNF-05 | Mantenibilidad | Mantenibilidad | Cambiar una regla de calificaciones solo toca el módulo Calificaciones. | Monolito modular por contextos, capas y dependencias hacia interfaces. |
| RNF-06 | Usabilidad y accesibilidad | Usabilidad | Funciones principales operables con teclado; contraste mínimo WCAG 2.1 AA. | Interfaz web responsiva con componentes accesibles. |
| RNF-07 | Integridad y consistencia | Fiabilidad (integridad) | Prueba de concurrencia: 2 solicitudes simultáneas por el último cupo dejan 1 matrícula. | Transacción con bloqueo de fila sobre el grupo y restricción única en la base. |
| RNF-08 | Interoperabilidad | Compatibilidad | Especificación OpenAPI publicada para todos los endpoints. | API REST documentada con OpenAPI. |
| RNF-09 | Respaldo y recuperación | Fiabilidad (recuperabilidad) | Pérdida máxima de 15 min de datos (RPO) y restauración en menos de 2 h (RTO); simulacro de restauración trimestral exitoso. | Respaldo diario completo más archivado continuo del WAL, cifrado y fuera del centro de datos principal (ADR-003). |
| RNF-10 | Trazabilidad | Mantenibilidad / Calidad del proceso | Cada RF y RNF aparece en la matriz con componente y método de verificación. | Matriz de trazabilidad y registros de decisiones (ADR). |
| RNF-11 | Privacidad | Seguridad (confidencialidad) | Un estudiante no puede consultar datos de otro estudiante. | Filtros por propietario y alcance del rol en el dominio. |
| RNF-12 | Compatibilidad | Compatibilidad / Portabilidad | Funciona en las dos últimas versiones de Chrome, Edge, Firefox y Safari, en 360 px y en 1366 px. | Interfaz web estándar y diseño responsivo. |

## 1.8 Observaciones del análisis

- **Los RNF que más pesan en la arquitectura** son RNF-03 (disponibilidad), RNF-05 (mantenibilidad) y RNF-07 (consistencia). Son los que deciden el estilo arquitectónico; los demás se resuelven con tácticas puntuales.
- **RNF-02 pide un escenario de calidad completo.** Fuente: estudiantes y docentes. Estímulo: consultas comunes. Artefacto: API y base de datos. Entorno: operación normal con 300 usuarios concurrentes. Respuesta: devolver los datos. Medida: el 95 % en 3 s o menos.
- **RNF-09 no da cifras.** Se propone un RPO de 15 minutos y un RTO de 2 horas. La propuesta inicial era de 24 h y 4 h; se mejoró tras evaluar la respuesta P6 de la IA, porque los servicios administrados ya incluyen recuperación a un punto en el tiempo. La institución debe confirmar estos valores.
- **RNF-10 se cumple con el propio informe:** la matriz de trazabilidad y los ADR son su evidencia.
