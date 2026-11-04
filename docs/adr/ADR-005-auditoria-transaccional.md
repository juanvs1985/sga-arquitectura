# ADR-005: Auditoría escrita en la misma transacción del cambio

- **Estado:** Aceptado
- **Fecha:** 2026-11-04
- **Requerimientos relacionados:** RF-12, RNF-07, RNF-10 · Reglas RN-07, RN-12, RN-14

## Contexto

RF-12 exige registrar los inicios de sesión, los cambios de rol, las matrículas y las modificaciones de calificaciones, con el usuario, la fecha, la acción y el registro afectado. Gemini propuso un bus de eventos en memoria procesado de forma asíncrona (P3). Con esa propuesta, si la aplicación se cae entre el guardado del cambio y el procesamiento del evento, el cambio queda guardado sin su registro de auditoría.

## Decisión

- El módulo Auditoría expone la interfaz **`IRegistroAuditoria.registrar(evento)`**.
- Los módulos que modifican datos auditables la llaman **dentro de la misma transacción** del cambio: o se guardan el cambio y su auditoría, o no se guarda ninguno.
- Cada registro guarda: usuario, rol, fecha y hora, acción, entidad, identificador del registro afectado, valor anterior, valor nuevo, justificación (si aplica), dirección IP e identificador de correlación de la petición.
- La tabla `auditoria.evento` es de **solo inserción**: el usuario de base de datos de la aplicación tiene permiso de INSERT y SELECT, pero no de UPDATE ni DELETE.
- Los intentos de inicio de sesión fallidos, que no modifican datos, se registran desde el *pipeline* de seguridad.

## Opciones consideradas

1. **Auditoría en la misma transacción** (elegida).
2. Bus de eventos en memoria asíncrono (propuesta de la IA).
3. Almacenamiento WORM externo.

## Consecuencias

- **Positivas:** ningún cambio auditable queda sin registro, y la auditoría tiene la misma garantía de consistencia que los datos.
- **Negativas:** cada escritura auditable hace una inserción adicional; el costo es bajo frente al volumen esperado. Además, la tabla crece de forma permanente, por lo que se particiona por mes y se archiva según la política de retención de la institución.
- **Verificación:** forzar un error después de modificar una nota y comprobar que no queda ni la nota cambiada ni el registro de auditoría. Comprobar también que el usuario de la aplicación no puede ejecutar UPDATE ni DELETE sobre la tabla.
