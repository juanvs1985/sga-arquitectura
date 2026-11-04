# ADR-002: Control de concurrencia de la matrícula con bloqueo pesimista

- **Estado:** Aceptado
- **Fecha:** 2026-11-04
- **Requerimientos relacionados:** RF-07, RNF-07, RNF-02 · Reglas RN-01, RN-02

## Contexto

En semanas de matrícula, varias solicitudes pueden llegar al mismo tiempo por el último cupo de un grupo. Si dos transacciones leen "queda 1 cupo" a la vez, ambas matriculan y el grupo queda con sobrecupo. Tampoco se puede permitir que un estudiante quede dos veces en el mismo grupo ni en dos grupos de la misma asignatura y periodo.

Por la regla de aislamiento entre módulos (ADR-001), Matrícula no puede escribir en las tablas de Gestión académica, donde vive el grupo.

## Decisión

1. El módulo Matrículas es dueño de la tabla **`cupo_grupo`** (`id_grupo`, `cupo_maximo`, `ocupados`). Cuando Gestión académica crea un grupo o cambia su cupo, Matrículas actualiza esta fila a través de su interfaz.
2. **Antes** de tomar el bloqueo se validan las condiciones que no dependen del cupo: estudiante activo, periodo abierto para matrícula y ausencia de cruce de horario. También se hace una **lectura sin bloqueo** de `cupo_grupo`: si el grupo ya está lleno, se rechaza de inmediato sin entrar en la cola de bloqueos *(mitigación del riesgo señalado por la IA en P7)*. Así el bloqueo dura lo mínimo y solo compiten las solicitudes que todavía tienen opción.
3. La matrícula se ejecuta en **una transacción** que:
   - bloquea la fila del grupo con `SELECT … FROM cupo_grupo WHERE id_grupo = ? FOR UPDATE`. Si se matriculan varios grupos a la vez, se bloquean **en orden ascendente de `id_grupo`** para evitar interbloqueos *(aporte de la IA, P5)*;
   - espera el bloqueo como máximo 5 segundos (`lock_timeout`); si se supera, responde "intente de nuevo";
   - valida `ocupados < cupo_maximo` y la ausencia de duplicados;
   - inserta la matrícula, incrementa `ocupados` y escribe el registro de auditoría (ADR-005);
   - confirma (COMMIT) o revierte todo.
4. Como segunda barrera, la base de datos tiene **restricciones únicas** `(id_estudiante, id_periodo)` en Matricula y `(id_matricula, id_asignatura)` y `(id_matricula, id_grupo)` en DetalleMatricula, más `CHECK (ocupados <= cupo_maximo)` en CupoGrupo.

## Opciones consideradas

1. **Bloqueo pesimista de fila** (elegida).
2. **Control optimista** con número de versión y reintentos.
3. **Cola de solicitudes** que procese las matrículas una por una.

## Argumentos

- El bloqueo pesimista solo serializa las solicitudes **del mismo grupo**. Los demás grupos se procesan en paralelo, así que el impacto en RNF-02 es bajo.
- El control optimista funciona bien con poca contención, pero en el último cupo de un grupo popular produce muchos reintentos fallidos y una mala experiencia.
- La cola agrega un componente que operar y vuelve asíncrona la respuesta al usuario. Con 300 usuarios concurrentes no se justifica.

## Consecuencias

- **Positivas:** nunca hay sobrecupo ni matrícula duplicada, incluso si falla la lógica de la aplicación, gracias a la restricción única.
- **Negativas:** las transacciones de matrícula deben ser cortas para no retener el bloqueo; por eso las validaciones sin contención van antes del bloqueo.
- **Riesgo residual:** si en el futuro se habilita la automatrícula y cientos de estudiantes piden el mismo grupo al mismo tiempo, la cola de bloqueos podría superar los 3 s de RNF-02 (riesgo R-04).
- **Verificación:**
  - Prueba de concurrencia con 50 solicitudes simultáneas por un grupo de 1 cupo. Resultado esperado: exactamente 1 matrícula y 49 rechazos controlados.
  - Prueba extrema propuesta por la IA en P7: 300 usuarios sobre un grupo con 5 cupos en 2 segundos. Resultado esperado: 5 matrículas, cero sobrecupos y medición del percentil 95 y 99.
