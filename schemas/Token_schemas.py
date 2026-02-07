from pydantic import BaseModel


class Token(Basemodel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str


class Login(BaseModel):
    email: str
    password: str
    