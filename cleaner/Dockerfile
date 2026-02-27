FROM catcord-bots-framework:latest

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY main.py /app/main.py
COPY cleaner.py /app/cleaner.py

ENTRYPOINT ["python", "-u", "/app/main.py"]
