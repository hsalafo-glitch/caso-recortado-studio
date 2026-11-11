#!/bin/sh
# Arranque en la nube: la web (gunicorn en el puerto que da Railway) y, si la web está abierta, el obrero de vídeos.
set -e
mkdir -p "${CR_DATOS:-/datos}"
if [ -z "$SECRET_KEY" ]; then
  echo "AVISO: falta la variable SECRET_KEY; se usa una guardada en el disco permanente."
fi
if [ "$CR_SOLO_LISTA" != "1" ]; then
  python web/worker.py &
fi
cd web
exec gunicorn -w 2 -k gthread --threads 8 -b "0.0.0.0:${PORT:-8000}" --access-logfile - app:app
