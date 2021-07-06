import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import config
from app.api.api_v1.api import api_router

app = FastAPI(
    title=config.PROJECT_NAME,
    openapi_url=config.OPENAPI_URL,
)

# CORS: Set all CORS enabled origins
origins = []
if config.BACKEND_CORS_ORIGINS:
    origins_raw = config.BACKEND_CORS_ORIGINS.split(",")
    for origin in origins_raw:
        use_origin = origin.strip()
        origins.append(use_origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),

app.include_router(api_router, prefix=config.API_PREFIX_STR)


@app.get("/")
def ping():
    """
    Serves as a fake heartbeat
    """
    return 'Im alive!'


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
