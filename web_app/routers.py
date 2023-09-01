from app_database.connect_database import get_async_session
from app_database.utils import object_exists_from_database
from app_database.models import User
from user.schemas import UserRegisterScheme
from fastapi import APIRouter, Request, status, HTTPException, Depends, responses
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, or_
from weather.schemas import WeatherSchemas
from weather._weather import return_weather
from web_app.forms import model_fields_for_the_form
from web_app.csrf_token import generate_csrf_token, verify_csrf_token
from web_app.web_utils import valid_form, templates_error

web_router = APIRouter(include_in_schema=False)

templates = Jinja2Templates(directory="web_app/templates")


@web_router.api_route("/", methods=["GET", "POST"])
async def get_weather_web(request: Request):
    """
    Получение прогноза погоды
    :param request: текущий HTTP запрос
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
                "request": request, "form": form, "csrf_token": csrf_token, "messages": messages
            }
        )
    elif request.method == "POST":
        form_data = await request.form()
        results = await return_weather(form_data.get("city"))
        try:
            await verify_csrf_token(request, csrf_token)  # проверяет csrf-токен
        except HTTPException:
            return templates.TemplateResponse(
                "error_csrf.html", status_code=status.HTTP_403_FORBIDDEN, context={"request": request}
            )
        csrf_token = await generate_csrf_token(request)  # генерирует новый csrf-токен
        return templates.TemplateResponse(
            "index.html", status_code=status.HTTP_200_OK, context={
                "request": request, "results": results, "form": form, "csrf_token": csrf_token
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
