async def object_exists_from_database(query, session):
    """
    Проверяет, существует ли объект в базе данных
    :param query: запрос к базе данных
    :param session: асинхронная сессия для подключения к базе данных
    :return: объект либо None
    """

    result = await session.execute(query)
    exists_object = result.scalar()
    return exists_object
