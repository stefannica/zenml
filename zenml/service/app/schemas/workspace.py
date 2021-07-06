from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


# Shared properties
class WorkspaceBase(BaseModel):
    name: Optional[str] = None
    team_id: Optional[str] = None
    metadatastore_id: Optional[str] = None


# Properties stored in DB
class WorkspaceInDB(WorkspaceBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class WorkspaceCreate(WorkspaceBase):
    pass


# Properties to receive via API on update
class WorkspaceUpdate(WorkspaceBase):
    pass


# Additional properties to return via API
class Workspace(WorkspaceInDB):
    pass
