async def valid_field(obj, key):
    """
    Получает ошибки данных если такие есть
    :param obj: результат валидации данных
    :param key: ключ словаря под которым находятся ошибки
    :return: список с ошибками или пустой список если ошибок не было
    """

    error_list = list()
    for _, j in obj:
        if isinstance(j, dict):
            error_list.append(j[key])
    return error_list
