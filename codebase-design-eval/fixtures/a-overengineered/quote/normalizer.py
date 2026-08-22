from .request import QuoteRequest


class QuoteRequestNormalizer:
    def normalize(self, request: QuoteRequest) -> QuoteRequest:
        return QuoteRequest(
            prices=tuple(request.prices),
            discount_percent=max(0, min(100, request.discount_percent)),
        )
