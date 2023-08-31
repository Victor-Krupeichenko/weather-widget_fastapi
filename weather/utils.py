from sqlalchemy import select
from app_database.models import RequestHistory


async def all_requests_weathers(current_user, session):
    """
    Показывает все запросы погоды которые пользователь делал ранее
    :param current_user: текущий пользователь
    :param session: асинхронная сессия для подключения к базе данных
    :return: список ранее сделанных запросов или сообщение, что ранее запросов не было
    """
    query = select(RequestHistory).where(RequestHistory.user_id == current_user.id)
    execute = await session.execute(query)
    results = execute.scalars().all()
    if len(results) == 0:
        return {"message": "ранее сервис не был использован либо ты делал запросы не авторизованным"}
    return {
        "data": results
    }
