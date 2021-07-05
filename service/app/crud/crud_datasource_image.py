# from typing import List
#
# from google.cloud import storage
# from google.oauth2 import service_account as sa_service
# from sqlalchemy.orm import Session
#
# from app.config import GCP_PROJECT
# from app.crud import organization
# from app.crud.base import CRUDBase
# from app.db.models import DatasourceImage, Datasource
# from app.schemas.datasource import DatasourceImageInDB, DatasourceImageUpdate
#
#
# class CRUDDatasourceImage(
#     CRUDBase[DatasourceImage, DatasourceImageInDB, DatasourceImageUpdate]):
#
#     def get_by_org(self, db_session: Session, *, org_id: str) \
#             -> List[DatasourceImage]:
#         return db_session.query(DatasourceImage).filter(
#             DatasourceImage.organization_id == org_id).all()
#
#     def create(self, db_session: Session, *,
#                obj_in: DatasourceImageInDB) -> DatasourceImage:
#
#         # Create storage client with client's service account
#         credentials = sa_service.Credentials.from_service_account_info(
#             obj_in.service_account)
#         client_gcs_client = storage.Client(
#             credentials=credentials,
#         )
#
#         # get list of files
#
#         client_storage_path = obj_in.client_storage_path.replace("gs://", "")
#         # split given client gcs path in bucket and prefix
#
#         client_storage_path_elements = list(
#             filter(None, client_storage_path.split("/"))
#         )  # purging empty strings
#         client_bucket_name = client_storage_path_elements.pop(0)
#
#         if client_storage_path_elements:
#             client_prefix = "/".join(client_storage_path_elements)
#
#         if not client_bucket_name:
#             raise ValueError  # this must be done nicer...
#
#         # get list of objects
#         if not client_prefix:
#             client_blobs = client_gcs_client.list_blobs(
#                 str(client_bucket_name),
#                 delimiter=None,  # disregard tree hierarchy
#             )  # returns an iterator of files
#         else:
#             print("non-empty client_prefix: ", client_prefix)
#             client_blobs = client_gcs_client.list_blobs(
#                 str(client_bucket_name),
#                 prefix=client_prefix,  # empty prefixes shouldn't matter
#                 delimiter=None,  # disregard tree hierarchy
#             )  # returns an iterator of files
#
#         # filter to supported file types
#         supported_types = ["bmp", "gif", "jpg", "jpeg", "png"]
#         file_list = [
#             "gs://{}/{}".format(blob.bucket.name, blob.name) for
#             blob in client_blobs if
#             blob.name.split(".")[-1] in supported_types]
#         file_list_content = "\n".join(file_list)  # will break on large lists
#
#         # persist list of objects newline-delimited in clients storage bucket
#         internal_gcs_client = storage.Client(project=GCP_PROJECT)
#         org = organization.get(db_session, obj_in.organization_id)
#
#         internal_bucket_obj = internal_gcs_client.bucket(org.bucket_name)
#         internal_blob_name = "datasource-image/{}.txt".format(obj_in.name)
#         file_list_blob_obj = internal_bucket_obj.blob(internal_blob_name)
#         file_list_blob_path = "{}/{}".format(
#             org.bucket_name, internal_blob_name)
#
#         file_list_blob_obj.upload_from_string(data=file_list_content)
#
#         db_obj = DatasourceImage(
#             name=obj_in.name,
#             organization_id=obj_in.organization_id,
#             client_storage_path=obj_in.client_storage_path,
#             internal_file_list_path=file_list_blob_path,
#             n_samples=len(file_list),
#             service_account=obj_in.service_account,
#         )
#         db_session.add(db_obj)
#         db_session.commit()
#         db_session.refresh(db_obj)
#         return db_obj
#
#     def delete(self, db: Session, *, id: str) -> DatasourceImage:
#         # create DB object for specified image datasource
#         ds_img_obj = db.query(DatasourceImage).get(id)
#         # delete actual image datasource
#         db.delete(ds_img_obj)
#
#         # delete parent object
#         ds_obj = db.query(Datasource).get(id)
#         db.delete(ds_obj)
#
#         db.commit()
#         return ds_img_obj
#
#
# datasource_image = CRUDDatasourceImage(DatasourceImage)
