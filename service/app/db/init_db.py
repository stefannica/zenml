import logging

from sqlalchemy.exc import IntegrityError

from app import crud
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.schemas.role import RoleCreate
from app.schemas.workspace import WorkspaceInDB
from app.utils.enums import RolesTypes


# make sure all SQL Alchemy models are imported before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi
# -postgresql/issues/28


async def init_db(db_session):
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    # create base organization
    organization_in = OrganizationCreate(name='ZenML Organization Inc')
    try:
        org_out = crud.organization.create(db_session, obj_in=organization_in)
    except IntegrityError:
        logging.warning(
            "Tried to bootstrap DB but demo org already exists!")
        return
    org_out = crud.organization.update(
        db_session,
        obj_in=OrganizationUpdate(),
        db_obj=org_out
    )

    # create roles
    admin_role_in = RoleCreate(type=RolesTypes.admin.name)
    admin_role_out = crud.role.create(db_session, obj_in=admin_role_in)
    dev_role_in = RoleCreate(type=RolesTypes.developer.name)
    dev_role_out = crud.role.create(db_session, obj_in=dev_role_in)
    operator_role_in = RoleCreate(type=RolesTypes.operator.name)
    operator_role_out = crud.role.create(db_session, obj_in=operator_role_in)
    creator_role_in = RoleCreate(type=RolesTypes.creator.name)
    creator_role_out = crud.role.create(db_session, obj_in=creator_role_in)

    # create default workspace
    work_in = WorkspaceInDB(name='Default Workspace',
                            organization_id=org_out.id)
    crud.workspace.create(db_session, obj_in=work_in)
