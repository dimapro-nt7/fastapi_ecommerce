# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
#
# # Строка подключения для SQLite
# DATABASE_URL = "sqlite:///ecommerce.db"
#
# # Создаём Engine
# engine = create_engine(DATABASE_URL, echo=True)
#
# # Настраиваем фабрику сеансов
# SessionLocal = sessionmaker(bind=engine)


# --------------- Асинхронное подключение к PostgreSQL -------------------------

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Строка подключения для PostgreSQl
DATABASE_URL = "postgresql+asyncpg://ecommerce_user:12345678@localhost:5432/ecommerce_db"
# DATABASE_URL=postgresql+asyncpg://ecommerce_user:12345678@localhost:5432/ecommerce_db?async_fallback=false&timeout=30&prepared_statement_cache_size=0&server_side_cursors=true

# Создаём Engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass
