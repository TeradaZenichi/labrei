from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class Bus(BaseModel):
    bus_number: int
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    nominal_voltage: Optional[float] = None
    nominal_current: Optional[float] = None
    extra_parameters: Optional[Dict] = None

class Measurement(BaseModel):
    bus_id: int
    timestamp: datetime
    freq_a: Optional[int]
    freq_b: Optional[int]
    freq_c: Optional[int]
    va_rms: Optional[int]
    vb_rms: Optional[int]
    vc_rms: Optional[int]
    ia_rms: Optional[int]
    ib_rms: Optional[int]
    ic_rms: Optional[int]
    pa: Optional[int]
    pb: Optional[int]
    pc: Optional[int]
    sa: Optional[int]
    sb: Optional[int]
    sc: Optional[int]
    qa: Optional[int]
    qb: Optional[int]
    qc: Optional[int]
    pfa: Optional[int]
    pfb: Optional[int]
    pfc: Optional[int]
    va_p: Optional[int]
    vb_p: Optional[int]
    vc_p: Optional[int]
    va_th: Optional[int]
    vb_th: Optional[int]
    vc_th: Optional[int]
    ia_p: Optional[int]
    ib_p: Optional[int]
    ic_p: Optional[int]
    ia_th: Optional[int]
    ib_th: Optional[int]
    ic_th: Optional[int]


class Setting(BaseModel):
    key: str
    value: int  # ou Union[str, int, float] se preferir
    type: Optional[str] = "int"
    updated_at: Optional[datetime] = None
