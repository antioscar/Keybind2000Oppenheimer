"""
tray_icon.py — Módulo para gestionar el icono en la bandeja del sistema (System Tray).

Maneja la minimización de la app y proporciona un menú contextual.
"""

import threading
from typing import Callable
from PIL import Image, ImageDraw, ImageFont
import pystray
from pystray import MenuItem as item


class TrayManager:
    """Maneja el ciclo de vida del icono en el System Tray."""

    def __init__(
        self,
        on_show: Callable[[], None],
        on_quit: Callable[[], None],
    ):
        """
        Inicializa el gestor del tray.

        Args:
            on_show: Función a llamar cuando el usuario quiere abrir la app.
            on_quit: Función a llamar cuando el usuario quiere cerrar la app por completo.
        """
        self.on_show = on_show
        self.on_quit = on_quit
        self.icon: pystray.Icon | None = None
        self._thread: threading.Thread | None = None

    def _create_image(self) -> Image.Image:
        """Genera un icono genérico con la letra 'K'."""
        width = 64
        height = 64
        color1 = "#000000"
        color2 = "#00B4FF"
        
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        
        # Borde
        dc.rectangle(
            (0, 0, width - 1, height - 1),
            outline=color2,
            width=3
        )
        
        # Letra 'K'
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

        # Approximate centering
        bbox = dc.textbbox((0, 0), "K", font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        x = (width - tw) / 2
        y = (height - th) / 2 - 4
        
        dc.text((x, y), "K", fill=color2, font=font)
        
        return image

    def _setup_icon(self):
        """Configura y arranca el icono."""
        menu = pystray.Menu(
            item('Abrir KeyBinder', self._handle_show, default=True),
            item('Salir completamente', self._handle_quit)
        )
        
        self.icon = pystray.Icon(
            "KeyBinder",
            self._create_image(),
            "KeyBinder - Gestor de Atajos",
            menu=menu
        )
        self.icon.run()

    def start(self):
        """Muestra el icono en el system tray en un hilo separado."""
        if self._thread and self._thread.is_alive():
            return
            
        self._thread = threading.Thread(target=self._setup_icon, daemon=True)
        self._thread.start()

    def stop(self):
        """Detiene y oculta el icono."""
        if self.icon:
            self.icon.stop()
            self.icon = None

    def _handle_show(self, icon, item):
        """Callback cuando se selecciona 'Abrir' o se hace doble clic."""
        self.on_show()

    def _handle_quit(self, icon, item):
        """Callback cuando se selecciona 'Salir'."""
        self.on_quit()
