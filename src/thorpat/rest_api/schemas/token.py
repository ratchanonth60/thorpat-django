from ninja import Schema


class LoginSchema(Schema):
    username: str
    password: str


class TokenResponseSchema(Schema):
    access_token: str
    refresh_token: str  # If implementing refresh
    token_type: str = "bearer"
