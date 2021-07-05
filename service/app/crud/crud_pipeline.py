from typing import List, Text

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models import Pipeline
from app.schemas.pipeline import PipelineInDB, PipelineUpdate


class CRUDPipeline(CRUDBase[Pipeline, PipelineInDB, PipelineUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: str) -> List[Pipeline]:
        return db.query(Pipeline).filter(
            Pipeline.user_id == user_id).all()

    def get_pipeline_names_per_ws(self, db: Session, *, workspace_id) -> List[
        Text]:
        return [x[0] for x in db.query(Pipeline.name).filter(
            Pipeline.workspace_id == workspace_id).all()]


pipeline = CRUDPipeline(Pipeline)
