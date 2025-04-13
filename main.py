from fastapi import FastAPI, HTTPException, Path, Query, Body, Depends, Response
from typing import Optional, List, Dict, Annotated

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from starlette import status
from starlette.responses import Response, RedirectResponse

from models import Table, Reservation
from database import engine, AsyncSessionLocal
from schemas import TableBase, TableResponse, ReservationBase, ReservationResponse
from utils import init_db, get_db, check_reservation_conflicts

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get(
    "/tables/",
    response_model=List[TableResponse],
    tags=["Столики"],
    summary="Список всех столиков",
)
async def get_tables(db: AsyncSession = Depends(get_db)) -> List[TableResponse]:
    result = await db.execute(select(Table))
    tables = result.scalars().all()

    tables_responses = []

    for table in tables:
        tables_responses.append(TableResponse(
            id=table.id,
            table_name=table.table_name,
            seats=table.seats,
            location=table.location,
        ))

    return tables_responses


@app.post(
    "/posts/",
    response_model=TableResponse,
    tags=["Столики"],
    summary="Создать новый столик",
)
async def create_table(table: TableBase, db: AsyncSession = Depends(get_db)) -> TableResponse:
    db_table = Table(table_name=table.table_name, seats=table.seats, location=table.location)
    db.add(db_table)
    await db.commit()
    await db.refresh(db_table)

    table_response = TableResponse(
        id=db_table.id,
        table_name=db_table.table_name,
        seats=db_table.seats,
        location=db_table.location,
    )
    return table_response


@app.delete(
    "/tables/{id}/",
    tags=["Столики"],
    summary="Удалить столик",
)
async def delete_table(db: AsyncSession = Depends(get_db), id: int = Path(..., description="ID столика", example=0)) -> Response:
    result = await db.execute(select(Table).where(Table.id == id))
    table_to_delete = result.scalars().first()
    if not table_to_delete:
        raise HTTPException(
            status_code=404,
            detail=f"Столик с ID {id} не найден",
        )

    await db.delete(table_to_delete)
    await db.commit()

    return Response(f"Столик с ID {id} удален")


@app.get(
    "/reservations/",
    response_model=List[ReservationResponse],
    tags=["Брони"],
    summary="Список всех броней",
)
async def get_reservations(db: AsyncSession = Depends(get_db)) -> List[ReservationResponse]:
    result = await db.execute(select(Reservation))
    reservations = result.scalars().all()

    res_responses = []

    for res in reservations:
        res_responses.append(ReservationResponse(
            id=res.id,
            customer_name=res.customer_name,
            table_id=res.table_id,
            reservation_time=res.reservation_time,
            duration_minutes=res.duration_minutes,
        ))

    return res_responses


@app.post(
    "/reservations/",
    response_model=ReservationResponse,
    tags=["Брони"],
    summary="Создать новую бронь",
)
async def create_reservation(res: ReservationBase, db: AsyncSession = Depends(get_db)) -> ReservationResponse:
    conflicting_reservations = await check_reservation_conflicts(
        table_id=res.table_id,
        reservation_time=res.reservation_time.replace(tzinfo=None),
        duration_minutes=res.duration_minutes,
        db=db
    )

    if conflicting_reservations:
        raise HTTPException(
            status_code=409,
            detail="На это время столик занят"
        )
    db_res = Reservation(
        customer_name=res.customer_name,
        table_id=res.table_id,
        reservation_time=res.reservation_time.replace(tzinfo=None),
        duration_minutes=res.duration_minutes
    )
    db.add(db_res)
    await db.commit()
    await db.refresh(db_res)

    res_response = ReservationResponse(
        id=db_res.id,
        customer_name=res.customer_name,
        table_id=res.table_id,
        reservation_time=res.reservation_time,
        duration_minutes=res.duration_minutes
    )
    return res_response


@app.delete(
    "/reservations/{id}/",
    tags=["Брони"],
    summary="Удалить бронь",
)
async def delete_table(db: AsyncSession = Depends(get_db), id: int = Path(..., description="ID брони", example=0)) -> Response:
    result = await db.execute(select(Reservation).where(Reservation.id == id))
    res_to_delete = result.scalars().first()
    if not res_to_delete:
        raise HTTPException(
            status_code=404,
            detail=f"Бронь с ID {id} не найдена",
        )

    await db.delete(res_to_delete)
    await db.commit()

    return Response(f"Бронь с ID {id} удалена")
