// Guarda el HTML del informe sencillo ya procesado por el navegador (con títulos de tabla).
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto("file://" + path.join(__dirname, "informe_v2.html"), { waitUntil: "networkidle" });
  fs.mkdirSync(path.join(__dirname, ".docx_tmp"), { recursive: true });
  fs.writeFileSync(path.join(__dirname, ".docx_tmp", "dom.html"), "<!doctype html>" + (await p.evaluate(() => document.documentElement.outerHTML)));
  await b.close();
})();
