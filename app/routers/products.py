from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update

from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate

from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db

from app.models.users import User as UserModel
from app.auth import get_current_seller

# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех товаров.
    """
    stmt =  select(ProductModel).join(CategoryModel).where(ProductModel.is_active == True,
                                                       CategoryModel.is_active == True,
                                                       ProductModel.stock > 0)
    products = await db.scalars(stmt)
    products = products.all()
    return products

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: ProductCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_seller)
):
    """
    Создаёт новый товар.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id,
                                           CategoryModel.is_active == True)
    category = await db.scalars(stmt)
    category = category.first()
    if category is None:
        raise HTTPException(status_code=400, detail="Category not found")
    db_product = ProductModel(**product.model_dump(), seller_id = current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    stmt = select(CategoryModel).where(CategoryModel.is_active == True, CategoryModel.id == category_id)
    category = await db.scalars(stmt)
    category = category.first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    stmt = select(ProductModel).where(ProductModel.is_active == True, ProductModel.category_id == category_id)
    products = await db.scalars(stmt)
    products = products.all()
    return products

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.is_active == True, ProductModel.id == product_id)
    product = await db.scalars(stmt)
    product = product.first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    stmt = select(CategoryModel).where(CategoryModel.is_active == True, CategoryModel.id == product.category_id)
    category = await db.scalars(stmt)
    category = category.first()
    if category is None:
        raise HTTPException(status_code=400, detail="Category not found")
    return product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
        product_id: int,
        product: ProductCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_seller)
):
    """
    Обновляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.is_active == True, ProductModel.id == product_id)
    db_product = await db.scalars(stmt)
    db_product = db_product.first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")
    stmt = select(CategoryModel).where(CategoryModel.is_active == True, CategoryModel.id == product.category_id)
    category = await db.scalars(stmt)
    category = category.first()
    if category is None:
        raise HTTPException(status_code=400, detail="Category not found")
        # Обновление категории
    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def delete_product(
        product_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_seller)
):
    """
    Удаляет товар по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    db_product = await db.scalars(stmt)
    db_product = db_product.first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")
    await db.execute(update(ProductModel).where(ProductModel.id == product_id).values(is_active=False))
    await db.commit()
    return db_product
