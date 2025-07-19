#!/usr/bin/env python3
import os
import time
import requests
import random
from datetime import datetime, timezone

# Load configuration from environment
# Deve apontar para o nome do service no Docker Compose
API_URL       = os.environ.get("API_URL", "http://backend:8000")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 5))  # seconds

def fetch_bus_list():
    """GET /buses -> retorna lista de bus_number"""
    resp = requests.get(f"{API_URL}/buses")
    resp.raise_for_status()
    return [b["bus_number"] for b in resp.json()]

def make_dummy_measurement(bus_id: int):
    """
    Gera payload sem escala x100.
    freq_* em Hz, unidades reais.
    """
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "bus_id": bus_id,
        "timestamp": now,
        "freq_a": random.randint(48, 52),
        "freq_b": random.randint(48, 52),
        "freq_c": random.randint(48, 52),
        "va_rms": random.randint(210, 230),
        "vb_rms": random.randint(210, 230),
        "vc_rms": random.randint(210, 230),
        "ia_rms": random.randint(0, 100),
        "ib_rms": random.randint(0, 100),
        "ic_rms": random.randint(0, 100),
        "pa":    random.randint(0, 2000),
        "pb":    random.randint(0, 2000),
        "pc":    random.randint(0, 2000),
        "sa":    random.randint(0, 2500),
        "sb":    random.randint(0, 2500),
        "sc":    random.randint(0, 2500),
        "qa":    random.randint(-500, 500),
        "qb":    random.randint(-500, 500),
        "qc":    random.randint(-500, 500),
        # agora inteiros entre 950 e 1000
        "pfa":   random.randint(950, 1000),
        "pfb":   random.randint(950, 1000),
        "pfc":   random.randint(950, 1000),
        "va_p":  random.randint(240, 260),
        "vb_p":  random.randint(240, 260),
        "vc_p":  random.randint(240, 260),
        "va_th": random.randint(0, 360),
        "vb_th": random.randint(0, 360),
        "vc_th": random.randint(0, 360),
        "ia_p":  random.randint(0, 150),
        "ib_p":  random.randint(0, 150),
        "ic_p":  random.randint(0, 150),
        "ia_th": random.randint(0, 360),
        "ib_th": random.randint(0, 360),
        "ic_th": random.randint(0, 360),
    }

def main():
    print(f"[test.py] Dummy Modbus collector — interval={POLL_INTERVAL}s, API={API_URL}")
    try:
        buses = fetch_bus_list()
        print(f"[test.py] Buses found: {buses}")
    except Exception as e:
        print(f"[test.py] ERROR fetching buses: {e}")
        return

    while True:
        for bus_id in buses:
            m = make_dummy_measurement(bus_id)
            try:
                r = requests.post(f"{API_URL}/buses/{bus_id}/measurements", json=m)
                r.raise_for_status()
                print(f"[{datetime.now().isoformat()}] Posted measurement for bus {bus_id}")
            except Exception as e:
                print(f"[{datetime.now().isoformat()}] ERROR posting for bus {bus_id}: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
