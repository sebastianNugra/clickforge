"""ClickForge: autoclicker con ventana de bienvenida y overlay discreto.

Teclas globales:
    F8  -> capturar el punto de clic (posición actual del mouse)
    F6  -> iniciar / detener el autoclicker
"""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from pynput import keyboard

from clickforge.autoclicker import AutoClicker

# paleta estilo "vidrio oscuro"
PANEL_BG = "#17181f"
PANEL_FG = "#e8e9f0"
MUTED = "#9aa0b4"
BORDER = "#3a3d4a"
RUNNING = "#4ade80"
STOPPED = "#f87171"

OVERLAY_W = 320
CONFIG_PATH = Path.home() / ".clickforge.json"

# unidades de tiempo: clave interna -> etiqueta en la UI
UNITS = {"seconds": "segundos", "minutes": "minutos", "hours": "horas"}
# etiquetas para el ritmo: "30 clics por minuto"
RATE_UNITS = {"seconds": "por segundo", "minutes": "por minuto", "hours": "por hora"}
UNIT_SHORT = {"seconds": "s", "minutes": "min", "hours": "h"}
UNIT_SECONDS = {"seconds": 1, "minutes": 60, "hours": 3600}

MAX_CLICKS_PER_SECOND = 100.0  # límite de seguridad de la app


class ClickForgeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.withdraw()  # la ventana raíz no se ve; solo existen las "pantallas"

        self._clicker = AutoClicker()
        # ritmo: "rate_value clics por rate_unit" (por defecto 10 por segundo)
        self._rate_value: float = 10.0
        self._rate_unit: str = "seconds"  # seconds | minutes | hours
        self._duration_value = 0  # 0 = sin límite
        self._duration_unit = "seconds"  # seconds | minutes | hours

        self.guide: tk.Toplevel | None = None
        self.overlay: tk.Toplevel | None = None
        self._settings: tk.Toplevel | None = None
        self._cps_quick: tk.Entry | None = None
        self._rate_unit_label: tk.Label | None = None

        self._load_config()

        self._point_var = tk.StringVar(value="sin capturar")
        self._state_var = tk.StringVar(value="detenido")

        self._hotkeys = keyboard.GlobalHotKeys({
            "<f8>": self._on_f8,
            "<f6>": self._on_f6,
        })
        self._hotkeys.start()

        root.protocol("WM_DELETE_WINDOW", self.quit)
        self._show_guide()
        root.after(80, self._tick)

    # ---------------------------------------------------------- pantallas
    def _center(self, win: tk.Toplevel, width: int, height: int) -> None:
        """Ubica la ventana justo en el centro de la pantalla."""
        x = max(0, (win.winfo_screenwidth() - width) // 2)
        y = max(0, (win.winfo_screenheight() - height) // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def _show_guide(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("ClickForge — Bienvenido")
        self._center(win, 600, 620)
        win.resizable(False, False)
        win.configure(bg=PANEL_BG)
        win.protocol("WM_DELETE_WINDOW", self.quit)

        tk.Label(win, text="👋 Bienvenido a ClickForge", font=("Segoe UI", 17, "bold"),
                 bg=PANEL_BG, fg=PANEL_FG).pack(pady=(28, 2))
        tk.Label(win, text="Autoclicker con overlay discreto que no estorba",
                 bg=PANEL_BG, fg=MUTED).pack(pady=(0, 18))

        steps = [
            ("1.", 'Pulsa "▶ Comenzar". Esta ventana se cierra y queda una\n'
                   'barra pequeña y translúcida, siempre visible arriba.'),
            ("2.", "Coloca el mouse justo sobre el lugar donde quieres hacer clic\n"
                   "y pulsa F8 para capturar ese punto."),
            ("3.", "Pulsa F6 para empezar a hacer clics, y F6 otra vez para detener."),
            ("4.", "El ritmo se ajusta en la barra (escribe los clics en la esquina)\n"
                   "o en ⚙ Configuración: por segundo, minuto u hora.\n"
                   "Ej.: 30 clics por minuto = 1 clic cada 2 segundos."),
            ("5.", "En ⚙ también defines el tiempo de ejecución (segundos, minutos\n"
                   "u horas; 0 = sin límite) y la app se detiene sola al terminar."),
            ("6.", "Para salir: el cuadro rojo con ✗ en la esquina superior derecha."),
        ]
        box = tk.Frame(win, bg=PANEL_BG)
        box.pack(fill="x", padx=36)
        for i, (num, text) in enumerate(steps):
            tk.Label(box, text=num, font=("Segoe UI", 11, "bold"),
                     bg=PANEL_BG, fg=RUNNING).grid(row=i, column=0, sticky="nw", pady=6)
            tk.Label(box, text=text, bg=PANEL_BG, fg=PANEL_FG, justify="left").grid(
                row=i, column=1, sticky="nw", padx=8, pady=6)
        box.columnconfigure(1, weight=1)

        tk.Label(win, text="💡 La barra se puede arrastrar con el mouse; el botón ✕ rojo sale de la app.",
                 bg=PANEL_BG, fg=MUTED).pack(pady=(14, 0))

        btn = tk.Button(win, text="▶  Comenzar  (F8)", font=("Segoe UI", 12, "bold"),
                        bg=RUNNING, fg="#0b0c10", activebackground="#86efac",
                        relief="flat", padx=24, pady=8, cursor="hand2",
                        command=self._start_overlay)
        btn.pack(pady=(22, 0))

        tk.Button(win, text="⏻  Salir de ClickForge", font=("Segoe UI", 9),
                  bg=STOPPED, fg="#0b0c10", activebackground="#fca5a5",
                  relief="flat", padx=14, pady=3, cursor="hand2",
                  command=self.quit).pack(pady=(10, 0))

        self.guide = win

    def _start_overlay(self) -> None:
        """Cierra la bienvenida y muestra el overlay de vidrio."""
        if self.overlay is not None:
            return
        if self.guide is not None:
            self.guide.destroy()
            self.guide = None

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)  # sin bordes de ventana
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.88)  # efecto vidrio translúcido
        win.configure(bg=BORDER)

        panel = tk.Frame(win, bg=PANEL_BG)
        panel.pack(padx=1, pady=1)  # el padx/pady de 1px forma el borde fino

        # fila de título (también sirve para arrastrar)
        title = tk.Frame(panel, bg=PANEL_BG)
        title.pack(fill="x", padx=10, pady=(8, 4))
        self._dot = tk.Label(title, text="●", bg=PANEL_BG, fg=STOPPED, font=("Segoe UI", 9))
        self._dot.pack(side="left")
        tk.Label(title, text="  ClickForge", bg=PANEL_BG, fg=PANEL_FG,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        # esquina superior derecha: cuadro rojo con X para salir
        close_box = tk.Label(title, text="✕", bg="#e5484d", fg="white",
                             font=("Segoe UI", 11, "bold"), padx=7, pady=1,
                             cursor="hand2")
        close_box.pack(side="right")
        close_box.bind("<Button-1>", lambda _e: self.quit())

        gear = tk.Label(title, text=" ⚙ ", bg=PANEL_BG, fg=MUTED, cursor="hand2",
                        font=("Segoe UI", 9))
        gear.pack(side="right", padx=(4, 6))
        gear.bind("<Button-1>", lambda _e: self._show_settings())
        # ritmo editable directo en la esquina de la barra (en la unidad activa)
        self._cps_quick = tk.Entry(title, width=5, justify="center",
                                   bg=BORDER, fg=PANEL_FG, insertbackground=PANEL_FG,
                                   relief="flat", font=("Segoe UI", 9))
        self._cps_quick.pack(side="right", ipady=2)
        self._cps_quick.insert(0, self._rate_display())
        self._cps_quick.bind("<Return>", lambda _e: self._apply_quick_cps())
        self._cps_quick.bind("<FocusOut>", lambda _e: self._apply_quick_cps())
        self._rate_unit_label = tk.Label(
            title, text=f"clics/{UNIT_SHORT[self._rate_unit]}  ",
            bg=PANEL_BG, fg=MUTED, font=("Segoe UI", 8))
        self._rate_unit_label.pack(side="right")

        # estado
        status = tk.Frame(panel, bg=PANEL_BG)
        status.pack(fill="x", padx=10)
        tk.Label(status, text="Punto:", bg=PANEL_BG, fg=MUTED).grid(row=0, column=0, sticky="w")
        tk.Label(status, textvariable=self._point_var, bg=PANEL_BG, fg=PANEL_FG).grid(
            row=0, column=1, sticky="w", padx=6)
        tk.Label(status, text="Clics:", bg=PANEL_BG, fg=MUTED).grid(row=1, column=0, sticky="w", pady=(2, 0))
        tk.Label(status, textvariable=self._state_var, bg=PANEL_BG, fg=PANEL_FG).grid(
            row=1, column=1, sticky="w", padx=6, pady=(2, 0))
        status.columnconfigure(1, weight=1)

        # botones de respaldo (por si no quieres usar el teclado)
        buttons = tk.Frame(panel, bg=PANEL_BG)
        buttons.pack(fill="x", padx=10, pady=(8, 8))
        tk.Button(buttons, text="F8  Capturar", bg=BORDER, fg=PANEL_FG, relief="flat",
                  cursor="hand2", command=self._clicker.capture_point).pack(side="left", expand=True, fill="x")
        self._toggle_btn = tk.Button(buttons, text="F6  Iniciar", bg=BORDER, fg=PANEL_FG,
                                     relief="flat", cursor="hand2", command=self._clicker.toggle)
        self._toggle_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))

        # arrastrable desde cualquier zona del panel
        for widget in (win, panel, title, status, buttons, self._dot):
            widget.bind("<Button-1>", self._drag_start)
            widget.bind("<B1-Motion>", self._drag_move)

        x = (win.winfo_screenwidth() - OVERLAY_W) // 2
        win.geometry(f"{OVERLAY_W}x120+{x}+36")
        self.overlay = win

    # ------------------------------------------------------------- lógica
    def _show_settings(self) -> None:
        """Ventana de configuración: cantidad de clicks por segundo."""
        if self._settings is not None and self._settings.winfo_exists():
            self._settings.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("ClickForge — Configuración")
        self._center(win, 400, 380)
        win.resizable(False, False)
        win.configure(bg=PANEL_BG)
        win.attributes("-topmost", True)
        win.protocol("WM_DELETE_WINDOW", lambda: self._close_settings(win))

        tk.Label(win, text="⚙  Configuración", font=("Segoe UI", 13, "bold"),
                 bg=PANEL_BG, fg=PANEL_FG).pack(pady=(18, 12))

        # ritmo: cuántos clics por segundo / minuto / hora
        row = tk.Frame(win, bg=PANEL_BG)
        row.pack(fill="x", padx=28)
        tk.Label(row, text="Ritmo de clics:", bg=PANEL_BG, fg=PANEL_FG).pack(side="left")

        self._rate_var = tk.DoubleVar(value=self._rate_value)
        rate_spin = tk.Spinbox(row, from_=1, to=6000, increment=1, width=6,
                               textvariable=self._rate_var, command=self._apply_settings)
        rate_spin.pack(side="right")
        rate_spin.bind("<Return>", lambda _e: self._apply_settings())

        self._rate_unit_var = tk.StringVar(value=RATE_UNITS[self._rate_unit])
        rate_unit = ttk.Combobox(row, textvariable=self._rate_unit_var, state="readonly",
                                 values=list(RATE_UNITS.values()), width=12)
        rate_unit.pack(side="right", padx=6)
        rate_unit.bind("<<ComboboxSelected>>", lambda _e: self._apply_settings())

        # resultado del cálculo, para que se entienda el ritmo
        self._interval_var = tk.StringVar(value="→ " + self._interval_text())
        tk.Label(win, textvariable=self._interval_var, bg=PANEL_BG, fg=RUNNING,
                 font=("Segoe UI", 9, "italic")).pack(pady=(6, 0), padx=28, anchor="w")

        # tiempo total de ejecución (0 = infinito), con unidad seleccionable
        row2 = tk.Frame(win, bg=PANEL_BG)
        row2.pack(fill="x", padx=28, pady=(16, 0))
        tk.Label(row2, text="Tiempo de ejecución:", bg=PANEL_BG, fg=PANEL_FG).pack(side="left")

        self._dur_var = tk.DoubleVar(value=self._duration_in(self._duration_value, reverse=True))
        dur_spin = tk.Spinbox(row2, from_=0, to=999, increment=1, width=5,
                              textvariable=self._dur_var, command=self._apply_settings)
        dur_spin.pack(side="right")
        dur_spin.bind("<Return>", lambda _e: self._apply_settings())

        self._unit_var = tk.StringVar(value=UNITS[self._duration_unit])
        unit = ttk.Combobox(row2, textvariable=self._unit_var, state="readonly",
                            values=list(UNITS.values()), width=9)
        unit.pack(side="right", padx=6)
        unit.bind("<<ComboboxSelected>>", lambda _e: self._apply_settings())

        tk.Label(win, text="Ej.: 30 clics por minuto → 1 clic cada 2 s.\n"
                           "El ritmo se calcula solo, no hace falta poner segundos.\n"
                           "Tiempo de ejecución 0 = sin límite (hasta pulsar F6).\n"
                           "Todo se guarda para la próxima vez.",
                 bg=PANEL_BG, fg=MUTED, justify="left").pack(pady=(16, 0), padx=28, anchor="w")

        tk.Button(win, text="Listo", bg=RUNNING, fg="#0b0c10", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=18, pady=4, cursor="hand2",
                  command=lambda: self._close_settings(win)).pack(pady=(14, 0))

        self._settings = win

    def _duration_in(self, value: float, reverse: bool = False) -> float:
        """Convierte entre la unidad elegida y segundos."""
        factor = UNIT_SECONDS[self._duration_unit]
        return value / factor if reverse else value * factor

    def _duration_in(self, value: float, reverse: bool = False) -> float:
        """Convierte entre la unidad elegida y segundos."""
        factor = UNIT_SECONDS[self._duration_unit]
        return value / factor if reverse else value * factor

    # ------------------------------------------------------------ ritmo
    def _apply_rate(self) -> None:
        """Convierte el ritmo (clics por unidad) a clicks/segundo del motor."""
        cps = self._rate_value / UNIT_SECONDS[self._rate_unit]
        self._clicker.clicks_per_second = min(MAX_CLICKS_PER_SECOND, cps)
        # mantiene el atajo de la barra sincronizado (valor y unidad)
        if self._cps_quick is not None:
            self._cps_quick.delete(0, "end")
            self._cps_quick.insert(0, self._rate_display())
        if self._rate_unit_label is not None:
            self._rate_unit_label.configure(text=f"clics/{UNIT_SHORT[self._rate_unit]}  ")

    def _rate_display(self) -> str:
        value = self._rate_value
        return f"{value:.0f}" if value == int(value) else f"{value:.2f}".rstrip("0").rstrip(".")

    def _interval_text(self) -> str:
        """Cálculo visible para el usuario: '30 clics/min → 1 clic cada 2 s'."""
        if self._rate_value <= 0:
            return "sin clics"
        seconds = UNIT_SECONDS[self._rate_unit] / self._rate_value
        if seconds >= 3600:
            return f"1 clic cada {seconds / 3600:.2f} h"
        if seconds >= 60:
            return f"1 clic cada {seconds / 60:.2f} min"
        if seconds >= 1:
            return f"1 clic cada {seconds:.2f} s"
        return f"{1 / seconds:.1f} clics por segundo"

    def _apply_settings(self) -> None:
        try:
            rate = float(self._rate_var.get())
            dur = float(self._dur_var.get())
        except (tk.TclError, ValueError):
            return
        rate = min(6000.0, max(1.0, rate))
        self._rate_var.set(round(rate, 2))
        self._rate_value = rate
        self._rate_unit = next(
            (k for k, v in RATE_UNITS.items() if v == self._rate_unit_var.get()), "seconds"
        )
        self._apply_rate()
        self._interval_var.set("→ " + self._interval_text())

        self._duration_unit = next(
            (k for k, v in UNITS.items() if v == self._unit_var.get()), "seconds"
        )
        dur = min(999.0, max(0.0, dur))
        self._dur_var.set(dur)
        self._duration_value = int(dur)
        # 0 apaga el límite; si está corriendo, el nuevo tiempo cuenta desde ya
        self._clicker.duration = self._duration_in(dur)
        self._save_config()

    def _apply_quick_cps(self) -> None:
        """Lee el ritmo escrito en el atajo de la barra (en la unidad activa)."""
        if self.overlay is None or self._cps_quick is None:
            return
        try:
            rate = float(self._cps_quick.get().replace(",", "."))
        except ValueError:
            pass
        else:
            self._rate_value = min(6000.0, max(1.0, rate))
            self._apply_rate()
            self._save_config()
        # siempre se reescribe el valor normalizado
        self._cps_quick.delete(0, "end")
        self._cps_quick.insert(0, self._rate_display())

    def _close_settings(self, win: tk.Toplevel) -> None:
        self._apply_settings()
        self._settings = None
        win.destroy()

    def _load_config(self) -> None:
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            # compatibilidad con la config vieja ("clicks_per_second")
            if "rate_value" in data:
                self._rate_value = max(1.0, float(data["rate_value"]))
                if data.get("rate_unit") in RATE_UNITS:
                    self._rate_unit = data["rate_unit"]
            elif "clicks_per_second" in data:
                self._rate_value = float(data["clicks_per_second"])
                self._rate_unit = "seconds"
            self._duration_value = max(0, int(data.get("duration_value", 0)))
            if data.get("duration_unit") in UNITS:
                self._duration_unit = data["duration_unit"]
            self._clicker.duration = self._duration_in(self._duration_value)
        except (OSError, ValueError, TypeError):
            pass  # sin config válida: se usa el valor por defecto
        self._apply_rate()

    def _save_config(self) -> None:
        try:
            CONFIG_PATH.write_text(
                json.dumps({
                    "rate_value": self._rate_value,
                    "rate_unit": self._rate_unit,
                    "duration_value": self._duration_value,
                    "duration_unit": self._duration_unit,
                }),
                encoding="utf-8",
            )
        except OSError:
            pass  # si no se puede guardar, no rompemos la app

    def _drag_start(self, event: tk.Event) -> None:
        self._drag_x = event.x_root - self.root.winfo_pointerx() + event.x
        self._drag_y = event.y_root - self.root.winfo_pointery() + event.y

    def _drag_move(self, event: tk.Event) -> None:
        if self.overlay is not None:
            self.overlay.geometry(
                f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}"
            )

    def _on_f8(self) -> None:
        """F8 desde la bienvenida empieza la app; ya dentro, captura el punto."""
        if self.overlay is None:
            self.root.after(0, self._start_overlay)
        self._clicker.capture_point()

    def _on_f6(self) -> None:
        """F6 desde la bienvenida también empieza la app."""
        if self.overlay is None:
            self.root.after(0, self._start_overlay)
        self._clicker.toggle()

    def _tick(self) -> None:
        if self._clicker.point is None:
            self._point_var.set("sin capturar  ·  F8")
        else:
            x, y = self._clicker.point
            self._point_var.set(f"({x}, {y})")

        running = self._clicker.running
        rate = f"{self._rate_display()} clics/{UNIT_SHORT[self._rate_unit]}"
        state = f"ejecutando · {rate}" if running else f"detenido · {rate}"
        remaining = self._clicker.remaining_seconds
        if remaining is not None:
            m, s = divmod(int(remaining), 60)
            h, m = divmod(m, 60)
            clock = f"{h:02}:{m:02}:{s:02}" if h else f"{m:02}:{s:02}"
            state += f" · ⏳{clock}"
        self._state_var.set(f"{state} · F6")
        if self.overlay is not None:
            self._dot.configure(fg=RUNNING if running else STOPPED)
            self._toggle_btn.configure(text="F6  Detener" if running else "F6  Iniciar")
            # mantener el atajo de la barra en sincronía (salvo que se esté escribiendo en él)
            if self._cps_quick is not None and self._cps_quick != self.root.focus_get():
                self._cps_quick.delete(0, "end")
                self._cps_quick.insert(0, cps_text)
            if self._settings is not None and self._settings.winfo_exists():
                self._cps_var.set(round(self._clicker.clicks_per_second, 1))

        self.root.after(80, self._tick)

    def quit(self) -> None:
        self._clicker.stop()
        self._hotkeys.stop()
        self.root.destroy()


def run() -> None:
    root = tk.Tk()
    root.withdraw()
    ClickForgeApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()
