# 🟢 CHANGED: Added basic dashboard login route
# REASON: Protect dashboard with simple demo-level authentication

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
async def login(payload: LoginRequest):
    expected_username = os.getenv("DASHBOARD_USERNAME", "admin")
    expected_password = os.getenv("DASHBOARD_PASSWORD", "admin123")
    token = os.getenv("DASHBOARD_TOKEN", "surakshanet-demo-token")

    if payload.username == expected_username and payload.password == expected_password:
        return {
            "status": "success",
            "token": token,
            "username": payload.username,
        }

    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.get("/auth/verify")
async def verify():
    return {"status": "auth route active"}
