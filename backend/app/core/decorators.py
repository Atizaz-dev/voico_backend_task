import functools
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


def session_manager(func: Callable) -> Callable:
    """Decorator that manages the database session lifecycle.

    Commits the session on success, rolls back on any exception.
    The route must include `session: AsyncSession` as a dependency.
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        session = kwargs.get("session")
        if session is None:
            raise RuntimeError("session_manager requires a `session` keyword argument")

        try:
            result = await func(*args, **kwargs)
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise

    return wrapper
