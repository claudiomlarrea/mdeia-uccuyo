# -*- coding: utf-8 -*-
"""UI Streamlit — encuestas MDeIA por audiencia."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from constants import FASE1_MENU
from lib.encuestas_mdeia import (
    aplicar_encuesta_a_diagnostico,
    audiencia_cfg,
    calcular_indicadores_desde_encuesta,
    generar_apps_script_google_forms,
    generar_plantilla_xlsx,
    listar_audiencias,
    plantilla_filename,
    resumen_encuesta_markdown,
)
from lib.oia_encuesta import load_oia_config, load_uploaded_file
from lib.unidades import reemplazar_respuestas_activas, respuestas_activas, unidad_label

_GS_PATH = Path(__file__).resolve().parent.parent / "scripts" / "google_forms" / "generar_encuestas_mdeia.gs"


def _init_session() -> None:
    if "mdeia_encuestas_resultados" not in st.session_state:
        st.session_state.mdeia_encuestas_resultados = {}


def _leer_excel_respuestas(name: str, data: bytes) -> pd.DataFrame:
    df = load_uploaded_file(name, data)
    if name.lower().endswith((".xlsx", ".xls")):
        xl = pd.ExcelFile(BytesIO(data))
        if "Respuestas" in xl.sheet_names:
            return xl.parse("Respuestas")
    return df


def render_encuestas_audiencia() -> None:
    _init_session()
    oia_cfg = load_oia_config()
    audiencias = listar_audiencias()
    ids = [a["id"] for a in audiencias]
    labels = {a["id"]: a["nombre"] for a in audiencias}

    st.subheader("Encuestas por audiencia")
    st.caption(
        f"Ámbito activo: **{unidad_label(st.session_state.mdeia_unidad_activa)}**. "
        "Descargá plantilla o generá Google Forms, socializá el enlace, exportá respuestas "
        "y cargalas aquí para actualizar indicadores MDeIA."
    )

    tab_plantillas, tab_cargar, tab_resultado, tab_forms = st.tabs(
        ["Plantillas Excel", "Cargar respuestas", "Resultado y aplicar", "Google Forms"]
    )

    with tab_plantillas:
        st.markdown("#### Descargar plantillas")
        for aud in audiencias:
            aud_id = aud["id"]
            aud_full = audiencia_cfg(aud_id)
            with st.expander(f"**{aud['nombre']}** — {aud.get('descripcion', '')}", expanded=aud_id == "estudiante"):
                st.markdown(f"**Población sugerida:** {aud_full.get('poblacion_ejemplo', '—')}")
                st.markdown(f"**Preguntas:** {len(aud_full.get('preguntas', []))}")
                if aud_full.get("indicadores"):
                    cods = ", ".join(f"`{i['codigo']}`" for i in aud_full["indicadores"])
                    st.markdown(f"**Indicadores que alimenta:** {cods}")
                st.download_button(
                    f"Descargar Excel — {aud['nombre']}",
                    data=generar_plantilla_xlsx(aud_id),
                    file_name=plantilla_filename(aud_id),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_tpl_{aud_id}",
                    type="primary" if aud_id == "estudiante" else "secondary",
                )

    with tab_forms:
        st.markdown("#### Crear formularios Google (enlaces para compartir)")
        st.markdown(
            """
            1. Abrí [script.google.com](https://script.google.com) → **Nuevo proyecto**.
            2. Pegá el script descargado abajo.
            3. Ejecutá **`crearTodasLasEncuestasMDeIA`** y autorizá Google Forms.
            4. En **Ver → Registros** obtenés **4 URLs** para compartir.
            5. Al cerrar: **Respuestas → Descargar .xlsx** → pestaña **Cargar respuestas**.
            """
        )
        gs_text = _GS_PATH.read_text(encoding="utf-8") if _GS_PATH.is_file() else generar_apps_script_google_forms()
        st.download_button(
            "Descargar script Google Apps Script (.gs)",
            data=gs_text,
            file_name="generar_encuestas_mdeia.gs",
            mime="text/plain",
            type="primary",
        )
        with st.expander("Ver / copiar script"):
            st.code(gs_text, language="javascript")
        url = oia_cfg.get("encuesta_clara_url")
        if url:
            st.info(f"Encuesta histórica OIA (Clara): [{url}]({url})")

    with tab_cargar:
        sel = st.selectbox(
            "Audiencia de la encuesta cargada",
            options=ids,
            format_func=lambda x: labels[x],
            key="mdeia_encuesta_audiencia_sel",
        )
        aud = audiencia_cfg(sel)
        st.caption(aud.get("descripcion", ""))
        pob = st.number_input(
            "Población convocada (para tasa de respuesta)",
            min_value=0,
            value=0,
            step=50,
            key=f"mdeia_enc_pob_{sel}",
            help=aud.get("poblacion_ejemplo", ""),
        )
        archivo = st.file_uploader(
            "Archivo de respuestas (.xlsx / .csv)",
            type=["xlsx", "xls", "csv"],
            key=f"mdeia_enc_file_{sel}",
        )
        if st.button("Analizar encuesta", type="primary", disabled=archivo is None, key=f"btn_anal_{sel}"):
            try:
                df = _leer_excel_respuestas(archivo.name, archivo.getvalue())
                pob_val = pob if pob > 0 else None
                metricas = calcular_indicadores_desde_encuesta(df, sel, poblacion=pob_val)
                st.session_state.mdeia_encuestas_resultados[sel] = metricas
                st.success("Encuesta analizada. Revisá **Resultado y aplicar**.")
            except Exception as exc:
                st.error(str(exc))

    with tab_resultado:
        sel_res = st.selectbox(
            "Ver resultado de audiencia",
            options=ids,
            format_func=lambda x: labels[x],
            key="mdeia_enc_res_sel",
        )
        metricas = st.session_state.mdeia_encuestas_resultados.get(sel_res)
        if not metricas:
            st.info("Todavía no hay encuesta analizada para esta audiencia.")
        else:
            st.markdown(resumen_encuesta_markdown(metricas))
            for row in metricas.get("detalle_indicadores") or []:
                st.markdown(f"- `{row['codigo']}` → **{row['valor']}** ({row.get('nota', '')})")
            if st.button("Aplicar al diagnóstico MDeIA", type="primary", key=f"btn_apply_{sel_res}"):
                merged = aplicar_encuesta_a_diagnostico(respuestas_activas(), metricas)
                reemplazar_respuestas_activas(merged)
                n = len(metricas.get("indicadores") or {})
                st.success(
                    f"Se actualizaron **{n}** indicadores en "
                    f"**{unidad_label(st.session_state.mdeia_unidad_activa)}**."
                )
