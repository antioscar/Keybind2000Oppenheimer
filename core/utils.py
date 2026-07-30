"""
utils.py — Utilidades generales para KeyBinder.
"""

import sys
import os
from pathlib import Path

def get_base_dir() -> Path:
    """
    Retorna el directorio base de la aplicación.
    Funciona tanto en desarrollo (script Python) como en producción (PyInstaller .exe).
    """
    if getattr(sys, 'frozen', False):
        # Si está empaquetado con PyInstaller, usa el directorio del ejecutable o MEIPASS
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        return Path(sys.executable).parent
    else:
        # En desarrollo, usa el directorio raíz del proyecto (2 niveles arriba de este archivo)
        return Path(__file__).resolve().parent.parent

def get_data_dir() -> Path:
    """
    Retorna el directorio donde se guardarán los datos del usuario (keybinds.json).
    En el .exe, lo guarda al lado del ejecutable para que sea portable.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "data"
    else:
        return get_base_dir() / "data"
