"""
main.py — Punto de entrada de KeyBinder.

Inicializa la aplicación y ejecuta el bucle principal de eventos.
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el path
# para que los imports relativos funcionen correctamente.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gui.app import KeyBinderApp


def main():
    """Punto de entrada principal de la aplicación."""
    print("=" * 50)
    print("  KEYBINDER - Gestor de Atajos de Teclado")
    print("=" * 50)
    print()

    start_in_tray = "--tray" in sys.argv
    app = KeyBinderApp(start_in_tray=start_in_tray)
    app.mainloop()

    print("\n[KeyBinder] Aplicación cerrada correctamente.")


if __name__ == "__main__":
    main()
