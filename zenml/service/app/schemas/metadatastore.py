from typing import Optional

from pydantic import BaseModel


# Shared properties
class MetadatastoreBase(BaseModel):
    orchestrator_host: Optional[str] = None
    internal_host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None


# Properties stored in DB
class MetadatastoreInDB(MetadatastoreBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class MetadatastoreCreate(MetadatastoreBase):
    pass


# Properties to receive via API on update
class MetadatastoreUpdate(MetadatastoreInDB):
    pass


# Additional properties to return via API
class Metadatastore(MetadatastoreInDB):
    pass
