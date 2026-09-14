"""Auth router — register and login (public endpoints)."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, status

from app import store
from app.auth import create_access_token, hash_password, verify_password
from app.models import Token, User, UserCreate

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate) -> Token:
    if body.username in store.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    user = User(
        id=str(uuid.uuid4()),
        username=body.username,
        hashed_password=hash_password(body.password),
    )
    store.users[user.username] = user
    return Token(access_token=create_access_token(user.username))


@router.post("/login", response_model=Token)
def login(body: UserCreate) -> Token:
    user = store.users.get(body.username)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return Token(access_token=create_access_token(user.username))
