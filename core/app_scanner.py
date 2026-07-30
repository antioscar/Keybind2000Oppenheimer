"""
app_scanner.py — Escáner de aplicaciones instaladas en Windows.

Busca aplicaciones instaladas leyendo los accesos directos (.lnk)
del Menú Inicio y las entradas del Registro de Windows. Retorna
una lista de (nombre, ruta_ejecutable) para usarse en la GUI.
"""

import os
import threading
from typing import Callable, Optional


def _scan_start_menu_fast(folder: str, results: dict[str, str]) -> None:
    """
    Escaneo rápido del Menú Inicio — solo recopila nombres y rutas de .lnk
    sin resolver los targets (mucho más rápido).

    Args:
        folder: Ruta de la carpeta a escanear.
        results: Diccionario nombre -> ruta .lnk
    """
    if not os.path.exists(folder):
        return

    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.lower().endswith(".lnk"):
                name = os.path.splitext(filename)[0]

                lower_name = name.lower()
                if any(skip in lower_name for skip in [
                    "uninstall", "desinstalar", "remove",
                    "readme", "help", "manual", "release notes",
                    "license", "website", "documentation",
                ]):
                    continue

                lnk_path = os.path.join(root, filename)
                if name not in results:
                    results[name] = lnk_path


def _scan_registry(results: dict[str, str]) -> None:
    """
    Escanea el Registro de Windows para encontrar aplicaciones instaladas.

    Lee las claves de desinstalación en HKLM y HKCU.

    Args:
        results: Diccionario nombre -> ruta donde agregar resultados.
    """
    import winreg

    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE,
         r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE,
         r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER,
         r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    for hive, path in registry_paths:
        try:
            key = winreg.OpenKey(hive, path)
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)

                    try:
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    except FileNotFoundError:
                        i += 1
                        continue

                    # Buscar el ejecutable
                    exe_path = None
                    for value_name in ["DisplayIcon", "InstallLocation"]:
                        try:
                            val = winreg.QueryValueEx(subkey, value_name)[0]
                            if val:
                                # DisplayIcon puede tener formato "path.exe,0"
                                clean = val.split(",")[0].strip().strip('"')
                                if clean.lower().endswith(".exe") and os.path.exists(clean):
                                    exe_path = clean
                                    break
                                elif os.path.isdir(clean):
                                    # Buscar .exe en InstallLocation
                                    for f in os.listdir(clean):
                                        if f.lower().endswith(".exe"):
                                            full = os.path.join(clean, f)
                                            if os.path.exists(full):
                                                exe_path = full
                                                break
                        except (FileNotFoundError, OSError):
                            continue

                    if name and exe_path and name not in results:
                        results[name] = exe_path

                    winreg.CloseKey(subkey)
                    i += 1
                except OSError:
                    break

            winreg.CloseKey(key)
        except (OSError, PermissionError):
            continue


class AppScanner:
    """
    Escáner de aplicaciones instaladas.

    Busca apps en el Menú Inicio y el Registro de Windows.
    Los resultados se cachean para no re-escanear cada vez.
    """

    def __init__(self):
        self._apps: dict[str, str] = {}  # nombre -> ruta
        self._scanned = False
        self._scanning = False

    def scan(self, callback: Callable[[list[tuple[str, str]]], None] = None) -> None:
        """
        Inicia el escaneo de aplicaciones en un hilo separado.

        Args:
            callback: Función llamada con la lista de (nombre, ruta) al terminar.
        """
        if self._scanning:
            return

        def _scan_thread():
            self._scanning = True
            try:
                results: dict[str, str] = {}

                # Escaneo rápido del Menú Inicio (solo nombres + rutas .lnk)
                start_menu_paths = [
                    os.path.join(
                        os.environ.get("PROGRAMDATA", r"C:\ProgramData"),
                        r"Microsoft\Windows\Start Menu\Programs"
                    ),
                    os.path.join(
                        os.environ.get("APPDATA", ""),
                        r"Microsoft\Windows\Start Menu\Programs"
                    ),
                ]
                for path in start_menu_paths:
                    _scan_start_menu_fast(path, results)

                # Escaneo del registro
                try:
                    _scan_registry(results)
                except Exception as e:
                    print(f"[AppScanner] Error escaneando registro: {e}")

                self._apps = results
                self._scanned = True

                if callback:
                    callback(self.get_app_list())

            except Exception as e:
                print(f"[AppScanner] Error en escaneo: {e}")
            finally:
                self._scanning = False

        thread = threading.Thread(target=_scan_thread, daemon=True)
        thread.start()

    def scan_sync(self) -> list[tuple[str, str]]:
        """
        Escaneo síncrono (bloquea hasta terminar).

        Returns:
            Lista de (nombre, ruta) ordenada alfabéticamente.
        """
        results: dict[str, str] = {}

        start_menu_paths = [
            os.path.join(
                os.environ.get("PROGRAMDATA", r"C:\ProgramData"),
                r"Microsoft\Windows\Start Menu\Programs"
            ),
            os.path.join(
                os.environ.get("APPDATA", ""),
                r"Microsoft\Windows\Start Menu\Programs"
            ),
        ]
        for path in start_menu_paths:
            _scan_start_menu_fast(path, results)

        try:
            _scan_registry(results)
        except Exception:
            pass

        self._apps = results
        self._scanned = True
        return self.get_app_list()

    def get_app_list(self) -> list[tuple[str, str]]:
        """
        Retorna las apps encontradas como lista de tuplas (nombre, ruta).

        Returns:
            Lista ordenada alfabéticamente de (nombre, ruta).
        """
        return sorted(self._apps.items(), key=lambda x: x[0].lower())

    def get_app_names(self) -> list[str]:
        """Retorna solo los nombres de las apps, ordenados."""
        return [name for name, _ in self.get_app_list()]

    def get_path_for_name(self, name: str) -> Optional[str]:
        """
        Retorna la ruta del ejecutable para un nombre de app.

        Args:
            name: Nombre de la aplicación.

        Returns:
            Ruta del ejecutable o None si no se encontró.
        """
        return self._apps.get(name)

    @property
    def is_scanned(self) -> bool:
        return self._scanned

    @property
    def is_scanning(self) -> bool:
        return self._scanning

    @property
    def app_count(self) -> int:
        return len(self._apps)
