from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.pipelinerun import PipelineRunSlim


# Shared properties
class PipelineBase(BaseModel):
    name: str = None
    workspace_id: Optional[str] = None


class PipelineInDB(PipelineBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    team_id: Optional[str] = None
    user_id: Optional[str] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class PipelineCreate(PipelineBase):
    pass


# Properties to receive via API on update
class PipelineUpdate(PipelineCreate):
    pass


# Additional properties to return via API
class Pipeline(PipelineInDB):
    pipeline_runs: List[PipelineRunSlim] = None
