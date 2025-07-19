import os
import psycopg2
import json
from buses_data import BUS_LIST

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ.get("DB_NAME", "labrei_microgrid"),
        user=os.environ.get("DB_USER", "labrei_admin"),
        password=os.environ.get("DB_PASSWORD", "YOUR_STRONG_PASSWORD")
    )

def ensure_buses():
    conn = get_db_conn()
    with conn.cursor() as cur:
        # Cria a tabela se não existir
        cur.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            id SERIAL PRIMARY KEY,
            bus_number INTEGER NOT NULL UNIQUE,
            name VARCHAR(50) NOT NULL,
            description TEXT,
            location VARCHAR(100),
            nominal_voltage REAL,
            nominal_current REAL,
            extra_parameters JSONB
        );
        """)
        # Insere cada barramento se não existir
        for bus in BUS_LIST:
            cur.execute("""
                INSERT INTO buses (bus_number, name, description, location, nominal_voltage, nominal_current, extra_parameters)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (bus_number) DO NOTHING;
            """, (bus[0], bus[1], bus[2], bus[3], bus[4], bus[5], json.dumps(bus[6])))
    conn.commit()
    # (Opcional) Exibe os barramentos cadastrados
    with conn.cursor() as cur:
        cur.execute("SELECT bus_number, name FROM buses ORDER BY bus_number;")
        buses = cur.fetchall()
        print("Registered buses in the database:")
        for b in buses:
            print(f"  Bus {b[0]}: {b[1]}")
    conn.close()

def ensure_measurements():
    conn = get_db_conn()
    cur = conn.cursor()
    # Cria tabela com todas as medidas e timestamp
    cur.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id SERIAL PRIMARY KEY,
        bus_id INTEGER NOT NULL REFERENCES buses(bus_number),
        timestamp TIMESTAMPTZ NOT NULL,
        freq_a INTEGER,
        freq_b INTEGER,
        freq_c INTEGER,
        va_rms INTEGER,
        vb_rms INTEGER,
        vc_rms INTEGER,
        ia_rms INTEGER,
        ib_rms INTEGER,
        ic_rms INTEGER,
        pa INTEGER,
        pb INTEGER,
        pc INTEGER,
        sa INTEGER,
        sb INTEGER,
        sc INTEGER,
        qa INTEGER,
        qb INTEGER,
        qc INTEGER,
        pfa INTEGER,
        pfb INTEGER,
        pfc INTEGER,
        va_p INTEGER,
        vb_p INTEGER,
        vc_p INTEGER,
        va_th INTEGER,
        vb_th INTEGER,
        vc_th INTEGER,
        ia_p INTEGER,
        ib_p INTEGER,
        ic_p INTEGER,
        ia_th INTEGER,
        ib_th INTEGER,
        ic_th INTEGER
    );
    """)
    # Cria o hypertable, se não existir ainda
    cur.execute("""
        SELECT create_hypertable('measurements', 'timestamp', if_not_exists => TRUE);
    """)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    ensure_buses()
    ensure_measurements()   # <--- Não esqueça de chamar para criar as duas tabelas!
