from pydantic import BaseModel
from datetime import datetime

class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category_id: int


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

class ReviewCreate(BaseModel):
    product_id: int
    grade: int
    comment: str | None


# class CreateReview(BaseModel):
#     user_id: int
#     product_id: int
#     rating_id: int
#     comment: str | None
#     comment_date: datetime | None
#
#     class Config:
#         orm_mode = True
#
# class CreateRating(BaseModel):
#     grade: int
#     user_id: int
#     product_id: int

# class ReviewResponse(BaseModel):
#     id: int
#     user_id: int
#     product_id: int
#     rating_id: int
#     comment: str | None
#     comment_date: datetime | None
#     is_active: bool
#
#     class Config:
#         orm_mode = True
#
# class ReviewWithRatingResponse(BaseModel):
#     review_id: int
#     user_id: int
#     product_id: int
#     rating_id: int
#     rating_grade: int
#     comment: str | None
#     comment_date: datetime | None
#     is_active: bool
