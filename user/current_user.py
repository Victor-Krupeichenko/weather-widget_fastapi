from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app_database.connect_database import get_async_session
from jose import jwt, JWTError
from setting_env import secret_key, algorithm, name_cookies
from sqlalchemy import select
from app_database.models import User


async def get_user(session, username):
    """
    Получает пользователя из базы данных
    :param session: асинхронная сессия для подключения к базе данных
    :param username: имя пользователя
    :return: объект пользователя или None
    """
    query = select(User).where(User.username == username)
    exists_object = await session.execute(query)
    result = exists_object.scalar()
    return result


async def get_current_user(request: Request, session: AsyncSession = Depends(get_async_session)):
    """
    Получает текущего пользователя
    :param request: объект HTTP-запроса
    :param session: асинхронная сессия для подключения к базе данных
    :return: текущего пользователя или None
    """

    try:
        cookie = request.cookies.get(name_cookies)  # получаем куки
        if cookie is None:
            return None
        scheme = cookie.split(" ")[1]  # Получаем только токен
        payload = jwt.decode(scheme, key=secret_key, algorithms=algorithm)  # декодируем токен
        username = payload.get("username")  # Из токена получаем имя пользователя
    except JWTError as ex:
        return {"error": ex}
    user = await get_user(session=session, username=username)
    if user:
        return user
    return None
