from .domain_service import QuoteDomainService
from .request import QuoteRequest


class QuoteUseCase:
    def __init__(self, service: QuoteDomainService) -> None:
        self._service = service

    def run(self, request: QuoteRequest) -> dict[str, int]:
        return self._service.quote(request)
