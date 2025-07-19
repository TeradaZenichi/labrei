from fastapi import FastAPI, APIRouter, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
from models import Bus, Measurement, Setting
import crud

app = FastAPI(
    title="LabREI Microgrid API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Namespaced routers
bus_router = APIRouter(prefix="/buses", tags=["Buses"])
measurement_router = APIRouter(prefix="/buses", tags=["Measurements"])
settings_router = APIRouter(prefix="/settings", tags=["Settings"])

# ———— BUSES ————
@bus_router.get("", response_model=List[Bus])
def read_buses():
    """List all buses."""
    return crud.get_all_buses()

@bus_router.post("", response_model=int, status_code=201)
def add_bus(bus: Bus):
    """Create a new bus. Returns new internal ID."""
    return crud.create_bus(bus)

@bus_router.get("/search", response_model=Bus)
def find_bus(name: str = Query(..., description="Exact bus name to search")):
    """Get a bus by its name."""
    result = crud.get_bus_by_name(name)
    if not result:
        raise HTTPException(404, f"Bus named '{name}' not found")
    return result

@bus_router.delete("/{bus_number}", response_model=bool)
def remove_bus(
    bus_number: int = Path(..., description="Bus number to delete")
):
    deleted = crud.delete_bus_if_no_measurements(bus_number)
    if not deleted:
        raise HTTPException(400, "Cannot delete: bus has measurements or does not exist")
    return True

@bus_router.put("/{bus_number}", response_model=bool)
def change_bus(
    bus_number: int = Path(..., description="Bus number to update"),
    bus: Bus = ...
):
    updated = crud.update_bus(bus_number, bus)
    if not updated:
        raise HTTPException(404, f"Bus {bus_number} not found")
    return True

# ———— MEASUREMENTS ————
@measurement_router.get("/{bus_id}/measurements", response_model=List[Measurement])
def read_measurements(
    bus_id: int = Path(..., description="Bus number"),
    limit: int = Query(100, ge=1, le=10000, description="Max number of records")
):
    """Get the latest N measurements for a bus."""
    return crud.get_measurements(bus_id, limit)

@measurement_router.get("/{bus_id}/measurements/last", response_model=Measurement)
def read_last_measurement(
    bus_id: int = Path(..., description="Bus number")
):
    m = crud.get_last_measurement(bus_id)
    if not m:
        raise HTTPException(404, "No measurements found for this bus")
    return m

@measurement_router.get("/{bus_id}/measurements/range", response_model=List[Measurement])
def read_measurements_in_range(
    bus_id: int = Path(..., description="Bus number"),
    start: datetime = Query(..., description="Start timestamp (ISO8601)"),
    end:   datetime = Query(..., description="End timestamp (ISO8601)"),
    limit: int      = Query(100, ge=1, le=10000, description="Limit records returned")
):
    return crud.get_measurements_in_range(bus_id, start, end, limit)

@measurement_router.post("/{bus_id}/measurements", response_model=dict, status_code=201)
def add_measurement(
    bus_id: int = Path(..., description="Bus number"),
    m: Measurement = ...
):
    if m.bus_id != bus_id:
        raise HTTPException(400, "Path bus_id and payload bus_id must match")
    return crud.add_measurement(m)

@measurement_router.put(
    "/{bus_id}/measurements/{year}/{month}/{day}/{hour}/{minute}/{second}",
    response_model=bool
)
def change_measurement(
    bus_id: int = Path(..., description="Bus number"),
    year:   int = Path(..., ge=2000, le=3000),
    month:  int = Path(..., ge=1, le=12),
    day:    int = Path(..., ge=1, le=31),
    hour:   int = Path(..., ge=0, le=23),
    minute: int = Path(..., ge=0, le=59),
    second: int = Path(..., ge=0, le=59),
    new: Measurement = ...
):
    success = crud.update_measurement(
        bus_id, year, month, day, hour, minute, second, new
    )
    if not success:
        raise HTTPException(404, "Measurement not found to update")
    return True

@measurement_router.delete(
    "/{bus_id}/measurements/{year}/{month}/{day}/{hour}/{minute}/{second}",
    response_model=bool
)
def remove_measurement(
    bus_id: int = Path(..., description="Bus number"),
    year:   int = Path(..., ge=2000, le=3000),
    month:  int = Path(..., ge=1, le=12),
    day:    int = Path(..., ge=1, le=31),
    hour:   int = Path(..., ge=0, le=23),
    minute: int = Path(..., ge=0, le=59),
    second: int = Path(..., ge=0, le=59)
):
    deleted = crud.delete_measurement(bus_id, year, month, day, hour, minute, second)
    if not deleted:
        raise HTTPException(404, "Measurement not found to delete")
    return True

@measurement_router.delete("/{bus_id}/measurements", response_model=int)
def remove_all_measurements(
    bus_id: int = Path(..., description="Bus number")
):
    return crud.delete_all_measurements(bus_id)

@measurement_router.delete("/{bus_id}/measurements/range", response_model=int)
def remove_measurements_in_range(
    bus_id: int = Path(..., description="Bus number"),
    start: datetime = Query(..., description="Start timestamp (ISO8601)"),
    end:   datetime = Query(..., description="End timestamp (ISO8601)")
):
    return crud.delete_measurements_in_range(bus_id, start, end)

@measurement_router.get("/{bus_id}/measurements/lastn", response_model=List[Measurement])
def read_last_n_measurements(
    bus_id: int = Path(..., description="Bus number"),
    n: int = Query(10, ge=1, le=1000, description="Number of most recent measurements")
):
    return crud.get_last_n_measurements(bus_id, n)

@measurement_router.get("/{bus_id}/measurements/lasthours", response_model=List[Measurement])
def get_measurements_last_n_hours(
    bus_id: int = Path(..., description="Bus number"),
    hours: int = Query(24, ge=1, le=168, description="Quantidade de horas (até 7 dias = 168)")
):
    """
    Retorna todas as medições das últimas N horas para o barramento informado.
    """
    return crud.get_measurements_last_n_hours(bus_id, hours)


@measurement_router.get("/{bus_id}/measurements/lastminutes", response_model=List[Measurement])
def get_measurements_last_n_minutes(
    bus_id: int = Path(..., description="Bus number"),
    minutes: int = Query(
        60,  # valor padrão: 60 minutos (1 hora)
        ge=1, le=1440,
        description="Quantidade de minutos (1 a 1440, onde 1440 = 24h)"
    )
):
    """
    Retorna todas as medições dos últimos N minutos para o barramento informado.
    """
    return crud.get_measurements_last_n_minutes(bus_id, minutes)


# ———— SETTINGS ————
@settings_router.get("/all", response_model=List[Setting])
def list_settings():
    return crud.get_all_settings()

@settings_router.get("/{key}", response_model=Setting)
def read_setting(key: str):
    return {"key": key, "value": crud.get_setting(key)}

@settings_router.put("/{key}", response_model=dict)
def update_setting(key: str, value: str):
    crud.update_setting(key, value)
    return {"status": "updated"}





# Inclui routers na app
app.include_router(bus_router)
app.include_router(measurement_router)
app.include_router(settings_router)
