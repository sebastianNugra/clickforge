"""Motor del autoclicker: captura de punto y clics automáticos."""

from __future__ import annotations

import threading

from pynput import mouse


class AutoClicker:
    """Hace clics repetidos en un punto fijo de la pantalla."""

    def __init__(self) -> None:
        self._mouse = mouse.Controller()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self.point: tuple[int, int] | None = None
        self._interval = 0.1  # segundos entre clics

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

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

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
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self.running:
            return
        self._stop.set()
        assert self._thread is not None
        self._thread.join(timeout=2)
        self._thread = None

    def _loop(self) -> None:
        assert self.point is not None
        x, y = self.point
        while not self._stop.is_set():
            self._mouse.position = (x, y)
            self._mouse.click(mouse.Button.left, 1)
            self._stop.wait(self.interval)
