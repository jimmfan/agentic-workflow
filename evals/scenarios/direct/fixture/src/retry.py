def retry_delay(
    attempt: int,
    base_seconds: float = 1.0,
    max_seconds: float = 30.0,
) -> float:
    raise NotImplementedError
