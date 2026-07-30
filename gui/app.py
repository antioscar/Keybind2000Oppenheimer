"""
app.py — Ventana principal de KeyBinder.
"""

import customtkinter as ctk
from typing import Optional

from gui.theme import *
from gui.components import HeaderBar, KeybindCard, StatusBar, EmptyState
from gui.dialogs import KeybindDialog, ConfirmDialog
from gui.icon_manager import load_fonts
from core.keybind_manager import KeybindManager
from core.listener import KeybindListener
from core.tray_icon import TrayManager
from core import startup_manager


class KeyBinderApp(ctk.CTk):
    def __init__(self, start_in_tray=False):
        super().__init__()

        if start_in_tray:
            self.withdraw()

        # Activar arranque con Windows automáticamente
        startup_manager.enable_startup()

        load_fonts()

        self.title("KeyBinder — Gestor de Atajos")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(700, 500)
        self.configure(fg_color=BG_PRIMARY)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (WINDOW_WIDTH // 2)
        y = (self.winfo_screenheight() // 2) - (WINDOW_HEIGHT // 2)
        self.geometry(f"+{x}+{y}")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.manager = KeybindManager()
        self.listener = KeybindListener()
        self.tray = TrayManager(on_show=self._show_window, on_quit=self._quit_app)

        self._build_ui()
        self._refresh_list()
        self._refresh_listener()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if start_in_tray:
            self.tray.start()

    def _build_ui(self):
        self.header = HeaderBar(
            self,
            on_add_click=self._open_create_dialog,
        )
        self.header.pack(fill="x")

        self.main_frame = ctk.CTkFrame(self, fg_color=BG_PRIMARY, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # ── Column Headers ──
        col_headers = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=24)
        col_headers.pack(fill="x", padx=(PADDING_LG + PADDING_MD, PADDING_LG + PADDING_MD), pady=(PADDING_MD, 0))
        col_headers.pack_propagate(False)

        ctk.CTkLabel(
            col_headers,
            text="NOMBRE",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(side="left", anchor="w")

        # Right-side labels packed in reverse order (right to left)
        ctk.CTkLabel(
            col_headers,
            text="ACCIONES",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            anchor="e",
        ).pack(side="right")

        ctk.CTkLabel(
            col_headers,
            text="ESTADO",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            anchor="e",
        ).pack(side="right", padx=(0, 20))

        ctk.CTkLabel(
            col_headers,
            text="ATAJO",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            anchor="e",
        ).pack(side="right", padx=(0, 16))

        self.col_headers = col_headers

        # ── Scrollable List ──
        self.scrollable = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color=BG_PRIMARY,
            scrollbar_button_color=BG_SECONDARY,
            scrollbar_button_hover_color=TEXT_MUTED,
            corner_radius=0,
        )
        self.scrollable.pack(fill="both", expand=True, padx=PADDING_LG, pady=(PADDING_SM, PADDING_MD))

        self.empty_state: Optional[EmptyState] = None

        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill="x", side="bottom")

    def _refresh_list(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        if self.empty_state:
            self.empty_state.destroy()
            self.empty_state = None

        keybinds = self.manager.get_all()

        if not keybinds:
            self.empty_state = EmptyState(
                self.scrollable,
                on_add_click=self._open_create_dialog,
            )
            self.empty_state.pack(fill="both", expand=True)
        else:
            for kb in keybinds:
                card = KeybindCard(
                    self.scrollable,
                    keybind_data=kb,
                    on_edit=self._open_edit_dialog,
                    on_delete=self._confirm_delete,
                    on_toggle=self._toggle_keybind,
                )
                card.pack(fill="x", pady=(0, PADDING_SM))

        total = len(keybinds)
        active = len(self.manager.get_enabled())
        self.status_bar.update_status(active, total)

    def _refresh_listener(self):
        enabled = self.manager.get_enabled()
        count = self.listener.refresh(enabled)
        total = len(self.manager.get_all())
        self.status_bar.update_status(count, total)

    # ── CRUD: Crear ──

    def _open_create_dialog(self):
        KeybindDialog(
            master=self,
            on_save=self._on_create_save,
            capture_hotkey_fn=self.listener.capture_hotkey,
        )

    def _on_create_save(self, data: dict):
        try:
            self.manager.add_keybind(
                name=data["name"],
                hotkey=data["hotkey"],
                action_type=data["action_type"],
                action_value=data["action_value"],
            )
            self._refresh_list()
            self._refresh_listener()
        except ValueError as e:
            print(f"[App] Error al crear keybind: {e}")

    # ── CRUD: Editar ──

    def _open_edit_dialog(self, keybind_data: dict):
        kb_id = keybind_data["id"]

        def on_edit_save(data: dict):
            self._on_edit_save(kb_id, data)

        KeybindDialog(
            master=self,
            on_save=on_edit_save,
            capture_hotkey_fn=self.listener.capture_hotkey,
            keybind_data=keybind_data,
        )

    def _on_edit_save(self, keybind_id: str, data: dict):
        try:
            self.manager.update_keybind(
                keybind_id=keybind_id,
                name=data["name"],
                hotkey=data["hotkey"],
                action_type=data["action_type"],
                action_value=data["action_value"],
            )
            self._refresh_list()
            self._refresh_listener()
        except ValueError as e:
            print(f"[App] Error al editar keybind: {e}")

    # ── CRUD: Eliminar ──

    def _confirm_delete(self, keybind_data: dict):
        name = keybind_data.get("name", "Sin nombre")
        kb_id = keybind_data["id"]

        ConfirmDialog(
            master=self,
            title="Eliminar Atajo",
            message=f'Eliminar "{name}"?',
            detail="Esta accion no se puede deshacer. "
                   "El atajo dejara de funcionar inmediatamente.",
            confirm_text="Eliminar",
            confirm_color=ACCENT_DANGER,
            on_confirm=lambda: self._on_delete_confirm(kb_id),
        )

    def _on_delete_confirm(self, keybind_id: str):
        self.manager.delete_keybind(keybind_id)
        self._refresh_list()
        self._refresh_listener()

    # ── Toggle On/Off ──

    def _toggle_keybind(self, keybind_data: dict):
        self.manager.toggle_keybind(keybind_data["id"])
        self._refresh_list()
        self._refresh_listener()

    # ── System Tray y Cierre ──

    def _show_window(self):
        """Restaura la ventana desde el system tray."""
        self.deiconify()
        self.tray.stop()

    def _quit_app(self):
        """Cierra completamente la aplicación."""
        self.listener.shutdown()
        self.tray.stop()
        self.destroy()

    def _on_close(self):
        """Oculta la ventana y la manda al system tray."""
        self.withdraw()
        self.tray.start()
