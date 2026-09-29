# Seguimiento histológico de defectos óseos

Sistema de seguimiento de muestras, tareas pendientes e historial de procesamiento histológico.

**Página de consulta:** https://javcanelo.github.io/defectos_oseos/

## Cómo funciona

- El trabajo se registra desde una aplicación local en Python y Streamlit.
- Al completar una tarea, se guarda su fecha y se habilita la etapa siguiente.
- La página pública muestra la última versión publicada.
- Las consultas e indicaciones pueden enviarse mediante el formulario enlazado en la página. Se revisan e incorporan manualmente al sistema.

La página pública es de solo lectura. No permite modificar muestras ni marcar tareas.

## Consultar el seguimiento

La página permite:

- Buscar una muestra por su identificador.
- Filtrar entre pendientes, archivadas o todas.
- Ver la acción pendiente en una etiqueta de color.
- Consultar los pasos siguientes pasando el cursor sobre la etiqueta.
- Desplegar el historial de cada muestra.
- Consultar la presencia registrada del bloque y de placas en el laboratorio.

**Archivada** significa que el trabajo actual está cerrado. No implica que el material haya salido del laboratorio.

La presencia de placas indica si hay alguna en el laboratorio; no constituye un inventario individual de todas las placas.

## Uso local

Desde la carpeta del proyecto:

```bash
source .env/bin/activate
streamlit run app.py --server.address 127.0.0.1
```

Abrir http://localhost:8501 y mantener la terminal abierta mientras se utiliza el tablero.

### Registrar avances

En la muestra correspondiente:

1. Seleccionar la acción realizada.
2. Indicar su fecha o marcar que se desconoce.
3. Pulsar **Marcar realizado**.

Para registrar una revisión de SA, seleccionar la decisión y guardar.

### Cambiar el plan o reabrir una muestra

Usar **Detalle, presencia y cambios de plan → Actualizar plan**, indicando el motivo.

Cambiar el plan no significa que esa tarea ya se haya realizado ni deshace eventos anteriores.

### Agregar muestras

Detener Streamlit antes de utilizar el script de ingreso, para evitar escrituras simultáneas.

```bash
python3 agregar_muestra.py
```

El script solicita los datos, muestra un resumen y pide confirmación antes de guardar. No sobrescribe muestras existentes.

### Presencia del material

Actualizar la presencia cuando corresponda. Una revisión o entrega no implica automáticamente una salida física.

## Publicar cambios

Los cambios locales no aparecen automáticamente en la página pública.

```bash
python3 publicar.py
git add data/muestras.json docs/
git commit -m "Actualizar seguimiento histológico"
git push
```

Si también se modificó código, agregar los archivos correspondientes al commit.

GitHub Pages publica después del push. Consultar el estado en **Actions** y comprobar la fecha de última publicación de la página.

## Archivos principales

| Archivo | Función |
|---|---|
| `app.py` | Tablero local de trabajo. |
| `flujo.py` | Etapas, transiciones y configuración de tinciones. |
| `agregar_muestra.py` | Ingreso interactivo de muestras desde terminal. |
| `iniciar.py` | Carga inicial; no se utiliza para agregar muestras posteriormente. |
| `data/muestras.json` | Datos actuales e historial de las muestras. |
| `publicar.py` | Generación de la página y del resumen CSV. |
| `docs/index.html` | Página generada para GitHub Pages. |
| `docs/resumen.csv` | Resumen generado para consulta o importación. |

No editar directamente los archivos de `docs/`: se reemplazan al ejecutar `publicar.py`.

## Flujo de trabajo

Recepción → reinclusión → desgaste o corte directo de evaluación.

Desgaste → corte de evaluación → HE de evaluación → revisión SA.

La revisión determina la siguiente tarea: profundizar, reincluir, realizar un protocolo de corte u otra indicación.

Corte de set → tinción HE correspondiente → archivo.

Las muestras archivadas pueden reabrirse para nuevos trabajos conservando su historial. Los bloques nuevos identificados en la carga inicial requieren desgaste después de la reinclusión.

## Protocolos de corte

La numeración es consecutiva por placa, incluyendo HE e IHQ.

| Protocolo | Secuencia | Total | Placas a teñir con HE |
|---|---|---:|---|
| Estándar | 3 HE + 3 IHQ + 3 HE + 3 IHQ + 3 HE | 15 | 1, 8, 15 |
| Estrella | 4 IHQ + 4 HE + 4 IHQ + 4 HE + 4 IHQ + 3 HE | 23 | 5, 21 |
| Corazón | 4 IHQ + 4 HE + 4 IHQ + 4 HE + 4 IHQ + 4 HE + 4 IHQ + 4 HE + 4 IHQ + 3 HE | 39 | 5, 21, 39 |

Las placas destinadas a IHQ quedan sin teñir en este seguimiento. El alcance del trabajo comprende el procesamiento, corte, tinciones HE y entrega.

## Criterios del registro

- Una tarea pendiente no se considera realizada hasta confirmarla.
- Las fechas desconocidas se mantienen como desconocidas.
- Los identificadores se conservan como texto, incluidos sus ceros iniciales.
- La publicación representa una copia del estado local en el momento indicado.
- Los tickets del formulario no modifican automáticamente los datos.
- El cierre del trabajo y la presencia física del material son independientes.

## Instalación en otro equipo

Con Python, Git y el repositorio disponible:

```bash
python3 -m venv .env
source .env/bin/activate
python -m pip install -r requirements.txt
```

Si `data/muestras.json` ya contiene el seguimiento, no ejecutar nuevamente la carga inicial.
