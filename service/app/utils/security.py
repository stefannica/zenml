from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from app import crud
from app.utils.db import get_db
from app.db.models import User
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")


def get_current_user(
        db: Session = Depends(get_db), token: str = Security(reusable_oauth2)
):
    try:
        payload = decode_token(token)
        token_data = TokenPayload(firebase_id=payload['user_id'])
    except Exception:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
    user = crud.user.get_by_firebase_id(db, firebase_id=token_data.firebase_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_admin(
        current_user: User = Security(get_current_user)):
    if not crud.user.is_admin(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
