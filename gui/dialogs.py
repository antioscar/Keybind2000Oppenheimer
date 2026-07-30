"""
dialogs.py — Diálogos modales estilo Logitech G HUB para KeyBinder.
"""

import customtkinter as ctk
from typing import Callable

from gui.theme import *
from gui.components import PrimaryButton, SecondaryButton, IconButton
from gui.icon_manager import icon, icon_font, FONT_AWESOME_SOLID, FONT_AWESOME_REGULAR
from core.keybind_manager import ACTION_TYPES
from core.app_scanner import AppScanner

USER_ACTION_TYPES = dict(ACTION_TYPES)

_app_scanner = AppScanner()


class KeybindDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        on_save: Callable,
        capture_hotkey_fn: Callable,
        keybind_data: dict = None,
        title: str = None,
    ):
        super().__init__(master)

        self.on_save = on_save
        self.capture_hotkey_fn = capture_hotkey_fn
        self.keybind_data = keybind_data
        self.result = None
        self._app_names: list[str] = []
        self._app_scanner = _app_scanner
        self._selected_app_path = None

        is_edit = keybind_data is not None
        dialog_title = title or ("Editar Atajo" if is_edit else "Nuevo Atajo")

        self.title(dialog_title)
        self.geometry(f"{DIALOG_WIDTH}x{DIALOG_HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=BG_DIALOG)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (DIALOG_WIDTH // 2)
        y = (self.winfo_screenheight() // 2) - (DIALOG_HEIGHT // 2)
        self.geometry(f"+{x}+{y}")

        self.transient(master)
        self.grab_set()

        self._build_ui(is_edit)

        if is_edit and keybind_data:
            self._populate_fields(keybind_data)

        self.name_entry.focus_set()
        self.bind("<Escape>", lambda e: self.destroy())
        self._start_app_scan()

    def _build_ui(self, is_edit: bool):
        # ── Header ──
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=PADDING_LG, pady=(PADDING_LG, PADDING_SM))

        header_text = "Editar Atajo" if is_edit else "Nuevo Atajo"
        ctk.CTkLabel(
            header_frame,
            text=header_text,
            font=FONT_TITLE,
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkFrame(
            self, fg_color=BORDER_DEFAULT, height=1, corner_radius=0
        ).pack(fill="x", padx=PADDING_LG, pady=(0, PADDING_MD))

        # ── Form ──
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=PADDING_LG, pady=0)

        self._form = form

        self._create_label(form, "NOMBRE DEL ATAJO")
        self.name_entry = self._create_entry(
            form, placeholder="Ej: Abrir navegador, Texto rapido..."
        )

        self._create_label(form, "COMBINACION DE TECLAS", pady_top=PADDING_MD)
        hotkey_frame = ctk.CTkFrame(form, fg_color="transparent")
        hotkey_frame.pack(fill="x", pady=(2, 0))

        self.hotkey_entry = ctk.CTkEntry(
            hotkey_frame,
            placeholder_text="Ej: ctrl+shift+t",
            font=FONT_HOTKEY,
            fg_color=BG_INPUT,
            border_color=BORDER_DEFAULT,
            border_width=1,
            text_color=ACCENT_PRIMARY,
            corner_radius=CORNER_RADIUS,
            height=36,
        )
        self.hotkey_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.capture_btn = PrimaryButton(
            hotkey_frame,
            text="Capturar",
            icon_name="capture",
            color=BG_INPUT,
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            width=110,
            height=36,
            command=self._start_capture,
        )
        self.capture_btn.pack(side="right")

        self._create_label(form, "TIPO DE ACCION", pady_top=PADDING_MD)
        action_options = list(USER_ACTION_TYPES.values())
        self.action_type_var = ctk.StringVar(value=action_options[0])

        self.action_dropdown = ctk.CTkOptionMenu(
            form,
            variable=self.action_type_var,
            values=action_options,
            font=FONT_BODY,
            fg_color=BG_INPUT,
            button_color=TEXT_SECONDARY,
            button_hover_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_hover_color=BG_CARD_HOVER,
            dropdown_text_color=TEXT_PRIMARY,
            text_color=TEXT_PRIMARY,
            corner_radius=CORNER_RADIUS,
            height=34,
            command=self._on_action_type_changed,
        )
        self.action_dropdown.pack(fill="x", pady=(2, 0))

        self._value_label = self._create_label(
            form, "VALOR DE LA ACCION", pady_top=PADDING_MD
        )

        self.value_container = ctk.CTkFrame(form, fg_color="transparent")
        self.value_container.pack(fill="x", pady=(2, 0))

        self.value_entry = ctk.CTkEntry(
            self.value_container,
            placeholder_text="Ruta, URL, texto o comando...",
            font=FONT_BODY,
            fg_color=BG_INPUT,
            border_color=BORDER_DEFAULT,
            border_width=1,
            text_color=TEXT_PRIMARY,
            corner_radius=CORNER_RADIUS,
            height=34,
        )
        self.value_entry.pack(fill="x")

        self.app_combobox = ctk.CTkComboBox(
            self.value_container,
            values=["Escaneando aplicaciones..."],
            font=FONT_BODY,
            fg_color=BG_INPUT,
            border_color=BORDER_DEFAULT,
            border_width=1,
            text_color=TEXT_PRIMARY,
            button_color=TEXT_SECONDARY,
            button_hover_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_hover_color=BG_CARD_HOVER,
            dropdown_text_color=TEXT_PRIMARY,
            corner_radius=CORNER_RADIUS,
            height=34,
            command=self._on_app_selected,
        )

        self.value_hint = ctk.CTkLabel(
            form,
            text="Selecciona una aplicacion de la lista o escribe la ruta",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.value_hint.pack(anchor="w", pady=(2, 0))

        # ── Buttons ──
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=PADDING_LG, pady=PADDING_LG)

        SecondaryButton(
            buttons_frame,
            text="Cancelar",
            width=110,
            height=36,
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        save_text = "Actualizar" if is_edit else "Crear Atajo"
        PrimaryButton(
            buttons_frame,
            text=save_text,
            icon_name="save",
            width=150,
            height=36,
            command=self._handle_save,
        ).pack(side="right")

        self._current_value_mode = "entry"

    def _create_label(self, parent, text: str, pady_top: int = 0):
        ctk.CTkLabel(
            parent,
            text=text,
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY,
            anchor="w",
        ).pack(anchor="w", pady=(pady_top, 2))

    def _create_entry(self, parent, placeholder: str = "") -> ctk.CTkEntry:
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            font=FONT_BODY,
            fg_color=BG_INPUT,
            border_color=BORDER_DEFAULT,
            border_width=1,
            text_color=TEXT_PRIMARY,
            corner_radius=CORNER_RADIUS,
            height=34,
        )
        entry.pack(fill="x", pady=(2, 0))
        return entry

    def _populate_fields(self, data: dict):
        self.name_entry.insert(0, data.get("name", ""))
        self.hotkey_entry.insert(0, data.get("hotkey", ""))

        action_type = data.get("action_type", "launch_app")
        display_name = USER_ACTION_TYPES.get(action_type, USER_ACTION_TYPES["launch_app"])
        self.action_type_var.set(display_name)

        action_value = data.get("action_value", "")

        if action_type == "launch_app":
            self._switch_to_combobox()
            self.app_combobox.set(action_value)
        else:
            self._switch_to_entry()
            self.value_entry.insert(0, action_value)

        self._on_action_type_changed(display_name)

    def _on_action_type_changed(self, choice: str):
        hints = {
            USER_ACTION_TYPES["launch_app"]: "Selecciona una aplicacion de la lista o escribe la ruta",
            USER_ACTION_TYPES["open_url"]: "Ingresa la URL completa (ej: https://google.com)",
            USER_ACTION_TYPES["type_text"]: "Ingresa el texto que se escribira automaticamente",
            USER_ACTION_TYPES["run_command"]: "Ingresa el comando a ejecutar (ej: notepad, calc)",
        }
        self.value_hint.configure(text=hints.get(choice, ""))

        if choice == USER_ACTION_TYPES["launch_app"]:
            self._switch_to_combobox()
        else:
            self._switch_to_entry()

    def _switch_to_combobox(self):
        if self._current_value_mode == "combobox":
            return
        self.value_entry.pack_forget()
        self.app_combobox.pack(fill="x")
        if hasattr(self, "_app_scanner") and self._app_scanner.is_scanned:
            names = self._app_scanner.get_app_names()
            if names:
                self.app_combobox.configure(values=names)
                if self.app_combobox.get() in ("Escaneando aplicaciones...", ""):
                    self.app_combobox.set(names[0])
        self._current_value_mode = "combobox"

    def _switch_to_entry(self):
        if self._current_value_mode == "entry":
            return
        self.app_combobox.pack_forget()
        self.value_entry.pack(fill="x")
        self._current_value_mode = "entry"

    def _on_app_selected(self, choice: str):
        path = self._app_scanner.get_path_for_name(choice)
        self._selected_app_path = path if path else choice

    def _start_app_scan(self):
        if self._app_scanner.is_scanned:
            self._update_app_combobox()
            return

        def on_scan_complete(apps):
            self.after(0, self._update_app_combobox)

        self._app_scanner.scan(callback=on_scan_complete)

    def _update_app_combobox(self):
        try:
            names = self._app_scanner.get_app_names()
            if names:
                self.app_combobox.configure(values=names)
                current = self.app_combobox.get()
                if current in ("Escaneando aplicaciones...", "") or current not in names:
                    if self._current_value_mode == "combobox":
                        self.app_combobox.set(names[0])
            else:
                self.app_combobox.configure(values=["No se encontraron aplicaciones"])
        except Exception:
            pass

    def _start_capture(self):
        self.capture_btn.configure(
            text="Esperando...",
            fg_color=BG_CARD,
            text_color=ACCENT_WARNING,
        )
        self.hotkey_entry.delete(0, "end")
        self.hotkey_entry.insert(0, "Esperando...")
        self.hotkey_entry.configure(text_color=ACCENT_WARNING)

        def on_captured(hotkey_str: str):
            self.after(0, lambda: self._on_hotkey_captured(hotkey_str))

        self.capture_hotkey_fn(on_captured)

    def _on_hotkey_captured(self, hotkey_str: str):
        self.hotkey_entry.delete(0, "end")
        if hotkey_str:
            self.hotkey_entry.insert(0, hotkey_str)
            self.hotkey_entry.configure(text_color=ACCENT_PRIMARY)
        else:
            self.hotkey_entry.configure(text_color=TEXT_PRIMARY)

        self.capture_btn.configure(
            text=f"{icon('capture')}  Capturar",
            fg_color=BG_INPUT,
            text_color=TEXT_PRIMARY,
        )

    def _handle_save(self):
        name = self.name_entry.get().strip()
        hotkey = self.hotkey_entry.get().strip()

        display_name = self.action_type_var.get()
        action_type = "launch_app"
        for key, val in USER_ACTION_TYPES.items():
            if val == display_name:
                action_type = key
                break

        if self._current_value_mode == "combobox":
            selected_name = self.app_combobox.get().strip()
            path = self._app_scanner.get_path_for_name(selected_name)
            action_value = path if path else selected_name
        else:
            action_value = self.value_entry.get().strip()

        has_error = False
        if not name:
            self.name_entry.configure(border_color="#E81123")
            has_error = True
        else:
            self.name_entry.configure(border_color=BORDER_DEFAULT)

        if not hotkey or hotkey == "Esperando...":
            self.hotkey_entry.configure(border_color="#E81123")
            has_error = True
        else:
            self.hotkey_entry.configure(border_color=BORDER_DEFAULT)

        if not action_value:
            if self._current_value_mode == "combobox":
                self.app_combobox.configure(border_color="#E81123")
            else:
                self.value_entry.configure(border_color="#E81123")
            has_error = True
        else:
            if self._current_value_mode == "combobox":
                self.app_combobox.configure(border_color=BORDER_DEFAULT)
            else:
                self.value_entry.configure(border_color=BORDER_DEFAULT)

        if has_error:
            return

        self.result = {
            "name": name,
            "hotkey": hotkey,
            "action_type": action_type,
            "action_value": action_value,
        }
        self.on_save(self.result)
        self.destroy()


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title: str = "Confirmar",
        message: str = "Estas seguro?",
        detail: str = "",
        confirm_text: str = "Eliminar",
        confirm_color: str = ACCENT_DANGER,
        on_confirm: Callable = None,
    ):
        super().__init__(master)

        self.on_confirm = on_confirm
        self.confirmed = False

        width, height = 380, 200
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.configure(fg_color=BG_DIALOG)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        self.transient(master)
        self.grab_set()

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=PADDING_LG, pady=PADDING_LG)

        ctk.CTkLabel(
            content,
            text=message,
            font=FONT_SUBTITLE,
            text_color=TEXT_PRIMARY,
        ).pack(pady=(20, 4))

        if detail:
            ctk.CTkLabel(
                content,
                text=detail,
                font=FONT_SMALL,
                text_color=TEXT_SECONDARY,
                wraplength=340,
            ).pack(pady=(0, 12))

        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=PADDING_LG, pady=(0, PADDING_LG))

        SecondaryButton(
            buttons_frame,
            text="Cancelar",
            width=110,
            height=34,
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            buttons_frame,
            text=confirm_text,
            font=FONT_BUTTON,
            fg_color=confirm_color,
            hover_color="#AA0000",
            text_color=TEXT_ON_ACCENT,
            width=110,
            height=34,
            corner_radius=CORNER_RADIUS,
            border_width=0,
            command=self._handle_confirm,
        ).pack(side="right")

        self.bind("<Escape>", lambda e: self.destroy())

    def _handle_confirm(self):
        self.confirmed = True
        if self.on_confirm:
            self.on_confirm()
        self.destroy()
