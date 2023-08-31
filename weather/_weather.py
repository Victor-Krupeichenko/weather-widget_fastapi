from pyowm import OWM
from pyowm.utils.config import get_default_config
from setting_env import weather_key, language
from math import ceil


async def settings_weather(lang, key):
    """
    Настройки
    :param lang: язык на котором будет работать приложение
    :param key: ключ от api
    :return: объект менеджера
    """
    owm_api_key = key
    config_dict = get_default_config()
    config_dict['language'] = lang
    owm = OWM(owm_api_key)
    mgr = owm.weather_manager()
    return mgr


async def return_weather(city):
    """
    Возвращает погоду
    :param city: Город в котором нужно узнать погоду
    :return: словарь с данными о погоде
    """
    mgr = await settings_weather(language, weather_key)
    try:
        observation = mgr.weather_at_place(city)
    except Exception as ex:
        return {"error": ex}
    weather = observation.weather
    pressure_hpa = weather.pressure["press"]
    response = {
        "Температура": weather.temperature("celsius")["temp"],
        "Состояние погоды": weather.detailed_status,
        "Атмосферное давление": f"{ceil(pressure_hpa * 0.750062)} мм рт.ст.",
        "Скорость ветра:": f"{weather.wind()['speed']} м/c",
    }
    return response
