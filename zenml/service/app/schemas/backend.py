from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class BackendBase(BaseModel):
    backend_class: str = None
    type: str = None
    name: str = None


class BackendInDB(BackendBase):
    id: Optional[str] = None
    user_id: str = None
    organization_id: str = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class BackendCreate(BackendBase):
    pass


# Properties to receive via API on update
class BackendUpdate(BackendBase):
    pass


# Additional properties to return via API
class Backend(BackendInDB):
    pass
