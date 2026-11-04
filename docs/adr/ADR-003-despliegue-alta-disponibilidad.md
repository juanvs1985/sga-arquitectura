# ADR-003: Despliegue con réplicas, base de datos administrada en alta disponibilidad y respaldo externo

- **Estado:** Aceptado
- **Fecha:** 2026-11-04
- **Requerimientos relacionados:** RNF-01, RNF-03, RNF-04, RNF-09, RNF-11, RNF-12

## Contexto

ADR-001 dejó una consecuencia abierta: con una sola base de datos, esta se vuelve un punto único de falla. RNF-03 exige 99,5 % de disponibilidad mensual (unas 3,6 horas de caída no programada al mes como máximo) y RNF-09 exige respaldo y un procedimiento de restauración. El presupuesto de la institución es moderado (S-08), así que se descartan Kubernetes y el despliegue en varias regiones.

## Decisión

| Capa | Decisión |
|---|---|
| Borde | **Cloudflare**: DNS, TLS, WAF básico, mitigación de DDoS, límite de peticiones y CDN. |
| Interfaz web | Archivos estáticos en almacenamiento de objetos, servidos por la CDN. |
| API | **2 instancias** del monolito en contenedores Docker, en subred privada, detrás del **balanceador administrado del proveedor** (redundante por diseño, no un Nginx en una sola máquina) con *health checks*. Despliegue *rolling update*. |
| Conexiones | Pool de máximo 20 conexiones por nodo y el *pooler* del servicio administrado (tipo PgBouncer). Los reportes usan un pool separado de 5 conexiones con tiempo máximo por consulta, para no afectar la matrícula. |
| Base de datos | **PostgreSQL administrado** con primaria y réplica en espera en **otra zona de disponibilidad**, con conmutación automática. Subred privada, sin IP pública, TLS obligatorio. |
| Respaldo | Copia completa diaria más archivado continuo del WAL (recuperación a un punto en el tiempo). Cifrado AES-256 y almacenamiento en otro proveedor o región, con bloqueo de objetos por 30 días. **RPO ≤ 15 min, RTO ≤ 2 h.** |
| Secretos | Gestor de secretos del proveedor; nada en el repositorio. |
| Operación | Monitor externo de disponibilidad con alertas y registros centralizados con identificador de correlación. |
| Auditoría | Exportación diaria de los eventos de auditoría al almacenamiento con bloqueo de objetos, para detectar alteraciones hechas por un superusuario de la base de datos. |

## Opciones consideradas

1. **Servicios administrados con 2 réplicas de la API y base de datos en alta disponibilidad** (elegida).
2. Un solo servidor con la API y la base de datos (más barato, pero con punto único de falla; no garantiza el 99,5 %).
3. Kubernetes en varias regiones (cumple de sobra, pero el costo y la complejidad no se justifican para 300 usuarios).

## Consecuencias

- **Positivas:**
  - La caída de una instancia de la API o de la base de datos primaria no detiene el servicio.
  - La pérdida máxima de datos es de 15 minutos.
  - Las actualizaciones no generan caídas.
- **Negativas:**
  - Hay dependencia de proveedores externos (nube y Cloudflare) que procesan datos personales. Requiere revisar los contratos de tratamiento de datos (Ley 1581 de 2012).
  - Durante la conmutación de la base de datos (60 a 120 s) las escrituras fallan; la interfaz debe mostrar "intente de nuevo".
- **Verificación:**
  - **Disponibilidad:** apagar una instancia de la API en pruebas y comprobar que el servicio sigue. Forzar la conmutación de la base de datos y medir el tiempo. Medir la disponibilidad mensual con el monitor externo.
  - **Respaldo:** simulacro de restauración trimestral, midiendo el RPO y el RTO reales.
