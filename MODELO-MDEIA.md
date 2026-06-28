MDeIA UCCuyo — Madurez digital e IA · UCCuyo
=============================================

Sistema de medición del **Índice de Madurez Digital (IMD)** e Inteligencia Artificial
para la Universidad Católica de Cuyo. Desarrollado por el Observatorio de IA.

Basado en **UDigital madurez** (MetaRed) con extensión **MDeIA** propia de la UCCuyo.

## Ejecutar en local

1. Abrí la app → sección **Línea de base IMD**
2. Revisá la **Guía del diagnóstico** (36 indicadores, sesión ~90 min)
3. Completá el autodiagnóstico y exportá el **informe HTML**

```bash
./run-mdeia.sh
```

Abrí: http://localhost:8502

## Estructura

| Ruta | Uso |
|------|-----|
| `streamlit_app.py` | Entrada Streamlit Cloud |
| `app.py` | Aplicación principal |
| `data/framework.json` | Marco: retos, objetivos, fases |
| `data/indicadores_*.json` | Catálogo de indicadores |
| `lib/mdeia_model.py` | Cálculo del IMD |

## Fórmula IMD

```
IMD = (P_satisfechas / P_totales) × 100
```

## Contacto

observatorioia@uccuyo.edu.ar
