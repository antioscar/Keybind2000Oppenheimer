"""
startup_manager.py — Módulo para gestionar el inicio automático en Windows.

Añade el ejecutable (o .bat) al registro de Windows para que inicie
silenciosamente con el sistema.
"""

import os
import sys
import winreg

APP_NAME = "KeyBinder"

def enable_startup() -> bool:
    """
    Añade el script principal al registro de inicio de Windows
    para que arranque automáticamente de forma invisible usando pythonw.exe.
    """
    try:
        if getattr(sys, 'frozen', False):
            # Si es un ejecutable compilado
            command = f'"{sys.executable}" --tray'
        else:
            # Calcular rutas absolutas para desarrollo
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pythonw_path = os.path.join(project_root, "venv", "Scripts", "pythonw.exe")
            main_script = os.path.join(project_root, "main.py")
            command = f'"{pythonw_path}" "{main_script}" --tray'

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[Startup] Error al añadir al inicio: {e}")
        return False

def disable_startup() -> bool:
    """Elimina la aplicación del registro de inicio."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        # Ya no existe la clave, así que está deshabilitado
        return True
    except Exception as e:
        print(f"[Startup] Error al remover del inicio: {e}")
        return False

def is_startup_enabled() -> bool:
    """Verifica si la app está en el registro de inicio."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"[Startup] Error al verificar inicio: {e}")
        return False
