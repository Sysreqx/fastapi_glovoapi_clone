from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    external_number = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    guest_count = Column(Integer, nullable=True)
    guests = Column(Integer, nullable=True)
    tab_name = Column(Integer, nullable=True)
    is_closed = Column(Boolean, default=False)
    source_key = Column(String, nullable=True)
    order_type_id = Column(String, nullable=True)

    items_owner = relationship("Items", back_populates="order")


class Items(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Integer, nullable=True)
    positionId = Column(Integer, nullable=True)
    amount = Column(Integer)
    productSizeId = Column(Integer, nullable=True)
    comment = Column(String, nullable=True)

    order_id = Column(Integer, ForeignKey("orders.id"))
    order = relationship("Orders", back_populates="items_owner")
