"""
theme.py — Estilo Logitech G HUB para KeyBinder.

Paleta oscura minimalista con acento azul, tipografía limpia
y dimensiones pensadas para una interfaz de escritorio moderna.
"""

from gui.icon_manager import FONT_AWESOME_SOLID, FONT_AWESOME_REGULAR

# ═══════════════════════════════════════════════════════════════════
#  PALETA DE COLORES (G HUB inspired)
# ═══════════════════════════════════════════════════════════════════

BG_PRIMARY = "#000000"
BG_SECONDARY = "#0D0D0D"
BG_CARD = "#1A1A1A"
BG_CARD_HOVER = "#242424"
BG_INPUT = "#1E1E1E"
BG_DIALOG = "#0D0D0D"

ACCENT_PRIMARY = "#00B4FF"
ACCENT_SECONDARY = "#009DEC"
ACCENT_DANGER = "#E81123"
ACCENT_WARNING = "#FF8C00"
ACCENT_INFO = "#00B4FF"

TEXT_PRIMARY = "#F0F0F0"
TEXT_SECONDARY = "#8A8A8A"
TEXT_MUTED = "#555555"
TEXT_ON_ACCENT = "#FFFFFF"

BORDER_DEFAULT = "#2A2A2A"
BORDER_ACTIVE = "#00B4FF"
BORDER_FOCUS = "#00B4FF"

TOGGLE_BG_ON = "#003355"
TOGGLE_BG_OFF = "#2A2A2A"

# ═══════════════════════════════════════════════════════════════════
#  TIPOGRAFÍA
# ═══════════════════════════════════════════════════════════════════

FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

FONT_TITLE = (FONT_FAMILY, 20, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 13, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_SMALL = (FONT_FAMILY, 10)
FONT_HOTKEY = (FONT_MONO, 13, "bold")
FONT_BUTTON = (FONT_FAMILY, 11, "bold")
FONT_HEADER = (FONT_FAMILY, 18, "bold")
FONT_BADGE = (FONT_MONO, 9)

# ═══════════════════════════════════════════════════════════════════
#  DIMENSIONES Y ESPACIADO
# ═══════════════════════════════════════════════════════════════════

CORNER_RADIUS = 6
CORNER_RADIUS_SM = 4
CORNER_RADIUS_LG = 10

PADDING_SM = 6
PADDING_MD = 12
PADDING_LG = 20
PADDING_XL = 30

CARD_HEIGHT = 64
BUTTON_HEIGHT = 32
BUTTON_WIDTH = 100

WINDOW_WIDTH = 820
WINDOW_HEIGHT = 660

DIALOG_WIDTH = 480
DIALOG_HEIGHT = 540

# ═══════════════════════════════════════════════════════════════════
#  MAPEO DE COLORES E ICONOS POR TIPO DE ACCIÓN
# ═══════════════════════════════════════════════════════════════════

ACTION_ICONS = {
    "launch_app": "app",
    "open_url": "globe",
    "type_text": "text",
    "run_command": "command",
}

ACTION_COLORS = {
    "launch_app": ACCENT_INFO,
    "open_url": ACCENT_PRIMARY,
    "type_text": ACCENT_SECONDARY,
    "run_command": ACCENT_WARNING,
}
