"""Entrada compatible al validador vigente del portal RF01/RF02."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("validate-rf01-rf02.py")), run_name="__main__")
