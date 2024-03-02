from pydantic import BaseModel


class FriendLogin(BaseModel):
    login: str
