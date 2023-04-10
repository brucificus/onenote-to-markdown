import time
from functools import wraps
from typing import Callable, TypeVar
from logging import getLogger

import pywintypes
from _ctypes import COMError


T = TypeVar('T')
decoratee = Callable[[...], T]


def retry_com(func_being_decorated: decoratee, *decorator_args, **decorator_kwargs) -> decoratee:
    logger = getLogger(__name__).getChild(func_being_decorated.__name__)

    def _calculate_backoff(attempt: int) -> float:
        return (1.9 * (2 ** attempt)) + 10

    def _log_backing_off(attempt: int, backoff: float, error: COMError):
        logger.warning(f"Invocation of {func_being_decorated.__name__} failed: {error}", exc_info=error)
        logger.info(f"Backing off {backoff} seconds before retrying (attempt {attempt})…")

    retryable_errors = (
        -2147023170,  # 0x800706BE "The remote procedure call failed."
        -2147023174,  # 0x800706BA "The RPC server is unavailable."
        -2147023175,  # 0x800706B9 "The RPC server is too busy to complete this operation."
    )

    @wraps(func_being_decorated)
    def wrapper_retry_com(*args, **kwargs) -> T:
        errors: list[COMError] = []
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                return func_being_decorated(*args, **kwargs)
            except pywintypes.com_error as error:
                if error.hresult not in retryable_errors:
                    raise

                errors.insert(0, error)
                if attempt >= max_attempts:
                    raise RuntimeError(
                        f"Failed to invoke {func_being_decorated.__name__} after {max_attempts} attempts: {errors}",
                        error
                    ) from error

                backoff = _calculate_backoff(attempt)
                _log_backing_off(attempt, backoff, error)
                time.sleep(backoff)
                continue

        raise NotImplementedError("This should be unreachable")

    return wrapper_retry_com
