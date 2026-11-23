#!/usr/bin/env bash
# Prueba con Docker Compose del Sprint 5 (Perfil Médico+) - Benjamín Leiva
#
# Cómo usarlo (desde la carpeta backend del repositorio):
#   cd "Fase 2/Evidencias Proyecto/Evidencias de sistema/Aplicacion/backend"
#   bash prueba_docker_sprint5.sh            # ejecuta los pasos D1 a D5
#   bash prueba_docker_sprint5.sh traccar    # además levanta Traccar (paso D6)
#   bash prueba_docker_sprint5.sh bajar      # apaga todo (conserva los datos)
#
# Qué hace: ejecuta cada comando de Guia_Docker_Compose_Sprint5.md, muestra la salida
# en pantalla (para tomar la captura) y la guarda en ./evidencias_docker/ con la fecha.
# No sube nada al repositorio y no toca el código. Crea .env solo si no existe, con un
# token de prueba. El .env NO debe subirse a GitHub.
#
# Honestidad: el resultado de cada paso se marca OK o FALLA según el código de salida.
# Si algo falla, el script lo dice y sigue con el siguiente paso.

set -u
TOKEN_PRUEBA="tok-docker-prueba-sprint5"
SALIDA="evidencias_docker"
FECHA="$(date +%Y-%m-%d_%H%M)"
RESUMEN="$SALIDA/resumen_${FECHA}.txt"
MODO="${1:-base}"

if [ "$MODO" = "bajar" ]; then
  docker compose down
  exit 0
fi

if [ ! -f docker-compose.yml ]; then
  echo "ERROR: ejecuta este script desde la carpeta backend (donde está docker-compose.yml)."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker no está activo. Abre Docker Desktop y espera a que diga 'running'."
  echo "Si pide virtualización, revisa que SVM Mode (AMD) o Intel VT-x esté activo en la BIOS."
  exit 1
fi

mkdir -p "$SALIDA"
: > "$RESUMEN"

paso() {  # paso <codigo> <titulo> <comando...>
  local cod="$1"; local titulo="$2"; shift 2
  echo
  echo "================ $cod - $titulo ================"
  echo "\$ $*"
  { echo "== $cod - $titulo"; echo "\$ $*"; date '+%Y-%m-%d %H:%M:%S'; } >> "$SALIDA/${cod}_${FECHA}.txt"
  "$@" 2>&1 | tee -a "$SALIDA/${cod}_${FECHA}.txt"
  local rc=${PIPESTATUS[0]}
  if [ "$rc" -eq 0 ]; then echo "$cod OK" | tee -a "$RESUMEN"; else echo "$cod FALLA (codigo $rc)" | tee -a "$RESUMEN"; fi
  echo ">>> Toma aquí la captura $cod (ver guía) y sigue."
}

# --- Preparación ---
if [ ! -f .env ]; then
  cp .env.example .env
  echo "TRACCAR_TOKEN=$TOKEN_PRUEBA" >> .env
  echo "Se creó .env desde .env.example con un token de prueba."
else
  grep -q '^TRACCAR_TOKEN=' .env || echo "TRACCAR_TOKEN=$TOKEN_PRUEBA" >> .env
fi
TOKEN_EN_ENV="$(grep '^TRACCAR_TOKEN=' .env | tail -1 | cut -d= -f2-)"

echo "== Perfil Médico+ - prueba Docker Sprint 5 - $FECHA" | tee -a "$RESUMEN"
echo "Docker: $(docker --version)" | tee -a "$RESUMEN"
echo "Commit del repositorio: $(git rev-parse --short HEAD 2>/dev/null || echo 'sin git')" | tee -a "$RESUMEN"

# --- D0: levantar ---
paso D0 "Construir y levantar" docker compose up --build -d

echo "Esperando a que la API responda (máx. 90 s)..."
for i in $(seq 1 45); do
  if curl -fs http://localhost:8000/health >/dev/null 2>&1; then echo "API lista."; break; fi
  sleep 2
done

# --- D1 a D5 ---
paso D1 "Estado de los servicios (db healthy, api en ejecución)" docker compose ps
paso D2 "Versión de migraciones (debe ser a5b6c7d8e9f0 (head))" docker compose exec -T api alembic current
paso D2b "alembic check (sin operaciones pendientes)" docker compose exec -T api alembic check
paso D3 "Health y documentación" bash -c 'curl -s -i http://localhost:8000/health | head -20; echo; curl -s http://localhost:8000/openapi.json | python3 -c "import sys,json; o=json.load(sys.stdin); print(\"rutas (paths):\",len(o[\"paths\"])); print(\"operaciones HTTP:\",sum(1 for p in o[\"paths\"].values() for m in p if m in (\"get\",\"post\",\"put\",\"patch\",\"delete\")))"'
echo ">>> Para D3 abre también http://localhost:8000/docs en el navegador y captura la lista de rutas."

paso D4 "Pruebas automáticas dentro del contenedor (esperado: 216)" docker compose exec -T api python -m pytest -q -p no:cacheprovider

# Prueba de humo: copia temporal con el puerto 8000 y el token del .env (no modifica el archivo del repositorio)
HUMO_TMP="$(mktemp -d)/prueba_humo_docker.py"
sed -e 's#http://localhost:8010#http://localhost:8000#' -e "s#TOK=\"tok-humo\"#TOK=\"$TOKEN_EN_ENV\"#" scripts/prueba_humo_sprint5.py > "$HUMO_TMP"
paso D5 "Prueba de humo (esperado: 29 de 29)" python3 "$HUMO_TMP"
rm -f "$HUMO_TMP"

# --- D6: Traccar (opcional) ---
if [ "$MODO" = "traccar" ]; then
  paso D6 "Con Traccar" docker compose -f docker-compose.yml -f traccar/docker-compose.traccar.yml up --build -d
  paso D6b "Servicios con Traccar" docker compose -f docker-compose.yml -f traccar/docker-compose.traccar.yml ps
  echo ">>> Abre http://localhost:8082 (panel de Traccar) y captura. Recuerda: el token de traccar/traccar.xml debe ser igual al TRACCAR_TOKEN del .env."
fi

echo
echo "================ RESUMEN ================"
cat "$RESUMEN"
echo "Salidas guardadas en: $SALIDA/"
echo "Para apagar: bash prueba_docker_sprint5.sh bajar"
