from app.crud.base import CRUDBase
from app.db.models import Metadatastore
from app.schemas.metadatastore import MetadatastoreCreate, MetadatastoreUpdate


class CRUDMetadatastore(CRUDBase[Metadatastore,
                                 MetadatastoreCreate,
                                 MetadatastoreUpdate]):
    pass


metadatastore = CRUDMetadatastore(Metadatastore)
