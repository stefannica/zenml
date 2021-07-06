from typing import List

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.crud.base import CRUDBase
from app.db.models import DatasourceCommit, PipelineRun
from app.schemas.datasource import DatasourceCommitInDB, DatasourceCommitUpdate


class CRUDDatasourceCommit(
    CRUDBase[
        DatasourceCommit, DatasourceCommitInDB, DatasourceCommitUpdate]):

    def get_by_datasource(self, db_session: Session, *, ds_id: str) \
            -> List[DatasourceCommit]:
        return db_session.query(DatasourceCommit).filter(
            DatasourceCommit.datasource_id == ds_id).all()

    def create_clean(self, db_session: Session, *,
               obj_in: DatasourceCommitInDB) -> DatasourceCommit:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj

    def get_datagen_run(self, db_session: Session, id: str) -> \
            PipelineRun:
        """
        Every commit has a run associated with it. This query gets that run
        """
        return db_session.query(PipelineRun).filter(
            PipelineRun.datasource_commit_id == id).first()


datasource_commit = CRUDDatasourceCommit(DatasourceCommit)
