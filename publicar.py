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
FORMULARIO = ""

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
body{font:16px system-ui;max-width:1050px;margin:32px auto;padding:0 20px;
background:#f5f7f8;color:#25343b}
article{background:white;padding:20px;border:1px solid #dde3e6;
border-radius:12px;margin:16px 0}
h2{margin-top:0}input,select{font:inherit;padding:10px;max-width:95%}
summary{cursor:pointer}li{margin:8px 0}
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
TARJETAS
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