# KeyBinder

App de escritorio Windows (solo Python) para gestionar atajos de teclado globales.

## Stack

- **GUI:** `customtkinter` (tema oscuro, paleta inspirada en G HUB en `gui/theme.py`)
- **Hotkeys:** librería `keyboard` para intercepción global
- **Bandeja:** `pystray` (icono en system tray con menú contextual)
- **Iconos:** Font Awesome 6 Free (descarga automática al primer inicio en `assets/fonts/`)
- **Empaquetado:** PyInstaller via `KeyBinder.spec`

## Comandos

```powershell
# Ejecutar en desarrollo (consola oculta)
.\venv\Scripts\pythonw.exe main.py

# Iniciar minimizado a la bandeja
.\venv\Scripts\pythonw.exe main.py --tray

# Compilar .exe
pyinstaller KeyBinder.spec
```

`KeyBinder.bat` ejecuta el primer comando — doble clic para lanzar.

## Arquitectura

- `main.py` — punto de entrada; agrega raíz del proyecto a `sys.path`, inicia `KeyBinderApp`
- `gui/app.py` — ventana principal; conecta manager, listener y tray
- `gui/dialogs.py` — diálogos modales que escanean Menú Inicio + Registro via `core/app_scanner.py`
- `core/keybind_manager.py` — CRUD con persistencia automática a `data/keybinds.json`
- `core/listener.py` — registro de hotkeys globales; las acciones se ejecutan en hilos daemon
- `core/startup_manager.py` — gestiona entrada `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- `core/utils.py` — resolución de rutas distinta entre desarrollo (`python main.py`) y .exe congelado (`getattr(sys, 'frozen', False)`)
- `gui/icon_manager.py` — descarga Font Awesome .ttf desde CDN si falta; registra via `AddFontResourceExW`

## Convenciones

- Textos de UI en **español**; comentarios/docstrings en **inglés**
- Tipos de acción (`keybind_manager.py:17-22`): `launch_app`, `open_url`, `type_text`, `run_command`
- Formato de hotkey: minúsculas con separador `+`, ej. `ctrl+shift+t`, `b+windows izquierda`
- `data/keybinds.json` vive junto al .exe en producción, o en la raíz del proyecto en desarrollo
- Cerrar ventana la manda a la bandeja (no cierra la app); usar menú "Salir completamente" para salir
