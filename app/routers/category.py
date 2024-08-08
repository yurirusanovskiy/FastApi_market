from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated

from app.models import *
from sqlalchemy import insert, select, update
from app.schemas import CreateCategory
from slugify import slugify

from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.auth import get_current_user

router = APIRouter(prefix='/category', tags=['category'])

@router.post('/create')
async def create_category(db: Annotated[AsyncSession, Depends(get_db)], create_category: CreateCategory, get_user:
                          Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        await db.execute(insert(Category).values(name=create_category.name,
                                           parent_id=create_category.parent_id,
                                           slug=slugify(create_category.name)))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be admin user for this'
        )

@router.get('/all_categories')
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    # categories = db.query(Category).filter(Category.is_active == True).all()
    categories = await db.scalars(
        select(Category).where(Category.is_active == True)
    )
    return categories.all()

@router.delete('/delete')
async def delete_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: int,
                          get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        category = await db.scalar(select(Category).where(Category.id == category_id))
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="There is no category found")

        await db.execute(update(Category).where(Category.id == category_id).values(is_active=False))
        # delete(Category).where(Category.id == category_id)
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Category delete is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be admin user for this'
        )

@router.put('/update_category')
async def update_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: int,
                          update_category: CreateCategory, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        category = await db.scalar(select(Category).where(Category.id == category_id))
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="There is no category found"
                                )
        await db.execute(update(Category).where(Category.id == category_id).values(
            name=update_category.name,
            slug=slugify(update_category.name),
            parent_id=update_category.parent_id
        ))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Category update is successful'
            }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be admin user for this'
        )

