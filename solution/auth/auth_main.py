from fastapi import APIRouter
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from starlette import status

from .schemas import CreateUser, ReadUser
from database.database_main import database as db
from database.models import User
from .auth_functions import check_valid_user_data, authenticate_user
from utils.jwt_functions import create_token

router = APIRouter(
    prefix='/api/auth',
    tags=['auth']
)


bcrypt_context = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"],
                              default="des_crypt", deprecated="auto")


@router.post('/register')
async def user_register(create_user_request: CreateUser):
    check_valid_user = await check_valid_user_data(create_user_request, db)
    if check_valid_user is None:
        user = User(
            login=create_user_request.login,
            email=create_user_request.email,
            password=bcrypt_context.hash(create_user_request.password),
            countryCode=create_user_request.countryCode,
            isPublic=create_user_request.isPublic,
            phone=create_user_request.phone,
            image=create_user_request.image
        )
        db.create_profile(user)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                'profile': create_user_request.user_register_response()
            }
        )
    return check_valid_user


@router.post('/sign-in')
async def user_sign_in(form_data: ReadUser):
    user_auth = await authenticate_user(form_data.login, form_data.password, db, bcrypt_context)
    if isinstance(user_auth, JSONResponse):
        return user_auth
    token = await create_token(form_data.login, form_data.password)
    return {'token': token}
