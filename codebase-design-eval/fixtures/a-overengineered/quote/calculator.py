from .request import QuoteRequest


class QuoteSubtotalCalculator:
    def calculate(self, request: QuoteRequest) -> int:
        subtotal = sum(request.prices)
        return subtotal - (subtotal * request.discount_percent // 100)
