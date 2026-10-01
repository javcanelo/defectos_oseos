import csv
import html
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import unicodedata
from flujo import titulo, avance, ETAPAS

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

COLORES = {
    "reincluir":       ("#f3e8ff", "#6b21a8"),
    "elegir":          ("#ede9fe", "#5b21b6"),
    "desgaste":        ("#ffedd5", "#9a3412"),
    "corte_eval":      ("#dbeafe", "#1e40af"),
    "he_eval":         ("#fce7f3", "#9d174d"),
    "revision":        ("#fef3c7", "#92400e"),
    "corte_estandar":  ("#cffafe", "#155e75"),
    "he_estandar":     ("#ffe4e6", "#9f1239"),
    "corte_estrella":  ("#e0e7ff", "#3730a3"),
    "he_estrella":     ("#fae8ff", "#86198f"),
    "corte_corazon":   ("#ccfbf1", "#115e59"),
    "he_corazon":      ("#fee2e2", "#991b1b"),
    "archivar":        ("#dcfce7", "#166534"),
    "archivada":       ("#edf0f2", "#52616b"),
}

ORDEN_ETAPAS = {
    "reincluir": 1,
    "elegir": 2,
    "desgaste": 2,
    "corte_eval": 3,
    "he_eval": 4,
    "revision": 5,
    "corte_estandar": 6,
    "corte_estrella": 6,
    "corte_corazon": 6,
    "he_estandar": 7,
    "he_estrella": 7,
    "he_corazon": 7,
    "archivar": 8,
    "archivada": 9,
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    return "".join(
        c for c in texto if not unicodedata.combining(c)
    ).casefold().strip()


# Acciones reales conocidas, incluyendo los nombres de la carga inicial.
ACCIONES_TRABAJO = {
    normalizar(nombre)
    for clave, (nombre, _) in ETAPAS.items()
    if clave not in ("elegir", "archivada")
}

ACCIONES_TRABAJO.update(normalizar(nombre) for nombre in [
    "Recepción",
    "Reinclusión",
    "Desgaste",
    "Corte de evaluación",
    "Tinción HE de evaluación",
    "Revisión SA",
    "Evaluación SA",
    "Corte estándar",
    "Corte estrella",
    "Corte corazón",
    "Tinción HE estándar 1, 8, 15",
    "Derretido y evaluación",
])


def ultimo_trabajo(muestra):
    # Usa el último trabajo registrado, aunque no tenga fecha.
    # No sustituye la fecha realizada por la fecha de ingreso al sistema.
    for evento in reversed(muestra.get("historial", [])):
        accion = evento.get("accion", "")
        if normalizar(accion) not in ACCIONES_TRABAJO:
            continue

        fecha = evento.get("fecha")
        if not fecha:
            fecha_visible = "Fecha desconocida"
        else:
            try:
                fecha_visible = datetime.fromisoformat(
                    str(fecha).replace("Z", "+00:00")
                ).strftime("%d/%m/%Y")
            except ValueError:
                fecha_visible = str(fecha)

        # La aplicación registra la revisión completada con este título.
        if normalizar(accion) == normalizar("Esperar revisión SA"):
            accion = "Revisión SA"

        return accion, fecha_visible

    return "Sin trabajo documentado", "Fecha desconocida"


opciones_etapas = "".join(
    f'<option value="{esc(clave)}">{esc(titulo(clave))}</option>'
    for clave in sorted(
        ETAPAS,
        key=lambda clave: (ORDEN_ETAPAS[clave], titulo(clave))
    )
)

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
    
    fondo, tinta = COLORES.get(
        m["pendiente"], ("#edf0f2", "#52616b")
    )
    secuencia = avance(m).split(" → ", 1)
    despues = (
        "Después: " + secuencia[1]
        if len(secuencia) > 1
        else "Sin siguiente paso automático."
    )
    
    ultima_accion, ultima_fecha = ultimo_trabajo(m)
    requiere_sa = m["pendiente"] == "revision"
    aviso_sa = (
        '<p class="aviso-sa">Requiere revisión SA · Acercarse a revisar</p>'
        if requiere_sa else ""
    )

    tarjetas.append(f"""
    <article
        data-id="{esc(ident)}"
        data-etapa="{esc(m['pendiente'])}"
        data-rango="{ORDEN_ETAPAS[m['pendiente']]}"
        data-prioridad="{int(bool(m['prioridad']))}"
        data-sa="{int(requiere_sa)}"
        data-archivada="{str(archivada).lower()}"
    >
        {aviso_sa}
    <header class="cabecera-muestra">
    <h2>{'★ ' if m['prioridad'] else ''}{esc(ident)}</h2>
    <span
        class="accion-pendiente"
        style="--fondo: {fondo}; --tinta: {tinta};"
        tabindex="0"
        aria-label="{esc(titulo(m['pendiente']))}. {esc(despues)}"
    >
        {esc(titulo(m['pendiente']))}
        <span class="ayuda-accion">{esc(despues)}</span>
    </span>
    </header>

    <div class="ultimo-trabajo">
        <span class="ultimo-titulo">Último trabajo registrado</span>
        <strong>{esc(ultima_accion)}</strong>
        <span class="ultima-fecha">{esc(ultima_fecha)}</span>
    </div>

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
.cabecera-muestra {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.cabecera-muestra h2 {
  margin: 0;
  font-size: 24px;
}

.accion-pendiente {
  position: relative;
  display: inline-block;
  max-width: 100%;
  padding: 10px 14px;
  border-radius: 10px;
  background: var(--fondo, #edf0f2);
  color: var(--tinta, #52616b);
  border: 1px solid currentColor;
  font-size: 18px;
  font-weight: 750;
  line-height: 1.3;
  cursor: help;
}

.ayuda-accion {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 20;
  width: 260px;
  max-width: 100%;
  padding: 12px;
  border-radius: 8px;
  background: #24343d;
  color: white;
  box-shadow: 0 6px 20px #00000026;
  font-size: 14px;
  font-weight: 400;
  line-height: 1.5;
}

.accion-pendiente:hover .ayuda-accion,
.accion-pendiente:focus .ayuda-accion {
  display: block;
}

.accion-pendiente:focus-visible {
  outline: 3px solid #25343b;
  outline-offset: 3px;
}

.filtros {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 12px;
  margin: 24px 0 12px;
}

.filtros label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  max-width: 100%;
  color: #52616b;
  font-size: 14px;
  font-weight: 600;
}

.filtros input,
.filtros select {
  margin: 0;
}

.ultimo-trabajo {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin: 16px 0;
  padding: 14px;
  border-radius: 8px;
  background: #f3f6f8;
}

.ultimo-titulo {
  color: #647580;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.ultimo-trabajo strong {
  font-size: 15px;
}

.ultima-fecha {
  color: #52616b;
  font-size: 14px;
}

article[data-sa="1"] {
  border: 2px solid #d49a22;
  border-top: 6px solid #d49a22;
  background: #fffdf5;
}

.aviso-sa {
  margin: 0 0 16px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #fff0bc;
  color: #704400;
  font-size: 14px;
  font-weight: 750;
}

.resultados {
  color: #52616b;
  font-size: 14px;
}

</style>
<h1>Seguimiento histológico</h1>
<p>Vista de consulta. Última publicación: FECHA</p>
FORMULARIO
<div class="filtros">
  <label>
    Buscar
    <input id="buscar" placeholder="ID o texto" oninput="filtrar()">
  </label>

  <label>
    Estado
    <select id="vista" onchange="filtrar()">
      <option value="false">Pendientes</option>
      <option value="true">Archivadas</option>
      <option value="todas">Todas</option>
    </select>
  </label>

  <label>
    Etapa
    <select id="etapa" onchange="filtrar()">
      <option value="todas">Todas las etapas</option>
      OPCIONES_ETAPAS
    </select>
  </label>

  <label>
    Orden por avance
    <select id="orden" onchange="filtrar()">
      <option value="desc">Más avanzadas primero</option>
      <option value="asc">Etapas iniciales primero</option>
    </select>
  </label>
</div>

<p class="resultados">
  Las muestras pendientes de revisión SA aparecen primero
  entre los resultados filtrados.
</p>
<p id="conteo" class="resultados" aria-live="polite"></p>

<main class="tablero">
TARJETAS
</main>
<script>
function normalizar(texto) {
  return texto.normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function filtrar() {
  const consulta = normalizar(
    document.getElementById("buscar").value.trim()
  );
  const vista = document.getElementById("vista").value;
  const etapa = document.getElementById("etapa").value;
  const direccion =
    document.getElementById("orden").value === "asc" ? 1 : -1;

  const tablero = document.querySelector(".tablero");
  const tarjetas = Array.from(tablero.querySelectorAll("article"));

  tarjetas.sort((a, b) => {
    // SA siempre primero, independientemente del sentido del orden.
    const diferenciaSA = Number(b.dataset.sa) - Number(a.dataset.sa);
    if (diferenciaSA) return diferenciaSA;

    const diferenciaEtapa =
      Number(a.dataset.rango) - Number(b.dataset.rango);
    if (diferenciaEtapa) return direccion * diferenciaEtapa;

    // Dentro de la misma etapa, mantener la prioridad manual.
    const diferenciaPrioridad =
      Number(b.dataset.prioridad) - Number(a.dataset.prioridad);
    if (diferenciaPrioridad) return diferenciaPrioridad;

    return a.dataset.id.localeCompare(
      b.dataset.id, "es", {numeric: true}
    );
  });

  let visibles = 0;
  let revisiones = 0;

  tarjetas.forEach(tarjeta => {
    const coincideTexto =
      normalizar(tarjeta.textContent).includes(consulta);
    const coincideEstado =
      vista === "todas" || tarjeta.dataset.archivada === vista;
    const coincideEtapa =
      etapa === "todas" || tarjeta.dataset.etapa === etapa;

    tarjeta.hidden = !(
      coincideTexto && coincideEstado && coincideEtapa
    );

    if (!tarjeta.hidden) {
      visibles++;
      if (tarjeta.dataset.sa === "1") revisiones++;
    }

    tablero.appendChild(tarjeta);
  });

  document.getElementById("conteo").textContent =
    visibles === 0
      ? "No hay muestras que coincidan con estos filtros."
      : `${visibles} muestras visibles · ${revisiones} requieren revisión SA`;
}

filtrar();
</script></html>"""

pagina = pagina.replace("FECHA", esc(ahora))
pagina = pagina.replace("FORMULARIO", enlace)
pagina = pagina.replace("OPCIONES_ETAPAS", opciones_etapas)
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