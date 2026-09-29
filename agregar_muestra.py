import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from flujo import ETAPAS

BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "data" / "muestras.json"
ZONA = ZoneInfo("America/Santiago")


def elegir(pregunta, opciones, defecto=0):
    print(f"\n{pregunta}")
    for i, opcion in enumerate(opciones, 1):
        marca = " [predeterminado]" if i - 1 == defecto else ""
        print(f"  {i}. {opcion}{marca}")

    while True:
        respuesta = input("Número o Enter: ").strip()
        if not respuesta:
            return defecto
        if respuesta.isdigit() and 1 <= int(respuesta) <= len(opciones):
            return int(respuesta) - 1
        print("Elige uno de los números mostrados.")


def preguntar_fecha():
    hoy = datetime.now(ZONA).date()

    while True:
        texto = input(
            f"\nFecha de recepción [Enter: {hoy:%d/%m/%Y}; "
            "?: desconocida]: "
        ).strip()

        if not texto:
            return hoy.isoformat()
        if texto == "?":
            return None

        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(texto, formato).date().isoformat()
            except ValueError:
                pass

        print("Usa DD/MM/AAAA o AAAA-MM-DD.")


def guardar(datos):
    # Escribe primero un temporal y después sustituye el archivo.
    descriptor, nombre = tempfile.mkstemp(
        dir=ARCHIVO.parent, suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
            archivo.write("\n")
        os.replace(nombre, ARCHIVO)
    finally:
        if os.path.exists(nombre):
            os.unlink(nombre)


def agregar():
    if not ARCHIVO.exists():
        raise SystemExit(
            "No encuentro data/muestras.json. "
            "Este script requiere el proyecto ya inicializado."
        )

    datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))

    print("\n=== AGREGAR MUESTRA ===")
    ident = input("ID de muestra, conservando ceros iniciales: ").strip()

    if not ident:
        print("Cancelado: falta el ID.")
        return

    if ident in datos:
        print(f"La muestra {ident} ya existe. No se modificó.")
        return

    recepcion = preguntar_fecha()

    etapas = [clave for clave in ETAPAS if clave != "elegir"]
    posicion = elegir(
        "¿Qué tiene pendiente ahora?",
        [ETAPAS[clave][0] for clave in etapas],
        defecto=etapas.index("reincluir"),
    )
    pendiente = etapas[posicion]

    desgaste_obligatorio = False
    if pendiente == "reincluir":
        desgaste_obligatorio = elegir(
            "Después de reincluir, ¿debe pasar obligatoriamente por desgaste?",
            ["Sí", "No: permitir desgaste o corte directo"],
        ) == 0

    prioridad = elegir("¿Es prioritaria?", ["No", "Sí"]) == 1

    opciones_bloque = [
        "En laboratorio",
        "Fuera del laboratorio",
        "Sin confirmar",
    ]
    bloque = opciones_bloque[elegir(
        "¿Dónde está el bloque?", opciones_bloque
    )]

    opciones_placas = [
        "No hay placas en laboratorio",
        "Hay placas en laboratorio",
        "Sin confirmar",
    ]
    placas = opciones_placas[elegir(
        "¿Hay placas de esta muestra en el laboratorio?", opciones_placas
    )]

    nota = input("\nObservación [opcional]: ").strip()
    ahora = datetime.now(ZONA).isoformat()

    historial = []
    if recepcion:
        historial.append({
            "accion": "Recepción",
            "fecha": recepcion,
        })

    historial.append({
        "accion": "Alta manual de muestra",
        "fecha": None,
        "registrado": ahora,
        "detalle": (
            f"Pendiente inicial: {ETAPAS[pendiente][0]}. "
            "No se presuponen realizadas las etapas anteriores."
        ),
    })

    muestra = {
        "pendiente": pendiente,
        "prioridad": prioridad,
        "desgaste_obligatorio": desgaste_obligatorio,
        "bloque": bloque,
        "placas": placas,
        "nota": nota,
        "historial": historial,
    }

    print(f"\nMuestra: {ident}")
    print(f"Recepción: {recepcion or 'Desconocida'}")
    print(f"Pendiente: {ETAPAS[pendiente][0]}")
    print(f"Prioridad: {'Sí' if prioridad else 'No'}")
    print(f"Bloque: {bloque}")
    print(f"Placas: {placas}")
    print(f"Observación: {nota or '—'}")

    if input("\n¿Guardar? [s/N]: ").strip().lower() not in ("s", "si", "sí"):
        print("Cancelado. No se guardaron cambios.")
        return

    datos[ident] = muestra
    guardar(datos)
    print(f"\n✓ Muestra {ident} guardada.")


if __name__ == "__main__":
    try:
        while True:
            agregar()
            otra = input("\n¿Agregar otra muestra? [s/N]: ").strip().lower()
            if otra not in ("s", "si", "sí"):
                break
    except (KeyboardInterrupt, EOFError):
        print("\nEntrada cancelada.")