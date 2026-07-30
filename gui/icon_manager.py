"""
icon_manager.py — Carga y gestión de Font Awesome para KeyBinder.

Descarga las fuentes en el primer inicio y las registra en Windows
para que estén disponibles en toda la aplicación.
"""

import ctypes
import os
import urllib.request
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from core.utils import get_base_dir

ASSETS_DIR = get_base_dir() / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

FONT_AWESOME_SOLID = "Font Awesome 6 Free Solid"
FONT_AWESOME_REGULAR = "Font Awesome 6 Free Regular"

FONT_URLS = {
    "fa-solid-900.ttf": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/webfonts/fa-solid-900.ttf",
    "fa-regular-400.ttf": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/webfonts/fa-regular-400.ttf",
}

ICONS = {
    "add": "\uf067",
    "edit": "\uf044",
    "delete": "\uf2ed",
    "save": "\uf0c7",
    "cancel": "\uf00d",
    "capture": "\uf192",
    "app": "\uf2d0",
    "globe": "\uf0ac",
    "text": "\uf031",
    "command": "\uf120",
    "system": "\uf013",
    "keyboard": "\uf11c",
    "status_ok": "\uf058",
    "status_off": "\uf111",
    "arrow_right": "\uf061",
    "search": "\uf002",
}

REGULAR_ICONS = {"edit", "delete", "capture", "app", "keyboard", "status_ok", "status_off"}

_fonts_loaded = False


def icon(name: str) -> str:
    return ICONS.get(name, "")


def icon_font(name: str) -> str:
    return FONT_AWESOME_REGULAR if name in REGULAR_ICONS else FONT_AWESOME_SOLID


def _get_font_path(filename: str) -> Path:
    return FONTS_DIR / filename


def _ensure_fonts() -> bool:
    os.makedirs(FONTS_DIR, exist_ok=True)
    ok = True
    for filename, url in FONT_URLS.items():
        fp = _get_font_path(filename)
        if not fp.exists():
            try:
                urllib.request.urlretrieve(url, fp)
            except Exception:
                ok = False
    return ok


def load_fonts() -> bool:
    global _fonts_loaded
    if _fonts_loaded:
        return True

    _ensure_fonts()

    FR_PRIVATE = 0x10
    ok = True
    for filename in FONT_URLS:
        fp = _get_font_path(filename)
        if fp.exists():
            try:
                if ctypes.windll.gdi32.AddFontResourceExW(str(fp), FR_PRIVATE, 0) == 0:
                    ok = False
            except Exception:
                ok = False
    _fonts_loaded = ok
    return ok
