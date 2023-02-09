# python imports
from typing import List

# fastapi  imports
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

# application imports
from src.auth.auth_router import user_router
from src.organization.org_router import org_router

# fastapi initialization
app = FastAPI()


# CORS Middleware
origins: List = []


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers from the application
app.include_router(user_router)
app.include_router(org_router)


# root of the server
@app.get("/", status_code=status.HTTP_200_OK)
def root() -> dict:
    return {"message": "Welcome to FastAPI SAAS Template", "docs": "/docs"}
