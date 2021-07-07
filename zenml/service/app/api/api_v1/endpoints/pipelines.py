import logging
from datetime import datetime, timezone
from typing import List, Dict, Text
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Body
from fastapi import Security
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN
from starlette.status import HTTP_412_PRECONDITION_FAILED

from app import crud
from app.db.models import User as DBUser
from app.schemas.artifact import Artifact
from app.schemas.datasource import DatasourceCommit
from app.schemas.pipeline import PipelineCreate, Pipeline, PipelineInDB
from app.schemas.pipelinerun import PipelineRunCreate, PipelineRunInDB
from app.schemas.pipelinerun import PipelineRunUpdate, \
    PipelineRunSlim
from app.schemas.pipelinestep import PipelineStepInDB
from app.schemas.user import UserBase
from app.utils.db import get_db
from app.utils.enums import PipelineStatusTypes, PipelineTypes, \
    PipelineRunTypes
from app.utils.security import get_current_user
from app.utils.security import reusable_oauth2

router = APIRouter()

DECLINE_MESSAGE = """
Wow, you're a power user! Unfortunately, we have to limit the resources
available during the Core Engine beta. Please reach out to us at 
support@maiot.io and we make sure all these pesky limits are removed!
"""


@router.get("/", response_model=List[Pipeline],
            response_model_exclude=["pipeline_config"])
def get_loggedin_pipelines(
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets the logged in users pipelines
    """
    return crud.pipeline.get_by_user_id(db, user_id=current_user.id)


@router.get("/{pipeline_id}", response_model=Pipeline)
def get_pipeline(
        pipeline_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets the pipeline specified by id
    """
    p = crud.pipeline.get(db, id=pipeline_id)
    if not p:
        raise HTTPException(
            status_code=404,
            detail="The pipeline does not exist.",
        )

    if not crud.user.is_admin(current_user):
        if p.team_id != current_user.team_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this pipeline.",
            )
    return p


@router.get("/{pipeline_id}/runs", response_model=List[PipelineRunSlim])
def get_pipeline_runs(
        pipeline_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets all the runs for a specified pipeline.
    """
    p = get_pipeline(pipeline_id, db, current_user)
    return p.pipeline_runs


@router.get("/{pipeline_id}/runs/{pipeline_run_id}",
            response_model=PipelineRunSlim)
def get_pipeline_run(
        pipeline_id: str,
        pipeline_run_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets a specific run for a specific pipeline
    """
    # First check if we are allowed to get this pipelines run
    p = crud.pipeline.get(db, id=pipeline_id)
    if not p:
        raise HTTPException(
            status_code=404,
            detail="The pipeline does not exist.",
        )

    if not crud.user.is_admin(current_user):
        if p.team_id != current_user.team_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this pipeline.",
            )

    run = crud.pipelinerun.get_by_pipeline(db, pipeline_id, pipeline_run_id)
    if run is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Could not find pipeline run {} for pipeline {}".format(
                pipeline_run_id, pipeline_id
            ),
        )

    return run


@router.get(
    "/{pipeline_id}/runs/{pipeline_run_id}/artifacts/{component_type}",
    response_model=List[Artifact]
)
def get_pipeline_artifacts(
        pipeline_id: str,
        pipeline_run_id: str,
        component_type: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets the artifact of any component within a pipeline run.
    """
    # TODO: [LOW] Write a check that would ensure the component_type is within
    #  GDP component list
    run = get_pipeline_run(pipeline_id, pipeline_run_id, db, current_user)

    if run.pipeline_run_type == PipelineRunTypes.datagen.name:
        raise HTTPException(
            status_code=400,
            detail="Datagen runs not supported",
        )

    if run.status == PipelineStatusTypes.NotStarted.name:
        raise HTTPException(
            status_code=400,
            detail="Run the pipeline first!",
        )
    comp_status = next(x for x in run.pipeline_steps
                       if component_type in x.component_type)
    if comp_status is None or comp_status.status != \
            PipelineStatusTypes.Succeeded.name:
        raise HTTPException(
            status_code=400,
            detail="Something went wrong while fetching the relevant resource."
                   "This could be because this pipeline failed unexpectedly "
                   "or is still running."
        )

    storage_client = get_storage_client(current_user.team)
    store = get_md_store_utils_by_workspace(db,
                                            workspace=run.pipeline.workspace)

    comp = crud.pipelinecomponent.get_by_component_type(
        db, run_id=run.id, component_type=component_type)
    artifacts = store.get_artifacts_by_execution(
        comp.ml_metadata_execution_id,
    )

    l = []
    for a in artifacts:
        bucket_name = a.uri.replace('gs://', '').split('/')[0]
        prefix = '/'.join(a.uri.replace('gs://', '').split('/')[1:])
        if not prefix.endswith('/'):
            prefix += '/'  # has to end with a / to avoid double counting
        bucket = storage_client.bucket(bucket_name)
        l.append(generate_download_signed_url_v4_dir(bucket, prefix))
    return l


@router.get(
    "/{pipeline_id}/runs/{pipeline_run_id}/artifact_uris/{component_type}",
    response_model=List[Text]
)
def get_pipeline_artifact_uris(
        pipeline_id: str,
        pipeline_run_id: str,
        component_type: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets the artifact of any component within a pipeline run.
    """
    # TODO: [LOW] Write a check that would ensure the component_type is within
    #  GDP component list

    run = get_pipeline_run(pipeline_id, pipeline_run_id, db, current_user)

    if run.pipeline_run_type == PipelineRunTypes.datagen.name:
        raise HTTPException(
            status_code=400,
            detail="Datagen runs not supported",
        )

    if run.status == PipelineStatusTypes.NotStarted.name:
        raise HTTPException(
            status_code=400,
            detail="Run the pipeline first!",
        )
    comp_status = next(x for x in run.pipeline_steps
                       if component_type in x.component_type)
    if comp_status is None or comp_status.status != \
            PipelineStatusTypes.Succeeded.name:
        raise HTTPException(
            status_code=400,
            detail="Something went wrong while fetching the relevant resource."
                   "This could be because this pipeline failed unexpectedly "
                   "or is still running."
        )
    store = get_md_store_utils_by_workspace(db,
                                            workspace=run.pipeline.workspace)
    comp = crud.pipelinecomponent.get_by_component_type(
        db, run_id=run.id, component_type=component_type)
    artifacts = store.get_artifacts_by_execution(
        comp.ml_metadata_execution_id,
    )

    return [a.uri for a in artifacts]


@router.get("/{pipeline_id}/runs/{pipeline_run_id}/logs", response_model=Text)
def get_pipeline_logs(
        pipeline_id: str,
        pipeline_run_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Creates and returns a log file of a pipeline as a signed URL
    """
    run = get_pipeline_run(pipeline_id, pipeline_run_id, db, current_user)

    if run.status == PipelineStatusTypes.NotStarted.name:
        raise HTTPException(
            status_code=400,
            detail="Run the pipeline first!",
        )

    # hard-code GCP orchestrator for now
    orch_meta = run.orchestrator_metadata['targetLink'].split('/')
    instance_id = run.orchestrator_metadata['targetId']
    project = orch_meta[6]

    return f'https://console.cloud.google.com/logs/query;query=logName%3D' \
           f'%22projects%2F{project}%2Flogs%2Fgcplogs-docker-driver%22' \
           f'%0Aresource.labels.instance_id%3D%22' \
           f'{instance_id}%22%0AjsonPayload.message:%22INFO:absl%22?project' \
           f'={project}&folder=true&query=%0A'
    # instance_name = orch_meta[-1]
    # zone = orch_meta[8]
    # return f'gcloud beta compute ssh --zone "{zone}" "{instance_name}" ' \
    #        f'--project "{project}" --command="sudo journalctl -u ' \
    #        f'google-startup-scripts.service -f"'


@router.get("/{pipeline_id}/runs/{pipeline_run_id}/hyperparameters",
            response_model=Dict)
def get_hyperparameters_pipeline(
        *,
        pipeline_id: str,
        pipeline_run_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets all hyperparameters available for a specific run.
    """
    run = get_pipeline_run(pipeline_id, pipeline_run_id, db, current_user)

    if run.pipeline_run_type == PipelineRunTypes.datagen.name:
        raise HTTPException(
            status_code=400,
            detail="Datagen runs not supported",
        )

    if run.status == PipelineStatusTypes.NotStarted.name:
        raise HTTPException(
            status_code=400,
            detail="Run the pipeline first!",
        )

    store = get_md_store_utils_by_workspace(db, run.pipeline.workspace)

    # We can use any component to get the runs context and then get all
    #  executions
    ml_metadata_execution_id = \
        run.pipeline_steps[0].ml_metadata_execution_id
    run_context = store.get_run_context_by_comp_execution_id(
        ml_metadata_execution_id)
    executions = store.store.get_executions_by_context(run_context.id)

    hparams = {}
    for e in executions:
        component_id = e.properties['component_id'].string_value.split('.')[1]
        if component_id == GDPComponent.Trainer.name:
            custom_config = eval(e.properties['custom_config'].string_value)
            trainer_config = custom_config['trainer']

            trainer_fn = trainer_config['fn']
            trainer_params = trainer_config['params']

            hparams['trainer_fn'] = trainer_fn
            hparams.update(trainer_params)

    # filter
    # whitelist = [
    #     'train_batch_size',
    #     'eval_batch_size',
    #     'optimizer',
    #     'loss',
    #     'labels',
    #     'train_steps',
    # ]
    #
    # return {k: v for k, v in hyperparam_dict.items() if k in whitelist}
    return hparams


@router.get("/{pipeline_id}/runs/{pipeline_run_id}/user",
            response_model=UserBase)
def get_pipeline_run_user(
        pipeline_id: str,
        pipeline_run_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
):
    """
    Gets the pipeline runs author
    """
    run = get_pipeline_run(pipeline_id, pipeline_run_id, db, current_user)

    if not crud.user.is_admin(current_user):
        # only if youre part of the same org
        if run.user.team_id != current_user.team_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this user.",
            )
    return UserBase(email=run.user.email, name=run.user.full_name)


@router.post("/", response_model=Pipeline)
async def create_pipeline(
        *,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
        pipe_in: PipelineCreate = Body(
            ...,
        )
):
    """
    Creates a core engine pipeline
    """
    logging.info("User {} creating pipeline with config: {}".format(
        current_user.email, pipe_in.pipeline_config))

    # check if its a duplicate name in the workspace
    all_names = crud.pipeline.get_pipeline_names_per_ws(
        db=db, workspace_id=pipe_in.workspace_id)
    if pipe_in.name in all_names:
        raise HTTPException(
            status_code=400,
            detail="You already have a pipeline with that name in this "
                   "workspace!"
        )

    org = current_user.team

    if pipe_in.pipeline_type != PipelineTypes.datagen.name:
        # TODO: [MEDIUM] This stuff needs to be cleaned up
        # infer custom methods from user pipeline config
        # set custom code to be empty
        pipe_in.pipeline_config[ExpGlobalKeys.CUSTOM_CODE_] = {}

        # handle transform first
        custom_method_refs = infer_custom_transform_injection(
            pipe_in.pipeline_config)
        # check if name checks out
        try:
            assert all(
                [len(n.split('@')) == 2 for n in
                 custom_method_refs[PreProcessKeys.TRANSFORM]])
        except AssertionError:
            raise HTTPException(
                status_code=400,
                detail="Please specify custom transform fn with a version in "
                       "the format function@version"
            )

        for function, version in [n.split('@') for n in set(
                custom_method_refs[PreProcessKeys.TRANSFORM])]:
            fn_block = resolve_custom_code(
                db, function, version, org.bucket_name)
            pipe_in.pipeline_config[ExpGlobalKeys.CUSTOM_CODE_].setdefault(
                CustomCodeKeys.TRANSFORM_, []).append(fn_block)

        # handle trainer
        custom_method_ref = infer_custom_trainer_injection(
            pipe_in.pipeline_config)
        if custom_method_ref is not None:
            # check if name checks out
            try:
                assert len(custom_method_ref.split('@')) == 2
            except AssertionError:
                raise HTTPException(
                    status_code=400,
                    detail="Please specify custom model fn with a version in "
                           "the format function@version"
                )

            function, version = custom_method_ref.split('@')
            fn_block = resolve_custom_code(
                db, function, version, org.bucket_name)
            pipe_in.pipeline_config[ExpGlobalKeys.CUSTOM_CODE_][
                CustomCodeKeys.MODEL_] = fn_block

        # run it through linting
        # TODO: [SEGMENT] Record such an event
        try:
            c = pipe_in.pipeline_config.copy()
            ConfigLinter.lint(c)
        except AssertionError as e:
            # ConfigLinter will always raise assertion error
            logging.error(e)
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )

    else:
        # TODO: [LOW] Add linting for datagen config here
        pass

    pipeline = PipelineInDB(
        name=pipe_in.name,
        pipeline_config=pipe_in.pipeline_config,
        team_id=current_user.team_id,
        workspace_id=pipe_in.workspace_id,
        user_id=current_user.id,
    )
    return crud.pipeline.create(db, obj_in=pipeline)


@router.post("/{pipeline_id}/runs", response_model=PipelineRunSlim)
async def create_pipeline_run(
        *,
        pipeline_id: str,
        db: Session = Depends(get_db),
        current_user: DBUser = Depends(get_current_user),
        pipe_run_in: PipelineRunCreate = Body(
            ...,
        )):
    """
    Create a pipeline run
    """
    # users org
    org = current_user.team

    # get pipeline
    pipeline = get_pipeline(pipeline_id=pipeline_id,
                            db=db,
                            current_user=current_user)

    # check first if users org has not exceeded any billing limits
    check_billing_limits_pipeline_runs(db, org)

    # check if provider is setup
    provider = [x for x in org.providers
                if x.type == OrchestratorTypes.gcp.name]
    if len(provider) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"Please set up a provider before you run. We only "
                   f"support {OrchestratorTypes.gcp.name} for now")

    # check how many pipelines are active
    if crud.user.get_running_pipelines_count(db, user=current_user) \
            > LIMIT_ACTIVE_PIPELINES_USER:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You cannot have more than {} pipelines active at "
                   "once. Please wait for the active ones to finish before"
                   " running a new pipeline. Feel free to reach out at "
                   "support@maiot.io to lift this "
                   "limit!".format(LIMIT_ACTIVE_PIPELINES_USER))

    # check if the user has exceeded his limit of pipeline executions
    if current_user.n_pipelines_executed >= LIMIT_PIPELINE_EXECUTED:
        logging.error("User {} exceeded the limit of pipeline executions "
                      "[{}]".format(current_user.email,
                                    LIMIT_PIPELINE_EXECUTED))
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail=DECLINE_MESSAGE,
        )

    # create the run in the db to get id
    pipeline_run = crud.pipelinerun.create(db, obj_in=PipelineRunInDB(
        pipeline_id=pipeline.id,
        status=PipelineStatusTypes.NotStarted.name,
        user_id=current_user.id,
        access_token=str(uuid4()),  # token is uuid for now
        **jsonable_encoder(pipe_run_in),
    ))

    from app.utils.run_builder import RunBuilder
    run = RunBuilder(db, pipeline_id, pipeline_run.id, current_user,
                     pipe_run_in).build()

    pipe_run_in.run_config = run.get_run_config()
    cloud_job_prefix = '{}_{}'.format(current_user.team_id,
                                      str(uuid4()).replace('-', '')).lower()

    start_time = datetime.now(timezone.utc)

    try:
        orchestrator_metadata = run.get_runner()(
            pipeline_config=run.get_pipeline_config(),
            run_config=pipe_run_in.run_config,
            cloud_job_prefix=cloud_job_prefix)
    except AssertionError as e:
        crud.pipelinerun.update(db, obj_in=PipelineRunInDB(
            pipeline_id=pipeline.id,
            status=PipelineStatusTypes.Failed.name,
            end_time=datetime.now(timezone.utc),
            orchestrator_metadata={},
            user_id=current_user.id,
            **jsonable_encoder(pipe_run_in),
        ), db_obj=pipeline_run)

        raise HTTPException(
            status_code=HTTP_412_PRECONDITION_FAILED,
            detail=str(e))
    except Exception as e:
        logging.error("Pipeline could not start: {}".format(str(e)))
        crud.pipelinerun.update(db, obj_in=PipelineRunInDB(
            pipeline_id=pipeline.id,
            status=PipelineStatusTypes.Failed.name,
            end_time=datetime.now(timezone.utc),
            orchestrator_metadata={},
            user_id=current_user.id,
            **jsonable_encoder(pipe_run_in),
        ), db_obj=pipeline_run)
        raise HTTPException(
            status_code=HTTP_412_PRECONDITION_FAILED,
            detail="Your pipeline could not be started, and we dont know what "
                   "exactly is wrong. Please check your config and make "
                   "sure everything is properly setup. Then try again.")

    return crud.pipelinerun.update(db, obj_in=PipelineRunInDB(
        pipeline_id=pipeline.id,
        status=PipelineStatusTypes.Running.name,
        start_time=start_time,
        orchestrator_metadata=orchestrator_metadata,
        user_id=current_user.id,
        processing_backend_id=run.processing_backend_id,
        orchestration_backend_id=run.orchestration_backend_id,
        training_backend_id=run.training_backend_id,
        serving_backend_id=run.serving_backend_id,
        training_args=run.training_args,
        serving_args=run.serving_args,
        **jsonable_encoder(pipe_run_in),
    ), db_obj=pipeline_run)


@router.put("/admin/{pipeline_id}/runs/{pipeline_run_id}",
            response_model=PipelineRunSlim)
def update_pipeline_run(
        pipeline_id: str,
        pipeline_run_id: str,
        db: Session = Depends(get_db),
        token: str = Security(reusable_oauth2),
        pipe_run_in: PipelineRunUpdate = Body(
            ...,
        )
):
    """
    Updates the pipeline and potentially its components. This is a
    special endpoint for pipeline runs to report back their status
    """
    logging.info(f"Updating pipeline with: {pipeline_id}, {pipeline_run_id}, "
                 f"{token}, {pipe_run_in}")

    # Get the run by using operator privelage
    run = get_pipeline_run(pipeline_id, pipeline_run_id, db,
                           crud.user.get_operator(db))

    if token != run.access_token:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You do not have a valid token to update this pipeline."
        )

    # update pipeline overall status
    crud.pipelinerun.update(db, db_obj=run, obj_in=pipe_run_in)

    # if no component, then return
    c = pipe_run_in.pipeline_step
    if c is None:
        return run

    # create component
    crud.pipelinecomponent.create(
        db,
        obj_in=PipelineStepInDB(
            start_time=c.start_time,
            end_time=c.end_time,
            status=c.status,
            component_type=c.component_type,
            ml_metadata_execution_id=c.ml_metadata_execution_id,
            pipeline_run_id=run.id,
        )
    )

    client = get_bq_client(run.user.team)
    n_datapoints = get_table_count(
        client,
        run.datasource_commit.destination_args[DestinationKeys.PROJECT],
        run.datasource_commit.destination_args[DestinationKeys.DATASET],
        run.datasource_commit.destination_args[DestinationKeys.TABLE],
    )

    # if its a datagen, then we do some more stuff
    if GDPComponent.DataGen.name in c.component_type:
        # get bq client based on user org
        table = get_table(
            client,
            run.datasource_commit.destination_args[DestinationKeys.PROJECT],
            run.datasource_commit.destination_args[DestinationKeys.DATASET],
            run.datasource_commit.destination_args[DestinationKeys.TABLE],
        )
        schema = get_schema(
            client,
            run.datasource_commit.destination_args[DestinationKeys.PROJECT],
            run.datasource_commit.destination_args[DestinationKeys.DATASET],
            run.datasource_commit.destination_args[DestinationKeys.TABLE],
        )
        crud.datasource_commit.update(
            db, db_obj=run.datasource_commit, obj_in=DatasourceCommit(
                used_schema=schema,
                n_datapoints=n_datapoints,
                n_features=len(table.schema),
                n_bytes=table.streaming_buffer.estimated_bytes,
            ))
    else:
        # report pipeline
        create_usage_record(run.pipeline.team, n_datapoints)

    return run
