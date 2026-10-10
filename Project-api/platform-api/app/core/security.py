
from concurrent.futures import
from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error





# app/core/security.py
from concurrent.futures import ThreadPoolExecutor
import asyncio

_hash_executor = ThreadPoolExecutor(max_workers=4)  # отдельный, не общий пул

async def hash_password_async(password: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_hash_executor, hash_password, password)

ph = PasswordHasher()


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
        ph.verify(hashed_password, plain_password)
        return True
    except Argon2Error:
        return False



