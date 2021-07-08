from typing import Text

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.db.models import User as DBUser
from app.db.session import Session
from app.schemas.token import Token
from app.schemas.user import User
from app.utils.security import get_current_user, get_db

router = APIRouter()


def login(db, email: Text, password: Text) -> Token:
    return Token(access_token='test', token_type='bearer')


@router.post("/login/access-token", response_model=Token, tags=["login"])
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                       db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        token = login(
            db=db,
            email=form_data.username,
            password=form_data.password,
        )
    except Exception:
        raise HTTPException(status_code=400,
                            detail="Incorrect email or password")
    return token


@router.post("/login/test-token", tags=["login"], response_model=User)
def test_token(current_user: DBUser = Depends(get_current_user)):
    """
    Test access token
    """
    return current_user
