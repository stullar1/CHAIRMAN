from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Client:
    id: int | None
    name: str
    phone: str
    notes: str = ""
    no_show_count: int = 0


@dataclass
class Service:
    id: int | None
    name: str
    price: float
    duration_minutes: int
    buffer_minutes: int = 0


@dataclass
class Appointment:
    id: int | None
    client_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    paid: bool = False
    payment_method: Optional[str] = None
    notes: str = ""
