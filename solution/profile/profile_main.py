from fastapi import APIRouter, Depends, Request
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from jose import JWTError
from passlib.context import CryptContext
from starlette import status

from .profile_functions import check_valid_update_user_data, check_valid_password
from .schemas import UserUpdate, UpdatePassword
from database.database_main import database as db
from utils.jwt_functions import read_token


router = APIRouter(
    prefix='/api',
    tags=['profile']
)


get_bearer_token = HTTPBearer(
    auto_error=False
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get('/me/profile')
async def get_user_profile(token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token)):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        if user:
            return user.user_response()
    except (JWTError, AttributeError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен.'
            }
        )


@router.patch('/me/profile')
async def edit_user_profile(
    new_user_data: UserUpdate,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token)
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        check_new_user_data = await check_valid_update_user_data(new_user_data, db)
        if isinstance(check_new_user_data, JSONResponse):
            return check_new_user_data
        if user:
            db.update_profile(login=token_data.login, **new_user_data.user_update_data_read())
        user = db.check_user(login=token_data.login)
        return user.user_response()
    except (JWTError, AttributeError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен'
            }
        )


@router.post('/me/updatePassword')
async def update_user_password(
    update_password_form: UpdatePassword,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token)
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    'reason': 'Переданный токен не существует либо некорректен.'
                }
            )
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        if not check_valid_password(token_data.password):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'reason': 'Вы ввели некорректный пароль!'
                }
            )
        if not bcrypt_context.verify(update_password_form.oldPassword, user.password):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    'reason': 'Указанный пароль не совпадает с действительным.'
                }
            )
        db.update_profile(
            login=token_data.login,
            password=bcrypt_context.hash(update_password_form.newPassword)
        )
        await create_token(token_data.login, update_password_form.newPassword)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ok"
            }
        )
    except (JWTError, AttributeError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен'
            }
        )


@router.get('/profiles/{login}')
async def get_other_user_profile(
    login: str,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token)
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        if not user:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    'reason': 'Профиль с таким логином не существует'
                }
            )
        if not user.isPublic and user.isPublic != token_data.login:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    'reason': 'У вас нет доступа к запрашиваемому профилю!'
                }
            )
        return user.user_response()
    except (JWTError, AttributeError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен'
            }
        )
