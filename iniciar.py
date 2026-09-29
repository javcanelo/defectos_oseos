import json
from pathlib import Path

destino = Path("data/muestras.json")
if destino.exists():
    raise SystemExit("Ya hay datos. No se reemplazaron.")

# ID, recepción, revisión SA, pendiente, estándar ya terminado.
filas = [
    ("1082288", "2026-08-21", "2026-08-28", "archivar", True),
    ("4874", "2026-08-28", "2026-09-02", "corte_estandar", False),
    ("1082292", "2026-08-28", "2026-09-02", "corte_estrella", True),
    ("1082297", "2026-08-28", "2026-09-02", "corte_estandar", False),
    ("909700", "2026-08-28", "2026-09-02", "desgaste", False),
    ("82293", "2026-08-28", "2026-09-02", "corte_estandar", False),
    ("1082?3801", "2026-09-02", "2026-09-25", "corte_estrella", False),
    ("1082301", "2026-09-02", "2026-09-25", "corte_estrella", False),
    ("1082", "2026-09-02", "2026-09-25", "corte_estrella", False),
    ("1062219", "2026-09-02", "2026-09-25", "corte_estrella", False),
    ("182281", "2026-09-02", "2026-09-25", "he_corazon", False),
    ("217", "2026-09-02", "2026-09-25", "desgaste", False),
    ("22", "2026-09-02", "2026-09-25", "corte_corazon", False),
    ("10880", "2026-09-02", "2026-09-25", "desgaste", False),
    ("1082291", "2026-09-25", None, "reincluir", False),
    ("082104", "2026-09-25", None, "reincluir", False),
    ("1082314", "2026-09-25", None, "reincluir", False),
    ("721093", "2026-09-25", None, "reincluir", False),
    ("1082113", "2026-09-25", None, "reincluir", False),
    ("1082101", "2026-09-25", None, "reincluir", False),
]

notas = {
    "1082292": "Bloque casi agotado. Corte estrella indicado; fecha de esa indicación no confirmada.",
    "1082?3801": "Confirmar identificador.",
    "909700": "Indicación SA: desgaste de 200 µm.",
    "217": "Indicación SA: desgaste de 200 µm.",
    "10880": "Indicación SA: desgaste de 200 µm.",
    "182281": "Pendiente HE corazón. El corte corazón previo no está documentado explícitamente.",
}

muestras = {}

for ident, recepcion, revision, pendiente, terminado in filas:
    historial = [{"accion": "Recepción", "fecha": recepcion}]

    if revision:
        for accion in [
            "Reinclusión", "Desgaste", "Reinclusión", "Desgaste",
            "Corte de evaluación", "Tinción HE de evaluación",
        ]:
            historial.append({"accion": accion, "fecha": None})

        historial.append({"accion": "Revisión SA", "fecha": revision})

    if terminado:
        historial.extend([
            {"accion": "Corte estándar", "fecha": None},
            {"accion": "Tinción HE estándar 1, 8, 15", "fecha": None},
        ])

    historial.append({
        "accion": "Plan inicial importado",
        "fecha": revision if ident != "1082292" else None,
        "detalle": pendiente,
    })

    muestras[ident] = {
        "pendiente": pendiente,
        "prioridad": ident == "1082314",
        "desgaste_obligatorio": revision is None,
        "bloque": "En laboratorio",
        "placas": "Sin confirmar" if revision else "No hay placas en laboratorio",
        "nota": notas.get(ident, ""),
        "historial": historial,
    }

destino.parent.mkdir(exist_ok=True)
destino.write_text(
    json.dumps(muestras, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("Cargadas 20 muestras.")