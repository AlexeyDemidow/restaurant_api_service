from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, text

from database import engine, AsyncSessionLocal, Base
from models import Reservation


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def check_reservation_conflicts(
    table_id: int,
    reservation_time: datetime,
    duration_minutes: int,
    db: AsyncSession
):

    start_time = reservation_time
    end_time = reservation_time + timedelta(minutes=duration_minutes)

    conflicting_reservations = await db.execute(
        select(Reservation).where(
            Reservation.table_id == table_id,
            and_(
                Reservation.reservation_time < end_time,  # Начало новой брони пересекается с существующей
                (Reservation.reservation_time + Reservation.duration_minutes * text("interval '1 minute'")) > start_time  # Конец новой брони пересекается с существующей
            )
        )
    )

    return conflicting_reservations.scalars().all()

