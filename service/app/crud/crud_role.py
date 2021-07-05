from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models import Role
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[Role,
                        RoleCreate,
                        RoleUpdate]):

    def get_by_type(self, db: Session, role_type: str) -> Optional[Role]:
        return db.query(Role).filter(Role.type == role_type).first()


role = CRUDRole(Role)
