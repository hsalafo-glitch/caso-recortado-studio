# Caso Recortado Studio en Railway (o cualquier servicio que construya un Dockerfile).
# La web y el obrero corren en el mismo servicio y comparten el disco permanente montado en /datos.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 CR_DATOS=/datos
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential pkg-config libcairo2-dev ffmpeg fontconfig \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements-web.txt .
RUN pip install -r requirements-web.txt
COPY . .
RUN install -m 644 fuentes/InterDisplay-Black.otf /usr/local/share/fonts/ && fc-cache -f >/dev/null \
    && chmod +x arrancar.sh
CMD ["./arrancar.sh"]
