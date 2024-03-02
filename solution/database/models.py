from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, ARRAY, TEXT, ForeignKey
from typing import Sequence


class Base(DeclarativeBase):
    pass


class Country(Base):
    __tablename__ = 'countries'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    alpha2: Mapped[str]
    alpha3: Mapped[str]
    region: Mapped[str]


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    countryCode: Mapped[str] = mapped_column(nullable=False)
    isPublic: Mapped[bool] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=True, unique=True)
    image: Mapped[str] = mapped_column(nullable=True)

    friends: Mapped[list["Friend"]] = relationship(back_populates='friend', uselist=True)

    def user_response(self):
        return {
            key: value for key, value in self.__dict__.items()
            if value is not None and key not in ['password', 'id']
        }


class Friend(Base):
    __tablename__ = 'friends'

    friend_login: Mapped[str] = mapped_column(primary_key=True)
    friend_add_data: Mapped[str]
    friend: Mapped['User'] = relationship(back_populates='friends', uselist=False)
    user_fk: Mapped[str] = mapped_column(ForeignKey('users.login'))
