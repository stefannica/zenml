from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel


# Shared properties
class TeamBase(BaseModel):
    name: Optional[str] = None


class TeamInDB(TeamBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class TeamCreate(TeamBase):
    pass


# Additional properties to return via API
class Team(TeamInDB):
    pass


# Properties to receive via API on update
class TeamUpdate(TeamInDB):
    pass
