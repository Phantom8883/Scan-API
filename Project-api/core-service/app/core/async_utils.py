import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Callable, TypeVar, ParamSpec, Coroutine, Any

P = ParamSpec(
    "P"
)  # Описывает сигнатуру параметров - сколько их, какие имена, какие типы и т.д.
R = TypeVar("R")  # Placeholder для одного типа


def run_sync_in_thread(executor: ThreadPoolExecutor | None = None):
    """
    Декоратор: берёт обычную синхронную функцию и возвращает
    её async-версию, которая выполняется в threapol.
    не блокируя event loop.
    executor=None - использует дефолтный общий пул (anyio/asyncio).
    """

    def decorator(func: Callable[P, R]) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(executor, lambda: func(*args, **kwargs))

        return wrapper

    return decorator
