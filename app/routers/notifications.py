from fastapi import Depends, HTTPException, APIRouter, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from enum import Enum

from app import models
from app.database import engine, SessionLocal
from app.routers.auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)

models.Base.metadata.create_all(bind=engine)


class MessageType(str, Enum):
    order_attention = "order_attentions"
    second_one = "enum_in_redoc"
    third_one = "doesnt_display_properly"


class Notification(BaseModel):
    order_source: str = Field(
        title=" ", description="Order source."
    )
    order_id: int = Field(
        title=" ", description="Order ID."
    )
    additional_info: str = Field(
        title=" ", description="Additional info about the problem."
    )
    # message_type: str = Field(
    #     title=" ", description="Default: order_attentions"
    # )
    message_type: MessageType = Query(
        default=..., title=" ", description=" "
    )
    organization_id: int = Field(
        title=" ", description="Organization UOC Id."
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/send",
             summary="Send notification to external systems (iikoFront and iikoWeb).")
async def send_notification_to_external_system(notification: Notification,
                                               user: dict = Depends(get_current_user),
                                               db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    notification_model = models.Operations()

    notification_model.order_source = notification.order_source
    notification_model.order_id = notification.order_id
    notification_model.additional_info = notification.additional_info
    notification_model.message_type = notification.message_type
    notification_model.organization_id = notification.organization_id
    notification_model.owner_id = user.get("id")

    db.add(notification_model)
    db.commit()

    notification_model_db = db.query(models.Operations) \
        .filter(models.Operations.order_source == notification_model.order_source) \
        .filter(models.Operations.order_id == notification_model.order_id) \
        .filter(models.Operations.additional_info == notification_model.additional_info) \
        .filter(models.Operations.organization_id == notification_model.organization_id) \
        .filter(models.Operations.owner_id == user.get("id")) \
        .first()

    if notification_model_db is None:
        return http_exception()

    return notification_model_db.id


def successful_response(status_code: int):
    return {
        "status": status_code,
        "transaction": "Successful"
    }


def http_exception():
    return HTTPException(status_code=404, detail="User not found")
