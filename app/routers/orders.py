import logging
from enum import Enum
from typing import List

from fastapi import Depends, HTTPException, APIRouter, Request, Header, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel, Field

from app import models
from app.database import engine, SessionLocal
from app.routers.auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

models.Base.metadata.create_all(bind=engine)


class StatusTypeEnum(str, Enum):
    ACCEPTED: str = "ACCEPTED"
    READY_FOR_PICKUP: str = "READY_FOR_PICKUP"
    OUT_FOR_DELIVERY: str = "OUT_FOR_DELIVERY"
    PICKED_UP_BY_CUSTOMER: str = "PICKED_UP_BY_CUSTOMER"


class Status(BaseModel):
    status: StatusTypeEnum = Field(title=" ",
                                   description="Use the following information to understand when to send each "
                                               "status:\n\n "
                                               "ACCEPTED: The order has been accepted by the store. Be aware that if "
                                               "you don't accept the order we will still move forward with the order, "
                                               "as we don't require an acceptance to proceed.\n\n "
                                               "READY_FOR_PICKUP: The order is ready to be picked up by a courier or "
                                               "the customer (Only available for orders delivered by Glovo "
                                               "couriers)\n\n "
                                               "OUT_FOR_DELIVERY: The courier has collected the order in the store "
                                               "and is now being delivered to the customer (Only available for "
                                               "Marketplace orders)\n\n "
                                               "PICKED_UP_BY_CUSTOMER: The order has been picked up by the customer ("
                                               "Only available for orders to be picked up by the customer) "
                                   )


class Order(BaseModel):
    store_id: int = Field(
        title=" ",
        description="Unique identifier of the store"
    )
    order_id: int = Field(
        title=" ",
        description="Unique identifier of the order to update"
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.put("/webhook/stores/{store_id}/orders/{order_id}/status",
            summary="Update order status",
            description="This method is a command. Use api/1/commands/status method to get the progress status.")
async def update_order_status(store_id: int,
                              order_id: int,
                              status: Status,
                              user: dict = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    return successful_response(201)


def successful_response(status_code: int):
    return {
        "status": status_code,
        "transaction": "Successful"
    }


def http_exception():
    return HTTPException(status_code=404, detail="Order not found")


def get_ids_from_list(a_list, needed_list):
    for i in a_list:
        emp_str = ""
        for m in str(i):
            if m.isdigit():
                emp_str = emp_str + m
        needed_list.append(int(emp_str))
