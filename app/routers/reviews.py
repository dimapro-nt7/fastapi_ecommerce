from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.models.reviews import Review as ReviewModel
from app.schemas import Review as ReviewSchema, ReviewCreate

from app.db_depends import get_async_db
from app.auth import get_current_buyer, get_current_admin
from app.routers.products import router as product_router

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)

async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()

@router.get("/", response_model=list[ReviewSchema])
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех отзывов.
    """
    stmt =  select(ReviewModel).join(ProductModel).where(ReviewModel.is_active == True,
                                                       ProductModel.is_active == True)
    reviews = await db.scalars(stmt)
    reviews = reviews.all()
    return reviews

@product_router.get("/{product_id}/reviews", response_model=list[ReviewSchema])
async def get_product_reviews(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех отзывов для указанного товара .
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    product = await db.scalars(stmt)
    product = product.first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    stmt =  select(ReviewModel).where(ReviewModel.is_active == True,
                                                       ReviewModel.product_id == product.id)
    reviews = await db.scalars(stmt)
    reviews = reviews.all()
    return reviews

@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate,
                        db: AsyncSession = Depends(get_async_db),
                        current_user: UserModel = Depends(get_current_buyer)):
    """
    Создаёт новый отзыв.
    """
    stmt = select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True)
    product = await db.scalars(stmt)
    product = product.first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    stmt = select(ReviewModel).where(ReviewModel.product_id == review.product_id,
                                     ReviewModel.user_id == current_user.id)
    db_review = await db.scalars(stmt)
    db_review = db_review.first()
    if db_review is not None:
        raise HTTPException(status_code=409, detail="Review already exists.")
    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    await update_product_rating(db, db_review.product_id)
    return db_review

@router.delete("/{review_id}", response_model=ReviewSchema, status_code=status.HTTP_200_OK)
async def delete_review(
        review_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_admin)
):
    """
    Удаляет отзыв по его ID.
    """
    stmt = select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active == True)
    db_review = await db.scalars(stmt)
    db_review = db_review.first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    await db.execute(update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False))
    await db.commit()
    await db.refresh(db_review)
    await update_product_rating(db, db_review.product_id)
    return db_review

