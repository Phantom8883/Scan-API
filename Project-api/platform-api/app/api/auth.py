from fastapi import APIRouter, Depends, status, HTTPException

from ..dependencies import get_user_service
from ..services.base_service import BaseService
from ..db.models.user import User
from ..schemas.user import UserCreate, UserLogin
from ..core.security import (
    hash_password_async, 
    verify_password_async, 
    create_access_token, 
    create_refresh_token,
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
        await service.create(email=data.email, password_hash=hashed)

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
    password_hash = user.password_hash if user else "$argon2id$v=19$m=65536,t=3,p=4$fake_salt_fake_salt$fake"
    is_valid = await verify_password_async(data.password, password_hash)

    if user is None or not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }