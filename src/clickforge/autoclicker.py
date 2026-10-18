"""Motor del autoclicker: captura de punto y clics automáticos."""

from __future__ import annotations

import threading
import time

from pynput import mouse


class AutoClicker:
    """Hace clics repetidos en un punto fijo de la pantalla."""

    def __init__(self) -> None:
        self._mouse = mouse.Controller()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self.point: tuple[int, int] | None = None
        self._interval = 0.1  # segundos entre clics
        self.duration = 0.0  # duración total en segundos; 0 = sin límite
        self._started_at: float | None = None

    # ------------------------------------------------------------- ritmo
    @property
    def interval(self) -> float:
        return self._interval

    @interval.setter
    def interval(self, value: float) -> None:
        # al menos 1 ms entre clics, para no saturar el CPU
        self._interval = max(0.001, value)

    @property
    def clicks_per_second(self) -> float:
        return 1.0 / self._interval

    @clicks_per_second.setter
    def clicks_per_second(self, value: float) -> None:
        self.interval = 1.0 / max(0.001, value)

    # --------------------------------------------------------------- estado
    @property
    def running(self) -> bool:
        """True mientras el hilo de clics está vivo."""
        thread = self._thread
        return thread is not None and thread.is_alive()

    @property
    def remaining_seconds(self) -> float | None:
        """Segundos restantes de la duración; None si no hay límite.

        Mientras corre devuelve el tiempo que falta; detenido devuelve el
        total configurado (así la barra siempre lo muestra antes de empezar).
        """
        if self.duration <= 0:
            return None
        started = self._started_at
        if self.running and started is not None:
            return max(0.0, self.duration - (time.monotonic() - started))
        return self.duration

    def capture_point(self) -> None:
        """Guarda la posición actual del mouse."""
        self.point = self._mouse.position

    def toggle(self) -> None:
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self) -> None:
        if self.point is None or self.running:
            return
        self._stop.clear()
        self._started_at = time.monotonic()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        thread = self._thread
        if thread is None or not thread.is_alive():
            self._thread = None
            self._started_at = None
            return
        self._stop.set()
        thread.join(timeout=2.0)
        self._thread = None
        self._started_at = None

    def _loop(self) -> None:
        assert self.point is not None
        x, y = self.point
        try:
            while not self._stop.is_set():
                wait = self._interval
                if self.duration > 0 and self._started_at is not None:
                    left = self.duration - (time.monotonic() - self._started_at)
                    if left <= 0:
                        break  # se agotó el tiempo: termina solo
                    # no dormir más de lo que falta, así se detiene a tiempo
                    wait = min(wait, left)
                self._mouse.position = (x, y)
                self._mouse.click(mouse.Button.left, 1)
                self._stop.wait(wait)
        finally:
            # al terminar (por F6 o por tiempo) deja todo listo para
            # volver a empezar desde cero
            self._thread = None
            self._started_at = None
