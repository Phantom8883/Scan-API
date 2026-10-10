from fastapi import APIRouter, Depends, status
import asyncio

from ..dependencies import get_user_service
from ..services.base_service import BaseService
from ..db.models.user import User
from ..schemas.user import UserCreate
from ..core.security import hash_password



router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=202)
async def register(
    data: UserCreate,
    service: BaseService[User] = Depends(get_user_service),
):
    existing = await service.repository.get_single(email=data.email)
    hashed = await 