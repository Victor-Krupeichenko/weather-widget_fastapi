from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .url_database import _URL

engine = create_async_engine(_URL, future=True)  # future=True - использование асинхронных версий операций
async_session = async_sessionmaker(engine)


async def get_async_session():
    """Получает асинхронную сессию"""
    async with async_session() as session:
        yield session
