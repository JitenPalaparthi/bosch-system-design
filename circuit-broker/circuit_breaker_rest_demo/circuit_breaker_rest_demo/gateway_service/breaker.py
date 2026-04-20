from __future__ import annotations

import threading
import time
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Callable


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(Exception):
    pass


@dataclass
class CircuitStats:
    state: str
    failure_count: int
    success_count: int
    failure_threshold: int
    success_threshold: int
    recovery_timeout: float
    last_failure_time: float | None


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 10.0,
        success_threshold: int = 2,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._lock = threading.Lock()

    def _transition_to_open(self) -> None:
        self._state = CircuitState.OPEN
        self._last_failure_time = time.time()
        self._success_count = 0

    def _transition_to_half_open(self) -> None:
        self._state = CircuitState.HALF_OPEN
        self._failure_count = 0
        self._success_count = 0

    def _transition_to_closed(self) -> None:
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None

    def _can_attempt_request(self) -> bool:
        if self._state != CircuitState.OPEN:
            return True

        if self._last_failure_time is None:
            return False

        elapsed = time.time() - self._last_failure_time
        if elapsed >= self.recovery_timeout:
            self._transition_to_half_open()
            return True
        return False

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        with self._lock:
            if not self._can_attempt_request():
                raise CircuitBreakerOpenError("Circuit is OPEN. Request blocked.")

        try:
            result = func(*args, **kwargs)
        except Exception:
            with self._lock:
                if self._state == CircuitState.HALF_OPEN:
                    self._transition_to_open()
                else:
                    self._failure_count += 1
                    if self._failure_count >= self.failure_threshold:
                        self._transition_to_open()
                    else:
                        self._last_failure_time = time.time()
            raise

        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._transition_to_closed()
            else:
                self._failure_count = 0

        return result

    def stats(self) -> dict[str, Any]:
        with self._lock:
            data = CircuitStats(
                state=self._state.value,
                failure_count=self._failure_count,
                success_count=self._success_count,
                failure_threshold=self.failure_threshold,
                success_threshold=self.success_threshold,
                recovery_timeout=self.recovery_timeout,
                last_failure_time=self._last_failure_time,
            )
            return asdict(data)
