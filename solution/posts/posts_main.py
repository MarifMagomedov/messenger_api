from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from passlib.context import CryptContext
from starlette import status

from .schemas import CreatePost
from .posts_functions import valid_post_data

from database.database_main import database as db
from utils.jwt_functions import read_token

router = APIRouter(
    prefix='/api',
    tags=['posts']
)


get_bearer_token = HTTPBearer(
    auto_error=False
)
bcrypt_context = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"],
                              default="des_crypt", deprecated="auto")


@router.post('/posts/new')
async def user_create_post(
    post_data: CreatePost,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token)
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        valid_post = valid_post_data(post_data)
        if isinstance(valid_post, JSONResponse):
            return valid_post
        post = db.create_user_post(token_data.login, user.isPublic, post_data)
        return post
    except (JWTError, AttributeError) as ex:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен.'
            }
        )


@router.get('/posts/{postId}')
async def get_post_for_id(
    postId: str,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token),
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        post = db.get_post_for_id(postId)
        if isinstance(post, JSONResponse):
            return post
        if not post['isPublic'] and post['author'] != user.login:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    'reason': 'У вас нет доступа к посту'
                }
            )
        del post['isPublic']
        return post
    except (JWTError, AttributeError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен.'
            }
        )


@router.get('/feed/my')
async def get_user_posts(
    limit: int = 5,
    offset: int = 0,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token),
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        if limit > 50 or limit < 0 or offset < 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'reason': 'Некорректный offset или limit'
                }
            )
        user_posts = db.get_user_posts(token_data.login, limit, offset, my=True)
        if isinstance(user_posts, JSONResponse):
            return user_posts
        for item in user_posts:
            del item['isPublic']
        return user_posts
    except (JWTError, AttributeError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен.'
            }
        )


@router.get('/posts/feed/{login}')
async def get_other_user_posts(
    login: str,
    limit: int = 5,
    offset: int = 0,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token)
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        if limit > 50 or limit < 0 or offset < 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'reason': 'Некорректный offset или limit'
                }
            )
        if (
            not user.isPublic
            and user.login != token_data.login
            and token_data.login not in [item.login for item in user.friends]
        ):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    'reason': 'У вас нет доступа к посту'
                }
            )
        user_posts = db.get_user_posts(login, limit, offset)
        for item in user_posts:
            del item['isPublic']
        return user_posts
    except (JWTError, AttributeError) as ex:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен.'
            }
        )


@router.get('/posts/{postId}/like')
async def like_post(
    postId: str,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token)
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        reactions = db.set_post_reaction(token_data.login, postId, True)
        del reactions['isPublic']
        return reactions
    except (JWTError, AttributeError) as ex:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен.'
            }
        )


@router.get('/posts/{postId}/dislike')
async def dislike_post(
    postId: str,
    token: HTTPAuthorizationCredentials | None = Depends(get_bearer_token)
):
    try:
        token = token.credentials.replace('"', '')
        token_data = await read_token(token)
        user = db.check_user(login=token_data.login)
        if not bcrypt_context.verify(token_data.password, user.password):
            raise JWTError
        reactions = db.set_post_reaction(token_data.login, postId, False)
        del reactions['isPublic']
        return reactions
    except (JWTError, AttributeError) as ex:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'reason': 'Переданный токен не существует либо некорректен.'
            }
        )
