#!/usr/bin/env python3
"""
Simula una pulsera GPS enviando lecturas a la API, sin hardware ni servidor Traccar.

Sirve para probar y mostrar en la demo las alarmas de la pulsera (HU 17 y HU 19): ubicación, salida de
una geocerca, botón SOS, caída y batería baja. Usa solo la biblioteca estándar de Python.

Requisitos: la API corriendo con `TRACCAR_TOKEN` configurado, y la pulsera ya registrada en un perfil
con el mismo identificador (`POST /perfiles/{id}/pulseras`).

Ejemplos (desde la carpeta backend):
    python scripts/simular_pulsera.py --token CLAVE --id 356938035643809 posicion --lat -33.4489 --lon -70.6693
    python scripts/simular_pulsera.py --token CLAVE --id 356938035643809 sos
    python scripts/simular_pulsera.py --token CLAVE --id 356938035643809 caida
    python scripts/simular_pulsera.py --token CLAVE --id 356938035643809 bateria --porcentaje 9
    python scripts/simular_pulsera.py --token CLAVE --id 356938035643809 recorrido --lat -33.4489 --lon -70.6693 --metros 1000

El comando `recorrido` parte en las coordenadas dadas (por ejemplo el centro de una geocerca) y se aleja
hacia el norte en varios pasos: al salir del radio de la geocerca se crea el evento de salida.
Agregue `--json` para enviar el formato JSON de Traccar (POST) en vez de parámetros en la URL (GET).
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

METROS_POR_GRADO_LATITUD = 111_320


def enviar(args, lat, lon, alarma=None, bateria=None):
    ahora = datetime.now(timezone.utc)
    if args.json:
        atributos = {}
        if alarma:
            atributos["alarm"] = alarma
        if bateria is not None:
            atributos["batteryLevel"] = bateria
        cuerpo = {
            "position": {"latitude": lat, "longitude": lon, "speed": 0.0, "fixTime": ahora.isoformat(), "attributes": atributos},
            "device": {"uniqueId": args.id, "name": "Pulsera simulada"},
        }
        url = f"{args.url}/traccar/posiciones?" + urllib.parse.urlencode({"token": args.token})
        pedido = urllib.request.Request(
            url, data=json.dumps(cuerpo).encode(), headers={"Content-Type": "application/json"}, method="POST"
        )
    else:
        params = {"token": args.token, "id": args.id, "lat": lat, "lon": lon, "timestamp": int(ahora.timestamp() * 1000)}
        if alarma:
            params["alarm"] = alarma
        if bateria is not None:
            params["batt"] = bateria
        pedido = urllib.request.Request(f"{args.url}/traccar/posiciones?" + urllib.parse.urlencode(params))
    try:
        with urllib.request.urlopen(pedido, timeout=10) as respuesta:
            print(f"  -> {respuesta.status} {respuesta.read().decode()}")
    except urllib.error.HTTPError as error:
        print(f"  -> ERROR {error.code}: {error.read().decode()}")
        sys.exit(1)
    except urllib.error.URLError as error:
        print(f"  -> No se pudo conectar con {args.url}: {error.reason}")
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(description="Simula una pulsera GPS enviando lecturas a la API.")
    p.add_argument("--url", default="http://localhost:8000", help="dirección de la API (por defecto http://localhost:8000)")
    p.add_argument("--token", required=True, help="el valor de TRACCAR_TOKEN de la API")
    p.add_argument("--id", required=True, help="identificador de la pulsera (el mismo con que se registró)")
    p.add_argument("--json", action="store_true", help="enviar el formato JSON de Traccar en vez de parámetros en la URL")
    sub = p.add_subparsers(dest="accion", required=True)

    base = argparse.ArgumentParser(add_help=False)
    base.add_argument("--lat", type=float, default=-33.4489, help="latitud (por defecto, Santiago centro)")
    base.add_argument("--lon", type=float, default=-70.6693, help="longitud")

    s = sub.add_parser("posicion", parents=[base], help="envía una lectura de ubicación")
    s.add_argument("--bateria", type=int, help="porcentaje de batería (0 a 100)")
    sub.add_parser("sos", parents=[base], help="envía la alarma del botón SOS")
    sub.add_parser("caida", parents=[base], help="envía la alarma de caída")
    s = sub.add_parser("bateria", parents=[base], help="envía una lectura con la batería baja")
    s.add_argument("--porcentaje", type=int, default=9)
    s = sub.add_parser("recorrido", parents=[base], help="se aleja hacia el norte en varios pasos")
    s.add_argument("--metros", type=int, default=1000, help="distancia total que se aleja (por defecto 1000)")
    s.add_argument("--pasos", type=int, default=5)
    s.add_argument("--pausa", type=float, default=1.0, help="segundos entre lecturas")

    args = p.parse_args()
    if args.accion == "posicion":
        print(f"Enviando posición ({args.lat}, {args.lon})")
        enviar(args, args.lat, args.lon, bateria=args.bateria)
    elif args.accion == "sos":
        print("Enviando alarma SOS")
        enviar(args, args.lat, args.lon, alarma="sos")
    elif args.accion == "caida":
        print("Enviando alarma de caída")
        enviar(args, args.lat, args.lon, alarma="fallDown")
    elif args.accion == "bateria":
        print(f"Enviando batería al {args.porcentaje} %")
        enviar(args, args.lat, args.lon, bateria=args.porcentaje)
    else:
        print(f"Recorrido de {args.metros} m hacia el norte en {args.pasos} pasos")
        for paso in range(args.pasos + 1):
            lat = args.lat + (args.metros * paso / args.pasos) / METROS_POR_GRADO_LATITUD
            print(f"Paso {paso}/{args.pasos}: ({lat:.5f}, {args.lon})")
            enviar(args, lat, args.lon)
            if paso < args.pasos:
                time.sleep(args.pausa)


if __name__ == "__main__":
    main()
