from fastapi import FastAPI
from user.routers import user_router
from weather.routers import weather_router
from web_app.routers import web_router
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from setting_env import secret_key_session

app = FastAPI(
    title="Погода",
    description="Приложение для показа погоды в разных городах",
    version="0.1.0",
    contact={
        "name": "Victor",
        "email": "krupeichenkovictor@gmail.com"
    }
)
app.add_middleware(SessionMiddleware, secret_key=secret_key_session)  # управление сессиями
app.include_router(user_router)
app.include_router(weather_router)
app.mount("/static", StaticFiles(directory="web_app/static"), name="static")
app.include_router(web_router)
