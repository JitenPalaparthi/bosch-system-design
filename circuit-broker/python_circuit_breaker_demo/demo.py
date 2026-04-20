import time
from breaker import CircuitBreaker
from unstable_service import unstable_api


def fallback_response() -> str:
    return "Fallback: using cached/default response"


if __name__ == "__main__":
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5)

    print("=== Python Circuit Breaker Demo ===")
    print("Failure threshold = 3")
    print("Recovery timeout = 5 seconds")
    print()

    for attempt in range(1, 11):
        print(f"\nRequest #{attempt}")
        print(f"Current state before call: {breaker.state.value}")

        try:
            response = breaker.call(unstable_api)
            print("Service response:", response)
        except Exception as exc:
            print("Main response path failed:", exc)
            print("Fallback response:", fallback_response())

        print(f"Current state after call: {breaker.state.value}")
        time.sleep(1)

    print("\nWaiting for recovery timeout to test HALF_OPEN...")
    time.sleep(6)

    print("\nRecovery test request")
    print(f"Current state before call: {breaker.state.value}")
    try:
        response = breaker.call(unstable_api)
        print("Service response:", response)
    except Exception as exc:
        print("Main response path failed:", exc)
        print("Fallback response:", fallback_response())
    print(f"Current state after call: {breaker.state.value}")
