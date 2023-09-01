from user.utils import valid_field
from fastapi import status


async def valid_form(scheme, data):
    """
    Валидация полей формы
    :param scheme: pydantic схема
    :param data: словарь с полями формы которым необходимо провести валидацию
    :return: результат валидации
    """
    result = scheme(**data)
    field_errors = await valid_field(result, "error")
    if field_errors:
        return field_errors
    return result


def templates_error(templates, html_template, request, csrf_token, form, errors_list, flag):
    """
    Шаблон для различных ошибок
    :param templates: указывает на место хранение html-шаблонов
    :param html_template: html-шаблон
    :param request: текущий HTTP запрос
    :param csrf_token: csrf-токен
    :param form: форму которую нужно редерить в html-шаблоне
    :param errors_list: список ошибок
    :param flag: флаг указывающий из какого endpoint был запрос
    :return: шаблонный ответ при различных ошибках
    """
    return templates.TemplateResponse(
        html_template, status_code=status.HTTP_400_BAD_REQUEST, context={
            "request": request, "error_list": errors_list,
            "csrf_token": csrf_token, "form": form, "flag": flag
        }
    )
