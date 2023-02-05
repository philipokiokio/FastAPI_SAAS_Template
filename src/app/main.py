from typing import List

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from src.auth.auth_router import user_router
from src.organization.org_router import org_router

app = FastAPI()


origins: List = []


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(org_router)


@app.get("/", status_code=status.HTTP_200_OK)
def root() -> dict:
    return {"message": "Welcome to FastAPI SAAS Template", "docs": "/docs"}
