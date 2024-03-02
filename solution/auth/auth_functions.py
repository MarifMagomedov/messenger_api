import re
from datetime import datetime, timedelta
from string import ascii_lowercase, ascii_uppercase
from fastapi.responses import JSONResponse
from jose import jwt
from passlib.context import CryptContext
from starlette import status
from .schemas import CreateUser


SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'


async def check_valid_user_data(user_data: CreateUser, db) -> JSONResponse | None:
    error = None
    check_user_exists = db.check_user_with_email_and_phone(user_data.email, user_data.login, user_data.phone)
    if check_user_exists:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                'reason': 'Юзер с таким email/login/phone уже существует!'
            }
        )
    if not re.fullmatch(r'[a-zA-Z0-9-]{1,30}', user_data.login) or user_data.login == 'my':
        error = 'Вы ввели некорректный логин!'
    elif not 1 <= len(user_data.email) <= 50:
        error = 'Вы ввели некорректный email'
    elif (
        not 6 <= len(user_data.password) <= 100
        or not any(i in ascii_lowercase for i in user_data.password)
        or not any(i in ascii_uppercase for i in user_data.password)
        or not any(i in '0123456789' for i in user_data.password)
    ):
        error = 'Вы ввели некорректный пароль!'
    elif not db.check_country_code(user_data.countryCode):
        error = 'Вы ввели некорректный код страны'
    elif user_data.phone is not None:
        if not re.fullmatch(r'\+\d+', user_data.phone):
            error = 'Вы ввели некорректный номер телефона!'
    elif user_data.phone is not None:
        if len(user_data.image) <= 200:
            error = 'Вы отправили некорректное фото!!'
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'reason': error
        }
    ) if error is not None else error


async def authenticate_user(login: str, password: str, db, bcrypt_context: CryptContext) -> JSONResponse:
    user = db.check_user(login=login)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Пользователь с указанным логином и паролем не найден'
            }
        )
    if not bcrypt_context.verify(password, user.password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Вы ввели неправильный пароль!'
            }
        )
    return user
