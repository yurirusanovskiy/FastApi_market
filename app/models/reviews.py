from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.backend.db import Base
from app.models import *


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    rating_id = Column(Integer, ForeignKey("rating.id"))
    comment = Column(String)
    comment_date = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

