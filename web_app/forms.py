def model_fields_for_the_form(scheme):
    """
    Получает все необходимые поля для html-формы
    :param scheme: pydantic схема
    :return: список полей
    """
    field_list = list()
    fields = scheme.model_json_schema().get("properties")
    for field in fields:
        field_list.append({"title": field, "required": "required"})
    return field_list
