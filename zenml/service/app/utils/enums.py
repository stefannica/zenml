from enum import Enum


class PipelineStatusTypes(Enum):
    NotStarted = 1
    Failed = 2
    Succeeded = 3
    Running = 4


class EnvironmentTypes(Enum):
    local = 1
    test = 2
    production = 3


class RolesTypes(Enum):
    admin = 1
    developer = 2
    operator = 3
    creator = 4


class PipelineRunTypes(Enum):
    training = 1
    datagen = 2
    infer = 3
    test = 4
    eval = 5


class PipelineTypes(Enum):
    normal = 1
    datagen = 2


class InviteStatus(Enum):
    pending = 1
    accepted = 2


class BackendClass(Enum):
    orchestration = 1
    processing = 2
    training = 3
    serving = 4


class BackendType(Enum):
    default = 1
    dataflow = 2
    gcaip = 3
