import os
import psycopg2

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ.get("DB_NAME", "labrei_microgrid"),
        user=os.environ.get("DB_USER", "labrei_admin"),
        password=os.environ.get("DB_PASSWORD", "YOUR_STRONG_PASSWORD")
    )

def ensure_tables():
    conn = get_db_conn()
    with conn.cursor() as cur:
        # buses
        cur.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            id               SERIAL PRIMARY KEY,
            bus_number       INTEGER NOT NULL UNIQUE,
            name             VARCHAR(50) NOT NULL,
            description      TEXT,
            location         VARCHAR(100),
            nominal_voltage  REAL,
            nominal_current  REAL,
            extra_parameters JSONB
        );
        """)

        # measurements sem id, PK natural bus_id+timestamp
        cur.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            bus_id    INTEGER      NOT NULL REFERENCES buses(bus_number),
            timestamp TIMESTAMPTZ  NOT NULL,
            freq_a    INTEGER, freq_b    INTEGER, freq_c    INTEGER,
            va_rms    INTEGER, vb_rms    INTEGER, vc_rms    INTEGER,
            ia_rms    INTEGER, ib_rms    INTEGER, ic_rms    INTEGER,
            pa        INTEGER, pb        INTEGER, pc        INTEGER,
            sa        INTEGER, sb        INTEGER, sc        INTEGER,
            qa        INTEGER, qb        INTEGER, qc        INTEGER,
            pfa       INTEGER, pfb       INTEGER, pfc       INTEGER,
            va_p      INTEGER, vb_p      INTEGER, vc_p      INTEGER,
            va_th     INTEGER, vb_th     INTEGER, vc_th     INTEGER,
            ia_p      INTEGER, ib_p      INTEGER, ic_p      INTEGER,
            ia_th     INTEGER, ib_th     INTEGER, ic_th     INTEGER,
            PRIMARY KEY (bus_id, timestamp)
        );
        """)

        # extensão e hypertable
        cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
        cur.execute("""
            SELECT create_hypertable('measurements', 'timestamp', if_not_exists => TRUE);
        """)
    conn.commit()
    conn.close()
