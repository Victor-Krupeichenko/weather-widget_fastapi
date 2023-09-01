from fastapi import APIRouter, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from weather.schemas import WeatherSchemas
from web_app.forms import model_fields_for_the_form
from weather._weather import return_weather
from web_app.csrf_token import generate_csrf_token, verify_csrf_token

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
    if request.method == "GET":
        return templates.TemplateResponse(
            "index.html", status_code=status.HTTP_200_OK, context={
                "request": request, "form": form, "csrf_token": csrf_token
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
