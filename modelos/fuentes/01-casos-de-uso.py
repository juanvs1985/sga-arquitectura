"""Genera el diagrama UML de casos de uso del SGA como SVG (sin dependencias externas).

Uso: python3 01-casos-de-uso.py  ->  escribe ../imagenes/01-casos-de-uso.svg
"""
from pathlib import Path

W, H = 1400, 1000
NAVY, INK, MUTED, LINE, FILL, GOLD, GOLD_FILL = "#1F3864", "#14243F", "#56657F", "#56657F", "#EEF2F7", "#A87A1E", "#F6EBD0"

# Casos de uso: id -> (x, y, texto línea 1, texto línea 2)
CU = {
    "CU-01": (700, 120, "CU-01 Iniciar y", "cerrar sesión"),
    "CU-15": (700, 560, "CU-15 Registrar evento", "de auditoría"),
    "CU-13": (700, 900, "CU-13 Buscar y", "filtrar registros"),
    "CU-02": (465, 110, "CU-02 Gestionar", "usuarios y roles"),
    "CU-14": (465, 195, "CU-14 Consultar", "auditoría"),
    "CU-03": (465, 280, "CU-03 Gestionar", "estudiantes"),
    "CU-04": (465, 365, "CU-04 Gestionar", "docentes"),
    "CU-12": (465, 450, "CU-12 Generar", "reportes"),
    "CU-05": (465, 535, "CU-05 Gestionar programas,", "planes y asignaturas"),
    "CU-06": (465, 620, "CU-06 Configurar", "periodos y grupos"),
    "CU-07": (465, 705, "CU-07 Matricular", "estudiante"),
    "CU-10": (465, 790, "CU-10 Cerrar notas", "del periodo"),
    "CU-08": (935, 420, "CU-08 Registrar", "calificaciones"),
    "CU-09": (935, 510, "CU-09 Publicar", "calificaciones"),
    "CU-11": (935, 640, "CU-11 Consultar", "horario y notas"),
}
ACTORES = {
    "Administrador": (110, 290, ["CU-01", "CU-02", "CU-14", "CU-03", "CU-04", "CU-12", "CU-13"]),
    "Coordinador académico": (110, 690, ["CU-01", "CU-03", "CU-04", "CU-12", "CU-05", "CU-06", "CU-07", "CU-10", "CU-13"]),
    "Docente": (1290, 420, ["CU-01", "CU-13", "CU-08", "CU-09"]),
    "Estudiante": (1290, 655, ["CU-01", "CU-11"]),
}
INCLUDES = ["CU-01", "CU-02", "CU-07", "CU-08"]  # todos incluyen CU-15
RX, RY = 112, 32


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def actor(name, x, y):
    s = [f'<g stroke="{INK}" stroke-width="2.2" fill="none">',
         f'<circle cx="{x}" cy="{y-48}" r="13" fill="#FFFFFF"/>',
         f'<line x1="{x}" y1="{y-35}" x2="{x}" y2="{y+5}"/>',
         f'<line x1="{x-22}" y1="{y-22}" x2="{x+22}" y2="{y-22}"/>',
         f'<line x1="{x}" y1="{y+5}" x2="{x-18}" y2="{y+35}"/>',
         f'<line x1="{x}" y1="{y+5}" x2="{x+18}" y2="{y+35}"/>', '</g>']
    for i, part in enumerate(name.split(" ")):
        s.append(f'<text x="{x}" y="{y+58+i*17}" text-anchor="middle" font-weight="700" fill="{INK}">{esc(part)}</text>')
    return "\n".join(s)


def edge_point(cx, cy, tx, ty):
    """Punto del borde de la elipse en dirección al destino."""
    import math
    a = math.atan2(ty - cy, tx - cx)
    return cx + RX * math.cos(a), cy + RY * math.sin(a)


out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Arial, Helvetica, sans-serif" font-size="14">',
       '<defs><marker id="open" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">'
       f'<path d="M0,0 L10,5 L0,10" fill="none" stroke="{GOLD}" stroke-width="1.6"/></marker></defs>',
       f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
       f'<rect x="300" y="40" width="800" height="920" rx="6" fill="#FFFFFF" stroke="{NAVY}" stroke-width="2"/>',
       f'<text x="700" y="68" text-anchor="middle" font-size="16" font-weight="700" fill="{NAVY}">Sistema de Gestión Académica (SGA)</text>']

# Asociaciones actor - caso de uso (se dibujan primero, quedan detrás de las elipses)
for name, (ax, ay, cus) in ACTORES.items():
    sx = ax + (26 if ax < W / 2 else -26)
    for c in cus:
        cx, cy = CU[c][0], CU[c][1]
        ex, ey = edge_point(cx, cy, sx, ay - 15)
        out.append(f'<line x1="{sx}" y1="{ay-15}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{LINE}" stroke-width="1.3"/>')

# «include» hacia CU-15
tx, ty = CU["CU-15"][0], CU["CU-15"][1]
for c in INCLUDES:
    cx, cy = CU[c][0], CU[c][1]
    if c == "CU-01":
        sx, sy, ex, ey = cx, cy + RY, tx, ty - RY
    elif cx < tx:
        sx, sy = cx + RX - 8, cy + (12 if cy < ty else -12)
        ex, ey = edge_point(tx, ty, sx, sy)
    else:
        sx, sy = cx - RX + 8, cy + 12
        ex, ey = edge_point(tx, ty, sx, sy)
    path = f'M{sx:.1f},{sy:.1f} L{ex:.1f},{ey:.1f}'
    lx, ly = (sx + ex) / 2 + (38 if c == "CU-01" else 0), (sy + ey) / 2
    out.append(f'<path d="{path}" fill="none" stroke="{GOLD}" stroke-width="1.5" stroke-dasharray="6 4" marker-end="url(#open)"/>')
    out.append(f'<text x="{lx:.0f}" y="{ly-4:.0f}" text-anchor="middle" font-size="12" fill="{GOLD}" stroke="#FFFFFF" stroke-width="4" paint-order="stroke">«include»</text>')

# Elipses de casos de uso
for c, (x, y, l1, l2) in CU.items():
    fill, stroke = (GOLD_FILL, GOLD) if c == "CU-15" else (FILL, NAVY)
    out.append(f'<ellipse cx="{x}" cy="{y}" rx="{RX}" ry="{RY}" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>')
    out.append(f'<text x="{x}" y="{y-3}" text-anchor="middle" fill="{INK}">{esc(l1)}</text>')
    out.append(f'<text x="{x}" y="{y+14}" text-anchor="middle" fill="{INK}">{esc(l2)}</text>')

for name, (ax, ay, _) in ACTORES.items():
    out.append(actor(name, ax, ay))

out.append(f'<text x="700" y="990" text-anchor="middle" font-size="12" fill="{MUTED}">CU-15 es interno: lo incluyen los casos auditables (RF-12). Fuente: elaboración propia.</text>')
out.append('</svg>')

dest = Path(__file__).resolve().parent.parent / "imagenes" / "01-casos-de-uso.svg"
dest.write_text("\n".join(out), encoding="utf-8")
print("escrito", dest)
