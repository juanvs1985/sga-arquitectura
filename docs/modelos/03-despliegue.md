# 6.3 Modelo de despliegue

## Figura 3. Nodos, canales y controles de seguridad

```mermaid
%%{init: {"theme":"base","flowchart":{"nodeSpacing":35,"rankSpacing":55},"themeVariables":{"fontFamily":"Arial","fontSize":"15px","primaryColor":"#EEF2F7","primaryBorderColor":"#1F3864","primaryTextColor":"#14243F","lineColor":"#56657F","clusterBkg":"#FFFFFF","clusterBorder":"#1F3864"}}}%%
flowchart TB
    U["<b>Usuarios</b><br/>navegador en computador o móvil"]
    CF["<b>Cloudflare</b><br/>DNS · TLS · WAF · anti-DDoS<br/>límite de peticiones · CDN"]
    ST[("<b>Almacenamiento de objetos</b><br/>interfaz web compilada (SPA)")]

    subgraph NUBE["Proveedor de nube · región principal"]
        direction TB
        subgraph PUB["Subred pública"]
            LB["<b>Balanceador de carga</b><br/>HTTPS · health checks"]
        end
        subgraph PRIV["Subred privada · sin IP pública"]
            direction LR
            API1["<b>API SGA · nodo 1</b><br/>contenedor Docker<br/>monolito modular"]
            API2["<b>API SGA · nodo 2</b><br/>contenedor Docker<br/>monolito modular"]
        end
        subgraph DATOS["Base de datos administrada · subred privada"]
            direction LR
            PG1[("<b>PostgreSQL primaria</b><br/>zona A")]
            PG2[("<b>PostgreSQL réplica</b><br/>zona B")]
        end
        SEC["Gestor de secretos<br/>llaves JWT · credenciales"]
    end

    BK[("<b>Respaldo externo</b><br/>otra región o proveedor<br/>AES-256 · bloqueo 30 días")]
    MON["<b>Monitoreo y alertas</b><br/>disponibilidad · registros centralizados"]

    U -->|"HTTPS 443 · TLS 1.3"| CF
    CF -->|"archivos estáticos"| ST
    CF -->|"HTTPS /api/v1/*"| LB
    LB -->|"HTTPS · red privada"| API1
    LB -->|"HTTPS · red privada"| API2
    API1 -->|"TLS 5432 · solo desde la API"| PG1
    API2 -->|"TLS 5432 · solo desde la API"| PG1
    PG1 <-->|"replicación síncrona<br/>conmutación automática"| PG2
    PG1 -->|"copia diaria + WAL continuo"| BK
    SEC -.->|"inyecta al arrancar"| API1
    SEC -.->|"inyecta al arrancar"| API2
    MON -.->|"verifica cada minuto"| CF

    classDef edge fill:#F6EBD0,stroke:#A87A1E,color:#14243F
    classDef app fill:#1F3864,stroke:#1F3864,color:#FFFFFF
    classDef db fill:#E8EEF6,stroke:#56657F,color:#14243F
    class CF,LB,SEC,MON edge
    class API1,API2 app
    class PG1,PG2,BK,ST db
```

*Fuente: elaboración propia, a partir de la propuesta P6 de Google AI Studio con las correcciones de la evaluación (ADR-003).*

## Nodos

| Nodo | Qué ejecuta | Por qué |
|---|---|---|
| Cloudflare | DNS, TLS, WAF, anti-DDoS, límite de peticiones y CDN | Primera línea de defensa y distribución de la interfaz sin costo adicional (RNF-01, RNF-02). |
| Almacenamiento de objetos | Interfaz web compilada (HTML, CSS, JS) | Archivos estáticos sin consumir CPU de la API (RNF-12). |
| Balanceador de carga administrado | Reparte el tráfico HTTPS entre los nodos y verifica su salud | Si un nodo falla, el tráfico pasa al otro en segundos. Al ser administrado, el proveedor lo mantiene redundante, así que no es un punto único de falla (RNF-03; crítica de la IA en P7). |
| API SGA · nodos 1 y 2 | El monolito modular en contenedores Docker, sin estado | Redundancia y escalado horizontal: agregar un tercer nodo no requiere cambios (RNF-04, ADR-004). |
| PostgreSQL primaria y réplica | Base de datos administrada en dos zonas | Elimina el punto único de falla de la base de datos, con conmutación automática (RNF-03, RNF-07). |
| Respaldo externo | Copia diaria y WAL continuo, cifrados y con bloqueo de 30 días | RPO de 15 min y RTO de 2 h; protección contra *ransomware* (RNF-09). |
| Gestor de secretos | Llaves JWT y credenciales | Nada sensible en el repositorio (RNF-01). |
| Monitoreo y alertas | Verificación de disponibilidad y registros centralizados | Medir el 99,5 % y reaccionar a tiempo (RNF-03, RNF-10). |

## Controles de seguridad por canal

| Canal | Protocolo | Control |
|---|---|---|
| Usuario → Cloudflare | HTTPS 443, TLS 1.3 | Redirección forzada de HTTP a HTTPS; WAF y límite de peticiones. |
| Cloudflare → Balanceador | HTTPS | Solo se aceptan conexiones desde Cloudflare. |
| Balanceador → API | HTTPS en red privada | Los nodos no tienen IP pública. |
| API → PostgreSQL | TLS, puerto 5432 | Subred privada; el puerto solo acepta tráfico de los nodos de la API; usuario de base de datos con permisos mínimos por esquema. |
| PostgreSQL → Respaldo | Cifrado AES-256 | Almacenamiento en otra región o proveedor, con bloqueo de objetos. |
