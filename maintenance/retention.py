#!/usr/bin/env python3
import os
import time
import psycopg2

# lê vars do .env
DB_HOST        = os.environ["DB_HOST"]
DB_PORT        = os.environ.get("DB_PORT", "5432")
DB_NAME        = os.environ["DB_NAME"]
DB_USER        = os.environ["DB_USER"]
DB_PASSWORD    = os.environ["DB_PASSWORD"]

# períodos configuráveis
RETENTION_DAYS       = int(os.environ.get("RETENTION_DAYS", 7))
COMPRESS_AFTER_HOURS = int(os.environ.get("COMPRESS_AFTER_HOURS", 24))
RUN_INTERVAL_HOURS   = int(os.environ.get("RUN_INTERVAL_HOURS", 24))

conn_info = {
    "host":     DB_HOST,
    "port":     DB_PORT,
    "dbname":   DB_NAME,
    "user":     DB_USER,
    "password": DB_PASSWORD
}

def apply_policies():
    with psycopg2.connect(**conn_info) as conn:
        with conn.cursor() as cur:
            # drop_chunks: primeiro o regclass da tabela, depois o intervalo
            cur.execute(f"""
                SELECT drop_chunks(
                  'measurements'::regclass,
                  INTERVAL '{RETENTION_DAYS} days'
                );
            """)
            print(f"[retention] dropped chunks older than {RETENTION_DAYS} days")

            # habilita compressão na hypertable
            cur.execute("""
                ALTER TABLE measurements
                SET (
                  timescaledb.compress,
                  timescaledb.compress_segmentby = 'bus_id'
                );
            """)
            print("[retention] compression enabled on measurements")

            # adiciona política de compressão
            cur.execute(f"""
                SELECT add_compression_policy(
                  'measurements',
                  INTERVAL '{COMPRESS_AFTER_HOURS} hours'
                );
            """)
            print(f"[retention] added compression policy for >{COMPRESS_AFTER_HOURS}h")

if __name__ == "__main__":
    print(f"[retention] starting, interval every {RUN_INTERVAL_HOURS}h")
    # primeira execução imediata
    apply_policies()
    # loop
    while True:
        time.sleep(RUN_INTERVAL_HOURS * 3600)
        apply_policies()
