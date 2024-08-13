import os
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# v1 routers
from routers.v1 import root as root_v1
from routers.v1 import graph as graph_v1
from routers.v1 import hardcoded as hardcoded_v1

from config import description, title
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title=title,
    description=description,
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url=None,
)

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for v1
app.include_router(router=root_v1.router, prefix="/api/v1")
app.include_router(router=graph_v1.router, prefix="/api/v1")
app.include_router(router=hardcoded_v1.router, prefix="/api/v1")


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("DEBUG", "False").lower() == "true"

    uvicorn.run("main:app", host=host, port=port, reload=reload, workers=4)
