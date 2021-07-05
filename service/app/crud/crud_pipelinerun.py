from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from app.crud import user
from app.crud.base import CRUDBase
from app.db.models import PipelineRun, Pipeline
from app.schemas.pipelinerun import PipelineRunInDB, PipelineRunUpdate
from app.schemas.user import UserUpdate
from app.utils.enums import PipelineRunTypes


class CRUDPipelineRun(
    CRUDBase[PipelineRun, PipelineRunInDB, PipelineRunUpdate]):

    def get_by_ml_metadata_context(self, db_session: Session, *,
                                   workspace_id: str,
                                   ml_metadata_context: str,
                                   ) \
            -> PipelineRun:
        db_obj = db_session.query(PipelineRun).filter(
            PipelineRun.ml_metadata_context ==
            ml_metadata_context).join(Pipeline).filter(
            Pipeline.workspace_id == workspace_id).first()

        if db_obj.pipeline_run_type != PipelineRunTypes.datagen.name:
            return db_obj
        raise HTTPException(
            status_code=400,
            detail='Not allowed to fetch datagen type pipelines by ml '
                   'metadata context.',
        )

    def get_by_pipeline(self, db_session: Session, pipeline_id: str, id: str) \
            -> PipelineRun:
        return db_session.query(PipelineRun).filter(
            PipelineRun.pipeline_id == pipeline_id).filter(
            PipelineRun.id == id).first()

    def create(self, db_session: Session, *,
               obj_in: PipelineRunInDB) -> PipelineRun:
        # add pipeline
        obj_in_data = jsonable_encoder(obj_in)
        db_pipeline_run = self.model(**obj_in_data)
        db_session.add(db_pipeline_run)
        db_session.commit()
        db_session.refresh(db_pipeline_run)
        return db_pipeline_run


pipelinerun = CRUDPipelineRun(PipelineRun)
