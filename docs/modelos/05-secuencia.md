# 6.5 Vista de secuencia: matrícula de un estudiante

Se modela la matrícula porque es el proceso más crítico del sistema: combina reglas de negocio, concurrencia y auditoría (RF-07, RF-12, RNF-07).

## Figura 5a. Flujo completo de la matrícula

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Arial","fontSize":"14px","primaryColor":"#EEF2F7","primaryBorderColor":"#1F3864","primaryTextColor":"#14243F","lineColor":"#56657F","actorBkg":"#EEF2F7","actorTextColor":"#14243F","labelTextColor":"#14243F","loopTextColor":"#14243F","actorBorder":"#1F3864","noteBkgColor":"#F6EBD0","noteBorderColor":"#A87A1E","signalColor":"#14243F","signalTextColor":"#14243F","labelBoxBkgColor":"#F6EBD0","labelBoxBorderColor":"#A87A1E","altSectionBkgColor":"#F7F9FC"}}}%%
sequenceDiagram
    autonumber
    actor C as Coordinador
    participant W as Interfaz web
    participant P as Pipeline de seguridad
    participant MC as ControladorMatriculas
    participant MS as ServicioMatricula
    participant CA as IConsultaAcademica
    participant R as RepositorioMatriculas
    participant A as IRegistroAuditoria
    participant BD as PostgreSQL

    C->>W: Selecciona estudiante y grupo
    W->>P: POST /api/v1/matriculas {idEstudiante, idGrupo} + JWT
    P->>P: Valida JWT y rol COORDINADOR
    P->>MC: Petición autorizada
    MC->>MC: Valida formato del DTO
    MC->>MS: matricular(idEstudiante, idGrupo)

    Note over MS,CA: Validaciones previas, sin bloqueo
    MS->>CA: estudianteActivo(idEstudiante)
    CA-->>MS: Activo
    MS->>CA: datosGrupo(idGrupo)
    CA-->>MS: Asignatura, periodo, horario, fechas de matrícula
    MS->>R: franjasDelEstudiante(idEstudiante, idPeriodo)
    R-->>MS: Franjas ya matriculadas
    MS->>MS: Periodo abierto (RN-11) y sin cruce de horario (RN-13)

    opt Falla una validación previa
        MS-->>MC: ReglaNegocioError
        MC-->>W: 409 Conflict + motivo
        W-->>C: Muestra el motivo
    end

    Note over MS,BD: Transacción con bloqueo (ADR-002)
    MS->>R: matricularEnTransaccion(...)
    R->>BD: BEGIN
    R->>BD: SELECT ocupados, cupo_maximo FROM cupo_grupo WHERE id_grupo = ? FOR UPDATE
    Note right of BD: Si otra solicitud tiene el bloqueo,<br/>espera como máximo 5 s
    BD-->>R: ocupados, cupo_maximo

    alt Sin cupo o asignatura ya matriculada
        R->>BD: ROLLBACK
        R-->>MS: CupoAgotado o MatriculaDuplicada
        MS-->>MC: Error de dominio
        MC-->>W: 409 Conflict
        W-->>C: "Sin cupo" o "Ya matriculado"
    else Hay cupo
        R->>BD: INSERT matricula (si no existe) e INSERT detalle_matricula
        R->>BD: UPDATE cupo_grupo SET ocupados = ocupados + 1
        MS->>A: registrar(MATRICULA, usuario, estudiante, grupo)
        A->>BD: INSERT evento_auditoria (misma transacción, ADR-005)
        R->>BD: COMMIT
        MS-->>MC: Matrícula creada
        MC-->>W: 201 Created
        W-->>C: Confirmación de matrícula
    end
```

*Fuente: elaboración propia, a partir de la propuesta P5 de Google AI Studio con las correcciones de la evaluación.*

**Puntos clave del flujo:**

1. **Pasos 2 a 5.** El pipeline de seguridad valida el token y el rol antes de que la petición llegue al módulo (RF-02, RNF-01).
2. **Pasos 7 a 13.** Las validaciones que no dependen del cupo se hacen **antes** del bloqueo: estudiante activo, periodo abierto y cruce de horario. Así el bloqueo dura lo mínimo.
3. **Paso 19.** `SELECT … FOR UPDATE` bloquea solo la fila del grupo en `cupo_grupo`. Otras matrículas de otros grupos siguen en paralelo (ADR-002).
4. **Pasos 26 a 30.** La matrícula, el cupo y el registro de auditoría se confirman en **una sola transacción**: o se guardan los tres o ninguno (ADR-005).
5. **Respuestas:** `201 Created` si se matricula; `409 Conflict` si no hay cupo, si hay un duplicado o si falla una regla de negocio.

## Figura 5b. Dos solicitudes simultáneas por el último cupo

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Arial","fontSize":"14px","primaryColor":"#EEF2F7","primaryBorderColor":"#1F3864","primaryTextColor":"#14243F","lineColor":"#56657F","actorBkg":"#EEF2F7","actorTextColor":"#14243F","labelTextColor":"#14243F","loopTextColor":"#14243F","actorBorder":"#1F3864","noteBkgColor":"#F6EBD0","noteBorderColor":"#A87A1E","signalColor":"#14243F","signalTextColor":"#14243F","labelBoxBkgColor":"#F6EBD0","labelBoxBorderColor":"#A87A1E","altSectionBkgColor":"#F7F9FC"}}}%%
sequenceDiagram
    participant S1 as Solicitud 1 (estudiante E1)
    participant BD as PostgreSQL<br/>cupo G01: 29 de 30
    participant S2 as Solicitud 2 (estudiante E2)

    par Llegan al mismo tiempo
        S1->>BD: BEGIN · SELECT … FOR UPDATE (G01)
    and
        S2->>BD: BEGIN · SELECT … FOR UPDATE (G01)
    end
    BD-->>S1: Bloqueo concedido · 29 de 30
    Note over BD,S2: S2 espera a que S1 libere el bloqueo
    S1->>BD: INSERT detalle · ocupados = 30 · INSERT auditoría
    S1->>BD: COMMIT (libera el bloqueo)
    BD-->>S2: Bloqueo concedido · 30 de 30
    S2->>BD: ROLLBACK (sin cupo) → 409 Conflict
    Note over S1,S2: Resultado: 1 matrícula y 1 rechazo. El grupo nunca queda en 31 de 30.
```

*Fuente: elaboración propia.*

Este escenario es la prueba de aceptación de RNF-07. Se repite con 50 solicitudes simultáneas sobre un grupo de 1 cupo, y el resultado esperado es exactamente 1 matrícula.

Cuando una matrícula incluye varios grupos, los bloqueos se toman en **orden ascendente de `id_grupo`** para evitar interbloqueos entre dos solicitudes que comparten grupos (aporte de la IA, P5).
