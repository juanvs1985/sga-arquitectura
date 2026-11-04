// Imprime informe.html a PDF en dos pasadas: la primera ubica la página de cada título,
// la segunda escribe esos números en el índice.  Uso: node informe/imprimir.js
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const dir = __dirname;
const html = "file://" + path.join(dir, "informe.html");
const salida = path.join(dir, "Informe_Arquitectura_SGA_Juan_Pablo_Vargas.pdf");
const tmp = path.join(dir, ".pasada1.pdf");

const opciones = {
  format: "Letter", printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
  headerTemplate: '<div style="width:100%;font-family:Carlito,Calibri,sans-serif;font-size:8.5pt;color:#5a6475;padding:0 1.6cm;display:flex;justify-content:space-between"><span>Arquitectura de un Sistema de Gestión Académica</span><span class="pageNumber"></span></div>',
  footerTemplate: "<div></div>",
};

function norm(s) { return s.normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/\s+/g, " ").trim().toLowerCase(); }

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto(html, { waitUntil: "networkidle" });
  await p.pdf({ ...opciones, path: tmp });
  const titulos = await p.evaluate(() => window.__tocTargets);
  const texto = execFileSync("pdftotext", ["-layout", tmp, "-"], { maxBuffer: 1 << 28 }).toString("utf8");
  const paginas = texto.split("\f").map(norm);
  const res = []; let desde = 2; // saltar portada e índice
  for (const t of titulos) {
    const clave = norm(t).slice(0, 38);
    let encontrada = "";
    for (let i = desde; i < paginas.length; i++) { if (paginas[i].includes(clave)) { encontrada = i + 1; desde = i; break; } }
    res.push(encontrada);
  }
  await p.evaluate(pg => window.__setPages(pg), res);
  await p.pdf({ ...opciones, path: salida });
  await b.close();
  fs.unlinkSync(tmp);
  const faltan = titulos.filter((t, i) => !res[i]);
  console.log("PDF:", salida, "| títulos sin página:", faltan.length ? faltan : "ninguno");
})();
