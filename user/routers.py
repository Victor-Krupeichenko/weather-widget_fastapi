from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from user.schemas import UserLoginScheme, UserRegisterScheme
from app_database.connect_database import get_async_session
from app_database.models import User
from sqlalchemy import select, exists, or_
from app_database.utils import object_exists_from_database
from user.utils import valid_field
from passlib.hash import pbkdf2_sha256
from user.get_token import write_token_to_cookie
from setting_env import name_cookies
from current_user import get_current_user

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.post("/register-user")
async def register_user(user: UserRegisterScheme, session: AsyncSession = Depends(get_async_session)):
    """
    Endpoint для регистрации пользователя
    :param user: логин, пароль, email
    :param session: асинхронная сессия для подключения к базе данных
    :return: имя пользователя и статус
    """

    error = await valid_field(user, "error")
    if error:
        return {"error": error}
    query = select(exists().where(or_(User.username == user.username, User.email == user.email)))
    if await object_exists_from_database(query, session):
        return {"error": "пользователь с таким именем или email уже существует"}
    new_user = User(username=user.username, email=user.email, hashed_password=user.password_confirm)
    session.add(new_user)
    await session.commit()
    return {
        "data": f"Пользователь: {user.username} успешно зарегистрировался",
        "status": status.HTTP_201_CREATED
    }


@user_router.post("/login-user")
async def user_login(user: UserLoginScheme, response: Response, session: AsyncSession = Depends(get_async_session)):
    """
    Endpoint для авторизации пользователя
    :param user: логин и пароль которые ввел пользователь
    :param response: объект HTTP запроса
    :param session: асинхронная сессия для подключения к базе данных
    :return: имя пользователя и токен
    """

    query = select(User).where(User.username == user.username)
    get_user = await object_exists_from_database(query, session)
    if not get_user:
        return {"error": f"пользователя: {user.username} не существует"}
    if not pbkdf2_sha256.verify(user.password, get_user.hashed_password):
        return {"error": "неверный пароль, попробуй снова"}
    jwt_token = await write_token_to_cookie(user.username, response)
    return {
        "data": f"{user.username} успешно авторизован",
        "token": jwt_token
    }


@user_router.get("/logout-user")
async def user_logout(response: Response, current_user=Depends(get_current_user)):
    """
    Endpoint для выхода пользователя
    :param response: объект HTTP запроса
    :param current_user: текущий пользователь
    :return: сообщение для пользователя, что он вышел
    """
    response.delete_cookie(key=name_cookies)
    return {"message": f"пользователь {current_user.username} вышел"}
