from datetime import datetime
from typing import Optional, Dict, List

from pydantic import BaseModel


# Shared properties
class DatasourceCommitBase(BaseModel):
    pass


# Representation of datasource in DB
class DatasourceCommitInDB(DatasourceCommitBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    user_id: Optional[str] = None
    datasource_id: Optional[str] = None

    class Config:
        orm_mode = True


# Properties from API
class DatasourceCommitCreate(DatasourceCommitBase):
    pass

# Properties to receive via API on update
class DatasourceCommitUpdate(DatasourceCommitInDB):
    pass


# Properties from API
class DatasourceCommit(DatasourceCommitInDB):
    pass


# Shared properties
class DatasourceBase(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None


# Representation of datasource in DB
class DatasourceInDB(DatasourceBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    organization_id: Optional[str] = None
    origin_pipeline_id: Optional[str] = None
    metadatastore_id: Optional[str] = None

    class Config:
        orm_mode = True


# Properties from API
class DatasourceCreate(DatasourceBase):
    pass


# Properties to receive via API on update
class DatasourceUpdate(DatasourceBase):
    pass


# Properties from API
class Datasource(DatasourceInDB):
    datasource_commits: List[DatasourceCommitInDB] = None
