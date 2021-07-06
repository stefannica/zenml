from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body
from sqlalchemy.orm import Session

from app import crud
from app.db.models import User as DBUser
from app.schemas.team import TeamCreate, Team
from app.schemas.user import UserInTeam
from app.utils.db import get_db
from app.utils.security import get_current_admin, get_current_user

router = APIRouter()


@router.post("/", response_model=Team)
def create_team(
        *,
        db: Session = Depends(get_db),
        org_in: TeamCreate = Body(
            ...,
            example={
                "name": "My Team",
            },
        ),
        current_user: DBUser = Depends(get_current_admin),
):
    """
    Create new team. Only for admins. Users create orgs via sign up.
    """
    org = crud.team.get_by_name(db, name=org_in.name)
    if org:
        raise HTTPException(
            status_code=400,
            detail="The team {} already exists.".format(org_in.name),
        )
    org = crud.team.create(db, obj_in=org_in)
    return org


@router.get("/", response_model=Team)
def get_loggedin_team(
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets the logged in users team details
    """
    return current_user.team


@router.get("/users", response_model=List[UserInTeam])
def get_org_users(
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets a list of all users in an team
    """
    return [UserInTeam(
        email=x.email,
        full_name=x.full_name,
        team_id=x.team_id,
        n_pipelines_executed=x.n_pipelines_executed,
        firebase_id=x.firebase_id,
        id=x.id,
        created_at=x.created_at,
        role_id=x.role_id,
        role=x.role.type
    ) for x in current_user.team.users]
