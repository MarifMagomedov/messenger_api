from pydantic import BaseModel


class ReadUser(BaseModel):
    login: str
    password: str


class CreateUser(BaseModel):
    login: str
    email: str
    password: str
    countryCode: str
    isPublic: bool
    phone: str = None
    image: str = None

    def user_register_response(self):
        return {
            key: value for key, value in self.__dict__.items()
            if value is not None and key != 'password'
        }


class Token:
    access_token: str
    token_type: str
