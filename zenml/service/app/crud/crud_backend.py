from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models import Backend
from app.schemas.backend import BackendInDB, BackendUpdate


class CRUDBackend(CRUDBase[Backend,
                           BackendInDB,
                           BackendUpdate]):
    def get_by_org(self, db: Session, *, org_id: str) -> List[Backend]:
        return db.query(Backend).filter(
            Backend.team_id == org_id).all()

    def get_by_name(self, db: Session, *, name: str) -> List[Backend]:
        return db.query(Backend).filter(
            Backend.name == name).all()

    def get_by_name_per_org(self, db: Session, *, name: str,
                            org_id: str) -> Backend:
        bs = db.query(Backend).filter(Backend.team_id == org_id).all()
        for x in bs:
            if x.name == name:
                return x

    def get_by_type_and_class(self, db: Session, *, org_id: str,
                              backend_type: str,
                              backend_class: str) -> List[Backend]:
        return db.query(Backend).filter(
            Backend.team_id == org_id).filter(
            Backend.backend_class == backend_class).filter(
            Backend.type == backend_type).all()


backend = CRUDBackend(Backend)
