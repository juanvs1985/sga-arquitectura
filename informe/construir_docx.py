"""Genera la versión Word (.docx) del informe sencillo.

Pasos: 1) node informe/volcar_dom.js  (HTML ya procesado por el navegador)
       2) python3 informe/construir_docx.py
"""
import copy
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parent
IMG = RAIZ / "modelos" / "imagenes"
TMP = DIR / ".docx_tmp"
TMP.mkdir(exist_ok=True)
SALIDA = DIR / "Informe_SGA_Vargas_Juan_Pablo.docx"

html = (TMP / "dom.html").read_text(encoding="utf-8")

# ---------------------------------------------------------------- 1. limpiar el HTML
html = re.sub(r"<script.*?</script>", "", html, flags=re.S)
html = re.sub(r"<style.*?</style>", "", html, flags=re.S)
html = re.sub(r'<section class="toc-pagina">.*?</section>', "<p>[[INDICE]]</p>", html, flags=re.S)

# portada
def portada(m):
    ps = re.findall(r"<p[^>]*>(.*?)</p>", m.group(1), flags=re.S)
    out = ["<p>[[PORTADA_INICIO]]</p>"]
    for p in ps:
        p = re.sub(r"<span[^>]*>(.*?)</span>", r"\1", p)
        out.append(f"<p>{p}</p>")
    out.append("<p>[[PORTADA_FIN]]</p>")
    return "\n".join(out)
html = re.sub(r'<section class="portada">(.*?)</section>', portada, html, flags=re.S)

# títulos sin número
html = re.sub(r'<h2 class="nonum"', '<h2 class="unnumbered"', html)
html = re.sub(r'<h3 class="nonum[^"]*"', '<h3 class="unnumbered"', html)

# títulos de figuras y tablas (negrita / cursiva)
html = re.sub(r'<p class="(?:fig|tab)-num">(.*?)</p>', r"<p><strong>\1</strong></p>", html)
html = re.sub(r'<p class="(?:fig|tab)-tit">(.*?)</p>', r"<p><em>\1</em></p>", html)
html = re.sub(r'<p class="fig-nota">(.*?)</p>', r"<p>\1</p>", html)

# imágenes: SVG -> PNG y ancho en cm
def img(m):
    tag = m.group(0)
    src = re.search(r'src="([^"]+)"', tag).group(1)
    if src.endswith(".svg"):
        src = src[:-4] + ".png"
    return f'<img src="{src}" __ANCHO__>'
html = re.sub(r"<img[^>]*>", img, html)

# figuras horizontales
def horiz(m):
    cuerpo = m.group(1).replace("__ANCHO__", 'width="23cm"')
    return f"<p>[[H_INICIO]]</p>{cuerpo}<p>[[H_FIN]]</p>"
html = re.sub(r'<section class="horizontal">(.*?)</section>', horiz, html, flags=re.S)

# capturas del anexo B en una tabla de dos columnas
def capturas(m):
    figs = re.findall(r'<figure class="cap">.*?<img src="([^"]+)"[^>]*>.*?<figcaption>(.*?)</figcaption>.*?</figure>', m.group(1), flags=re.S)
    filas = []
    for i in range(0, len(figs), 2):
        celdas = []
        for src, cap in figs[i:i + 2]:
            celdas.append(f'<td><img src="{src}" width="7.6cm"><br>{cap}</td>')
        if len(celdas) == 1:
            celdas.append("<td></td>")
        filas.append("<tr>" + "".join(celdas) + "</tr>")
    return '<p>[[CAPTURAS]]</p><table><tbody>' + "".join(filas) + "</tbody></table>"
html = re.sub(r'<div class="capturas">(.*?)</div>', capturas, html, flags=re.S)

# el resto de imágenes: ancho según el estilo original
def ancho_resto(m):
    tag = m.group(0)
    return tag.replace("__ANCHO__", 'width="15.5cm"')
html = re.sub(r'<img[^>]*__ANCHO__[^>]*>', ancho_resto, html)
html = html.replace('class="pendiente"', "")
html = re.sub(r'<figure class="fig">(.*?)</figure>', lambda m: re.sub(r'(<img[^>]*>)', r'<p>\1</p>', m.group(1)), html, flags=re.S)

(TMP / "limpio.html").write_text(html, encoding="utf-8")

# ---------------------------------------------------------------- 2. documento de referencia (estilos)
ref = TMP / "ref.docx"
subprocess.run(["pandoc", "-o", str(ref), "--print-default-data-file", "reference.docx"], check=True)
d = Document(ref)
_por_id = {x.style_id: x for x in d.styles}
_alias = {"Normal": "Normal", "Body Text": "BodyText", "First Paragraph": "FirstParagraph", "Compact": "Compact",
          "Heading 1": "Heading1", "Heading 2": "Heading2", "Title": "Title", "Subtitle": "Subtitle",
          "Author": "Author", "Date": "Date", "Source Code": "SourceCode"}
class _Estilos:
    def __getitem__(self, k): return _por_id[_alias.get(k, k)]
    def __iter__(self): return iter(_por_id.values())
st = _Estilos()
def fuente(estilo, tam, negrita=False, cursiva=False):
    s = st[estilo]
    s.font.name = "Calibri"
    s.font.size = Pt(tam)
    s.font.bold = negrita
    s.font.italic = cursiva
    s.font.color.rgb = RGBColor(0, 0, 0)
    rpr = s.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), "Calibri")
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        rf.attrib.pop(qn(a), None)
for e in ("Normal", "Body Text", "First Paragraph", "Compact"):
    if _alias.get(e) in _por_id:
        fuente(e, 11)
        st[e].paragraph_format.space_after = Pt(6)
        st[e].paragraph_format.line_spacing = 1.15
fuente("Heading 1", 13, True)
fuente("Heading 2", 11.5, True)
for e, antes in (("Heading 1", 18), ("Heading 2", 12)):
    pf = st[e].paragraph_format
    pf.space_before = Pt(antes); pf.space_after = Pt(6); pf.keep_with_next = True
st["Heading 1"].paragraph_format.page_break_before = True
for e in ("Title", "Subtitle", "Author", "Date"):
    if _alias.get(e) in _por_id:
        fuente(e, 12)
if "SourceCode" in _por_id:
    _por_id["SourceCode"].font.size = Pt(8.5)
d.save(ref)

# ---------------------------------------------------------------- 3. pandoc
tmp_docx = TMP / "pandoc.docx"
subprocess.run(["pandoc", str(TMP / "limpio.html"), "-f", "html", "-t", "docx", "--reference-doc", str(ref),
                "--shift-heading-level-by=-1", "--number-sections", "-o", str(tmp_docx),
                "--resource-path", str(RAIZ)], check=True)

# ---------------------------------------------------------------- 4. ajustes finales con python-docx
doc = Document(tmp_docx)
body = doc.element.body

def texto(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))

def sectpr(horizontal):
    s = OxmlElement("w:sectPr")
    pg = OxmlElement("w:pgSz")
    if horizontal:
        pg.set(qn("w:w"), "15840"); pg.set(qn("w:h"), "12240"); pg.set(qn("w:orient"), "landscape")
    else:
        pg.set(qn("w:w"), "12240"); pg.set(qn("w:h"), "15840")
    mar = OxmlElement("w:pgMar")
    for k, v in (("top", 1417), ("right", 1417), ("bottom", 1417), ("left", 1417), ("header", 709), ("footer", 709), ("gutter", 0)):
        mar.set(qn(f"w:{k}"), str(v))
    if horizontal:
        for k in ("top", "bottom"): mar.set(qn(f"w:{k}"), "1134")
    s.append(pg); s.append(mar)
    return s

def fijar_seccion(p, horizontal):
    ppr = p.find(qn("w:pPr"))
    if ppr is None:
        ppr = OxmlElement("w:pPr"); p.insert(0, ppr)
    for r in list(p):
        if r.tag != qn("w:pPr"):
            p.remove(r)
    ppr.append(sectpr(horizontal))

parrafos = list(body.iter(qn("w:p")))
en_portada = False
for p in parrafos:
    t = texto(p)
    if t == "[[PORTADA_INICIO]]":
        en_portada = True; body.remove(p); continue
    if t == "[[PORTADA_FIN]]":
        en_portada = False
        for r in list(p):
            if r.tag != qn("w:pPr"): p.remove(r)
        r = OxmlElement("w:r"); br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br); p.append(r)
        continue
    if en_portada:
        ppr = p.find(qn("w:pPr"))
        if ppr is None:
            ppr = OxmlElement("w:pPr"); p.insert(0, ppr)
        for viejo in ppr.findall(qn("w:jc")) + ppr.findall(qn("w:spacing")):
            ppr.remove(viejo)
        sp = OxmlElement("w:spacing")
        grande = t.startswith("Diseño de la arquitectura")
        sp.set(qn("w:before"), "1400" if grande or t.startswith("Juan Pablo") or t.startswith("8 de") or t.startswith("Video") else "0")
        sp.set(qn("w:after"), "1400" if grande else "60")
        ppr.append(sp)
        jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center"); ppr.append(jc)
        for rr in p.iter(qn("w:r")):
            rpr = rr.find(qn("w:rPr"))
            if rpr is None: rpr = OxmlElement("w:rPr"); rr.insert(0, rpr)
            if grande: rpr.insert(0, OxmlElement("w:b"))
            sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "28" if grande else "24"); rpr.append(sz)
        continue
    if t == "[[INDICE]]":
        for r in list(p):
            if r.tag != qn("w:pPr"): p.remove(r)
        tit = copy.deepcopy(p)
        r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr"); rpr.append(OxmlElement("w:b")); sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "26"); rpr.append(sz)
        r.append(rpr); tt = OxmlElement("w:t"); tt.text = "Contenido"; r.append(tt); tit.append(r)
        p.addprevious(tit)
        def fld(tipo, txt=None):
            r = OxmlElement("w:r")
            if tipo == "instr":
                e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt
            elif tipo == "text":
                e = OxmlElement("w:t"); e.text = txt
            else:
                e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tipo)
            r.append(e); return r
        for x in (fld("begin"), fld("instr", 'TOC \\o "1-2" \\h \\z \\u'), fld("separate"),
                  fld("text", "Haga clic derecho aquí y elija «Actualizar campos» para ver el índice."), fld("end")):
            p.append(x)
        r = OxmlElement("w:r"); br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br)
        p.append(r)
        continue
    if t == "[[H_INICIO]]":
        fijar_seccion(p, horizontal=False); continue
    if t == "[[H_FIN]]":
        fijar_seccion(p, horizontal=True); continue
    if t == "[[CAPTURAS]]":
        body.remove(p); continue

# el primer título después de una sección horizontal no necesita salto de página adicional: se deja como está
# márgenes de la última sección (vertical)
final = body.find(qn("w:sectPr"))
for hijo in list(final):
    if hijo.tag in (qn("w:pgSz"), qn("w:pgMar")):
        final.remove(hijo)
_nuevo = sectpr(False)
for hijo in list(_nuevo):
    final.append(hijo)

# tablas: bordes simples, encabezado gris, letra 9.5
def bordes(tbl):
    tblpr = tbl.find(qn("w:tblPr"))
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{lado}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "000000"); b.append(e)
    old = tblpr.find(qn("w:tblBorders"))
    if old is not None: tblpr.remove(old)
    despues = [qn("w:shd"), qn("w:tblLayout"), qn("w:tblCellMar"), qn("w:tblLook"), qn("w:tblCaption"), qn("w:tblDescription")]
    ancla = next((h for h in tblpr if h.tag in despues), None)
    if ancla is not None: ancla.addprevious(b)
    else: tblpr.append(b)
def ancho_total(tbl):
    tblpr = tbl.find(qn("w:tblPr"))
    w = tblpr.find(qn("w:tblW"))
    if w is None:
        w = OxmlElement("w:tblW"); tblpr.append(w)
    w.set(qn("w:type"), "pct"); w.set(qn("w:w"), "5000")
    lay = tblpr.find(qn("w:tblLayout"))
    if lay is not None: tblpr.remove(lay)

def anchos_columnas(tbl):
    filas = tbl.rows
    ncol = len(tbl.columns)
    largo = [0] * ncol
    for f in filas:
        for j, c in enumerate(f.cells[:ncol]):
            largo[j] = max(largo[j], min(len(c.text), 160))
    pesos = [max(6, l) ** 0.75 for l in largo]
    total_tw = 9406 if not tbl._tbl.xpath("ancestor::w:body") else 9406
    suma = sum(pesos)
    tw = [int(total_tw * p / suma) for p in pesos]
    grid = tbl._tbl.find(qn("w:tblGrid"))
    if grid is not None:
        for g, v in zip(grid.findall(qn("w:gridCol")), tw):
            g.set(qn("w:w"), str(v))
    for f in filas:
        for j, c in enumerate(f.cells[:ncol]):
            tcpr = c._tc.get_or_add_tcPr()
            tcw = tcpr.find(qn("w:tcW"))
            if tcw is None:
                tcw = OxmlElement("w:tcW"); tcpr.insert(0, tcw)
            tcw.set(qn("w:type"), "dxa"); tcw.set(qn("w:w"), str(tw[j]))

for tbl in doc.tables:
    ancho_total(tbl._tbl)
    es_capturas = any(c._tc.findall(".//" + qn("w:drawing")) for c in tbl.rows[0].cells)
    if es_capturas:
        continue
    anchos_columnas(tbl)
    bordes(tbl._tbl)
    for i, fila in enumerate(tbl.rows):
        for c in fila.cells:
            for par in c.paragraphs:
                par.paragraph_format.space_after = Pt(0)
                for run in par.runs:
                    run.font.size = Pt(9.5)
                    if i == 0: run.font.bold = True
            if i == 0:
                tcpr = c._tc.get_or_add_tcPr()
                sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), "E7E6E6"); tcpr.append(sh)

# encabezado con número de página a la derecha (todas las secciones heredan del primero)
sec0 = doc.sections[0]
hp = sec0.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = hp.add_run()
for tipo, txt in (("begin", None), ("instr", "PAGE"), ("end", None)):
    if tipo == "instr":
        e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt
    else:
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tipo)
    r._r.append(e)

# que Word actualice el índice al abrir
settings = doc.settings.element
uf = OxmlElement("w:updateFields"); uf.set(qn("w:val"), "true")
_despues = [qn(f"w:{x}") for x in ("hdrShapeDefaults", "footnotePr", "endnotePr", "compat", "docVars", "rsids", "attachedSchema", "themeFontLang", "clrSchemeMapping", "doNotIncludeSubdocsInStats", "decimalSymbol", "listSeparator")] + ["{http://schemas.openxmlformats.org/officeDocument/2006/math}mathPr"]
_ancla = next((h for h in settings if h.tag in _despues), None)
if _ancla is not None: _ancla.addprevious(uf)
else: settings.append(uf)

# idioma español (Colombia)
for s in ("Normal",):
    rpr = doc.styles[s].element.get_or_add_rPr()
    lang = OxmlElement("w:lang"); lang.set(qn("w:val"), "es-CO"); rpr.append(lang)

doc.core_properties.author = "Juan Pablo Vargas Sánchez"
doc.core_properties.title = "Diseño de la arquitectura de un sistema de gestión académica mediante Google AI Studio"
doc.core_properties.language = "es-CO"
doc.save(SALIDA)
print("docx:", SALIDA)

# ---------------------------------------------------------------- 5. normalizar el XML según el esquema de Word
import zipfile
from lxml import etree
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
ORDEN = {
    "pPr": "pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr suppressLineNumbers pBdr shd tabs suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi adjustRightInd snapToGrid spacing ind contextualSpacing mirrorIndents suppressOverlap jc textDirection textAlignment textboxTightWrap outlineLvl divId cnfStyle rPr sectPr pPrChange",
    "rPr": "rStyle rFonts b bCs i iCs caps smallCaps strike dstrike outline shadow emboss imprint noProof snapToGrid vanish webHidden color spacing w kern position sz szCs highlight u effect bdr shd fitText vertAlign rtl cs em lang eastAsianLayout specVanish oMath",
    "tblPr": "tblStyle tblpPr tblOverlap bidiVisual tblStyleRowBandSize tblStyleColBandSize tblW jc tblCellSpacing tblInd tblBorders shd tblLayout tblCellMar tblLook tblCaption tblDescription",
    "tcPr": "cnfStyle tcW gridSpan hMerge vMerge tcBorders shd noWrap tcMar textDirection tcFitText vAlign hideMark",
    "style": "name aliases basedOn next link autoRedefine hidden uiPriority semiHidden unhideWhenUsed qFormat locked personal personalCompose personalReply rsid pPr rPr tblPr trPr tcPr tblStylePr",
    "settings": "writeProtection view zoom removePersonalInformation removeDateAndTime doNotDisplayPageBoundaries displayBackgroundShape printPostScriptOverText printFractionalCharacterWidth printFormsData embedTrueTypeFonts embedSystemFonts saveSubsetFonts saveFormsData mirrorMargins alignBordersAndEdges bordersDoNotSurroundHeader bordersDoNotSurroundFooter gutterAtTop hideSpellingErrors hideGrammaticalErrors activeWritingStyle proofState formsDesign attachedTemplate linkStyles stylePaneFormatFilter stylePaneSortMethod documentType mailMerge revisionView trackRevisions doNotTrackMoves doNotTrackFormatting documentProtection autoFormatOverride styleLockTheme styleLockQFSet defaultTabStop autoHyphenation consecutiveHyphenLimit hyphenationZone doNotHyphenateCaps showEnvelope summaryLength clickAndTypeStyle defaultTableStyle evenAndOddHeaders bookFoldRevPrinting bookFoldPrinting bookFoldPrintingSheets drawingGridHorizontalSpacing drawingGridVerticalSpacing displayHorizontalDrawingGridEvery displayVerticalDrawingGridEvery doNotUseMarginsForDrawingGridOrigin drawingGridHorizontalOrigin drawingGridVerticalOrigin doNotShadeFormData noPunctuationKerning characterSpacingControl printTwoOnOne strictFirstAndLastChars noLineBreaksAfter noLineBreaksBefore savePreviewPicture doNotValidateAgainstSchema saveInvalidXml ignoreMixedContent alwaysShowPlaceholderText doNotDemarcateInvalidXml saveXmlDataOnly useXSLTWhenSaving saveThroughXslt showXMLTags alwaysMergeEmptyNamespace updateFields hdrShapeDefaults footnotePr endnotePr compat docVars rsids mathPr attachedSchema themeFontLang clrSchemeMapping doNotIncludeSubdocsInStats doNotAutoCompressPictures forceUpgrade captions readModeInkLockDown smartTagType schemaLibrary shapeDefaults doNotEmbedSmartTags decimalSymbol listSeparator",
}
ORDEN = {k: {n: i for i, n in enumerate(v.split())} for k, v in ORDEN.items()}

def reordenar(raiz):
    for el in raiz.iter():
        if not isinstance(el.tag, str):
            continue
        nombre = etree.QName(el).localname
        if nombre in ORDEN and len(el):
            tabla = ORDEN[nombre]
            hijos = list(el)
            hijos.sort(key=lambda h: tabla.get(etree.QName(h).localname, len(tabla)) if isinstance(h.tag, str) else len(tabla))
            for h in hijos:
                el.remove(h)
            for h in hijos:
                el.append(h)
        if nombre == "rPr":
            el.text = None
            for h in el:
                h.tail = None
        if nombre == "nsid":
            v = el.get(W + "val")
            if v and len(v) < 8:
                el.set(W + "val", v.zfill(8))

tmp_final = SALIDA.with_suffix(".tmp.docx")
with zipfile.ZipFile(SALIDA) as zin, zipfile.ZipFile(tmp_final, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        if item.filename.endswith("/"):
            continue
        datos = zin.read(item.filename)
        if item.filename in ("word/document.xml", "word/styles.xml", "word/settings.xml", "word/numbering.xml") or item.filename.startswith("word/header"):
            raiz = etree.fromstring(datos)
            reordenar(raiz)
            datos = etree.tostring(raiz, xml_declaration=True, encoding="UTF-8", standalone=True)
        zout.writestr(item, datos)
tmp_final.replace(SALIDA)
print("XML normalizado")
