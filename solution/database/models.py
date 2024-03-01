from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger


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