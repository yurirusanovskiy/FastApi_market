from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from sqlalchemy import select, insert, update
from app.schemas import CreateProduct
from app.models import *

from app.routers.auth import get_current_user

router = APIRouter(prefix='/products', tags=['products'])



@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0))
    if products is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return products.all()


@router.post('/create')
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct, get_user:
                          Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        await db.execute(insert(Product).values(name=create_product.name,
                                          description=create_product.description,
                                          price=create_product.price,
                                          image_url=create_product.image_url,
                                          stock=create_product.stock,
                                          category_id=create_product.category,
                                          rating=0.0,
                                          slug=slugify(create_product.name),
                                          supplier_id=get_user.get('id')))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )


@router.get('/{category_slug}')
async def product_by_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    subcategories = await db.scalars(select(Category).where(Category.parent_id == category.id))
    categories_and_subcategories = [category.id] + [i.id for i in subcategories.all()]
    products_category = await db.scalars(
        select(Product).where(Product.category_id.in_(categories_and_subcategories), Product.is_active == True,
                              Product.stock > 0))
    return products_category.all()


@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(
        select(Product).where(Product.slug == product_slug, Product.is_active == True, Product.stock > 0))
    if product is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return product


@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         update_product_model: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):

    product_update = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )

    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == product_update.supplier_id or get_user.get('is_admin'):
            await db.execute(
                update(Product).where(Product.slug == product_slug)
                .values(name=update_product_model.name,
                        description=update_product_model.description,
                        price=update_product_model.price,
                        image_url=update_product_model.image_url,
                        stock=update_product_model.stock,
                        category_id=update_product_model.category,
                        slug=slugify(update_product_model.name)))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product update is successful'
            }
        else:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )


@router.delete('/delete')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    product_delete = await db.scalar(select(Product).where(Product.id == product_id))
    if product_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == product_delete.supplier_id or get_user.get('is_admin'):
            await db.execute(update(Product).where(Product.id == product_id).values(is_active=False))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )

# @router.post('/create')
# async def create_product(
#     db: Annotated[Session, Depends(get_db)],
#     create_product: CreateProduct
# ):
#     new_product = {
#         'name': create_product.name,
#         'slug': slugify(create_product.name),
#         'description': create_product.description,
#         'price': create_product.price,
#         'image_url': create_product.image_url,
#         'stock': create_product.stock,
#         'category_id': create_product.category,
#         'rating': 0.0,
#         'is_active': True
#     }
#     db.execute(insert(Product).values(**new_product))
#     db.commit()
#     return {
#         'status_code': status.HTTP_201_CREATED,
#         'transaction': 'Successful'
#     }

# @router.get('/all_products')
# async def get_all_products(db: Annotated[Session, Depends(get_db)]):
#     products = db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()
#
#     await check_product(products)
#
#     return products

# @router.get('/product_by_category')
# async def get_product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
#     category = db.scalar(select(Category).where(Category.slug == category_slug))
#     if not category:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
#
#     subcategories = db.scalars(select(Category.id).where(Category.parent_id == category.id)).all()
#
#     category_ids = [category.id] + subcategories
#
#     products = db.scalars(
#         select(Product).where(
#             Product.category_id.in_(category_ids),
#             Product.is_active == True,
#             Product.stock > 0
#         )
#     ).all()
#
#     return products

# @router.get('/product_detail')
# async def get_product_detail(db: Annotated[Session, Depends(get_db)], product_slug: str):
#     product = db.scalar(select(Product).where(Product.slug == product_slug))
#     await check_product(product)
#     return product
#
# @router.put('/update')
# async def update_product(
#     product_slug: str,
#     update_product: CreateProduct,
#     db: Annotated[Session, Depends(get_db)]
# ):
#     product = db.scalar(select(Product).where(Product.slug == product_slug))
#     await check_product(product)
#
#     updated_values = {
#         'name': update_product.name,
#         'slug': slugify(update_product.name),
#         'description': update_product.description,
#         'price': update_product.price,
#         'image_url': update_product.image_url,
#         'stock': update_product.stock,
#         'category_id': update_product.category,
#         'rating': 0.0,
#         'is_active': True
#     }
#
#     db.execute(update(Product).where(Product.slug == product_slug).values(**updated_values))
#     db.commit()
#     return {
#         'status_code': status.HTTP_200_OK,
#         'transaction': 'Product update is successful'
#     }
#
#
#
# @router.delete('/delete')
# async def delete_product(db: Annotated[Session, Depends(get_db)], product_slug: str):
#     product = db.scalar(select(Product).where(Product.slug == product_slug))
#     await check_product(product)
#
#     db.execute(update(Product).where(Product.slug==product_slug).values(is_active=False))
#     db.commit()
#
#     return {
#         'status_code': status.HTTP_200_OK,
#         'transaction': 'Product delete is successful'
#     }
#
#
# async def check_product(product):
#     if product is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no product found")
#     return True
