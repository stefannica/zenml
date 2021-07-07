import os

from app.utils.enums import EnvironmentTypes


def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result


# API variables
API_PREFIX_STR = "/api/v1"
OPENAPI_URL = API_PREFIX_STR + '/openapi.json'
PROJECT_NAME = os.getenv("PROJECT_NAME", 'ZenML Service')
API_HOST = os.getenv("API_HOST", "http://0.0.0.0:8000")
ENV_TYPE = os.getenv("ZENML_ENV_TYPE", EnvironmentTypes.local.name)

# Postgres
POSTGRES_ADDRESS = os.getenv("POSTGRES_ADDRESS", 'localhost')
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_DB = os.getenv('POSTGRES_DB', 'app')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD',
                              'ificatchyouwiththisinproductioniwillfindyouandendyou')
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_ADDRESS}:"
    f"{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

# CORS
BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS"
)  # a string of origins separated by commas, e.g: "http://localhost,
# http://localhost:4200, http://localhost:3000, http://localhost:8080,
# http://local.dockertoolbox.tiangolo.com"
