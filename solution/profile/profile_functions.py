import re
from string import ascii_lowercase, ascii_uppercase
from starlette import status
from starlette.responses import JSONResponse

from .schemas import UserUpdate


async def check_valid_update_user_data(user_data: UserUpdate, db) -> JSONResponse | None:
    error = None
    if not db.check_country_code(user_data.countryCode.upper()):
        error = 'Вы ввели некорректный код страны'
    elif user_data.phone is not None:
        if not re.fullmatch(r'\+\d{1,20}', user_data.phone):
            error = 'Вы ввели некорректный номер телефона!'
    elif user_data.image is not None:
        if not 1 <= len(user_data.image) <= 200:
            error = 'Вы отправили некорректное фото!'
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'reason': error
        }
    ) if error is not None else error


async def check_valid_password(password: str) -> bool:
    return (
        not 6 <= len(password) <= 100
        or not any(i in ascii_lowercase for i in password)
        or not any(i in ascii_uppercase for i in password)
        or not any(i in '0123456789' for i in password)
    )