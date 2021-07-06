from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel


# Shared properties
class OrganizationBase(BaseModel):
    name: Optional[str] = None


class OrganizationInDB(OrganizationBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class OrganizationCreate(OrganizationBase):
    pass


# Additional properties to return via API
class Organization(OrganizationInDB):
    pass


# Properties to receive via API on update
class OrganizationUpdate(OrganizationInDB):
    pass
