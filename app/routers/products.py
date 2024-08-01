from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated

from app.models import *
from sqlalchemy import insert, select, update
from app.schemas import CreateProduct
from slugify import slugify


router = APIRouter(prefix='/products', tags=['products'])

@router.post('/create')
async def create_product(
    db: Annotated[Session, Depends(get_db)],
    create_product: CreateProduct
):
    new_product = {
        'name': create_product.name,
        'slug': slugify(create_product.name),
        'description': create_product.description,
        'price': create_product.price,
        'image_url': create_product.image_url,
        'stock': create_product.stock,
        'category_id': create_product.category,
        'rating': 0.0,
        'is_active': True
    }
    db.execute(insert(Product).values(**new_product))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.get('/all_products')
async def get_all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()

    await check_product(products)

    return products

@router.get('/product_by_category')
async def get_product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    subcategories = db.scalars(select(Category.id).where(Category.parent_id == category.id)).all()

    category_ids = [category.id] + subcategories

    products = db.scalars(
        select(Product).where(
            Product.category_id.in_(category_ids),
            Product.is_active == True,
            Product.stock > 0
        )
    ).all()

    return products

@router.get('/product_detail')
async def get_product_detail(db: Annotated[Session, Depends(get_db)], product_slug: str):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    await check_product(product)
    return product

@router.put('/update')
async def update_product(
    product_slug: str,
    update_product: CreateProduct,
    db: Annotated[Session, Depends(get_db)]
):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    await check_product(product)

    updated_values = {
        'name': update_product.name,
        'slug': slugify(update_product.name),
        'description': update_product.description,
        'price': update_product.price,
        'image_url': update_product.image_url,
        'stock': update_product.stock,
        'category_id': update_product.category,
        'rating': 0.0,
        'is_active': True
    }

    db.execute(update(Product).where(Product.slug == product_slug).values(**updated_values))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product update is successful'
    }



@router.delete('/delete')
async def delete_product(db: Annotated[Session, Depends(get_db)], product_slug: str):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    await check_product(product)

    db.execute(update(Product).where(Product.slug==product_slug).values(is_active=False))
    db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Product delete is successful'
    }


async def check_product(product):
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no product found")
    return True


# @router.get('/')
# async def all_products():
#     pass
#
#
# @router.post('/create')
# async def create_product():
#     pass
#
#
# @router.get('/{category_slug}')
# async def product_by_category(category_slug: str):
#     pass
#
#
# @router.get('/detail/{product_slug}')
# async def product_detail(product_slug: str):
#     pass
#
#
# @router.put('/detail/{product_slug}')
# async def update_product(product_slug: str):
#     pass
#
#
# @router.delete('/delete')
# async def delete_product(product_id: int):
#     pass