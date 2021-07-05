from typing import Optional

from pydantic import BaseModel


# Shared properties
class RoleBase(BaseModel):
    type: Optional[str] = None


class RoleInDB(RoleBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class RoleCreate(RoleBase):
    pass


# Properties to receive via API on update
class RoleUpdate(RoleBase):
    pass


# Additional properties to return via API
class Role(RoleInDB):
    pass
