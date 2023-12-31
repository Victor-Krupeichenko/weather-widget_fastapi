# weather-widget_fastapi
![Python](https://img.shields.io/badge/-Python-f1f518?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/-FastAPI-74cf3c?style=flat-square&logo=fastapi)
![Postgresql](https://img.shields.io/badge/-Postgresql-1de4f2?style=flat-square&logo=postgresql)  
![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-ba7378?style=flat-square&logo=sqlalchemy)
![Alembic](https://img.shields.io/badge/-Alembic-80cced?style=flat-square&logo=Alembic)
![Pydantic](https://img.shields.io/badge/-Pydantic-E92063?style=flat-square&logo=Pydantic)
![Bootstrap](https://img.shields.io/badge/-Bootstrap-ce62f5?style=flat-square&logo=bootstrap)
![Docker](https://img.shields.io/badge/-Docker-1de4f2?style=flat-square&logo=docker)
![Git](https://img.shields.io/badge/-Git-COLOR?style=flat-square&logo=git)

Приложение для получения текущей погоды в конкретно указанном городе.
Приложение написано на Fast API
Приложение состоит из отдельных трех частей:

1. api приложения в которое входит:

- регистрация пользователя;
- авторизация пользователя;
- выход пользователя.

2. api погоды в которое входит:

- получение текущей погоды в конкретном городе;
- получение всех ранее сделанных запросов текущим пользователем на получение погоды
  (работает только если пользователь делал запросы будучи авторизованным)
- получение текущей погоды осуществляется с помощью библиотеки pyowm==3.3.0

3. web-интерфейс в который входит

- регистрация пользователя через html-форму
- авторизация пользователя через html-форму
- выход пользователя
- получение текущей погоды в конкретном городе через html-форму
- получение всех ранее сделанных запросов для получения погоды через html-форму

## Установка

1. необходимо создать в корне проекта файл .env в котором указать:
POSTGRES_DB=ваше_название_для базы данных
POSTGRES_HOST=weather_database
POSTGRES_USER=ваше_имя_пользователя
POSTGRES_PASSWORD=ваш_пароль
POSTGRES_PORT=1223(можете указать другой порт-тогда и в docker-compose.yml необходимо изменить на другой)

_SECRET_KEY=ваш_секретный_ключ_для_шифрования_токена
_ALGORITHM=HS256(можете указать свой_алгоритм_шифрования_токена)

_TOKEN_EXPIRATION_DATE=1(можете_указать_свое_время_хранения_токена) - по умолчанию 1 день
_NAME_COOKIES=своё_название_для_cookies

_WEATHER_KEY=можете получить на https://openweathermap.org/api
LANGUAGE=ru(по умолчанию русский)
SECRET_KEY_SESSIONS=свой_секретный_ключ для сессии

## Установка на локальный компьютер
- git clone https://github.com/Victor-Krupeichenko/weather-widget_fastapi.git
- pip install -r requirements.txt
- запуск через терминал:  uvicorn main:app --reload
- перейти по ссылке: http://127.0.0.1:8000 для api документации http://127.0.0.1:8000/docs

## Установка в docker
- git clone https://github.com/Victor-Krupeichenko/weather-widget_fastapi.git
- запуск через терминал(обязательно должны находится в папке проекта): docker compose up или docker-compose up
- перейти по ссылке: http://0.0.0.0:7654 для api документации http://0.0.0.0:7654/docs

## Структура проекта

В папке app_database находится что касается работы с базой данных:
1. Подключение к базе данных
2. модели таблиц базы данных
3. url-маршрут к базе данных
4. дополнительная утилита которая делает запрос в базу данных на проверку пользователя

В папке migrations находятся:
1. папка version содержит миграцию на создание таблиц в базе данных
2. в env.py указаны переменные окружения для подключения к базе данных и метаданные моделей таблиц базы данных
3. служебные файлы библиотеки alembic

B папке start_docker находится:
1. bash-скрипт который запускает миграцию на создание таблиц базы данных перед запуском самого приложения

В папке tests находятся:
- Тесты для endpoint api регистрации и авторизации пользователя

В папке user находятся:
1. current_user.py - получение текущего пользователя и с вспомогательной функцией
2. get_token.py - создание токена(для регистрации пользователя), запись токена в cookies и удаление токена из cookies(при выходе пользователя)
3. routers.py - endpoints для регистрации, авторизации и выхода пользователя
4. schemas.py - pydantic схемы для валидации данных полученных от пользователя
5. utils.py - вспомогательная функция

В папке weather находится:
1. _weather.py - настройки для библиотеки pyowm(получения погоды)
2. routers.py - endpoints для получения погоды в конкретном городе и получение всех ранее сделанных запросов на получение погоды
3. schemas.py - pydantic схема
4. utils.py - вспомогательная функция

В папке web_app(веб-составляющая приложения) находятся:
1. папка static содержит .png - файл для навигационной панели
2. папка templates:
- папка _inc - содержит подключаемые html-шаблоны
- html-шаблоны составляющие web-часть приложения
3. csrf_token.py - генерирует и проверяет csrf-токен для защиты от несанкционированных действий злоумышленников
4. forms.py - получает из pydantic схемы необходимые поля для генерации html-формы
5. routers.py - содержит endpoints для:
- для регистрации пользователя;
- авторизации пользователя;
- выхода пользователя;
- получения текущей погоды в указанном городе;
- получение всех ранее сделанных запросов на получение погоды
6. web_utils.py - вспомогательные функции

- alembic.ini содержит маршрут для подключения alembic к базе данных
- docker-compose.yml содержит описание запуска проекта в docker
- Dockerfile содержит инструкции для создания docker-образа
- main.py по сути это файл который запускает само приложение
- requirements.txt в нем находятся все необходимые для работы приложения библиотеки и зависимости
- setting_env.py - настройки имен переменно окружения


## Контакты:
Виктор
# Email:
- krupeichenkovictor@gmail.com
- victor_krupeichenko@hotmail.com
# Viber:
- +375447031953 

