from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_403_FORBIDDEN

from app import crud
from app.db.models import User as DBUser
from app.db.session import Session
from app.schemas.auth import AuthEmail, PasswordReset
from app.schemas.token import Token
from app.schemas.user import User
from app.utils.security import get_current_user, get_db

router = APIRouter()


@router.post("/login/access-token", response_model=Token, tags=["login"])
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                       db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        token = login(email=form_data.username, password=form_data.password,
                      db=db)
    except Exception:
        raise HTTPException(status_code=400,
                            detail="Incorrect email or password")
    if token is None:
        # Only None when user not verified
        raise HTTPException(
            status_code=403,
            detail="Your email is not verified. We have sent another "
                   "verification email to your inbox. Please verify your email"
                   " to continue using the Core Engine.",
        )
    else:
        # segment track
        user = get_current_user(db, token.access_token)

    return token


@router.post("/login/test-token", tags=["login"], response_model=User)
def test_token(current_user: DBUser = Depends(get_current_user)):
    """
    Test access token
    """
    # segment track
    return current_user


@router.post("/login/getverificationlink", response_model=Dict, tags=["login"])
def generate_verification_link(
        email: AuthEmail,
        current_user: DBUser = Depends(get_current_user)):
    """
    Generates a verification email link.
    """
    if current_user.email != email.email and \
            not crud.user.is_admin(current_user):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are now allowed to do this operation for that email!"
        )
    try:
        return {'link': generate_email_verification_link(email.email)}
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="We are unable to get the verification email at this "
                   "moment. Please try again later.")


@router.post("/login/email/resetpassword", response_model=Dict, tags=["login"])
def send_reset_pass_email(email: str):
    """
    Sends an email to the users registered email address for resetting their
    password.
    """
    # segment track
    track_event(None, SEND_RESET_PASS_EMAIL, {})

    try:
        send_password_reset_email(email=email)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="This email is not registered."
        )
    return {"msg": "Password reset email sent"}


@router.post("/login/resetpassword/", response_model=Dict, tags=["login"])
def reset_password(pr: PasswordReset,
                   current_user: DBUser = Depends(get_current_user)):
    """
    Used to reset the users password.
    """
    # segment track
    track_event(current_user.id, RESET_PASSWORD, {})

    if current_user.email != pr.email and not crud.user.is_admin(current_user):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are now allowed to do this operation for that email!"
        )

    if not verify_oob_code(pr.oob_code, current_user.email):
        raise HTTPException(
            status_code=400,
            detail="Either you are trying to update someone else's password or"
                   "your password reset time has expired.",
        )
    reset_password_fb(pr.oob_code, pr.new_password)
    return {"msg": "Password updated successfully"}
