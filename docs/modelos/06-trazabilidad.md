# 6.6 Matriz de trazabilidad de requerimientos

Cada requerimiento se relaciona con los componentes que lo satisfacen, los modelos donde aparece, las decisiones que lo sustentan y el método para verificarlo.

**Abreviaturas de modelos:** CU = casos de uso (Fig. 1) · CO = componentes (Fig. 2a/2b) · DE = despliegue (Fig. 3) · DA = datos (Fig. 4) · SE = secuencia (Fig. 5a/5b).

**Estado:** como la actividad no exige implementar el sistema (restricción R-06), todos los requerimientos están **diseñados**, no probados. La columna de verificación indica cómo se comprobaría cada uno.

## Requerimientos funcionales

| Id | Requerimiento | Componente(s) | Modelos | Decisión / regla | Método de verificación y criterio de aceptación |
|---|---|---|---|---|---|
| RF-01 | Autenticación | Identidad y acceso; pipeline de seguridad | CU-01 · CO · DA (Usuario, Sesion) | ADR-004 | **Prueba de API:** credenciales válidas → 200 con tokens; inválidas → 401; tras cerrar sesión, renovar el token → 401. |
| RF-02 | Roles y permisos | Identidad y acceso (UsuarioRol); pipeline; dominio de cada módulo | CU-02 · CO · DA (Rol, UsuarioRol) | ADR-004 · RN-08 | **Matriz de permisos automatizada:** cada endpoint se llama con los 4 roles; los no autorizados reciben 403. |
| RF-03 | Gestión de estudiantes | Gestión académica | CU-03 · CO · DA (Estudiante) | S-03 (baja lógica) | **Prueba funcional:** crear, consultar, editar y desactivar; el estudiante desactivado no se puede matricular. |
| RF-04 | Gestión de docentes | Gestión académica | CU-04 · CO · DA (Docente) | S-03 | **Prueba funcional:** igual que RF-03; un docente desactivado no se puede asignar a un grupo. |
| RF-05 | Programas y asignaturas | Gestión académica | CU-05 · DA (Programa, PlanEstudio, Asignatura) | RN-09 | **Prueba funcional:** crear un plan con asignaturas; un código de asignatura repetido → 409. |
| RF-06 | Grupos y periodos | Gestión académica; Matrículas (CupoGrupo) | CU-06 · DA (PeriodoAcademico, Grupo, Horario, Aula, CupoGrupo) | RN-10 · RN-13 · RN-15 | **Prueba funcional:** crear un grupo con cupo, docente, horario y aula o enlace; asignar al mismo docente en una franja cruzada → 409; cupo de 40 en un aula de 25 → 409. |
| RF-07 | Matrícula académica | Matrículas; IConsultaAcademica; Auditoría | CU-07 · SE (5a, 5b) · DA (Matricula, DetalleMatricula) | ADR-002 · RN-01 a RN-04 · RN-11 · RN-13 | **Pruebas de dominio** de cada regla y **prueba de concurrencia** (ver RNF-07). |
| RF-08 | Registro de calificaciones | Calificaciones; IConsultaAcademica; IConsultaMatriculas | CU-08 · CU-10 · DA (Evaluacion, Calificacion) | RN-05 · RN-06 · RN-12 | **Prueba de API:** un docente registra notas en su grupo → 200; en un grupo ajeno → 403; después del cierre → 409; nota de 5,5 → 400. |
| RF-09 | Consulta de resultados | Calificaciones; Matrículas | CU-09 · CU-11 · DA (Calificacion.estado) | S-04 · RN-08 | **Prueba de API:** el estudiante ve solo sus notas **publicadas**; las notas en borrador no aparecen. |
| RF-10 | Reportes | Reportes (vistas de solo lectura) | CU-12 · CO | Evaluación IA 3.11 | **Prueba con datos de ejemplo:** el total del reporte de matriculados por periodo y programa coincide con un conteo directo en la base. |
| RF-11 | Búsqueda y filtros | Listados de cada módulo | CU-13 · CO | Evaluación IA 3.12 · RNF-11 | **Prueba de API:** buscar por código, nombre, programa, periodo y estado; un docente solo obtiene resultados de sus grupos. |
| RF-12 | Auditoría | Auditoría (IRegistroAuditoria) | CU-14 · CU-15 · SE (5a, pasos 28–29) · DA (EventoAuditoria) | ADR-005 · RN-07 · RN-14 | **Prueba de integración:** cada inicio de sesión, cambio de rol, matrícula y cambio de nota genera un evento completo. **Prueba de caos:** matar el proceso (`kill -9`) durante un flujo de matrículas y comprobar que el número de matrículas coincide con el de eventos de auditoría. |

## Requerimientos no funcionales

| Id | Requerimiento | Componente(s) | Modelos | Decisión | Método de verificación y criterio de aceptación |
|---|---|---|---|---|---|
| RNF-01 | Seguridad | Cloudflare; balanceador; pipeline; Identidad y acceso; gestor de secretos | DE · CO · DA (hash_contrasena) | ADR-003 · ADR-004 | **Escaneo** con OWASP ZAP sin hallazgos altos; HTTP redirige a HTTPS; revisar que la tabla de usuarios solo tenga hashes Argon2id; análisis del repositorio sin secretos. |
| RNF-02 | Rendimiento | API (2 nodos); índices; caché en memoria; pools de conexiones separados para reportes | DE · CO | ADR-001 · ADR-002 · ADR-003 | **Prueba de carga** con k6: mezcla de 70 % consultas, 20 % matrículas y 10 % reportes, subiendo de 50 a 500 usuarios. Con 300, el percentil 95 de las consultas comunes debe ser ≤ 3 s; se registra el punto donde se degrada. |
| RNF-03 | Disponibilidad | Balanceador administrado + 2 nodos; PostgreSQL con réplica; monitoreo | DE | ADR-003 | **Prueba de falla:** apagar un nodo y forzar la conmutación de la base; el servicio responde. **En operación:** monitor externo con disponibilidad mensual ≥ 99,5 %. |
| RNF-04 | Escalabilidad | API sin estado | DE · CO | ADR-001 · ADR-004 | **Prueba:** agregar un tercer nodo detrás del balanceador sin cambiar código y repetir la prueba de carga. |
| RNF-05 | Mantenibilidad | Monolito modular en capas; interfaces entre módulos | CO (2a, 2b) | ADR-001 | **Pruebas de arquitectura** (por ejemplo, ArchUnit) que fallan si un módulo accede al repositorio de otro; complejidad ciclomática < 10 medida con SonarQube. |
| RNF-06 | Usabilidad y accesibilidad | Interfaz web; pipeline de integración continua | DE | — | **Automática en cada cambio:** axe-core y Lighthouse CI con puntaje de accesibilidad ≥ 90. **Manual:** recorrido completo de matrícula y registro de notas solo con teclado. |
| RNF-07 | Integridad y consistencia | Matrículas (CupoGrupo, transacción); restricciones de la base; Calificaciones | SE (5a, 5b) · DA (restricciones) | ADR-002 · ADR-005 | **Prueba de concurrencia:** 50 solicitudes simultáneas por un grupo de 1 cupo → exactamente 1 matrícula y 49 rechazos 409; `ocupados` nunca supera `cupo_maximo`. |
| RNF-08 | Interoperabilidad | API REST `/api/v1` | CO | — | **Especificación OpenAPI** (`api/openapi.yaml`) validada con un linter; los endpoints responden según el contrato. |
| RNF-09 | Respaldo y recuperación | PostgreSQL administrado; respaldo externo | DE | ADR-003 | **Simulacro trimestral** de restauración en un entorno de pruebas: RPO real ≤ 15 min y RTO real ≤ 2 h. |
| RNF-10 | Trazabilidad | Esta matriz; ADR; auditoría con identificador de correlación | Todos | ADR-001 a ADR-005 | **Revisión documental:** cada RF y RNF tiene al menos un componente, un modelo y un método de verificación (esta tabla). |
| RNF-11 | Privacidad | Dominio de cada módulo (filtros por propietario); subred privada | CO · DE | ADR-004 · RN-08 | **Prueba de API:** el estudiante A pide los datos del estudiante B → 403; un docente consulta un grupo ajeno → 403. |
| RNF-12 | Compatibilidad | Interfaz web responsiva | DE | — | **Pruebas en navegadores** con Playwright: Chrome, Edge, Firefox y Safari (WebKit), en 360 px y en 1366 px. |

## Cobertura

- **12 de 12** RF y **12 de 12** RNF tienen componente, modelo y método de verificación.
- Los requerimientos **más cubiertos** son RF-07, RF-12 y RNF-07: aparecen en 3 o más modelos y en 2 decisiones.
- Los **menos sustentados** en el diseño son RNF-06 y RNF-12: dependen de la implementación de la interfaz, que no está dentro del alcance. Se registran como riesgo de validación.
