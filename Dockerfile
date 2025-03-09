# Basis-Image (zum Beispiel Python 3.9 slim)
FROM python:3.12

# Arbeitsverzeichnis festlegen
WORKDIR /app

# Kopiere das Python-Skript in das Image
COPY proxy.py .

# Exponiere den Port, auf dem der Proxy lauscht
EXPOSE 8888

# Setze den Standardbefehl, um den Proxy zu starten
CMD ["python", "-u", "proxy.py"]
