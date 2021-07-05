from datetime import timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import crud
from app.crud.base import CRUDBase
from app.db.models import Organization, User
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.utils.enums import RolesTypes


class CRUDOrganization(CRUDBase[Organization,
                                OrganizationCreate,
                                OrganizationUpdate]):
    def get_by_name(self, db_session: Session, *, name: str) \
            -> Optional[Organization]:
        return db_session.query(Organization).filter(
            Organization.name == name).first()

    def count_users_in_org(self, db: Session, id: str):
        # return db.query(User.id).filter(User.organization_id == id)
        return db.query(func.count(User.id)).filter(
            User.organization_id == id).scalar()

    def get_total_datapoints(self, db: Session, org: Organization) -> int:
        # TODO [MEDIUM] Can be optimized with a sql query
        total = 0
        for user in org.users:
            total += crud.user.get_user_total_datapoints(db, user)
        return total

    def get_datapoints_in_last_delta(self, db: Session, org: Organization,
                                     delta: timedelta = timedelta(days=1)) \
            -> int:
        # TODO [MEDIUM] Can be optimized with a sql query
        total = 0
        for user in org.users:
            total += crud.user.get_user_datapoints_in_last_delta(
                db, user, delta)
        return total

    def get_creator(self, db: Session, org_id: str) -> User:
        role_id = crud.role.get_by_type(db, RolesTypes.creator.name)
        return db.query(User.organization_id == org_id).filter(
            User.role_id == role_id).first()


organization = CRUDOrganization(Organization)
