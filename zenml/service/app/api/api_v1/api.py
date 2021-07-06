from fastapi import APIRouter

from app.api.api_v1.endpoints import login, users, pipelines, datasources, \
    organization, backends

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organization.router, prefix="/organizations",
                          tags=["organizations"])
api_router.include_router(datasources.router, prefix="/datasources",
                          tags=["datasources"])
api_router.include_router(pipelines.router, prefix="/pipelines",
                          tags=["pipelines"])
api_router.include_router(backends.router, prefix="/backends",
                          tags=["backends"])
