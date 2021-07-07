import logging
import time
from typing import List, Dict, Text

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from app import crud
from app.api.api_v1.endpoints import pipelines as pipeline_endpoints
from app.db.models import User as DBUser
from app.schemas.datasource import Datasource, DatasourceInDB, \
    DatasourceCreate, DatasourceCommitInDB, DatasourceCommit, \
    DatasourceCommitCreate
from app.schemas.pipeline import PipelineCreate
from app.schemas.pipelinerun import PipelineRunCreate
from app.utils.db import get_db
from app.utils.enums import PipelineStatusTypes, PipelineTypes, \
    PipelineRunTypes
from app.utils.misc import sanitize_name
from app.utils.security import get_current_user

router = APIRouter()


@router.get("/", response_model=List[Datasource])
def get_datasources(
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets all datasources of the logged in users team.
    """
    ds = crud.datasource.get_by_org(db, org_id=current_user.team_id)
    return ds


@router.get("/{ds_id}", response_model=Datasource)
def get_datasource(
        ds_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets the datasource specified by ID
    """
    ds = crud.datasource.get(db, id=ds_id)
    if not ds:
        raise HTTPException(
            status_code=404,
            detail="The datasource does not exist.",
        )

    if ds.team_id != current_user.team_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this datasource.",
        )
    return ds


# get all commits for a datasource
@router.get("/{ds_id}/commits",
            response_model=List[DatasourceCommit])
def get_commits(
        ds_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets all the commits of the specified datasource.
    """
    # verify ownership
    ds = get_datasource(
        ds_id=ds_id,
        db=db,
        current_user=current_user,
    )
    return ds.datasource_commits


@router.get("/{ds_id}/commits/{commit_id}",
            response_model=DatasourceCommit)
def get_datasource_commit(
        ds_id: str,
        commit_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets commit of one datasource
    """
    ds_commit = crud.datasource_commit.get(db_session=db, id=commit_id)
    if not ds_commit:
        raise HTTPException(
            status_code=404,
            detail="The commit does not exist.",
        )
    if ds_commit.datasource_id != ds_id:
        raise HTTPException(
            status_code=404,
            detail="You are not allowed to fetch this commit!",
        )
    if ds_commit.datasource.team_id != current_user.team_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this datasource.",
        )
    return ds_commit


@router.get("/commits/{commit_id}",
            response_model=DatasourceCommit)
def get_single_commit(
        commit_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets commit of one datasource
    """
    ds_commit = crud.datasource_commit.get(db_session=db, id=commit_id)
    if not ds_commit:
        raise HTTPException(
            status_code=404,
            detail="The commit does not exist.",
        )

    if ds_commit.datasource.team_id != current_user.team_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this datasource.",
        )
    return ds_commit


@router.get("/{ds_id}/commits/{commit_id}/status", response_model=Text)
def get_datasource_commit_status(
        ds_id: str,
        commit_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets the status of the pipeline of this datasource commit
    """
    commit = get_datasource_commit(ds_id, commit_id, db, current_user)
    run = crud.datasource_commit.get_datagen_run(db, commit.id)
    return run.status


@router.get("/{ds_id}/commits/{commit_id}/metadata",
            response_model=List[str])
def get_datasource_commit_metadata(
        ds_id: str,
        commit_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets distinct values from column name. Maximum 1000 distinct values.
    """
    commit = get_datasource_commit(ds_id, commit_id, db, current_user)
    status = crud.datasource_commit.get_datagen_run(db, commit.id).status
    if status != PipelineStatusTypes.Succeeded.name:
        raise HTTPException(
            status_code=500,
            detail="Please wait for the datasource commit to finish "
                   "processing!")

    return {
        'n_datapoints': commit.n_datapoints,
        'n_features': commit.n_features,
        'n_bytes': commit.n_bytes,
    }


@router.get("/{ds_id}/commits/{commit_id}/schema", response_model=Dict)
def get_datasource_commit_schema(
        ds_id: str,
        commit_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets all the bigquery datasources of the logged in user
    """
    commit = get_datasource_commit(ds_id, commit_id, db, current_user)
    status = crud.datasource_commit.get_datagen_run(db, commit.id).status
    if status != PipelineStatusTypes.Succeeded.name:
        raise HTTPException(
            status_code=400,
            detail="Please wait for the datasource commit to finish "
                   "processing!")
    return commit.used_schema


@router.get("/{ds_id}/commits/{commit_id}/schema/{column_name}",
            response_model=List[str])
def get_datasource_commit_distinct_col_values(
        ds_id: str,
        commit_id: str,
        column_name: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets distinct values from column name. Maximum 1000 distinct values.
    """
    commit = get_datasource_commit(ds_id, commit_id, db, current_user)
    status = crud.datasource_commit.get_datagen_run(db, commit.id).status
    if status != PipelineStatusTypes.Succeeded.name:
        raise HTTPException(
            status_code=400,
            detail="Please wait for the datasource commit to finish "
                   "processing!")

    return get_distinct_by_column(
        get_bq_client(current_user.team),
        commit.destination_args[DestinationKeys.PROJECT],
        commit.destination_args[DestinationKeys.DATASET],
        commit.destination_args[DestinationKeys.TABLE],
        column_name,
    )


@router.get("/{ds_id}/commits/{commit_id}/data", response_model=List[Dict])
def get_datasource_commit_data_sample(
        ds_id: str,
        commit_id: str,
        sample_size: int = 10,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets a random sample of data from datasource
    """
    commit = get_datasource_commit(ds_id, commit_id, db, current_user)
    status = crud.datasource_commit.get_datagen_run(db, commit.id).status

    if status != PipelineStatusTypes.Succeeded.name:
        raise HTTPException(
            status_code=400,
            detail="Please wait for the datasource commit to finish "
                   "processing!")

    if sample_size > 100:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Requested sample size must by < 100 datapoints!",
        )
    return get_random_sample(
        get_bq_client(current_user.team),
        commit.destination_args[DestinationKeys.PROJECT],
        commit.destination_args[DestinationKeys.DATASET],
        commit.destination_args[DestinationKeys.TABLE],
        commit.used_schema,
        sample_size
    )


@router.post("/", response_model=Datasource)
async def create_datasource(
        *,
        db: Session = Depends(get_db),
        datasource_in: DatasourceCreate = Body(
            ...,
        ),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Create new datasource for logged in user.
    """
    if any(x.name == datasource_in.name
           for x in current_user.team.datasources):
        raise HTTPException(
            status_code=400,
            detail="A datasource with this name already exists.",
        )
    if datasource_in.type is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Please provide a datasource type.")
    try:
        if crud.provider.get(db_session=db,
                             id=datasource_in.provider_id) is None:
            raise Exception
    except:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=f"Provider with ID: {datasource_in.provider_id} "
                   f"does not exist.")
    # Check limits
    check_billing_limits_datasources(db, org=current_user.team)

    # Lint
    datagen_source = source_factory.get_single_source(datasource_in.source)
    config = jsonable_encoder(datasource_in)
    # TODO: [MEDIUM] Hard-coded for now
    config.pop('name')
    config.pop('provider_id')
    try:
        datagen_source.config_parser(config)
    except AssertionError as e:
        raise HTTPException(
            status_code=400,
            detail='Problem while reading the config file: {}'.format(e)
        )

    # All pipelines have this one metadata store
    metadatastore = create_md_store_db(
        db,
        current_user.team_id,
        'datagen'
    )

    try:
        # Create a pipeline first
        pipeline = await pipeline_endpoints.create_pipeline(
            db=db,
            current_user=current_user,
            pipe_in=PipelineCreate(
                name='{}_{}_{}'.format(
                    current_user.team_id.replace('-', '_')[0:15],
                    sanitize_name(datasource_in.name),
                    int(time.time())),
                pipeline_config={},
                pipeline_type=PipelineTypes.datagen.name,
            )
        )

        # Then persist the datasource
        datasource_db = DatasourceInDB(
            **jsonable_encoder(datasource_in),
            team_id=current_user.team_id,
            origin_pipeline_id=pipeline.id,
            metadatastore_id=metadatastore.id,
        )
        ds = crud.datasource.create(db, obj_in=datasource_db)

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(e)
        raise HTTPException(
            status_code=500,
            detail="We are unable to create the datasource at this time. "
                   "Please contact us if this error persists!")
    return ds


@router.post("/{ds_id}/commits", response_model=DatasourceCommit)
async def create_datasource_commit(*,
                                   ds_id: str,
                                   db: Session = Depends(get_db),
                                   ds_commit_in: DatasourceCommitCreate = Body(
                                       ...,
                                   ),
                                   current_user: DBUser = Depends(
                                       get_current_user),
                                   ):
    # Get the datasource and make checks
    ds = crud.datasource.get(db, id=ds_id)
    if ds.team_id != current_user.team_id:
        raise HTTPException(
            status_code=400,
            detail="You are not allowed to edit this datasource.",
        )
    if not ds:
        raise HTTPException(
            status_code=404,
            detail="The datasource does not exist.",
        )

    # Create a commit message if it isnt there
    if ds_commit_in.message is None:
        ds_commit_in.message = 'Latest commit of {}'.format(ds.name)

    # Create the datagen config
    org = current_user.team
    additional_args = dict()

    additional_args[DatalineKeys.DATASOURCE] = {
        DataSourceKeys.DATA_SOURCE: ds.source,
        DataSourceKeys.DATA_TYPE: ds.type,
        DataSourceKeys.ARGS: ds.args,
    }

    additional_args[DatalineKeys.DESTINATION] = {
        DestinationKeys.PROJECT: org.service_account['project_id'],
        DestinationKeys.DATASET: sanitize_name(org.name),
        DestinationKeys.TABLE: sanitize_name(ds.name) + '_'
    }

    additional_args[DatalineKeys.SCHEMA_] = ds_commit_in.used_schema

    # Create the commit
    try:
        # create commit in DB
        ds_commit_db = DatasourceCommitInDB(
            **jsonable_encoder(ds_commit_in),
            user_id=current_user.id,
            datasource_id=ds_id,
            destination_args=additional_args[DatalineKeys.DESTINATION],
        )
        datasource_commit = crud.datasource_commit.create(
            db, obj_in=ds_commit_db)

        # now destination args are resolved
        additional_args[DatalineKeys.DESTINATION] = \
            datasource_commit.destination_args

        await pipeline_endpoints.create_pipeline_run(
            pipeline_id=ds.origin_pipeline.id,
            db=db,
            current_user=current_user,
            pipe_run_in=PipelineRunCreate(
                workers=ds_commit_in.workers,
                cpus_per_worker=ds_commit_in.cpus_per_worker,
                orchestrator_backen=ds_commit_in.orchestration_backend,
                orchestration_args=ds_commit_in.orchestration_args,
                processing_backend=ds_commit_in.processing_backend,
                processing_args=ds_commit_in.processing_args,
                datasource_commit_id=datasource_commit.id,
                workspace_id=None,
                additional_args=additional_args,
                pipeline_run_type=PipelineRunTypes.datagen.name,
            ),
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error('Error while creating ds commit')
        logging.error(e)
        raise HTTPException(
            status_code=500,
            detail="We are unable to commit the datasource at this time. "
                   "Please contact us if this error persists!")
    return datasource_commit
