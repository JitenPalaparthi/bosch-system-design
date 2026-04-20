import random


def unstable_api() -> str:
    """
    Simulates an unstable remote service.
    Around 60% of the calls fail.
    """
    if random.random() < 0.6:
        raise Exception("Remote service failed with 500 error")
    return "Remote service success"
