from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from typing import Annotated

from app.models.reviews import Review
from app.models.rating import  Rating
from app.models.products import Product
from app.schemas import ReviewCreate
from app.backend.db_depends import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix='/review', tags=['review'])

@router.get("/all_reviews")
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    return reviews.all()

@router.get("/products_reviews/{product_id}")
async def get_product_reviews(product_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(Review, Rating).join(Rating, Review.rating_id == Rating.id).where(
            Review.product_id == product_id, Review.is_active == True
        )
    )
    reviews_with_ratings = result.all()

    if not reviews_with_ratings:
        raise HTTPException(status_code=404, detail="Reviews not found")

    reviews_list = [
        {
            "review_id": review.id,
            "user_id": review.user_id,
            "product_id": review.product_id,
            "rating_id": review.rating_id,
            "rating_grade": rating.grade,
            "comment": review.comment,
            "comment_date": review.comment_date,
            "is_active": review.is_active
        }
        for review, rating in reviews_with_ratings
    ]

    return reviews_list


@router.post("/add_review")
async def add_review(review: ReviewCreate, db: AsyncSession = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    # Проверка, что продукт существует
    product = await db.scalar(select(Product).filter(Product.id == review.product_id,
                                              Product.is_active == True))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Создание нового рейтинга
    new_rating = Rating(grade=review.grade, user_id=current_user['id'], product_id=review.product_id)
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)

    # Создание нового отзыва
    new_review = Review(user_id=current_user['id'], product_id=review.product_id, rating_id=new_rating.id,
                               comment=review.comment)
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)

    # Пересчет среднего рейтинга продукта
    ratings = (await db.execute(select(Rating).filter(Rating.product_id == review.product_id,
                                             Rating.is_active == True))).scalars().all()
    if ratings:
        new_average_rating = sum(rating.grade for rating in ratings) / len(ratings)
        product.rating = new_average_rating
        await db.commit()
        await db.refresh(product)

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put("/delete_reviews")
async def delete_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    get_user: Annotated[dict, Depends(get_current_user)],
    product_id: int
):
    if not get_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You must be an admin user for this'
        )

    review_exists = await db.scalar(select(Review.id).where(Review.product_id == product_id, Review.is_active == True))
    if review_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    await db.execute(update(Review).where(Review.product_id == product_id).values(is_active=False))
    await db.execute(update(Rating).where(Rating.product_id == product_id).values(is_active=False))

    await db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Reviews and ratings deactivated successfully"
    }
