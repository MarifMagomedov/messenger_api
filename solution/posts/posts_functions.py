from starlette import status
from starlette.responses import JSONResponse

from .schemas import CreatePost


def valid_post_data(post_data: CreatePost) -> JSONResponse | bool:
    if not len(post_data.content) <= 1000:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'reason': 'Вы ввели некорректный текст контента'
            }
        )
    if not all(1 <= len(i) <= 20 for i in post_data.tags):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'reason': 'Вы ввели некорректные тег/теги'
            }
        )
    return True
