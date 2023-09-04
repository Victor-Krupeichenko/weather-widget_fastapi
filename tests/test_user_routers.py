import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data, response_data",
    [
        (
                {
                    "username": "TestUser", "email": "test@gmail.com", "password": "password123",
                    "password_confirm": "password123"
                },
                {
                    "error": "пользователь с таким именем или email уже существует",
                }

        ),
        (
                {
                    "username": "TestUser", "email": "teest@gmail.com", "password": "password",
                    "password_confirm": "password"
                },
                {
                    "error": ["пароль должен состоять из букв и цифр"],
                }
        ),
        (
                {
                    "username": "TestUser", "email": "test_gmail.com", "password": "password123",
                    "password_confirm": "password123"
                },
                {
                    "error": ["email адрес не прошел проверку"],
                }
        ),
        (
                {
                    "username": "TestUser", "email": "teest@gmail.com", "password": "newpassword",
                    "password_confirm": "password123"
                },
                {
                    "error": ["пароли не совпадают"],
                }
        )
    ]
)
async def test_register_user(user_data, response_data, client):
    """
    Тестирование endpoint для регистрации пользователя(только негативные тесты)
    :param user_data: данные которые поступают на вход
    :param response_data: ожидаемый ответ
    :param client: http-клиент
    """

    response = await client.post("user/register-user", json=user_data)
    assert response.json().get("error") == response_data.get("error")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data, response_data",
    [
        (
                {
                    "username": "NewUser", "password": "password123"
                },
                {
                    "error": "пользователя: NewUser не существует"
                }
        ),
        (
                {
                    "username": "TestUser", "password": "test"
                },
                {
                    "error": "неверный пароль, попробуй снова"
                }
        )
    ]
)
async def test_login_user(user_data, response_data, client):
    """
    Тестирование авторизации пользователя(только негативные тесты)
    :param user_data: данные которые поступают на вход
    :param response_data: ожидаемый ответ
    :param client: http-клиент
    """

    response = await client.post(url="user/login-user", json=user_data)
    assert response.json().get("error") == response_data.get("error")
