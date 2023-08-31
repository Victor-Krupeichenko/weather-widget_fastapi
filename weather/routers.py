from fastapi import APIRouter, Depends
from weather.schemas import WeatherSchemas
from weather._weather import return_weather
from weather.utils import all_requests_weathers
from user.current_user import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app_database.connect_database import get_async_session
from app_database.models import RequestHistory

weather_router = APIRouter(prefix="/weather", tags=["weather"])


@weather_router.post("/weather")
async def get_weather(
        city: WeatherSchemas, session: AsyncSession = Depends(get_async_session), current_user=Depends(get_current_user)
):
    """
    Получает текущую погоду
    :param city: название города
    :param session: асинхронная сессия для подключения к базе данных (если пользователь авторизован)
    :param current_user: текущий пользователь
    :return: текущую погоду
    """

    result = await return_weather(city=city.city)
    if not current_user:
        return result
    if "error" not in result:
        new_date = RequestHistory(
            city=city.city, weather=str(result), user_id=current_user.id
        )
        session.add(new_date)
        await session.commit()
    return result


@weather_router.get("/weather-all-request")
async def get_all_request_weather(
        current_user=Depends(get_current_user), session: AsyncSession = Depends(get_async_session)
):
    """
    Получает все ранее сделанные на получение погоды запросы пользователя
    :param current_user: текущий пользователь
    :param session: асинхронная сессия для подключения к базе данных
    :return: словарь со списком всех ранее сделанных запросов пользователя
    """

    if not current_user:
        return {"message": "историю запросов могут смотреть только авторизованные пользователи"}

    results = await all_requests_weathers(current_user, session)
    return results
