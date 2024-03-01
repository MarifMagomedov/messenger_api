from jose import jwt


SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'


async def read_token(token: str) -> str:
    decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    login = decode_token.get('sub')
    return login
