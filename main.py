from fastapi import FastAPI
from user.routers import user_router
from weather.routers import weather_router

app = FastAPI(
    title="Погода",
    description="Приложение для показа погоды в разных городах",
    version="0.1.0",
    contact={
        "name": "Victor",
        "email": "krupeichenkovictor@gmail.com"
    }
)
app.include_router(user_router)
app.include_router(weather_router)