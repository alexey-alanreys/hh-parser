# syntax=docker/dockerfile:1

# --- Stage 1: build frontend ---
FROM node:20-slim AS frontend-build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: runtime — nginx (static + reverse proxy) + uvicorn in one container ---
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

# Backend
WORKDIR /backend
COPY backend/requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY backend/app ./app

# Frontend static
COPY --from=frontend-build /frontend/dist /usr/share/nginx/html

# Config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]