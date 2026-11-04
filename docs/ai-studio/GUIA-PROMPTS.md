# Guía de prompts para Google AI Studio

**Proyecto:** Arquitectura de un Sistema de Gestión Académica (SGA)
**Asignatura:** Arquitectura de Software · CUN
**Uso:** correr los prompts en orden, en una sola conversación, y guardar evidencia de cada uno.

---

## Antes de empezar (5 minutos)

1. Entra a **aistudio.google.com** con tu cuenta de Google.
2. Abre **Create prompt** (chat nuevo). Deja el modelo que aparece por defecto (Gemini Pro o Flash) y **anota su nombre**: va en el informe.
3. Corre los 7 prompts **en orden y en el mismo chat**, para que la IA recuerde el contexto.
4. Después de cada respuesta:
   - Toma una **captura** donde se vean tu prompt y el inicio de la respuesta. Nómbrala `P1.png`, `P2.png`, etc.
   - Copia la **respuesta completa** (botón de copiar o seleccionando el texto) y pégala en un archivo de texto `respuestas-ai-studio.txt`, con el título `=== P1 ===`, `=== P2 ===`, etc.
5. Al terminar, pásame el archivo de texto y las capturas. Con eso armo la tabla de lo **aceptado, modificado y descartado**, que vale parte del 15 %.

**Importante:**
- No pongas nombres reales de estudiantes, correos ni contraseñas en los prompts.
- No le corrijas nada a la IA durante los prompts 1 a 6. Que proponga lo que quiera: la nota está en mostrar que la revisamos con criterio. El prompt 7 es la parte crítica.
- Si una respuesta sale cortada, escribe **"continúa"** y captura también esa parte.

Tiempo estimado: 45 a 60 minutos.

---

## P1 · Análisis del problema

```text
Actúa como arquitecto de software senior. Te voy a dar el caso de un Sistema de Gestión Académica (SGA) para una institución de educación superior. Necesito analizarlo antes de diseñar la arquitectura.

CONTEXTO: La institución requiere un SGA que centralice la información de estudiantes, docentes, programas académicos, asignaturas, grupos, matrículas, calificaciones y horarios. Hoy parte de la información se maneja en archivos y aplicaciones independientes, lo que genera duplicidad de datos, demoras en la consulta y dificultades de trazabilidad. La solución debe ser segura, mantenible, escalable y accesible desde navegadores web.

REQUERIMIENTOS FUNCIONALES:
RF-01 Autenticación: iniciar y cerrar sesión con credenciales individuales.
RF-02 Roles y permisos: mínimo administrador, coordinador académico, docente y estudiante; restringir funciones según permisos.
RF-03 Gestión de estudiantes: registrar, consultar, actualizar y desactivar estudiantes.
RF-04 Gestión de docentes: registrar, consultar, actualizar y desactivar docentes.
RF-05 Programas y asignaturas: crear y actualizar programas, planes de estudio y asignaturas (código, nombre, créditos, semestre o nivel).
RF-06 Grupos y periodos: configurar periodos académicos, grupos, cupos, docentes asignados, horarios y aulas o enlaces.
RF-07 Matrícula: matricular estudiantes en asignaturas o grupos de un periodo, validar cupos y evitar matrículas duplicadas.
RF-08 Calificaciones: el docente registra y actualiza calificaciones de los estudiantes de sus grupos.
RF-09 Consulta de resultados: el estudiante consulta asignaturas matriculadas, horarios y calificaciones publicadas.
RF-10 Reportes: reportes básicos de matriculados, grupos, asignaturas y resultados, con filtros por periodo y programa.
RF-11 Búsqueda y filtros: buscar y filtrar por identificadores, nombres, programa, periodo o estado.
RF-12 Auditoría: registrar inicios de sesión, cambios de roles, matrículas y modificaciones de calificaciones (usuario, fecha, acción, registro afectado).

REQUERIMIENTOS NO FUNCIONALES:
RNF-01 Seguridad: HTTPS, contraseñas no en texto plano, acceso por roles y permisos.
RNF-02 Rendimiento: el 95 % de las consultas comunes responde en máximo 3 segundos con hasta 300 usuarios concurrentes.
RNF-03 Disponibilidad: objetivo mensual de al menos 99,5 %, excluyendo mantenimientos programados.
RNF-04 Escalabilidad: aumentar recursos y atender crecimiento sin rediseñar todo el sistema.
RNF-05 Mantenibilidad: separar responsabilidades, bajo acoplamiento y cohesión adecuada.
RNF-06 Usabilidad y accesibilidad: interfaz consistente, adaptable a móvil, etiquetas claras, contraste y operación por teclado.
RNF-07 Integridad y consistencia: matrícula y calificaciones validan reglas de negocio y preservan consistencia ante errores o solicitudes simultáneas.
RNF-08 Interoperabilidad: interfaces documentadas, preferiblemente API REST.
RNF-09 Respaldo y recuperación: copias periódicas y procedimiento de restauración.
RNF-10 Trazabilidad: relacionar decisiones y requerimientos con componentes, modelos y evidencias.
RNF-11 Privacidad: limitar acceso a datos personales y académicos según el rol.
RNF-12 Compatibilidad: navegadores recientes y distintos tamaños de pantalla.

TAREA: 
1. Identifica los actores principales y secundarios.
2. Propón supuestos razonables donde el caso no es explícito.
3. Lista las restricciones técnicas y del negocio.
4. Extrae las reglas de negocio implícitas en los requerimientos (por ejemplo, sobre cupos, matrículas duplicadas y quién puede modificar calificaciones).
5. Clasifica cada RNF según el atributo de calidad que representa.
Responde en español, con tablas cuando ayuden.
```

---

## P2 · Propuesta de estilo arquitectónico

```text
Con base en el análisis anterior, propón el estilo arquitectónico para el SGA. 
Compara al menos tres opciones: arquitectura en capas, monolito modular y microservicios. 
Para cada una evalúa: complejidad de desarrollo y operación, rendimiento con 300 usuarios concurrentes, disponibilidad del 99,5 %, escalabilidad, mantenibilidad y consistencia en la matrícula ante solicitudes simultáneas. 
Al final recomienda una opción y justifícala frente a los requerimientos no funcionales. Responde en español con una tabla comparativa.
```

---

## P3 · Componentes y vista lógica

```text
Para la arquitectura que recomendaste, describe la vista lógica: 
los módulos o componentes principales, la responsabilidad de cada uno, las interfaces que exponen (por ejemplo, endpoints REST principales) y las dependencias entre ellos. 
Debe quedar claro cómo se organizan autenticación y autorización, gestión académica, matrículas, calificaciones, reportes y auditoría. 
Genera además el diagrama en sintaxis Mermaid.
```

---

## P4 · Modelo de datos conceptual

```text
Propón el modelo de datos conceptual del SGA con las entidades: Usuario, Rol, Estudiante, Docente, Programa, Asignatura, PeriodoAcadémico, Grupo, Matrícula y Calificación, más las que consideres necesarias (por ejemplo, para horarios o auditoría). 
Indica los atributos principales y las cardinalidades de cada relación, y explica las restricciones que evitan matrículas duplicadas. 
Genera el diagrama entidad-relación en sintaxis Mermaid (erDiagram).
```

---

## P5 · Secuencia de la matrícula

```text
Modela el diagrama de secuencia del proceso de matrícula de un estudiante en un grupo. 
Incluye los participantes (estudiante o coordinador, interfaz web, API, módulos internos, base de datos y auditoría), el orden de los mensajes, la validación de cupo, la validación de matrícula duplicada y qué pasa si dos solicitudes llegan al mismo tiempo por el último cupo. 
Genera el diagrama en sintaxis Mermaid (sequenceDiagram).
```

---

## P6 · Despliegue, seguridad y respaldo

```text
Propón el modelo de despliegue del SGA: nodos o servicios donde se ejecutan la interfaz web, la API, la base de datos y los servicios complementarios. 
Indica los canales de comunicación, los controles de seguridad (HTTPS, firewall, manejo de contraseñas, tokens), cómo se logra la disponibilidad del 99,5 % y cómo serían las copias de seguridad y la restauración. 
Considera que es una institución con presupuesto moderado. Genera el diagrama en sintaxis Mermaid.
```

---

## P7 · Revisión crítica de la propia propuesta

```text
Ahora actúa como evaluador externo y critica la arquitectura que propusiste en esta conversación. 
1. ¿Qué requerimientos funcionales o no funcionales quedaron sin cubrir o cubiertos de forma débil? 
2. ¿Qué puntos únicos de falla existen? 
3. ¿Qué riesgos de seguridad y privacidad ves? 
4. ¿Cuáles son los límites de escalabilidad? 
5. ¿Qué decisiones requieren validación adicional y cómo se validarían (pruebas de carga, pruebas de concurrencia, simulacros de restauración)? 
Sé concreto y no repitas lo que ya dijiste.
```

---

## Qué me devuelves

- [ ] Nombre del modelo usado en AI Studio y fecha.
- [ ] Capturas `P1.png` a `P7.png` (y las de "continúa", si hubo).
- [ ] Archivo `respuestas-ai-studio.txt` con las 7 respuestas completas.
