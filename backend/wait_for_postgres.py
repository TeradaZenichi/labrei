#!/usr/bin/env python3
import os
import time
import psycopg2
import json

# Definição estática dos barramentos
BUS_LIST = [
    (1,  'Main Bus',       'Main feeder',      'Lab 1', 220.0, 100.0, {"manufacturer": "Siemens"}),
    (2,  'Secondary Bus',  'Backup line',      'Lab 1', 220.0, 80.0,  {"manufacturer": "Siemens"}),
    (3,  'Load Bus',       'Load section',     'Lab 1', 220.0, 50.0,  {"manufacturer": "ABB"}),
    (4,  'Generation Bus', 'Solar plant',      'Lab 2', 380.0, 60.0,  {"manufacturer": "ABB"}),
    (5,  'Battery Bus',    'Battery section',  'Lab 2', 220.0, 40.0,  {"manufacturer": "LG"}),
    (6,  'Aux Bus',        'Auxiliary circuit','Lab 2', 220.0, 10.0,  {"manufacturer": "LG"}),
    (7,  'Spare Bus 1',    'Spare',            'Lab 3', 220.0, 15.0,  {}),
    (8,  'Spare Bus 2',    'Spare',            'Lab 3', 220.0, 15.0,  {}),
    (9,  'Spare Bus 3',    'Spare',            'Lab 3', 220.0, 15.0,  {}),
    (10, 'Test Bus 1',     'For testing',      'Lab 1', 220.0, 30.0,  {}),
    (11, 'Test Bus 2',     'For testing',      'Lab 1', 220.0, 30.0,  {}),
    (12, 'Test Bus 3',     'For testing',      'Lab 1', 220.0, 30.0,  {}),
    (13, 'External Bus',   'External source',  'Yard',  380.0, 100.0, {})
]

SETTINGS = [
    ("api_update_time",       "10", "int"),
    ("modbus_update_time",    "5",  "int"),
    ("RETENTION_DAYS",        "30", "int"),
    ("COMPRESS_AFTER_HOURS",  "24", "int"),
    ("RUN_INTERVAL_HOURS",    "1",  "int"),
]

# Leitura de environment vars
host      = os.environ.get("DB_HOST", "postgres")
port      = int(os.environ.get("DB_PORT", 5432))
user      = os.environ.get("DB_USER", "labrei_admin")
password  = os.environ.get("DB_PASSWORD", "unicamp2025")
dbname    = os.environ.get("DB_NAME", "labrei_microgrid")
timeout   = int(os.environ.get("WAIT_TIMEOUT", 60))

# Espera o banco subir
start = time.time()
while True:
    try:
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=dbname
        )
        print("Database is up!")
        break
    except psycopg2.OperationalError as e:
        elapsed = int(time.time() - start)
        if elapsed > timeout:
            print(f"Timed out after {timeout}s waiting for DB: {e}")
            exit(1)
        print(f"Waiting for database {host}:{port}... ({elapsed}/{timeout}s)")
        time.sleep(2)

# Criação das tabelas
cur = conn.cursor()

# 0) settings
cur.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key VARCHAR(64) PRIMARY KEY,
    value TEXT NOT NULL,
    type VARCHAR(16) DEFAULT 'int',
    updated_at TIMESTAMPTZ DEFAULT now()
);
""")
for key, value, typ in SETTINGS:
    cur.execute("""
        INSERT INTO settings (key, value, type)
        VALUES (%s, %s, %s)
        ON CONFLICT (key) DO UPDATE
        SET value = EXCLUDED.value,
            type = EXCLUDED.type,
            updated_at = now();
    """, (key, value, typ))

# 1) buses
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
# Inserção inicial de barramentos
for bus in BUS_LIST:
    cur.execute("""
        INSERT INTO buses (
            bus_number, name, description, location,
            nominal_voltage, nominal_current, extra_parameters
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (bus_number) DO NOTHING;
    """, (
        bus[0], bus[1], bus[2], bus[3],
        bus[4], bus[5], json.dumps(bus[6])
    ))

# 2) measurements
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
# transform into hypertable
cur.execute("""
    SELECT create_hypertable('measurements', 'timestamp', if_not_exists => TRUE);
""")

# finalize
conn.commit()
cur.close()
conn.close()
print("✅ Tables buses, measurements, and settings created/seeded.")
