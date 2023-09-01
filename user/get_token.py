from jose import jwt
from setting_env import secret_key, algorithm, token_expiration_date
from datetime import datetime, timedelta
from fastapi import Response
from setting_env import name_cookies


def create_success_token(data: dict):
    """
    Создание токена
    :param data: словарь с данными для кодирования токена
    :return: закодированный токен
    """

    expire = datetime.now() + timedelta(days=int(token_expiration_date))  # срок действия токена
    encode_jwt = jwt.encode({**data, "exp": expire}, key=secret_key, algorithm=algorithm)  # кодирование токена
    return encode_jwt


async def write_token_to_cookie(username, response: Response):
    """
    Записывает токен в cookies
    :param username: имя пользователя
    :param response: объект HTTP ответа
    :return: токен
    """

    jwt_token = create_success_token(data={"username": username})
    response.set_cookie(key=name_cookies, value=f"Bearer {jwt_token}", httponly=True)
    return jwt_token


async def delete_token_to_cookies(response: Response):
    """
    Удаляет токен из cookies
    :param response: объект HTTP ответа
    """
    response.delete_cookie(key=name_cookies)
