from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body
from sqlalchemy.orm import Session

from app import crud
from app.db.models import User as DBUser
from app.schemas.organization import OrganizationCreate, Organization
from app.schemas.user import UserInOrganization
from app.utils.db import get_db
from app.utils.security import get_current_admin
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/", response_model=Organization)
def create_organization(
        *,
        db: Session = Depends(get_db),
        org_in: OrganizationCreate = Body(
            ...,
            example={
                "name": "My Organization",
            },
        ),
        current_user: DBUser = Depends(get_current_admin),
):
    """
    Create new organization. Only for admins. Users create orgs via sign up.
    """
    # segment track
    track_event(current_user.id, CREATE_ORGANIZATION, {})

    org = crud.organization.get_by_name(db, name=org_in.name)
    if org:
        raise HTTPException(
            status_code=400,
            detail="The organization {} already exists.".format(org_in.name),
        )
    org = crud.organization.create(db, obj_in=org_in)

    # update the user
    # updated_user = UserUpdate(organization_id=org.id)
    # logging.info(
    #     "Updating user ID {} with organization ID {}".format(current_user.id,
    #                                                          org.id))
    # crud.user.update(db, db_obj=current_user, obj_in=updated_user)

    return org


@router.get("/", response_model=Organization,
            response_model_exclude=["service_account"])
def get_loggedin_organization(
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets the logged in users organization details
    """
    # segment track
    track_event(current_user.id, GET_LOGGEDIN_ORGANIZATION, {})

    return current_user.organization


@router.get("/users", response_model=List[UserInOrganization])
def get_org_users(
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets a list of all users in an organization
    """
    # segment track
    track_event(current_user.id, GET_ORG_USERS, {})

    return [UserInOrganization(
        email=x.email,
        full_name=x.full_name,
        organization_id=x.organization_id,
        n_pipelines_executed=x.n_pipelines_executed,
        firebase_id=x.firebase_id,
        id=x.id,
        created_at=x.created_at,
        role_id=x.role_id,
        role=x.role.type
    ) for x in current_user.organization.users]
