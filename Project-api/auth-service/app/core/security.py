from concurrent.futures import ThreadPoolExecutor
import asyncio
import jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

from .async_utils import run_sync_in_thread
from .config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    HASH_THREAD_POOL_SIZE,
)

DUMMY_PASSWORD_HASH = "$argon2id$v=19$m=65536,t=3,p=4$rGSURLqH9QUQm7PutSB+rA$ix5l1HcRyuY9JG52n+fUov+QnkY5u3weD37iEvZ2+tw"
# Хеш
ph = PasswordHasher()
_hash_executor = ThreadPoolExecutor(
    max_workers=HASH_THREAD_POOL_SIZE
)  # отдельный, не общий пул


def hash_password(password: str) -> str:
    """
    Хеширует паоль перед сохранением в БД.
    """
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Сверяет введённый пароль с хэшем из БД.
    """
    try:
        return ph.verify(hashed_password, plain_password)
    except Argon2Error:
        return False


hash_password_async = run_sync_in_thread(_hash_executor)(hash_password)
verify_password_async = run_sync_in_thread(_hash_executor)(verify_password)


# Токены
def create_access_token(user_id: UUID) -> str:  # Токен доступа
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:  # Токен обновлений
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Расшифровывает и проверяет подпись токена.
    Бросает jwt.InvalidTokenError (и его подклассы, включая
    ExpiredSignatureError), если токен просрочен или подделан.
    """
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
