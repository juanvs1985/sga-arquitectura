# ADR-004: Autenticación sin estado con token de acceso corto y token de renovación

- **Estado:** Aceptado
- **Fecha:** 2026-11-04
- **Requerimientos relacionados:** RF-01, RF-02, RNF-01, RNF-03, RNF-04, RNF-11

## Contexto

La API corre en dos o más réplicas detrás de un balanceador (RNF-03, RNF-04). Si la sesión se guarda en la memoria de una réplica, el usuario pierde la sesión cuando el balanceador lo envía a otra. Además, cerrar sesión (RF-01) debe invalidar el acceso de verdad, y se descartó usar Redis (evaluación P2).

## Decisión

- Al iniciar sesión, el módulo Identidad y acceso verifica la contraseña contra su hash **Argon2id** y entrega:
  - un **token de acceso JWT** firmado, de vida corta (15 minutos), con el identificador del usuario y su rol;
  - un **token de renovación** opaco, de vida más larga (8 horas), guardado como hash en la tabla `sesion` del esquema de identidad.
- Cada réplica valida el JWT sin consultar la base de datos.
- Cada vez que se usa el token de renovación se emite uno nuevo y se invalida el anterior (**rotación**). Si se detecta el uso de un token ya rotado, se revoca toda la sesión *(aporte de la IA, P6)*.
- **Cerrar sesión** revoca el token de renovación en la base de datos. El token de acceso expira solo en máximo 15 minutos.
- Si el usuario tiene varios roles (S-05), elige al entrar el perfil con el que trabajará. El token lleva un único **rol activo** y los permisos se evalúan con ese rol; cambiar de perfil emite un token nuevo *(mitigación señalada por la IA en P7)*.
- El rol viaja en el token, pero la **autorización fina** ("solo mis grupos", "solo mis notas") la decide el dominio de cada módulo (RN-05, RN-08).
- Los tokens viajan solo por HTTPS. En el navegador, el token de renovación se guarda en una cookie `HttpOnly`, `Secure` y `SameSite=Strict`.

## Opciones consideradas

1. **JWT corto + token de renovación en base de datos** (elegida).
2. Sesión en memoria del servidor con "sesión pegajosa" en el balanceador.
3. JWT con lista negra en Redis.

## Consecuencias

- **Positivas:** cualquier réplica atiende cualquier petición, y se puede escalar horizontalmente sin cambios. Además, no hay un componente adicional que operar.
- **Negativas:** tras cerrar sesión, el token de acceso sigue siendo válido hasta 15 minutos. Es un riesgo aceptado y mitigado por la vida corta del token.
- **Extensión futura:** el inicio de sesión se aísla detrás de una interfaz, para poder agregar SSO institucional (Google o Microsoft) sin tocar los demás módulos.
