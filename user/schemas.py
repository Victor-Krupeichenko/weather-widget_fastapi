from pydantic import BaseModel, SecretStr, field_validator
from string import punctuation
from app_database.models import User
from email_validator import validate_email, EmailNotValidError


class UserRegisterScheme(BaseModel):
    """
    Схема валидации при регистрации пользователя
    """
    
    username: str
    email: str
    password: SecretStr
    password_confirm: SecretStr

    @field_validator("password_confirm")
    @classmethod
    def validate_password(cls, password_confirm, values):
        """Валидация поля password"""

        password = values.data.get("password").get_secret_value()
        secret_value = password_confirm.get_secret_value()
        if len(secret_value) < 5:
            return {"error": "пароль должен состоять из 5 и более символов"}
        elif secret_value.isalpha() or secret_value.isdigit():
            return {"error": "пароль должен состоять из букв и цифр"}
        elif any(char in punctuation for char in secret_value):
            return {"error": "пароль должен состоять только из букв и цифр"}
        elif secret_value != password:
            return {"error": "пароли не совпадают"}
        hashed = User.hashed(secret_value)  # хеширование пароля
        return hashed

    @field_validator("email")
    @classmethod
    def validate_email(cls, email):
        """Валидация поля email"""

        try:
            validate_email(email)
        except EmailNotValidError:
            return {"error": "email адрес не прошел проверку"}
        return email

    @field_validator("username")
    @classmethod
    def validate_username(cls, username):
        """Валидация поля username"""

        if len(username) < 5:
            return {"error": "имя пользователя должно состоять из 5 и более символов"}
        return username

    class Config:
        """Автоматически преобразует объекты sqlalchemy orm в объекты pydantic"""

        from_attributes = True


class UserLoginScheme(BaseModel):
    """
    Схема авторизации пользователя
    """

    username: str
    password: SecretStr

    @field_validator("password")
    @classmethod
    def password_to_string(cls, password):
        """Возвращает пароль в читаемом виде"""

        return password.get_secret_value()

    class Config:
        """Автоматически преобразует объекты sqlalchemy orm в объекты pydantic"""

        from_attributes = True
