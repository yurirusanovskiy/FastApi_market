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
