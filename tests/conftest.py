import pytest
import pytest_asyncio
from app_database.models import Base
from app_database.url_database import _URL
from app_database.connect_database import get_async_session
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from main import app


@pytest_asyncio.fixture()
async def db_session():
    """
    Запускает создание тестовой базы данных
    :return: асинхронную сессию для подключения к базе данных
    """

    db_url = _URL
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаления тестовой базы данных если она существует
        await conn.run_sync(Base.metadata.create_all)  # Создание новой тестовой базы данных
        session = async_sessionmaker(engine)()
    yield session
    await session.close()


@pytest.fixture()
def test_app(db_session):
    """
    Создание приложения с переопределенной зависимостью
    :param db_session: асинхронная сессия из fixture
    :return: приложение
    """

    # get_async_session - получение асинхронной сессии в приложении
    # переопределяем на получение асинхронной сессии из fixture
    app.dependency_overrides[get_async_session] = lambda: db_session
    return app


@pytest_asyncio.fixture
async def client(test_app):
    """
    Создание тестового http-клиента, и создание тестового пользователя
    :param test_app: приложение
    :return: http-клиент
    """

    async with AsyncClient(app=test_app, base_url="http://my_tests_server") as client:
        create_user = {
            "username": "TestUser",
            "email": "test@gmail.com",
            "password": "password123",
            "password_confirm": "password123"
        }
        await client.post("user/register-user", json=create_user)
        yield client
