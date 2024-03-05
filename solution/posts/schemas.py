from pydantic import BaseModel


class CreatePost(BaseModel):
    content: str
    tags: list[str]
