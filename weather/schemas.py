from pydantic import BaseModel, field_validator


class WeatherSchemas(BaseModel):
    """
    Схема для получения погоды по указанному городу
    """

    city: str

    @field_validator("city")
    @classmethod
    def validate_city(cls, value):
        """
        Проверяет поля city
        :param value: название города
        :return: название города если его названия состоит из двух и более символа
        """

        if len(value) < 2:
            return {"error": "название города должно состоять из 2 и более символов"}
        return value
