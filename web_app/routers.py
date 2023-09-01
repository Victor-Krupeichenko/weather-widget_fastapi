from app_database.connect_database import get_async_session
from app_database.utils import object_exists_from_database
from app_database.models import User
from user.schemas import UserRegisterScheme, UserLoginScheme
from user.current_user import get_current_user
from fastapi import APIRouter, Request, status, HTTPException, Depends, responses
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, or_
from weather.schemas import WeatherSchemas
from weather._weather import return_weather
from weather.utils import all_requests_weathers
from web_app.forms import model_fields_for_the_form
from web_app.csrf_token import generate_csrf_token, verify_csrf_token
from web_app.web_utils import valid_form, templates_error
from passlib.hash import pbkdf2_sha256
from user.get_token import write_token_to_cookie, delete_token_to_cookies

web_router = APIRouter(include_in_schema=False)

templates = Jinja2Templates(directory="web_app/templates")


@web_router.api_route("/", methods=["GET", "POST"])
async def get_weather_web(request: Request, current_user=Depends(get_current_user)):
    """
    Получение прогноза погоды
    :param request: текущий HTTP запрос
    :param current_user: текущий пользователь
    :return: если метод get то рендерит html-форму,
    если методом post то рендерит html-форму и возвращает информацию о погоде,
    если csrf_token не прошел проверку то рендерит страницу с ошибкой
    """

    form = model_fields_for_the_form(WeatherSchemas)  # получает необходимые поля для формы
    csrf_token = await generate_csrf_token(request)  # генерирует csrf-токен
    messages = request.session.pop("messages", "")  # удаляет ключ message и возвращает его значение из сессии
    if request.method == "GET":
        return templates.TemplateResponse(
            "index.html", status_code=status.HTTP_200_OK, context={
                "request": request, "form": form, "csrf_token": csrf_token, "messages": messages,
                "current_user": current_user
            }
        )
    elif request.method == "POST":
        form_data = await request.form()
        results = await return_weather(form_data.get("city"))
        try:
            await verify_csrf_token(request, csrf_token)  # проверяет csrf-токен
        except HTTPException:
            return templates.TemplateResponse(
                "error_csrf.html", status_code=status.HTTP_403_FORBIDDEN, context={
                    "request": request, "current_user": current_user
                }
            )
        csrf_token = await generate_csrf_token(request)  # генерирует новый csrf-токен
        return templates.TemplateResponse(
            "index.html", status_code=status.HTTP_200_OK, context={
                "request": request, "results": results, "form": form, "csrf_token": csrf_token,
                "current_user": current_user
            }
        )


@web_router.api_route("/user-register", methods=["GET", "POST"])
async def web_user_register(request: Request, db_session: AsyncSession = Depends(get_async_session)):
    """
    Регистрация пользователя
    :param db_session: асинхронная сессия для подключения к базе данных
    :param request: текущий HTTP запрос
    :return: если GET-запрос рендеринг html-формы, если POST-запрос валидация полей формы,
    если все проверки прошли успешно то добавление пользователя в базу данных и перенаправление на другую страницу
    """
    form = model_fields_for_the_form(UserRegisterScheme)  # Передает в форму нужные поля
    csrf_token = await generate_csrf_token(request)  # Создает csrf-токен
    html_template = "user_register_or_user_login.html"
    flag = "register"  # Флаг, чтобы выводить правильное название кнопки и подсвечивать соответствующий пункт меню
    if request.method == "GET":
        return templates.TemplateResponse(
            html_template, status_code=status.HTTP_200_OK, context={
                "request": request, "form": form, "csrf_token": csrf_token, "flag": flag
            }
        )
    elif request.method == "POST":
        form_data = await request.form()
        data = dict(form_data)

        # Валидация полей формы
        results = await valid_form(UserRegisterScheme, data)
        if isinstance(results, list):  # Если в форме есть ошибки (ошибки хранятся в списке)
            csrf_token = await generate_csrf_token(request)
            error_list = results
            return templates_error(templates, html_template, request, csrf_token, form, error_list, flag)

        # Проверка есть такой пользователь или email в базе данных
        query = select(
            exists().where(or_(User.username == form_data.get("username"), User.email == form_data.get("email"))))
        if await object_exists_from_database(query, db_session):
            error_list = ["пользователь с таким именем или email уже зарегистрирован"]
            return templates_error(templates, html_template, request, csrf_token, form, error_list, flag)

        # Добавление нового пользователя в базу данных
        new_user = User(username=results.username, email=results.email, hashed_password=results.password_confirm)
        db_session.add(new_user)
        await db_session.commit()

        # Перенаправление на другую страницу
        redirect_url = web_router.url_path_for("get_weather_web")
        request.session["messages"] = f"пользователь {form_data.get('username')} зарегистрирован"
        return responses.RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)


@web_router.api_route("/user-login", methods=["GET", "POST"])
async def web_user_login(request: Request, db_session: AsyncSession = Depends(get_async_session)):
    """
    Авторизация пользователя
    :param request: текущий HTTP запрос
    :param db_session: асинхронная сессия для подключения к базе данных
    :return: если GET-запрос рендеринг html-формы, если POST-запрос валидация полей формы,
    если все проверки прошли успешно то авторизовавшись, перенаправляется на другую страницу
    """
    form = model_fields_for_the_form(UserLoginScheme)
    csrf_token = await generate_csrf_token(request)
    html_template = "user_register_or_user_login.html"
    flag = "login"
    if request.method == "GET":
        return templates.TemplateResponse(
            html_template, status_code=status.HTTP_200_OK, context={
                "request": request, "form": form, "csrf_token": csrf_token, "flag": flag
            }
        )
    elif request.method == "POST":
        form_data = await request.form()
        results = await valid_form(UserLoginScheme, dict(form_data))
        if isinstance(results, list):  # Если в форме есть ошибки (ошибки хранятся в списке)
            csrf_token = await generate_csrf_token(request)
            error_list = results
            return templates_error(templates, html_template, request, csrf_token, form, error_list, flag)

        # проверка находится ли пользователь в базе
        query = select(User).where(User.username == results.username)
        get_user = await object_exists_from_database(query, db_session)
        if not get_user:
            csrf_token = await generate_csrf_token(request)
            error_list = [f"пользователя: {results.username} не существует"]
            return templates_error(templates, html_template, request, csrf_token, form, error_list, flag)

        # проверка пароля
        if not pbkdf2_sha256.verify(results.password, get_user.hashed_password):
            csrf_token = await generate_csrf_token(request)
            error_list = ["неверный пароль, попробуй снова"]
            return templates_error(templates, html_template, request, csrf_token, form, error_list, flag)

        request.session["messages"] = f"пользователь {results.username} авторизован"
        redirect_url = web_router.url_path_for("get_weather_web")
        response = responses.RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
        await write_token_to_cookie(results.username, response)  # сохранение токена в cookies
        return response


@web_router.get("/user-logout")
async def web_user_logout(request: Request, current_user=Depends(get_current_user)):
    """
    Выход пользователя
    :param request:  текущий HTTP запрос
    :param current_user:  текущий пользователь
    :return: удаляет токен из cookies и перенаправляет пользователя на главную страницу
    """

    request.session["messages"] = f"{current_user.username} вышел"
    url_redirect = web_router.url_path_for("get_weather_web")
    response = responses.RedirectResponse(url_redirect, status_code=status.HTTP_302_FOUND)
    await delete_token_to_cookies(response)
    return response


@web_router.get("/all-request")
async def web_all_request_weather(
        request: Request, current_user=Depends(get_current_user), db_session: AsyncSession = Depends(get_async_session)
):
    """
    Получение всех ранее сделанных запросов на получение информации о погоде
    :param request: текущий HTTP запрос
    :param current_user: текущий пользователь
    :param db_session: асинхронная сессия для подключения к базе данных
    :return: список запросов
    """

    if not current_user:
        url_redirect = web_router.url_path_for("get_weather_web")
        request.session["message"] = ["историю запросов могут смотреть только авторизованные пользователи"]
        return responses.RedirectResponse(url_redirect, status_code=status.HTTP_302_FOUND)
    flag = "all_request"
    results = await all_requests_weathers(current_user, db_session)

    return templates.TemplateResponse(
        "all_request_weather.html", status_code=status.HTTP_200_OK, context={
            "request": request, "flag": flag, "results": results.get("data"), "current_user": current_user
        }
    )
