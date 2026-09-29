import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st
from flujo import (
    ETAPAS, DECISIONES, HE_CORAZON,
    titulo, acciones, siguiente, avance,
)

ARCHIVO = Path("data/muestras.json")
ZONA = ZoneInfo("America/Santiago")

st.set_page_config(page_title="Histología", layout="wide")
st.title("Seguimiento histológico")

datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))


def guardar(ident, accion, fecha, detalle=""):
    datos[ident]["historial"].append({
        "accion": accion,
        "fecha": fecha.isoformat() if fecha else None,
        "registrado": datetime.now(ZONA).isoformat(),
        "detalle": detalle,
    })
    temporal = ARCHIVO.with_suffix(".tmp")
    temporal.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporal.replace(ARCHIVO)
    st.rerun()


vista = st.radio(
    "Mostrar", ["Pendientes", "Archivadas", "Todas"], horizontal=True
)
busqueda = st.text_input("Buscar muestra").strip()

for ident, m in sorted(
    datos.items(), key=lambda par: (not par[1]["prioridad"], par[0])
):
    archivada = m["pendiente"] == "archivada"

    if vista == "Pendientes" and archivada:
        continue
    if vista == "Archivadas" and not archivada:
        continue
    if busqueda and busqueda not in ident:
        continue

    with st.container(border=True):
        st.subheader(("★ " if m["prioridad"] else "") + ident)
        st.write(avance(m))
        if m["nota"]:
            st.caption(m["nota"])

        etapa = m["pendiente"]

        if not archivada:
            with st.form("avance-" + ident):
                fecha = st.date_input(
                    "Fecha realizada", datetime.now(ZONA).date(),
                    key="fecha-" + ident,
                )
                desconocida = st.checkbox(
                    "Fecha desconocida", key="sinfecha-" + ident
                )

                if etapa == "revision":
                    decision = st.selectbox(
                        "Decisión de SA", list(DECISIONES),
                        key="decision-" + ident,
                    )
                    accion = "revision"
                else:
                    accion = st.selectbox(
                        "Acción realizada", acciones(m),
                        format_func=titulo, key="accion-" + ident,
                    )

                detalle = st.text_input(
                    "Detalle opcional", key="detalle-" + ident
                )

                bloqueo = accion == "he_corazon" and not HE_CORAZON
                if bloqueo:
                    st.info("Falta confirmar las placas HE del protocolo corazón.")

                hecho = st.form_submit_button(
                    "Guardar revisión" if etapa == "revision"
                    else "Marcar realizado",
                    disabled=bloqueo,
                )

                if hecho:
                    if etapa == "revision":
                        m["pendiente"] = DECISIONES[decision]
                        detalle = decision + (
                            " — " + detalle if detalle else ""
                        )
                    else:
                        m["pendiente"] = siguiente(m, accion)
                        if accion == "reincluir":
                            m["desgaste_obligatorio"] = False
                        if accion.startswith("corte_"):
                            m["placas"] = "Hay placas en laboratorio"

                    guardar(
                        ident, titulo(accion),
                        None if desconocida else fecha, detalle,
                    )

        with st.expander("Detalle, presencia y cambios de plan"):
            st.write({
                "Bloque": m["bloque"],
                "Placas": m["placas"],
            })

            with st.form("plan-" + ident):
                opciones = [
                    x for x in ETAPAS
                    if x not in ("archivada", "elegir")
                ]
                nueva = st.selectbox(
                    "Programar otra tarea / reabrir",
                    opciones, format_func=titulo,
                    key="nuevo-" + ident,
                )
                motivo = st.text_input(
                    "Motivo del cambio", key="motivo-" + ident
                )

                if st.form_submit_button("Actualizar plan"):
                    if not motivo.strip():
                        st.error("Describe brevemente el motivo.")
                    else:
                        anterior = m["pendiente"]
                        m["pendiente"] = nueva
                        guardar(
                            ident, "Cambio de plan",
                            datetime.now(ZONA).date(),
                            f"{anterior} → {nueva}. {motivo}",
                        )

            with st.form("material-" + ident):
                estados_b = [
                    "En laboratorio", "Fuera del laboratorio", "Sin confirmar"
                ]
                estados_p = [
                    "Hay placas en laboratorio",
                    "No hay placas en laboratorio",
                    "Sin confirmar",
                ]
                bloque = st.selectbox(
                    "Presencia del bloque", estados_b,
                    index=estados_b.index(m["bloque"]),
                    key="bloque-" + ident,
                )
                placas = st.selectbox(
                    "Presencia de placas", estados_p,
                    index=estados_p.index(m["placas"]),
                    key="placas-" + ident,
                )
                observacion = st.text_input(
                    "Detalle de entrega / salida / retorno",
                    key="movimiento-" + ident,
                )
                if st.form_submit_button("Guardar presencia"):
                    m["bloque"], m["placas"] = bloque, placas
                    guardar(
                        ident, "Actualización de presencia",
                        datetime.now(ZONA).date(),
                        f"Bloque: {bloque}. Placas: {placas}. {observacion}",
                    )

            st.dataframe(m["historial"], hide_index=True)