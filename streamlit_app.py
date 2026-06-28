# -*- coding: utf-8 -*-
"""MDeIA UCCuyo — punto de entrada para Streamlit Cloud y local."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parent / "app.py"), run_name="__main__")
