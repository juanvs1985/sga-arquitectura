# ADR-001: Monolito modular en capas como estilo arquitectónico

- **Estado:** Aceptado
- **Fecha:** 2026-11-04
- **Requerimientos relacionados:** RNF-02, RNF-03, RNF-04, RNF-05, RNF-07, RNF-09

## Contexto

El SGA debe atender hasta 300 usuarios concurrentes (RNF-02), con 99,5 % de disponibilidad mensual (RNF-03). Tiene que poder crecer sin un rediseño total (RNF-04) y permitir cambiar un módulo sin afectar a los demás (RNF-05). Su proceso más delicado es la matrícula: dos solicitudes simultáneas por el último cupo no pueden producir un sobrecupo (RNF-07). La institución tiene un presupuesto moderado y el equipo de desarrollo es pequeño.

## Decisión

Construiremos el SGA como un **monolito modular**: una sola aplicación desplegable, dividida en seis módulos por contexto de negocio:

- Identidad y acceso
- Gestión académica
- Matrículas
- Calificaciones
- Reportes
- Auditoría

Cada módulo se organiza internamente en tres **capas**: controlador REST, dominio y repositorio. Un módulo solo usa a otro a través de su interfaz pública y es dueño de su propio esquema en una única base de datos PostgreSQL. La interfaz web es una aplicación separada que consume la API REST.

## Opciones consideradas

1. **Arquitectura en capas sin módulos:** simple, pero sin límites entre áreas de negocio. Con el tiempo, matrícula, notas y auditoría terminarían acopladas.
2. **Monolito modular en capas** (elegida).
3. **Microservicios:** un servicio y una base de datos por módulo.

## Argumentos

| Criterio | Capas sin módulos | Monolito modular (elegida) | Microservicios |
|---|---|---|---|
| Consistencia de la matrícula (RNF-07) | Transacción ACID local | Transacción ACID local | Consistencia eventual (Sagas); riesgo de sobrecupo |
| Rendimiento con 300 usuarios (RNF-02) | Suficiente | Llamadas en memoria, sin red | Latencia entre servicios |
| Disponibilidad (RNF-03) | 2 réplicas + balanceador | 2 réplicas + balanceador | Alta, pero con fallos en cascada |
| Mantenibilidad (RNF-05) | Se degrada con el tiempo | Módulos cohesivos con interfaces | Alta por servicio, pero con contratos distribuidos |
| Costo y operación | Bajo | Bajo: un solo artefacto | Alto: orquestador, trazas distribuidas |

## Consecuencias

**Positivas:**
- La matrícula se resuelve con una transacción en una sola base de datos.
- Un solo artefacto que desplegar y respaldar.
- Si el día de mañana un módulo necesita escalar por separado, se puede extraer como servicio con el patrón Strangler Fig.

**Negativas:**
- El sistema escala completo, no por módulo.
- Los límites entre módulos dependen de la disciplina del equipo; se controlarán con pruebas de arquitectura (por ejemplo, ArchUnit o una regla equivalente en el lenguaje elegido).
- La base de datos es un punto único de falla si no se replica (ver ADR-003 y el análisis de riesgos).
