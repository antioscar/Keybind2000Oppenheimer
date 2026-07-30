"""
listener.py — Módulo de interceptación global de teclado para KeyBinder.

Usa la librería `keyboard` para registrar hotkeys globales que funcionan
incluso cuando la aplicación está minimizada. También provee la funcionalidad
de captura de hotkeys para la interfaz gráfica.
"""

import os
import subprocess
import threading
import webbrowser
from typing import Any, Callable, Optional

import keyboard


class KeybindListener:
    """
    Interceptor global de teclado.

    Registra hotkeys usando la librería `keyboard` y ejecuta las acciones
    asociadas (abrir apps, URLs, escribir texto, ejecutar comandos).
    """

    def __init__(self):
        """Inicializa el listener con un registro vacío de hotkeys."""
        # Mapea hotkey_string -> hook_handle para poder desregistrar
        self._registered_hotkeys: dict[str, Any] = {}
        self._capturing = False
        self._capture_keys: list[str] = []

    def register_all(self, keybinds: list[dict[str, Any]]) -> int:
        """
        Registra todos los keybinds habilitados como hotkeys globales.

        Args:
            keybinds: Lista de diccionarios de keybinds.

        Returns:
            Número de hotkeys registrados exitosamente.
        """
        count = 0
        for kb in keybinds:
            if kb.get("enabled", True):
                success = self._register_single(kb)
                if success:
                    count += 1
        return count

    def unregister_all(self) -> None:
        """Desregistra todos los hotkeys globales activos."""
        for hotkey_str, hook in list(self._registered_hotkeys.items()):
            try:
                keyboard.remove_hotkey(hook)
            except (ValueError, KeyError):
                # El hook ya fue removido o es inválido
                pass
        self._registered_hotkeys.clear()

    def refresh(self, keybinds: list[dict[str, Any]]) -> int:
        """
        Refresca todos los hotkeys: desregistra los actuales y registra los nuevos.

        Args:
            keybinds: Lista actualizada de keybinds.

        Returns:
            Número de hotkeys registrados exitosamente.
        """
        self.unregister_all()
        return self.register_all(keybinds)

    def _register_single(self, keybind: dict[str, Any]) -> bool:
        """
        Registra un único keybind como hotkey global.

        Args:
            keybind: Diccionario del keybind a registrar.

        Returns:
            True si se registró exitosamente.
        """
        hotkey_str = keybind.get("hotkey", "")
        if not hotkey_str:
            return False

        # Si ya existe un hook para esta combinación, desregistrarlo primero
        if hotkey_str in self._registered_hotkeys:
            try:
                keyboard.remove_hotkey(self._registered_hotkeys[hotkey_str])
            except (ValueError, KeyError):
                pass

        try:
            # Crear callback con los datos del keybind capturados por closure
            action_type = keybind["action_type"]
            action_value = keybind["action_value"]
            kb_name = keybind.get("name", "Sin nombre")

            def on_trigger(at=action_type, av=action_value, name=kb_name, hs=hotkey_str):
                self._execute_action(at, av, name, hs)

            hook = keyboard.add_hotkey(
                hotkey_str,
                on_trigger,
                suppress=True,
                trigger_on_release=False,
            )
            self._registered_hotkeys[hotkey_str] = hook
            return True

        except Exception as e:
            print(f"[Listener] Error al registrar hotkey '{hotkey_str}': {e}")
            return False

    def _execute_action(
        self, action_type: str, action_value: str, name: str, hotkey_str: str = ""
    ) -> None:
        """
        Ejecuta la acción asociada a un keybind en un hilo separado.

        Args:
            action_type: Tipo de acción.
            action_value: Valor de la acción.
            name: Nombre del keybind (para logging).
            hotkey_str: Atajo pulsado, usado para arreglos de focus/menu.
        """
        # Hack para evitar que el Menú Inicio se abra si el atajo incluye 'windows'
        # Al suprimir la tecla secundaria, Windows cree que solo se presionó y soltó 'Win'
        if "windows" in hotkey_str:
            keyboard.send("ctrl")

        def _run():
            try:
                if action_type == "launch_app":
                    self._action_launch_app(action_value)
                elif action_type == "open_url":
                    self._action_open_url(action_value)
                elif action_type == "type_text":
                    self._action_type_text(action_value)
                elif action_type == "run_command":
                    self._action_run_command(action_value)
                else:
                    print(f"[Listener] Tipo de acción desconocido: '{action_type}'")
            except Exception as e:
                print(f"[Listener] Error al ejecutar '{name}': {e}")

        # Ejecutar en hilo separado para no bloquear el hook
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    @staticmethod
    def _action_launch_app(path: str) -> None:
        """Abre una aplicación o archivo ejecutable."""
        if os.path.exists(path):
            os.startfile(path)
        else:
            # Intentar como comando del sistema
            subprocess.Popen(path, shell=True)

    @staticmethod
    def _action_open_url(url: str) -> None:
        """Abre una URL en el navegador predeterminado."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)

    @staticmethod
    def _action_type_text(text: str) -> None:
        """Escribe un texto simulando pulsaciones de teclado."""
        # Pequeño delay para que la tecla del hotkey se libere primero
        import time
        time.sleep(0.1)
        keyboard.write(text, delay=0.02)

    @staticmethod
    def _action_run_command(command: str) -> None:
        """Ejecuta un comando del sistema."""
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def capture_hotkey(
        self,
        callback: Callable[[str], None],
        timeout: float = 10.0,
    ) -> None:
        """
        Inicia el modo de captura de hotkey en un hilo separado.

        Escucha las teclas presionadas por el usuario y cuando las libera,
        devuelve la combinación capturada al callback.

        Args:
            callback: Función que recibe la combinación de teclas como string.
            timeout: Segundos máximos de espera (por defecto 10).
        """
        if self._capturing:
            return

        def _capture_thread():
            self._capturing = True
            try:
                event = keyboard.read_hotkey(suppress=False)
                if event:
                    callback(event)
            except Exception as e:
                print(f"[Listener] Error en captura: {e}")
                callback("")
            finally:
                self._capturing = False

        thread = threading.Thread(target=_capture_thread, daemon=True)
        thread.start()

    @property
    def is_capturing(self) -> bool:
        """Retorna True si está en modo captura de hotkey."""
        return self._capturing

    @property
    def active_count(self) -> int:
        """Retorna el número de hotkeys actualmente registrados."""
        return len(self._registered_hotkeys)

    def shutdown(self) -> None:
        """Limpia todos los recursos del listener."""
        self.unregister_all()
