# 6.4 Modelo de datos conceptual

## Figura 4. Entidades, atributos principales y cardinalidades

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Arial","fontSize":"14px","primaryColor":"#EEF2F7","primaryBorderColor":"#1F3864","primaryTextColor":"#14243F","lineColor":"#56657F","actorBkg":"#1F3864","actorTextColor":"#FFFFFF","actorBorder":"#1F3864","noteBkgColor":"#F6EBD0","noteBorderColor":"#A87A1E","signalColor":"#14243F","signalTextColor":"#14243F","labelBoxBkgColor":"#F6EBD0","labelBoxBorderColor":"#A87A1E","altSectionBkgColor":"#F7F9FC"}}}%%
erDiagram
    USUARIO ||--o{ USUARIO_ROL : "tiene"
    ROL ||--o{ USUARIO_ROL : "se asigna en"
    USUARIO ||--o{ SESION : "abre"
    USUARIO ||--o| ESTUDIANTE : "es"
    USUARIO ||--o| DOCENTE : "es"
    USUARIO ||--o{ EVENTO_AUDITORIA : "genera"
    PROGRAMA ||--o{ PLAN_ESTUDIO : "define"
    PLAN_ESTUDIO ||--|{ ASIGNATURA : "incluye"
    PROGRAMA ||--o{ ESTUDIANTE : "inscribe"
    ASIGNATURA ||--o{ GRUPO : "se oferta en"
    PERIODO_ACADEMICO ||--o{ GRUPO : "abre"
    DOCENTE |o--o{ GRUPO : "dicta"
    GRUPO ||--|{ HORARIO : "tiene"
    AULA |o--o{ HORARIO : "se usa en"
    GRUPO ||--|| CUPO_GRUPO : "controla"
    GRUPO ||--|{ EVALUACION : "define"
    ESTUDIANTE ||--o{ MATRICULA : "realiza"
    PERIODO_ACADEMICO ||--o{ MATRICULA : "contiene"
    MATRICULA ||--|{ DETALLE_MATRICULA : "incluye"
    GRUPO ||--o{ DETALLE_MATRICULA : "recibe"
    DETALLE_MATRICULA ||--o{ CALIFICACION : "obtiene"
    EVALUACION ||--o{ CALIFICACION : "se califica en"

    USUARIO {
        int id_usuario PK
        string correo UK
        string hash_contrasena "Argon2id"
        string nombres
        string apellidos
        string estado "Activo o Inactivo"
    }
    ROL {
        int id_rol PK
        string codigo UK "ADMIN, COORDINADOR, DOCENTE, ESTUDIANTE"
        string descripcion
    }
    USUARIO_ROL {
        int id_usuario PK,FK
        int id_rol PK,FK
    }
    SESION {
        int id_sesion PK
        int id_usuario FK
        string hash_token_renovacion
        datetime expira_en
        bool revocada
    }
    ESTUDIANTE {
        int id_estudiante PK
        int id_usuario FK,UK
        string codigo UK
        int id_programa FK
        string estado
    }
    DOCENTE {
        int id_docente PK
        int id_usuario FK,UK
        string codigo UK
        string estado
    }
    PROGRAMA {
        int id_programa PK
        string codigo UK
        string nombre
        string nivel
    }
    PLAN_ESTUDIO {
        int id_plan PK
        int id_programa FK
        string version
        bool vigente
    }
    ASIGNATURA {
        int id_asignatura PK
        int id_plan FK
        string codigo UK
        string nombre
        int creditos
        int semestre
    }
    PERIODO_ACADEMICO {
        int id_periodo PK
        string codigo UK "2026-2"
        date fecha_inicio
        date fecha_fin
        date inicio_matricula
        date fin_matricula
        date limite_notas
        bool notas_cerradas
    }
    GRUPO {
        int id_grupo PK
        int id_asignatura FK
        int id_periodo FK
        int id_docente FK
        string codigo "G01"
        int cupo_maximo
    }
    HORARIO {
        int id_horario PK
        int id_grupo FK
        int id_aula FK "nulo si es virtual"
        int dia_semana
        time hora_inicio
        time hora_fin
        string enlace "si es virtual"
    }
    AULA {
        int id_aula PK
        string codigo UK
        string sede
        int capacidad "cupo del grupo <= capacidad"
    }
    CUPO_GRUPO {
        int id_grupo PK,FK
        int cupo_maximo
        int ocupados "CHECK ocupados <= cupo_maximo"
    }
    MATRICULA {
        int id_matricula PK
        int id_estudiante FK "UK con id_periodo"
        int id_periodo FK
        datetime fecha
        string estado
    }
    DETALLE_MATRICULA {
        int id_detalle PK
        int id_matricula FK "UK con id_asignatura y con id_grupo"
        int id_grupo FK
        int id_asignatura FK "FK compuesta con id_grupo"
        string estado "Matriculado o Retirado"
    }
    EVALUACION {
        int id_evaluacion PK
        int id_grupo FK
        string nombre "Parcial 1"
        decimal porcentaje "suma 100 por grupo"
    }
    CALIFICACION {
        int id_calificacion PK
        int id_detalle FK "UK con id_evaluacion"
        int id_evaluacion FK
        decimal nota "0,0 a 5,0"
        string estado "Borrador o Publicada"
        datetime fecha_registro
    }
    EVENTO_AUDITORIA {
        bigint id_evento PK
        int id_usuario FK
        string accion
        string entidad
        string id_registro
        json valor_anterior
        json valor_nuevo
        string justificacion
        datetime fecha_hora
        string ip_origen
        string id_correlacion
    }
```

*Fuente: elaboración propia, a partir de la propuesta P4 de Google AI Studio con las correcciones de la evaluación.*

**Notación (pata de gallo):** `||` uno y solo uno · `o|` cero o uno · `|{` uno o muchos · `o{` cero o muchos.

## Entidades por módulo

Cada entidad pertenece al esquema del módulo que es su dueño (ADR-001).

| Módulo (esquema) | Entidades |
|---|---|
| Identidad y acceso | Usuario, Rol, UsuarioRol, Sesion |
| Gestión académica | Estudiante, Docente, Programa, PlanEstudio, Asignatura, PeriodoAcademico, Grupo, Horario, Aula |
| Matrículas | Matricula, DetalleMatricula, CupoGrupo |
| Calificaciones | Evaluacion, Calificacion |
| Auditoría | EventoAuditoria |

## Cardinalidades más importantes

| Relación | Cardinalidad | Significado |
|---|---|---|
| Usuario – Rol | M:N (vía UsuarioRol) | Un usuario puede tener varios roles; por ejemplo, un docente que también coordina (S-05). |
| Usuario – Estudiante / Docente | 1 : 0..1 | Un usuario puede ser estudiante, docente, ambos o ninguno (administrador). |
| Programa – PlanEstudio – Asignatura | 1:N y 1:N | Un programa tiene varios planes (versiones) y cada plan agrupa asignaturas con su semestre (RF-05). |
| Asignatura – Grupo | 1:N | Una asignatura se ofrece en varios grupos por periodo. |
| PeriodoAcademico – Grupo | 1:N | Cada grupo pertenece a un solo periodo. |
| Docente – Grupo | 0..1 : N | Un grupo puede crearse sin docente y asignarse después (RF-06). |
| Grupo – Horario | 1 : 1..N | Un grupo tiene una o más franjas semanales. |
| Aula – Horario | 0..1 : N | Una franja presencial usa un aula; una virtual usa un enlace. El cupo del grupo no puede superar la capacidad del aula (RN-15, aporte de la IA en P7). |
| Grupo – CupoGrupo | 1:1 | Control de ocupación, propiedad del módulo Matrículas (ADR-002). |
| Estudiante – Matricula | 1:N | Una matrícula por estudiante y periodo (restricción única). |
| Matricula – DetalleMatricula | 1 : 1..N | Una matrícula incluye uno o más grupos. |
| Grupo – Evaluacion | 1 : 1..N | Los cortes del grupo, cuyos porcentajes suman 100. |
| DetalleMatricula – Calificacion – Evaluacion | 1:N y N:1 | Una nota por estudiante matriculado y por evaluación (restricción única). |

## Restricciones de integridad (RNF-07)

| Restricción | Protege la regla |
|---|---|
| `UNIQUE (id_estudiante, id_periodo)` en Matricula | Una sola matrícula por estudiante y periodo. |
| `UNIQUE (id_matricula, id_grupo)` en DetalleMatricula | No matricular dos veces el mismo grupo (RN-01). |
| `UNIQUE (id_matricula, id_asignatura)` en DetalleMatricula | No matricular dos grupos de la misma asignatura (RN-01). |
| FK compuesta `(id_grupo, id_asignatura)` → Grupo | El `id_asignatura` del detalle coincide con el del grupo. |
| `CHECK (ocupados <= cupo_maximo)` en CupoGrupo | Nunca hay sobrecupo, aunque falle la aplicación (RN-02). |
| `UNIQUE (id_detalle, id_evaluacion)` en Calificacion | Una sola nota por estudiante y evaluación. |
| `CHECK (nota BETWEEN 0 AND 5)` en Calificacion | Escala de notas (RN-06). |
| Solo INSERT y SELECT sobre EventoAuditoria | Auditoría inmutable (RN-14, ADR-005). |
| Baja lógica (`estado`) en Usuario, Estudiante y Docente | Se conserva el historial (S-03). |
