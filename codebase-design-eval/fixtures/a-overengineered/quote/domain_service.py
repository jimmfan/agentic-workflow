from .calculator import QuoteSubtotalCalculator
from .request import QuoteRequest


class QuoteDomainService:
    def __init__(self, calculator: QuoteSubtotalCalculator) -> None:
        self._calculator = calculator

    def quote(self, request: QuoteRequest) -> dict[str, int]:
        return {"total": self._calculator.calculate(request)}
