"""
components.py — Widgets personalizados estilo Logitech G HUB para KeyBinder.
"""

import customtkinter as ctk
from typing import Callable, Optional

from gui.theme import *
from gui.icon_manager import icon, icon_font, FONT_AWESOME_SOLID, FONT_AWESOME_REGULAR
from core.keybind_manager import ACTION_TYPES


class PrimaryButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        text: str = "",
        icon_name: str = None,
        color: str = ACCENT_PRIMARY,
        hover_color: str = ACCENT_SECONDARY,
        text_color: str = TEXT_ON_ACCENT,
        width: int = 140,
        height: int = BUTTON_HEIGHT,
        command: Callable = None,
        **kwargs,
    ):
        display_text = f"{icon(icon_name)}  {text}" if icon_name else text
        super().__init__(
            master,
            text=display_text,
            font=FONT_BUTTON,
            fg_color=color,
            hover_color=hover_color,
            text_color=text_color,
            width=width,
            height=height,
            command=command,
            corner_radius=CORNER_RADIUS,
            border_width=0,
            **kwargs,
        )


class SecondaryButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        text: str = "",
        border_color: str = BORDER_DEFAULT,
        text_color: str = TEXT_SECONDARY,
        hover_color: str = BG_CARD_HOVER,
        width: int = 100,
        height: int = BUTTON_HEIGHT,
        command: Callable = None,
        **kwargs,
    ):
        super().__init__(
            master,
            text=text,
            font=FONT_BUTTON,
            fg_color="transparent",
            hover_color=hover_color,
            text_color=text_color,
            border_color=border_color,
            border_width=1,
            width=width,
            height=height,
            command=command,
            corner_radius=CORNER_RADIUS,
            **kwargs,
        )


class IconButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        icon_name: str,
        text_color: str = TEXT_SECONDARY,
        hover_color: str = BG_CARD_HOVER,
        hover_text_color: str = TEXT_PRIMARY,
        width: int = 32,
        height: int = 28,
        command: Callable = None,
        **kwargs,
    ):
        super().__init__(
            master,
            text=icon(icon_name),
            font=(icon_font(icon_name), 14),
            fg_color="transparent",
            hover_color=hover_color,
            text_color=text_color,
            width=width,
            height=height,
            command=command,
            corner_radius=CORNER_RADIUS_SM,
            border_width=0,
            **kwargs,
        )


class ToggleSwitch(ctk.CTkSwitch):
    def __init__(self, master, initial: bool = True, command: Callable = None, **kwargs):
        self._var = ctk.BooleanVar(value=initial)
        super().__init__(
            master,
            text="",
            variable=self._var,
            onvalue=True,
            offvalue=False,
            command=command,
            width=36,
            height=18,
            switch_width=32,
            switch_height=16,
            fg_color=TOGGLE_BG_OFF,
            progress_color=ACCENT_PRIMARY,
            button_color=TEXT_SECONDARY,
            button_hover_color=ACCENT_PRIMARY,
            **kwargs,
        )

    @property
    def is_on(self) -> bool:
        return self._var.get()


class HeaderBar(ctk.CTkFrame):
    def __init__(self, master, on_add_click: Callable = None, **kwargs):
        super().__init__(
            master,
            fg_color=BG_SECONDARY,
            corner_radius=0,
            height=52,
            **kwargs,
        )
        self.pack_propagate(False)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=PADDING_LG, pady=(0, 0))
        inner.pack_configure(expand=True)

        title_frame = ctk.CTkFrame(inner, fg_color="transparent")
        title_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_frame,
            text="KEYBINDER",
            font=FONT_HEADER,
            text_color=TEXT_PRIMARY,
        ).pack(side="left", anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Gestor de Atajos",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY,
        ).pack(side="left", anchor="w", padx=(10, 0))

        add_btn = PrimaryButton(
            inner,
            text="Nuevo Atajo",
            icon_name="add",
            width=150,
            height=BUTTON_HEIGHT,
            command=on_add_click,
        )
        add_btn.pack(side="right", anchor="e")


class KeybindCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        keybind_data: dict,
        on_edit: Callable = None,
        on_delete: Callable = None,
        on_toggle: Callable = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=BG_CARD,
            corner_radius=CORNER_RADIUS,
            border_width=0,
            height=CARD_HEIGHT,
            **kwargs,
        )
        self.pack_propagate(False)

        self.keybind_data = keybind_data
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_toggle = on_toggle
        is_enabled = keybind_data.get("enabled", True)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=PADDING_MD, pady=(0, 0))
        content.pack_configure(expand=True)

        # ── Left: name + action type ──
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="y", expand=True, anchor="w")

        name_color = TEXT_PRIMARY if is_enabled else TEXT_MUTED

        name_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_row.pack(anchor="w")

        ctk.CTkLabel(
            name_row,
            text=keybind_data.get("name", "Sin nombre"),
            font=FONT_SUBTITLE,
            text_color=name_color,
            anchor="w",
        ).pack(side="left")

        if keybind_data.get("is_default", False):
            ctk.CTkLabel(
                name_row,
                text="SISTEMA",
                font=FONT_BADGE,
                text_color=TEXT_MUTED,
                fg_color=BG_INPUT,
                corner_radius=CORNER_RADIUS_SM,
                padx=4,
            ).pack(side="left", padx=(8, 0))

        action_type = keybind_data.get("action_type", "launch_app")
        action_color = ACTION_COLORS.get(action_type, ACCENT_PRIMARY)
        action_icon_name = ACTION_ICONS.get(action_type, "")
        action_color_display = action_color if is_enabled else TEXT_MUTED

        action_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        action_row.pack(anchor="w", pady=(1, 0))

        ctk.CTkLabel(
            action_row,
            text=icon(action_icon_name),
            font=(icon_font(action_icon_name), 10),
            text_color=action_color_display,
        ).pack(side="left")

        ctk.CTkLabel(
            action_row,
            text=f"  {ACTION_TYPES.get(action_type, action_type)}",
            font=FONT_SMALL,
            text_color=action_color_display,
            anchor="w",
        ).pack(side="left")

        value_text = keybind_data.get("action_value", "")
        if len(value_text) > 30:
            value_text = value_text[:27] + "..."
        if value_text:
            ctk.CTkLabel(
                action_row,
                text=f"  \u2192  {value_text}",
                font=FONT_SMALL,
                text_color=TEXT_SECONDARY if is_enabled else TEXT_MUTED,
                anchor="w",
            ).pack(side="left")

        # ── Center: hotkey ──
        hotkey_text = keybind_data.get("hotkey", "").upper()
        if hotkey_text:
            ctk.CTkLabel(
                content,
                text=f"  {hotkey_text}  ",
                font=FONT_HOTKEY,
                text_color=ACCENT_PRIMARY if is_enabled else TEXT_MUTED,
                fg_color=BG_INPUT,
                corner_radius=CORNER_RADIUS_SM,
            ).pack(side="left", padx=PADDING_MD)

        # ── Right: toggle + actions ──
        actions_frame = ctk.CTkFrame(content, fg_color="transparent")
        actions_frame.pack(side="right", fill="y")

        toggle = ToggleSwitch(
            actions_frame,
            initial=is_enabled,
            command=self._handle_toggle,
        )
        toggle.pack(side="left", padx=(0, PADDING_SM))

        IconButton(
            actions_frame,
            icon_name="edit",
            command=self._handle_edit,
        ).pack(side="left", padx=1)

        IconButton(
            actions_frame,
            icon_name="delete",
            text_color="#555555",
            hover_text_color=ACCENT_DANGER,
            command=self._handle_delete,
        ).pack(side="left", padx=1)

        self.bind("<Enter>", lambda e: self.configure(fg_color=BG_CARD_HOVER))
        self.bind("<Leave>", lambda e: self.configure(fg_color=BG_CARD))

    def _handle_edit(self):
        if self.on_edit:
            self.on_edit(self.keybind_data)

    def _handle_delete(self):
        if self.on_delete:
            self.on_delete(self.keybind_data)

    def _handle_toggle(self):
        if self.on_toggle:
            self.on_toggle(self.keybind_data)


class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=BG_SECONDARY,
            corner_radius=0,
            height=28,
            **kwargs,
        )
        self.pack_propagate(False)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=PADDING_LG, pady=2)

        self.status_label = ctk.CTkLabel(
            inner,
            text=f"{icon('status_ok')}  Listener activo",
            font=FONT_SMALL,
            text_color=ACCENT_PRIMARY,
        )
        self.status_label.pack(side="left")

        self.count_label = ctk.CTkLabel(
            inner,
            text="0 atajos activos",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY,
        )
        self.count_label.pack(side="right")

    def update_status(self, active_count: int, total_count: int, listener_ok: bool = True):
        if listener_ok:
            self.status_label.configure(
                text=f"{icon('status_ok')}  Listener activo",
                text_color=ACCENT_PRIMARY,
            )
        else:
            self.status_label.configure(
                text=f"{icon('status_off')}  Listener inactivo",
                text_color=ACCENT_DANGER,
            )
        self.count_label.configure(
            text=f"{active_count} de {total_count} atajos activos",
        )


class EmptyState(ctk.CTkFrame):
    def __init__(self, master, on_add_click: Callable = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        ctk.CTkLabel(
            self,
            text=icon("keyboard"),
            font=(FONT_AWESOME_REGULAR, 48),
            text_color=TEXT_MUTED,
        ).pack(pady=(80, 12))

        ctk.CTkLabel(
            self,
            text="No hay atajos configurados",
            font=FONT_SUBTITLE,
            text_color=TEXT_SECONDARY,
        ).pack(pady=(0, 2))

        ctk.CTkLabel(
            self,
            text="Crea tu primer atajo de teclado para empezar",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
        ).pack(pady=(0, 16))

        PrimaryButton(
            self,
            text="Crear Primer Atajo",
            icon_name="add",
            width=200,
            height=40,
            command=on_add_click,
        ).pack()
