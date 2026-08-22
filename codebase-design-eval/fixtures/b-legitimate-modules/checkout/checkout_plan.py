from dataclasses import dataclass

from .approval_policy import ApprovalPolicy
from .stock_ledger import StockLedger


@dataclass(frozen=True)
class CheckoutPlan:
    accepted: bool
    explanation_code: str
    allocated: int
    backordered: int


class CheckoutPlanner:
    def __init__(self, approval_policy: ApprovalPolicy, stock_ledger: StockLedger) -> None:
        self._approval_policy = approval_policy
        self._stock_ledger = stock_ledger

    def plan(
        self,
        jurisdiction: str,
        customer_age: int,
        requested: int,
        available: int,
        per_customer_cap: int,
    ) -> CheckoutPlan:
        approval = self._approval_policy.decide(jurisdiction, customer_age)
        if not approval.permitted:
            return CheckoutPlan(False, approval.explanation_code, 0, requested)
        allocation = self._stock_ledger.allocate(requested, available, per_customer_cap)
        return CheckoutPlan(
            accepted=allocation.allocated > 0,
            explanation_code="ALLOCATED" if allocation.allocated else "OUT_OF_STOCK",
            allocated=allocation.allocated,
            backordered=allocation.backordered,
        )
