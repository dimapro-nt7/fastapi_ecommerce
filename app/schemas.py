from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    """
    name: str = Field(min_length=3, max_length=50,
                      description="Название категории (3-50 символов)")
    parent_id: Optional[int] = Field(None, description="ID родительской категории, если есть")

class Category(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор категории")
    name: str = Field(description="Название категории")
    parent_id: Optional[int] = Field(None, description="ID родительской категории, если есть")
    is_active: bool = Field(description="Активность категории")
    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    name: str = Field(min_length=3, max_length=100,
                      description="Название товара (3-100 символов)")
    description: Optional[str] = Field(None, max_length=500,
                                       description="Описание товара (до 500 символов)")
    price: float = Field(gt=0, description="Цена товара (больше 0)")
    image_url: Optional[str] = Field(None, max_length=200, description="URL изображения товара")
    stock: int = Field(ge=0, description="Количество товара на складе (0 или больше)")
    category_id: int = Field(description="ID категории, к которой относится товар")

class Product(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET запросах.
    """
    id: int = Field(description="Уникальный идентификатор товара")
    name: str = Field(description="Название товара")
    description: Optional[str] = Field(None, description="Описание товара")
    price: float = Field(description="Цена товара")
    image_url: Optional[str] = Field(None, description="URL изображения товара")
    stock: int = Field(description="Количество товара на складе")
    category_id: int = Field(description="ID категории")
    seller_id: int = Field(description="Seller ID")
    rating: float = Field(description="Рейтинг товара")
    is_active: bool = Field(description="Активность товара")
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    """
    Модель для создания пользователя.
    Используется в POST и PUT запросах.
    """
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль (минимум 8 символов)")
    role: str = Field(default="buyer", pattern="^(buyer|seller|admin)$",
                      description="Роль: 'buyer', 'seller' или 'admin")

class User(BaseModel):
    """
    Модель для ответа с данными пользователя.
    Используется в GET запросах.
    """
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)

class RefreshTokenRequest(BaseModel):
    """
    RefreshTokenRequest.
    """
    refresh_token: str

class ReviewCreate(BaseModel):
    """
    Модель создания отзыва.
    Используется в POST и PUT запросах.
    """
    product_id: int = Field(description="ID товара")
    comment: Optional[str] = Field(default=None, description="Содержание отзыва")
    grade: int = Field(ge=1, le=5, description="Оценка отзыва от 1 до 5")

class Review(BaseModel):
    """
    Модель для ответа с данными отзыва.
    Используется в GET запросах.
    """
    id: int = Field(description="Уникальный идентификатор отзыва")
    user_id: int = Field(description="ID пользователя")
    product_id: int = Field(description="ID товара")
    comment: Optional[str] = Field(description="Содержание отзыва")
    comment_date: datetime = Field(description="Дата и время отзыва")
    grade: int = Field(description="Оценка отзыва")
    is_active: bool = Field(description="Активность товара")
    model_config = ConfigDict(from_attributes=True)
