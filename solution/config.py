from environs import Env
import os
from pydantic import BaseModel


class JWTConfig(BaseModel):
    algorithm: str
    secret_key: str


def load_configs(database: bool = None) -> str | JWTConfig:
    env = Env()
    env.read_env()
    if database:
        return os.environ['POSTGRES_CONN']
    return JWTConfig(
        algorithm=os.environ['ALGORITHM'],
        secret_key=os.environ['SECRET_KEY']
    )
