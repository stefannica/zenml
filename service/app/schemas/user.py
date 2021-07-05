from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class UserBase(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None


# Shared properties
class UserInDBBase(UserBase):
    organization_id: Optional[str] = None


class UserInDB(UserInDBBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    role_id: Optional[str] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class UserCreate(UserInDBBase):
    password: str = None
    role: str = None
    organization_name: str = None


# Properties to receive via API on update
class UserUpdate(UserInDBBase):
    pass


# Additional properties to return via API
class User(UserInDB):
    pass


# Additional properties to return via API
class UserInOrganization(UserInDB):
    role: str = None
