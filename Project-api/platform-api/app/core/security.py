
from concurrent.futures import ThreadPoolExecutor
import asyncio

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

from .async_utils import run_sync_in_thread
from .config import HASH_THREAD_POOL_SIZE



ph = PasswordHasher()
_hash_executor = ThreadPoolExecutor(max_workers=HASH_THREAD_POOL_SIZE) # отдельный, не общий пул


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
