from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from app import crud
from app.utils.db import get_db
from app.db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")


def decode_token():
    pass


def get_current_user(
        db: Session = Depends(get_db), token: str = Security(oauth2_scheme)
):
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
    return user


def get_current_admin(
        current_user: User = Security(get_current_user)):
    if not crud.user.is_admin(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
