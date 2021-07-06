from uuid import uuid4

from sqlalchemy import String, Column, Integer, ForeignKey, Table, JSON, \
    DateTime
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.db.guid import GUID

users_workspaces = Table(
    'users_workspaces', Base.metadata,
    Column('user_id', GUID(), ForeignKey('user.id')),
    Column('workspace_id', GUID(), ForeignKey('workspace.id'))
)


class Team(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    users = relationship("User", back_populates="team")
    workspaces = relationship("Workspace", back_populates="team")
    datasources = relationship("Datasource", back_populates="team")
    pipelines = relationship("Pipeline", back_populates="team")


class Role(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    type = Column(String)

    # Relationship
    users = relationship("User", back_populates="role")


class User(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # FK
    team_id = Column(GUID(),
                             ForeignKey('team.id'),
                             nullable=True)
    role_id = Column(GUID(), ForeignKey('role.id'), nullable=True)

    # Relationship
    team = relationship("Team", back_populates="users")
    role = relationship("Role", back_populates="users")
    pipeline_runs = relationship("PipelineRun", back_populates="user")
    workspaces = relationship("Workspace",
                              secondary=users_workspaces,
                              back_populates="users")
    pipelines = relationship("Pipeline", back_populates="user")


class Datasource(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # type of data, i.e., tabular, image, text
    type = Column(String)

    # FK
    team_id = Column(GUID(), ForeignKey('team.id'))
    metadatastore_id = Column(GUID(), ForeignKey('metadatastore.id'))
    origin_pipeline_id = Column(GUID(), ForeignKey('pipeline.id'), index=True)

    # Relationship
    team = relationship("Team", back_populates="datasources")
    datasource_commits = relationship("DatasourceCommit",
                                      back_populates="datasource")
    metadatastore = relationship("Metadatastore", back_populates="datasource")
    origin_pipeline = relationship("Pipeline")


class DatasourceCommit(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # FK
    user_id = Column(GUID(), ForeignKey('user.id'), index=True)
    datasource_id = Column(GUID(), ForeignKey('datasource.id'), index=True)

    # Relationship
    datasource = relationship("Datasource",
                              back_populates="datasource_commits")
    pipeline_runs = relationship("PipelineRun",
                                 back_populates="datasource_commit")


class Workspace(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # FK
    team_id = Column(GUID(), ForeignKey('team.id'))
    metadatastore_id = Column(GUID(), ForeignKey('metadatastore.id'))

    # Relationship
    team = relationship("Team", back_populates="workspaces")
    metadatastore = relationship("Metadatastore", back_populates="workspace")
    pipelines = relationship("Pipeline", back_populates="workspace")
    users = relationship("User",
                         secondary=users_workspaces,
                         back_populates="workspaces")


class Metadatastore(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    orchestrator_host = Column(String)
    internal_host = Column(String)
    port = Column(Integer)
    database = Column(String)
    username = Column(String)

    # Relationship
    # You can either have workspace or datasource, not both at the same time
    workspace = relationship("Workspace",
                             uselist=False,
                             back_populates="metadatastore")
    datasource = relationship("Datasource",
                              uselist=False,
                              back_populates="metadatastore")


class Pipeline(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # FK
    team_id = Column(GUID(), ForeignKey('team.id'))
    workspace_id = Column(GUID(), ForeignKey('workspace.id'), nullable=True)
    user_id = Column(GUID(), ForeignKey('user.id'), index=True)

    # Relationship
    team = relationship("Team", back_populates="pipelines")
    pipeline_runs = relationship("PipelineRun",
                                 back_populates="pipeline",
                                 lazy="joined")
    workspace = relationship("Workspace", back_populates="pipelines")
    user = relationship("User", back_populates="pipelines")


class PipelineRun(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    run_config = Column(MutableDict.as_mutable(JSON))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    status = Column(String, index=True)
    pipeline_run_type = Column(String, nullable=False)

    # dict of metadata returned by orchestrator
    orchestrator_metadata = Column(JSON, nullable=True)

    # FK
    pipeline_id = Column(GUID(), ForeignKey('pipeline.id'), index=True)
    datasource_commit_id = Column(GUID(), ForeignKey('datasourcecommit.id'))
    user_id = Column(GUID(), ForeignKey('user.id'), index=True)

    # Relationship
    pipeline = relationship("Pipeline",
                            back_populates="pipeline_runs")
    datasource_commit = relationship("DatasourceCommit",
                                     back_populates="pipeline_runs")
    user = relationship("User", back_populates="pipeline_runs")

    pipeline_steps = relationship("PipelineStep",
                                  back_populates="pipeline_run")


class PipelineStep(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    status = Column(String, index=True)
    step_type = Column(String, nullable=False)

    # FK
    pipeline_run_id = Column(GUID(), ForeignKey('pipelinerun.id'))

    # Relationship
    pipeline_run = relationship("PipelineRun",
                                back_populates="pipeline_steps")


class Backend(Base):
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # unique name of the backend
    name = Column(String)

    # class of provider, i.e., gcp
    backend_class = Column(String)

    # type of provider, i.e., gcp
    type = Column(String)

    # FK
    user_id = Column(GUID(), ForeignKey('user.id'), index=True)
    team_id = Column(GUID(),
                             ForeignKey('team.id'),
                             nullable=True)
