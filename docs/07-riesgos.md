# 7. Análisis crítico: riesgos, puntos únicos de falla y validación

Este análisis combina la revisión propia con la autocrítica que se pidió a Google AI Studio (P7). Cada riesgo se califica con **Riesgo = Probabilidad × Impacto**, en una escala de 1 (bajo) a 3 (alto):

- **Nivel alto:** 6 a 9.
- **Nivel medio:** 3 o 4.
- **Nivel bajo:** 1 o 2.

## 7.1 Puntos únicos de falla

| Componente | ¿Es punto único de falla? | Cómo se resolvió |
|---|---|---|
| Nodo de la API | No | Dos nodos sin estado detrás del balanceador (ADR-003, ADR-004). |
| Balanceador de carga | No | Se usa el balanceador administrado del proveedor, redundante por diseño (crítica de la IA en P7). |
| Base de datos | No | Primaria y réplica en otra zona, con conmutación automática (ADR-003). |
| Redis | No existe | Se descartó: el diseño no depende de una caché compartida (evaluación P2, P3, P6). |
| Auditoría por bus de eventos | No existe | La auditoría va en la misma transacción del cambio (ADR-005). |
| **Cloudflare** | **Sí, residual** | Un proveedor externo de borde. Se acepta por su disponibilidad histórica alta y su costo cero; si cae, se puede apuntar el DNS directo al balanceador (procedimiento manual). |
| **Región del proveedor de nube** | **Sí, residual** | Todo corre en una región. Una caída regional completa supera el 99,5 %; se recupera desde el respaldo externo en otra región (RTO 2 h). Desplegar en varias regiones no se justifica por costo (S-08). |

## 7.2 Registro de riesgos

| Id | Riesgo | Tipo | P | I | Nivel | Mitigación en el diseño | Validación |
|---|---|---|---|---|---|---|---|
| R-01 | Sobrecupo o matrícula duplicada por solicitudes simultáneas | Integridad | 3 | 3 | **9 Alto** | Bloqueo de fila en `cupo_grupo`, restricciones únicas y `CHECK` (ADR-002) | Prueba de concurrencia: 50 solicitudes por 1 cupo y 300 usuarios por 5 cupos |
| R-02 | Cambio de nota o matrícula sin registro de auditoría | Trazabilidad | 2 | 3 | **6 Alto** | Auditoría en la misma transacción (ADR-005) | Prueba de caos con `kill -9`: matrículas = eventos |
| R-03 | Un superusuario de la base de datos altera la auditoría | Seguridad | 1 | 3 | 3 Medio | Usuario de aplicación sin UPDATE/DELETE; exportación diaria con bloqueo de objetos; registro de actividad del proveedor | Comparar la exportación con la tabla en un muestreo mensual |
| R-04 | Cola de bloqueos supera 3 s si cientos de estudiantes piden el mismo grupo (si se habilita la automatrícula) | Rendimiento | 2 | 2 | 4 Medio | Hoy matricula el coordinador (S-02); lectura previa sin bloqueo para rechazo rápido; `lock_timeout` de 5 s | Prueba extrema de 300 usuarios sobre 5 cupos en 2 s; medir P95 y P99 |
| R-05 | Agotamiento de conexiones a PostgreSQL | Rendimiento / Disponibilidad | 2 | 3 | **6 Alto** | Pool de 20 por nodo, *pooler* administrado, pool aparte para reportes | Prueba de carga de 50 a 500 usuarios; observar conexiones activas |
| R-06 | Reportes pesados degradan la matrícula en el cierre de periodo | Rendimiento | 2 | 2 | 4 Medio | Vistas de solo lectura, pool separado con tiempo máximo; réplica de lectura si hace falta | Prueba de carga con 10 % de reportes |
| R-07 | Usuario con varios roles usa permisos de otro perfil | Seguridad | 2 | 2 | 4 Medio | Rol activo único en el token (ADR-004); filtros por propietario en el dominio | Prueba de API con un usuario docente y estudiante |
| R-08 | Acceso de un estudiante a datos de otro | Privacidad | 2 | 3 | **6 Alto** | Filtros por propietario en el dominio de cada módulo (RN-08) | Pruebas de API automatizadas: A pide datos de B → 403 |
| R-09 | Robo de token en un computador compartido | Seguridad | 2 | 2 | 4 Medio | Token de acceso de 15 min; renovación de 8 h con rotación; cookie `HttpOnly` | Revisión de seguridad con OWASP ZAP |
| R-10 | Datos personales tratados por proveedores externos (nube, Cloudflare) sin acuerdo | Legal (Ley 1581 de 2012) | 2 | 3 | **6 Alto** | Fuera del alcance técnico | Revisión jurídica de los contratos de tratamiento de datos antes de producción |
| R-11 | Los límites entre módulos se erosionan con el tiempo | Mantenibilidad | 2 | 2 | 4 Medio | Interfaces explícitas y un esquema por módulo (ADR-001) | Pruebas de arquitectura (ArchUnit) en el pipeline |
| R-12 | El respaldo no se puede restaurar cuando se necesita | Recuperación | 1 | 3 | 3 Medio | WAL continuo, copia diaria, bloqueo de objetos (ADR-003) | Simulacro trimestral midiendo RPO y RTO reales |
| R-13 | La interfaz no cumple accesibilidad ni compatibilidad | Usabilidad | 2 | 2 | 4 Medio | Requisitos en la matriz | axe-core y Lighthouse CI; pruebas en 4 navegadores con Playwright |

## 7.3 Límites de escalabilidad

- **El monolito escala completo.** Si un solo módulo concentra la carga (por ejemplo, Matrículas en semanas pico), hay que replicar toda la aplicación. Es aceptable para 300 usuarios. Si el crecimiento lo exige, el módulo se extrae como servicio con el patrón Strangler Fig, gracias a que ya tiene su propia interfaz y su propio esquema.
- **Una sola base de datos primaria** recibe todas las escrituras. El techo depende del tamaño de la máquina (escalado vertical). Las lecturas pesadas se pueden llevar a una réplica de lectura.
- **Un grupo muy popular** es un punto de contención inevitable: las matrículas a un mismo grupo se procesan en fila. Las de grupos distintos, en paralelo.

## 7.4 Decisiones arquitectónicas que requieren validación

| Decisión | Hipótesis que hay que comprobar | Prueba propuesta | Criterio de éxito |
|---|---|---|---|
| ADR-001 Monolito modular | Con 2 nodos se atienden 300 usuarios concurrentes | Prueba de carga k6: 70 % consultas, 20 % matrículas, 10 % reportes; de 50 a 500 usuarios | P95 ≤ 3 s con 300 usuarios; registrar el punto de degradación |
| ADR-002 Bloqueo pesimista | No hay sobrecupo y la espera es aceptable | 300 usuarios sobre un grupo con 5 cupos en 2 s | 5 matrículas exactas; P95 ≤ 3 s; cero errores 500 |
| ADR-003 Alta disponibilidad | El servicio sobrevive a la caída de un nodo y a la conmutación de la base | Apagar un nodo; forzar la conmutación de la base | Servicio disponible; conmutación ≤ 120 s |
| ADR-003 Respaldo | RPO ≤ 15 min y RTO ≤ 2 h son alcanzables | Simulacro de desastre: dañar la base en pruebas y restaurar con copia + WAL | Pérdida ≤ 15 min; servicio restaurado en ≤ 2 h |
| ADR-005 Auditoría transaccional | Ningún cambio queda sin auditar | Prueba de caos con `kill -9` durante matrículas | Matrículas guardadas = eventos de auditoría |

**Las cinco decisiones principales y su justificación** están documentadas en `docs/adr/` (ADR-001 a ADR-005). El enunciado pide al menos tres.
