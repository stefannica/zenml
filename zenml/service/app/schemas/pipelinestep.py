from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class PipelineStepBase(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = None
    step_type: str = None


class PipelineStepInDB(PipelineStepBase):
    id: Optional[str] = None
    pipeline_run_id: str = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class PipelineStepCreate(PipelineStepInDB):
    pass


# Properties to receive via API on update
class PipelineStepUpdate(PipelineStepInDB):
    pass


# Additional properties to return via API
class PipelineStep(PipelineStepBase):
    class Config:
        orm_mode = True
