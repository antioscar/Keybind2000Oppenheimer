"""
storage.py — Módulo de persistencia para KeyBinder.

Maneja la lectura y escritura del archivo JSON donde se almacenan
los keybinds del usuario. Crea el archivo y directorio automáticamente
si no existen, y maneja errores de JSON corrupto o permisos.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Any


class Storage:
    """Gestiona la persistencia de keybinds en un archivo JSON local."""

    def __init__(self, filepath: str = None):
        """
        Inicializa el almacenamiento.

        Args:
            filepath: Ruta al archivo JSON. Si es None, usa 'data/keybinds.json'
                      relativo al directorio raíz del proyecto.
        """
        if filepath is None:
            from core.utils import get_data_dir
            filepath = get_data_dir() / "keybinds.json"

        self.filepath = filepath
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Crea el directorio padre del archivo si no existe."""
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def load(self) -> list[dict[str, Any]]:
        """
        Carga los keybinds desde el archivo JSON.

        Returns:
            Lista de diccionarios, cada uno representando un keybind.
            Retorna lista vacía si el archivo no existe o está corrupto.
        """
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validar que el contenido sea una lista
            if not isinstance(data, list):
                print(f"[Storage] Advertencia: El archivo no contiene una lista. "
                      f"Se creará un backup y se reiniciará.")
                self._create_backup()
                return []

            return data

        except json.JSONDecodeError as e:
            print(f"[Storage] Error: JSON corrupto en '{self.filepath}': {e}")
            self._create_backup()
            return []
        except PermissionError:
            print(f"[Storage] Error: Sin permisos para leer '{self.filepath}'.")
            return []
        except Exception as e:
            print(f"[Storage] Error inesperado al cargar: {e}")
            return []

    def save(self, keybinds: list[dict[str, Any]]) -> bool:
        """
        Guarda la lista de keybinds en el archivo JSON.

        Args:
            keybinds: Lista de diccionarios de keybinds a guardar.

        Returns:
            True si se guardó correctamente, False en caso de error.
        """
        self._ensure_directory()

        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(keybinds, f, indent=2, ensure_ascii=False)
            return True

        except PermissionError:
            print(f"[Storage] Error: Sin permisos para escribir en '{self.filepath}'.")
            return False
        except Exception as e:
            print(f"[Storage] Error inesperado al guardar: {e}")
            return False

    def _create_backup(self) -> None:
        """
        Crea un backup del archivo JSON corrupto antes de reiniciarlo.
        El backup se nombra con timestamp para evitar colisiones.
        """
        if os.path.exists(self.filepath):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.filepath}.backup_{timestamp}"
            try:
                shutil.copy2(self.filepath, backup_path)
                print(f"[Storage] Backup creado en: {backup_path}")
            except Exception as e:
                print(f"[Storage] No se pudo crear backup: {e}")
