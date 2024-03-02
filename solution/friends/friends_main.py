from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from passlib.context import CryptContext
from starlette import status
from starlette.responses import JSONResponse

from .schemas import FriendLogin
from database.database_main import database as db
from utils.jwt_functions import read_token


router = APIRouter(
    prefix='/api/friends',
    tags=['friends']
)


get_bearer_token = HTTPBearer(
    auto_error=False
)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post('/add')
async def add_friend(
    friend_login: FriendLogin,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token)
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        friend = db.check_user(login=friend_login.login)
        if not friend:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    'reason': 'Пользователь с указанным логином не найден.'
                }
            )
        db.add_user_friend(friend_login=friend_login.login, user_login=token_data.login)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'status': 'ok'
            }
        )
    except (JWTError, AttributeError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен'
            }
        )


@router.post('/remove')
async def remove_user_friend(
    friend_login: FriendLogin,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token)
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        friend = db.check_user(login=friend_login.login)
        print(friend)
        if not friend:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    'reason': 'Пользователь с указанным логином не найден.'
                }
            )
        db.remove_user_friend(friend_login=friend_login.login, user_login=token_data.login)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'status': 'ok'
            }
        )
    except (JWTError, AttributeError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен'
            }
        )