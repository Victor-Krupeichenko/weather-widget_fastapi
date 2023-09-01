from fastapi import HTTPException, status
from secrets import token_hex


async def generate_csrf_token(request):
    """
    Генерация csrf токена
    :param request: текущий HTTP запрос
    :return: csrf-токен
    """
    csrf_token = token_hex(32)
    request.session["csrf_token"] = csrf_token  # записываем csrf-токен в сессию
    return csrf_token


async def verify_csrf_token(request, csrf_token):
    """
    Проверяет csrf токен
    :param request: текущий HTTP запрос
    :param csrf_token: сгенерированный ранее csrf-токен
    :return: поднимает исключение если csrf-токен не совпадает
    """
    get_csrf_token = request.session.get("csrf_token")
    if csrf_token != get_csrf_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Неверный csrf token")
