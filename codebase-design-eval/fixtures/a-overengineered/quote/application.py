from .calculator import QuoteSubtotalCalculator
from .domain_service import QuoteDomainService
from .normalizer import QuoteRequestNormalizer
from .request import QuoteRequest
from .use_case import QuoteUseCase


class QuoteApplication:
    def __init__(self) -> None:
        self._normalizer = QuoteRequestNormalizer()
        self._use_case = QuoteUseCase(QuoteDomainService(QuoteSubtotalCalculator()))

    def execute(self, prices: list[int], discount_percent: int) -> dict[str, int]:
        request = QuoteRequest(tuple(prices), discount_percent)
        return self._use_case.run(self._normalizer.normalize(request))
