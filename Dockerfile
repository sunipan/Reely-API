FROM python:3.12-slim
WORKDIR /app
# system deps
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg curl ca-certificates unzip \
    && update-ca-certificates \
    && curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh -s -- -q \
    && rm -rf /var/lib/apt/lists/*
# python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY service.py .

ENV PORT=5000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} service:app"]