from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from passlib.hash import pbkdf2_sha256
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Модель User таблицы в базе данных"""

    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    history = relationship("RequestHistory", back_populates="user", cascade="all, delete")

    @classmethod
    def hashed(cls, password):
        """При регистрации хэширует пароль"""

        return pbkdf2_sha256.hash(password)


class RequestHistory(Base):
    """
    Модель History таблицы в базе данных
    в эту таблицу будет сохраниться информация о запросах пользователя если пользователь был авторизован
    """

    __tablename__ = "history"
    id = Column(Integer, primary_key=True)
    city = Column(String)
    date = Column(TIMESTAMP, default=datetime.utcnow())
    weather = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship('User', back_populates="history")
