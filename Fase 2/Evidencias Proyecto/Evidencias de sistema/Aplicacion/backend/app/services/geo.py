"""Distancias entre coordenadas (HU 17)."""
from math import asin, cos, radians, sin, sqrt

RADIO_TIERRA_M = 6_371_000


def distancia_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia en metros entre dos puntos (fórmula de haversine)."""
    f1, f2 = radians(lat1), radians(lat2)
    df, dl = f2 - f1, radians(lon2 - lon1)
    a = sin(df / 2) ** 2 + cos(f1) * cos(f2) * sin(dl / 2) ** 2
    return 2 * RADIO_TIERRA_M * asin(sqrt(a))


def dentro(lat: float, lon: float, centro_lat: float, centro_lon: float, radio_m: float) -> bool:
    return distancia_m(lat, lon, centro_lat, centro_lon) <= radio_m
