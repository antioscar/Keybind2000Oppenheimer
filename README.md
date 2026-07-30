# KeyBinder ⌨️🚀

KeyBinder es una aplicación de escritorio ligera y moderna para Windows que te permite crear y gestionar atajos de teclado globales personalizados. Con una interfaz limpia e inspirada en software profesional, KeyBinder funciona silenciosamente en segundo plano para potenciar tu productividad.

## ✨ Características

*   **Atajos Globales:** Los atajos funcionan en cualquier lugar de Windows, sin importar qué aplicación tengas abierta.
*   **Acciones Múltiples:** 
    *   **Abrir Aplicación:** Lanza programas o archivos locales (`.exe`, `.txt`, etc.).
    *   **Abrir URL:** Abre sitios web en tu navegador predeterminado.
    *   **Escribir Texto:** Simula la escritura de bloques de texto (ideal para correos, firmas o respuestas rápidas).
    *   **Ejecutar Comando:** Ejecuta comandos de consola de Windows (CMD/PowerShell) de forma invisible.
*   **Totalmente en Segundo Plano:** Al cerrar la ventana, la aplicación se minimiza a la bandeja del sistema (System Tray) junto al reloj, consumiendo mínimos recursos.
*   **Inicio Automático:** Se integra de forma nativa e invisible con el arranque de Windows para que tus atajos estén siempre listos al encender la PC.
*   **Portable:** Los atajos se guardan en un archivo `.json` junto al ejecutable. ¡Puedes llevar la carpeta en un USB a cualquier PC!

## 📥 Instalación y Uso (Usuarios)

No necesitas instalar Python ni usar la consola. Sigue estos pasos:

1. Ve a la sección de [Releases](https://github.com/antioscar/Keybind2000Oppenheimer/releases) en la derecha de esta página.
2. Descarga el archivo **`KeyBinder.zip`** de la última versión.
3. Descomprime la carpeta en el lugar que prefieras (ej. en tus Documentos).
4. Haz doble clic en **`KeyBinder.exe`**.
5. ¡Crea tus atajos! Al darle a la "X" para cerrar, la app se minimizará a la barra de tareas.

## 🛠️ Para Desarrolladores

Si quieres modificar el código fuente, la aplicación está construida enteramente en Python usando `customtkinter` para la interfaz gráfica y `keyboard` para la intercepción de eventos.

### Requisitos
*   Python 3.10+
*   Windows OS

### Configuración del Entorno
```powershell
# Clonar el repositorio
git clone https://github.com/antioscar/Keybind2000Oppenheimer.git
cd Keybind2000Oppenheimer

# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo desarrollo
python main.py
```

### Compilar el Ejecutable (PyInstaller)
Si haces cambios y quieres generar tu propio `.exe`:
```powershell
pyinstaller --noconfirm --onedir --windowed --name "KeyBinder" main.py
```
El resultado estará en la carpeta `dist/KeyBinder`.

## 📜 Licencia
Este proyecto es de código abierto y de uso libre.
