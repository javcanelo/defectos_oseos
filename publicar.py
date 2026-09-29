import csv
import html
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from flujo import titulo, avance

datos = json.loads(
    Path("data/muestras.json").read_text(encoding="utf-8")
)
salida = Path("docs")
salida.mkdir(exist_ok=True)

# Pega aquí el enlace de respuesta del formulario cuando lo crees.
FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSeoyFcBhHTaBb1uFyI7mweF1ukKjRBWFNC8a-HPCEJCb9bBPg/viewform"

ahora = datetime.now(ZoneInfo("America/Santiago")).isoformat(
    timespec="minutes"
)
esc = lambda x: html.escape(str(x))
tarjetas = []
filas = []

for ident, m in sorted(
    datos.items(), key=lambda par: (not par[1]["prioridad"], par[0])
):
    archivada = m["pendiente"] == "archivada"
    historia = "".join(
        "<li>" + esc(e.get("fecha") or "Fecha desconocida")
        + " — " + esc(e["accion"])
        + ": " + esc(e.get("detalle", "")) + "</li>"
        for e in m["historial"]
    )

    tarjetas.append(f"""
    <article data-archivada="{str(archivada).lower()}">
      <h2>{'★ ' if m['prioridad'] else ''}{esc(ident)}</h2>
      <p><strong>{esc(titulo(m['pendiente']))}</strong></p>
      <p>{esc(avance(m))}</p>
      <p>{esc(m['nota'])}</p>
      <p>Bloque: {esc(m['bloque'])}<br>Placas: {esc(m['placas'])}</p>
      <details><summary>Historial</summary><ol>{historia}</ol></details>
    </article>
    """)

    filas.append([
        "ID " + ident, titulo(m["pendiente"]),
        m["bloque"], m["placas"], m["prioridad"], m["nota"], ahora,
    ])

enlace = (
    f'<p><a href="{esc(FORMULARIO)}">Enviar consulta u observación</a></p>'
    if FORMULARIO else ""
)

pagina = """<!doctype html><html lang="es"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Seguimiento histológico</title>
<style>
* {
  box-sizing: border-box;
}

body {
  font: 16px system-ui, sans-serif;
  max-width: 1440px;
  margin: 32px auto;
  padding: 0 24px;
  background: #f3f6f8;
  color: #25343b;
}

h1 {
  margin-bottom: 8px;
}

input, select {
  font: inherit;
  padding: 12px;
  margin: 0 8px 12px 0;
  max-width: 100%;
  border: 1px solid #ccd6dc;
  border-radius: 8px;
  background: white;
}

.tablero {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 12px;
  align-items: start;
}

article {
  min-width: 0;
  background: white;
  padding: 22px;
  border: 1px solid #dde5e9;
  border-top: 4px solid #287c76;
  border-radius: 12px;
  box-shadow: 0 3px 12px #25343b08;
  overflow-wrap: anywhere;
}

article[hidden] {
  display: none;
}

article[data-archivada="true"] {
  border-top-color: #98a5ad;
}

h2 {
  margin: 0 0 14px;
  font-size: 23px;
}

p {
  line-height: 1.5;
}

a {
  color: #176c66;
}

summary {
  cursor: pointer;
  color: #176c66;
  font-weight: 600;
}

details {
  border-top: 1px solid #edf0f2;
  padding-top: 14px;
  margin-top: 18px;
}

ol {
  padding-left: 20px;
}

li {
  margin: 10px 0;
  font-size: 14px;
  line-height: 1.5;
}

@media (max-width: 1000px) {
  .tablero {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  body {
    padding: 0 14px;
  }

  .tablero {
    grid-template-columns: 1fr;
  }
}
</style>
<h1>Seguimiento histológico</h1>
<p>Vista de consulta. Última publicación: FECHA</p>
FORMULARIO
<input id="buscar" placeholder="Buscar muestra" oninput="filtrar()">
<select id="vista" onchange="filtrar()">
<option value="false">Pendientes</option>
<option value="true">Archivadas</option>
<option value="todas">Todas</option>
</select>
<main class="tablero">
TARJETAS
</main>
<script>
function filtrar(){
 const q=document.getElementById('buscar').value.toLowerCase();
 const v=document.getElementById('vista').value;
 document.querySelectorAll('article').forEach(a=>{
  a.hidden=!(a.textContent.toLowerCase().includes(q)
    &&(v==='todas'||a.dataset.archivada===v));
 });
}
filtrar();
</script></html>"""

pagina = pagina.replace("FECHA", esc(ahora))
pagina = pagina.replace("FORMULARIO", enlace)
pagina = pagina.replace("TARJETAS", "".join(tarjetas))
(salida / "index.html").write_text(pagina, encoding="utf-8")
(salida / ".nojekyll").touch()

with (salida / "resumen.csv").open(
    "w", encoding="utf-8", newline=""
) as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow([
        "Muestra", "Pendiente", "Bloque", "Placas",
        "Prioridad", "Observación", "Publicado",
    ])
    escritor.writerows(filas)

print("Página y resumen generados en docs/.")