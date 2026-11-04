# Guía: prototipo navegable con Google AI Studio Build

**Objetivo:** generar con AI Studio Build una maqueta web navegable del SGA que respete la arquitectura diseñada (módulos, reglas de negocio y decisiones ADR-001 a ADR-005), y verificar con criterio qué respetó la IA y qué no.

**Importante:** el resultado es un **prototipo con datos simulados en memoria**. No es la implementación de la arquitectura: no tiene backend, ni base de datos PostgreSQL, ni seguridad real. Así se debe presentar en el informe y en el video.

Tiempo estimado: 45 a 60 minutos.

---

## Paso 1. Abrir Build

1. Entra a **aistudio.google.com** con tu cuenta de la CUN.
2. En el menú izquierdo, en **BUILD**, toca **New app**.
3. Deja el modelo que aparece (Gemini 3.8 Flash) y anótalo.

## Paso 2. Pegar el prompt principal

Copia todo el bloque y envíalo. La generación puede tardar algunos minutos.

```text
Construye una aplicación web llamada "SGA · Sistema de Gestión Académica", en español (Colombia), que sea un PROTOTIPO NAVEGABLE de una arquitectura ya diseñada. Usa React con TypeScript. Todos los datos son ficticios y viven en memoria (no uses backend real). No uses nombres de personas reales.

ARQUITECTURA QUE DEBES RESPETAR (es un monolito modular en capas):
Organiza el código en seis módulos, cada uno en su propia carpeta dentro de src/modulos/: identidad, academico, matriculas, calificaciones, reportes y auditoria. Cada módulo tiene tres capas: 
- api.ts: el contrato REST simulado del módulo (funciones con el nombre del endpoint, por ejemplo POST /api/v1/matriculas), 
- dominio.ts: las reglas de negocio, 
- repositorio.ts: los datos en memoria. 
Un módulo NO puede leer el repositorio de otro módulo; solo puede llamar funciones del dominio de otro módulo a través de una interfaz (por ejemplo, IConsultaAcademica, IConsultaMatriculas, IRegistroAuditoria). La interfaz de usuario solo llama a los api.ts.

ROLES Y ACCESO:
- Pantalla de inicio de sesión simulada con cuatro usuarios de ejemplo: administrador, coordinador académico, docente y estudiante. Un usuario de ejemplo debe tener dos roles (docente y coordinador) y al entrar debe elegir con qué perfil trabajar ("rol activo").
- Muestra en la parte superior el usuario, el rol activo y un botón para cerrar sesión.
- El menú lateral solo muestra las opciones permitidas para el rol activo. Si alguien intenta una acción no permitida, muestra "403 · No tiene permiso".

MÓDULO GESTIÓN ACADÉMICA (administrador y coordinador):
- Estudiantes y docentes: crear, consultar, editar y desactivar (baja lógica: cambia el estado, no se borra). Búsqueda por código o nombre y filtros por programa y estado.
- Programas, planes de estudio y asignaturas (código único, nombre, créditos, semestre).
- Periodos académicos con: fechas de matrícula, fecha límite de notas y botón "Cerrar notas del periodo".
- Grupos con asignatura, periodo, docente, cupo máximo, horario (día, hora inicio, hora fin) y aula (con capacidad) o enlace virtual. Regla: el cupo no puede superar la capacidad del aula. Un docente no puede tener dos grupos con cruce de horario.

MÓDULO MATRÍCULAS (coordinador):
- Matricular a un estudiante en uno o varios grupos de un periodo. Valida en este orden y muestra un mensaje claro si falla:
  1) estudiante activo, 2) periodo abierto para matrícula, 3) sin cruce de horario con lo que ya tiene, 4) no tener ya esa asignatura en el periodo, 5) cupo disponible.
- Muestra el cupo como "ocupados / cupo máximo" en cada grupo.
- Agrega un botón de demostración "Simular dos solicitudes simultáneas por el último cupo": deja un grupo en 29/30, lanza dos matrículas a la vez y muestra el resultado: una exitosa (201) y una rechazada (409 · Sin cupo). Explica en pantalla que en la arquitectura real esto lo garantiza un bloqueo de fila en una transacción (SELECT ... FOR UPDATE) y una restricción CHECK en la base de datos.
- El estudiante puede ver su horario y sus matrículas, pero no matricularse.

MÓDULO CALIFICACIONES:
- El docente solo ve SUS grupos. Cada grupo tiene evaluaciones (por ejemplo, Parcial 1, 30 %) cuyos porcentajes deben sumar 100 %.
- El docente registra notas entre 0,0 y 5,0. Las notas quedan en estado "Borrador" hasta que pulse "Publicar".
- Si el periodo tiene las notas cerradas, el docente ya no puede editar.
- Cambiar una nota ya publicada exige escribir una justificación.
- El estudiante solo ve sus notas PUBLICADAS y la nota final ponderada.

MÓDULO REPORTES (coordinador y administrador):
- Reportes de estudiantes matriculados, grupos y resultados académicos, con filtros por periodo y programa, y botón para exportar a CSV.

MÓDULO AUDITORÍA (solo administrador):
- Cada inicio de sesión, cambio de rol, matrícula y cambio de nota genera un evento con: usuario, rol, fecha y hora, acción, registro afectado, valor anterior, valor nuevo y justificación.
- El registro de auditoría es de solo lectura: no hay botones para editar ni borrar. Filtros por usuario, acción y rango de fechas.
- El evento de auditoría debe guardarse en la MISMA operación que el cambio: si el cambio falla, tampoco se guarda el evento.

PÁGINA "ARQUITECTURA" (visible para todos los roles):
- Un diagrama simple de los seis módulos con las interfaces que usan entre sí.
- La lista de endpoints REST de cada módulo (/api/v1/...).
- Un resumen de las decisiones: ADR-001 monolito modular en capas; ADR-002 bloqueo pesimista en la matrícula; ADR-003 dos nodos sin estado y PostgreSQL con réplica; ADR-004 JWT de 15 minutos con token de renovación y rol activo; ADR-005 auditoría en la misma transacción.
- Una nota visible: "Prototipo con datos simulados. No representa la implementación final."

DISEÑO Y ACCESIBILIDAD:
- Interfaz clara y consistente, adaptable a celular y computador.
- Todas las funciones principales deben poder usarse solo con el teclado, con foco visible, etiquetas en los campos y buen contraste.

DATOS DE EJEMPLO:
- 2 programas, 8 asignaturas, 1 periodo abierto, 6 grupos (uno casi lleno: 29/30), 12 estudiantes, 4 docentes, todos con nombres inventados.
```

## Paso 3. Revisar con esta lista de pruebas

Prueba cada caso en la aplicación generada y anota el resultado. Esta tabla es la evidencia del **uso crítico** de la IA, y en el video puedes mostrar dos o tres de estas pruebas.

| # | Prueba | Resultado esperado | ¿Cumple? (Sí / No / Parcial) | Observación |
|---|---|---|---|---|
| B1 | Entrar como estudiante e intentar abrir Matrículas o Auditoría | No aparece en el menú, o muestra 403 | | |
| B2 | Usuario con dos roles: entrar y elegir el perfil | Pide elegir el rol activo; el menú cambia según el rol | | |
| B3 | Matricular en un grupo lleno | Rechaza con "Sin cupo" | | |
| B4 | Matricular dos grupos con el mismo horario | Rechaza por cruce de horario | | |
| B5 | Matricular dos grupos de la misma asignatura | Rechaza por duplicado | | |
| B6 | Botón "Simular dos solicitudes por el último cupo" | Una 201 y una 409; el grupo queda en 30/30 | | |
| B7 | Grupo con cupo mayor que la capacidad del aula | Rechaza | | |
| B8 | Docente intenta ver un grupo que no es suyo | No lo ve o muestra 403 | | |
| B9 | Docente registra 5,5 | Rechaza (escala 0,0–5,0) | | |
| B10 | Estudiante consulta notas en borrador | No las ve; solo ve publicadas | | |
| B11 | Cerrar notas del periodo e intentar editar como docente | Edición bloqueada | | |
| B12 | Cambiar una nota publicada | Exige justificación y queda en auditoría con valor anterior y nuevo | | |
| B13 | Abrir Auditoría como administrador | Solo lectura; aparecen login, matrícula y cambio de nota | | |
| B14 | Reporte de matriculados filtrado por periodo y programa | Muestra datos coherentes y exporta CSV | | |
| B15 | Revisar el código (pestaña de código `< >`) | Seis carpetas en `src/modulos/`, cada una con `api.ts`, `dominio.ts` y `repositorio.ts` | | |
| B16 | Navegar solo con el teclado (Tab, Enter) | Se puede matricular y registrar una nota sin mouse | | |

## Paso 4. Corregir lo que falle

Si alguna prueba no cumple, pídele a Build la corrección en el mismo chat, por ejemplo:

```text
La prueba de cruce de horario no funciona: pude matricular al estudiante en dos grupos que se dan el lunes de 8:00 a 10:00. Corrige la validación en src/modulos/matriculas/dominio.ts para que rechace la matrícula con el mensaje "Cruce de horario con <asignatura>". No cambies otros módulos.
```

Anota cada corrección pedida: sirve como evidencia de que verificaste y ajustaste lo que generó la IA.

## Paso 5. Guardar evidencias

- [ ] Capturas: el prompt enviado, la app generada, la página "Arquitectura", la estructura de carpetas del código y 3 o 4 pruebas (incluida la de concurrencia).
- [ ] La tabla de pruebas llena (puede ser una foto o texto).
- [ ] El enlace de la app: botón **Share** arriba a la derecha, con acceso "Cualquier persona con el enlace".
- [ ] Opcional: botón de descarga del código (ícono de descarga o "Download") para subirlo al repositorio.
