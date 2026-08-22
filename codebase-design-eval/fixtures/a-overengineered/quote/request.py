from dataclasses import dataclass


@dataclass(frozen=True)
class QuoteRequest:
    prices: tuple[int, ...]
    discount_percent: int
