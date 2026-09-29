ETAPAS = {
    "reincluir": ("Reincluir", "elegir"),
    "desgaste": ("Desgastar", "corte_eval"),
    "corte_eval": ("Cortar HE de evaluación", "he_eval"),
    "he_eval": ("Teñir HE de evaluación", "revision"),
    "revision": ("Esperar revisión SA", None),

    "corte_estandar": ("Cortar set estándar", "he_estandar"),
    "he_estandar": ("Teñir HE estándar: 1, 8, 15", "archivar"),

    "corte_estrella": ("Cortar set estrella", "he_estrella"),
    "he_estrella": ("Teñir HE estrella: 5, 21", "archivar"),

    "corte_corazon": ("Cortar set corazón", "he_corazon"),
    "he_corazon": ("Teñir HE corazón: 5, 21, 39", "archivar"),

    "archivar": ("Archivar / cerrar trabajo", "archivada"),
    "archivada": ("Archivada", None),
    "elegir": ("Desgaste o corte directo de evaluación", None),
}

DECISIONES = {
    "Set estándar": "corte_estandar",
    "Set estrella": "corte_estrella",
    "Set corazón": "corte_corazon",
    "Profundizar desgaste": "desgaste",
    "Reincluir nuevamente": "reincluir",
    "Archivar": "archivar",
}

# Completar cuando confirmes la numeración.
HE_CORAZON = [5, 21, 39]


def titulo(etapa):
    return ETAPAS[etapa][0]


def acciones(muestra):
    etapa = muestra["pendiente"]
    if etapa == "elegir":
        return ["desgaste", "corte_eval"]
    return [etapa]


def siguiente(muestra, accion):
    if accion == "reincluir" and muestra.get("desgaste_obligatorio"):
        return "desgaste"
    return ETAPAS[accion][1]


def avance(muestra):
    etapa = muestra["pendiente"]
    cadena = [titulo(etapa)]

    for _ in range(2):
        etapa = (
            "desgaste"
            if etapa == "reincluir" and muestra.get("desgaste_obligatorio")
            else ETAPAS[etapa][1]
        )
        if etapa is None:
            break
        cadena.append(titulo(etapa))

    return " → ".join(cadena)