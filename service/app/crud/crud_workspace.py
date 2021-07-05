from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.db.models import User
from app.db.models import Workspace
from app.schemas.workspace import WorkspaceInDB, WorkspaceUpdate


class CRUDWorkspace(CRUDBase[Workspace, WorkspaceInDB, WorkspaceUpdate]):

    def add_user(self, db: Session, *, ws_id: str, user: User) -> Workspace:
        ws_obj = db.query(Workspace).get(ws_id)

        # add user
        all_users = [u for u in ws_obj.users]
        all_users.append(user)
        ws_obj.users = all_users

        db.add(ws_obj)
        db.commit()
        db.refresh(ws_obj)
        return ws_obj

    def delete(self, db: Session, *, id: str) -> Workspace:
        # TODO: [MEDIUM] Delete attached pipelines
        ws_obj = db.query(Workspace).get(id)

        # delete attached metadatastore
        crud.metadatastore.delete(db_session=db, id=ws_obj.metadatastore_id)

        # delete ws
        db.delete(ws_obj)
        db.commit()
        return ws_obj


workspace = CRUDWorkspace(Workspace)
