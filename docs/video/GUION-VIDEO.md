# Guion del video: Arquitectura del SGA con Google AI Studio

**Duración objetivo:** 5:00 (máximo permitido: 5 a 6 minutos) · **Narración:** 616 palabras, unos 4 min 30 s leídos con calma; el resto son pausas para hacer clic · **Formato:** grabación de pantalla con tu voz (cámara opcional en una esquina)

---

## Antes de grabar (15 minutos)

**Pestañas abiertas en este orden** (así solo cambias de pestaña, sin buscar nada):

1. El informe en PDF, abierto en la portada.
2. El informe en la página de la **Tabla de requerimientos no funcionales** (sección 4).
3. **AI Studio · Playground** con la conversación de los 7 prompts, en el P1.
4. El informe en la **Figura 2** (módulos e interfaces).
5. El informe en la **Figura 9** (diagrama ilegible de la IA) o la captura `P3-06.png`.
6. El informe en la tabla **"Resultado de la evaluación"** (47 / 40 / 6).
7. **AI Studio · Build** con el prototipo abierto en la pantalla de inicio de sesión.
8. El repositorio en GitHub: `github.com/juanvs1985/sga-arquitectura`.

**Configuración:**

- Zoom del navegador al **125 %**, para que se lea en el video.
- Cierra WhatsApp, correo y notificaciones de Windows (Configuración → Sistema → Notificaciones → No molestar).
- Prepara el prototipo:
  - Pulsa **Restablecer a 29/30** antes de grabar.
  - Ten a mano un estudiante para el caso de cruce de horario.
- Graba con **Xbox Game Bar** (`Windows + Alt + R` para iniciar y detener) o con **Clipchamp** (viene con Windows 11 y permite cortar al final).
- Haz una prueba de 20 segundos para revisar que el micrófono se escuche bien.

**Consejo:** no tienes que leer palabra por palabra. Lee el guion dos veces en voz alta antes de grabar y luego usa las **frases en negrita** como apoyo. Si te equivocas, haz una pausa de dos segundos y repite la frase: luego cortas en Clipchamp.

---

## Escena 1 · Apertura — 0:00 a 0:25

**En pantalla:** portada del informe (pestaña 1).

**Lo que dices:**

> Hola, soy Juan Pablo Vargas Sánchez, estudiante de Ingeniería de Sistemas de la CUN. En este video presento el diseño de la arquitectura de un **Sistema de Gestión Académica** para una institución de educación superior, construido a partir de 24 requerimientos y con **Google AI Studio como herramienta de apoyo**. Les voy a mostrar cómo lo hice, qué propuso la inteligencia artificial y, sobre todo, **qué le acepté y qué le corregí**.

*(72 palabras)*

---

## Escena 2 · El problema y el análisis — 0:25 a 0:55

**En pantalla:** tabla de requerimientos no funcionales (pestaña 2). Desplázate despacio.

**Lo que dices:**

> El problema: hoy la información académica está en archivos y aplicaciones separadas, con **datos duplicados, consultas lentas y sin trazabilidad**. Antes de abrir la IA hice mi propio análisis: identifiqué cuatro actores, administrador, coordinador, docente y estudiante, y le puse a cada requerimiento un **criterio verificable**. Por ejemplo, el rendimiento quedó como "el 95 % de las consultas en menos de 3 segundos con 300 usuarios". Hacer esto primero fue clave, porque me dio con qué comparar lo que respondiera la IA.

*(82 palabras)*

---

## Escena 3 · Cómo usé AI Studio — 0:55 a 1:50

**En pantalla:** AI Studio Playground (pestaña 3).

1. Señala con el mouse el panel derecho: **Gemini 3.8 Flash**, **Thinking: High**, **Grounding apagado**.
2. Muestra el prompt P1 completo.
3. Baja despacio por la conversación, pasando por los prompts P2 a P7.

**Lo que dices:**

> En AI Studio configuré Gemini 3.8 Flash con razonamiento alto y **desactivé la búsqueda en Google**, para que trabajara solo con el caso. Armé **siete prompts en una sola conversación**, en el mismo orden en que se diseña una arquitectura. En el primero le entregué el contexto y los 24 requerimientos completos y le pedí actores, supuestos y reglas de negocio. Después le pedí comparar estilos arquitectónicos, luego los componentes, el modelo de datos, la secuencia de la matrícula y el despliegue. Y en el séptimo le pedí algo importante: que **criticara su propia propuesta** como si fuera un evaluador externo.

*(101 palabras)*

---

## Escena 4 · La arquitectura resultante — 1:50 a 2:40

**En pantalla:** Figura 2, módulos e interfaces (pestaña 4). Señala cada módulo mientras lo nombras.

**Lo que dices:**

> El resultado es un **monolito modular en capas**: una sola aplicación con seis módulos, identidad y acceso, gestión académica, matrículas, calificaciones, reportes y auditoría. Cada módulo tiene sus propias capas y su propio esquema en la base de datos, y solo se comunica con los otros por **interfaces**. ¿Por qué no microservicios? Porque el requisito más delicado es que **la matrícula nunca genere sobrecupo**, y eso se garantiza mucho mejor con una transacción en una sola base de datos. Lo despliego en dos servidores detrás de un balanceador y con PostgreSQL replicado, para cumplir el **99,5 % de disponibilidad**.

*(99 palabras)*

---

## Escena 5 · El uso crítico de la IA — 2:40 a 3:30

**En pantalla:**

1. Diagrama ilegible de la IA (pestaña 5). Déjalo **3 segundos**.
2. Cambia a la tabla 47 / 40 / 6 (pestaña 6).

**Lo que dices:**

> Aquí está lo más importante. Evalué las **93 propuestas** de la IA una por una: **acepté 47, modifiqué 40 y descarté 6**. La IA acertó en lo grande, recomendó el mismo estilo, pero cometió errores serios. Propuso una **auditoría asíncrona** que podía perder registros si el servidor se caía; la corregí para que se guarde en la misma transacción del cambio. Insistió **cuatro veces en agregar Redis** sin que ningún requerimiento lo pidiera. Y sus diagramas, como este, salieron ilegibles, así que los redibujé todos.

*(85 palabras)*

---

## Escena 6 · El prototipo en AI Studio Build — 3:30 a 4:35

**En pantalla:** prototipo en Build (pestaña 7).

1. Inicia sesión con `javier.morales@sga.edu.co` y muestra que **pide elegir el rol**. Elige **Coordinador**.
2. Ve a **Matrículas & Concurrencia** y pulsa el **botón amarillo**. Muestra el resultado: 201 y 409.
3. Señala el recuadro **"Fundamento Arquitectónico"** (versión antes de la corrección, si la capturaste).
4. Si alcanzas: intenta una matrícula con **cruce de horario** y muestra el rechazo.

**Lo que dices:**

> Además, con **AI Studio Build** generé un prototipo navegable, pero no con un "hazme un sistema académico", sino entregándole **mi arquitectura ya diseñada**. Este usuario tiene dos roles, y el sistema le pide elegir con cuál trabajar. En matrículas, este botón simula **dos estudiantes pidiendo el último cupo**: uno queda matriculado y el otro recibe un rechazo. Pero ojo con dos cosas. Primero, esto es una simulación en el navegador; la garantía real la da el **bloqueo de fila en PostgreSQL**. Y segundo, miren esta explicación: la IA bloquea la **tabla de grupos**, que es de otro módulo. Ese error ya se lo había corregido en el diseño, y aquí lo repitió; se lo volví a corregir.

*(117 palabras)*

---

## Escena 7 · Cierre — 4:35 a 5:00

**En pantalla:** repositorio en GitHub (pestaña 8). Baja despacio por el README.

**Lo que dices:**

> Todo está en este repositorio: el análisis, los seis modelos, las cinco decisiones de arquitectura y todas las evidencias de AI Studio. Mi conclusión es que **la IA aceleró mucho el trabajo, pero no lo reemplazó**: acierta en lo general y aporta buenas ideas, pero se contradice y repite errores. **Hay que revisar cada respuesta contra los requerimientos.** Muchas gracias.

*(60 palabras)*

---

## Tarjeta de apoyo (si prefieres no leer)

| Tiempo | Pantalla | Idea clave |
|---|---|---|
| 0:00 | Portada | Quién soy · SGA · 24 requerimientos · qué acepté y qué corregí |
| 0:25 | Tabla RNF | Problema · 4 actores · criterios verificables · análisis propio primero |
| 0:55 | Playground | Gemini 3.8 Flash · sin grounding · 7 prompts en orden · P7 autocrítica |
| 1:50 | Figura 2 | Monolito modular · 6 módulos · interfaces · por qué no microservicios · 99,5 % |
| 2:40 | Diagrama IA → tabla | 93 propuestas: 47 / 40 / 6 · auditoría asíncrona · Redis ×4 · diagramas ilegibles |
| 3:30 | Build | Mi arquitectura como prompt · rol activo · último cupo 201/409 · es simulación · error de la tabla grupos repetido |
| 4:35 | GitHub | Todo en el repositorio · la IA acelera, no reemplaza · revisar contra requerimientos |

---

## Después de grabar: subir a YouTube

1. Entra a **studio.youtube.com** con tu cuenta y toca **Crear → Subir videos**.
2. **Título:** `Arquitectura de un Sistema de Gestión Académica con Google AI Studio · Arquitectura de Software CUN`
3. **Descripción:**
   ```
   Actividad de aprendizaje · Arquitectura de Software (INGS0763) · CUN
   Estudiante: Juan Pablo Vargas Sánchez · Docente: Alexander Calderón Martínez

   Repositorio: https://github.com/juanvs1985/sga-arquitectura

   0:00 Presentación
   0:25 Problema y análisis de requerimientos
   0:55 Uso de Google AI Studio
   1:50 Arquitectura propuesta
   2:40 Evaluación crítica de la IA
   3:30 Prototipo en AI Studio Build
   4:35 Conclusiones
   ```
4. **Audiencia:** "No, no es contenido para niños".
5. **Visibilidad:** **No listado**. El video no aparece en búsquedas, pero cualquiera con el enlace lo ve, incluido el docente. Si prefieres que sea público, también sirve.
6. Copia el enlace y **mándamelo**: lo agrego al informe y regenero el PDF.
