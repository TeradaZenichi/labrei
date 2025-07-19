import os
import time
import schedule
import psycopg2
import json
from pymodbus.client.sync import ModbusTcpClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # Carrega as variáveis do .env, se existir

DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ.get("DB_NAME", "labrei_microgrid")
DB_USER = os.environ.get("DB_USER", "labrei_admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "YOUR_STRONG_PASSWORD")

MODBUS_HOST = os.environ.get("MODBUS_HOST", "192.168.0.123")
MODBUS_PORT = int(os.environ.get("MODBUS_PORT", 502))

def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def collect_modbus_data():
    print(f"[{datetime.now()}] Connecting to Modbus at {MODBUS_HOST}:{MODBUS_PORT}...")
    client = ModbusTcpClient(MODBUS_HOST, port=MODBUS_PORT)
    if client.connect():
        try:
            # Exemplo: ler 2 registradores a partir do endereço 0 do barramento 1
            rr = client.read_holding_registers(0, 2, unit=1)
            if rr.isError():
                print("Error reading Modbus registers.")
            else:
                value = rr.registers[0]
                print(f"Read value: {value}")
                # Insere no banco (ajuste conforme seu modelo de measurements)
                conn = get_db_conn()
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO measurements (bus_id, timestamp, measurement_type, value, unit)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (1, datetime.now(), 'voltage', value, 'V'))
                conn.commit()
                conn.close()
        finally:
            client.close()
    else:
        print("Could not connect to Modbus device.")

# Agenda para rodar a cada 1 minuto
schedule.every(1).minutes.do(collect_modbus_data)

if __name__ == "__main__":
    print("Starting Modbus Collector")
    while True:
        schedule.run_pending()
        time.sleep(1)
