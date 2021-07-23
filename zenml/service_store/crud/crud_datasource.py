from typing import List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models import Datasource
from app.schemas.datasource import DatasourceCreate, DatasourceUpdate


class CRUDDatasource(
    CRUDBase[Datasource, DatasourceCreate, DatasourceUpdate]):

    def get_by_org(self, db_session: Session, *, org_id: str) \
            -> List[Datasource]:
        return db_session.query(Datasource).filter(
            Datasource.team_id == org_id).all()


datasource = CRUDDatasource(Datasource)
