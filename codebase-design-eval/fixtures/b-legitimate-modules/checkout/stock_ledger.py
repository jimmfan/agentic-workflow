from dataclasses import dataclass


@dataclass(frozen=True)
class Allocation:
    allocated: int
    backordered: int


class StockLedger:
    def allocate(self, requested: int, available: int, per_customer_cap: int) -> Allocation:
        if min(requested, available, per_customer_cap) < 0:
            raise ValueError("stock quantities must be non-negative")
        allocated = min(requested, available, per_customer_cap)
        return Allocation(allocated=allocated, backordered=requested - allocated)
