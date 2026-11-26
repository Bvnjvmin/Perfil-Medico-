"""
Límite de intentos fallidos (por ejemplo, de inicio de sesión).

Guarda en memoria la hora de cada fallo reciente por clave y bloquea cuando se llega al máximo
dentro de la ventana. Frena la adivinanza de contraseñas por fuerza bruta.

Limitaciones (declaradas): vive en la memoria de un solo proceso, así que se reinicia al reiniciar la API y
no se comparte entre varias instancias (para eso haría falta Redis). Detrás de un proxy inverso, todas las
solicitudes parecen venir de la IP del proxy: habría que leer la cabecera X-Forwarded-For de un proxy de confianza.
"""
import math
import threading
import time
from collections import deque
from typing import Callable


class LimitadorIntentos:
    def __init__(self, reloj: Callable[[], float] = time.monotonic) -> None:
        self._reloj = reloj
        self._fallos: dict[str, deque] = {}
        self._cerrojo = threading.Lock()

    def _purgar(self, clave: str, ventana_s: float) -> deque:
        fallos = self._fallos.setdefault(clave, deque())
        limite = self._reloj() - ventana_s
        while fallos and fallos[0] <= limite:
            fallos.popleft()
        if not fallos:
            self._fallos.pop(clave, None)
        return fallos

    def segundos_de_espera(self, clave: str, maximo: int, ventana_s: float) -> int:
        """0 si se puede intentar; si no, los segundos que faltan para el siguiente intento."""
        with self._cerrojo:
            fallos = self._purgar(clave, ventana_s)
            if len(fallos) < maximo:
                return 0
            return max(1, math.ceil(ventana_s - (self._reloj() - fallos[0])))

    def registrar_fallo(self, clave: str) -> None:
        with self._cerrojo:
            self._fallos.setdefault(clave, deque()).append(self._reloj())

    def limpiar(self, clave: str) -> None:
        with self._cerrojo:
            self._fallos.pop(clave, None)

    def reiniciar(self) -> None:
        with self._cerrojo:
            self._fallos.clear()
