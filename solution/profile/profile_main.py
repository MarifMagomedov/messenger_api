from fastapi import APIRouter, Header, Depends, Cookie, Request
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from database.database_main import Database
from database.models import User
from starlette import status

from .profile_functions import read_token


router = APIRouter(
    prefix='/api',
    tags=['profile']
)
bearer = HTTPBearer()
db = Database()


@router.get('/me/profile')
async def get_user_profile(request: Request):
    token = request.headers.get('Authorization').split(' ')[-1]
    login = await read_token(token)
    user = db.check_user(login=login, auth=True)
    if user:
        return {
            key: value for key, value in user.__dict__.items()
            if value is not None and key != 'password' and key != 'id'
        }
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            'reason': 'Переданный токен не существует либо некорректен.'
        }
    )


@router.patch('/me/profile')
async def edit_user_profile():
    pass
