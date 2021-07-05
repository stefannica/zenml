import logging
import re
from datetime import datetime
from typing import List, Text

import pytz
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.config import ENV_TYPE
from app.db.models import User as DBUser
from app.schemas.organization import OrganizationCreate
from app.schemas.user import User, UserUpdate
from app.schemas.user import UserCreate
from app.utils.db import get_db
from app.utils.enums import EnvironmentTypes
from app.utils.enums import InviteStatus
from app.utils.enums import RolesTypes
from app.utils.security import get_current_admin, \
    get_current_user

router = APIRouter()


@router.put("/", response_model=User)
def update_loggedin_user(
        *,
        db: Session = Depends(get_db),
        user_in: UserUpdate,
        current_user: DBUser = Depends(get_current_user),
):
    """
    Update own user.
    """
    raise HTTPException(
        status_code=500,
        detail="Not implemented!",
    )


@router.get("/me", response_model=User)
def get_loggedin_user(
        current_user: DBUser = Depends(get_current_user),
):
    """
    Get current user.
    """
    # segment track
    return current_user


@router.get("/", response_model=List[User])
def get_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: DBUser = Depends(get_current_admin),
):
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=User)
async def create_user(
        *,
        db: Session = Depends(get_db),
        user_in: UserCreate,
):
    """
    Create new user and organization
    """
    total_active_users = crud.user.get_total_users(db)
    logging.info("Signing up: {}".format(user_in.email))
    logging.info("Total users: {}".format(total_active_users))

    # Make a regular expression for validating an Email
    regex = '[^@]+@[^@]+\.[^@]+'
    if not re.search(regex, user_in.email):
        raise HTTPException(status_code=400, detail="Invalid email")

    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    # create an organization if not specified
    if user_in.organization_name is None:
        raise HTTPException(
            status_code=400,
            detail="Please specify an organization name when creating user."
        )

    org = crud.organization.get_by_name(db, name=user_in.organization_name)
    if not org:
        # creating without an invite
        org = crud.organization.create(
            db_session=db,
            obj_in=OrganizationCreate(name=user_in.organization_name))

        # always a creator if the first one in the org
        user_in.role = RolesTypes.creator.name

        # Set the organization
        user_in.organization_id = org.id

        # create a user
        user = crud.user.create(db, obj_in=user_in)

        # create stripe default subscription
        try:
            if ENV_TYPE == EnvironmentTypes.production.name or \
                    ENV_TYPE == EnvironmentTypes.test.name:
                # Create a subscription for this users organization if its new
                create_default_subscription(db=db,
                                            user=user,
                                            organization=org)
        except Exception as e:
            logging.error(str(e))
            # TODO [High]: If this happens, we should delete the firebase
            #  user as well. Implement a proper crud.user.delete for this.
            crud.user.delete(db_session=db, id=user.id)
            crud.organization.delete(db_session=db, id=org.id)
            raise HTTPException(
                status_code=500,
                detail="We are unable to create the organization at this "
                       "moment. Please contact support@maiot.io."
            )
    else:
        # this means that it was via invite
        invite = crud.invite.get_by_email_and_org(
            db=db, email=user_in.email, org_id=org.id)

        if invite is None:
            raise HTTPException(
                status_code=400,
                detail=f"Organization names already taken. Please create a "
                       f"unique name for your organization."
            )
        # make sure invite isnt expired
        if datetime.utcnow().replace(tzinfo=pytz.utc) >= invite.expires_on:
            raise HTTPException(
                status_code=400,
                detail=f"Invite has expired!"
            )

        # make sure invite is for the same email
        if user_in.email != invite.email:
            raise HTTPException(
                status_code=400,
                detail=f"Email and invite code don't match!"
            )

        # update invite
        crud.invite.update(
            db_session=db, db_obj=invite,
            obj_in=InviteInDB(status=InviteStatus.accepted.name))

        # always a developer if invited
        user_in.role = RolesTypes.developer.name

        # Set the organization
        user_in.organization_id = org.id

        # create a user
        user = crud.user.create(db, obj_in=user_in)

        # add this user to all workspaces in organization
        for ws in user.organization.workspaces:
            crud.workspace.add_user(db, ws_id=ws.id, user=user)

    # We add a default workspace
    # work_in = WorkspaceInDB(name='Default Workspace',
    #                         organization_id=user.organization_id,
    #                         user_ids=[user.id])
    # ws_out = crud.workspace.create(db, obj_in=work_in)

    # segment track
    identify_user(user.id, user.email, user.full_name)
    associate_group(
        user.id, org.id, org.name,
        {'employees': crud.organization.count_users_in_org(db, org.id)})
    track_event(user.id, CREATE_USER, metadata={})

    return user


@router.get("/{user_id}", response_model=User)
def get_user_by_id(
        user_id: str,
        current_user: DBUser = Depends(get_current_admin),
        db: Session = Depends(get_db),
):
    """
    Get a specific user by id.
    """
    # segment track
    track_event(current_user.id, GET_USER_BY_ID, {})

    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with ID {} does not exist.".format(user_id),
        )
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: str,
        user_in: UserUpdate,
        current_user: DBUser = Depends(get_current_admin),
):
    """
    Update a user.
    """
    # segment track
    track_event(current_user.id, UPDATE_USER, {})

    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=Text)
def delete_user(
        user_id: str,
        db: Session = Depends(get_db),
        admin: DBUser = Depends(get_current_admin),
):
    """
    Deletes the user specified by ID. Currently, these conditions must be met:
    1) User must have 0 pipelines executed
    2) User must have only 1 or less workspaces
    3) User must have only 1 or less datasources

    In this case, the user will be deleted from here, from firebase, the
    workspace will be deleted, the datasource will be deleted, credit entry
    will be deleted.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    if user.n_pipelines_executed != 0:
        raise HTTPException(
            status_code=404,
            detail="The user has {} created pipelines. You can only delete "
                   "users which have 0 executed pipeline.".format(
                user.n_pipelines_executed
            ),
        )

    n_workspaces = len(user.workspaces)
    if n_workspaces > 1:
        raise HTTPException(
            status_code=404,
            detail="The user has {} workspaces. You can only delete "
                   "users which have less than 1 created workspace.".format(
                n_workspaces
            ),
        )

    n_ds = len(user.organization.datasources)
    if n_ds > 1:
        raise HTTPException(
            status_code=404,
            detail="The user has {} datasource. You can only delete "
                   "users which have less than 1 datasource.".format(
                n_ds
            ),
        )
    crud.user.delete(db, id=user.id)
    return user_id
