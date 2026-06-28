# MDeIA UCCuyo

**Modelo de Madurez Digital e Inteligencia Artificial** · Universidad Católica de Cuyo  
Observatorio de Inteligencia Artificial · Secretaría de Investigación

Sistema de medición del **Índice de Madurez Digital (IMD)** con extensión propia de IA, basado en UDigital madurez (MetaRed) y adaptado a la UCCuyo.

Documentación del modelo: [`MODELO-MDEIA.md`](MODELO-MDEIA.md)

## En vivo (Streamlit Cloud)

https://mdeia-uccuyo.streamlit.app

## Ejecutar en local

```bash
cd mdeia-uccuyo
./run-mdeia.sh
```

Abrí: http://localhost:8502

## Estructura

| Ruta | Uso |
|------|-----|
| `streamlit_app.py` | Entrada para Streamlit Cloud |
| `app.py` | Aplicación principal |
| `data/` | Marco, indicadores, unidades académicas |
| `lib/` | Cálculo IMD, informes, encuesta OIA |

## Secrets (encuesta estudiantil, opcional)

Copiá `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` en local,  
o configurá en Streamlit Cloud → Settings → Secrets.

## Contacto

observatorioia@uccuyo.edu.ar
