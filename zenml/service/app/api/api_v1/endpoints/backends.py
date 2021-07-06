from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body
from sqlalchemy.orm import Session

from app import crud
from app.db.models import User as DBUser
from app.schemas.backend import BackendCreate, Backend, \
    BackendInDB
from app.utils.db import get_db
from app.utils.enums import BackendType, BackendClass
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/", response_model=Backend)
def create_backend(
        *,
        db: Session = Depends(get_db),
        backend_in: BackendCreate = Body(
            ...,
        ),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Connect new backend.
    """
    if backend_in.type not in BackendType.__members__:
        raise HTTPException(
            status_code=400,
            detail="{} must be one of {}".format(
                backend_in.type, list(BackendType.__members__.keys()))
        )

    if backend_in.backend_class not in BackendClass.__members__:
        raise HTTPException(
            status_code=400,
            detail="{} must be one of {}".format(
                backend_in.backend_class,
                list(BackendClass.__members__.keys()))
        )

    if crud.backend.get_by_name_per_org(db, name=backend_in.name,
                                        org_id=current_user.organization_id) \
            is not None:
        raise HTTPException(
            status_code=400,
            detail="Please provide a unique name for your backends",
        )

    backend = crud.backend.create(db, obj_in=BackendInDB(
        args=backend_in.args,
        type=backend_in.type,
        name=backend_in.name,
        backend_class=backend_in.backend_class,
        provider_id=backend_in.provider_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
    ))
    return backend


@router.get("/", response_model=List[Backend],
            response_model_exclude=["args"])
def get_loggedin_backend(
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets the logged in users backend details
    """
    # segment track
    return current_user.organization.backends
