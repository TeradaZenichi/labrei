from db import get_db_conn
from models import Bus, Measurement
import psycopg2.extras
from datetime import datetime
from datetime import datetime, timedelta


# ————— BUSES —————

def get_all_buses():
    """Consultar todos os barramentos."""
    conn = get_db_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT * FROM buses ORDER BY bus_number;")
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_bus(bus: Bus):
    """Inserir um novo barramento."""
    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO buses
              (bus_number, name, description, location, nominal_voltage, nominal_current, extra_parameters)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            bus.bus_number, bus.name, bus.description, bus.location,
            bus.nominal_voltage, bus.nominal_current, psycopg2.extras.Json(bus.extra_parameters)
        ))
        new_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return new_id

def get_bus_by_name(name: str):
    """Consultar barramento pelo nome."""
    conn = get_db_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT * FROM buses WHERE name = %s;", (name,))
        row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_bus_if_no_measurements(bus_number: int) -> bool:
    """
    Deletar o barramento somente se não houver medidas associadas.
    Retorna True se deletou, False se havia medidas ou não existia.
    """
    conn = get_db_conn()
    with conn.cursor() as cur:
        # checa existência de medidas
        cur.execute("SELECT 1 FROM measurements WHERE bus_id = %s LIMIT 1;", (bus_number,))
        if cur.fetchone():
            conn.close()
            return False
        # deleta barramento
        cur.execute("DELETE FROM buses WHERE bus_number = %s;", (bus_number,))
        deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def update_bus(bus_number: int, bus: Bus) -> bool:
    """Alterar os dados de um barramento existente. Retorna True se existia e foi atualizado."""
    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE buses SET
              name             = %s,
              description      = %s,
              location         = %s,
              nominal_voltage  = %s,
              nominal_current  = %s,
              extra_parameters = %s
            WHERE bus_number = %s;
        """, (
            bus.name, bus.description, bus.location,
            bus.nominal_voltage, bus.nominal_current,
            psycopg2.extras.Json(bus.extra_parameters),
            bus_number
        ))
        updated = cur.rowcount > 0
    conn.commit()
    conn.close()
    return updated


# ————— MEASUREMENTS —————

def get_measurements(bus_id: int, limit: int = 100):
    """Consultar as últimas N medições de um barramento."""
    conn = get_db_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT * FROM measurements
             WHERE bus_id = %s
             ORDER BY timestamp DESC
             LIMIT %s;
        """, (bus_id, limit))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_measurement(m: Measurement):
    """Adicionar uma medida para um barramento."""
    return create_measurement(m)  # já implementado abaixo

def create_measurement(m: Measurement):
    """Interno: insere um registro de medições."""
    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO measurements (
                bus_id, timestamp,
                freq_a, freq_b, freq_c,
                va_rms, vb_rms, vc_rms,
                ia_rms, ib_rms, ic_rms,
                pa, pb, pc,
                sa, sb, sc,
                qa, qb, qc,
                pfa, pfb, pfc,
                va_p, vb_p, vc_p,
                va_th, vb_th, vc_th,
                ia_p, ib_p, ic_p,
                ia_th, ib_th, ic_th
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s
            );
        """, (
            m.bus_id, m.timestamp,
            m.freq_a, m.freq_b, m.freq_c,
            m.va_rms, m.vb_rms, m.vc_rms,
            m.ia_rms, m.ib_rms, m.ic_rms,
            m.pa, m.pb, m.pc,
            m.sa, m.sb, m.sc,
            m.qa, m.qb, m.qc,
            m.pfa, m.pfb, m.pfc,
            m.va_p, m.vb_p, m.vc_p,
            m.va_th, m.vb_th, m.vc_th,
            m.ia_p, m.ib_p, m.ic_p,
            m.ia_th, m.ib_th, m.ic_th
        ))
    conn.commit()
    conn.close()
    # retornamos o par natural de PK
    return {"bus_id": m.bus_id, "timestamp": m.timestamp}

def update_measurement(
    bus_id: int,
    year: int, month: int, day: int, hour: int, minute: int, second: int,
    new: Measurement
) -> bool:
    """
    Alterar uma medida existente, identificada por bus_id + timestamp (sem milissegundos).
    Retorna True se atualizou.
    """
    ts = datetime(year, month, day, hour, minute, second)
    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE measurements SET
              freq_a = %s, freq_b = %s, freq_c = %s,
              va_rms = %s, vb_rms = %s, vc_rms = %s,
              ia_rms = %s, ib_rms = %s, ic_rms = %s,
              pa     = %s, pb     = %s, pc     = %s,
              sa     = %s, sb     = %s, sc     = %s,
              qa     = %s, qb     = %s, qc     = %s,
              pfa    = %s, pfb    = %s, pfc    = %s,
              va_p   = %s, vb_p   = %s, vc_p   = %s,
              va_th  = %s, vb_th  = %s, vc_th  = %s,
              ia_p   = %s, ib_p   = %s, ic_p   = %s,
              ia_th  = %s, ib_th  = %s, ic_th  = %s
            WHERE bus_id = %s AND timestamp = %s;
        """, (
            new.freq_a, new.freq_b, new.freq_c,
            new.va_rms, new.vb_rms, new.vc_rms,
            new.ia_rms, new.ib_rms, new.ic_rms,
            new.pa, new.pb, new.pc,
            new.sa, new.sb, new.sc,
            new.qa, new.qb, new.qc,
            new.pfa, new.pfb, new.pfc,
            new.va_p, new.vb_p, new.vc_p,
            new.va_th, new.vb_th, new.vc_th,
            new.ia_p, new.ib_p, new.ic_p,
            new.ia_th, new.ib_th, new.ic_th,
            bus_id, ts
        ))
        updated = cur.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def delete_measurement(
    bus_id: int,
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> bool:
    """
    Excluir uma medida única, identificada por bus_id + timestamp (sem ms).
    """
    ts = datetime(year, month, day, hour, minute, second)
    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM measurements WHERE bus_id = %s AND timestamp = %s;",
            (bus_id, ts)
        )
        deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def delete_measurements_in_range(
    bus_id: int,
    start: datetime,  # ou (yr,mo,da,hr,mi,se) mas recebe datetime
    end: datetime
) -> int:
    """
    Excluir medidas de um barramento em um intervalo [start, end].
    Retorna número de linhas deletadas.
    """
    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM measurements
             WHERE bus_id = %s
               AND timestamp BETWEEN %s AND %s;
        """, (bus_id, start, end))
        count = cur.rowcount
    conn.commit()
    conn.close()
    return count

def delete_all_measurements(bus_id: int) -> int:
    """Excluir todas as medidas de um barramento. Retorna quantas foram removidas."""
    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM measurements WHERE bus_id = %s;", (bus_id,))
        count = cur.rowcount
    conn.commit()
    conn.close()
    return count

def get_last_measurement(bus_id: int):
    """Consultar a última medida de um barramento."""
    conn = get_db_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT * FROM measurements
             WHERE bus_id = %s
             ORDER BY timestamp DESC
             LIMIT 1;
        """, (bus_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_measurements_in_range(
    bus_id: int,
    start: datetime,
    end: datetime,
    limit: int = 100
):
    """
    Consultar uma faixa de medidas de um barramento no intervalo [start, end].
    Retorna até `limit` registros ordenados por timestamp.
    """
    conn = get_db_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT * FROM measurements
             WHERE bus_id = %s
               AND timestamp BETWEEN %s AND %s
             ORDER BY timestamp DESC
             LIMIT %s;
        """, (bus_id, start, end, limit))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_last_n_measurements(bus_id: int, n: int = 100):
    """
    Retorna as N últimas medições de um barramento, ordenadas do mais antigo para o mais recente.
    """
    conn = get_db_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT * FROM measurements
             WHERE bus_id = %s
             ORDER BY timestamp DESC
             LIMIT %s;
        """, (bus_id, n))
        rows = cur.fetchall()
    conn.close()
    # Inverte a ordem para retornar do mais antigo para o mais recente
    return [dict(r) for r in reversed(rows)]


def get_setting(key: str):
    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT value, type FROM settings WHERE key = %s;", (key,))
        row = cur.fetchone()
    conn.close()
    if row is None:
        raise ValueError(f"Config '{key}' not found")
    value, typ = row
    if typ == "int":
        return int(value)
    if typ == "float":
        return float(value)
    if typ == "json":
        import json
        return json.loads(value)
    return value  # string por padrão

def update_setting(key: str, value: str, typ: str = None):
    """
    Atualiza o valor (e opcionalmente o tipo) de uma configuração global.
    Se a chave não existir, insere. Se existir, atualiza o valor.
    """
    conn = get_db_conn()
    with conn.cursor() as cur:
        if typ is not None:
            cur.execute("""
                INSERT INTO settings (key, value, type, updated_at)
                VALUES (%s, %s, %s, now())
                ON CONFLICT (key) DO UPDATE
                SET value = EXCLUDED.value,
                    type = EXCLUDED.type,
                    updated_at = now();
            """, (key, value, typ))
        else:
            cur.execute("""
                INSERT INTO settings (key, value, updated_at)
                VALUES (%s, %s, now())
                ON CONFLICT (key) DO UPDATE
                SET value = EXCLUDED.value,
                    updated_at = now();
            """, (key, value))
    conn.commit()
    conn.close()


def get_all_settings():
    conn = get_db_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT key, value, type, updated_at FROM settings ORDER BY key;")
        rows = cur.fetchall()
    conn.close()
    # Monta uma lista de dicts, já pronto para o Pydantic
    return [
        {
            "key": row[0],
            "value": row[1],
            "type": row[2],
            "updated_at": row[3],
        }
        for row in rows
    ]



def get_measurements_last_n_hours(bus_id: int, hours: int):
    now = datetime.utcnow()
    since = now - timedelta(hours=hours)
    conn = get_db_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT * FROM measurements
            WHERE bus_id = %s
              AND timestamp >= %s
            ORDER BY timestamp ASC;
        """, (bus_id, since))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

from datetime import datetime, timedelta

def get_measurements_last_n_minutes(bus_id: int, minutes: int):
    now = datetime.utcnow()
    since = now - timedelta(minutes=minutes)
    conn = get_db_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT * FROM measurements
            WHERE bus_id = %s
              AND timestamp >= %s
            ORDER BY timestamp ASC;
        """, (bus_id, since))
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
