FROM python:3.11-slim

WORKDIR /app

# Copie o script de espera e garanta formato Unix e permissão de execução
# COPY wait-for-it.sh /wait-for-it.sh
# RUN sed -i 's/\r$//' /wait-for-it.sh && chmod +x /wait-for-it.sh

# Copie dependências e instale-as
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação
COPY . .

EXPOSE 8000

# Comando padrão: espera o postgres subir e inicia o FastAPI
# CMD ["/wait-for-it.sh", "postgres", "5432", "--", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["sh", "-c", "python wait_for_postgres.py && uvicorn app:app --host 0.0.0.0 --port 8000"]
