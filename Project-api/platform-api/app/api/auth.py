from fastapi import APIRouter, Depends, status, HTTPException
from uuid import UUID
import jwt

from ..dependencies import get_user_service
from ..services.base_service import BaseService
from ..db.models.user import User
from ..schemas.user import UserCreate, UserLogin
from ..schemas.auth import RefreshRequest, TokenPair
from ..core.security import (
    hash_password_async, 
    verify_password_async, 
    create_access_token, 
    create_refresh_token,
    decode_token,
    DUMMY_PASSWORD_HASH,
    )



router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=202)
async def register(
    data: UserCreate,
    service: BaseService[User] = Depends(get_user_service),
):


    existing = await service.repository.get_single(email=data.email)
    hashed = await hash_password_async(data.password)

    if existing is None:
        await service.create(name=data.name, email=data.email, password_hash=hashed)

    return {"message": "Если этот email ещё не зарегистрирован, аккаунт создан. Проверьте почту."}


@router.post("/login")
async def login(
    data: UserLogin,
    service: BaseService[User] = Depends(get_user_service),
):
    user = await service.repository.get_single(email=data.email)

    # если юзера нет - сверяем пароль с ЗАГОТОВЛЕННЫМ фейковым хэшем,
    # чтобы verify_password_async всё равно отработал и занял те же 200-300мс,
    # что и в ветке с реальным юзером
    password_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
    is_valid = await verify_password_async(data.password, password_hash)

    if user is None or not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    data: RefreshRequest,
    service: BaseService[User] = Depends(get_user_service),
):
    try:
        payload = decode_token(data.refresh_token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный refresh-токен")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный refresh-токен")

    user = await service.get(UUID(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалилный refresh-токен")


    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        token_type="bearer",
    )