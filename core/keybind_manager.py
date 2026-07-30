"""
keybind_manager.py — Módulo de lógica de negocio para KeyBinder.

Encapsula todas las operaciones CRUD sobre los keybinds:
crear, leer, actualizar, eliminar y alternar el estado activo.
Cada keybind se representa como un diccionario con campos tipados.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from core.storage import Storage


# Tipos de acción soportados
ACTION_TYPES = {
    "launch_app": "Abrir Aplicacion",
    "open_url": "Abrir URL",
    "type_text": "Escribir Texto",
    "run_command": "Ejecutar Comando",
}


def _create_keybind_dict(
    name: str,
    hotkey: str,
    action_type: str,
    action_value: str,
    enabled: bool = True,
) -> dict[str, Any]:
    """
    Crea un diccionario de keybind con todos los campos requeridos.

    Args:
        name: Nombre descriptivo del keybind.
        hotkey: Combinación de teclas (ej: 'ctrl+shift+t').
        action_type: Tipo de acción (ver ACTION_TYPES).
        action_value: Valor asociado a la acción (ruta, URL, texto, comando).
        enabled: Si el keybind está activo.

    Returns:
        Diccionario con todos los campos del keybind.
    """
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "hotkey": hotkey,
        "action_type": action_type,
        "action_value": action_value,
        "enabled": enabled,
        "created_at": datetime.now().isoformat(),
    }


class KeybindManager:
    """
    Gestor de keybinds — CRUD completo con persistencia automática.

    Cada operación de escritura (add, update, delete, toggle) guarda
    automáticamente los cambios en disco a través del módulo Storage.
    """

    def __init__(self, storage: Storage = None):
        """
        Inicializa el gestor cargando los keybinds existentes.

        Args:
            storage: Instancia de Storage. Si es None, usa la configuración por defecto.
        """
        self.storage = storage or Storage()
        self.keybinds: list[dict[str, Any]] = self.storage.load()

    def get_all(self) -> list[dict[str, Any]]:
        """Retorna una copia de todos los keybinds."""
        return list(self.keybinds)

    def get_by_id(self, keybind_id: str) -> Optional[dict[str, Any]]:
        """
        Busca un keybind por su ID.

        Args:
            keybind_id: UUID del keybind.

        Returns:
            El diccionario del keybind o None si no se encontró.
        """
        for kb in self.keybinds:
            if kb["id"] == keybind_id:
                return kb
        return None

    def get_enabled(self) -> list[dict[str, Any]]:
        """Retorna solo los keybinds que están habilitados."""
        return [kb for kb in self.keybinds if kb.get("enabled", True)]

    def add_keybind(
        self,
        name: str,
        hotkey: str,
        action_type: str,
        action_value: str,
        enabled: bool = True,
    ) -> dict[str, Any]:
        """
        Crea un nuevo keybind y lo guarda.

        Args:
            name: Nombre descriptivo.
            hotkey: Combinación de teclas.
            action_type: Tipo de acción.
            action_value: Valor de la acción.
            enabled: Estado inicial (por defecto True).

        Returns:
            El diccionario del keybind recién creado.

        Raises:
            ValueError: Si el action_type no es válido o faltan campos.
        """
        # Validaciones
        if not name or not name.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if not hotkey or not hotkey.strip():
            raise ValueError("El atajo de teclado no puede estar vacío.")
        if action_type not in ACTION_TYPES:
            raise ValueError(
                f"Tipo de acción inválido: '{action_type}'. "
                f"Opciones: {list(ACTION_TYPES.keys())}"
            )
        if not action_value or not action_value.strip():
            raise ValueError("El valor de la acción no puede estar vacío.")

        keybind = _create_keybind_dict(
            name=name.strip(),
            hotkey=hotkey.strip().lower(),
            action_type=action_type,
            action_value=action_value.strip(),
            enabled=enabled,
        )

        self.keybinds.append(keybind)
        self._save()
        return keybind

    def update_keybind(
        self,
        keybind_id: str,
        name: str = None,
        hotkey: str = None,
        action_type: str = None,
        action_value: str = None,
    ) -> Optional[dict[str, Any]]:
        """
        Actualiza los campos de un keybind existente.

        Solo se actualizan los campos que no sean None.

        Args:
            keybind_id: UUID del keybind a actualizar.
            name: Nuevo nombre (opcional).
            hotkey: Nueva combinación de teclas (opcional).
            action_type: Nuevo tipo de acción (opcional).
            action_value: Nuevo valor de acción (opcional).

        Returns:
            El keybind actualizado o None si no se encontró.

        Raises:
            ValueError: Si un valor proporcionado es inválido.
        """
        keybind = self.get_by_id(keybind_id)
        if keybind is None:
            return None

        if name is not None:
            if not name.strip():
                raise ValueError("El nombre no puede estar vacío.")
            keybind["name"] = name.strip()

        if hotkey is not None:
            if not hotkey.strip():
                raise ValueError("El atajo de teclado no puede estar vacío.")
            keybind["hotkey"] = hotkey.strip().lower()

        if action_type is not None:
            if action_type not in ACTION_TYPES:
                raise ValueError(f"Tipo de acción inválido: '{action_type}'.")
            keybind["action_type"] = action_type

        if action_value is not None:
            if not action_value.strip():
                raise ValueError("El valor de la acción no puede estar vacío.")
            keybind["action_value"] = action_value.strip()

        self._save()
        return keybind

    def delete_keybind(self, keybind_id: str) -> bool:
        """
        Elimina un keybind por su ID.

        Args:
            keybind_id: UUID del keybind a eliminar.

        Returns:
            True si se eliminó, False si no se encontró.
        """
        original_count = len(self.keybinds)
        self.keybinds = [kb for kb in self.keybinds if kb["id"] != keybind_id]

        if len(self.keybinds) < original_count:
            self._save()
            return True
        return False

    def toggle_keybind(self, keybind_id: str) -> Optional[bool]:
        """
        Alterna el estado enabled/disabled de un keybind.

        Args:
            keybind_id: UUID del keybind.

        Returns:
            El nuevo estado (True/False) o None si no se encontró.
        """
        keybind = self.get_by_id(keybind_id)
        if keybind is None:
            return None

        keybind["enabled"] = not keybind.get("enabled", True)
        self._save()
        return keybind["enabled"]

    def _save(self) -> None:
        """Persiste el estado actual de los keybinds en disco."""
        self.storage.save(self.keybinds)
