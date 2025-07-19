# modbus_collector/maintenance/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY retention.py .

RUN pip install --no-cache-dir psycopg2-binary==2.9.6


CMD ["python", "retention.py"]
