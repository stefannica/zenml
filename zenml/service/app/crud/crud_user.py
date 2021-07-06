import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from app import crud
from app.config import ENV_TYPE
from app.crud.base import CRUDBase
from app.db.models import User, PipelineRun
from app.schemas.user import UserCreate, UserUpdate
from app.utils.enums import EnvironmentTypes
from app.utils.enums import PipelineStatusTypes, RolesTypes, PipelineRunTypes


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def get_by_firebase_id(self, db: Session, *, firebase_id: str) \
            -> Optional[User]:
        return db.query(User).filter(
            User.firebase_id == firebase_id).first()

    def get_by_email(self, db: Session, *, email: str) \
            -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_total_users(self, db: Session) \
            -> Optional[User]:
        return db.query(func.count(User.id)).scalar()

    def is_admin(self, user: User):
        if user.role.type == RolesTypes.admin.name or \
                user.role.type == RolesTypes.operator.name:
            return True
        return False

    def get_user_total_datapoints(self, db: Session, user: User) -> int:
        runs = db.query(PipelineRun).filter(
            PipelineRun.user_id == user.id).all()
        # TODO [MEDIUM] Can be optimized with a sql query
        return sum([x.datasource_commit.n_datapoints for x in runs
                    if x.datasource_commit.n_datapoints is not None
                    and x.pipeline_run_type != PipelineRunTypes.datagen.name
                    and x.status == PipelineStatusTypes.Succeeded.name])

    def get_user_datapoints_in_last_delta(self, db: Session, user: User,
                                          delta: timedelta = timedelta(
                                              days=1)) \
            -> int:
        runs = self.get_runs_in_last_delta(db, user, delta)
        # TODO [MEDIUM] Can be optimized with a sql query
        return sum([x.datasource_commit.n_datapoints for x in runs
                    if x.datasource_commit.n_datapoints is not None
                    and x.pipeline_run_type != PipelineRunTypes.datagen.name
                    and x.status == PipelineStatusTypes.Succeeded.name])

    def get_runs_in_last_delta(self, db: Session, user: User,
                               delta: timedelta = timedelta(days=1)) \
            -> List[PipelineRun]:
        time_24_hours_ago = datetime.utcnow() - delta
        return db.query(PipelineRun).filter(
            PipelineRun.start_time >= time_24_hours_ago).filter(
            PipelineRun.user_id == user.id).all()

    def get_operator(self, db: Session):
        """
        Gets a random operator to get admin access
        """
        op = crud.role.get_by_type(db, role_type=RolesTypes.operator.name)
        return db.query(User).filter(User.role_id == op.id).first()

    def is_operator(self, user: User):
        if user.role.type == RolesTypes.operator.name:
            return True
        return False

    def get_running_pipelines_count(self, db: Session, *, user: User):
        return db.query(func.count(PipelineRun.id)).filter(
            PipelineRun.user_id == user.id).filter(
            PipelineRun.status == PipelineStatusTypes.Running.name).scalar()

    def did_recently_run_pipeline(self, db: Session, *, user_id: str) -> bool:
        """
        Returns true if there is an executed pipeline within 60 seconds.
        :param db:
        :param user_id:
        :return:
        """
        # TODO: [LOW] Check if we can optimize query
        since = datetime.now(timezone.utc) - timedelta(seconds=15)
        q = db.query(PipelineRun.id).filter(
            PipelineRun.user_id == user_id).filter(
            PipelineRun.start_time > since
        )
        if q.scalar():
            return True
        else:
            return False

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        if obj_in.firebase_id is None:
            # only create firebase user in production
            if ENV_TYPE == EnvironmentTypes.production.name or \
                    ENV_TYPE == EnvironmentTypes.test.name:
                try:
                    obj_in.firebase_id = \
                        firebase.create_user_with_email_and_password(
                            email=obj_in.email,
                            password=obj_in.password,
                        )
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=str(e),
                    )

        # figure out role_id
        if obj_in.role not in RolesTypes._member_names_:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Role must be one of: {}".format(
                    RolesTypes._member_names_),
            )
        else:
            role_id = crud.role.get_by_type(db, role_type=obj_in.role).id

        db_obj = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            firebase_id=obj_in.firebase_id,
            team_id=obj_in.team_id,
            role_id=role_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    # TODO: [LOW] Make atomic
    def delete(self, db: Session, *, id: str) -> User:
        user_obj = db.query(User).get(id)
        logging.info("Deleting user id: {}, email: {}".format(
            user_obj.id,
            user_obj.email,
        ))
        # delete workspaces
        # TODO: [LOW] Add ability to delete through crud.workspace.delete
        assert len(user_obj.workspaces) <= 1
        for ws in user_obj.workspaces:
            crud.workspace.delete(db=db, id=ws.id)
            logging.info("User workspace deleted: {}".format(ws.name))

        # delete datasource
        # assert len(user_obj.team.datasources) <= 1
        # for ds in user_obj.team.datasources:
        #     assert ds.datasource_type == 'datasourcebq'
        #     crud.datasource.delete(db=db, id=ds.id)
        #     logging.info("User datasource deleted: {}".format(ds.name))

        # delete team
        org_id = user_obj.team.id
        crud.team.delete(db=db, id=org_id)
        logging.info("User team deleted: {}".format(
            org_id))

        # delete firebase
        if user_obj.firebase_id is not None:
            firebase.delete_user(user_obj.firebase_id)

        db.delete(user_obj)
        db.commit()
        logging.info("Deleted user id: {}, email: {}".format(
            user_obj.id,
            user_obj.email,
        ))
        return user_obj


user = CRUDUser(User)
