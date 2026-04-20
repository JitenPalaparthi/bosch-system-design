import time
from enum import Enum
from typing import Callable, Any


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 5):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0.0

    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        current_time = time.time()

        if self.state == CircuitState.OPEN:
            if current_time - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                print("[Breaker] Timeout finished. Moving to HALF_OPEN state.")
            else:
                raise Exception("Circuit is OPEN. Request blocked to protect the system.")

        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as exc:
            self._record_failure()
            raise exc

    def _record_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            print("[Breaker] Test request succeeded. Closing circuit.")
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()
        print(f"[Breaker] Failure count = {self.failure_count}")

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print("[Breaker] Failure threshold reached. Opening circuit.")
