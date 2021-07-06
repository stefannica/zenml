from pydantic import BaseModel


class AuthEmail(BaseModel):
    email: str


class PasswordReset(AuthEmail):
    oob_code: str
    new_password: str
