from pydantic import BaseModel


class UserUpdate(BaseModel):
    countryCode: str = None
    isPublic: bool = None
    phone: str = None
    image: str = None

    def user_update_data_read(self):
        return {
            key: value for key, value in self.__dict__.items()
            if value is not None and key != 'password' and key != 'login'
        }


class UpdatePassword(BaseModel):
    oldPassword: str
    newPassword: str
