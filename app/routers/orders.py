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


class Attribute(BaseModel):
    id: int = Field(
        title=" ",
        description="Unique identifier of the attribute within a store"
    )
    quantity: int = Field(
        title=" ",
        description="Attribute quantity"
    )


class AttributeNotRequired(BaseModel):
    id: int = Field(
        title=" ",
        description="Unique identifier of the attribute within a store"
    )
    quantity: int = Field(
        title=" ",
        description="Product quantity"
    )


class Product(BaseModel):
    id: int = Field(
        title=" ",
        description="Unique identifier of the product within a store"
    )
    quantity: int = Field(
        title=" ",
        description="Product quantity"
    )
    attributes: list[AttributeNotRequired] = Field(
        title=" ",
        description="List of attributes associated with the replaced product"
    )


class AddedProduct(BaseModel):
    id: int = Field(
        title=" ",
        description="Unique identifier of the product within a store"
    )
    quantity: int = Field(
        title=" ",
        description="Product quantity"
    )
    attributes: list[Attribute] = Field(
        title=" ",
        description="List of attributes associated with the replaced product"
    )


class Replacement(BaseModel):
    purchased_product_id: int = Field(
        title=" ",
        description="Unique identifier of the purchased product (purchased_product_id) that will be replaced in the "
                    "original order "
    )
    product: Product = Field(
        title=" ",
        description="The replacement product"
    )


class Order(BaseModel):
    replacements: list[Replacement] = Field(
        title=" ",
        description="List of products to replace in the order"
    )
    removed_purchases: list[str] = Field(
        title=" ",
        description="List of unique identifiers of purchased products (purchased_product_id) to be removed from the "
                    "order "
    )
    added_products: list[AddedProduct] = Field(
        title=" ",
        description="List of products to be added to the order"
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


@router.post("/webhook/stores/{store_id}/orders/{order_id}/status",
             summary="Modify order products",
             description="This option allows an update to the products and attributes of an order when a customer asks "
                         "for changes or the order cannot be fulfilled as initially requested.\n\n "
                         "Depending on the information in the request body, we will replace products / attributes from "
                         "the order, remove products from the order or add products to the order.\n\n "
                         "An order can only be modified once. An attempt to modify an order more than once will result "
                         "in an error.")
async def modify_order_products(store_id: int,
                                order_id: int,
                                order: Order,
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
