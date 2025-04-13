from typing import Optional

from pydantic import BaseModel
from typing import List
from datetime import datetime


class TableBase(BaseModel):
    table_name: str
    seats: int
    location: str


class TableResponse(TableBase):
    id: int

    class Config:
        orm_mode = True


class ReservationBase(BaseModel):

    customer_name: str
    table_id: int
    reservation_time: datetime
    duration_minutes: int


class ReservationResponse(ReservationBase):
    id: int

    class Config:
        orm_mode = True
