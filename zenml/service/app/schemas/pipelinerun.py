from datetime import datetime
from typing import Optional, Dict, List

from pydantic import BaseModel

from app.schemas.pipelinestep import PipelineStepCreate, \
    PipelineStep


# Shared properties
class PipelineRunBase(BaseModel):
    datasource_commit_id: Optional[str] = None
    run_config: Optional[dict] = {}
    pipeline_run_type: Optional[str] = None


# Properties stored in DB
class PipelineRunInDB(PipelineRunBase):
    id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = None
    orchestrator_metadata: Optional[Dict] = None
    pipeline_id: Optional[str] = None
    user_id: Optional[str] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class PipelineRunCreate(PipelineRunBase):
    pass


class PipelineRunUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = None
    pipeline_step: Optional[PipelineStepCreate] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class PipelineRun(PipelineRunInDB):
    pipeline_steps: List[PipelineStep] = None


# Additional properties to return via API
class PipelineRunSlim(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None

    class Config:
        orm_mode = True
