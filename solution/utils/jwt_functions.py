from datetime import datetime, timedelta

from jose import jwt
from pydantic import BaseModel

SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'


class TokenData(BaseModel):
    login: str
    password: str


async def create_token(login: str, password: str) -> str:
    expires_delta = timedelta(hours=24)
    exp = datetime.utcnow() + expires_delta
    encode = {'sub': login, 'pas': password, 'exp': exp}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def read_token(token: str) -> TokenData:
    decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    login = decode_token.get('sub')
    password = decode_token.get('pas')
    return TokenData(login=login, password=password)
