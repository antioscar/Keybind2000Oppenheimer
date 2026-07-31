# KeyBinder

Gestor de atajos de teclado globales para Windows. Básicamente, asignas una combinación de teclas a una acción (abrir un programa, una URL, ejecutar un comando, escribir texto) y funciona sin importar en qué ventana estés.

La interfaz está hecha con customtkinter y tiene un tema oscuro inspirado en Logitech G HUB. Al cerrar la ventana se va a la bandeja del sistema — la app sigue corriendo en background.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-only-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/Licencia-libre-green)

---

## Qué hace

- **Atajos globales** — Funcionan en todo Windows, no solo dentro de la app
- **Abrir aplicaciones** — Lanza cualquier `.exe` o archivo desde un atajo
- **Abrir URLs** — Abre sitios en el navegador predeterminado
- **Escribir texto** — Simula escritura (para firmas, templates, respuestas frecuentes)
- **Ejecutar comandos** — Corre comandos CMD/PowerShell en silencio, sin abrir ventana
- **System Tray** — Se minimiza al lado del reloj, consume casi nada de recursos
- **Inicio con Windows** — Se configura automáticamente para arrancar con el sistema
- **Portable** — Los atajos se guardan en un `.json` junto al ejecutable, te lo llevas en un USB y listo

---

## Descarga (usuarios)

No necesitas Python ni consola ni nada.

1. Ir a [Releases](https://github.com/antioscar/Keybind2000Oppenheimer/releases)
2. Bajar `KeyBinder.zip` de la última versión
3. Descomprimir donde quieras
4. Doble clic en `KeyBinder.exe`
5. Crear atajos. Al cerrar la ventana se queda en la bandeja

---

## Para desarrollo

### Requisitos

- Python 3.10+
- Windows (usa APIs nativas como `os.startfile`, registro de Windows, etc.)

### Setup

```powershell
git clone https://github.com/antioscar/Keybind2000Oppenheimer.git
cd Keybind2000Oppenheimer

python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt
```

### Correr

```powershell
# Normal (con consola de debug)
python main.py

# Sin consola (modo "producción local")
.\venv\Scripts\pythonw.exe main.py

# Iniciar directo en la bandeja
.\venv\Scripts\pythonw.exe main.py --tray
```

También hay un `KeyBinder.bat` que lo lanza con doble clic.

### Compilar el .exe

```powershell
.\venv\Scripts\pyinstaller KeyBinder.spec
```

El resultado queda en `dist/KeyBinder/`.

---

## Estructura del proyecto

```
keybinder/
├── main.py                  # Punto de entrada
├── gui/
│   ├── app.py               # Ventana principal, conecta todo
│   ├── components.py        # Cards, header, status bar, empty state
│   ├── dialogs.py           # Modales (crear/editar atajo, confirmar borrado)
│   ├── theme.py             # Colores, fuentes, dimensiones (paleta G HUB)
│   └── icon_manager.py      # Descarga Font Awesome si no existe, registra la fuente
├── core/
│   ├── keybind_manager.py   # CRUD de atajos + persistencia a JSON
│   ├── listener.py          # Registro de hotkeys globales via `keyboard`
│   ├── storage.py           # Lectura/escritura del archivo de datos
│   ├── tray_icon.py         # Icono en system tray con pystray
│   ├── startup_manager.py   # Entrada en el registro de Windows para inicio automático
│   ├── app_scanner.py       # Escanea Menú Inicio y Registro para sugerir apps
│   └── utils.py             # Resolución de rutas (dev vs .exe congelado)
├── assets/
│   ├── icon.ico             # Icono de la app
│   └── fonts/               # Font Awesome (se descarga automáticamente)
├── data/
│   └── keybinds.json        # Atajos guardados
├── requirements.txt
├── KeyBinder.spec           # Config de PyInstaller
└── KeyBinder.bat            # Launcher rápido
```

---

## Cómo funciona por dentro

El flujo es bastante simple:

1. `main.py` arranca `KeyBinderApp` (la ventana de customtkinter)
2. `KeybindManager` carga los atajos desde `keybinds.json`
3. `KeybindListener` registra cada atajo como hotkey global usando la librería `keyboard`
4. Cuando detecta una combinación, ejecuta la acción en un hilo daemon aparte para no bloquear nada
5. Al cerrar la ventana, `TrayManager` toma el control y la app sigue escuchando desde la bandeja

Los atajos se guardan automáticamente en cada operación (crear, editar, borrar, toggle). El archivo vive junto al `.exe` en producción o en la raíz del proyecto en desarrollo.

### Detalle sobre la tecla Windows

Si un atajo incluye la tecla Windows (ej: `b+windows izquierda`), hay un hack en el listener que manda un `ctrl` fantasma después de suprimir la tecla. Esto evita que Windows interprete la liberación de Win como "abrir el Menú Inicio".

---

## Dependencias

| Paquete | Para qué |
|---|---|
| `customtkinter` | Interfaz gráfica (tema oscuro nativo) |
| `keyboard` | Interceptar teclas a nivel global |
| `Pillow` | Procesamiento de imágenes para iconos |
| `pystray` | Icono en el system tray |

---

## Licencia

Código abierto, uso libre.
