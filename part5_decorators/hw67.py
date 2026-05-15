import json
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar, cast
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime) -> None:
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        validation_exceptions = []

        if not self._is_positive_integer(critical_count):
            validation_exceptions.append(ValueError(INVALID_CRITICAL_COUNT))

        if not self._is_positive_integer(time_to_recover):
            validation_exceptions.append(ValueError(INVALID_RECOVERY_TIME))

        if validation_exceptions:
            raise ExceptionGroup(VALIDATIONS_FAILED, validation_exceptions)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self._fail_counter = 0
        self._block_time: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            func_name = self._get_func_name(func)

            if self._is_blocked():
                raise BreakerError(func_name, self._get_block_time())

            try:
                result = func(*args, **kwargs)
            except self.triggers_on as request_exception:
                self._fail_counter += 1

                if self._fail_counter >= self.critical_count:
                    self._block_time = datetime.now(UTC)
                    raise BreakerError(func_name, self._get_block_time()) from request_exception

                raise
            except Exception:
                raise

            self._fail_counter = 0
            self._block_time = None
            return result

        return cast(CallableWithMeta[P, R_co], wrapper)

    @staticmethod
    def _is_positive_integer(number: int) -> bool:
        return isinstance(number, int) and not isinstance(number, bool) and number > 0

    @staticmethod
    def _get_func_name(func: CallableWithMeta[P, R_co]) -> str:
        return f"{func.__module__}.{func.__name__}"

    def _is_blocked(self) -> bool:
        if self._block_time is None:
            return False

        recovery_time = self._block_time + timedelta(seconds=self.time_to_recover)

        if datetime.now(UTC) < recovery_time:
            return True

        self._fail_counter = 0
        self._block_time = None
        return False

    def _get_block_time(self) -> datetime:
        if self._block_time is None:
            return datetime.now(UTC)

        return self._block_time


circuit_breaker = CircuitBreaker(5, 30, Exception)


def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту.

    Args:
        post_id (int): Идентификатор поста.

    Returns:
        list[dict[int | str]]: Список комментариев.
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
