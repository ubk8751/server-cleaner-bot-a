FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /framework
COPY pyproject.toml /framework/pyproject.toml
COPY catcord_bots /framework/catcord_bots

RUN pip install --no-cache-dir /framework
