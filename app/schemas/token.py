from pydantic.v1 import BaseModel


class TokenData(BaseModel):
    username: str
    id: int
